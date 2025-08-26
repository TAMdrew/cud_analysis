import unittest
from pathlib import Path

from finops_analysis_platform.config_manager import ConfigManager
from finops_analysis_platform.discount_mapping import MachineTypeDiscountMapping
from finops_analysis_platform.savings_calculator import SavingsCalculator


class TestSavingsCalculator(unittest.TestCase):
    """Test suite for the SavingsCalculator class."""

    def setUp(self):
        """Set up a test instance of the savings calculator."""
        self.config = {
            "cud_strategy": {"base_layer_coverage": 70},
        }
        self.config_manager = ConfigManager()
        self.config_manager.config = self.config

        self.test_discounts_path = Path("test_discounts.yaml")
        with open(self.test_discounts_path, "w") as f:
            f.write(
                """
discounts:
  n1: {'1yr_resource': 0.37, '3yr_resource': 0.55, '1yr_flex': 0.28, '3yr_flex': 0.46, 'sud': 0.30}
  e2: {'1yr_resource': 0.37, '3yr_resource': 0.55, '1yr_flex': 0.28, '3yr_flex': 0.46, 'sud': 0.20}
families:
  'General Purpose': ['n1', 'e2']
prefixes: ['n1', 'e2']
"""
            )
        self.discount_mapping = MachineTypeDiscountMapping(
            config_path=self.test_discounts_path
        )
        self.savings_calculator = SavingsCalculator(
            self.config_manager, self.discount_mapping
        )

    def tearDown(self):
        """Clean up the dummy discount file."""
        if self.test_discounts_path.exists():
            self.test_discounts_path.unlink()

    def test_calculate_savings_by_machine(self):
        """Test the calculation of savings by machine type."""
        distribution = {"n1": 300, "e2": 50}
        savings = self.savings_calculator.calculate_savings_by_machine(distribution)

        self.assertIn("n1", savings)
        self.assertIn("e2", savings)

        # Check n1 savings
        n1_savings_options = savings["n1"]["savings_options"]
        self.assertAlmostEqual(
            n1_savings_options["1yr_resource"]["monthly_savings"], 300 * 0.7 * 0.37
        )
        self.assertAlmostEqual(
            n1_savings_options["3yr_resource"]["monthly_savings"], 300 * 0.7 * 0.55
        )

        # Check e2 savings
        e2_savings_options = savings["e2"]["savings_options"]
        self.assertAlmostEqual(
            e2_savings_options["1yr_flex"]["monthly_savings"], 50 * 0.7 * 0.28
        )


if __name__ == "__main__":
    unittest.main()
