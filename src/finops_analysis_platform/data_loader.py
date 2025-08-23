import io
import logging
import random
from typing import Dict, List

import numpy as np
import pandas as pd
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
import google.auth

logger = logging.getLogger(__name__)

# --- Sample Data Generation Functions ---
# These functions are used to create realistic sample data for demonstration
# when GCS data is not available.

def _generate_realistic_cost(usage: float, sku: str) -> float:
    """Generates a realistic cost based on usage and SKU."""
    base_cost_per_hour = {
        'n2': 0.1, 'e2': 0.05, 'c2': 0.15, 'm1': 0.5, 't2': 0.08, 'a2': 1.2, 'gpu': 2.5
    }
    sku_family = sku.split('-')[0]
    cost_multiplier = base_cost_per_hour.get(sku_family, 0.1)
    return usage * cost_multiplier * (1 + random.uniform(-0.1, 0.1))

def generate_sample_billing_data(rows: int = 1000) -> pd.DataFrame:
    """Generates a DataFrame with realistic sample billing data."""
    machine_types = [
        'n2-standard-8', 'n2-highmem-4', 'e2-standard-4', 'c2-standard-16',
        'm1-megamem-96', 't2d-standard-8', 'a2-highgpu-1g', 'gpu-t4-instance'
    ]
    projects = [f'project-{chr(97 + i)}' for i in range(5)]
    services = ['Compute Engine'] * rows

    df = pd.DataFrame({
        'SKU': np.random.choice(machine_types, rows),
        'Service': services,
        'Usage': np.random.gamma(2, 250, rows),
        'Project': np.random.choice(projects, rows, p=[0.4, 0.3, 0.15, 0.1, 0.05]),
        'Start Time': pd.to_datetime(pd.to_datetime('now') - pd.to_timedelta(np.random.rand(rows) * 90, 'D')),
    })
    df['End Time'] = df['Start Time'] + pd.to_timedelta(np.random.randint(1, 24, rows), 'H')
    df['Cost'] = df.apply(lambda row: _generate_realistic_cost(row['Usage'], row['SKU']), axis=1)
    return df

def generate_sample_recommendations_data(rows: int = 50) -> pd.DataFrame:
    """Generates a DataFrame with sample recommendations data."""
    return pd.DataFrame({
        'Resource': [f'instance-{i}' for i in range(rows)],
        'Type': np.random.choice(['Idle VM', 'Rightsizing', 'Unattached Disk', 'Snapshot'], rows),
        'Monthly savings': np.random.uniform(50, 2000, rows),
        'Recommendation': np.random.choice(['Delete', 'Resize', 'Snapshot and Delete'], rows),
        'Impact': np.random.choice(['Low', 'Medium', 'High'], rows)
    })

def generate_sample_manual_analysis_data(rows: int = 100) -> pd.DataFrame:
    """Generates a DataFrame with sample manual analysis data."""
    machine_types = ['n2-standard-4', 'e2-medium']
    return pd.DataFrame({
        'Sku Id': [f'sku-{i}' for i in range(rows)],
        'Sku Description': np.random.choice(machine_types, rows),
        'Project': np.random.choice(['project-a', 'project-b'], rows),
        'Cost': np.random.uniform(100, 5000, rows),
        'Credits': np.random.uniform(0, 500, rows),
        'Usage Amount': np.random.uniform(1, 1000, rows),
        'Usage Unit': ['hours'] * rows
    })

def generate_sample_spend_distribution() -> Dict[str, float]:
    """Generate a sample spend distribution by machine type."""
    return {
        'n2': 250000, 'n1': 180000, 'e2': 150000, 'c2': 120000,
        'm1': 100000, 'm3': 95000, 'n2d': 85000, 't2d': 75000,
        'c3': 70000, 'a2': 65000, 'gpu-t4': 60000, 'gpu-l4': 55000,
        'h3': 50000, 'c4a': 45000, 'z3': 40000
    }


