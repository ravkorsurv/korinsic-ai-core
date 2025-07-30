"""
Cost Curve Analyzer for Economic Withholding Detection.

This module analyzes cost curves vs submitted offers using ARERA methodology
for detecting economic withholding through statistical analysis of offer-cost relationships.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats, optimize
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from datetime import datetime

logger = logging.getLogger(__name__)


class CostCurveAnalyzer:
    """
    Analyzes cost curves vs submitted offers using ARERA methodology.
    
    Implements the Italian regulatory approach for detecting economic
    withholding through statistical analysis of offer-cost relationships.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the cost curve analyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.cost_curve_methods = self.config.get('cost_curve_methods', ['linear', 'quadratic', 'step_function'])
        self.statistical_tests = self.config.get('statistical_tests', ['t_test', 'mann_whitney', 'kolmogorov_smirnov'])
        self.confidence_intervals = self.config.get('confidence_intervals', [0.90, 0.95, 0.99])
        
        logger.info("Cost curve analyzer initialized")

    def analyze_offer_cost_relationship(
        self, 
        offers: List[Dict[str, Any]], 
        costs: Dict[str, Any],
        plant_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze relationship between offers and declared costs.
        
        Args:
            offers: List of submitted offers
            costs: Cost data and calculations
            plant_characteristics: Plant technical data
            
        Returns:
            Analysis results
        """
        try:
            analysis_results = {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analysis_type': 'offer_cost_relationship',
                'offers_analyzed': len(offers),
                'cost_basis': costs,
                'relationships': {},
                'statistical_measures': {},
                'anomaly_detection': {},
                'regulatory_flags': []
            }
            
            # Prepare data for analysis
            offer_data = self._prepare_offer_data(offers, costs)
            
            if len(offer_data) == 0:
                analysis_results['error'] = 'No valid offer data for analysis'
                return analysis_results
            
            # Analyze different cost-offer relationships
            analysis_results['relationships'] = self._analyze_cost_relationships(
                offer_data, plant_characteristics
            )
            
            # Calculate statistical measures
            analysis_results['statistical_measures'] = self._calculate_statistical_measures(
                offer_data
            )
            
            # Detect anomalies
            analysis_results['anomaly_detection'] = self._detect_cost_anomalies(
                offer_data, costs
            )
            
            # Generate regulatory flags
            analysis_results['regulatory_flags'] = self._generate_regulatory_flags(
                analysis_results
            )
            
            logger.info(f"Offer-cost relationship analysis completed for {len(offers)} offers")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in offer-cost relationship analysis: {str(e)}")
            return {'error': str(e)}

    def _prepare_offer_data(
        self, 
        offers: List[Dict[str, Any]], 
        costs: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Prepare offer data for analysis.
        
        Args:
            offers: List of offers
            costs: Cost data
            
        Returns:
            Prepared DataFrame
        """
        data = []
        marginal_cost = costs.get('marginal_cost', 0.0)
        
        for offer in offers:
            price = offer.get('price_eur_mwh', 0.0)
            quantity = offer.get('quantity_mw', 0.0)
            timestamp = offer.get('timestamp')
            
            if price > 0 and quantity > 0:
                markup_ratio = (price - marginal_cost) / marginal_cost if marginal_cost > 0 else 0
                markup_absolute = price - marginal_cost
                
                data.append({
                    'price': price,
                    'quantity': quantity,
                    'marginal_cost': marginal_cost,
                    'markup_ratio': markup_ratio,
                    'markup_absolute': markup_absolute,
                    'timestamp': timestamp
                })
        
        return pd.DataFrame(data)

    def _analyze_cost_relationships(
        self, 
        offer_data: pd.DataFrame, 
        plant_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze different types of cost-offer relationships.
        
        Args:
            offer_data: Prepared offer data
            plant_characteristics: Plant data
            
        Returns:
            Relationship analysis results
        """
        relationships = {}
        
        try:
            # Linear relationship analysis
            relationships['linear'] = self._analyze_linear_relationship(offer_data)
            
            # Quadratic relationship analysis (for capacity constraints)
            relationships['quadratic'] = self._analyze_quadratic_relationship(offer_data)
            
            # Step function analysis (for unit commitment costs)
            relationships['step_function'] = self._analyze_step_function(offer_data)
            
            # Capacity utilization relationship
            relationships['capacity_utilization'] = self._analyze_capacity_relationship(
                offer_data, plant_characteristics
            )
            
        except Exception as e:
            logger.warning(f"Error in relationship analysis: {str(e)}")
            relationships['error'] = str(e)
        
        return relationships

    def _analyze_linear_relationship(self, offer_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze linear relationship between quantity and markup.
        
        Args:
            offer_data: Offer data
            
        Returns:
            Linear relationship analysis
        """
        if len(offer_data) < 2:
            return {'error': 'Insufficient data for linear analysis'}
        
        X = offer_data[['quantity']].values
        y = offer_data['markup_ratio'].values
        
        # Fit linear regression
        reg = LinearRegression()
        reg.fit(X, y)
        
        y_pred = reg.predict(X)
        r2 = r2_score(y, y_pred)
        
        # Statistical significance test
        n = len(offer_data)
        if n > 2:
            # Calculate t-statistic for slope
            slope = reg.coef_[0]
            intercept = reg.intercept_
            
            # Standard error of slope
            mse = np.mean((y - y_pred) ** 2)
            x_mean = np.mean(X)
            ss_x = np.sum((X - x_mean) ** 2)
            se_slope = np.sqrt(mse / ss_x) if ss_x > 0 else 0
            
            t_stat = slope / se_slope if se_slope > 0 else 0
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2)) if n > 2 else 1.0
        else:
            t_stat = 0
            p_value = 1.0
        
        return {
            'slope': float(reg.coef_[0]),
            'intercept': float(reg.intercept_),
            'r_squared': float(r2),
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant_at_05': p_value < 0.05,
            'relationship_strength': 'strong' if r2 > 0.7 else 'moderate' if r2 > 0.3 else 'weak'
        }

    def _analyze_quadratic_relationship(self, offer_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze quadratic relationship (capacity constraints).
        
        Args:
            offer_data: Offer data
            
        Returns:
            Quadratic relationship analysis
        """
        if len(offer_data) < 3:
            return {'error': 'Insufficient data for quadratic analysis'}
        
        X = offer_data[['quantity']].values
        y = offer_data['markup_ratio'].values
        
        # Create polynomial features
        poly_features = PolynomialFeatures(degree=2)
        X_poly = poly_features.fit_transform(X)
        
        # Fit quadratic regression
        reg = LinearRegression()
        reg.fit(X_poly, y)
        
        y_pred = reg.predict(X_poly)
        r2 = r2_score(y, y_pred)
        
        # Extract coefficients
        intercept = reg.intercept_
        linear_coef = reg.coef_[1] if len(reg.coef_) > 1 else 0
        quad_coef = reg.coef_[2] if len(reg.coef_) > 2 else 0
        
        return {
            'intercept': float(intercept),
            'linear_coefficient': float(linear_coef),
            'quadratic_coefficient': float(quad_coef),
            'r_squared': float(r2),
            'curvature': 'convex' if quad_coef > 0 else 'concave' if quad_coef < 0 else 'linear',
            'relationship_strength': 'strong' if r2 > 0.7 else 'moderate' if r2 > 0.3 else 'weak'
        }

    def _analyze_step_function(self, offer_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze step function behavior (unit commitment).
        
        Args:
            offer_data: Offer data
            
        Returns:
            Step function analysis
        """
        if len(offer_data) < 2:
            return {'error': 'Insufficient data for step function analysis'}
        
        # Sort by quantity
        sorted_data = offer_data.sort_values('quantity')
        quantities = sorted_data['markup_ratio'].values
        
        # Detect steps using change point detection
        steps = []
        threshold = 0.05  # 5% markup change threshold
        
        for i in range(1, len(quantities)):
            change = abs(quantities[i] - quantities[i-1])
            if change > threshold:
                steps.append({
                    'position': i,
                    'quantity': float(sorted_data.iloc[i]['quantity']),
                    'markup_change': float(change),
                    'direction': 'increase' if quantities[i] > quantities[i-1] else 'decrease'
                })
        
        # Calculate step consistency
        if len(steps) > 0:
            step_sizes = [step['markup_change'] for step in steps]
            step_consistency = 1.0 - (np.std(step_sizes) / np.mean(step_sizes)) if np.mean(step_sizes) > 0 else 0
        else:
            step_consistency = 0.0
        
        return {
            'steps_detected': len(steps),
            'step_details': steps,
            'step_consistency': float(step_consistency),
            'pattern_type': 'stepped' if len(steps) > 2 else 'smooth'
        }

    def _analyze_capacity_relationship(
        self, 
        offer_data: pd.DataFrame, 
        plant_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze relationship with capacity utilization.
        
        Args:
            offer_data: Offer data
            plant_characteristics: Plant data
            
        Returns:
            Capacity relationship analysis
        """
        capacity_mw = plant_characteristics.get('capacity_mw', 0)
        if capacity_mw <= 0:
            return {'error': 'No capacity data available'}
        
        if len(offer_data) == 0:
            return {'error': 'No offer data available'}
        
        # Calculate capacity utilization
        offer_data = offer_data.copy()
        offer_data['capacity_utilization'] = offer_data['quantity'] / capacity_mw
        
        # Analyze markup vs capacity utilization
        utilization = offer_data['capacity_utilization'].values
        markup = offer_data['markup_ratio'].values
        
        if len(utilization) < 2:
            return {'error': 'Insufficient data for capacity analysis'}
        
        # Correlation analysis
        correlation, p_value = stats.pearsonr(utilization, markup)
        
        # Capacity bands analysis
        bands = {
            'low_utilization': {'range': [0.0, 0.3], 'offers': [], 'avg_markup': 0.0},
            'medium_utilization': {'range': [0.3, 0.7], 'offers': [], 'avg_markup': 0.0},
            'high_utilization': {'range': [0.7, 1.0], 'offers': [], 'avg_markup': 0.0}
        }
        
        for i, util in enumerate(utilization):
            if util <= 0.3:
                bands['low_utilization']['offers'].append(markup[i])
            elif util <= 0.7:
                bands['medium_utilization']['offers'].append(markup[i])
            else:
                bands['high_utilization']['offers'].append(markup[i])
        
        # Calculate average markup per band
        for band_name, band_data in bands.items():
            if len(band_data['offers']) > 0:
                band_data['avg_markup'] = float(np.mean(band_data['offers']))
                band_data['count'] = len(band_data['offers'])
            else:
                band_data['avg_markup'] = 0.0
                band_data['count'] = 0
        
        return {
            'correlation': float(correlation),
            'p_value': float(p_value),
            'significant_correlation': p_value < 0.05,
            'capacity_bands': bands,
            'max_utilization': float(np.max(utilization)),
            'avg_utilization': float(np.mean(utilization))
        }

    def _calculate_statistical_measures(self, offer_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate statistical measures of offer behavior.
        
        Args:
            offer_data: Offer data
            
        Returns:
            Statistical measures
        """
        if len(offer_data) == 0:
            return {'error': 'No data for statistical analysis'}
        
        markup_ratios = offer_data['markup_ratio'].values
        prices = offer_data['price'].values
        quantities = offer_data['quantity'].values
        
        measures = {
            'markup_statistics': {
                'mean': float(np.mean(markup_ratios)),
                'median': float(np.median(markup_ratios)),
                'std': float(np.std(markup_ratios)),
                'min': float(np.min(markup_ratios)),
                'max': float(np.max(markup_ratios)),
                'percentiles': {
                    '25': float(np.percentile(markup_ratios, 25)),
                    '75': float(np.percentile(markup_ratios, 75)),
                    '90': float(np.percentile(markup_ratios, 90)),
                    '95': float(np.percentile(markup_ratios, 95))
                }
            },
            'price_statistics': {
                'mean': float(np.mean(prices)),
                'median': float(np.median(prices)),
                'std': float(np.std(prices)),
                'coefficient_of_variation': float(np.std(prices) / np.mean(prices)) if np.mean(prices) > 0 else 0
            },
            'quantity_statistics': {
                'mean': float(np.mean(quantities)),
                'median': float(np.median(quantities)),
                'std': float(np.std(quantities)),
                'total': float(np.sum(quantities))
            }
        }
        
        # Normality tests
        if len(markup_ratios) >= 3:
            shapiro_stat, shapiro_p = stats.shapiro(markup_ratios)
            measures['normality_tests'] = {
                'shapiro_wilk': {
                    'statistic': float(shapiro_stat),
                    'p_value': float(shapiro_p),
                    'is_normal': shapiro_p > 0.05
                }
            }
        
        # Outlier detection using IQR method
        q1 = np.percentile(markup_ratios, 25)
        q3 = np.percentile(markup_ratios, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = markup_ratios[(markup_ratios < lower_bound) | (markup_ratios > upper_bound)]
        measures['outlier_analysis'] = {
            'outlier_count': len(outliers),
            'outlier_percentage': float(len(outliers) / len(markup_ratios) * 100),
            'outlier_values': outliers.tolist(),
            'iqr_bounds': {'lower': float(lower_bound), 'upper': float(upper_bound)}
        }
        
        return measures

    def detect_bid_shape_anomalies(self, offer_curve: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect anomalous bid shapes that suggest strategic withholding.
        
        Args:
            offer_curve: List of price-quantity pairs
            
        Returns:
            Bid shape anomaly analysis
        """
        try:
            if len(offer_curve) < 2:
                return {'error': 'Insufficient data for bid shape analysis'}
            
            # Sort by quantity
            sorted_curve = sorted(offer_curve, key=lambda x: x.get('quantity_mw', 0))
            
            anomalies = {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'curve_points': len(sorted_curve),
                'shape_characteristics': {},
                'anomaly_flags': [],
                'anomaly_score': 0.0
            }
            
            # Extract price and quantity arrays
            quantities = [point.get('quantity_mw', 0) for point in sorted_curve]
            prices = [point.get('price_eur_mwh', 0) for point in sorted_curve]
            
            # Shape characteristics
            anomalies['shape_characteristics'] = self._analyze_curve_shape(quantities, prices)
            
            # Detect specific anomalies
            anomalies['anomaly_flags'] = self._detect_shape_anomalies(quantities, prices)
            
            # Calculate overall anomaly score
            anomalies['anomaly_score'] = self._calculate_shape_anomaly_score(
                anomalies['shape_characteristics'], anomalies['anomaly_flags']
            )
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in bid shape anomaly detection: {str(e)}")
            return {'error': str(e)}

    def _analyze_curve_shape(self, quantities: List[float], prices: List[float]) -> Dict[str, Any]:
        """
        Analyze the shape characteristics of the bid curve.
        
        Args:
            quantities: Quantity values
            prices: Price values
            
        Returns:
            Shape characteristics
        """
        if len(quantities) < 2:
            return {}
        
        # Calculate price gradients
        gradients = []
        for i in range(1, len(prices)):
            if quantities[i] != quantities[i-1]:
                gradient = (prices[i] - prices[i-1]) / (quantities[i] - quantities[i-1])
                gradients.append(gradient)
        
        characteristics = {
            'monotonicity': self._check_monotonicity(prices),
            'convexity': self._check_convexity(quantities, prices),
            'gradient_analysis': {
                'mean_gradient': float(np.mean(gradients)) if gradients else 0.0,
                'max_gradient': float(np.max(gradients)) if gradients else 0.0,
                'gradient_variance': float(np.var(gradients)) if gradients else 0.0,
                'steep_sections': len([g for g in gradients if g > np.mean(gradients) * 2]) if gradients else 0
            },
            'price_range': {
                'min_price': float(min(prices)),
                'max_price': float(max(prices)),
                'price_span': float(max(prices) - min(prices)),
                'relative_span': float((max(prices) - min(prices)) / min(prices)) if min(prices) > 0 else 0
            }
        }
        
        return characteristics

    def _check_monotonicity(self, prices: List[float]) -> Dict[str, Any]:
        """Check if prices are monotonically increasing."""
        increasing_violations = 0
        for i in range(1, len(prices)):
            if prices[i] < prices[i-1]:
                increasing_violations += 1
        
        return {
            'is_monotonic_increasing': increasing_violations == 0,
            'violations': increasing_violations,
            'violation_rate': float(increasing_violations / (len(prices) - 1)) if len(prices) > 1 else 0
        }

    def _check_convexity(self, quantities: List[float], prices: List[float]) -> Dict[str, Any]:
        """Check convexity of the bid curve."""
        if len(quantities) < 3:
            return {'insufficient_data': True}
        
        # Calculate second derivatives (discrete approximation)
        second_derivatives = []
        for i in range(1, len(prices) - 1):
            if quantities[i+1] != quantities[i-1]:
                second_deriv = 2 * (prices[i] - (prices[i-1] + prices[i+1]) / 2)
                second_derivatives.append(second_deriv)
        
        if not second_derivatives:
            return {'insufficient_data': True}
        
        convex_points = len([d for d in second_derivatives if d > 0])
        concave_points = len([d for d in second_derivatives if d < 0])
        
        return {
            'overall_convexity': 'convex' if convex_points > concave_points else 'concave' if concave_points > convex_points else 'mixed',
            'convex_points': convex_points,
            'concave_points': concave_points,
            'convexity_ratio': float(convex_points / len(second_derivatives)) if second_derivatives else 0
        }

    def _detect_shape_anomalies(self, quantities: List[float], prices: List[float]) -> List[str]:
        """Detect specific shape anomalies."""
        anomaly_flags = []
        
        if len(quantities) < 2:
            return anomaly_flags
        
        # Check for price jumps
        for i in range(1, len(prices)):
            if quantities[i] > quantities[i-1]:  # Avoid division by zero
                price_increase_rate = (prices[i] - prices[i-1]) / (quantities[i] - quantities[i-1])
                if price_increase_rate > 10:  # Steep price increase (>10 $/MWh per MW)
                    anomaly_flags.append('STEEP_PRICE_JUMP')
                    break
        
        # Check for flat segments (economic withholding indicator)
        flat_segments = 0
        for i in range(1, len(prices)):
            if abs(prices[i] - prices[i-1]) < 0.01 and quantities[i] != quantities[i-1]:
                flat_segments += 1
        
        if flat_segments > len(prices) * 0.3:  # More than 30% flat segments
            anomaly_flags.append('EXCESSIVE_FLAT_SEGMENTS')
        
        # Check for hockey stick pattern (sudden steep increase)
        if len(prices) >= 3:
            gradients = []
            for i in range(1, len(prices)):
                if quantities[i] != quantities[i-1]:
                    gradient = (prices[i] - prices[i-1]) / (quantities[i] - quantities[i-1])
                    gradients.append(gradient)
            
            if gradients:
                mean_gradient = np.mean(gradients)
                for gradient in gradients[-2:]:  # Check last two gradients
                    if gradient > mean_gradient * 5:  # 5x average gradient
                        anomaly_flags.append('HOCKEY_STICK_PATTERN')
                        break
        
        # Check for capacity withholding (low final quantity)
        max_quantity = max(quantities)
        expected_capacity = max_quantity * 1.2  # Assume 20% more capacity available
        if max_quantity < expected_capacity * 0.8:  # Using less than 80% of expected
            anomaly_flags.append('POTENTIAL_CAPACITY_WITHHOLDING')
        
        return anomaly_flags

    def _calculate_shape_anomaly_score(
        self, 
        characteristics: Dict[str, Any], 
        anomaly_flags: List[str]
    ) -> float:
        """Calculate overall shape anomaly score."""
        score = 0.0
        
        # Score based on anomaly flags
        flag_weights = {
            'STEEP_PRICE_JUMP': 0.3,
            'EXCESSIVE_FLAT_SEGMENTS': 0.2,
            'HOCKEY_STICK_PATTERN': 0.4,
            'POTENTIAL_CAPACITY_WITHHOLDING': 0.3
        }
        
        for flag in anomaly_flags:
            score += flag_weights.get(flag, 0.1)
        
        # Score based on characteristics
        if 'monotonicity' in characteristics:
            violation_rate = characteristics['monotonicity'].get('violation_rate', 0)
            score += violation_rate * 0.2
        
        if 'gradient_analysis' in characteristics:
            gradient_var = characteristics['gradient_analysis'].get('gradient_variance', 0)
            if gradient_var > 100:  # High gradient variance
                score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0

    def calculate_markup_statistics(
        self, 
        offers: List[Dict[str, Any]], 
        marginal_costs: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate statistical measures of markup over marginal cost.
        
        Args:
            offers: List of offers
            marginal_costs: List of marginal costs
            
        Returns:
            Markup statistics
        """
        try:
            if len(offers) != len(marginal_costs):
                return {'error': 'Offers and marginal costs length mismatch'}
            
            markup_data = []
            for i, offer in enumerate(offers):
                price = offer.get('price_eur_mwh', 0)
                marginal_cost = marginal_costs[i] if i < len(marginal_costs) else 0
                
                if marginal_cost > 0:
                    markup_ratio = (price - marginal_cost) / marginal_cost
                    markup_absolute = price - marginal_cost
                    markup_data.append({
                        'markup_ratio': markup_ratio,
                        'markup_absolute': markup_absolute,
                        'price': price,
                        'marginal_cost': marginal_cost,
                        'quantity': offer.get('quantity_mw', 0)
                    })
            
            if not markup_data:
                return {'error': 'No valid markup data'}
            
            markup_ratios = [d['markup_ratio'] for d in markup_data]
            markup_absolutes = [d['markup_absolute'] for d in markup_data]
            
            statistics = {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'sample_size': len(markup_data),
                'markup_ratio_stats': {
                    'mean': float(np.mean(markup_ratios)),
                    'median': float(np.median(markup_ratios)),
                    'std': float(np.std(markup_ratios)),
                    'min': float(np.min(markup_ratios)),
                    'max': float(np.max(markup_ratios)),
                    'percentiles': {
                        '10': float(np.percentile(markup_ratios, 10)),
                        '25': float(np.percentile(markup_ratios, 25)),
                        '75': float(np.percentile(markup_ratios, 75)),
                        '90': float(np.percentile(markup_ratios, 90)),
                        '95': float(np.percentile(markup_ratios, 95))
                    }
                },
                'markup_absolute_stats': {
                    'mean': float(np.mean(markup_absolutes)),
                    'median': float(np.median(markup_absolutes)),
                    'std': float(np.std(markup_absolutes))
                },
                'distribution_analysis': {},
                'regulatory_thresholds': {}
            }
            
            # Distribution analysis
            if len(markup_ratios) >= 3:
                shapiro_stat, shapiro_p = stats.shapiro(markup_ratios)
                statistics['distribution_analysis'] = {
                    'normality_test': {
                        'statistic': float(shapiro_stat),
                        'p_value': float(shapiro_p),
                        'is_normal': shapiro_p > 0.05
                    },
                    'skewness': float(stats.skew(markup_ratios)),
                    'kurtosis': float(stats.kurtosis(markup_ratios))
                }
            
            # Regulatory threshold analysis
            threshold_15pct = len([r for r in markup_ratios if r > 0.15])
            threshold_20pct = len([r for r in markup_ratios if r > 0.20])
            threshold_25pct = len([r for r in markup_ratios if r > 0.25])
            
            statistics['regulatory_thresholds'] = {
                'above_15_percent': {
                    'count': threshold_15pct,
                    'percentage': float(threshold_15pct / len(markup_ratios) * 100)
                },
                'above_20_percent': {
                    'count': threshold_20pct,
                    'percentage': float(threshold_20pct / len(markup_ratios) * 100)
                },
                'above_25_percent': {
                    'count': threshold_25pct,
                    'percentage': float(threshold_25pct / len(markup_ratios) * 100)
                }
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error calculating markup statistics: {str(e)}")
            return {'error': str(e)}

    def _detect_cost_anomalies(
        self, 
        offer_data: pd.DataFrame, 
        costs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect anomalies in cost declarations.
        
        Args:
            offer_data: Offer data
            costs: Cost data
            
        Returns:
            Cost anomaly detection results
        """
        anomalies = {
            'fuel_cost_anomalies': [],
            'efficiency_anomalies': [],
            'vom_cost_anomalies': [],
            'overall_anomaly_score': 0.0
        }
        
        try:
            # This would typically compare against market benchmarks
            # For now, implement basic consistency checks
            
            declared_marginal_cost = costs.get('marginal_cost', 0)
            fuel_cost = costs.get('fuel_cost', 0)
            efficiency = costs.get('efficiency', 0.45)
            
            # Check for unreasonably low efficiency
            if efficiency < 0.25:
                anomalies['efficiency_anomalies'].append({
                    'type': 'LOW_EFFICIENCY',
                    'declared_value': efficiency,
                    'benchmark_range': [0.35, 0.60],
                    'severity': 'high'
                })
            
            # Check for fuel cost consistency
            if fuel_cost > 0:
                # This would compare against market fuel prices
                market_fuel_price = 50.0  # Placeholder
                fuel_deviation = abs(fuel_cost - market_fuel_price) / market_fuel_price
                
                if fuel_deviation > 0.20:  # >20% deviation
                    anomalies['fuel_cost_anomalies'].append({
                        'type': 'FUEL_COST_DEVIATION',
                        'declared_value': fuel_cost,
                        'market_benchmark': market_fuel_price,
                        'deviation_percent': fuel_deviation * 100,
                        'severity': 'medium' if fuel_deviation < 0.30 else 'high'
                    })
            
            # Calculate overall anomaly score
            anomaly_count = (
                len(anomalies['fuel_cost_anomalies']) +
                len(anomalies['efficiency_anomalies']) +
                len(anomalies['vom_cost_anomalies'])
            )
            
            anomalies['overall_anomaly_score'] = min(anomaly_count * 0.3, 1.0)
            
        except Exception as e:
            logger.warning(f"Error in cost anomaly detection: {str(e)}")
            anomalies['error'] = str(e)
        
        return anomalies

    def _generate_regulatory_flags(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Generate regulatory compliance flags based on analysis results.
        
        Args:
            analysis_results: Complete analysis results
            
        Returns:
            List of regulatory flags
        """
        flags = []
        
        try:
            # Check markup statistics
            statistical_measures = analysis_results.get('statistical_measures', {})
            markup_stats = statistical_measures.get('markup_statistics', {})
            
            mean_markup = markup_stats.get('mean', 0)
            max_markup = markup_stats.get('max', 0)
            p95_markup = markup_stats.get('percentiles', {}).get('95', 0)
            
            # ARERA-style flags
            if mean_markup > 0.15:  # 15% average markup
                flags.append('ARERA_EXCESSIVE_AVERAGE_MARKUP')
            
            if max_markup > 0.25:  # 25% maximum markup
                flags.append('ARERA_EXCESSIVE_MAXIMUM_MARKUP')
            
            if p95_markup > 0.20:  # 20% 95th percentile markup
                flags.append('ARERA_SYSTEMATIC_HIGH_MARKUP')
            
            # Check relationship analysis
            relationships = analysis_results.get('relationships', {})
            linear_rel = relationships.get('linear', {})
            
            if linear_rel.get('significant_at_05', False) and linear_rel.get('slope', 0) > 0.1:
                flags.append('ARERA_QUANTITY_DEPENDENT_MARKUP')
            
            # Check anomaly detection
            anomaly_detection = analysis_results.get('anomaly_detection', {})
            anomaly_score = anomaly_detection.get('overall_anomaly_score', 0)
            
            if anomaly_score > 0.5:
                flags.append('ARERA_COST_DECLARATION_ANOMALIES')
            
            # Check outliers
            outlier_analysis = statistical_measures.get('outlier_analysis', {})
            outlier_percentage = outlier_analysis.get('outlier_percentage', 0)
            
            if outlier_percentage > 20:  # >20% outliers
                flags.append('ARERA_EXCESSIVE_OUTLIERS')
            
        except Exception as e:
            logger.warning(f"Error generating regulatory flags: {str(e)}")
            flags.append('ANALYSIS_ERROR')
        
        return flags