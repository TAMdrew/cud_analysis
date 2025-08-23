# 📖 Documentation

This document provides detailed documentation for the **Cloud FinOps CUD Analysis Platform** library (V2.0.0).

## 🏗️ Project Structure

The project is organized as a standard Python package:

```
.
├── config.yaml
├── notebooks
│   ├── CUD_Analysis_Walkthrough.ipynb
│   └── AI_Powered_Analysis.ipynb
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
│       ├── gemini_service.py
│       └── reporting.py
└── tests
    └── ...
```

## 🧩 Core Modules

### `config_manager.py`

#### `ConfigManager`

Handles loading the application's configuration from YAML and environment variables.

- **`__init__(self, config_path='config.yaml', env_path='.env')`**: Initializes the manager.
- **`get(self, key, default=None)`**: Retrieves a configuration value. Supports dot notation for nested keys (e.g., `'gcp.project_id'`).

### `data_loader.py`

#### `GCSDataLoader`

Responsible for loading data from Google Cloud Storage.

- **`__init__(self, bucket_name)`**: Initializes the data loader with a GCS bucket name.
- **`load_all_data(self)`**: Loads all CSV files from the predefined GCS folder structure. Falls back to generating realistic sample data if GCS is unavailable.

### `core.py`

#### `MachineTypeDiscountMapping`

Manages the mapping of GCP machine types to their various discount rates.

- **`__init__(self, config_path=None)`**: Initializes the class, loading discount rates from `config/machine_discounts.yaml`.
- **`get_discount(self, machine_type, discount_type)`**: Returns the discount rate for a specific machine type and discount type.

#### `CUDAnalyzer`

The main analysis engine.

- **`__init__(self, config_manager, billing_data)`**: Initializes the analyzer. It validates that the `billing_data` DataFrame contains the required columns (`Cost` and a SKU column) before proceeding.
- **`generate_comprehensive_analysis(self)`**: Runs the full suite of CUD analysis.

### `reporting.py`

#### `PDFReportGenerator`

Generates professional, multi-page PDF reports.

- **`__init__(self, config_manager)`**: Initializes the report generator.
- **`generate_report(self, analysis)`**: Generates a PDF report. The theme (colors) and company logo are customizable via the `config.yaml` file.

#### `create_dashboard(analysis, config_manager)`

Generates an interactive Plotly dashboard to visualize the analysis results.

### `gemini_service.py`

#### `initialize_gemini(project_id, location)`

Initializes and returns a Gemini client.

#### `generate_content(client, model_id, prompt, tools)`

Generates content using the Gemini API with a specified list of tools. This allows for flexible use of features like Code Execution and URL Context.

## 🖥️ Command-Line Interface (CLI)

The CLI provides an easy way to run the analysis from the command line.

### `finops-cli run`

Runs the entire analysis pipeline.
- **`--config TEXT`**: Path to the configuration file.

### `finops-cli profile`

Profiles a specific dataset.
- **`--dataset TEXT`**: Name of the dataset to profile (e.g., "billing").

---
*Author: andrewanolasco@ (Maintained by Jules) | Version: V2.0.0 | Date: August 2025*
