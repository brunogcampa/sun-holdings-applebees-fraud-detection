"""Bounded-memory preparation of immutable source arrays for Serverless JSON scans.

Run the companion prepare_checks_jsonl.ipynb before the Lakeflow update. No Spark
or third-party packages are used. This module is also imported by local tests.
Original JSON tokens, array order, nulls, signs and numeric literals are preserved.
"""
import hashlib
import json
from pathlib import Path

VERSION = 1
PART_BYTES = 16 * 1024 * 1024
CHUNK_CHARS = 1024 * 1024
MAX_RECORD_CHARS = 32 * 1024 * 1024


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_objects(handle, chunk_chars=CHUNK_CHARS, max_record_chars=MAX_RECORD_CHARS):
    """Yield each top-level object's original JSON text; reject invalid arrays.

    Buffer is bounded by one record plus a read chunk. Never load a daily array.
    JSONDecoder locates record boundaries even with nested arrays/escaped braces.
    """
    decoder = json.JSONDecoder()
    buffer, eof = "", False

    def more():
        nonlocal buffer, eof
        text = handle.read(chunk_chars)
        if text:
            buffer += text
        else:
            eof = True

    def skip_space():
        nonlocal buffer
        while True:
            buffer = buffer.lstrip(" \t\r\n")
            if buffer or eof:
                return
            more()

    skip_space()
    if not buffer.startswith("["):
        raise ValueError("Expected one top-level JSON array")
    buffer = buffer[1:]
    skip_space()
    if buffer.startswith("]"):
        buffer = buffer[1:]
    else:
        while True:
            skip_space()
            if not buffer.startswith("{"):
                raise ValueError("Expected a check object; scalar/null/trailing comma is invalid")
            while True:
                try:
                    record, end = decoder.raw_decode(buffer)
                    break
                except json.JSONDecodeError as error:
                    if eof:
                        raise ValueError("Malformed or truncated source JSON") from error
                    if len(buffer) > max_record_chars:
                        raise ValueError("A single check exceeds the bounded record limit") from error
                    more()
            if end > max_record_chars:
                raise ValueError("A single check exceeds the bounded record limit")
            if not isinstance(record, dict) or "_source_file" in record:
                raise ValueError("Expected an object without reserved _source_file metadata")
            original = buffer[:end]
            buffer = buffer[end:]
            yield original
            skip_space()
            if buffer.startswith("]"):
                buffer = buffer[1:]
                break
            if not buffer.startswith(","):
                raise ValueError("Expected ',' or ']' after a check")
            buffer = buffer[1:]
    skip_space()
    if buffer:
        raise ValueError("Unexpected content after the source array")


def compact_object(text):
    """Remove only insignificant whitespace, keeping numeric/string tokens exact."""
    if "\n" not in text and "\r" not in text:
        return text
    result = []
    in_string = escaped = False
    for char in text:
        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
            result.append(char)
        elif char not in " \t\r\n":
            result.append(char)
    return "".join(result)


