"""
Core analysis engine for the FinOps CUD Analysis Platform.
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

import numpy as np
import pandas as pd
import yaml

from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class MachineTypeDiscountMapping:
    """
    Manages the mapping of all GCP machine types to their respective discount rates.
    This class loads its data from a YAML configuration file.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initializes the discount mapping.

        Args:
            config_path: The path to the machine discounts YAML file. If not provided,
                         it defaults to 'config/machine_discounts.yaml' inside the package.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "machine_discounts.yaml"
        self._load_discounts_from_yaml(config_path)

    def _load_discounts_from_yaml(self, path: Path):
        """Loads discount rates and machine families from a YAML file."""
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                self.discounts = data.get('discounts', {})
                self.families = data.get('families', {})
                logger.info(f"Loaded {len(self.discounts)} machine types from {path}")
        except FileNotFoundError:
            logger.error(f"Discount configuration file not found at {path}")
            self.discounts, self.families = {}, {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {path}: {e}")
            self.discounts, self.families = {}, {}

    def get_discount(self, machine_type: str, discount_type: str) -> Optional[float]:
        """
        Retrieves the discount rate for a specific machine type and discount type.

        Args:
            machine_type: The name of the machine type (e.g., 'n2-standard-8').
            discount_type: The type of discount (e.g., '1yr_resource', '3yr_flex').

        Returns:
            The discount rate as a float, or None if not found.
        """
        machine_base = self._extract_machine_base(machine_type)
        return self.discounts.get(machine_base, {}).get(discount_type)

    def _extract_machine_base(self, machine_type: str) -> str:
        """
        Extracts the base machine type from a full instance name (e.g., 'n2-standard-8' -> 'n2').
        This is used to group similar machines for discount purposes.
        """
        machine_type = machine_type.lower()

        # Priority prefixes for major families
        prefixes = [
            'n1', 'n2d', 'n2', 'n4', 'e2', 't2d', 't2a', 'c2d', 'c3d', 'c4a',
            'c2', 'c3', 'c4', 'm1', 'm2', 'm3', 'm4', 'z3', 'a2', 'a3', 'g2', 'h3'
        ]

        for prefix in prefixes:
            if machine_type.startswith(prefix):
                return prefix

        # Handle GPUs and other special cases
        if 'gpu' in machine_type or any(gpu in machine_type for gpu in ['l4', 't4', 'a100']):
            return 'gpu' # Simplified GPU category
        if 'gcve' in machine_type:
            return 'gcve'
        if 'ssd' in machine_type:
            return 'local-ssd'

        logger.debug(f"Could not determine base type for '{machine_type}', defaulting to 'n2'.")
        return 'n2' # Default fallback

    def get_family(self, machine_type: str) -> str:
        """Retrieves the family (e.g., 'General Purpose') for a machine type."""
        machine_base = self._extract_machine_base(machine_type)
        for family, types in self.families.items():
            if machine_base in types:
                return family
        return 'General Purpose' # Default fallback


class CUDAnalyzer:
    """
    Core engine for performing Committed Use Discount (CUD) analysis.
    This class takes billing data and a configuration manager to produce
    a comprehensive analysis of CUD savings opportunities and risks.
    """

    def __init__(self, config_manager: ConfigManager, billing_data: Optional[pd.DataFrame] = None):
        """
        Initializes the CUDAnalyzer.

        Args:
            config_manager: An instance of ConfigManager for accessing configuration.
            billing_data: A pandas DataFrame containing billing data. If not provided,
                          the analyzer will rely on sample data.
        """
        self.config_manager = config_manager
        self.discount_mapping = MachineTypeDiscountMapping()
        self.billing_data = self._validate_billing_data(billing_data)
        self.analysis_results: Dict[str, Any] = {}

    def _validate_billing_data(self, df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
        """Validates the input billing data DataFrame."""
        if df is None or df.empty:
            logger.warning("Billing data is empty. Analysis will rely on sample data.")
            return None

        required_cols = ['Cost']
        sku_cols = ['SKU', 'Sku Description']

        if not any(col in df.columns for col in sku_cols):
            logger.error(f"Billing data must contain one of {sku_cols}.")
            return None

        if not all(col in df.columns for col in required_cols):
            logger.error(f"Billing data must contain all of the following columns: {required_cols}.")
            return None

        logger.info("Billing data validation successful.")
        return df

    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Runs the full suite of CUD analysis.

        Returns:
            A dictionary containing all analysis results.
        """
        logger.info("Starting comprehensive CUD analysis...")

        machine_distribution = self._analyze_machine_distribution()
        savings_by_machine = self._calculate_savings_by_machine(machine_distribution)
        portfolio = self._generate_portfolio_recommendation(savings_by_machine)
        total_savings = self._calculate_total_savings(savings_by_machine)
        risk_assessment = self._assess_risk(savings_by_machine)

        self.analysis_results = {
            'machine_spend_distribution': machine_distribution,
            'savings_by_machine': savings_by_machine,
            'portfolio_recommendation': portfolio,
            'total_savings_summary': total_savings,
            'risk_assessment': risk_assessment,
            'analysis_date': datetime.now(),
            'config': self.config_manager.get('analysis', {})
        }
        logger.info("Comprehensive CUD analysis complete.")
        return self.analysis_results

    def _analyze_machine_distribution(self) -> Dict[str, float]:
        """Analyzes and returns the spend distribution by machine type."""
        if self.billing_data is None:
            from .data_loader import generate_sample_spend_distribution
            logger.warning("No billing data provided, using sample spend distribution.")
            return generate_sample_spend_distribution()

        sku_col = 'SKU' if 'SKU' in self.billing_data.columns else 'Sku Description'

        # Ensure cost column is numeric
        self.billing_data['Cost'] = pd.to_numeric(self.billing_data['Cost'], errors='coerce')

        grouped = self.billing_data.groupby(sku_col)['Cost'].sum()

        distribution: Dict[str, float] = {}
        for machine_type, cost in grouped.items():
            base_type = self.discount_mapping._extract_machine_base(str(machine_type))
            distribution.setdefault(base_type, 0)
            distribution[base_type] += cost

        return distribution

    def _calculate_savings_by_machine(self, distribution: Dict[str, float]) -> Dict[str, Any]:
        """Calculates potential savings for each machine type."""
        savings = {}
        strategy_config = self.config_manager.get('cud_strategy', {})
        stable_coverage = strategy_config.get('base_layer_coverage', 40) / 100.0

        for machine_type, monthly_spend in distribution.items():
            stable_workload = monthly_spend * stable_coverage
            discounts = {
                '1yr_resource': self.discount_mapping.get_discount(machine_type, '1yr_resource') or 0,
                '3yr_resource': self.discount_mapping.get_discount(machine_type, '3yr_resource') or 0,
                '1yr_flex': self.discount_mapping.get_discount(machine_type, '1yr_flex') or 0,
                '3yr_flex': self.discount_mapping.get_discount(machine_type, '3yr_flex') or 0,
            }

            savings[machine_type] = {
                'family': self.discount_mapping.get_family(machine_type),
                'monthly_spend': monthly_spend,
                'stable_workload': stable_workload,
                'savings_options': {
                    key: {'discount': value, 'monthly_savings': stable_workload * value}
                    for key, value in discounts.items()
                },
                'recommendation': self._get_recommendation(discounts)
            }
        return savings

    def _get_recommendation(self, discounts: Dict[str, float]) -> str:
        """Determines the best CUD strategy based on available discounts."""
        if discounts['3yr_resource'] >= 0.65:
            return "3-Year Resource CUD (Highest Savings)"
        if discounts['1yr_resource'] >= 0.45:
            return "1-Year Resource CUD (Good Savings, Less Commitment)"
        if discounts['3yr_flex'] > 0:
            return "3-Year Flex CUD (Good Flexibility)"
        return "1-Year Flex CUD (Maximum Flexibility)"

    def _generate_portfolio_recommendation(self, savings_by_machine: Dict) -> Dict[str, Any]:
        """Generates an optimal portfolio recommendation based on savings."""
        layers = []
        for machine_type, savings in savings_by_machine.items():
            options = savings['savings_options']
            best_option = max(options, key=lambda k: options[k]['monthly_savings'])

            if options[best_option]['monthly_savings'] > 0:
                layers.append({
                    'machine_type': machine_type,
                    'strategy': best_option,
                    'monthly_spend': savings['stable_workload'],
                    'monthly_savings': options[best_option]['monthly_savings']
                })

        total_savings = sum(layer['monthly_savings'] for layer in layers)
        total_spend = sum(s['monthly_spend'] for s in savings_by_machine.values())

        return {
            'layers': sorted(layers, key=lambda x: x['monthly_savings'], reverse=True),
            'total_monthly_savings': total_savings,
            'total_annual_savings': total_savings * 12,
            'coverage_percentage': (total_savings / total_spend * 100) if total_spend > 0 else 0
        }

    def _calculate_total_savings(self, savings_by_machine: Dict) -> Dict[str, float]:
        """Calculates the total savings across all strategies."""
        totals: Dict[str, float] = {
            '1yr_resource': 0, '3yr_resource': 0,
            '1yr_flex': 0, '3yr_flex': 0, 'optimal_mix': 0
        }
        for savings in savings_by_machine.values():
            options = savings['savings_options']
            for key, value in options.items():
                totals[key] += value['monthly_savings']
            totals['optimal_mix'] += max(opt['monthly_savings'] for opt in options.values())
        return totals

    def _assess_risk(self, savings_by_machine: Dict) -> Dict[str, Any]:
        """Assesses risk levels for CUD commitments."""
        # Simplified risk assessment logic. In a real-world scenario, this would be more complex.
        risk_levels = {'low': 0, 'medium': 0, 'high': 0}
        for machine_type, savings in savings_by_machine.items():
            if 'm' in machine_type or 'c' in machine_type: # Memory/Compute optimized are often stable
                risk_levels['low'] += savings['monthly_spend']
            elif 'gpu' in machine_type or 'a2' in machine_type: # Specialized hardware is higher risk
                risk_levels['high'] += savings['monthly_spend']
            else:
                risk_levels['medium'] += savings['monthly_spend']

        total_spend = sum(risk_levels.values())
        if total_spend == 0:
            return {'overall_risk': 'UNKNOWN', 'recommendation': 'No data to assess.'}

        high_risk_pct = risk_levels['high'] / total_spend
        if high_risk_pct > 0.3:
            overall_risk, recommendation = 'HIGH', "High exposure to specialized hardware. Favor Flex CUDs."
        elif high_risk_pct > 0.1:
            overall_risk, recommendation = 'MEDIUM', "Balanced portfolio. Mix of Resource and Flex CUDs is ideal."
        else:
            overall_risk, recommendation = 'LOW', "Low-risk portfolio. Good candidate for 3-year Resource CUDs."

        return {'overall_risk': overall_risk, 'recommendation': recommendation, 'risk_distribution': risk_levels}
