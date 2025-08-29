# 📖 Documentation

This document provides detailed documentation for the **Cloud FinOps CUD Analysis Platform** library (V2.1.0).

## 🏗️ Project Structure

The project is organized as a standard Python package:

```
.
├── AGENTS.md
├── config.yaml
├── notebooks
│   ├── CUD_Analysis_Walkthrough.ipynb
│   ├── AI_Powered_Analysis.ipynb
│   └── Automated_CUD_Analysis.ipynb
├── src
│   └── finops_analysis_platform
│       └── ...
└── tests
    └── ...
```

## 🧱 Data Models (`models.py`)

To ensure robustness and clarity, the analysis engine uses a set of strongly-typed data classes to represent its output.

-   **`AnalysisResults`**: The main container for a complete analysis run. It holds all other data models.
-   **`PortfolioRecommendation`**: Describes the recommended CUD portfolio, including a list of layers and total savings.
-   **`PortfolioLayer`**: Represents a single recommendation for a specific machine type (e.g., "Commit to 3-Year CUD for N2 machines").
-   **`RiskAssessment`**: Contains the overall risk level and a breakdown of risk by machine type.

## 🧩 Core Modules

### `config_manager.py`

Handles loading the application's configuration from `config.yaml`. The new `analysis.risk_tolerance` parameter (`low`, `medium`, `high`) is used by the AI portfolio optimizer.

### `data_loader.py`

- **`GCSDataLoader`**: Responsible for loading data from Google Cloud Storage.
- **`load_data_from_config(config_manager)`**: A new helper function that streamlines data loading in the notebooks.

### `core.py`

#### `CUDAnalyzer`
The main analysis engine. It now includes a powerful new method for AI-driven analysis.

- **`generate_comprehensive_analysis(self)`**: Runs the full suite of CUD analysis, now including the AI portfolio optimization.
- **`generate_cud_portfolio_optimization(self, savings_by_machine)`**: A new method that uses Gemini to recommend a risk-adjusted CUD portfolio based on the `risk_tolerance` set in `config.yaml`.

### `reporting.py`

Generates professional PDF reports and interactive dashboards. The `generate_report` function now accepts a `filename` argument to customize the output file name.

### `gemini_service.py`

The Gemini service has been significantly enhanced for cost, performance, and robustness.

- **`_get_model_for_prompt(prompt)`**: Dynamically selects a cost-effective model (`gemini-1.5-pro` or `gemini-1.5-flash`) based on prompt complexity.
- **`create_cached_content_from_df(client, model, df)`**: Creates a context cache from a pandas DataFrame to reduce cost and latency on repeated queries.
- **`generate_content(...)`**: Now includes robust error handling and can leverage a context cache.

## 📓 Jupyter Notebooks

### `CUD_Analysis_Walkthrough.ipynb`
A step-by-step guide to the core CUD analysis. It has been refactored to be more modular.

### `AI_Powered_Analysis.ipynb`
A **truly interactive tool** for ad-hoc analysis.
- Uses `ipywidgets` for user input, allowing you to ask any question about your data.
- Showcases Code Execution, URL Context, and the new AI Portfolio Optimization feature.

### `Automated_CUD_Analysis.ipynb`
A new, non-interactive notebook designed for **programmatic execution and orchestration**.
- Can be run with tools like `papermill` and integrated into **Vertex AI Pipelines**.
- Key parameters like the config path and output report name are injectable.

## 🖥️ Command-Line Interface (CLI)

The CLI provides an easy way to run the analysis from the command line.

- **`finops-cli run`**: Runs the entire analysis pipeline.
- **`finops-cli profile`**: Profiles a specific dataset.

---
*Author: andrewanolasco@ (Maintained by Jules) | Version: V2.1.0 | Date: August 2025*
