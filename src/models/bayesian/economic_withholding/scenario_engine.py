"""
Scenario Simulation Engine for Economic Withholding Detection.

This module implements ARERA-style counterfactual "what-if" simulation
for detecting economic withholding in power markets by constructing
efficient offer curves based on declared costs and comparing against actual offers.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ScenarioSimulationEngine:
    """
    Counterfactual simulation engine for economic withholding detection.
    
    Implements ARERA-style "what-if" analysis by constructing efficient
    offer curves based on declared costs and comparing against actual offers.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the scenario simulation engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.monte_carlo_iterations = self.config.get('monte_carlo_iterations', 1000)
        self.confidence_intervals = self.config.get('confidence_intervals', [0.90, 0.95, 0.99])
        self.benchmark_scenarios = self.config.get('benchmark_scenarios', ['min_cost', 'median_cost', 'max_cost'])
        
        logger.info("Scenario simulation engine initialized")

    def generate_benchmark_offers(
        self, 
        plant_characteristics: Dict[str, Any],
        market_conditions: Dict[str, Any],
        fuel_prices: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Generate range of benchmark cost-based offers using ARERA methodology.
        
        Args:
            plant_characteristics: Plant technical and cost data
            market_conditions: Market context (load, constraints, etc.)
            fuel_prices: Current fuel price data
            
        Returns:
            List of benchmark offer scenarios
        """
        try:
            benchmark_offers = []
            
            # Extract plant data
            unit_id = plant_characteristics.get('unit_id')
            fuel_type = plant_characteristics.get('fuel_type', 'gas')
            capacity_mw = plant_characteristics.get('capacity_mw', 0)
            heat_rate = plant_characteristics.get('heat_rate', 7500)  # BTU/kWh
            efficiency = plant_characteristics.get('efficiency', 0.45)
            
            # Get variable costs
            variable_costs = plant_characteristics.get('variable_costs', {})
            fuel_cost = fuel_prices.get(fuel_type, 50.0)  # $/MMBtu
            vom_cost = variable_costs.get('vom_cost', 3.5)  # $/MWh
            emission_cost = variable_costs.get('emission_cost', 1.2)  # $/MWh
            
            # Calculate base marginal cost
            base_marginal_cost = self._calculate_marginal_cost(
                fuel_cost, heat_rate, efficiency, vom_cost, emission_cost
            )
            
            # Generate benchmark scenarios
            for scenario in self.benchmark_scenarios:
                if scenario == 'min_cost':
                    # Optimistic cost scenario (best efficiency, lowest costs)
                    scenario_marginal_cost = base_marginal_cost * 0.95
                    scenario_description = "Minimum cost scenario"
                    
                elif scenario == 'median_cost':
                    # Expected cost scenario
                    scenario_marginal_cost = base_marginal_cost
                    scenario_description = "Expected cost scenario"
                    
                elif scenario == 'max_cost':
                    # Conservative cost scenario (account for uncertainties)
                    scenario_marginal_cost = base_marginal_cost * 1.10
                    scenario_description = "Maximum cost scenario"
                
                # Generate offer curve for this scenario
                offer_curve = self._generate_cost_based_offer_curve(
                    scenario_marginal_cost, capacity_mw, market_conditions
                )
                
                benchmark_offers.append({
                    'scenario': scenario,
                    'description': scenario_description,
                    'unit_id': unit_id,
                    'marginal_cost': scenario_marginal_cost,
                    'offer_curve': offer_curve,
                    'total_capacity': capacity_mw,
                    'fuel_type': fuel_type,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            logger.info(f"Generated {len(benchmark_offers)} benchmark scenarios for unit {unit_id}")
            return benchmark_offers
            
        except Exception as e:
            logger.error(f"Error generating benchmark offers: {str(e)}")
            return []

    def _calculate_marginal_cost(
        self, 
        fuel_cost: float, 
        heat_rate: float, 
        efficiency: float,
        vom_cost: float, 
        emission_cost: float
    ) -> float:
        """
        Calculate marginal cost based on plant characteristics.
        
        Args:
            fuel_cost: Fuel cost in $/MMBtu
            heat_rate: Plant heat rate in BTU/kWh
            efficiency: Plant efficiency (0-1)
            vom_cost: Variable O&M cost in $/MWh
            emission_cost: Emission cost in $/MWh
            
        Returns:
            Marginal cost in $/MWh
        """
        # Convert fuel cost to $/MWh
        # Heat rate (BTU/kWh) * Fuel cost ($/MMBtu) / 1000 (BTU/MMBtu conversion)
        fuel_cost_per_mwh = (heat_rate * fuel_cost) / 1000
        
        # Adjust for efficiency
        adjusted_fuel_cost = fuel_cost_per_mwh / efficiency
        
        # Total marginal cost
        marginal_cost = adjusted_fuel_cost + vom_cost + emission_cost
        
        return marginal_cost

    def _generate_cost_based_offer_curve(
        self,
        marginal_cost: float,
        capacity_mw: float,
        market_conditions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate cost-based offer curve.
        
        Args:
            marginal_cost: Marginal cost in $/MWh
            capacity_mw: Plant capacity in MW
            market_conditions: Market context
            
        Returns:
            List of price-quantity offer pairs
        """
        offer_curve = []
        
        # Get market conditions
        load_factor = market_conditions.get('load_factor', 'normal_demand')
        market_tightness = market_conditions.get('market_tightness', 'balanced')
        
        # Determine offer strategy based on market conditions
        if load_factor == 'peak_demand' and market_tightness == 'tight':
            # Allow small markup during peak/tight conditions
            price_multiplier = 1.05
        elif load_factor == 'low_demand' and market_tightness == 'surplus':
            # Competitive pricing during low demand
            price_multiplier = 1.0
        else:
            # Normal conditions
            price_multiplier = 1.02
        
        # Generate stepped offer curve
        step_size = capacity_mw / 4  # 4 steps
        
        for i in range(4):
            quantity = step_size * (i + 1)
            # Slightly increasing price for higher quantities (startup costs, etc.)
            price = marginal_cost * price_multiplier * (1 + i * 0.01)
            
            offer_curve.append({
                'price_eur_mwh': round(price, 2),
                'quantity_mw': round(quantity, 1),
                'marginal_cost_basis': round(marginal_cost, 2)
            })
        
        return offer_curve

    def run_counterfactual_simulation(
        self,
        actual_offers: List[Dict[str, Any]],
        benchmark_offers: List[Dict[str, Any]],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run ARERA-style counterfactual simulation comparing actual vs benchmark offers.
        
        Args:
            actual_offers: List of actual submitted offers
            benchmark_offers: List of benchmark cost-based offers
            market_data: Market context data
            
        Returns:
            Counterfactual analysis results
        """
        try:
            results = {
                'simulation_timestamp': datetime.utcnow().isoformat(),
                'analysis_type': 'arera_counterfactual',
                'scenarios_analyzed': len(benchmark_offers),
                'actual_offers_count': len(actual_offers),
                'comparisons': [],
                'statistical_analysis': {},
                'risk_indicators': {}
            }
            
            # Compare actual offers against each benchmark scenario
            for benchmark in benchmark_offers:
                comparison = self._compare_offers_to_benchmark(
                    actual_offers, benchmark, market_data
                )
                results['comparisons'].append(comparison)
            
            # Perform statistical analysis
            results['statistical_analysis'] = self._perform_statistical_analysis(
                actual_offers, benchmark_offers
            )
            
            # Calculate risk indicators
            results['risk_indicators'] = self._calculate_risk_indicators(
                results['comparisons'], results['statistical_analysis']
            )
            
            logger.info("Counterfactual simulation completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in counterfactual simulation: {str(e)}")
            return {'error': str(e)}

    def _compare_offers_to_benchmark(
        self,
        actual_offers: List[Dict[str, Any]],
        benchmark: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare actual offers to a benchmark scenario.
        
        Args:
            actual_offers: Actual submitted offers
            benchmark: Benchmark scenario
            market_data: Market context
            
        Returns:
            Comparison results
        """
        comparison = {
            'benchmark_scenario': benchmark['scenario'],
            'benchmark_marginal_cost': benchmark['marginal_cost'],
            'offer_deviations': [],
            'average_markup': 0.0,
            'max_markup': 0.0,
            'markup_distribution': [],
            'price_impact_estimate': 0.0
        }
        
        total_markup = 0.0
        markup_values = []
        
        # Compare each actual offer to benchmark
        for actual_offer in actual_offers:
            actual_price = actual_offer.get('price_eur_mwh', 0)
            actual_quantity = actual_offer.get('quantity_mw', 0)
            
            # Find corresponding benchmark offer
            benchmark_price = self._find_benchmark_price(
                actual_quantity, benchmark['offer_curve']
            )
            
            # Calculate markup
            if benchmark_price > 0:
                markup_ratio = (actual_price - benchmark_price) / benchmark_price
                markup_absolute = actual_price - benchmark_price
            else:
                markup_ratio = 0.0
                markup_absolute = 0.0
            
            deviation = {
                'actual_price': actual_price,
                'benchmark_price': benchmark_price,
                'markup_ratio': markup_ratio,
                'markup_absolute': markup_absolute,
                'quantity': actual_quantity,
                'timestamp': actual_offer.get('timestamp')
            }
            
            comparison['offer_deviations'].append(deviation)
            total_markup += markup_ratio
            markup_values.append(markup_ratio)
        
        # Calculate summary statistics
        if len(actual_offers) > 0:
            comparison['average_markup'] = total_markup / len(actual_offers)
            comparison['max_markup'] = max(markup_values) if markup_values else 0.0
            comparison['markup_distribution'] = {
                'mean': np.mean(markup_values),
                'median': np.median(markup_values),
                'std': np.std(markup_values),
                'percentiles': {
                    '75': np.percentile(markup_values, 75),
                    '90': np.percentile(markup_values, 90),
                    '95': np.percentile(markup_values, 95)
                }
            }
            
            # Estimate price impact (simplified)
            total_capacity = sum(offer.get('quantity_mw', 0) for offer in actual_offers)
            system_load = market_data.get('system_load_mw', 10000)
            if system_load > 0:
                market_share = total_capacity / system_load
                comparison['price_impact_estimate'] = comparison['average_markup'] * market_share
        
        return comparison

    def _find_benchmark_price(
        self, 
        quantity: float, 
        benchmark_curve: List[Dict[str, Any]]
    ) -> float:
        """
        Find benchmark price for given quantity from offer curve.
        
        Args:
            quantity: Quantity to find price for
            benchmark_curve: Benchmark offer curve
            
        Returns:
            Benchmark price
        """
        if not benchmark_curve:
            return 0.0
        
        # Find the appropriate price tier
        for offer in benchmark_curve:
            if quantity <= offer['quantity_mw']:
                return offer['price_eur_mwh']
        
        # If quantity exceeds all tiers, use highest tier price
        return benchmark_curve[-1]['price_eur_mwh']

    def _perform_statistical_analysis(
        self,
        actual_offers: List[Dict[str, Any]],
        benchmark_offers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform statistical analysis of offer deviations.
        
        Args:
            actual_offers: Actual offers
            benchmark_offers: Benchmark offers
            
        Returns:
            Statistical analysis results
        """
        analysis = {
            'tests_performed': [],
            'significance_levels': {},
            'confidence_intervals': {},
            'hypothesis_test_results': {}
        }
        
        try:
            # Collect markup data across all scenarios
            all_markups = []
            
            for benchmark in benchmark_offers:
                for actual_offer in actual_offers:
                    actual_price = actual_offer.get('price_eur_mwh', 0)
                    actual_quantity = actual_offer.get('quantity_mw', 0)
                    
                    benchmark_price = self._find_benchmark_price(
                        actual_quantity, benchmark['offer_curve']
                    )
                    
                    if benchmark_price > 0:
                        markup = (actual_price - benchmark_price) / benchmark_price
                        all_markups.append(markup)
            
            if len(all_markups) > 0:
                # T-test against zero (no markup)
                t_stat, p_value = stats.ttest_1samp(all_markups, 0)
                analysis['hypothesis_test_results']['t_test_vs_zero'] = {
                    'statistic': t_stat,
                    'p_value': p_value,
                    'significant_at_05': p_value < 0.05,
                    'significant_at_01': p_value < 0.01
                }
                analysis['tests_performed'].append('t_test_vs_zero')
                
                # Calculate confidence intervals
                for confidence in self.confidence_intervals:
                    alpha = 1 - confidence
                    ci = stats.t.interval(
                        confidence, 
                        len(all_markups) - 1,
                        loc=np.mean(all_markups),
                        scale=stats.sem(all_markups)
                    )
                    analysis['confidence_intervals'][f'{int(confidence*100)}%'] = {
                        'lower': ci[0],
                        'upper': ci[1],
                        'contains_zero': ci[0] <= 0 <= ci[1]
                    }
                
                # Normality test
                shapiro_stat, shapiro_p = stats.shapiro(all_markups)
                analysis['hypothesis_test_results']['normality_test'] = {
                    'statistic': shapiro_stat,
                    'p_value': shapiro_p,
                    'is_normal_at_05': shapiro_p > 0.05
                }
                analysis['tests_performed'].append('shapiro_wilk_normality')
                
                # Non-parametric test (Wilcoxon signed-rank)
                wilcoxon_stat, wilcoxon_p = stats.wilcoxon(all_markups)
                analysis['hypothesis_test_results']['wilcoxon_test'] = {
                    'statistic': wilcoxon_stat,
                    'p_value': wilcoxon_p,
                    'significant_at_05': wilcoxon_p < 0.05
                }
                analysis['tests_performed'].append('wilcoxon_signed_rank')
            
        except Exception as e:
            logger.warning(f"Error in statistical analysis: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis

    def _calculate_risk_indicators(
        self,
        comparisons: List[Dict[str, Any]],
        statistical_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate risk indicators based on ARERA methodology.
        
        Args:
            comparisons: Offer comparison results
            statistical_analysis: Statistical test results
            
        Returns:
            Risk indicators
        """
        risk_indicators = {
            'overall_risk_score': 0.0,
            'markup_risk_score': 0.0,
            'statistical_significance_score': 0.0,
            'pattern_consistency_score': 0.0,
            'arera_compliance_flags': [],
            'risk_level': 'low'
        }
        
        try:
            # Calculate markup risk score
            max_average_markup = 0.0
            markup_consistency = 0.0
            
            for comparison in comparisons:
                avg_markup = comparison.get('average_markup', 0.0)
                max_average_markup = max(max_average_markup, avg_markup)
                
                # Check markup consistency across scenarios
                markup_std = comparison['markup_distribution'].get('std', 0.0)
                if markup_std < 0.05:  # Low variance indicates consistent pattern
                    markup_consistency += 1
            
            # Markup risk score (0-1 scale)
            if max_average_markup > 0.20:  # >20% markup
                risk_indicators['markup_risk_score'] = 1.0
            elif max_average_markup > 0.15:  # >15% markup
                risk_indicators['markup_risk_score'] = 0.8
            elif max_average_markup > 0.10:  # >10% markup
                risk_indicators['markup_risk_score'] = 0.6
            elif max_average_markup > 0.05:  # >5% markup
                risk_indicators['markup_risk_score'] = 0.4
            else:
                risk_indicators['markup_risk_score'] = 0.2
            
            # Statistical significance score
            hypothesis_tests = statistical_analysis.get('hypothesis_test_results', {})
            significance_score = 0.0
            
            if 't_test_vs_zero' in hypothesis_tests:
                if hypothesis_tests['t_test_vs_zero'].get('significant_at_01', False):
                    significance_score += 0.5
                elif hypothesis_tests['t_test_vs_zero'].get('significant_at_05', False):
                    significance_score += 0.3
            
            if 'wilcoxon_test' in hypothesis_tests:
                if hypothesis_tests['wilcoxon_test'].get('significant_at_05', False):
                    significance_score += 0.3
            
            risk_indicators['statistical_significance_score'] = min(significance_score, 1.0)
            
            # Pattern consistency score
            if len(comparisons) > 0:
                risk_indicators['pattern_consistency_score'] = markup_consistency / len(comparisons)
            
            # Overall risk score (weighted combination)
            risk_indicators['overall_risk_score'] = (
                0.4 * risk_indicators['markup_risk_score'] +
                0.4 * risk_indicators['statistical_significance_score'] +
                0.2 * risk_indicators['pattern_consistency_score']
            )
            
            # ARERA compliance flags
            if max_average_markup > 0.15:
                risk_indicators['arera_compliance_flags'].append('EXCESSIVE_MARKUP')
            
            confidence_90 = statistical_analysis.get('confidence_intervals', {}).get('90%', {})
            if not confidence_90.get('contains_zero', True):
                risk_indicators['arera_compliance_flags'].append('STATISTICALLY_SIGNIFICANT_MARKUP')
            
            # Risk level classification
            overall_score = risk_indicators['overall_risk_score']
            if overall_score >= 0.8:
                risk_indicators['risk_level'] = 'high'
            elif overall_score >= 0.6:
                risk_indicators['risk_level'] = 'medium'
            else:
                risk_indicators['risk_level'] = 'low'
            
        except Exception as e:
            logger.error(f"Error calculating risk indicators: {str(e)}")
            risk_indicators['error'] = str(e)
        
        return risk_indicators

    def run_monte_carlo_simulation(
        self,
        plant_characteristics: Dict[str, Any],
        market_conditions: Dict[str, Any],
        uncertainty_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation to account for parameter uncertainties.
        
        Args:
            plant_characteristics: Plant data
            market_conditions: Market context
            uncertainty_parameters: Uncertainty ranges for key parameters
            
        Returns:
            Monte Carlo simulation results
        """
        try:
            results = {
                'iterations': self.monte_carlo_iterations,
                'marginal_cost_distribution': [],
                'offer_price_distribution': [],
                'markup_distribution': [],
                'summary_statistics': {}
            }
            
            # Extract uncertainty parameters
            fuel_cost_std = uncertainty_parameters.get('fuel_cost_std', 5.0)  # $/MMBtu
            efficiency_std = uncertainty_parameters.get('efficiency_std', 0.02)  # efficiency points
            vom_cost_std = uncertainty_parameters.get('vom_cost_std', 0.5)  # $/MWh
            
            # Base parameters
            base_fuel_cost = uncertainty_parameters.get('base_fuel_cost', 50.0)
            base_efficiency = plant_characteristics.get('efficiency', 0.45)
            base_vom_cost = plant_characteristics.get('variable_costs', {}).get('vom_cost', 3.5)
            heat_rate = plant_characteristics.get('heat_rate', 7500)
            emission_cost = plant_characteristics.get('variable_costs', {}).get('emission_cost', 1.2)
            
            # Run Monte Carlo iterations
            for i in range(self.monte_carlo_iterations):
                # Sample parameters from distributions
                fuel_cost = np.random.normal(base_fuel_cost, fuel_cost_std)
                efficiency = np.random.normal(base_efficiency, efficiency_std)
                vom_cost = np.random.normal(base_vom_cost, vom_cost_std)
                
                # Ensure reasonable bounds
                fuel_cost = max(fuel_cost, 10.0)  # Minimum fuel cost
                efficiency = np.clip(efficiency, 0.2, 0.7)  # Reasonable efficiency range
                vom_cost = max(vom_cost, 0.0)  # Non-negative VOM cost
                
                # Calculate marginal cost for this iteration
                marginal_cost = self._calculate_marginal_cost(
                    fuel_cost, heat_rate, efficiency, vom_cost, emission_cost
                )
                
                results['marginal_cost_distribution'].append(marginal_cost)
            
            # Calculate summary statistics
            mc_costs = results['marginal_cost_distribution']
            results['summary_statistics'] = {
                'mean': np.mean(mc_costs),
                'median': np.median(mc_costs),
                'std': np.std(mc_costs),
                'min': np.min(mc_costs),
                'max': np.max(mc_costs),
                'percentiles': {
                    '5': np.percentile(mc_costs, 5),
                    '25': np.percentile(mc_costs, 25),
                    '75': np.percentile(mc_costs, 75),
                    '95': np.percentile(mc_costs, 95)
                }
            }
            
            logger.info(f"Monte Carlo simulation completed with {self.monte_carlo_iterations} iterations")
            return results
            
        except Exception as e:
            logger.error(f"Error in Monte Carlo simulation: {str(e)}")
            return {'error': str(e)}

    def generate_sensitivity_analysis(
        self,
        base_case: Dict[str, Any],
        sensitivity_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate sensitivity analysis for key parameters.
        
        Args:
            base_case: Base case scenario
            sensitivity_parameters: Parameters to vary
            
        Returns:
            Sensitivity analysis results
        """
        try:
            sensitivity_results = {
                'base_case': base_case,
                'parameter_variations': [],
                'tornado_chart_data': []
            }
            
            base_marginal_cost = base_case.get('marginal_cost', 0.0)
            
            # Analyze sensitivity to each parameter
            for param_name, variation_range in sensitivity_parameters.items():
                low_value, high_value = variation_range
                
                # Calculate impact of parameter variation
                low_impact = self._calculate_parameter_impact(
                    base_case, param_name, low_value
                )
                high_impact = self._calculate_parameter_impact(
                    base_case, param_name, high_value
                )
                
                variation_result = {
                    'parameter': param_name,
                    'base_value': base_case.get(param_name, 0.0),
                    'low_value': low_value,
                    'high_value': high_value,
                    'low_marginal_cost': low_impact,
                    'high_marginal_cost': high_impact,
                    'sensitivity': abs(high_impact - low_impact) / (2 * base_marginal_cost) if base_marginal_cost > 0 else 0
                }
                
                sensitivity_results['parameter_variations'].append(variation_result)
                
                # Tornado chart data
                sensitivity_results['tornado_chart_data'].append({
                    'parameter': param_name,
                    'low_impact': low_impact - base_marginal_cost,
                    'high_impact': high_impact - base_marginal_cost
                })
            
            # Sort by sensitivity (for tornado chart)
            sensitivity_results['tornado_chart_data'].sort(
                key=lambda x: abs(x['high_impact'] - x['low_impact']), 
                reverse=True
            )
            
            return sensitivity_results
            
        except Exception as e:
            logger.error(f"Error in sensitivity analysis: {str(e)}")
            return {'error': str(e)}

    def _calculate_parameter_impact(
        self,
        base_case: Dict[str, Any],
        parameter: str,
        value: float
    ) -> float:
        """
        Calculate the impact of changing a parameter value.
        
        Args:
            base_case: Base case scenario
            parameter: Parameter to change
            value: New parameter value
            
        Returns:
            New marginal cost
        """
        # Create modified case
        modified_case = base_case.copy()
        modified_case[parameter] = value
        
        # Recalculate marginal cost
        fuel_cost = modified_case.get('fuel_cost', 50.0)
        heat_rate = modified_case.get('heat_rate', 7500)
        efficiency = modified_case.get('efficiency', 0.45)
        vom_cost = modified_case.get('vom_cost', 3.5)
        emission_cost = modified_case.get('emission_cost', 1.2)
        
        return self._calculate_marginal_cost(
            fuel_cost, heat_rate, efficiency, vom_cost, emission_cost
        )