import io
import logging
from typing import Dict
import numpy as np
import pandas as pd
from google.cloud import storage
import google.auth

logger = logging.getLogger(__name__)

class GCSDataLoader:
    """Load data from organized GCS bucket structure"""

    def __init__(self, bucket_name='cud_analysis'):
        self.bucket_name = bucket_name
        self.storage_client = None
        self.data_frames = {}

        # Define the GCS structure
        self.gcs_structure = {
            'billing': 'data/billing/',
            'recommendations': 'data/recommendations/',
            'manual_analysis': 'data/manual_analysis/',
            'reports': 'reports/cfo_dashboard/'
        }

        self._initialize_client()

    def _initialize_client(self):
        """Initialize GCS client"""
        try:
            credentials, project = google.auth.default()
            self.storage_client = storage.Client(credentials=credentials)
            logger.info(f"✅ GCS client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize GCS client: {e}")
            logger.info("Will use sample data for demonstration")

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV files from GCS bucket"""
        logger.info(f"\n🔍 Scanning GCS bucket: gs://{self.bucket_name}")

        if not self.storage_client:
            logger.info("📁 GCS not available, generating sample data...")
            return self._generate_sample_data()

        try:
            bucket = self.storage_client.bucket(self.bucket_name)

            # Load all CSV files from each folder
            for data_type, folder_path in self.gcs_structure.items():
                if data_type == 'reports':
                    continue  # Skip reports folder

                logger.info(f"\nLoading {data_type} data from {folder_path}")
                blobs = bucket.list_blobs(prefix=folder_path)

                for blob in blobs:
                    if blob.name.endswith('.csv'):
                        try:
                            content = blob.download_as_text()
                            df = pd.read_csv(io.StringIO(content))

                            # Store with simplified key
                            if data_type not in self.data_frames:
                                self.data_frames[data_type] = df
                                logger.info(f"  ✅ Loaded {blob.name}: {len(df)} rows")
                            else:
                                # Append if multiple files
                                self.data_frames[data_type] = pd.concat([self.data_frames[data_type], df], ignore_index=True)
                                logger.info(f"  ✅ Appended {blob.name}: {len(df)} rows")
                        except Exception as e:
                            logger.warning(f"  ⚠️ Could not load {blob.name}: {e}")

            if self.data_frames:
                logger.info(f"\n📊 Successfully loaded {len(self.data_frames)} datasets from GCS")
                self._print_summary()
            else:
                logger.warning("⚠️ No data loaded from GCS, using sample data")
                return self._generate_sample_data()

            return self.data_frames

        except Exception as e:
            logger.error(f"Error accessing GCS bucket: {e}")
            logger.info("Generating sample data for demonstration...")
            return self._generate_sample_data()

    def _generate_sample_data(self) -> Dict[str, pd.DataFrame]:
        """Generate sample data for demonstration"""
        np.random.seed(42)

        billing_data = generate_sample_billing_data()
        recommendations_data = generate_sample_recommendations_data()
        manual_analysis_data = generate_sample_manual_analysis_data()

        self.data_frames = {
            'billing': billing_data,
            'recommendations': recommendations_data,
            'manual_analysis': manual_analysis_data,
            'sample_data': True
        }

        logger.info("📊 Generated sample data for demonstration")
        return self.data_frames

    def _print_summary(self):
        """Print summary of loaded data"""
        print("\n" + "="*60)
        print("DATA LOADING SUMMARY")
        print("="*60)

        for data_type, df in self.data_frames.items():
            if isinstance(df, pd.DataFrame):
                print(f"\n{data_type.upper()}:")
                print(f"  Rows: {len(df):,}")
                print(f"  Columns: {len(df.columns)}")
                print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

                # Show column names
                cols = list(df.columns)[:5]
                if len(df.columns) > 5:
                    cols.append('...')
                print(f"  Columns: {', '.join(cols)}")

        print("\n" + "="*60)

    def save_report_to_gcs(self, filename: str, local_path: str):
        """Save generated report to GCS"""
        if not self.storage_client:
            logger.warning("GCS client not available, report saved locally only")
            return False

        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(f"reports/cfo_dashboard/{filename}")
            blob.upload_from_filename(local_path)
            logger.info(f"✅ Report uploaded to gs://{self.bucket_name}/reports/cfo_dashboard/{filename}")
            return True
        except Exception as e:
            logger.error(f"Could not upload report to GCS: {e}")
            return False

# --- Standalone helper functions below ---

def generate_sample_billing_data(rows=500) -> pd.DataFrame:
    """Generate a DataFrame with sample billing data."""
    machine_types = [
        'n2-standard-4', 'n2-standard-8', 'n2-highmem-4',
        'e2-medium', 'e2-standard-4', 'e2-highmem-2',
        'c2-standard-4', 'c2-standard-8', 'c2-standard-16',
        'm1-megamem-96', 'm2-megamem-416', 'm3-megamem-64',
        'n1-standard-4', 'n1-standard-8', 'n1-highmem-4',
        't2d-standard-4', 't2a-standard-8',
        'a2-highgpu-1g', 'a2-megagpu-16g',
        'gpu-l4-instance', 'gpu-t4-instance', 'gpu-a100-instance'
    ]
    return pd.DataFrame({
        'SKU': np.random.choice(machine_types, rows),
        'Service': ['Compute Engine'] * rows,
        'Cost': np.random.uniform(100, 10000, rows),
        'Usage': np.random.uniform(1, 1000, rows),
        'Project': np.random.choice(['project-1', 'project-2', 'project-3'], rows),
        'Start Time': pd.to_datetime(pd.date_range(start='2025-01-01', periods=rows, freq='H')),
        'End Time': pd.to_datetime(pd.date_range(start='2025-01-01 01:00:00', periods=rows, freq='H'))
    })

def generate_sample_recommendations_data(rows=50) -> pd.DataFrame:
    """Generate a DataFrame with sample recommendations data."""
    return pd.DataFrame({
        'Resource': [f'instance-{i}' for i in range(rows)],
        'Type': np.random.choice(['Idle VM', 'Rightsizing', 'Unattached Disk', 'Snapshot'], rows),
        'Monthly savings': np.random.uniform(50, 2000, rows),
        'Recommendation': np.random.choice(['Delete', 'Resize', 'Snapshot and Delete'], rows),
        'Impact': np.random.choice(['Low', 'Medium', 'High'], rows)
    })

def generate_sample_manual_analysis_data(rows=100) -> pd.DataFrame:
    """Generate a DataFrame with sample manual analysis data."""
    machine_types = [
        'n2-standard-4', 'n2-standard-8', 'n2-highmem-4',
        'e2-medium', 'e2-standard-4', 'e2-highmem-2',
    ]
    return pd.DataFrame({
        'Sku Id': [f'sku-{i}' for i in range(rows)],
        'Sku Description': np.random.choice(machine_types, rows),
        'Project': np.random.choice(['project-1', 'project-2', 'project-3'], rows),
        'Cost': np.random.uniform(100, 5000, rows),
        'Credits': np.random.uniform(0, 500, rows),
        'Usage Amount': np.random.uniform(1, 1000, rows),
        'Usage Unit': ['hours'] * rows
    })

def generate_sample_spend_distribution() -> Dict[str, float]:
    """Generate a sample spend distribution by machine type."""
    return {
        'n2': 250000,
        'n1': 180000,
        'e2': 150000,
        'c2': 120000,
        'm1': 100000,
        'm3': 95000,
        'n2d': 85000,
        't2d': 75000,
        'c3': 70000,
        'a2': 65000,
        'gpu-t4': 60000,
        'gpu-l4': 55000,
        'h3': 50000,
        'c4a': 45000,
        'z3': 40000
    }
