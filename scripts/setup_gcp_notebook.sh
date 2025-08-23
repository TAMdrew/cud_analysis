#!/bin/bash
# Setup script for Google Cloud Notebooks (Vertex AI Workbench / Colab Enterprise)
# Author: andrewanolasco@
# Version: V1.0.0
# Date: August 2025

echo "🚀 Setting up Cloud FinOps CUD Analysis for GCP Notebooks..."

# Check if running in Google Cloud environment
if [[ -f "/opt/deeplearning/bin/env-setup.sh" ]]; then
    echo "✅ Detected Vertex AI Workbench environment"
elif [[ -d "/content" ]]; then
    echo "✅ Detected Google Colab environment"
else
    echo "⚠️  Not running in a Google Cloud notebook environment"
fi

# Install required packages
echo "📦 Installing Python packages..."
pip install -q pandas numpy numpy-financial
pip install -q google-cloud-storage google-cloud-bigquery google-auth
pip install -q plotly matplotlib seaborn
pip install -q scikit-learn scipy
pip install -q reportlab
pip install -q python-dotenv pyyaml

# Set up Google Cloud authentication
echo "🔐 Setting up authentication..."
if [[ -z "${GOOGLE_APPLICATION_CREDENTIALS}" ]]; then
    echo "Using Application Default Credentials"
    gcloud auth application-default login --quiet
fi

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data/sample logs reports

# Copy config template if not exists
if [ ! -f "config.yaml" ]; then
    echo "📝 Creating config.yaml from template..."
    cp config.yaml.template config.yaml 2>/dev/null || echo "Please configure config.yaml"
fi

echo "✅ Setup complete! You can now run the notebook."
echo "📓 Open notebooks/2025-08_CUD_Analysis_Platform.ipynb to start"
