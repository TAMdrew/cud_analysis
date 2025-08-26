import unittest
from pathlib import Path

from finops_analysis_platform.discount_mapping import MachineTypeDiscountMapping


class TestMachineTypeDiscountMapping(unittest.TestCase):
    """Test suite for the MachineTypeDiscountMapping class."""

    def setUp(self):
        """Set up a test instance of the discount mapping."""
        self.test_discounts_path = Path("test_discounts.yaml")
        with open(self.test_discounts_path, "w") as f:
            f.write(
                """
discounts:
  n1: {'1yr_resource': 0.37, '3yr_resource': 0.55, '1yr_flex': 0.28, '3yr_flex': 0.46, 'sud': 0.30}
  e2: {'1yr_resource': 0.37, '3yr_resource': 0.55, '1yr_flex': 0.28, '3yr_flex': 0.46, 'sud': 0.20}
  gpu: {'1yr_resource': 0.20, '3yr_resource': 0.40, '1yr_flex': 0.10, '3yr_flex': 0.20, 'sud': 0.10}
families:
  'General Purpose': ['n1', 'e2']
  'GPU': ['gpu']
prefixes: ['n1', 'e2', 'gpu']
"""
            )
        self.discount_mapping = MachineTypeDiscountMapping(
            config_path=self.test_discounts_path
        )

    def tearDown(self):
        """Clean up the dummy discount file."""
        if self.test_discounts_path.exists():
            self.test_discounts_path.unlink()

    def test_get_discount(self):
        """Test that the correct discount is returned."""
        self.assertEqual(
            self.discount_mapping.get_discount("n1-standard-4", "1yr_resource"), 0.37
        )
        self.assertEqual(
            self.discount_mapping.get_discount("e2-medium", "3yr_flex"), 0.46
        )
        self.assertEqual(
            self.discount_mapping.get_discount("gpu-t4-instance", "3yr_resource"), 0.40
        )
        self.assertIsNone(
            self.discount_mapping.get_discount("z3-standard-4", "1yr_resource")
        )

    def test_get_family(self):
        """Test that the correct machine family is returned."""
        self.assertEqual(
            self.discount_mapping.get_family("n1-highcpu-8"), "General Purpose"
        )
        self.assertEqual(self.discount_mapping.get_family("gpu-a100"), "GPU")
        self.assertEqual(
            self.discount_mapping.get_family("c2-standard-8"), "General Purpose"
        )  # default


if __name__ == "__main__":
    unittest.main()