class GCSDataLoader:
    """Loads data from a structured GCS bucket."""

    GCS_STRUCTURE = {
        'billing': 'data/billing/',
        'recommendations': 'data/recommendations/',
        'manual_analysis': 'data/manual_analysis/',
    }

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.storage_client = self._initialize_client()

    def _initialize_client(self) -> storage.Client | None:
        """Initializes the GCS client, handling authentication."""
        try:
            credentials, project = google.auth.default()
            logger.info("Successfully authenticated with Google Cloud.")
            return storage.Client(credentials=credentials, project=project)
        except DefaultCredentialsError:
            logger.warning("Google Cloud authentication failed. Could not find default credentials.")
            logger.info("Proceeding with sample data generation.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during GCS client initialization: {e}")
            return None

    def load_all_data(self) -> Dict[str, pd.DataFrame | bool]:
        """
        Loads all CSV files from the GCS bucket.
        If GCS access fails, it falls back to generating sample data.
        """
        if not self.storage_client:
            return self._generate_sample_data()

        logger.info(f"Starting data load from GCS bucket: gs://{self.bucket_name}")
        data_frames = self._load_data_from_gcs()

        if not data_frames:
            logger.warning("No data loaded from GCS. Falling back to sample data.")
            return self._generate_sample_data()

        self._log_summary(data_frames)
        return data_frames

    def _load_data_from_gcs(self) -> Dict[str, pd.DataFrame]:
        """Iterates through GCS structure and loads data from blobs."""
        data_frames: Dict[str, pd.DataFrame] = {}
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            for data_type, folder_path in self.GCS_STRUCTURE.items():
                logger.info(f"Loading '{data_type}' data from gs://{self.bucket_name}/{folder_path}")
                blobs = list(bucket.list_blobs(prefix=folder_path))
                if not blobs:
                    logger.info(f"No files found in {folder_path}.")
                    continue

                df_list = [self._process_blob(blob) for blob in blobs if blob.name.endswith('.csv')]

                if df_list:
                    # Filter out None values before concatenating
                    valid_dfs = [df for df in df_list if df is not None]
                    if valid_dfs:
                        data_frames[data_type] = pd.concat(valid_dfs, ignore_index=True)
                        logger.info(f"Successfully loaded and combined {len(valid_dfs)} files for '{data_type}'.")

        except Exception as e:
            logger.error(f"Failed to access GCS bucket 'gs://{self.bucket_name}': {e}")
            return {}

        return data_frames

    def _process_blob(self, blob: storage.Blob) -> pd.DataFrame | None:
        """Downloads and parses a single CSV blob into a DataFrame."""
        try:
            content = blob.download_as_text()
            df = pd.read_csv(io.StringIO(content))
            logger.debug(f"Loaded {blob.name}: {len(df)} rows.")
            return df
        except Exception as e:
            logger.warning(f"Could not load or parse blob {blob.name}: {e}")
            return None

    def _generate_sample_data(self) -> Dict[str, pd.DataFrame | bool]:
        """Generates a dictionary of sample data for demonstration."""
        logger.info("Generating sample data sets for demonstration purposes.")
        return {
            'billing': generate_sample_billing_data(),
            'recommendations': generate_sample_recommendations_data(),
            'manual_analysis': generate_sample_manual_analysis_data(),
            'sample_data': True  # Flag to indicate sample data is used
        }

    def _log_summary(self, data_frames: Dict[str, pd.DataFrame]):
        """Logs a summary of the loaded data."""
        summary_lines = ["\n" + "="*60, "DATA LOADING SUMMARY", "="*60]
        for data_type, df in data_frames.items():
            if isinstance(df, pd.DataFrame):
                summary_lines.append(f"\n{data_type.upper()}:")
                summary_lines.append(f"  - Rows: {len(df):,}")
                summary_lines.append(f"  - Columns: {len(df.columns)}")
                summary_lines.append(f"  - Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                cols = list(df.columns)[:5]
                if len(df.columns) > 5:
                    cols.append('...')
                summary_lines.append(f"  - Columns: {', '.join(cols)}")
        summary_lines.append("\n" + "="*60)
        logger.info('\\n'.join(summary_lines))

    def save_report_to_gcs(self, filename: str, local_path: str) -> bool:
        """Saves a generated report to the GCS reports path."""
        if not self.storage_client:
            logger.warning("GCS client not available. Report saved locally only.")
            return False
        try:
            reports_path = 'reports/cfo_dashboard/' # Hardcoded for now, could be in config
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(f"{reports_path}{filename}")
            blob.upload_from_filename(local_path)
            logger.info(f"Report uploaded to gs://{self.bucket_name}/{reports_path}{filename}")
            return True
        except Exception as e:
            logger.error(f"Could not upload report to GCS: {e}")
            return False
