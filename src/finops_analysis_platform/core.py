"""Core analysis engine for the FinOps CUD Analysis Platform."""

import logging
from datetime import datetime
from typing import Optional

import pandas as pd

from .config_manager import ConfigManager
from .models import AnalysisResults
from .portfolio_recommender import AIPortfolioRecommender, RuleBasedPortfolioRecommender
from .recommendation_analyzer import RecommendationAnalyzer
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
        *,
        rule_based_recommender: RuleBasedPortfolioRecommender,
        ai_recommender: AIPortfolioRecommender,
        risk_assessor: RiskAssessor,
        recommendation_analyzer: RecommendationAnalyzer,
        billing_data: Optional[pd.DataFrame] = None,
        recommendations_data: Optional[pd.DataFrame] = None,
    ):
        """Initializes the CUD analyzer."""
        self.config_manager = config_manager
        self.spend_analyzer = spend_analyzer
        self.savings_calculator = savings_calculator
        self.rule_based_recommender = rule_based_recommender
        self.ai_recommender = ai_recommender
        self.risk_assessor = risk_assessor
        self.recommendation_analyzer = recommendation_analyzer
        self.billing_data = self._validate_billing_data(billing_data)
        self.recommendations_data = recommendations_data

    def _validate_billing_data(
        self, dataframe: Optional[pd.DataFrame]
    ) -> Optional[pd.DataFrame]:
        """Validates that the billing DataFrame has the required columns."""
        if dataframe is None or dataframe.empty:
            logger.warning("Billing data is empty. Analysis may use sample data.")
            return None
        required_cols = ["Cost"]
        sku_cols = ["SKU", "Sku Description"]
        has_sku = any(col in dataframe.columns for col in sku_cols)
        has_required = all(col in dataframe.columns for col in required_cols)
        if not has_sku or not has_required:
            logger.error(
                "Billing data is missing required columns ('Cost' and "
                "'SKU' or 'Sku Description')."
            )
            return None
        logger.info("Billing data validation successful.")
        return dataframe

    def generate_comprehensive_analysis(self) -> AnalysisResults:
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
        active_assist = self.recommendation_analyzer.analyze(self.recommendations_data)

        analysis = AnalysisResults(
            machine_spend_distribution=machine_distribution,
            savings_by_machine=savings_by_machine,
            portfolio_recommendation=portfolio,
            ai_portfolio_recommendation=ai_portfolio,
            risk_assessment=risk_assessment,
            active_assist_summary=active_assist,
            analysis_date=datetime.now(),
            config=self.config_manager.get("analysis", {}),
        )
        logger.info("Comprehensive CUD analysis complete.")
        return analysis
