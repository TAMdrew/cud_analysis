# type: ignore
"""Advanced FinOps Analytics Module.

This module provides sophisticated quantitative finance models for cloud cost
optimization, including portfolio theory, option pricing, and stochastic
modeling to support advanced CUD analysis.
"""

import logging
import warnings
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, cast

import numpy as np
import numpy_financial as npf
import pandas as pd
from scipy import optimize, stats
from scipy.stats import norm
from statsmodels.tsa.holtwinters import ExponentialSmoothing

warnings.filterwarnings("ignore", category=RuntimeWarning)
logger = logging.getLogger(__name__)


class RiskModel(Enum):
    """Enumeration for risk modeling approaches."""

    VAR = "Value at Risk"
    CVAR = "Conditional Value at Risk"
    MONTE_CARLO = "Monte Carlo Simulation"
    BLACK_SCHOLES = "Black-Scholes Option Pricing"


@dataclass
class FinancialMetrics:
    """A container for key financial metrics."""

    npv: float
    irr: float
    payback_period: float
    roi: float
    break_even_point: float
    risk_adjusted_return: float


class Forecast(TypedDict, total=False):
    forecast: Optional[pd.Series]
    lower_95: Optional[pd.Series]
    upper_95: Optional[pd.Series]


class AdvancedAnalytics(TypedDict, total=False):
    portfolio_optimization: Dict[str, Any]
    risk_metrics: Dict[str, Any]
    monte_carlo_projection: Dict[str, Any]
    commitment_ladder: Dict[str, Any]
    financial_metrics: Dict[str, Any]
    option_valuation: Dict[str, Any]
    stress_test_results: Dict[str, Any]


class AnalysisResults(TypedDict, total=False):
    machine_spend_distribution: Dict[str, float]
    savings_by_machine: Dict[str, Any]
    portfolio_recommendation: Dict[str, Any]
    ai_portfolio_recommendation: Optional[Dict]
    total_savings_summary: Dict[str, float]
    risk_assessment: Dict[str, Any]
    analysis_date: datetime
    config: Dict[str, Any]
    advanced_analytics: AdvancedAnalytics


