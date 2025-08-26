"""Core analysis engine for the FinOps CUD Analysis Platform."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd

from .config_manager import ConfigManager
from .portfolio_recommender import AIPortfolioRecommender, RuleBasedPortfolioRecommender
from .risk_assessor import RiskAssessor
from .savings_calculator import SavingsCalculator
from .spend_analyzer import SpendAnalyzer

logger = logging.getLogger(__name__)


class CUDAnalyzer:
    """Core engine for performing Committed Use Discount (CUD) analysis."""

    def __init__(
        self,
        config_manager: ConfigManager,
        spend_analyzer: SpendAnalyzer,
        savings_calculator: SavingsCalculator,
        rule_based_recommender: RuleBasedPortfolioRecommender,
        ai_recommender: AIPortfolioRecommender,
        risk_assessor: RiskAssessor,
        billing_data: Optional[pd.DataFrame] = None,
    ):
        """Initializes the CUD analyzer."""
        self.config_manager = config_manager
        self.spend_analyzer = spend_analyzer
        self.savings_calculator = savings_calculator
        self.rule_based_recommender = rule_based_recommender
        self.ai_recommender = ai_recommender
        self.risk_assessor = risk_assessor
        self.billing_data = self._validate_billing_data(billing_data)
        self.analysis_results: Dict[str, Any] = {}

    def _validate_billing_data(
        self, df: Optional[pd.DataFrame]
    ) -> Optional[pd.DataFrame]:
        """Validates that the billing DataFrame has the required columns."""
        if df is None or df.empty:
            logger.warning("Billing data is empty. Analysis may use sample data.")
            return None
        required_cols = ["Cost"]
        sku_cols = ["SKU", "Sku Description"]
        has_sku = any(col in df.columns for col in sku_cols)
        has_required = all(col in df.columns for col in required_cols)
        if not has_sku or not has_required:
            logger.error(
                "Billing data is missing required columns ('Cost' and "
                "'SKU' or 'Sku Description')."
            )
            return None
        logger.info("Billing data validation successful.")
        return df

    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generates a full CUD analysis."""
        logger.info("Starting comprehensive CUD analysis...")
        machine_distribution = self.spend_analyzer.analyze_machine_distribution(
            self.billing_data
        )
        savings_by_machine = self.savings_calculator.calculate_savings_by_machine(
            machine_distribution
        )
        portfolio = self.rule_based_recommender.recommend_portfolio(savings_by_machine)
        risk_assessment = self.risk_assessor.assess_risk(savings_by_machine)
        ai_portfolio = self.ai_recommender.recommend_portfolio(savings_by_machine)

        self.analysis_results = {
            "machine_spend_distribution": machine_distribution,
            "savings_by_machine": savings_by_machine,
            "portfolio_recommendation": portfolio,
            "ai_portfolio_recommendation": ai_portfolio,
            "risk_assessment": risk_assessment,
            "analysis_date": datetime.now(),
            "config": self.config_manager.get("analysis", {}),
        }
        logger.info("Comprehensive CUD analysis complete.")
        return self.analysis_results
