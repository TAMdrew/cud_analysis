# ☁️ Cloud FinOps CUD Analysis Platform 💰

A production-ready tool for analyzing Google Cloud Committed Use Discounts (CUDs) with CFO-level reporting capabilities, designed for Google Cloud notebook environments (Colab Enterprise, Vertex AI Workbench).

## ✨ Features

- **📈 Machine-Type-Specific Analysis**: 100% coverage of GCP machine types including GPUs
- **🔄 Automated GCS Integration**: Direct loading from Google Cloud Storage buckets
- **🔬 Advanced Analytics**: Portfolio optimization, Monte Carlo simulations, VaR/CVaR analysis
- **📊 Executive Reporting**: Professional PDF reports with interactive dashboards
- **🤖 AI-Powered Insights**: Use Gemini to perform interactive analysis and generate insights with natural language prompts
- **⚙️ Zero Configuration**: Smart defaults with optional customization

## 🚀 Quick Start

### 1. 📦 Installation & Setup

Clone the repository and run the setup script. This will install all necessary dependencies.

#### Option A: Google Colab / Colab Enterprise
```python
# First, clone the repository in your notebook
!git clone https://github.com/TAMdrew/cud_analysis.git
!cd cud_analysis && bash scripts/setup_gcp_notebook.sh

# Import the modules
import sys
sys.path.append('/content/cud_analysis')
```

#### Option B: Vertex AI Workbench
```bash
# Clone in terminal
git clone https://github.com/TAMdrew/cud_analysis.git
cd cud_analysis
bash scripts/setup_gcp_notebook.sh
```

### 2. 📝 Configuration

Copy the example configuration file and customize it to your needs:

```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your settings
```

At a minimum, set your GCS bucket name and GCP project ID:

```yaml
gcs:
  bucket_name: "your-bucket-name"  # Your GCS bucket with billing CSVs
gcp:
  project_id: "your-project-id"    # Your GCP project ID
```

### 3. 🏃‍♀️ Run Analysis

You can run the analysis using the **Jupyter Notebooks** or the **Command-Line Interface (CLI)**.

#### Jupyter Notebooks
- **`notebooks/2025-08_CUD_Analysis_Platform.ipynb`**: A step-by-step guide to running the core CUD analysis
- **`notebooks/gemini_powered_analysis.ipynb`**: An interactive notebook that uses Gemini to perform ad-hoc analysis and generate insights

Navigate to the notebook and execute the cells sequentially.

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

*Author: andrewanolasco@ | Version: V1.0.0 | Date: August 2025*
