"""Tests for the Recommendation Analyzer."""

import unittest

import pandas as pd

from finops_analysis_platform.recommendation_analyzer import RecommendationAnalyzer


class TestRecommendationAnalyzer(unittest.TestCase):
    """Test suite for the RecommendationAnalyzer."""

    def setUp(self):
        """Set up the analyzer for tests."""
        self.analyzer = RecommendationAnalyzer()

    def test_analyze_valid_data(self):
        """Test analysis with a valid DataFrame."""
        data = {
            "Recommendation": ["Rightsize VM", "Shut down Idle VM", "Rightsize VM"],
            "Monthly savings": [100.50, 75.00, 50.25],
        }
        df = pd.DataFrame(data)
        result = self.analyzer.analyze(df)
        self.assertIsNotNone(result)
        self.assertIn("Rightsize VM", result)
        self.assertIn("Shut down Idle VM", result)
        self.assertAlmostEqual(result["Rightsize VM"], 150.75)
        self.assertAlmostEqual(result["Shut down Idle VM"], 75.00)

    def test_analyze_empty_dataframe(self):
        """Test analysis with an empty DataFrame."""
        df = pd.DataFrame({"Recommendation": [], "Monthly savings": []})
        result = self.analyzer.analyze(df)
        self.assertIsNone(result)

    def test_analyze_none_input(self):
        """Test analysis with None as input."""
        result = self.analyzer.analyze(None)
        self.assertIsNone(result)

    def test_analyze_missing_savings_column(self):
        """Test analysis with a missing 'Monthly savings' column."""
        df = pd.DataFrame({"Recommendation": ["Rightsize VM"]})
        result = self.analyzer.analyze(df)
        self.assertIsNone(result)

    def test_analyze_non_numeric_savings(self):
        """Test analysis with non-numeric values in the savings column."""
        data = {
            "Recommendation": ["Rightsize VM", "Shut down Idle VM"],
            "Monthly savings": [100.50, "-"],  # Invalid value
        }
        df = pd.DataFrame(data)
        result = self.analyzer.analyze(df)
        self.assertIsNotNone(result)
        self.assertIn("Rightsize VM", result)
        self.assertNotIn("Shut down Idle VM", result)  # Should be filtered out
        self.assertAlmostEqual(result["Rightsize VM"], 100.50)


if __name__ == "__main__":
    unittest.main()
