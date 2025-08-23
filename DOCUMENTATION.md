# 📖 Documentation

This document provides detailed documentation for the **Cloud FinOps CUD Analysis Platform** library.

## 🏗️ Project Structure

The project is organized as a standard Python package:

```
.
├── config.yaml
├── notebooks
│   └── 2025-08_CUD_Analysis_Platform.ipynb
├── src
│   └── finops_analysis_platform
│       ├── __init__.py
│       ├── advanced.py
│       ├── cli.py
│       ├── config
│       │   └── machine_discounts.yaml
│       ├── config_manager.py
│       ├── core.py
│       ├── data_loader.py
│       └── reporting.py
└── tests
    ├── test_advanced.py
    └── test_core.py
```

## 🧩 Core Modules

### `config_manager.py`

#### `ConfigManager`

This class handles loading the application's configuration.

- **`__init__(self, config_path='config.yaml', env_path='.env')`**: Initializes the manager. It loads the base configuration from the specified YAML file and then overrides any values with environment variables found in the `.env` file.
- **`get(self, key, default=None)`**: Retrieves a configuration value for a given key.

### `data_loader.py`

#### `GCSDataLoader`

This class is responsible for loading data from Google Cloud Storage.

- **`__init__(self, bucket_name)`**: Initializes the data loader with the name of the GCS bucket.
- **`load_all_data(self)`**: Loads all CSV files from the predefined GCS folder structure (`data/billing/`, `data/recommendations/`, etc.). If it cannot connect to GCS, it generates sample data for demonstration.

### `core.py`

#### `MachineTypeDiscountMapping`

This class manages the mapping of GCP machine types to their various discount rates (1-year CUD, 3-year CUD, Flex CUD, etc.).

- **`__init__(self, config_path=None)`**: Initializes the class, loading the discount rates from the `machine_discounts.yaml` file.
- **`get_discount(self, machine_type, discount_type)`**: Returns the discount rate for a specific machine type and discount type.
- **`get_family(self, machine_type)`**: Returns the family (e.g., "General Purpose", "Compute Optimized") for a given machine type.

#### `CUDAnalyzer`

This is the main analysis engine.

- **`__init__(self, config_manager, billing_data)`**: Initializes the analyzer with a `ConfigManager` instance and a pandas DataFrame containing the billing data.
- **`generate_comprehensive_analysis(self)`**: Runs the full suite of CUD analysis, including spend distribution, savings calculations, portfolio recommendations, and risk assessment. Returns a dictionary with the analysis results.

### `reporting.py`

#### `PDFReportGenerator`

This class generates a professional, multi-page PDF report summarizing the analysis results.

- **`__init__(self, config_manager)`**: Initializes the report generator with a `ConfigManager` instance.
- **`generate_report(self, analysis)`**: Generates the PDF report from the analysis results dictionary. Returns the filename of the generated report.

#### `create_dashboard(analysis)`

This function generates an interactive Plotly dashboard to visualize the analysis results.

## 🖥️ Command-Line Interface (CLI)

The CLI provides an easy way to run the analysis from the command line.

### `finops-cli run`

This command runs the entire analysis pipeline.

**Options:**
- `--config TEXT`: Path to the configuration file. Defaults to `config.yaml`.

**Example:**
```bash
finops-cli run --config /path/to/your/config.yaml
```

---
*Author: andrewanolasco@ | Version: V1.0.0 | Date: August 2025*
