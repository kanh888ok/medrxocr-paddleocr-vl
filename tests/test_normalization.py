import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.normalization import normalize_frequency, normalize_route, normalize_space, normalize_unit


class TestNormalization(unittest.TestCase):
    def test_normalize_space_preserves_none(self):
        self.assertIsNone(normalize_space(None))
        self.assertEqual(normalize_space("  take   daily "), "take daily")

    def test_frequency_and_route_maps_common_abbreviations(self):
        self.assertEqual(normalize_frequency("B.I.D."), "twice_daily")
        self.assertEqual(normalize_route("PO"), "oral")

    def test_unit_normalization_handles_chinese_units(self):
        self.assertEqual(normalize_unit("500 毫克"), "500 mg")
        self.assertEqual(normalize_unit("10 ML"), "10 ml")


if __name__ == "__main__":
    unittest.main()
