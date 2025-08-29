import unittest
from unittest.mock import patch

from finops_analysis_platform.config_manager import ConfigManager
from finops_analysis_platform.models import PortfolioRecommendation
from finops_analysis_platform.portfolio_recommender import (
    AIPortfolioRecommender,
    RuleBasedPortfolioRecommender,
)


class TestRuleBasedPortfolioRecommender(unittest.TestCase):
    """Test suite for the RuleBasedPortfolioRecommender class."""

    def setUp(self):
        """Set up a test instance of the recommender."""
        self.recommender = RuleBasedPortfolioRecommender()

    def test_recommend_portfolio(self):
        """Test the portfolio recommendation logic."""
        savings_by_machine = {
            "n1": {
                "monthly_spend": 300,
                "stable_workload": 210,
                "savings_options": {
                    "1yr_resource": {"monthly_savings": 77.7},
                    "3yr_resource": {"monthly_savings": 115.5},
                },
            },
            "e2": {
                "monthly_spend": 50,
                "stable_workload": 35,
                "savings_options": {"1yr_flex": {"monthly_savings": 9.8}},
            },
        }
        portfolio = self.recommender.recommend_portfolio(savings_by_machine)

        self.assertIsInstance(portfolio, PortfolioRecommendation)
        self.assertEqual(len(portfolio.layers), 2)
        self.assertAlmostEqual(portfolio.total_monthly_savings, 125.3)


class TestAIPortfolioRecommender(unittest.TestCase):
    """Test suite for the AIPortfolioRecommender class."""

    def setUp(self):
        """Set up a test instance of the recommender."""
        self.config_manager = ConfigManager()
        self.config_manager.config = {
            "gcp": {"project_id": "test-project"},
            "analysis": {"risk_tolerance": "medium"},
        }

    @patch("finops_analysis_platform.portfolio_recommender.initialize_vertex_ai")
    @patch("finops_analysis_platform.portfolio_recommender.generate_content")
    def test_recommend_portfolio_with_ai(
        self, mock_generate_content, mock_initialize_vertex_ai
    ):
        """Test the AI portfolio recommendation logic."""
        mock_initialize_vertex_ai.return_value = True
        self.recommender = AIPortfolioRecommender(self.config_manager)

        mock_generate_content.return_value = (
            '{"strategy_summary": "test", "portfolio": []}'
        )

        savings_by_machine = {
            "n1": {
                "monthly_spend": 300,
                "family": "General Purpose",
                "savings_options": {
                    "1yr_resource": {"monthly_savings": 77.7},
                    "3yr_resource": {"monthly_savings": 115.5},
                },
            }
        }
        portfolio = self.recommender.recommend_portfolio(savings_by_machine)

        self.assertIn("strategy_summary", portfolio)
        self.assertEqual(portfolio["strategy_summary"], "test")
        mock_initialize_vertex_ai.assert_called_once_with(
            project_id="test-project", location="us-central1"
        )


if __name__ == "__main__":
    unittest.main()
