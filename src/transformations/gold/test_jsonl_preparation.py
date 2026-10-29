"""Tests of lossless JSONL conversion, bounded reads, cache and failure recovery."""
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

SILVER = Path(__file__).resolve().parent.parent / "silver"
spec = importlib.util.spec_from_file_location("prepare", SILVER / "prepare_checks_jsonl_source.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class PreparationTests(unittest.TestCase):
    def test_nested_arrays_escaped_strings_and_tiny_chunks(self):
        original = [{"Id": -1, "Payments": [], "text": 'café, [\\"]\n'},
                    {"Id": 2, "Payments": None, "ItemsSold": [{"Discounts": [{"Amount": -3.50}]}]}]
        text = json.dumps(original, ensure_ascii=False, indent=2)
        found = list(prepare.iter_objects(io.StringIO(text), chunk_chars=3))
        self.assertEqual([json.loads(record) for record in found], original)
        self.assertTrue(all("\n" not in prepare.compact_object(record) for record in found))

    def test_numeric_literals_are_not_rounded_or_reformatted(self):
        raw = '{\n "Id": 9007199254740993, "Amount": -0.00000000000000000001230, "n": 1.2300e+10\n}'
        compact = prepare.compact_object(raw)
        self.assertIn("9007199254740993", compact)
        self.assertIn("-0.00000000000000000001230", compact)
        self.assertIn("1.2300e+10", compact)

    def test_rejects_invalid_framing_and_reserved_lineage(self):
        invalid = ['{}', '[null]', '[1]', '[{},]', '[{}{}]', '[{}]extra', '[{"Id":',
                   '[{"_source_file":"spoof"}]']
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(ValueError):
                list(prepare.iter_objects(io.StringIO(text), chunk_chars=2))

    def test_reads_have_explicit_bound_and_large_record_limit(self):
        class BoundedReader(io.StringIO):
            def read(self, size=-1):
                if not 0 < size <= 16:
                    raise AssertionError("Unbounded read")
                return super().read(size)
        text = json.dumps([{"Id": value} for value in range(1000)])
        self.assertEqual(len(list(prepare.iter_objects(BoundedReader(text), chunk_chars=16))), 1000)
        with self.assertRaises(ValueError):
            list(prepare.iter_objects(io.StringIO('[{"x":"' + 'a' * 100 + '"}]'),
                                      chunk_chars=8, max_record_chars=32))

    def test_shards_lineage_and_same_source_rerun(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            day = root / "facts/checks/brand=rmh/dt=2026-04-28/checks.json"
            day.parent.mkdir(parents=True)
            records = [{"Id": i, "Payments": [] if i % 2 else None} for i in range(25)]
            day.write_text('\ufeff' + json.dumps(records, indent=2), encoding="utf-8")
            first = prepare.prepare_all(root, part_bytes=512, progress=lambda _: None)
            self.assertGreater(len(first["output_files"]), 1)
            found = []
            for part in first["output_files"]:
                self.assertLessEqual(Path(part).stat().st_size, 512)
                found.extend(json.loads(line) for line in Path(part).read_text(encoding="utf-8").splitlines())
            self.assertEqual([record.pop("_source_file") for record in found], [day.as_posix()] * 25)
            self.assertEqual(found, records)
            second = prepare.prepare_all(root, part_bytes=512, progress=lambda _: None)
            self.assertEqual(first, second)
            self.assertEqual(day.read_text(encoding="utf-8"), '\ufeff' + json.dumps(records, indent=2))

    def test_incomplete_preparation_keeps_prior_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            day = root / "facts/checks/day.json"
            day.parent.mkdir(parents=True)
            day.write_text('[{"Id":1}]', encoding="utf-8")
            prepare.prepare_all(root, progress=lambda _: None)
            marker = Path(str(root) + "_jsonl/_READY.json")
            before = marker.read_bytes()
            day.write_text('[{"Id":2},', encoding="utf-8")
            with self.assertRaises(ValueError):
                prepare.prepare_all(root, progress=lambda _: None)
            self.assertEqual(marker.read_bytes(), before)

    def test_changed_source_replaces_active_inventory_without_duplicate_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            day = root / "facts/checks/day.json"
            day.parent.mkdir(parents=True)
            day.write_text('[{"Id":1}]', encoding="utf-8")
            first = prepare.prepare_all(root, progress=lambda _: None)
            day.write_text('[{"Id":2},{"Id":3}]', encoding="utf-8")
            second = prepare.prepare_all(root, progress=lambda _: None)
            self.assertNotEqual(first["source_inventory_sha256"], second["source_inventory_sha256"])
            self.assertEqual(second["records"], 2)
            self.assertTrue(set(first["output_files"]).isdisjoint(second["output_files"]))
            self.assertTrue(all(Path(part).exists() for part in first["output_files"]))

    def test_changed_prepared_file_is_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            day = root / "facts/checks/day.json"
            day.parent.mkdir(parents=True)
            day.write_text('[{"Id":1}]', encoding="utf-8")
            ready = prepare.prepare_all(root, progress=lambda _: None)
            Path(ready["output_files"][0]).write_text('{}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed"):
                prepare.prepare_all(root, progress=lambda _: None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
