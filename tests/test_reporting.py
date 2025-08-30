"""Tests for the Reporting Module."""

import unittest
from unittest.mock import MagicMock, patch

from finops_analysis_platform.config_manager import ConfigManager
from finops_analysis_platform.models import (
    AnalysisResults,
    PortfolioRecommendation,
    RiskAssessment,
)
from finops_analysis_platform.reporting import PDFReportGenerator, create_dashboard


class TestReporting(unittest.TestCase):
    """Test suite for the reporting module."""

    def setUp(self):
        """Set up common objects for tests."""
        self.config_manager = ConfigManager()
        self.analysis_results = AnalysisResults(
            machine_spend_distribution={"n1": 1000},
            savings_by_machine={},
            portfolio_recommendation=PortfolioRecommendation(total_monthly_savings=100),
            risk_assessment=RiskAssessment(
                overall_risk="LOW", recommendation="", risk_distribution={"low": 1000}
            ),
            analysis_date=MagicMock(),
            config={},
        )

    @patch("plotly.graph_objects.Figure.show")
    def test_create_dashboard_runs_without_error(self, mock_show):
        """Test that the dashboard creation function executes without errors."""
        try:
            create_dashboard(self.analysis_results, self.config_manager)
        except Exception as e:
            self.fail(f"create_dashboard raised an exception: {e}")
        # mock_show.assert_called_once() # This can be added if you want to ensure it's called

    @patch("reportlab.platypus.SimpleDocTemplate.build")
    def test_generate_report_runs_without_error(self, mock_build):
        """Test that the PDF report generation function executes without errors."""
        generator = PDFReportGenerator(config_manager=self.config_manager)
        try:
            generator.generate_report(self.analysis_results, filename="test_report.pdf")
        except Exception as e:
            self.fail(f"generate_report raised an exception: {e}")
        mock_build.assert_called_once()


if __name__ == "__main__":
    unittest.main()
