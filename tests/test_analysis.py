import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.evaluation.analysis import analyze_predictions


class TestAnalysis(unittest.TestCase):
    def test_analyze_predictions_reports_latency_and_digits(self):
        rows = [
            {
                "image_id": "x1",
                "gold_text": "AB 10",
                "prediction": {"full_ocr_text": "AB 10"},
                "exact_match": True,
                "edit_distance": 0,
                "gold_chars": 5,
                "cer": 0.0,
                "elapsed_sec": 1.0,
                "error": None,
            },
            {
                "image_id": "x2",
                "gold_text": "CD",
                "prediction": {"full_ocr_text": "CE"},
                "exact_match": False,
                "edit_distance": 1,
                "gold_chars": 2,
                "cer": 0.5,
                "elapsed_sec": 12.0,
                "error": None,
            },
        ]
        report = analyze_predictions(rows, slow_threshold_sec=10)
        self.assertEqual(report["summary"]["n_records"], 2)
        self.assertEqual(report["latency"]["slow_count"], 1)
        self.assertEqual(report["digit"]["digit_exact_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
