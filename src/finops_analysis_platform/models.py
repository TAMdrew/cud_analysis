"""Defines the core data structures for the FinOps Analysis Platform.

This module provides strongly-typed, self-documenting, and stable data models
for analysis results, conforming to best practices for data representation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class PortfolioLayer:
    """Represents a single layer in a CUD portfolio recommendation.

    Attributes:
        machine_type: The base machine type for the commitment (e.g., 'n2').
        strategy: The recommended CUD strategy (e.g., '3yr_resource').
        monthly_spend: The monthly spend to be covered by this commitment.
        monthly_savings: The potential monthly savings from this commitment.
    """

    machine_type: str
    strategy: str
    monthly_spend: float
    monthly_savings: float


@dataclass
class PortfolioRecommendation:
    """Represents a complete CUD portfolio recommendation.

    Attributes:
        layers: A list of `PortfolioLayer` objects, sorted by savings.
        total_monthly_savings: The sum of savings from all layers.
        total_annual_savings: The total monthly savings multiplied by 12.
        coverage_percentage: The percentage of total spend covered by CUDs.
    """

    layers: List[PortfolioLayer] = field(default_factory=list)
    total_monthly_savings: float = 0.0
    total_annual_savings: float = 0.0
    coverage_percentage: float = 0.0


@dataclass
class RiskAssessment:
    """Represents the risk assessment for a CUD portfolio.

    Attributes:
        overall_risk: The calculated overall risk level ('LOW', 'MEDIUM', 'HIGH').
        recommendation: A text-based recommendation based on the risk profile.
        risk_distribution: A dictionary mapping risk levels to the spend in each.
    """

    overall_risk: str
    recommendation: str
    risk_distribution: Dict[str, float] = field(default_factory=dict)


@dataclass
class AnalysisResults:
    """A comprehensive, strongly-typed container for all CUD analysis results.

    Attributes:
        machine_spend_distribution: Maps machine types to their total monthly spend.
        savings_by_machine: Detailed savings calculations for each machine type.
        portfolio_recommendation: The rule-based portfolio recommendation.
        risk_assessment: The overall risk assessment of the portfolio.
        analysis_date: Timestamp of when the analysis was performed.
        config: The analysis configuration settings used for the run.
        ai_portfolio_recommendation: The portfolio recommendation from the AI.
        advanced_analytics: Results from advanced quantitative modeling.
        active_assist_summary: A summary of savings from Active Assist.
    """

    machine_spend_distribution: Dict[str, float]
    savings_by_machine: Dict[str, Any]
    portfolio_recommendation: PortfolioRecommendation
    risk_assessment: RiskAssessment
    analysis_date: datetime
    config: Dict[str, Any]
    ai_portfolio_recommendation: Optional[Dict[str, Any]] = None
    advanced_analytics: Optional[Dict[str, Any]] = None
    active_assist_summary: Optional[Dict[str, float]] = None
