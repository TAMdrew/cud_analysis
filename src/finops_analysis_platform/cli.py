import click
from .config_manager import ConfigManager
from .data_loader import GCSDataLoader
from .core import CUDAnalyzer
from .reporting import create_dashboard, PDFReportGenerator

@click.group()
def main():
    """A CLI for the FinOps CUD Analysis Platform."""
    pass

@main.command()
@click.option('--config', default='config.yaml', help='Path to the configuration file.')
def run(config):
    """Run the CUD analysis."""
    click.echo("🚀 Starting FinOps CUD Analysis...")

    # Load configuration
    config_manager = ConfigManager(config_path=config)
    click.echo(f"✅ Loaded configuration from {config}")

    # Load data
    gcs_config = config_manager.get('gcs', {})
    loader = GCSDataLoader(bucket_name=gcs_config.get('bucket_name'))
    data = loader.load_all_data()
    billing_data = data.get('billing')

    # Run analysis
    analyzer = CUDAnalyzer(config_manager=config_manager, billing_data=billing_data)
    analysis = analyzer.generate_comprehensive_analysis()
    click.echo("✅ Analysis complete!")

    # Generate reports
    if config_manager.get('reporting', {}).get('generate_pdf', True):
        pdf_generator = PDFReportGenerator(config_manager=config_manager)
        report_filename = pdf_generator.generate_report(analysis)
        click.echo(f"📄 PDF report generated: {report_filename}")

        # Upload to GCS if available
        if loader.storage_client:
            if loader.save_report_to_gcs(report_filename, report_filename):
                click.echo(f"☁️ Report uploaded to GCS: gs://{loader.bucket_name}/reports/cfo_dashboard/{report_filename}")

    # Create dashboard
    if config_manager.get('reporting', {}).get('create_dashboard', False):
        create_dashboard(analysis)
        click.echo("📊 Dashboard created.")

    click.echo("🎉 FinOps CUD Analysis finished successfully!")

if __name__ == '__main__':
    main()
