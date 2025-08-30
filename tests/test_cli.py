"""Tests for the Command-Line Interface."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from finops_analysis_platform.cli import main
from finops_analysis_platform.data_loader import SampleDataLoader


def test_run_command_executes_successfully():
    """Test that the 'run' command executes without errors."""
    runner = CliRunner()
    with (
        patch("finops_analysis_platform.cli.PDFReportGenerator") as mock_pdf_generator,
        patch(
            "finops_analysis_platform.cli.AIPortfolioRecommender"
        ) as mock_ai_recommender,
        # Mock the data loader to prevent any actual GCS calls
        patch("finops_analysis_platform.cli.get_data_loader") as mock_get_data_loader,
    ):
        # Configure the mocks
        mock_pdf_instance = mock_pdf_generator.return_value
        mock_pdf_instance.generate_report.return_value = "test_report.pdf"
        mock_ai_recommender.return_value = MagicMock()

        # Ensure the data loader returns sample data
        mock_loader_instance = SampleDataLoader()
        mock_get_data_loader.return_value = mock_loader_instance

        result = runner.invoke(main, ["run"])

        assert result.exit_code == 0, f"CLI command failed with output: {result.output}"
        assert "FinOps CUD Analysis finished successfully!" in result.output
        mock_pdf_instance.generate_report.assert_called_once()
        mock_ai_recommender.assert_called_once()
        mock_get_data_loader.assert_called_once()


def test_profile_command_executes_successfully():
    """Test that the 'profile' command executes without errors."""
    runner = CliRunner()
    # We patch the function that actually creates the file
    with patch(
        "finops_analysis_platform.cli.create_profile_report"
    ) as mock_create_report:
        result = runner.invoke(main, ["profile", "--dataset", "billing"])

        assert result.exit_code == 0
        assert "Starting data profiling" in result.output
        # Verify that the report creation function was called
        mock_create_report.assert_called_once()


def test_profile_command_handles_missing_dataset():
    """Test the profile command with a dataset that doesn't exist."""
    runner = CliRunner()
    with patch(
        "finops_analysis_platform.cli.create_profile_report"
    ) as mock_create_report:
        result = runner.invoke(main, ["profile", "--dataset", "nonexistent"])

        assert result.exit_code != 0
        assert "Invalid value for '--dataset'" in result.output
        # Ensure the report function was NOT called
        mock_create_report.assert_not_called()
