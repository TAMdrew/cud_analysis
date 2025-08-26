"""Recommends a CUD portfolio."""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Protocol, cast

from .config_manager import ConfigManager
from .gemini_service import generate_content, initialize_gemini

logger = logging.getLogger(__name__)


class PortfolioRecommender(Protocol):
    """Protocol for portfolio recommenders."""

    def recommend_portfolio(self, savings_by_machine: Dict) -> Dict[str, Any]:
        """Recommends a CUD portfolio."""
        ...


class RuleBasedPortfolioRecommender(PortfolioRecommender):
    """Generates a simple, rule-based portfolio recommendation."""

    def recommend_portfolio(self, savings_by_machine: Dict) -> Dict[str, Any]:
        """Generates a simple, rule-based portfolio recommendation."""
        layers = []
        for machine_type, savings in savings_by_machine.items():
            current_options = savings["savings_options"]
            best_option = max(
                current_options,
                key=lambda k: cast(Dict[str, float], current_options[k])[
                    "monthly_savings"
                ],
            )
            if current_options[best_option]["monthly_savings"] > 0:
                layers.append(
                    {
                        "machine_type": machine_type,
                        "strategy": best_option,
                        "monthly_spend": savings["stable_workload"],
                        "monthly_savings": current_options[best_option][
                            "monthly_savings"
                        ],
                    }
                )

        total_savings = sum(layer["monthly_savings"] for layer in layers)
        total_spend = sum(s["monthly_spend"] for s in savings_by_machine.values())

        coverage = (total_savings / total_spend * 100) if total_spend > 0 else 0
        return {
            "layers": sorted(layers, key=lambda x: x["monthly_savings"], reverse=True),
            "total_monthly_savings": total_savings,
            "total_annual_savings": total_savings * 12,
            "coverage_percentage": coverage,
        }


class AIPortfolioRecommender(PortfolioRecommender):
    """Generates a CUD portfolio optimization using the Gemini AI."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.gemini_initialized = self._initialize_gemini()

    def _initialize_gemini(self) -> bool:
        """Initializes the Gemini client if configured."""
        project_id = self.config_manager.get("gcp.project_id")
        location = self.config_manager.get("gcp.location", "us-central1")
        if project_id and self._is_valid_project_id(project_id):
            return initialize_gemini(project_id=project_id, location=location)
        logger.warning(
            "Gemini client not initialized due to missing or invalid project_id."
        )
        return False

    def _is_valid_project_id(self, project_id: str) -> bool:
        """Validates GCP project ID format."""
        # GCP project IDs must be 6-30 characters, lowercase letters, digits, hyphens
        pattern = r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$"
        return bool(re.match(pattern, project_id))

    def recommend_portfolio(self, savings_by_machine: Dict) -> Dict[str, Any]:
        """Generates a CUD portfolio optimization using the Gemini AI."""
        if not self.gemini_initialized:
            logger.warning(
                "Cannot generate AI portfolio optimization without Gemini client."
            )
            return {}

        risk_tolerance = self.config_manager.get("analysis.risk_tolerance", "medium")
        spend_data = {
            mt: {"monthly_spend": data["monthly_spend"], "family": data["family"]}
            for mt, data in savings_by_machine.items()
        }
        spend_data_json = json.dumps(spend_data, indent=2)

        prompt_path = Path(__file__).parent / "prompts" / "portfolio_optimization.txt"
        with open(prompt_path, "r", encoding="utf-8") as prompt_file:
            prompt_template = prompt_file.read()

        prompt = prompt_template.format(
            risk_tolerance=risk_tolerance.upper(), spend_data_json=spend_data_json
        )

        logger.info(
            "Generating AI CUD portfolio for risk tolerance: %s", risk_tolerance
        )
        response = generate_content(prompt)

        if not (response and response.text):
            return {"error": "No response from AI for portfolio optimization."}
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.error("Failed to decode Gemini's portfolio recommendation.")
            return {
                "error": "Failed to parse AI response.",
                "raw_response": response.text,
            }
