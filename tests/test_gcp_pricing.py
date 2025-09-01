"""Tests for the GCP SKU Price Fetcher."""

import unittest
from unittest.mock import MagicMock, patch

import requests

from finops_analysis_platform.gcp_pricing import GcpSkuFetcher


class TestGcpSkuFetcher(unittest.TestCase):
    """Test suite for the GcpSkuFetcher."""

    def setUp(self):
        """Set up the fetcher for tests."""
        self.api_key = "test-api-key"
        self.fetcher = GcpSkuFetcher(api_key=self.api_key)

    @patch("requests.get")
    def test_get_all_skus_success_single_page(self, mock_get):
        """Test successful SKU fetch with a single page of results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"skus": [{"skuId": "123"}, {"skuId": "456"}]}
        mock_get.return_value = mock_response

        skus = self.fetcher.get_all_skus("test-service")
        self.assertIsNotNone(skus)
        self.assertEqual(len(skus), 2)
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_get_all_skus_success_multiple_pages(self, mock_get):
        """Test successful SKU fetch with pagination."""
        # Simulate two pages of results
        mock_response_page1 = MagicMock()
        mock_response_page1.json.return_value = {
            "skus": [{"skuId": "123"}],
            "nextPageToken": "page2",
        }
        mock_response_page2 = MagicMock()
        mock_response_page2.json.return_value = {"skus": [{"skuId": "456"}]}
        mock_get.side_effect = [mock_response_page1, mock_response_page2]

        skus = self.fetcher.get_all_skus("test-service")
        self.assertIsNotNone(skus)
        self.assertEqual(len(skus), 2)
        self.assertEqual(mock_get.call_count, 2)

    @patch("requests.get")
    def test_get_all_skus_api_error(self, mock_get):
        """Test handling of an API error during SKU fetch."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        skus = self.fetcher.get_all_skus("test-service")
        self.assertIsNone(skus)

    def test_init_raises_error_on_empty_key(self):
        """Test that the initializer raises a ValueError for an empty API key."""
        with self.assertRaises(ValueError):
            GcpSkuFetcher(api_key="")


if __name__ == "__main__":
    unittest.main()
