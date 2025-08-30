"""Handles loading data from Google Cloud Storage and local samples.

This module provides data loaders responsible for fetching billing,
recommendations, and other data files from GCS. If GCS is unavailable, it
falls back to loading local sample data for demonstration purposes.
"""

from __future__ import annotations

import io
import logging
import os
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


def _generate_realistic_cost_vectorized(
    usage_series: pd.Series,
    sku_series: pd.Series,
) -> pd.Series:
    """Generates a realistic cost based on usage and SKU in a vectorized way.

    Args:
        usage_series: A pandas Series containing usage amounts.
        sku_series: A pandas Series containing SKU descriptions.

    Returns:
        A pandas Series with the calculated costs.
    """
    base_costs = {
        "n2": 0.1,
        "e2": 0.05,
        "c2": 0.15,
        "m1": 0.5,
        "t2": 0.08,
        "a2": 1.2,
        "gpu": 2.5,
    }
    sku_families = sku_series.str.split("-").str[0]
    cost_multipliers = sku_families.map(base_costs).fillna(0.1)
    random_factors = 1 + np.random.uniform(-0.1, 0.1, len(usage_series))
    return usage_series * cost_multipliers * random_factors


def generate_sample_billing_data(rows: int = 1000) -> pd.DataFrame:
    """Generates a DataFrame with realistic sample billing data.

    Args:
        rows: The number of sample rows to generate.

    Returns:
        A pandas DataFrame with sample billing data.
    """
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
    dataframe = pd.DataFrame(data)
    dataframe["End Time"] = dataframe["Start Time"] + pd.to_timedelta(
        np.random.randint(1, 24, rows), "h"
    )
    dataframe["Cost"] = _generate_realistic_cost_vectorized(
        dataframe["Usage"], dataframe["SKU"]
    )
    return dataframe


