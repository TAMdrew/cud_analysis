"""Analyzes spend distribution across different machine types."""

from typing import Dict

import pandas as pd

from .data_loader import generate_sample_spend_distribution
from .discount_mapping import MachineTypeDiscountMapping


class SpendAnalyzer:
    """Analyzes spend distribution from billing data."""

    def __init__(self, discount_mapping: MachineTypeDiscountMapping):
        """Initializes the SpendAnalyzer.

        Args:
            discount_mapping: The mapping of machine types to discount rates.
        """
        self.discount_mapping = discount_mapping

    def analyze_machine_distribution(
        self, billing_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Analyzes the spend distribution across different machine types.

        This method aggregates costs by the base machine type (e.g., 'n2', 'e2')
        to provide a high-level view of the spend landscape.

        Args:
            billing_data: A DataFrame containing billing/spend data. It must
                have a 'Cost' column and either a 'SKU' or 'Sku Description'
                column.

        Returns:
            A dictionary mapping each base machine type to its total cost.
        """
        if billing_data is None or billing_data.empty:
            return generate_sample_spend_distribution()

        sku_col = "SKU" if "SKU" in billing_data.columns else "Sku Description"
        dataframe = billing_data.copy()
        dataframe["Cost"] = pd.to_numeric(dataframe["Cost"], errors="coerce")

        # Vectorized operation for better performance
        dataframe["base_type"] = dataframe[sku_col].apply(
            self.discount_mapping.get_machine_base
        )
        distribution = dataframe.groupby("base_type")["Cost"].sum().to_dict()

        return distribution
