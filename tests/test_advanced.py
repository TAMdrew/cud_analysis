#!/usr/bin/env python3
"""
Test Suite for Advanced FinOps Analytics
Validates quantitative models and financial calculations
Author: andrewanolasco@
Version: V1.0.0
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import warnings

warnings.filterwarnings('ignore')

# Import the modules to test
from finops_analysis_platform.advanced import (
    AdvancedCUDOptimizer,
    CloudEconomicsModeler,
    QuantitativeRiskAnalyzer,
    enhance_with_advanced_analytics
)

class TestAdvancedCUDOptimizer(unittest.TestCase):
    """Test suite for Advanced CUD Optimizer"""

    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = AdvancedCUDOptimizer(risk_free_rate=0.03)

        # Create sample data
        np.random.seed(42)
        self.monthly_costs = np.random.normal(100000, 10000, 36)

        # Create sample machine type data
        self.machine_types = {
            'n2': 50000,
            'e2': 30000,
            'c2': 20000
        }

        # Create historical usage DataFrame
        dates = pd.date_range(start='2023-01-01', periods=36, freq='M')
        self.historical_usage = pd.DataFrame({
            'n2': np.random.normal(50000, 5000, 36),
            'e2': np.random.normal(30000, 3000, 36),
            'c2': np.random.normal(20000, 2000, 36)
        }, index=dates)

    def test_portfolio_optimization(self):
        """Test portfolio optimization calculations"""
        result = self.optimizer.calculate_optimal_portfolio(
            self.machine_types,
            self.historical_usage
        )

        # Check that results contain expected keys
        self.assertIn('optimal_allocation', result)
        self.assertIn('sharpe_ratio', result)
        self.assertIn('expected_return', result)

        # Check that allocations sum to 1
        total_allocation = sum(result['optimal_allocation'].values())
        self.assertAlmostEqual(total_allocation, 1.0, places=5)

        # Check that all allocations are non-negative
        for allocation in result['optimal_allocation'].values():
            self.assertGreaterEqual(allocation, 0)

    def test_var_cvar_calculation(self):
        """Test Value at Risk and Conditional Value at Risk"""
        result = self.optimizer.calculate_var_cvar(
            self.monthly_costs,
            confidence_level=0.95,
            time_horizon=12
        )

        # Check that VaR is less than CVaR (tail risk)
        self.assertLess(result['var_95'], result['cvar_95'])

        # Check that expected cost is reasonable
        self.assertGreater(result['expected_cost'], 0)

        # Check volatility is positive
        self.assertGreater(result['cost_volatility'], 0)

    def test_black_scholes_valuation(self):
        """Test Black-Scholes option pricing for CUDs"""
        result = self.optimizer.black_scholes_cud_valuation(
            spot_price=100000,
            strike_price=70000,
            time_to_maturity=3,
            volatility=0.20,
            discount_rate=0.37
        )

        # Check option value is positive
        self.assertGreater(result['option_value'], 0)

        # Check Greeks are calculated
        self.assertIn('delta', result['greeks'])
        self.assertIn('gamma', result['greeks'])
        self.assertIn('theta', result['greeks'])
        self.assertIn('vega', result['greeks'])

        # Delta should be between 0 and 1
        self.assertGreaterEqual(result['greeks']['delta'], 0)
        self.assertLessEqual(result['greeks']['delta'], 1)

    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation for cost projections"""
        result = self.optimizer.monte_carlo_simulation(
            initial_cost=100000,
            drift=0.05,
            volatility=0.20,
            time_periods=36,
            n_simulations=1000
        )

        # Check that results are reasonable
        self.assertGreater(result['expected_final_cost'], 0)
        self.assertGreater(result['median_final_cost'], 0)

        # Check percentiles are ordered correctly
        self.assertLess(result['percentile_5'], result['percentile_95'])

        # Check probability is between 0 and 1
        self.assertGreaterEqual(result['probability_cost_doubles'], 0)
        self.assertLessEqual(result['probability_cost_doubles'], 1)

class TestCloudEconomicsModeler(unittest.TestCase):
    """Test suite for Cloud Economics Modeler"""

    def setUp(self):
        """Set up test fixtures"""
        self.modeler = CloudEconomicsModeler()

        # Create sample time series data
        np.random.seed(42)
        dates = pd.date_range(start='2022-01-01', periods=36, freq='M')
        trend = np.linspace(80000, 120000, 36)
        seasonal = 10000 * np.sin(np.arange(36) * 2 * np.pi / 12)
        noise = np.random.normal(0, 5000, 36)

        self.historical_usage = pd.Series(
            trend + seasonal + noise,
            index=dates
        )

    def test_price_elasticity(self):
        """Test price elasticity calculation"""
        # Create price and demand series
        prices = pd.Series(np.linspace(0.10, 0.15, 36))
        demand = pd.Series(np.linspace(100000, 80000, 36))

        elasticity = self.modeler.calculate_price_elasticity(prices, demand)

        # Elasticity should be negative (inverse relationship)
        self.assertLess(elasticity, 0)

    def test_commitment_ladder(self):
        """Test optimal commitment ladder strategy"""
        forecast = {
            'forecast': pd.Series(np.random.normal(100000, 10000, 12))
        }

        # Test conservative strategy
        result_conservative = self.modeler.calculate_optimal_commitment_ladder(
            forecast,
            risk_tolerance=0.2
        )

        # Test aggressive strategy
        result_aggressive = self.modeler.calculate_optimal_commitment_ladder(
            forecast,
            risk_tolerance=0.8
        )

        # Conservative should have more buffer
        self.assertGreater(
            result_conservative['ladder_strategy'].get('on_demand_buffer', 0),
            result_aggressive['ladder_strategy'].get('on_demand_buffer', 0)
        )

        # Both should have positive expected savings
        self.assertGreaterEqual(result_conservative['expected_monthly_savings'], 0)
        self.assertGreaterEqual(result_aggressive['expected_monthly_savings'], 0)