def generate_sample_recommendations_data(rows: int = 50) -> pd.DataFrame:
    """Generates a DataFrame with sample recommendations data.

    Args:
        rows: The number of sample rows to generate.

    Returns:
        A pandas DataFrame with sample recommendations data.
    """
    data = {
        "Resource": [f"instance-{i}" for i in range(rows)],
        "Recommendation": [
            "Rightsize VM",
            "Shut down Idle VM",
            "Delete idle disk",
            "Delete idle IP address",
        ]
        * (rows // 4 + 1),
        "Monthly savings": np.random.uniform(5, 500, rows),
        "Impact": np.random.choice(["Low", "Medium", "High"], rows),
    }
    return pd.DataFrame(data).head(rows)


def generate_sample_manual_analysis_data(rows: int = 100) -> pd.DataFrame:
    """Generates a DataFrame with sample manual analysis data.

    Args:
        rows: The number of sample rows to generate.

    Returns:
        A pandas DataFrame with sample manual analysis data.
    """
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
    """Generates a sample spend distribution by machine type."""
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
    """Loads data from a structured Google Cloud Storage bucket."""

    GCS_STRUCTURE = {
        "billing": "data/billing/",
        "recommendations": "data/recommendations/",
        "manual_analysis": "data/manual_analysis/",
    }

    def __init__(self, bucket_name: str):
        """Initializes the GCSDataLoader.

        Args:
            bucket_name: The name of the GCS bucket to load data from.
        """
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
                "Google Cloud authentication failed. Could not find default "
                "credentials. Proceeding with sample data as fallback."
            )
            return None
        except (google.api_core.exceptions.GoogleAPICallError, OSError) as exception:
            logger.error(
                "An unexpected error occurred during GCS client init: %s", exception
            )
            return None

    def load_all_data(self) -> Dict[str, Union[pd.DataFrame, bool]]:
        """Loads all CSV files from the GCS bucket.

        If GCS access fails, it falls back to generating sample data.

        Returns:
            A dictionary containing pandas DataFrames for each data type.
        """
        if not self.storage_client:
            return SampleDataLoader().load_all_data()

        logger.info("Starting data load from GCS bucket: gs://%s", self.bucket_name)
        data_frames = self._load_data_from_gcs()

        if not data_frames.get("billing"):
            logger.warning(
                "No billing data loaded from GCS. Falling back to sample data."
            )
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

                dataframe_list = [
                    self._process_blob(blob)
                    for blob in blobs
                    if blob.name.endswith(".csv")
                ]

                valid_dataframes = [df for df in dataframe_list if df is not None]
                if valid_dataframes:
                    data_frames[data_type] = pd.concat(
                        valid_dataframes, ignore_index=True
                    )
                    logger.info(
                        "Successfully loaded and combined %d files for '%s'.",
                        len(valid_dataframes),
                        data_type,
                    )
        except (google.api_core.exceptions.GoogleAPICallError, OSError) as exception:
            logger.error(
                "Failed to access GCS bucket 'gs://%s': %s",
                self.bucket_name,
                exception,
            )
            return {}

        return data_frames

    def _process_blob(self, blob: storage.Blob) -> Union[pd.DataFrame, None]:
        """Downloads and parses a single CSV blob into a DataFrame."""
        try:
            content = blob.download_as_text()
            dataframe = pd.read_csv(io.StringIO(content))
            logger.debug("Loaded %s: %d rows.", blob.name, len(dataframe))
            return dataframe
        except (pd.errors.ParserError, ValueError) as exception:
            logger.warning("Could not load or parse blob %s: %s", blob.name, exception)
            return None

    def _log_summary(self, data_frames: Dict[str, pd.DataFrame]):
        """Logs a summary of the loaded data."""
        summary_lines = ["\n" + "=" * 60, "DATA LOADING SUMMARY", "=" * 60]
        for data_type, dataframe in data_frames.items():
            if isinstance(dataframe, pd.DataFrame):
                summary_lines.append(f"\n{data_type.upper()}:")
                summary_lines.append(f"  - Rows: {len(dataframe):,}")
                summary_lines.append(f"  - Columns: {len(dataframe.columns)}")
                mem_mb = dataframe.memory_usage(deep=True).sum() / 1024**2
                summary_lines.append(f"  - Memory: {mem_mb:.2f} MB")
                cols = list(dataframe.columns)[:5]
                if len(dataframe.columns) > 5:
                    cols.append("...")
                summary_lines.append(f"  - Columns: {', '.join(cols)}")
        summary_lines.append("\n" + "=" * 60)
        logger.info("\n".join(summary_lines))

    def save_report_to_gcs(self, filename: str, local_path: str) -> bool:
        """Saves a generated report to the GCS reports path.

        Args:
            filename: The desired filename for the report in GCS.
            local_path: The local path to the file to be uploaded.

        Returns:
            True if the upload was successful, False otherwise.
        """
        if not self.storage_client:
            logger.warning("GCS client not available. Report saved locally only.")
            return False

        safe_filename = os.path.basename(filename)
        if safe_filename != filename:
            logger.warning("Invalid filename detected: %s", filename)
            return False

        try:
            reports_path = "reports/cfo_dashboard"
            blob_path = str(Path(reports_path) / safe_filename)
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_path)
            logger.info("Report uploaded to gs://%s/%s", self.bucket_name, blob_path)
            return True
        except (google.api_core.exceptions.GoogleAPICallError, OSError) as exception:
            logger.error("Could not upload report to GCS: %s", exception)
            return False


class SampleDataLoader(DataLoader):
    """Generates sample data for demonstration purposes."""

    def load_all_data(self) -> Dict[str, Union[pd.DataFrame, bool]]:
        """Generates a dictionary of sample data for demonstration.

        Returns:
            A dictionary containing sample pandas DataFrames.
        """
        logger.info("Generating sample data sets for demonstration purposes.")
        return {
            "billing": generate_sample_billing_data(),
            "recommendations": generate_sample_recommendations_data(),
            "manual_analysis": generate_sample_manual_analysis_data(),
            "sample_data": True,
        }


def get_data_loader(config_manager: ConfigManager) -> DataLoader:
    """Factory function to get the appropriate data loader.

    Args:
        config_manager: The application's configuration manager.

    Returns:
        An initialized data loader, either for GCS or for sample data.
    """
    if config_manager.get("gcp.bucket_name"):
        return GCSDataLoader(bucket_name=config_manager.get("gcp.bucket_name"))
    return SampleDataLoader()


def load_data_from_config(
    config_manager: ConfigManager,
) -> Dict[str, Union[pd.DataFrame, bool]]:
    """Loads all datasets based on the application configuration.

    Args:
        config_manager: An instance of ConfigManager.

    Returns:
        A dictionary containing the loaded dataframes.
    """
    loader = get_data_loader(config_manager)
    return loader.load_all_data()
