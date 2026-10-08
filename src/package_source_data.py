"""Empaquetar fuentes locales conservando sus rutas, sin subirlas a GitHub."""
import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def package(root, destination):
    files = sorted(list((root / "dimensions").rglob("*.json")) + list((root / "facts").rglob("*.json")))
    if not files:
        raise ValueError("No se encontraron fuentes JSON.")
    if destination.exists():
        raise FileExistsError(str(destination))
    manifest = [{"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size} for p in files]
    with ZipFile(destination, "w", ZIP_DEFLATED, compresslevel=1, allowZip64=True) as archive:
        for index, path in enumerate(files, 1):
            archive.write(path, path.relative_to(root).as_posix())
            if index % 10 == 0 or index == len(files):
                print(f"Empaquetados {index}/{len(files)}", flush=True)
    with ZipFile(destination) as archive:
        entries = [{"path": e.filename, "bytes": e.file_size} for e in archive.infolist()]
        if entries != manifest:
            raise ValueError("El manifiesto del ZIP no coincide con las fuentes.")
    destination.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"ZIP listo: {destination.resolve()} ({destination.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    package(args.root, args.destination)
