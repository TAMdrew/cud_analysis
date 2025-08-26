"""Analyzes spend distribution across different machine types."""

from typing import Dict

import pandas as pd

from .data_loader import generate_sample_spend_distribution
from .discount_mapping import MachineTypeDiscountMapping


class SpendAnalyzer:
    """Analyzes spend distribution."""

    def __init__(self, discount_mapping: MachineTypeDiscountMapping):
        self.discount_mapping = discount_mapping

    def analyze_machine_distribution(
        self, billing_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Analyzes the spend distribution across different machine types."""
        if billing_data is None or billing_data.empty:
            return generate_sample_spend_distribution()

        sku_col = "SKU" if "SKU" in billing_data.columns else "Sku Description"
        df = billing_data.copy()
        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")

        # Vectorized operation for better performance
        df["base_type"] = df[sku_col].apply(self.discount_mapping.get_machine_base)
        distribution = df.groupby("base_type")["Cost"].sum().to_dict()

        return distribution
