import unittest
from unittest.mock import MagicMock

import pandas as pd

from finops_analysis_platform.config_manager import ConfigManager
from finops_analysis_platform.core import CUDAnalyzer


class TestCUDAnalyzer(unittest.TestCase):
    """Test suite for the CUDAnalyzer class."""

    def setUp(self):
        """Set up a test instance of the CUD analyzer."""
        self.config_manager = ConfigManager()
        self.config_manager.config = {
            "analysis": {"target_utilization": 85},
            "cud_strategy": {"base_layer_coverage": 70},
        }

        self.billing_data = pd.DataFrame(
            {
                "SKU": ["n1-standard-4", "e2-medium", "n1-standard-8"],
                "Cost": [100, 50, 200],
            }
        )

        self.spend_analyzer = MagicMock()
        self.savings_calculator = MagicMock()
        self.rule_based_recommender = MagicMock()
        self.ai_recommender = MagicMock()
        self.risk_assessor = MagicMock()

        self.analyzer = CUDAnalyzer(
            config_manager=self.config_manager,
            spend_analyzer=self.spend_analyzer,
            savings_calculator=self.savings_calculator,
            rule_based_recommender=self.rule_based_recommender,
            ai_recommender=self.ai_recommender,
            risk_assessor=self.risk_assessor,
            billing_data=self.billing_data,
        )

    def test_generate_comprehensive_analysis(self):
        """Test the generation of a comprehensive analysis."""
        self.spend_analyzer.analyze_machine_distribution.return_value = {
            "n1": 300,
            "e2": 50,
        }
        self.savings_calculator.calculate_savings_by_machine.return_value = {
            "n1": {"savings_options": {}},
            "e2": {"savings_options": {}},
        }
        self.rule_based_recommender.recommend_portfolio.return_value = {"layers": []}
        self.risk_assessor.assess_risk.return_value = {"overall_risk": "LOW"}
        self.ai_recommender.recommend_portfolio.return_value = {"portfolio": []}

        analysis = self.analyzer.generate_comprehensive_analysis()

        self.assertIn("machine_spend_distribution", analysis)
        self.assertIn("savings_by_machine", analysis)
        self.assertIn("portfolio_recommendation", analysis)
        self.assertIn("risk_assessment", analysis)
        self.assertIn("ai_portfolio_recommendation", analysis)


if __name__ == "__main__":
    unittest.main()
