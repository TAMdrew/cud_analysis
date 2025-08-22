#!/usr/bin/env python3
"""
Advanced FinOps Analytics Module
Sophisticated quantitative finance models for cloud cost optimization
Version: 1.0.0
Author: Senior Cloud Economics Team
"""

import numpy as np
import pandas as pd
from scipy import optimize, stats
from scipy.stats import norm, lognorm
from typing import Dict, List, Tuple, Optional, Union
import warnings
from dataclasses import dataclass
from enum import Enum
import numpy_financial as npf

warnings.filterwarnings('ignore')

class RiskModel(Enum):
    """Risk modeling approaches"""
    VAR = "Value at Risk"
    CVAR = "Conditional Value at Risk"
    MONTE_CARLO = "Monte Carlo Simulation"
    BLACK_SCHOLES = "Black-Scholes Option Pricing"

@dataclass
class FinancialMetrics:
    """Financial metrics container"""
    npv: float
    irr: float
    payback_period: float
    roi: float
    break_even_point: float
    risk_adjusted_return: float

class AdvancedCUDOptimizer:
    """
    Advanced CUD optimization using quantitative finance methods
    Implements portfolio theory, option pricing, and stochastic modeling
    """

    def __init__(self, risk_free_rate: float = 0.03):
        self.risk_free_rate = risk_free_rate
        self.volatility_estimates = {}

    def calculate_optimal_portfolio(self,
                                   machine_types: Dict[str, float],
                                   historical_usage: pd.DataFrame) -> Dict:
        """
        Apply Modern Portfolio Theory to CUD allocation
        Uses Markowitz optimization for risk-return tradeoff
        """
        # Calculate returns for each machine type
        returns = {}
        volatilities = {}

        for machine_type in machine_types:
            if machine_type in historical_usage.columns:
                series = historical_usage[machine_type]
                # Calculate log returns
                log_returns = np.log(series / series.shift(1)).dropna()
                returns[machine_type] = log_returns.mean() * 252  # Annualized
                volatilities[machine_type] = log_returns.std() * np.sqrt(252)

        # Create covariance matrix
        return_df = pd.DataFrame(returns, index=[0]).T
        n_assets = len(returns)

        # Optimize using Sharpe Ratio
        def negative_sharpe(weights, returns, cov_matrix, risk_free_rate):
            portfolio_return = np.sum(returns * weights)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
            return -sharpe_ratio

        # Constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1/n_assets] * n_assets)

        # Optimize
        result = optimize.minimize(
            negative_sharpe,
            initial_guess,
            args=(np.array(list(returns.values())),
                  np.eye(n_assets) * 0.1,  # Simplified covariance
                  self.risk_free_rate),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        optimal_weights = dict(zip(returns.keys(), result.x))

        return {
            'optimal_allocation': optimal_weights,
            'expected_return': np.sum(result.x * np.array(list(returns.values()))),
            'portfolio_volatility': np.sqrt(result.fun),
            'sharpe_ratio': -result.fun,
            'diversification_ratio': 1 / np.sum(result.x ** 2)  # Herfindahl index
        }

    def calculate_var_cvar(self,
                           monthly_costs: np.ndarray,
                           confidence_level: float = 0.95,
                           time_horizon: int = 12) -> Dict:
        """
        Calculate Value at Risk and Conditional Value at Risk
        Essential for understanding tail risk in cloud spending
        """
        # Fit distribution to historical costs
        mu, sigma = stats.norm.fit(monthly_costs)

        # Generate scenarios
        n_simulations = 10000
        simulated_costs = np.random.normal(mu, sigma, (n_simulations, time_horizon))
        total_costs = np.sum(simulated_costs, axis=1)

        # Calculate VaR and CVaR
        var_threshold = np.percentile(total_costs, (1 - confidence_level) * 100)
        cvar = np.mean(total_costs[total_costs >= var_threshold])

        return {
            'var_95': var_threshold,
            'cvar_95': cvar,
            'expected_cost': np.mean(total_costs),
            'cost_volatility': np.std(total_costs),
            'worst_case_scenario': np.max(total_costs),
            'best_case_scenario': np.min(total_costs),
            'probability_exceeding_budget': lambda budget: np.mean(total_costs > budget)
        }

    def black_scholes_cud_valuation(self,
                                    spot_price: float,
                                    strike_price: float,
                                    time_to_maturity: float,
                                    volatility: float,
                                    discount_rate: float) -> Dict:
        """
        Apply Black-Scholes model to value CUD as a financial option
        CUD can be viewed as a call option on compute resources
        """
        d1 = (np.log(spot_price/strike_price) +
              (self.risk_free_rate + 0.5*volatility**2)*time_to_maturity) / \
             (volatility * np.sqrt(time_to_maturity))
        d2 = d1 - volatility * np.sqrt(time_to_maturity)

        call_value = (spot_price * norm.cdf(d1) -
                     strike_price * np.exp(-self.risk_free_rate * time_to_maturity) * norm.cdf(d2))

        # Greeks for risk management
        delta = norm.cdf(d1)
        gamma = norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_maturity))
        theta = (-(spot_price * norm.pdf(d1) * volatility) / (2 * np.sqrt(time_to_maturity)) -
                self.risk_free_rate * strike_price * np.exp(-self.risk_free_rate * time_to_maturity) * norm.cdf(d2))
        vega = spot_price * norm.pdf(d1) * np.sqrt(time_to_maturity)
        rho = strike_price * time_to_maturity * np.exp(-self.risk_free_rate * time_to_maturity) * norm.cdf(d2)

        return {
            'option_value': call_value,
            'intrinsic_value': max(spot_price - strike_price, 0),
            'time_value': call_value - max(spot_price - strike_price, 0),
            'greeks': {
                'delta': delta,  # Price sensitivity
                'gamma': gamma,  # Delta sensitivity
                'theta': theta,  # Time decay
                'vega': vega,    # Volatility sensitivity
                'rho': rho       # Interest rate sensitivity
            },
            'break_even_utilization': strike_price / spot_price,
            'implied_volatility_target': volatility
        }

    def monte_carlo_simulation(self,
                              initial_cost: float,
                              drift: float,
                              volatility: float,
                              time_periods: int = 36,
                              n_simulations: int = 10000) -> Dict:
        """
        Monte Carlo simulation for cloud cost projections
        Uses Geometric Brownian Motion to model cost evolution
        """
        dt = 1/12  # Monthly time steps

        # Generate random walks
        random_shocks = np.random.normal(0, 1, (n_simulations, time_periods))

        # Initialize price paths
        price_paths = np.zeros((n_simulations, time_periods + 1))
        price_paths[:, 0] = initial_cost

        # Simulate paths using GBM
        for t in range(1, time_periods + 1):
            price_paths[:, t] = price_paths[:, t-1] * np.exp(
                (drift - 0.5 * volatility**2) * dt +
                volatility * np.sqrt(dt) * random_shocks[:, t-1]
            )

        # Calculate statistics
        final_costs = price_paths[:, -1]

        return {
            'expected_final_cost': np.mean(final_costs),
            'median_final_cost': np.median(final_costs),
            'cost_std_dev': np.std(final_costs),
            'percentile_5': np.percentile(final_costs, 5),
            'percentile_95': np.percentile(final_costs, 95),
            'probability_cost_doubles': np.mean(final_costs > 2 * initial_cost),
            'max_drawdown': np.min(np.min(price_paths, axis=1) / initial_cost - 1),
            'paths_summary': {
                'mean_path': np.mean(price_paths, axis=0),
                'upper_bound': np.percentile(price_paths, 95, axis=0),
                'lower_bound': np.percentile(price_paths, 5, axis=0)
            }
        }

    def calculate_financial_metrics(self,
                                   initial_investment: float,
                                   cash_flows: List[float],
                                   discount_rate: float = None) -> FinancialMetrics:
        """
        Calculate comprehensive financial metrics for CUD investment
        """
        if discount_rate is None:
            discount_rate = self.risk_free_rate

        # NPV calculation
        npv = npf.npv(discount_rate, [-initial_investment] + cash_flows)

        # IRR calculation
        try:
            irr = npf.irr([-initial_investment] + cash_flows)
        except:
            irr = 0

        # Payback period
        cumulative_cf = np.cumsum([-initial_investment] + cash_flows)
        payback_idx = np.where(cumulative_cf > 0)[0]
        payback_period = payback_idx[0] if len(payback_idx) > 0 else len(cash_flows)

        # ROI
        total_return = sum(cash_flows)
        roi = (total_return - initial_investment) / initial_investment

        # Break-even point
        break_even = initial_investment / np.mean(cash_flows) if np.mean(cash_flows) > 0 else float('inf')

        # Risk-adjusted return (Sharpe-like ratio)
        returns = np.array(cash_flows) / initial_investment
        risk_adjusted = (np.mean(returns) - discount_rate) / (np.std(returns) + 1e-10)

        return FinancialMetrics(
            npv=npv,
            irr=irr,
            payback_period=payback_period,
            roi=roi,
            break_even_point=break_even,
            risk_adjusted_return=risk_adjusted
        )

