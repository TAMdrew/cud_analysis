"""Tests for the Gemini Service Module."""

import unittest
from unittest.mock import MagicMock, patch

from google.api_core import exceptions

from finops_analysis_platform.gemini_service import generate_content


class TestGeminiService(unittest.TestCase):
    """Test suite for the Gemini service."""

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_generate_content_success(self, mock_generative_model, mock_configure):
        """Test successful content generation."""
        # Mock the model and its response
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model_instance

        response = generate_content(prompt="test prompt")

        self.assertIsNotNone(response)
        self.assertEqual(response.text, "Test response")
        mock_generative_model.assert_called_once()

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_generate_content_api_error(self, mock_generative_model, mock_configure):
        """Test handling of a realistic API error during content generation."""
        # Configure the mock instance to raise a specific, expected exception
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = (
            exceptions.GoogleAPICallError("API Error")
        )
        mock_generative_model.return_value = mock_model_instance

        response = generate_content(prompt="test prompt")
        self.assertIsNone(response)


if __name__ == "__main__":
    unittest.main()
