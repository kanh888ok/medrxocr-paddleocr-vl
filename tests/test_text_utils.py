import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.utils.text import length_bin, normalize_text


class TestTextUtils(unittest.TestCase):
    def test_normalize_text_handles_none_and_spaces(self):
        self.assertEqual(normalize_text(None), "")
        self.assertEqual(normalize_text("  ABC   10mg  "), "abc 10mg")

    def test_length_bin_uses_rxhandbd_eval_buckets(self):
        self.assertEqual(length_bin("abcde"), "short_0_5")
        self.assertEqual(length_bin("abcdef"), "common_6_8")
        self.assertEqual(length_bin("abcdefghi"), "long_9_12")
        self.assertEqual(length_bin("abcdefghijklm"), "very_long_13_plus")


if __name__ == "__main__":
    unittest.main()