class AdvancedCUDOptimizer:
    """
    Implements advanced CUD optimization using quantitative finance methods.
    """

    def __init__(self, risk_free_rate: float = 0.03):
        """Initializes the optimizer with a risk-free rate."""
        self.risk_free_rate = risk_free_rate
        self.volatility_estimates: Dict[str, float] = {}

    def calculate_optimal_portfolio(
        self, machine_returns: Dict[str, float], historical_usage: pd.DataFrame
    ) -> Dict[str, Any]:
        """Applies Modern Portfolio Theory to CUD allocation."""
        returns = self._calculate_returns(machine_returns, historical_usage)

        if not returns:
            return {"optimal_allocation": {}}

        optimal_weights_result = self._optimize_portfolio_weights(returns)
        optimal_weights = dict(zip(returns.keys(), optimal_weights_result.x))
        metrics = self._calculate_portfolio_metrics(optimal_weights_result, returns)

        return {"optimal_allocation": optimal_weights, **metrics}

    def _calculate_returns(
        self, machine_returns: Dict[str, float], historical_usage: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate returns for each machine type."""
        returns = {}
        for machine_type in machine_returns:
            if machine_type in historical_usage.columns:
                series = historical_usage[machine_type]
                log_returns = np.log(series / series.shift(1)).dropna()
                returns[machine_type] = log_returns.mean() * 252
                self.volatility_estimates[machine_type] = log_returns.std() * np.sqrt(
                    252
                )
        return returns

    def _optimize_portfolio_weights(
        self, returns: Dict[str, float]
    ) -> optimize.OptimizeResult:
        """Optimize portfolio weights using Sharpe ratio maximization."""
        n_assets = len(returns)
        cov_matrix = np.eye(n_assets) * 0.1

        def neg_sharpe(weights, exp_returns, cov, rf_rate):
            p_return = np.sum(exp_returns * weights)
            p_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
            return -(p_return - rf_rate) / p_std if p_std > 0 else -np.inf

        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1 / n_assets] * n_assets)

        result = optimize.minimize(
            neg_sharpe,
            initial_guess,
            args=(np.array(list(returns.values())), cov_matrix, self.risk_free_rate),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        return result

    def _calculate_portfolio_metrics(
        self, weights_result: optimize.OptimizeResult, returns: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate portfolio performance metrics."""
        optimal_weights = weights_result.x
        portfolio_return = np.sum(optimal_weights * np.array(list(returns.values())))
        sharpe_ratio = -weights_result.fun if weights_result.fun != -np.inf else 0
        portfolio_volatility = np.sqrt(
            np.dot(
                optimal_weights.T, np.dot(np.eye(len(returns)) * 0.1, optimal_weights)
            )
        )
        diversification_ratio = 1 / np.sum(optimal_weights**2)

        return {
            "expected_return": portfolio_return,
            "sharpe_ratio": sharpe_ratio,
            "portfolio_volatility": portfolio_volatility,
            "diversification_ratio": diversification_ratio,
        }

    def calculate_var_cvar(
        self,
        monthly_costs: np.ndarray,
        confidence_level: float = 0.95,
        time_horizon: int = 12,
    ) -> Dict[str, Any]:
        """Calculates Value at Risk and Conditional Value at Risk."""
        mean_cost, sigma = stats.norm.fit(monthly_costs)
        n_simulations = 10000
        simulated_costs = np.random.normal(
            mean_cost, sigma, (n_simulations, time_horizon)
        )
        total_costs = np.sum(simulated_costs, axis=1)
        var_threshold = np.percentile(total_costs, (1 - confidence_level) * 100)
        cvar = np.mean(total_costs[total_costs >= var_threshold])

        return {
            "var_95": var_threshold,
            "cvar_95": cvar,
            "expected_cost": np.mean(total_costs),
            "cost_volatility": np.std(total_costs),
            "worst_case_scenario": np.max(total_costs),
            "best_case_scenario": np.min(total_costs),
            "probability_exceeding_budget": lambda budget: np.mean(
                total_costs > budget
            ),
        }

    # pylint: disable=too-many-arguments
    def black_scholes_cud_valuation(
        self,
        spot_price: float,
        strike_price: float,
        time_to_maturity: float,
        *,
        volatility: float,
        discount_rate: float,
    ) -> Dict[str, Any]:
        """Applies Black-Scholes model to value a CUD as a call option."""
        if volatility == 0:
            # Handle the zero volatility case to avoid division by zero
            intrinsic_value = max(spot_price - strike_price, 0)
            option_value = intrinsic_value * np.exp(-discount_rate * time_to_maturity)
            return {
                "option_value": option_value,
                "intrinsic_value": intrinsic_value,
                "time_value": 0,
                "greeks": {
                    "delta": 1 if spot_price > strike_price else 0,
                    "gamma": 0,
                    "theta": 0,
                    "vega": 0,
                    "rho": 0,
                },
                "break_even_utilization": strike_price / spot_price,
                "implied_volatility_target": 0,
            }

        d1 = (
            np.log(spot_price / strike_price)
            + (discount_rate + 0.5 * volatility**2) * time_to_maturity
        ) / (volatility * np.sqrt(time_to_maturity))
        d2 = d1 - volatility * np.sqrt(time_to_maturity)

        call_value = spot_price * norm.cdf(d1) - strike_price * np.exp(
            -discount_rate * time_to_maturity
        ) * norm.cdf(d2)

        delta = norm.cdf(d1)
        gamma = norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_maturity))
        theta = -(spot_price * norm.pdf(d1) * volatility) / (
            2 * np.sqrt(time_to_maturity)
        ) - discount_rate * strike_price * np.exp(
            -discount_rate * time_to_maturity
        ) * norm.cdf(
            d2
        )
        vega = spot_price * norm.pdf(d1) * np.sqrt(time_to_maturity)
        rho = (
            strike_price
            * time_to_maturity
            * np.exp(-self.risk_free_rate * time_to_maturity)
            * norm.cdf(d2)
        )

        return {
            "option_value": call_value,
            "intrinsic_value": max(spot_price - strike_price, 0),
            "time_value": call_value - max(spot_price - strike_price, 0),
            "greeks": {
                "delta": delta,
                "gamma": gamma,
                "theta": theta,
                "vega": vega,
                "rho": rho,
            },
            "break_even_utilization": strike_price / spot_price,
            "implied_volatility_target": volatility,
        }

    def monte_carlo_simulation(
        self,
        initial_cost: float,
        drift: float,
        volatility: float,
        *,
        time_periods: int = 36,
        n_simulations: int = 10000,
    ) -> Dict[str, Any]:
        """Runs a Monte Carlo simulation for cloud cost projections."""
        time_step = 1 / 12
        random_shocks = np.random.normal(0, 1, (n_simulations, time_periods))
        price_paths = np.zeros((n_simulations, time_periods + 1))
        price_paths[:, 0] = initial_cost

        for time_period in range(1, time_periods + 1):
            price_paths[:, time_period] = price_paths[:, time_period - 1] * np.exp(
                (drift - 0.5 * volatility**2) * time_step
                + volatility * np.sqrt(time_step) * random_shocks[:, time_period - 1]
            )

        final_costs = price_paths[:, -1]
        return {
            "expected_final_cost": np.mean(final_costs),
            "median_final_cost": np.median(final_costs),
            "cost_std_dev": np.std(final_costs),
            "percentile_5": np.percentile(final_costs, 5),
            "percentile_95": np.percentile(final_costs, 95),
            "probability_cost_doubles": np.mean(final_costs > 2 * initial_cost),
            "max_drawdown": np.min(np.min(price_paths, axis=1) / initial_cost - 1),
            "paths_summary": {
                "mean_path": np.mean(price_paths, axis=0),
                "upper_bound": np.percentile(price_paths, 95, axis=0),
                "lower_bound": np.percentile(price_paths, 5, axis=0),
            },
        }

    def calculate_financial_metrics(
        self,
        initial_investment: float,
        cash_flows: List[float],
        discount_rate: Optional[float] = None,
    ) -> FinancialMetrics:
        """Calculates comprehensive financial metrics for a CUD investment."""
        if discount_rate is None:
            discount_rate = self.risk_free_rate

        npv = npf.npv(discount_rate, [-initial_investment] + cash_flows)
        try:
            irr = npf.irr([-initial_investment] + cash_flows)
        except (ValueError, RuntimeError) as exception:
            # IRR calculation can fail for certain cash flow patterns
            logger.warning("IRR calculation failed for cash flows: %s", str(exception))
            irr = float("nan")  # Use NaN instead of 0 to indicate calculation failure

        cumulative_cf = np.cumsum([-initial_investment] + cash_flows)
        payback_idx = np.where(cumulative_cf > 0)[0]
        payback_period = payback_idx[0] + 1 if payback_idx.size > 0 else float("inf")

        total_return = sum(cash_flows)
        roi = (
            (total_return - initial_investment) / initial_investment
            if initial_investment
            else 0
        )

        break_even = (
            initial_investment / np.mean(cash_flows)
            if np.mean(cash_flows) > 0
            else float("inf")
        )

        returns = (
            np.array(cash_flows) / initial_investment
            if initial_investment
            else np.array([0])
        )
        risk_adjusted = (np.mean(returns) - discount_rate) / (np.std(returns) + 1e-10)

        return FinancialMetrics(
            npv=npv,
            irr=irr,
            payback_period=payback_period,
            roi=roi,
            break_even_point=break_even,
            risk_adjusted_return=risk_adjusted,
        )


