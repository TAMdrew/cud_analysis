# Cloud FinOps CUD Analysis Platform

A production-ready, modular, and extensible tool for analyzing Google Cloud Committed Use Discounts (CUDs) with CFO-level reporting capabilities. This refactored version (V2.0.0) is designed for scalability, maintainability, and easy integration into automated FinOps workflows.

## Features

- **Modular Architecture**: A clean, object-oriented design that separates concerns for data loading, analysis, and reporting.
- **Command-Line Interface (CLI)**: Run analyses from the command line for easy automation and integration.
- **Extensible Configuration**: A central `config.yaml` file, overridable with environment variables for flexible deployment.
- **Machine-Type-Specific Analysis**: 100% coverage of GCP machine types, including GPUs, with discount rates managed in an external config file.
- **Advanced Analytics**: Optional modules for portfolio optimization, Monte Carlo simulations, and VaR/CVaR analysis.
- **Automated GCS Integration**: Direct loading from Google Cloud Storage buckets.
- **Executive Reporting**: Professional PDF reports and interactive dashboards.

## Quick Start

### 1. Installation

Clone the repository and install the package in editable mode. This will also install all the necessary dependencies.

```bash
git clone https://github.com/TAMdrew/cud_analysis.git
cd cud_analysis
pip install -e .
```

### 2. Configuration

Copy the `config.yaml.example` to `config.yaml` and customize it to your needs. At a minimum, you should set your GCS bucket name.

```bash
cp config.yaml.example config.yaml
# Now edit config.yaml
```

You can also set environment variables to override the values in `config.yaml`. See `.env.example` for a list of available variables.

### 3. CLI Usage

The easiest way to run an analysis is with the command-line interface.

```bash
finops-cli run --config /path/to/your/config.yaml
```

If you don't provide a `--config` path, it will look for `config.yaml` in the current directory.

### 4. Library Usage (in a Notebook or Script)

You can also use the library directly in your own Python scripts or Jupyter notebooks. See `notebooks/2025-08_CUD_Analysis_Platform.ipynb` for a detailed example.

Here's a basic example:

```python
from finops_analysis_platform.config_manager import ConfigManager
from finops_analysis_platform.data_loader import GCSDataLoader
from finops_analysis_platform.core import CUDAnalyzer
from finops_analysis_platform.reporting import create_dashboard, PDFReportGenerator

# 1. Load Configuration
config_manager = ConfigManager(config_path='config.yaml')

# 2. Load Data
gcs_config = config_manager.get('gcs', {})
loader = GCSDataLoader(bucket_name=gcs_config.get('bucket_name'))
data = loader.load_all_data()
billing_data = data.get('billing')

# 3. Run Analysis
analyzer = CUDAnalyzer(config_manager=config_manager, billing_data=billing_data)
analysis = analyzer.generate_comprehensive_analysis()

# 4. Generate Reports
pdf_generator = PDFReportGenerator(config_manager=config_manager)
report_filename = pdf_generator.generate_report(analysis)
print(f"Report generated: {report_filename}")
```

## Data Structure

Place your billing CSV files in the following GCS structure:

```
gs://your-bucket-name/
├── data/billing/           # Billing export CSVs
├── data/recommendations/   # Cost recommender exports (optional)
└── data/manual_analysis/   # Manual analysis files (optional)
```

## Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed usage instructions and API reference.

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Version: V2.0.0 | Date: August 2025*