class TestQuantitativeRiskAnalyzer(unittest.TestCase):
    """Test suite for Quantitative Risk Analyzer"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = QuantitativeRiskAnalyzer()

        # Create sample usage data
        np.random.seed(42)
        self.historical_usage = pd.Series(
            np.random.normal(100000, 20000, 36)
        )

    def test_commitment_risk_score(self):
        """Test risk score calculation"""
        result = self.analyzer.calculate_commitment_risk_score(
            commitment_amount=80000,
            historical_usage=self.historical_usage,
            commitment_period=36
        )

        # Check risk score is between 0 and 100
        self.assertGreaterEqual(result['risk_score'], 0)
        self.assertLessEqual(result['risk_score'], 100)

        # Check risk category is valid
        self.assertIn(result['risk_category'], ['LOW', 'MEDIUM', 'HIGH'])

        # Check metrics are calculated
        self.assertIn('coefficient_of_variation', result['metrics'])
        self.assertIn('downside_risk', result['metrics'])
        self.assertIn('underutilization_probability', result['metrics'])

    def test_stress_test_scenarios(self):
        """Test stress testing scenarios"""
        result = self.analyzer.stress_test_scenarios(
            base_cost=100000,
            commitment_level=70000
        )

        # Check that scenarios are included
        self.assertIn('scenarios', result)
        self.assertIn('baseline', result['scenarios'])
        self.assertIn('mild_recession', result['scenarios'])
        self.assertIn('severe_recession', result['scenarios'])

        # Check weighted impact is calculated
        self.assertIn('weighted_risk_impact', result)

        # Baseline should have zero impact
        self.assertEqual(result['scenarios']['baseline']['cost_impact'], 0)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""

    def test_enhance_with_advanced_analytics(self):
        """Test the integration function"""
        # Create sample analysis results
        analysis_results = {
            'machine_spend_distribution': {
                'n2': 50000,
                'e2': 30000,
                'c2': 20000
            },
            'total_savings_summary': {
                'optimal_mix': 25000
            }
        }

        # Create sample billing data
        billing_data = pd.DataFrame({
            'Cost': np.random.normal(100000, 10000, 36),
            'Date': pd.date_range(start='2023-01-01', periods=36, freq='M')
        }).set_index('Date')

        # Enhance with advanced analytics
        enhanced = enhance_with_advanced_analytics(
            analysis_results,
            billing_data
        )

        # Check that advanced analytics are added
        self.assertIn('advanced_analytics', enhanced)

        # Check key components are present
        adv = enhanced['advanced_analytics']
        self.assertIn('portfolio_optimization', adv)
        self.assertIn('risk_metrics', adv)
        self.assertIn('monte_carlo_projection', adv)
        self.assertIn('financial_metrics', adv)
        self.assertIn('option_valuation', adv)
        self.assertIn('stress_test_results', adv)

class TestFinancialCalculations(unittest.TestCase):
    """Test financial calculations accuracy"""

    def test_npv_calculation(self):
        """Test NPV calculation accuracy"""
        optimizer = AdvancedCUDOptimizer(risk_free_rate=0.05)

        # Known NPV calculation
        initial_investment = 100000
        cash_flows = [30000] * 5  # 5 years of 30k returns

        metrics = optimizer.calculate_financial_metrics(
            initial_investment=initial_investment,
            cash_flows=cash_flows,
            discount_rate=0.05
        )

        # Manual NPV calculation for verification
        expected_npv = -initial_investment
        for i, cf in enumerate(cash_flows):
            expected_npv += cf / (1.05 ** (i + 1))

        self.assertAlmostEqual(metrics.npv, expected_npv, places=2)

    def test_irr_calculation(self):
        """Test IRR calculation"""
        optimizer = AdvancedCUDOptimizer()

        # Known IRR scenario
        initial_investment = 100000
        cash_flows = [40000] * 3  # Should give positive IRR

        metrics = optimizer.calculate_financial_metrics(
            initial_investment=initial_investment,
            cash_flows=cash_flows
        )

        # IRR should be positive for this scenario
        self.assertGreater(metrics.irr, 0)

        # IRR should be reasonable (not infinite)
        self.assertLess(metrics.irr, 1.0)  # Less than 100%

def run_tests():
    """Run all tests and generate report"""
    print("="*60)
    print("ADVANCED FINOPS ANALYTICS TEST SUITE")
    print("="*60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedCUDOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestCloudEconomicsModeler))
    suite.addTests(loader.loadTestsFromTestCase(TestQuantitativeRiskAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestFinancialCalculations))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")

        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split(chr(10))[0]}")

        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split(chr(10))[0]}")

    print("="*60)

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