def _write_json(path, value):
    # Publish metadata only after all referenced data files are closed/verified.
    # Volume writes are not claimed to be a multi-file atomic transaction.
    with Path(path).open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def prepare_source(source, source_root, prepared_root, part_bytes=PART_BYTES):
    source = Path(source)
    before = source.stat()
    source_hash = sha256_file(source)
    identity = f"{VERSION}:{part_bytes}:{source.as_posix()}:{source_hash}"
    cache_key = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    cache = Path(prepared_root) / "files" / cache_key
    marker = cache / "_manifest.json"
    if marker.is_file():
        entry = json.loads(marker.read_text(encoding="utf-8"))
        if entry.get("source_file") != source.as_posix() or entry.get("source_sha256") != source_hash:
            raise ValueError("Prepared cache identity mismatch")
        for part in entry["parts"]:
            output = Path(part["path"])
            if output.parent.resolve() != cache.resolve():
                raise ValueError("Prepared cache path escapes its expected directory")
            if output.stat().st_size != part["bytes"] or sha256_file(output) != part["sha256"]:
                raise ValueError("Prepared JSONL changed; preserve it and investigate the cache")
        return entry

    cache.mkdir(parents=True, exist_ok=True)
    parts, output, part_path, part_hash = [], None, None, None
    part_size = records = 0
    lineage = '{"_source_file":' + json.dumps(source.as_posix(), ensure_ascii=False)
    def close_part():
        nonlocal output
        if output is not None:
            output.close()
            parts.append({"path": part_path.as_posix(), "bytes": part_size,
                          "sha256": part_hash.hexdigest()})
            output = None

    try:
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            for raw in iter_objects(handle):
                compact = compact_object(raw)
                # Insert lineage without deserializing/reserializing business values.
                separator = "" if compact == "{}" else ","
                line = (lineage + separator + compact[1:] + "\n").encode("utf-8")
                if output is None or (part_size and part_size + len(line) > part_bytes):
                    close_part()
                    part_path = cache / f"part-{len(parts):05d}.jsonl"
                    output = part_path.open("wb")
                    part_size, part_hash = 0, hashlib.sha256()
                output.write(line)
                part_hash.update(line)
                part_size += len(line)
                records += 1
        close_part()
        after = source.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or sha256_file(source) != source_hash:
            raise ValueError("Source changed during preparation; do not run the pipeline")
        entry = {"source_file": source.as_posix(),
                 "relative_path": source.relative_to(source_root).as_posix(),
                 "source_sha256": source_hash, "source_bytes": before.st_size,
                 "records": records, "parts": parts}
        _write_json(marker, entry)
        return entry
    finally:
        if output is not None:
            output.close()


def prepare_all(source_root, part_bytes=PART_BYTES, progress=print):
    source_root = Path(source_root).resolve()
    prepared_root = Path(str(source_root) + "_jsonl")
    sources = sorted((source_root / "facts" / "checks").rglob("*.json"))
    if not sources:
        raise ValueError("No source JSON found under facts/checks")
    if part_bytes < 1:
        raise ValueError("part_bytes must be positive")
    prepared_root.mkdir(parents=True, exist_ok=True)
    entries = []
    for number, source in enumerate(sources, 1):
        entry = prepare_source(source, source_root, prepared_root, part_bytes)
        entries.append(entry)
        progress(f"{number}/{len(sources)} files prepared; {sum(e['records'] for e in entries):,} checks")
    if sorted((source_root / "facts" / "checks").rglob("*.json")) != sources:
        raise ValueError("Source inventory changed during preparation")
    inventory = [(e["relative_path"], e["source_sha256"]) for e in entries]
    ready = {"format_version": VERSION, "source_root": source_root.as_posix(),
             "source_inventory_sha256": hashlib.sha256(json.dumps(inventory).encode()).hexdigest(),
             "source_files": len(entries), "records": sum(e["records"] for e in entries),
             "output_files": [p["path"] for e in entries for p in e["parts"]], "files": entries}
    if not ready["output_files"]:
        raise ValueError("No checks were prepared; no ready manifest published")
    _write_json(prepared_root / "_READY.json", ready)
    progress(f"READY: {ready['records']:,} checks from {ready['source_files']} source files")
    return ready


def run_databricks():
    dbutils.widgets.text("source_root", "/Volumes/workspace/applebees_raw/source/applebees_source",
                         "Original source root")
    source_root = dbutils.widgets.get("source_root").rstrip("/")
    if not source_root.startswith("/Volumes/") or ".." in Path(source_root).parts:
        raise ValueError("Use the original /Volumes/... source root")
    result = prepare_all(source_root, progress=lambda message: print(message, flush=True))
    print(json.dumps({key: result[key] for key in ("source_files", "records", "source_inventory_sha256")}, indent=2))


if __name__ == "__main__" and "dbutils" in globals():
    run_databricks()
