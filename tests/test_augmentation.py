import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from medrxocr.data.augmentation import get_variant, resolve_variants, variant_names


class TestAugmentation(unittest.TestCase):
    def test_default_variants_include_camera_cases(self):
        names = variant_names()
        self.assertIn("blur", names)
        self.assertIn("rotate", names)
        self.assertIn("perspective", names)

    def test_resolve_variants_keeps_requested_order(self):
        specs = resolve_variants(["rotate", "blur"])
        self.assertEqual([spec.name for spec in specs], ["rotate", "blur"])

    def test_unknown_variant_raises_clear_error(self):
        with self.assertRaisesRegex(ValueError, "Unknown augmentation variant"):
            get_variant("unknown")


if __name__ == "__main__":
    unittest.main()
