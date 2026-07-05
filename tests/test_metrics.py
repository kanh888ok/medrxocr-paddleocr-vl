import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.evaluation.metrics import char_error_breakdown, exact_match, text_cer


class TestMetrics(unittest.TestCase):
    def test_exact_match_normalizes_case_and_space(self):
        self.assertTrue(exact_match("  ABC  10mg", "abc 10mg"))

    def test_text_cer_uses_gold_length(self):
        self.assertEqual(text_cer("abc", "adc"), 1 / 3)

    def test_char_error_breakdown_counts_basic_ops(self):
        res = char_error_breakdown("abx", "abc")
        self.assertEqual(res["substitutions"], 1)
        self.assertEqual(res["edit_distance"], 1)


if __name__ == "__main__":
    unittest.main()
