"""Assesses CUD portfolio risk based on machine type stability."""

from typing import Dict

from .models import RiskAssessment


class RiskAssessor:
    """Assesses portfolio risk based on machine type stability."""

    def assess_risk(self, savings_by_machine: Dict) -> RiskAssessment:
        """Assesses the portfolio risk based on machine type stability.

        This method uses a simple heuristic to categorize spend into low,
        medium, and high risk buckets based on the machine type's typical
        workload stability (e.g., general purpose vs. specialized GPUs).

        Args:
            savings_by_machine: A dictionary containing potential savings and
                spend for each machine type.

        Returns:
            A `RiskAssessment` object with the overall risk and recommendation.
        """
        risk_levels = {"low": 0.0, "medium": 0.0, "high": 0.0}
        for machine_type, savings in savings_by_machine.items():
            spend = savings["monthly_spend"]
            if "m" in machine_type or "c" in machine_type:
                risk_levels["low"] += spend
            elif "gpu" in machine_type or "a2" in machine_type:
                risk_levels["high"] += spend
            else:
                risk_levels["medium"] += spend

        total_spend = sum(risk_levels.values())
        if total_spend == 0:
            return RiskAssessment(
                overall_risk="UNKNOWN",
                recommendation="No data to assess.",
                risk_distribution=risk_levels,
            )

        high_risk_pct = risk_levels["high"] / total_spend
        if high_risk_pct > 0.3:
            overall_risk = "HIGH"
            recommendation = "High exposure to specialized hardware. Favor Flex CUDs."
        elif high_risk_pct > 0.1:
            overall_risk = "MEDIUM"
            recommendation = "Balanced portfolio. Mix of Resource and Flex CUDs."
        else:
            overall_risk = "LOW"
            recommendation = "Low-risk portfolio. Good for 3-year Resource CUDs."

        return RiskAssessment(
            overall_risk=overall_risk,
            recommendation=recommendation,
            risk_distribution=risk_levels,
        )
