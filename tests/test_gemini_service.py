"""Tests for the Gemini Service Module."""

import unittest
from unittest.mock import MagicMock, patch

from finops_analysis_platform.gemini_service import generate_content


class TestGeminiService(unittest.TestCase):
    """Test suite for the Gemini service."""

    @patch("google.generativeai.GenerativeModel")
    def test_generate_content_success(self, mock_generative_model):
        """Test successful content generation."""
        # Mock the model and its response
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model_instance

        response = generate_content(
            prompt="test prompt", project_id="test-project", location="us-central1"
        )

        self.assertIsNotNone(response)
        self.assertEqual(response.text, "Test response")
        mock_generative_model.assert_called_once()

    @patch(
        "finops_analysis_platform.gemini_service.generate_content",
        side_effect=Exception("API Error"),
    )
    def test_generate_content_api_error(self, mock_generate_content):
        """Test handling of an API error during content generation."""
        response = generate_content(
            prompt="test prompt", project_id="test-project", location="us-central1"
        )
        self.assertIsNone(response)


if __name__ == "__main__":
    unittest.main()
