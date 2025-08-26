"""Command-Line Interface for the FinOps CUD Analysis Platform.

This module provides a CLI for running CUD analysis, generating reports,
and profiling datasets directly from the command line.
"""

import click

from .config_manager import ConfigManager
from .core import CUDAnalyzer
from .data_loader import get_data_loader
from .discount_mapping import MachineTypeDiscountMapping
from .portfolio_recommender import AIPortfolioRecommender, RuleBasedPortfolioRecommender
from .profiler import create_profile_report
from .reporting import PDFReportGenerator, create_dashboard
from .risk_assessor import RiskAssessor
from .savings_calculator import SavingsCalculator
from .spend_analyzer import SpendAnalyzer


@click.group()
def main():
    """A CLI for the FinOps CUD Analysis Platform."""


@main.command()
@click.option("--config", default="config.yaml", help="Path to the configuration file.")
def run(config):
    """Run the CUD analysis."""
    click.echo("🚀 Starting FinOps CUD Analysis...")

    # Load configuration
    config_manager = ConfigManager(config_path=config)
    click.echo(f"✅ Loaded configuration from {config}")

    # Load data
    loader = get_data_loader(config_manager)
    data = loader.load_all_data()
    billing_data = data.get("billing")

    # Initialize components
    discount_mapping = MachineTypeDiscountMapping()
    spend_analyzer = SpendAnalyzer(discount_mapping)
    savings_calculator = SavingsCalculator(config_manager, discount_mapping)
    rule_based_recommender = RuleBasedPortfolioRecommender()
    ai_recommender = AIPortfolioRecommender(config_manager)
    risk_assessor = RiskAssessor()

    # Run analysis
    analyzer = CUDAnalyzer(
        config_manager=config_manager,
        spend_analyzer=spend_analyzer,
        savings_calculator=savings_calculator,
        rule_based_recommender=rule_based_recommender,
        ai_recommender=ai_recommender,
        risk_assessor=risk_assessor,
        billing_data=billing_data,
    )
    analysis = analyzer.generate_comprehensive_analysis()
    click.echo("✅ Analysis complete!")

    # Generate reports
    if config_manager.get("reporting", {}).get("generate_pdf", True):
        pdf_generator = PDFReportGenerator(config_manager=config_manager)
        report_filename = pdf_generator.generate_report(analysis)
        click.echo(f"📄 PDF report generated: {report_filename}")

        # Upload to GCS if available
        if hasattr(loader, "storage_client") and loader.storage_client:
            if loader.save_report_to_gcs(report_filename, report_filename):
                click.echo(
                    f"☁️ Report uploaded to GCS: gs://{loader.bucket_name}/"
                    f"reports/cfo_dashboard/{report_filename}"
                )

    # Create dashboard
    if config_manager.get("reporting", {}).get("create_dashboard", False):
        create_dashboard(analysis, config_manager=config_manager)
        click.echo("📊 Dashboard created.")

    click.echo("🎉 FinOps CUD Analysis finished successfully!")


@main.command()
@click.option("--config", default="config.yaml", help="Path to the configuration file.")
@click.option(
    "--dataset",
    type=click.Choice(["billing", "recommendations", "manual_analysis"]),
    required=True,
    help="The dataset to profile.",
)
def profile(config, dataset):
    """Generate a data profiling report for a specific dataset."""
    click.echo(f"🚀 Starting data profiling for the '{dataset}' dataset...")

    # Load configuration
    config_manager = ConfigManager(config_path=config)
    click.echo(f"✅ Loaded configuration from {config}")

    # Load data
    loader = get_data_loader(config_manager)
    data = loader.load_all_data()

    if dataset in data:
        df = data[dataset]
        create_profile_report(df, title=f"{dataset.replace('_', ' ').title()} Dataset")
    else:
        click.echo(f"⚠️ Dataset '{dataset}' not found.")


if __name__ == "__main__":
    main()
