"""Handles loading data from GCS and generating sample data.

This module provides the GCSDataLoader class which is responsible for
authenticating with Google Cloud Storage and loading billing, recommendations,
and other data files. If GCS access fails, it falls back to generating
realistic sample data for demonstration purposes.
"""

from __future__ import annotations

import io
import logging
import os
import random
from pathlib import Path
from typing import Dict, Union

import google.auth
import numpy as np
import pandas as pd
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage

from .config_manager import ConfigManager
from .data_loader_protocol import DataLoader

logger = logging.getLogger(__name__)

# --- Sample Data Generation Functions ---


def _generate_realistic_cost(usage: float, sku: str) -> float:
    """Generates a realistic cost based on usage and SKU."""
    base_cost_per_hour = {
        "n2": 0.1,
        "e2": 0.05,
        "c2": 0.15,
        "m1": 0.5,
        "t2": 0.08,
        "a2": 1.2,
        "gpu": 2.5,
    }
    sku_family = sku.split("-")[0]
    cost_multiplier = base_cost_per_hour.get(sku_family, 0.1)
    return usage * cost_multiplier * (1 + random.uniform(-0.1, 0.1))


def _generate_realistic_cost_vectorized(
    usage_series: pd.Series,
    sku_series: pd.Series,
) -> pd.Series:
    """Vectorized cost generation for better performance."""
    base_costs = {
        "n2": 0.1,
        "e2": 0.05,
        "c2": 0.15,
        "m1": 0.5,
        "t2": 0.08,
        "a2": 1.2,
        "gpu": 2.5,
    }

    # Extract SKU families
    sku_families = sku_series.str.split("-").str[0]

    # Map to cost multipliers
    cost_multipliers = sku_families.map(base_costs).fillna(0.1)

    # Generate random variations
    random_factors = 1 + np.random.uniform(-0.1, 0.1, len(usage_series))

    return usage_series * cost_multipliers * random_factors


def generate_sample_billing_data(rows: int = 1000) -> pd.DataFrame:
    """Generates a DataFrame with realistic sample billing data."""
    machine_types = [
        "n2-standard-8",
        "n2-highmem-4",
        "e2-standard-4",
        "c2-standard-16",
        "m1-megamem-96",
        "t2d-standard-8",
        "a2-highgpu-1g",
        "gpu-t4-instance",
    ]
    projects = [f"project-{chr(97 + i)}" for i in range(5)]
    start_times = pd.to_datetime(
        pd.to_datetime("now", utc=True)
        - pd.to_timedelta(np.random.rand(rows) * 90, "D")
    )
    data = {
        "SKU": np.random.choice(machine_types, rows),
        "Service": ["Compute Engine"] * rows,
        "Usage": np.random.gamma(2, 250, rows),
        "Project": np.random.choice(projects, rows, p=[0.4, 0.3, 0.15, 0.1, 0.05]),
        "Start Time": start_times,
    }
    df = pd.DataFrame(data)
    df["End Time"] = df["Start Time"] + pd.to_timedelta(
        np.random.randint(1, 24, rows), "h"
    )
    df["Cost"] = _generate_realistic_cost_vectorized(df["Usage"], df["SKU"])
    return df


def generate_sample_recommendations_data(rows: int = 50) -> pd.DataFrame:
    """Generates a DataFrame with sample recommendations data."""
    data = {
        "Resource": [f"instance-{i}" for i in range(rows)],
        "Type": np.random.choice(
            ["Idle VM", "Rightsizing", "Unattached Disk", "Snapshot"], rows
        ),
        "Monthly savings": np.random.uniform(50, 2000, rows),
        "Recommendation": np.random.choice(
            ["Delete", "Resize", "Snapshot and Delete"], rows
        ),
        "Impact": np.random.choice(["Low", "Medium", "High"], rows),
    }
    return pd.DataFrame(data)


def generate_sample_manual_analysis_data(rows: int = 100) -> pd.DataFrame:
    """Generates a DataFrame with sample manual analysis data."""
    data = {
        "Sku Id": [f"sku-{i}" for i in range(rows)],
        "Sku Description": np.random.choice(["n2-standard-4", "e2-medium"], rows),
        "Project": np.random.choice(["project-a", "project-b"], rows),
        "Cost": np.random.uniform(100, 5000, rows),
        "Credits": np.random.uniform(0, 500, rows),
        "Usage Amount": np.random.uniform(1, 1000, rows),
        "Usage Unit": ["hours"] * rows,
    }
    return pd.DataFrame(data)


def generate_sample_spend_distribution() -> Dict[str, float]:
    """Generate a sample spend distribution by machine type."""
    return {
        "n2": 250000,
        "n1": 180000,
        "e2": 150000,
        "c2": 120000,
        "m1": 100000,
        "m3": 95000,
        "n2d": 85000,
        "t2d": 75000,
        "c3": 70000,
        "a2": 65000,
        "gpu-t4": 60000,
        "gpu-l4": 55000,
        "h3": 50000,
        "c4a": 45000,
        "z3": 40000,
    }


