# ☁️ Cloud FinOps CUD Analysis Platform 💰

A production-ready, staff-level tool for analyzing Google Cloud Committed Use Discounts (CUDs) with CFO-level reporting capabilities, designed for Google Cloud notebook environments (Colab Enterprise, Vertex AI Workbench).

## ✨ Features

- **📈 Granular Analysis**: 100% coverage of GCP machine types, including GPUs.
- **🔄 Automated GCS Integration**: Seamlessly loads data from Google Cloud Storage.
- **🔬 Advanced Analytics**: Portfolio optimization, risk assessment, and forecasting.
- **📊 Customizable Executive Reporting**: Generate professional PDF reports with configurable themes and company logos.
- **🤖 AI-Powered Insights with Gemini 2.5 Pro**: Utilize Gemini 2.5 Pro for interactive analysis, including advanced features like **Code Execution** and **URL Context** to query data and external sources with natural language.
- **⚙️ Zero Configuration Start**: Get started quickly with smart defaults, with deep customization available via a comprehensive `config.yaml`.

## 🚀 Quick Start

### 1. 🛠️ Installation & Setup

Getting started is easy! Just clone the repository and run the setup script. This script handles everything, from installing dependencies to preparing your analysis notebook.

#### Option A: Google Colab / Colab Enterprise ☁️
```python
# 1. Clone the repository in your notebook
!git clone https://github.com/TAMdrew/cud_analysis.git

# 2. Run the setup script
!cd cud_analysis && bash scripts/setup_gcp_notebook.sh

# 💡 **Note:** The setup script creates a new, dated copy of the main analysis notebook for you (e.g., `notebooks/2025-08_CUD_Analysis_Platform.ipynb`). This is the notebook you should use!

# 3. Add the project to your Python path
import sys
sys.path.append('/content/cud_analysis')
```

#### Option B: Vertex AI Workbench 💻
```bash
# 1. Clone the repository in the terminal
git clone https://github.com/TAMdrew/cud_analysis.git

# 2. Navigate into the directory and run the setup script
cd cud_analysis
bash scripts/setup_gcp_notebook.sh

# 💡 **Note:** The setup script creates a new, dated copy of the main analysis notebook for you (e.g., `notebooks/2025-08_CUD_Analysis_Platform.ipynb`). This is the notebook you should use!
```

### 2. 📝 Configuration

Copy the example configuration file and customize it to your needs:

```bash
cp .env.example .env
# Edit config.yaml with your settings, including GCS bucket and project ID.
# You can also set environment variables in .env
```

At a minimum, set your GCS bucket name and GCP project ID in `config.yaml`:

```yaml
gcs:
  bucket_name: "your-bucket-name"
gcp:
  project_id: "your-project-id"
```

### 3. 🏃‍♀️ Run Analysis

You can run the analysis using the **Jupyter Notebooks** or the **Command-Line Interface (CLI)**.

#### Jupyter Notebooks
- **`notebooks/CUD_Analysis_Walkthrough.ipynb`**: A comprehensive, step-by-step guide to running the core CUD analysis and generating reports.
- **`notebooks/AI_Powered_Analysis.ipynb`**: An interactive notebook that uses Gemini 2.5 Pro to perform ad-hoc analysis using natural language, code execution, and URL context.

Navigate to the notebooks and execute the cells sequentially.

#### Command-Line Interface (CLI)
```bash
# Run the core CUD analysis
finops-cli run --config /path/to/your/config.yaml

# Profile a dataset
finops-cli profile --dataset billing
```

## 🗂️ Data Structure

Place your billing CSV files in the following GCS structure:

```
gs://your-bucket-name/
├── data/billing/           # Billing export CSVs
├── data/recommendations/   # Cost recommender exports (optional)
└── data/manual_analysis/   # Manual analysis files (optional)
```

## 📖 Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed usage instructions and API reference.

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

**Disclaimer**: This repository contains tools for Google Cloud cost optimization and is not affiliated with or officially supported by Google Cloud Platform.

## 💬 Support

For issues or questions, please open an issue in the repository.

---

*Author: andrewanolasco@ (Maintained by Jules) | Version: V2.0.0 | Date: August 2025*
