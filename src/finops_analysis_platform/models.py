"""models.py

Defines the core data structures for the FinOps Analysis Platform using
dataclasses. This provides a strongly-typed, self-documenting, and stable
data model for analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class PortfolioLayer:
    """Represents a single layer in a CUD portfolio recommendation."""

    machine_type: str
    strategy: str
    monthly_spend: float
    monthly_savings: float


@dataclass
class PortfolioRecommendation:
    """Represents a complete CUD portfolio recommendation."""

    layers: List[PortfolioLayer] = field(default_factory=list)
    total_monthly_savings: float = 0.0
    total_annual_savings: float = 0.0
    coverage_percentage: float = 0.0


@dataclass
class RiskAssessment:
    """Represents the risk assessment for a CUD portfolio."""

    overall_risk: str
    recommendation: str
    risk_distribution: Dict[str, float] = field(default_factory=dict)


@dataclass
class AnalysisResults:
    """
    A comprehensive, strongly-typed container for all CUD analysis results.
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