class CloudEconomicsModeler:
    """Models cloud economics with elasticity and demand forecasting."""

    def calculate_price_elasticity(
        self, price_history: pd.Series, demand_history: pd.Series
    ) -> float:
        """Calculates price elasticity of demand for cloud resources."""
        log_price = np.log(price_history)
        log_demand = np.log(demand_history)
        coef = np.polyfit(log_price, log_demand, 1)[0]
        return coef

    def forecast_demand(
        self,
        historical_usage: pd.Series,
        periods: int = 12,
        method: str = "holt_winters",
    ) -> Dict[str, Any]:
        """Forecasts demand using time series analysis."""
        forecast, lower_bound, upper_bound = None, None, None

        if method == "holt_winters" and len(historical_usage) >= 24:
            model = ExponentialSmoothing(
                historical_usage,
                seasonal_periods=12,
                trend="add",
                seasonal="add",
                initialization_method="estimated",
            )
            fit = model.fit()
            forecast = fit.forecast(periods)
            residuals = historical_usage - fit.fittedvalues
            std_error = np.std(residuals)
            lower_bound = forecast - 1.96 * std_error
            upper_bound = forecast + 1.96 * std_error

        return {
            "forecast": forecast,
            "lower_95": lower_bound,
            "upper_95": upper_bound,
        }

    def calculate_optimal_commitment_ladder(
        self, forecast: Forecast, risk_tolerance: float = 0.5
    ) -> Dict:
        """Designs an optimal CUD commitment ladder strategy."""
        if "forecast" not in forecast or forecast["forecast"] is None:
            return {}

        base_demand = forecast["forecast"].mean()

        if "lower_95" in forecast and forecast["lower_95"] is not None:
            high_confidence_level = forecast["lower_95"].mean()
        else:
            std_dev = (
                forecast["forecast"].std()
                if forecast["forecast"].std() > 0
                else base_demand * 0.1
            )
            high_confidence_level = base_demand - 1.96 * std_dev

        if risk_tolerance < 0.3:  # Conservative
            ladder = {
                "3_year_commitment": high_confidence_level * 0.5,
                "1_year_commitment": high_confidence_level * 0.3,
                "flex_commitment": high_confidence_level * 0.2,
                "on_demand_buffer": base_demand - high_confidence_level,
            }
        elif risk_tolerance < 0.7:  # Moderate
            ladder = {
                "3_year_commitment": high_confidence_level * 0.6,
                "1_year_commitment": high_confidence_level * 0.25,
                "flex_commitment": high_confidence_level * 0.15,
                "on_demand_buffer": base_demand - high_confidence_level,
            }
        else:  # Aggressive
            ladder = {
                "3_year_commitment": base_demand * 0.7,
                "1_year_commitment": base_demand * 0.2,
                "flex_commitment": base_demand * 0.1,
                "on_demand_buffer": base_demand * 0.1,
            }

        total_savings = (
            ladder.get("3_year_commitment", 0) * 0.55
            + ladder.get("1_year_commitment", 0) * 0.37
            + ladder.get("flex_commitment", 0) * 0.28
        )

        return {"ladder_strategy": ladder, "expected_monthly_savings": total_savings}