class CloudEconomicsModeler:
    """
    Advanced cloud economics modeling with elasticity and demand forecasting
    """

    def __init__(self):
        self.elasticity_coefficients = {}

    def calculate_price_elasticity(self,
                                  price_history: pd.Series,
                                  demand_history: pd.Series) -> float:
        """
        Calculate price elasticity of demand for cloud resources
        Essential for understanding cost optimization boundaries
        """
        # Log-log regression for elasticity
        log_price = np.log(price_history)
        log_demand = np.log(demand_history)

        # Calculate elasticity coefficient
        coef = np.polyfit(log_price, log_demand, 1)[0]

        return coef

    def forecast_demand(self,
                       historical_usage: pd.Series,
                       periods: int = 12,
                       method: str = 'holt_winters') -> Dict:
        """
        Advanced demand forecasting using time series analysis
        """
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        if method == 'holt_winters':
            # Holt-Winters exponential smoothing
            model = ExponentialSmoothing(
                historical_usage,
                seasonal_periods=12,
                trend='add',
                seasonal='add'
            )
            fit = model.fit()
            forecast = fit.forecast(periods)

            # Calculate prediction intervals
            residuals = historical_usage - fit.fittedvalues
            std_error = np.std(residuals)

            lower_bound = forecast - 1.96 * std_error
            upper_bound = forecast + 1.96 * std_error

        return {
            'forecast': forecast,
            'lower_95': lower_bound,
            'upper_95': upper_bound,
            'seasonality_strength': self._calculate_seasonality_strength(historical_usage),
            'trend_strength': self._calculate_trend_strength(historical_usage)
        }

    def _calculate_seasonality_strength(self, series: pd.Series) -> float:
        """Calculate strength of seasonal pattern"""
        if len(series) < 24:
            return 0

        # Decompose series
        seasonal = np.array([series[i::12].mean() for i in range(12)])
        seasonal = np.tile(seasonal, len(series)//12 + 1)[:len(series)]

        # Calculate R-squared
        ss_res = np.sum((series - seasonal)**2)
        ss_tot = np.sum((series - series.mean())**2)

        return 1 - (ss_res/ss_tot) if ss_tot > 0 else 0

    def _calculate_trend_strength(self, series: pd.Series) -> float:
        """Calculate strength of trend"""
        x = np.arange(len(series))
        coef = np.polyfit(x, series, 1)
        trend = np.polyval(coef, x)

        ss_res = np.sum((series - trend)**2)
        ss_tot = np.sum((series - series.mean())**2)

        return 1 - (ss_res/ss_tot) if ss_tot > 0 else 0

    def calculate_optimal_commitment_ladder(self,
                                           forecast: Dict,
                                           risk_tolerance: float = 0.5) -> Dict:
        """
        Design optimal CUD commitment ladder strategy
        Balances risk and return across multiple time horizons
        """
        base_demand = forecast['forecast'].mean()
        volatility = forecast['forecast'].std()

        # Calculate commitment levels based on confidence intervals
        high_confidence_level = base_demand - 2 * volatility  # 95% confidence
        medium_confidence_level = base_demand - volatility    # 68% confidence
        low_confidence_level = base_demand                    # 50% confidence

        # Optimal ladder based on risk tolerance
        if risk_tolerance < 0.3:  # Conservative
            ladder = {
                '3_year_commitment': high_confidence_level * 0.5,
                '1_year_commitment': high_confidence_level * 0.3,
                'flex_commitment': high_confidence_level * 0.2,
                'on_demand_buffer': base_demand - high_confidence_level
            }
        elif risk_tolerance < 0.7:  # Moderate
            ladder = {
                '3_year_commitment': medium_confidence_level * 0.6,
                '1_year_commitment': medium_confidence_level * 0.25,
                'flex_commitment': medium_confidence_level * 0.15,
                'on_demand_buffer': base_demand - medium_confidence_level
            }
        else:  # Aggressive
            ladder = {
                '3_year_commitment': low_confidence_level * 0.7,
                '1_year_commitment': low_confidence_level * 0.2,
                'flex_commitment': low_confidence_level * 0.1,
                'on_demand_buffer': base_demand * 0.1
            }

        # Calculate expected savings
        savings_3yr = ladder['3_year_commitment'] * 0.55  # 55% discount
        savings_1yr = ladder['1_year_commitment'] * 0.37   # 37% discount
        savings_flex = ladder['flex_commitment'] * 0.28    # 28% discount

        total_savings = savings_3yr + savings_1yr + savings_flex
        effective_discount = total_savings / base_demand if base_demand > 0 else 0

        return {
            'ladder_strategy': ladder,
            'expected_monthly_savings': total_savings,
            'effective_discount_rate': effective_discount,
            'risk_coverage': sum(ladder.values()) / base_demand,
            'flexibility_ratio': (ladder['flex_commitment'] + ladder['on_demand_buffer']) / base_demand
        }

class QuantitativeRiskAnalyzer:
    """
    Sophisticated risk analysis using quantitative methods
    """

    def __init__(self):
        self.risk_metrics = {}

    def calculate_commitment_risk_score(self,
                                       commitment_amount: float,
                                       historical_usage: pd.Series,
                                       commitment_period: int) -> Dict:
        """
        Calculate comprehensive risk score for CUD commitment
        """
        # Calculate usage statistics
        mean_usage = historical_usage.mean()
        std_usage = historical_usage.std()
        cv = std_usage / mean_usage if mean_usage > 0 else float('inf')

        # Calculate downside risk
        downside_deviations = historical_usage[historical_usage < commitment_amount]
        if len(downside_deviations) > 0:
            downside_risk = np.mean((commitment_amount - downside_deviations) / commitment_amount)
        else:
            downside_risk = 0

        # Calculate probability of underutilization
        if std_usage > 0:
            z_score = (commitment_amount - mean_usage) / std_usage
            prob_underutilization = norm.cdf(z_score)
        else:
            prob_underutilization = 0.5

        # Calculate maximum drawdown risk
        cumsum = historical_usage.cumsum()
        running_max = cumsum.cummax()
        drawdown = (cumsum - running_max) / running_max
        max_drawdown = drawdown.min()

        # Composite risk score (0-100, higher is riskier)
        risk_score = (
            cv * 20 +                           # Coefficient of variation weight
            downside_risk * 30 +                # Downside risk weight
            prob_underutilization * 30 +        # Underutilization probability weight
            abs(max_drawdown) * 20              # Drawdown weight
        ) * 100

        # Risk category
        if risk_score < 30:
            risk_category = "LOW"
            recommendation = "Safe for long-term commitment"
        elif risk_score < 60:
            risk_category = "MEDIUM"
            recommendation = "Consider mixed commitment strategy"
        else:
            risk_category = "HIGH"
            recommendation = "Prefer flexible or short-term commitments"

        return {
            'risk_score': min(risk_score, 100),
            'risk_category': risk_category,
            'recommendation': recommendation,
            'metrics': {
                'coefficient_of_variation': cv,
                'downside_risk': downside_risk,
                'underutilization_probability': prob_underutilization,
                'max_drawdown': max_drawdown,
                'volatility': std_usage,
                'commitment_coverage': commitment_amount / mean_usage if mean_usage > 0 else 0
            }
        }

    def stress_test_scenarios(self,
                            base_cost: float,
                            commitment_level: float) -> Dict:
        """
        Run stress test scenarios for risk assessment
        """
        scenarios = {
            'baseline': {
                'usage_change': 0,
                'cost_impact': 0
            },
            'mild_recession': {
                'usage_change': -0.20,
                'cost_impact': (base_cost * 0.8 - commitment_level) if base_cost * 0.8 < commitment_level else 0
            },
            'severe_recession': {
                'usage_change': -0.40,
                'cost_impact': (base_cost * 0.6 - commitment_level) if base_cost * 0.6 < commitment_level else 0
            },
            'rapid_growth': {
                'usage_change': 0.50,
                'cost_impact': base_cost * 0.5 * 0.3  # Additional on-demand premium
            },
            'technology_shift': {
                'usage_change': -0.30,
                'cost_impact': (base_cost * 0.7 - commitment_level) if base_cost * 0.7 < commitment_level else 0
            }
        }

        # Calculate weighted risk
        weights = {'baseline': 0.4, 'mild_recession': 0.25, 'severe_recession': 0.1,
                  'rapid_growth': 0.15, 'technology_shift': 0.1}

        weighted_impact = sum(scenarios[s]['cost_impact'] * weights[s] for s in scenarios)

        return {
            'scenarios': scenarios,
            'weighted_risk_impact': weighted_impact,
            'worst_case_impact': max(s['cost_impact'] for s in scenarios.values()),
            'risk_adjusted_commitment': commitment_level * (1 - weighted_impact/base_cost) if base_cost > 0 else commitment_level
        }

# Integration function to add to main analysis
def enhance_with_advanced_analytics(analysis_results: Dict,
                                   billing_data: pd.DataFrame = None) -> Dict:
    """
    Enhance existing analysis with advanced quantitative methods
    """
    optimizer = AdvancedCUDOptimizer()
    modeler = CloudEconomicsModeler()
    risk_analyzer = QuantitativeRiskAnalyzer()

    # Extract relevant data
    total_spend = sum(analysis_results.get('machine_spend_distribution', {}).values())

    # Create synthetic historical data if not provided
    if billing_data is None or len(billing_data) == 0:
        np.random.seed(42)
        historical_usage = pd.Series(
            np.random.normal(total_spend/len(analysis_results.get('machine_spend_distribution', {'default': 1})),
                           total_spend * 0.1, 36)
        )
    else:
        historical_usage = billing_data.groupby(pd.Grouper(freq='M'))['Cost'].sum()

    # Advanced portfolio optimization
    if len(analysis_results.get('machine_spend_distribution', {})) > 1:
        portfolio = optimizer.calculate_optimal_portfolio(
            analysis_results['machine_spend_distribution'],
            pd.DataFrame({k: [v] * 12 for k, v in analysis_results['machine_spend_distribution'].items()})
        )
    else:
        portfolio = {'optimal_allocation': {}, 'sharpe_ratio': 0}

    # Risk analysis
    var_cvar = optimizer.calculate_var_cvar(historical_usage.values)

    # Monte Carlo simulation
    monte_carlo = optimizer.monte_carlo_simulation(
        initial_cost=total_spend,
        drift=0.05,  # 5% annual growth
        volatility=0.20  # 20% volatility
    )

    # Demand forecasting
    if len(historical_usage) >= 12:
        forecast = modeler.forecast_demand(historical_usage)
        commitment_ladder = modeler.calculate_optimal_commitment_ladder(forecast)
    else:
        forecast = {'forecast': pd.Series([total_spend] * 12)}
        commitment_ladder = {'ladder_strategy': {}, 'expected_monthly_savings': 0}

    # Black-Scholes valuation
    bs_valuation = optimizer.black_scholes_cud_valuation(
        spot_price=total_spend,
        strike_price=total_spend * 0.7,  # 30% discount
        time_to_maturity=3,  # 3 years
        volatility=0.20,
        discount_rate=0.37
    )

    # Financial metrics
    cash_flows = [analysis_results['total_savings_summary']['optimal_mix']] * 36
    financial_metrics = optimizer.calculate_financial_metrics(
        initial_investment=total_spend * 0.7,  # Committed amount
        cash_flows=cash_flows
    )

    # Risk scoring
    risk_score = risk_analyzer.calculate_commitment_risk_score(
        commitment_amount=total_spend * 0.7,
        historical_usage=historical_usage,
        commitment_period=36
    )

    # Stress testing
    stress_test = risk_analyzer.stress_test_scenarios(
        base_cost=total_spend,
        commitment_level=total_spend * 0.7
    )

    # Combine with original analysis
    enhanced_analysis = analysis_results.copy()
    enhanced_analysis['advanced_analytics'] = {
        'portfolio_optimization': portfolio,
        'risk_metrics': {
            'var_95': var_cvar['var_95'],
            'cvar_95': var_cvar['cvar_95'],
            'risk_score': risk_score['risk_score'],
            'risk_category': risk_score['risk_category']
        },
        'monte_carlo_projection': {
            'expected_cost_3yr': monte_carlo['expected_final_cost'],
            'cost_range_95': (monte_carlo['percentile_5'], monte_carlo['percentile_95']),
            'probability_cost_doubles': monte_carlo['probability_cost_doubles']
        },
        'commitment_ladder': commitment_ladder,
        'financial_metrics': {
            'npv': financial_metrics.npv,
            'irr': financial_metrics.irr,
            'payback_period': financial_metrics.payback_period,
            'roi': financial_metrics.roi
        },
        'option_valuation': {
            'cud_option_value': bs_valuation['option_value'],
            'break_even_utilization': bs_valuation['break_even_utilization'],
            'greeks': bs_valuation['greeks']
        },
        'stress_test_results': stress_test
    }

    return enhanced_analysis

if __name__ == "__main__":
    # Example usage
    print("Advanced FinOps Analytics Module Loaded")
    print("=" * 60)
    print("Available Classes:")
    print("  • AdvancedCUDOptimizer - Portfolio optimization & option pricing")
    print("  • CloudEconomicsModeler - Demand forecasting & elasticity")
    print("  • QuantitativeRiskAnalyzer - Risk scoring & stress testing")
    print("=" * 60)
