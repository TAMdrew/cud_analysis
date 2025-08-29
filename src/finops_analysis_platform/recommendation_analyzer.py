"""recommendation_analyzer.py

Analyzes cost-saving recommendations from Google Cloud's Active Assist.
This module processes exported recommendation data to quantify potential
savings from rightsizing, deleting idle resources, and other optimizations.
"""

import logging
from typing import Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class RecommendationAnalyzer:
    """
    Processes and summarizes cost-saving recommendations from Active Assist.
    """

    def analyze(
        self, recommendations_df: Optional[pd.DataFrame]
    ) -> Optional[Dict[str, float]]:
        """
        Analyzes the recommendations DataFrame to summarize savings by type.

        Args:
            recommendations_df: DataFrame containing Active Assist recommendations.

        Returns:
            A dictionary summarizing total potential monthly savings by
            recommendation type, or None if the input is invalid.
        """
        if recommendations_df is None or recommendations_df.empty:
            logger.info("No recommendations data to analyze.")
            return None

        if "Monthly savings" not in recommendations_df.columns:
            logger.warning(
                "Recommendations data is missing the 'Monthly savings' column."
            )
            return None

        # Clean the 'Monthly savings' column
        # It can contain non-numeric values like '-'
        # Coerce errors will turn invalid parsing into NaT
        recommendations_df["savings"] = pd.to_numeric(
            recommendations_df["Monthly savings"], errors="coerce"
        )

        # Group by the 'Recommendation' type and sum the savings
        savings_summary = (
            recommendations_df.groupby("Recommendation")["savings"].sum().to_dict()
        )

        # Filter out any recommendation types with zero savings
        savings_summary = {
            rec_type: total_savings
            for rec_type, total_savings in savings_summary.items()
            if total_savings > 0
        }

        logger.info(
            "Successfully analyzed Active Assist recommendations. Found %d categories.",
            len(savings_summary),
        )
        return savings_summary
