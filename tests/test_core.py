import unittest
import pandas as pd
from pathlib import Path

from finops_analysis_platform.core import CUDAnalyzer, MachineTypeDiscountMapping
from finops_analysis_platform.config_manager import ConfigManager

class TestMachineTypeDiscountMapping(unittest.TestCase):
    """Test suite for the MachineTypeDiscountMapping class."""

    def setUp(self):
        """Set up a test instance of the discount mapping."""
        self.test_discounts_path = Path("test_discounts.yaml")
        with open(self.test_discounts_path, "w") as f:
            f.write("""
discounts:
  n1: {'1yr_resource': 0.37, '3yr_resource': 0.55, '1yr_flex': 0.28, '3yr_flex': 0.46, 'sud': 0.30}
  e2: {'1yr_resource': 0.37, '3yr_resource': 0.55, '1yr_flex': 0.28, '3yr_flex': 0.46, 'sud': 0.20}
  gpu: {'1yr_resource': 0.20, '3yr_resource': 0.40, '1yr_flex': 0.10, '3yr_flex': 0.20, 'sud': 0.10}
families:
  'General Purpose': ['n1', 'e2']
  'GPU': ['gpu']
""")
        self.discount_mapping = MachineTypeDiscountMapping(config_path=self.test_discounts_path)

    def tearDown(self):
        """Clean up the dummy discount file."""
        if self.test_discounts_path.exists():
            self.test_discounts_path.unlink()

    def test_get_discount(self):
        """Test that the correct discount is returned."""
        self.assertEqual(self.discount_mapping.get_discount('n1-standard-4', '1yr_resource'), 0.37)
        self.assertEqual(self.discount_mapping.get_discount('e2-medium', '3yr_flex'), 0.46)
        self.assertEqual(self.discount_mapping.get_discount('gpu-t4-instance', '3yr_resource'), 0.40)
        self.assertIsNone(self.discount_mapping.get_discount('z3-standard-4', '1yr_resource'))

    def test_get_family(self):
        """Test that the correct machine family is returned."""
        self.assertEqual(self.discount_mapping.get_family('n1-highcpu-8'), 'General Purpose')
        self.assertEqual(self.discount_mapping.get_family('gpu-a100'), 'GPU')
        self.assertEqual(self.discount_mapping.get_family('c2-standard-8'), 'General Purpose') # default

class TestCUDAnalyzer(unittest.TestCase):
    """Test suite for the CUDAnalyzer class."""

    def setUp(self):
        """Set up a test instance of the CUD analyzer."""
        self.config = {
            'analysis': {'target_utilization': 85},
            'cud_strategy': {'base_layer_coverage': 70}
        }
        self.config_manager = ConfigManager()
        self.config_manager.config = self.config

        self.billing_data = pd.DataFrame({
            'SKU': ['n1-standard-4', 'e2-medium', 'n1-standard-8'],
            'Cost': [100, 50, 200]
        })

        self.analyzer = CUDAnalyzer(config_manager=self.config_manager, billing_data=self.billing_data)

        self.test_discounts_path = Path("test_discounts.yaml")
        with open(self.test_discounts_path, "w") as f:
            f.write("""
discounts:
  n1: {'1yr_resource': 0.37, '3yr_resource': 0.55, '1yr_flex': 0.28, '3yr_flex': 0.46, 'sud': 0.30}
  e2: {'1yr_resource': 0.37, '3yr_resource': 0.55, '1yr_flex': 0.28, '3yr_flex': 0.46, 'sud': 0.20}
families:
  'General Purpose': ['n1', 'e2']
""")
        self.analyzer.discount_mapping = MachineTypeDiscountMapping(config_path=self.test_discounts_path)

    def tearDown(self):
        """Clean up the dummy discount file."""
        if self.test_discounts_path.exists():
            self.test_discounts_path.unlink()

    def test_analyze_machine_distribution(self):
        """Test the analysis of machine spend distribution."""
        distribution = self.analyzer._analyze_machine_distribution()
        self.assertIn('n1', distribution)
        self.assertIn('e2', distribution)
        self.assertAlmostEqual(distribution['n1'], 300)
        self.assertAlmostEqual(distribution['e2'], 50)

    def test_calculate_savings_by_machine(self):
        """Test the calculation of savings by machine type."""
        distribution = {'n1': 300, 'e2': 50}
        savings = self.analyzer._calculate_savings_by_machine(distribution)

        self.assertIn('n1', savings)
        self.assertIn('e2', savings)

        # Check n1 savings
        n1_savings_options = savings['n1']['savings_options']
        self.assertAlmostEqual(n1_savings_options['1yr_resource']['monthly_savings'], 300 * 0.7 * 0.37)
        self.assertAlmostEqual(n1_savings_options['3yr_resource']['monthly_savings'], 300 * 0.7 * 0.55)

        # Check e2 savings
        e2_savings_options = savings['e2']['savings_options']
        self.assertAlmostEqual(e2_savings_options['1yr_flex']['monthly_savings'], 50 * 0.7 * 0.28)

if __name__ == '__main__':
    unittest.main()
