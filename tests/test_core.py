import unittest
from unittest.mock import MagicMock

import pandas as pd

from finops_analysis_platform.config_manager import ConfigManager
from finops_analysis_platform.core import CUDAnalyzer
from finops_analysis_platform.models import PortfolioRecommendation, RiskAssessment


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
        self.recommendation_analyzer = MagicMock()

        self.analyzer = CUDAnalyzer(
            config_manager=self.config_manager,
            spend_analyzer=self.spend_analyzer,
            savings_calculator=self.savings_calculator,
            rule_based_recommender=self.rule_based_recommender,
            ai_recommender=self.ai_recommender,
            risk_assessor=self.risk_assessor,
            recommendation_analyzer=self.recommendation_analyzer,
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
        self.rule_based_recommender.recommend_portfolio.return_value = (
            PortfolioRecommendation()
        )
        self.risk_assessor.assess_risk.return_value = RiskAssessment(
            overall_risk="LOW", recommendation=""
        )
        self.ai_recommender.recommend_portfolio.return_value = {"portfolio": []}
        self.recommendation_analyzer.analyze.return_value = {"Rightsize VM": 123.45}

        analysis = self.analyzer.generate_comprehensive_analysis()

        self.assertIsNotNone(analysis.machine_spend_distribution)
        self.assertIsNotNone(analysis.savings_by_machine)
        self.assertIsInstance(
            analysis.portfolio_recommendation, PortfolioRecommendation
        )
        self.assertEqual(analysis.risk_assessment.overall_risk, "LOW")
        self.assertIsNotNone(analysis.ai_portfolio_recommendation)
        self.assertIn("Rightsize VM", analysis.active_assist_summary)


if __name__ == "__main__":
    unittest.main()
