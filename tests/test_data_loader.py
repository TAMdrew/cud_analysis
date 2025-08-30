"""Tests for the Data Loader Module."""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
from google.auth.exceptions import DefaultCredentialsError

from finops_analysis_platform.config_manager import ConfigManager
from finops_analysis_platform.data_loader import GCSDataLoader, get_data_loader


class TestDataLoaders(unittest.TestCase):
    """Test suite for the data loaders."""

    def setUp(self):
        """Set up common objects for tests."""
        self.config_manager = ConfigManager()
        self.config_manager.config = {"gcp": {"bucket_name": "test-bucket"}}

    @patch("google.auth.default", side_effect=DefaultCredentialsError)
    def test_gcs_loader_falls_back_to_sample_on_auth_error(self, mock_auth):
        """Test that GCSDataLoader falls back to SampleDataLoader on auth error."""
        loader = GCSDataLoader(bucket_name="test-bucket")
        data = loader.load_all_data()
        self.assertTrue(data.get("sample_data"))

    @patch("google.cloud.storage.Client")
    @patch("google.auth.default")
    def test_gcs_loader_loads_data_successfully(self, mock_auth, mock_storage_client):
        """Test successful data loading from a mocked GCS."""
        # Mock the auth call to return mock credentials and project
        mock_auth.return_value = (MagicMock(), "test-project")

        # Mock the GCS client and blobs
        mock_blob_content = "col1,col2\nval1,val2"
        mock_blob = MagicMock()
        mock_blob.name = "data/billing/test.csv"
        mock_blob.download_as_text.return_value = mock_blob_content
        mock_bucket = MagicMock()
        mock_bucket.list_blobs.return_value = [mock_blob]
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        loader = GCSDataLoader(bucket_name="test-bucket")
        data = loader.load_all_data()

        self.assertIn("billing", data)
        self.assertIsInstance(data["billing"], pd.DataFrame)
        self.assertEqual(len(data["billing"]), 1)

    def test_get_data_loader_factory(self):
        """Test the get_data_loader factory function."""
        # Test with a bucket name (should return GCSDataLoader)
        loader = get_data_loader(self.config_manager)
        self.assertIsInstance(loader, GCSDataLoader)

        # Test without a bucket name (should return SampleDataLoader)
        self.config_manager.config = {}
        loader = get_data_loader(self.config_manager)
        self.assertNotIsInstance(loader, GCSDataLoader)


if __name__ == "__main__":
    unittest.main()
