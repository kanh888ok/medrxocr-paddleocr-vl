import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.training.selection import hard_sample_score, select_hard_samples


def row(image_id, text, difficulty="easy"):
    return {
        "image_id": image_id,
        "metadata": {
            "difficulty": difficulty,
            "visual_tags": ["handwritten"],
        },
        "annotation": {"full_ocr_text": text},
    }


class TestTrainingSelection(unittest.TestCase):
    def test_digits_and_longer_text_score_higher(self):
        plain = row("a", "abc")
        hard = row("b", "Vitamin B12 500mg", "hard")
        self.assertGreater(hard_sample_score(hard), hard_sample_score(plain))

    def test_prediction_cer_can_drive_selection(self):
        rows = [row("easy", "abcdef"), row("missed", "abc")]
        selected = select_hard_samples(rows, 1, {"missed": {"cer": 1.0}})
        self.assertEqual(selected[0]["image_id"], "missed")


if __name__ == "__main__":
    unittest.main()
