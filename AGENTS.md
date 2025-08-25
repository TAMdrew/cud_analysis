# 🤖 Agent Instructions for Cloud FinOps Analysis Platform

Welcome, fellow agent! This document provides instructions for working with the Cloud FinOps CUD Analysis Platform codebase. Adhering to these guidelines will ensure consistency and maintainability.

## 🚀 Project Overview

This is a Python-based platform for analyzing Google Cloud Committed Use Discounts (CUDs). It is designed to be run in Google Cloud notebook environments (Colab Enterprise, Vertex AI Workbench) and can be executed both interactively via Jupyter notebooks and programmatically via a CLI or orchestrated pipelines.

The core of the platform is the `finops_analysis_platform` library located in the `src/` directory.

### Key Components:
- **`src/finops_analysis_platform/core.py`**: Contains the main `CUDAnalyzer` class, which is the engine for all financial analysis.
- **`src/finops_analysis_platform/gemini_service.py`**: A service layer for interacting with the Google Gemini API. This is used for all AI-powered features.
- **`src/finops_analysis_platform/data_loader.py`**: Handles loading data from Google Cloud Storage.
- **`config.yaml`**: The main configuration file for the entire application. All parameters should be managed here.
- **`notebooks/`**: Contains user-facing notebooks for running analysis.
  - `CUD_Analysis_Walkthrough.ipynb`: A step-by-step guide.
  - `AI_Powered_Analysis.ipynb`: An interactive analysis tool.
  - `Automated_CUD_Analysis.ipynb`: A parameterized notebook for automated execution.

## 🛠️ Development Workflow

### 1. Environment Setup

To set up the development environment, run the setup script from the repository root:

```bash
bash scripts/setup_gcp_notebook.sh
```

This will install all necessary dependencies listed in `requirements.txt`.

### 2. Running the Analysis

You can run the analysis using the notebooks or the CLI.

- **Notebooks**: Open any of the notebooks in the `notebooks/` directory and execute the cells. Ensure your `config.yaml` is correctly configured.
- **CLI**:
  ```bash
  finops-cli run --config /path/to/your/config.yaml
  ```

### 3. Running Tests

This project uses `pytest`. To run the test suite, execute the following command from the repository root:

```bash
python -m pytest
```

**IMPORTANT**: Before submitting any changes, you **must** run the tests to ensure you have not introduced any regressions.

## 📝 Coding Conventions

- **Style**: Follow the PEP 8 style guide. Use `black` for code formatting.
- **Docstrings**: All public functions and classes must have Google-style docstrings.
- **Type Hinting**: All function signatures must include type hints.
- **Configuration**: Do not hardcode any values (e.g., project IDs, bucket names) in the source code. All configuration should be managed through `config.yaml` and accessed via the `ConfigManager`.
- **Logging**: Use the `logging` module for all output. Do not use `print()`.

## ✅ Pre-Submission Checklist

Before submitting your work, please ensure you have completed the following:

1.  **Run all tests**: `python -m pytest`
2.  **Verify notebooks**: Ensure all notebooks run from top to bottom without errors.
3.  **Update Documentation**: If you add or change any features, update `DOCUMENTATION.md` accordingly.
