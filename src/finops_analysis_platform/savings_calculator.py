"""Calculates potential savings for each machine type."""

from typing import Any, Dict

from .config_manager import ConfigManager
from .discount_mapping import MachineTypeDiscountMapping


class SavingsCalculator:
    """Calculates potential savings."""

    def __init__(
        self,
        config_manager: ConfigManager,
        discount_mapping: MachineTypeDiscountMapping,
    ):
        self.config_manager = config_manager
        self.discount_mapping = discount_mapping

    def calculate_savings_by_machine(
        self, distribution: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculates potential savings for each machine type."""
        savings = {}
        strategy_config = self.config_manager.get("cud_strategy", {})
        stable_coverage = strategy_config.get("base_layer_coverage", 40) / 100.0

        for machine_type, monthly_spend in distribution.items():
            stable_workload = monthly_spend * stable_coverage
            discounts = {
                "1yr_resource": self.discount_mapping.get_discount(
                    machine_type, "1yr_resource"
                )
                or 0,
                "3yr_resource": self.discount_mapping.get_discount(
                    machine_type, "3yr_resource"
                )
                or 0,
                "1yr_flex": self.discount_mapping.get_discount(machine_type, "1yr_flex")
                or 0,
                "3yr_flex": self.discount_mapping.get_discount(machine_type, "3yr_flex")
                or 0,
            }
            savings[machine_type] = {
                "family": self.discount_mapping.get_family(machine_type),
                "monthly_spend": monthly_spend,
                "stable_workload": stable_workload,
                "savings_options": {
                    key: {"discount": value, "monthly_savings": stable_workload * value}
                    for key, value in discounts.items()
                },
                "recommendation": self._get_recommendation(discounts),
            }
        return savings

    def _get_recommendation(self, discounts: Dict[str, float]) -> str:
        """Gets a CUD recommendation based on available discount rates."""
        if discounts.get("3yr_resource", 0) >= 0.65:
            return "3-Year Resource CUD (Highest Savings)"
        if discounts.get("1yr_resource", 0) >= 0.45:
            return "1-Year Resource CUD (Good Savings, Less Commitment)"
        if discounts.get("3yr_flex", 0) > 0:
            return "3-Year Flex CUD (Good Flexibility)"
        return "1-Year Flex CUD (Maximum Flexibility)"
