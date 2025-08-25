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

# Install the project in editable mode, which also installs all dependencies
echo "📦 Installing project and dependencies from pyproject.toml..."
pip install -e .

# Set up Google Cloud authentication
echo "🔐 Setting up authentication..."
if [[ -z "${GOOGLE_APPLICATION_CREDENTIALS}" ]]; then
    echo "Using Application Default Credentials. Please follow the prompts to authenticate."
    gcloud auth application-default login --quiet
fi

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data logs reports

# Copy config template if not exists
if [ ! -f "config.yaml" ]; then
    echo "📝 Creating config.yaml from example..."
    cp config.yaml.example config.yaml 2>/dev/null || echo "Please create and configure config.yaml"
fi

# Create a dated copy of the main notebook for this month's analysis
NOTEBOOK_TEMPLATE="notebooks/CUD_Analysis_Walkthrough.ipynb"
DATED_NOTEBOOK="notebooks/$(date +%Y-%m)_CUD_Analysis_Platform.ipynb"

if [ -f "$NOTEBOOK_TEMPLATE" ]; then
    cp "$NOTEBOOK_TEMPLATE" "$DATED_NOTEBOOK"
    echo "✅ Created a new notebook for this month's analysis: ${DATED_NOTEBOOK}"
else
    echo "⚠️  Warning: Notebook template not found at ${NOTEBOOK_TEMPLATE}"
fi

echo "✅ Setup complete! You can now run the notebook."
echo "📓 Open ${DATED_NOTEBOOK} to start"