class QuantitativeRiskAnalyzer:
    """Performs sophisticated risk analysis using quantitative methods."""

    def calculate_commitment_risk_score(
        self,
        commitment_amount: float,
        historical_usage: pd.Series,
        commitment_period: int,
    ) -> Dict[str, Any]:
        """Calculates a comprehensive risk score for a CUD commitment."""
        del commitment_period  # Unused in this risk model version.

        mean_usage = historical_usage.mean()
        std_usage = historical_usage.std()
        coefficient_of_variation = (
            std_usage / mean_usage if mean_usage > 0 else float("inf")
        )

        downside_deviations = historical_usage[historical_usage < commitment_amount]
        downside_risk = (
            np.mean((commitment_amount - downside_deviations) / commitment_amount)
            if not downside_deviations.empty
            else 0
        )

        prob_underutilization = (
            norm.cdf((commitment_amount - mean_usage) / std_usage)
            if std_usage > 0
            else 0.5
        )

        risk_score = (
            coefficient_of_variation * 20
            + downside_risk * 50
            + prob_underutilization * 30
        )

        if risk_score < 30:
            risk_category = "LOW"
        elif risk_score < 60:
            risk_category = "MEDIUM"
        else:
            risk_category = "HIGH"

        return {
            "risk_score": min(risk_score, 100),
            "risk_category": risk_category,
            "metrics": {
                "coefficient_of_variation": coefficient_of_variation,
                "downside_risk": downside_risk,
                "underutilization_probability": prob_underutilization,
            },
        }

    def stress_test_scenarios(
        self, base_cost: float, commitment_level: float
    ) -> Dict[str, Any]:
        """Runs a stress test scenarios for risk assessment."""
        scenarios = {
            "baseline": {"usage_change": 0, "cost_impact": 0},
            "mild_recession": {"usage_change": -0.20},
            "severe_recession": {"usage_change": -0.40},
            "rapid_growth": {"usage_change": 0.50},
            "technology_shift": {"usage_change": -0.30},
        }
        for name, scenario in scenarios.items():
            if name == "baseline":
                continue
            new_cost = base_cost * (1 + scenario["usage_change"])
            underutilization_cost = max(0, commitment_level - new_cost)
            overage_cost = max(0, new_cost - base_cost) * 0.3  # Overage premium
            scenario["cost_impact"] = underutilization_cost + overage_cost

        weights = {
            "baseline": 0.4,
            "mild_recession": 0.25,
            "severe_recession": 0.1,
            "rapid_growth": 0.15,
            "technology_shift": 0.1,
        }

        weighted_impact = sum(
            scenario["cost_impact"] * weights[name]
            for name, scenario in scenarios.items()
        )

        return {
            "scenarios": scenarios,
            "weighted_risk_impact": weighted_impact,
            "worst_case_impact": max(s["cost_impact"] for s in scenarios.values()),
            "risk_adjusted_commitment": (
                commitment_level * (1 - weighted_impact / base_cost)
                if base_cost > 0
                else commitment_level
            ),
        }


