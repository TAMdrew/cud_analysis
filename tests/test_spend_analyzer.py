import unittest
from pathlib import Path

import pandas as pd

from finops_analysis_platform.discount_mapping import MachineTypeDiscountMapping
from finops_analysis_platform.spend_analyzer import SpendAnalyzer


class TestSpendAnalyzer(unittest.TestCase):
    """Test suite for the SpendAnalyzer class."""

    def setUp(self):
        """Set up a test instance of the spend analyzer."""
        self.test_discounts_path = Path("test_discounts.yaml")
        with open(self.test_discounts_path, "w") as f:
            f.write(
                """
discounts: {}
families: {}
prefixes: ['n1', 'e2']
"""
            )
        self.discount_mapping = MachineTypeDiscountMapping(
            config_path=self.test_discounts_path
        )
        self.spend_analyzer = SpendAnalyzer(self.discount_mapping)

    def tearDown(self):
        """Clean up the dummy discount file."""
        if self.test_discounts_path.exists():
            self.test_discounts_path.unlink()

    def test_analyze_machine_distribution(self):
        """Test the analysis of machine spend distribution."""
        billing_data = pd.DataFrame(
            {
                "SKU": ["n1-standard-4", "e2-medium", "n1-standard-8"],
                "Cost": [100, 50, 200],
            }
        )
        distribution = self.spend_analyzer.analyze_machine_distribution(billing_data)
        self.assertIn("n1", distribution)
        self.assertIn("e2", distribution)
        self.assertAlmostEqual(distribution["n1"], 300)
        self.assertAlmostEqual(distribution["e2"], 50)

    def test_analyze_machine_distribution_empty_input(self):
        """Test the analysis with an empty or None DataFrame."""
        # Test with an empty DataFrame
        empty_df = pd.DataFrame({"SKU": [], "Cost": []})
        distribution_empty = self.spend_analyzer.analyze_machine_distribution(empty_df)
        self.assertIsInstance(distribution_empty, dict)
        self.assertGreater(len(distribution_empty), 0)  # Should return sample data

        # Test with None
        distribution_none = self.spend_analyzer.analyze_machine_distribution(None)
        self.assertIsInstance(distribution_none, dict)
        self.assertGreater(len(distribution_none), 0)  # Should also return sample data


if __name__ == "__main__":
    unittest.main()
