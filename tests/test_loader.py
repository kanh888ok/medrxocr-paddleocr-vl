import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.data.loader import filter_records, load_jsonl


class TestLoader(unittest.TestCase):
    def test_load_jsonl_and_filter(self):
        path = Path("outputs") / "_unit_rows.jsonl"
        path.parent.mkdir(exist_ok=True)
        rows = [
            {"image_id": "a", "metadata": {"source_id": "s1", "task_type": "word_ocr"}},
            {"image_id": "b", "metadata": {"source_id": "s2", "task_type": "full_ocr"}},
        ]
        try:
            path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
            loaded = load_jsonl(path)
            selected = filter_records(loaded, source_id="s1", task_type="word_ocr")
            self.assertEqual([row["image_id"] for row in selected], ["a"])
        finally:
            if path.exists():
                path.unlink()


if __name__ == "__main__":
    unittest.main()
