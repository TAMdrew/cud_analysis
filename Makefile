# Makefile for the FinOps CUD Analysis Platform

.PHONY: help install test lint clean

# Set the default virtual environment directory
VENV_DIR := finops_venv_py312
ACTIVATE := source $(VENV_DIR)/bin/activate

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install    Create a virtual environment and install dependencies"
	@echo "  test       Run the pytest test suite"
	@echo "  lint       Run pre-commit hooks (linting, formatting, type-checking)"
	@echo "  clean      Remove temporary files (e.g., caches)"


install:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo ">>> Creating virtual environment in $(VENV_DIR)...\"; \
		python3 -m venv $(VENV_DIR); \
	fi
	@echo ">>> Installing dependencies from pyproject.toml..."
	@$(ACTIVATE) && python -m pip install --upgrade pip && python -m pip install -e .[dev]
	@echo "✅ Installation complete. Activate with: source $(VENV_DIR)/bin/activate"

test:
	@echo ">>> Running pytest suite..."
	@$(ACTIVATE) && pytest

lint:
	@echo ">>> Running pre-commit hooks..."
	@$(ACTIVATE) && pre-commit run --all-files

clean:
	@echo ">>> Removing temporary cache files..."
	@rm -rf .pytest_cache .mypy_cache .ruff_cache coverage.xml
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@echo "✅ Clean complete."