def _calculate_historical_usage(
    analysis_results: AnalysisResults, billing_data: Optional[pd.DataFrame] = None
) -> pd.Series:
    """Helper to extract or generate historical usage data."""
    spend_dist = analysis_results.get("machine_spend_distribution", {})
    total_spend = sum(spend_dist.values())

    if billing_data is None or billing_data.empty:
        np.random.seed(42)
        std_dev = total_spend * 0.1 if total_spend > 0 else 1
        return pd.Series(np.random.normal(total_spend, std_dev, 36))
    return billing_data.groupby(pd.Grouper(freq="ME"))["Cost"].sum()


def enhance_with_advanced_analytics(
    analysis_results: AnalysisResults, billing_data: Optional[pd.DataFrame] = None
) -> AnalysisResults:
    """Enhances analysis results with advanced quantitative methods."""
    optimizer = AdvancedCUDOptimizer()
    modeler = CloudEconomicsModeler()
    risk_analyzer = QuantitativeRiskAnalyzer()

    historical_usage = _calculate_historical_usage(analysis_results, billing_data)
    spend_dist = analysis_results.get("machine_spend_distribution", {})
    total_spend = sum(spend_dist.values())

    portfolio = (
        optimizer.calculate_optimal_portfolio(
            spend_dist, pd.DataFrame({k: [v] * 12 for k, v in spend_dist.items()})
        )
        if len(spend_dist) > 1
        else {"optimal_allocation": {}, "sharpe_ratio": 0}
    )
    var_cvar = optimizer.calculate_var_cvar(historical_usage.values)
    monte_carlo = optimizer.monte_carlo_simulation(
        initial_cost=total_spend, drift=0.05, volatility=0.2
    )
    forecast = cast(Forecast, modeler.forecast_demand(historical_usage))
    commitment_ladder = (
        modeler.calculate_optimal_commitment_ladder(forecast)
        if forecast.get("forecast") is not None
        else {}
    )
    bs_valuation = optimizer.black_scholes_cud_valuation(
        spot_price=total_spend,
        strike_price=total_spend * 0.7,
        time_to_maturity=3,
        volatility=0.2,
        discount_rate=0.03,
    )
    cash_flows = [
        analysis_results.get("total_savings_summary", {}).get("optimal_mix", 0)
    ] * 36
    financial_metrics = optimizer.calculate_financial_metrics(
        initial_investment=total_spend * 0.7, cash_flows=cash_flows
    )
    risk_score = risk_analyzer.calculate_commitment_risk_score(
        commitment_amount=total_spend * 0.7,
        historical_usage=historical_usage,
        commitment_period=36,
    )
    stress_test = risk_analyzer.stress_test_scenarios(
        base_cost=total_spend, commitment_level=total_spend * 0.7
    )

    enhanced_analysis = deepcopy(analysis_results)
    enhanced_analysis["advanced_analytics"] = {  # type: ignore
        "portfolio_optimization": portfolio,
        "risk_metrics": {**var_cvar, **risk_score},
        "monte_carlo_projection": monte_carlo,
        "commitment_ladder": commitment_ladder,
        "financial_metrics": financial_metrics.__dict__,
        "option_valuation": bs_valuation,
        "stress_test_results": stress_test,
    }
    return enhanced_analysis