class GCSDataLoader(DataLoader):
    """Loads data from a structured GCS bucket."""

    GCS_STRUCTURE = {
        "billing": "data/billing/",
        "recommendations": "data/recommendations/",
        "manual_analysis": "data/manual_analysis/",
    }

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.storage_client = self._initialize_client()

    def _initialize_client(self) -> Union[storage.Client, None]:
        """Initializes the GCS client, handling authentication."""
        try:
            credentials, project = google.auth.default()
            logger.info("Successfully authenticated with Google Cloud.")
            return storage.Client(credentials=credentials, project=project)
        except DefaultCredentialsError:
            logger.warning(
                "Google Cloud authentication failed. Could not find default credentials. "
                "Proceeding with sample data generation as fallback."
            )
            return None
        except (google.api_core.exceptions.GoogleAPICallError, OSError) as e:
            logger.error("An unexpected error occurred during GCS client init: %s", e)
            return None

    def load_all_data(self) -> Dict[str, Union[pd.DataFrame, bool]]:
        """
        Loads all CSV files from the GCS bucket.
        If GCS access fails, it falls back to generating sample data.
        """
        if not self.storage_client:
            return SampleDataLoader().load_all_data()

        logger.info("Starting data load from GCS bucket: gs://%s", self.bucket_name)
        data_frames = self._load_data_from_gcs()

        if not data_frames:
            logger.warning("No data loaded from GCS. Falling back to sample data.")
            return SampleDataLoader().load_all_data()

        self._log_summary(data_frames)
        return data_frames

    def _load_data_from_gcs(self) -> Dict[str, pd.DataFrame]:
        """Iterates through GCS structure and loads data from blobs."""
        if not self.storage_client:
            return {}
        data_frames: Dict[str, pd.DataFrame] = {}
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            for data_type, folder_path in self.GCS_STRUCTURE.items():
                logger.info(
                    "Loading '%s' data from gs://%s/%s",
                    data_type,
                    self.bucket_name,
                    folder_path,
                )
                blobs = list(bucket.list_blobs(prefix=folder_path))
                if not blobs:
                    logger.info("No files found in %s.", folder_path)
                    continue

                df_list = [
                    self._process_blob(blob)
                    for blob in blobs
                    if blob.name.endswith(".csv")
                ]

                # Filter out None values before concatenating
                valid_dfs = [df for df in df_list if df is not None]
                if valid_dfs:
                    data_frames[data_type] = pd.concat(valid_dfs, ignore_index=True)
                    logger.info(
                        "Successfully loaded and combined %d files for '%s'.",
                        len(valid_dfs),
                        data_type,
                    )
        except (google.api_core.exceptions.GoogleAPICallError, OSError) as e:
            logger.error(
                "Failed to access GCS bucket 'gs://%s': %s", self.bucket_name, e
            )
            return {}

        return data_frames

    def _process_blob(self, blob: storage.Blob) -> Union[pd.DataFrame, None]:
        """Downloads and parses a single CSV blob into a DataFrame."""
        try:
            content = blob.download_as_text()
            df = pd.read_csv(io.StringIO(content))
            logger.debug("Loaded %s: %d rows.", blob.name, len(df))
            return df
        except (pd.errors.ParserError, ValueError) as e:
            logger.warning("Could not load or parse blob %s: %s", blob.name, e)
            return None

    def _log_summary(self, data_frames: Dict[str, pd.DataFrame]):
        """Logs a summary of the loaded data."""
        summary_lines = ["\n" + "=" * 60, "DATA LOADING SUMMARY", "=" * 60]
        for data_type, df in data_frames.items():
            if isinstance(df, pd.DataFrame):
                summary_lines.append(f"\n{data_type.upper()}:")
                summary_lines.append(f"  - Rows: {len(df):,}")
                summary_lines.append(f"  - Columns: {len(df.columns)}")
                mem_mb = df.memory_usage(deep=True).sum() / 1024**2
                summary_lines.append(f"  - Memory: {mem_mb:.2f} MB")
                cols = list(df.columns)[:5]
                if len(df.columns) > 5:
                    cols.append("...")
                summary_lines.append(f"  - Columns: {', '.join(cols)}")
        summary_lines.append("\n" + "=" * 60)
        logger.info("\n".join(summary_lines))

    def save_report_to_gcs(self, filename: str, local_path: str) -> bool:
        """Saves a generated report to the GCS reports path."""
        if not self.storage_client:
            logger.warning("GCS client not available. Report saved locally only.")
            return False

        # Sanitize filename to prevent path traversal
        safe_filename = os.path.basename(filename)
        if safe_filename != filename:
            logger.warning("Invalid filename detected: %s", filename)
            return False

        try:
            reports_path = "reports/cfo_dashboard"
            # Use Path for safe path joining
            blob_path = str(Path(reports_path) / safe_filename)
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_path)
            logger.info("Report uploaded to gs://%s/%s", self.bucket_name, blob_path)
            return True
        except (google.api_core.exceptions.GoogleAPICallError, OSError) as e:
            logger.error("Could not upload report to GCS: %s", e)
            return False


class SampleDataLoader(DataLoader):
    """Generates sample data for demonstration purposes."""

    def load_all_data(self) -> Dict[str, Union[pd.DataFrame, bool]]:
        """Generates a dictionary of sample data for demonstration."""
        logger.info("Generating sample data sets for demonstration purposes.")
        return {
            "billing": generate_sample_billing_data(),
            "recommendations": generate_sample_recommendations_data(),
            "manual_analysis": generate_sample_manual_analysis_data(),
            "sample_data": True,
        }


def get_data_loader(config_manager: ConfigManager) -> DataLoader:
    """Factory function to get the appropriate data loader."""
    if config_manager.get("gcp.bucket_name"):
        return GCSDataLoader(bucket_name=config_manager.get("gcp.bucket_name"))
    return SampleDataLoader()


def load_data_from_config(
    config_manager: ConfigManager,
) -> Dict[str, Union[pd.DataFrame, bool]]:
    """
    Loads all datasets from GCS based on the application configuration.

    Args:
        config_manager: An instance of ConfigManager.

    Returns:
        A dictionary containing the loaded dataframes.
    """
    loader = get_data_loader(config_manager)
    return loader.load_all_data()
