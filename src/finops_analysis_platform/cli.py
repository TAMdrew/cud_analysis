"""Command-Line Interface for the FinOps CUD Analysis Platform.

This module provides a CLI for running CUD analysis, generating reports,
and profiling datasets directly from the command line.
"""

import click

from .config_manager import ConfigManager
from .core import CUDAnalyzer
from .data_loader import GCSDataLoader
from .profiler import create_profile_report
from .reporting import PDFReportGenerator, create_dashboard


@click.group()
def main() -> None:
    """A CLI for the FinOps CUD Analysis Platform."""


def _generate_reports(
    analysis: dict, config_manager: ConfigManager, loader: GCSDataLoader
) -> None:
    """Generates and optionally uploads reports based on configuration."""
    # Generate PDF report
    if config_manager.get("reporting", {}).get("generate_pdf", True):
        pdf_generator = PDFReportGenerator(config_manager=config_manager)
        report_filename = pdf_generator.generate_report(analysis)
        click.echo(f"📄 PDF report generated: {report_filename}")

        # Upload to GCS if available
        if loader.storage_client and loader.save_report_to_gcs(
            report_filename, report_filename
        ):
            click.echo(
                f"☁️ Report uploaded to GCS: gs://{loader.bucket_name}/"
                f"reports/cfo_dashboard/{report_filename}"
            )

    # Create dashboard
    if config_manager.get("reporting", {}).get("create_dashboard", False):
        create_dashboard(analysis, config_manager=config_manager)
        click.echo("📊 Dashboard created.")


def _execute_analysis(config_manager: ConfigManager, loader: GCSDataLoader) -> None:
    """Core logic for running the CUD analysis and generating reports."""
    # Load data
    data = loader.load_all_data()
    billing_data = data.get("billing")

    # Instantiate analyzer with all its dependencies, including data
    analyzer = CUDAnalyzer(config_manager=config_manager, billing_data=billing_data)

    # Run analysis
    analysis = analyzer.generate_comprehensive_analysis()
    click.echo("✅ Analysis complete!")

    # Generate reports
    _generate_reports(analysis, config_manager, loader)


@main.command()
@click.option("--config", default="config.yaml", help="Path to the configuration file.")
def run(config: str) -> None:
    """Run the CUD analysis."""
    click.echo("🚀 Starting FinOps CUD Analysis...")

    # --- Dependency Setup ---
    # Setup dependencies that don't rely on runtime data.
    config_manager = ConfigManager(config_path=config)
    click.echo(f"✅ Loaded configuration from {config}")

    gcs_config = config_manager.get("gcs", {})
    loader = GCSDataLoader(bucket_name=gcs_config.get("bucket_name"))

    # --- Execute Core Logic ---
    _execute_analysis(config_manager, loader)

    click.echo("🎉 FinOps CUD Analysis finished successfully!")


@main.command()
@click.option("--config", default="config.yaml", help="Path to the configuration file.")
@click.option(
    "--dataset",
    type=click.Choice(["billing", "recommendations", "manual_analysis"]),
    required=True,
    help="The dataset to profile.",
)
def profile(config: str, dataset: str) -> None:
    """Generate a data profiling report for a specific dataset."""
    click.echo(f"🚀 Starting data profiling for the '{dataset}' dataset...")

    # Load configuration
    config_manager = ConfigManager(config_path=config)
    click.echo(f"✅ Loaded configuration from {config}")

    # Load data
    gcs_config = config_manager.get("gcs", {})
    loader = GCSDataLoader(bucket_name=gcs_config.get("bucket_name"))
    df = loader.load_single_dataset(dataset)

    if df is not None:
        create_profile_report(df, title=f"{dataset.replace('_', ' ').title()} Dataset")
    else:
        click.echo(f"⚠️ Could not load or find dataset '{dataset}'.")


if __name__ == "__main__":
    main()
