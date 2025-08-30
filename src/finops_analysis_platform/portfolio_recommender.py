import json
import logging
from pathlib import Path
from typing import Any, Dict, Protocol, cast

from .config_manager import ConfigManager
from .gemini_service import generate_content
from .models import PortfolioLayer, PortfolioRecommendation

logger = logging.getLogger(__name__)


class PortfolioRecommender(Protocol):
    """Protocol for portfolio recommenders."""

    def recommend_portfolio(
        self, savings_by_machine: Dict
    ) -> PortfolioRecommendation | Dict:
        """Recommends a CUD portfolio.

        Args:
            savings_by_machine: A dictionary with savings data for each
                machine type.

        Returns:
            A `PortfolioRecommendation` object or a dictionary for AI results.
        """
        ...


class RuleBasedPortfolioRecommender(PortfolioRecommender):
    """Generates a portfolio recommendation based on predefined rules."""

    def recommend_portfolio(self, savings_by_machine: Dict) -> PortfolioRecommendation:
        """Generates a simple, rule-based portfolio recommendation.

        This method selects the CUD option with the highest monthly savings for
        each machine type and aggregates them into a portfolio.

        Args:
            savings_by_machine: A dictionary containing potential savings for
                each machine type.

        Returns:
            A `PortfolioRecommendation` object detailing the optimal portfolio.
        """
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
                    PortfolioLayer(
                        machine_type=machine_type,
                        strategy=best_option,
                        monthly_spend=savings["stable_workload"],
                        monthly_savings=current_options[best_option]["monthly_savings"],
                    )
                )

        total_savings = sum(layer.monthly_savings for layer in layers)
        total_spend = sum(s["monthly_spend"] for s in savings_by_machine.values())

        coverage = (total_savings / total_spend * 100) if total_spend > 0 else 0
        return PortfolioRecommendation(
            layers=sorted(layers, key=lambda x: x.monthly_savings, reverse=True),
            total_monthly_savings=total_savings,
            total_annual_savings=total_savings * 12,
            coverage_percentage=coverage,
        )


class AIPortfolioRecommender(PortfolioRecommender):
    """Generates a CUD portfolio optimization using the Gemini AI."""

    def __init__(self, config_manager: ConfigManager):
        """Initializes the AIPortfolioRecommender.

        Args:
            config_manager: The application's configuration manager.
        """
        self.config_manager = config_manager

    def recommend_portfolio(self, savings_by_machine: Dict) -> Dict[str, Any]:
        """Generates a CUD portfolio optimization using the Gemini AI.

        Args:
            savings_by_machine: A dictionary containing potential savings for
                each machine type.

        Returns:
            A dictionary containing the AI's portfolio recommendation, or an
            error message if the generation fails.
        """
        project_id = self.config_manager.get("gcp.project_id")
        location = self.config_manager.get("gcp.location", "us-central1")

        if not project_id:
            logger.warning(
                "Cannot generate AI portfolio: gcp.project_id not configured."
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
        response = generate_content(
            prompt=prompt, project_id=project_id, location=location
        )

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
