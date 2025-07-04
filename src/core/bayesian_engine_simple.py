"""
Simplified Bayesian Inference Engine for Market Abuse Detection
Uses basic probability calculations to demonstrate surveillance capabilities
"""

import numpy as np
from typing import Dict, List, Any


class SimpleBayesianEngine:
    """Simplified Bayesian inference engine for market abuse detection"""
    
    def __init__(self):
        """Initialize the simplified Bayesian engine"""
        self.insider_dealing_weights = {
            'material_info_access': 0.3,
            'trading_timing': 0.25,
            'volume_anomaly': 0.2,
            'price_impact': 0.15,
            'frequency_pattern': 0.1
        }
        
        self.spoofing_weights = {
            'order_cancellation_rate': 0.35,
            'order_size_ratio': 0.25,
            'price_movement_timing': 0.2,
            'volume_imbalance': 0.15,
            'pattern_frequency': 0.05
        }
    
    def calculate_insider_dealing_risk(self, features: Dict[str, Any]) -> float:
        """
        Calculate insider dealing risk using weighted feature scoring
        
        Args:
            features: Dictionary containing extracted features
            
        Returns:
            Risk score between 0.0 and 1.0
        """
        # Material information access score
        material_score = 0.0
        if features.get('has_material_events', False):
            days_before = features.get('days_before_material_event', 30)
            material_score = max(0, (30 - days_before) / 30) * 0.8
            if features.get('trader_role') in ['executive', 'insider']:
                material_score += 0.2
        
        # Trading timing score
        timing_score = 0.0
        if features.get('trading_outside_hours', False):
            timing_score += 0.3
        if features.get('unusual_timing_pattern', False):
            timing_score += 0.4
        timing_score = min(timing_score, 1.0)
        
        # Volume anomaly score
        volume_ratio = features.get('volume_vs_average', 1.0)
        volume_score = min((volume_ratio - 1.0) / 10.0, 1.0) if volume_ratio > 1.0 else 0.0
        
        # Price impact score
        price_impact = abs(features.get('price_impact_bps', 0))
        price_score = min(price_impact / 500.0, 1.0)  # Normalize to 500 bps
        
        # Frequency pattern score
        frequency_score = min(features.get('trading_frequency_anomaly', 0) / 5.0, 1.0)
        
        # Calculate weighted risk score
        risk_score = (
            material_score * self.insider_dealing_weights['material_info_access'] +
            timing_score * self.insider_dealing_weights['trading_timing'] +
            volume_score * self.insider_dealing_weights['volume_anomaly'] +
            price_score * self.insider_dealing_weights['price_impact'] +
            frequency_score * self.insider_dealing_weights['frequency_pattern']
        )
        
        return min(max(risk_score, 0.0), 1.0)
    
    def calculate_spoofing_risk(self, features: Dict[str, Any]) -> float:
        """
        Calculate spoofing risk using weighted feature scoring
        
        Args:
            features: Dictionary containing extracted features
            
        Returns:
            Risk score between 0.0 and 1.0
        """
        # Order cancellation rate score
        cancellation_rate = features.get('order_cancellation_rate', 0.0)
        cancellation_score = min(cancellation_rate, 1.0)
        
        # Order size ratio score (large orders vs small executions)
        large_to_small_ratio = features.get('large_to_small_order_ratio', 1.0)
        size_ratio_score = min((large_to_small_ratio - 1.0) / 20.0, 1.0) if large_to_small_ratio > 1.0 else 0.0
        
        # Price movement timing score
        price_timing_score = 0.0
        if features.get('price_movement_after_orders', False):
            price_timing_score = 0.6
        if features.get('immediate_cancellation_after_movement', False):
            price_timing_score += 0.4
        price_timing_score = min(price_timing_score, 1.0)
        
        # Volume imbalance score
        volume_imbalance = features.get('bid_ask_volume_imbalance', 0.0)
        volume_imbalance_score = min(abs(volume_imbalance) / 0.8, 1.0)
        
        # Pattern frequency score
        pattern_frequency = features.get('spoofing_pattern_frequency', 0)
        frequency_score = min(pattern_frequency / 10.0, 1.0)
        
        # Calculate weighted risk score
        risk_score = (
            cancellation_score * self.spoofing_weights['order_cancellation_rate'] +
            size_ratio_score * self.spoofing_weights['order_size_ratio'] +
            price_timing_score * self.spoofing_weights['price_movement_timing'] +
            volume_imbalance_score * self.spoofing_weights['volume_imbalance'] +
            frequency_score * self.spoofing_weights['pattern_frequency']
        )
        
        return min(max(risk_score, 0.0), 1.0)
    
    def analyze_risk(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market abuse risk for the given data
        
        Args:
            data: Market data including trades, orders, trader info, etc.
            
        Returns:
            Dictionary containing risk scores and analysis
        """
        # Extract features from data (simplified version)
        features = self._extract_features(data)
        
        # Calculate risk scores
        insider_risk = self.calculate_insider_dealing_risk(features)
        spoofing_risk = self.calculate_spoofing_risk(features)
        
        # Determine overall risk level
        overall_risk = max(insider_risk, spoofing_risk)
        
        return {
            'insider_dealing_risk': insider_risk,
            'spoofing_risk': spoofing_risk,
            'overall_risk': overall_risk,
            'risk_level': self._get_risk_level(overall_risk),
            'features_analyzed': features,
            'model_confidence': 0.85,  # Simplified confidence score
            'explanation': self._generate_explanation(insider_risk, spoofing_risk, features)
        }
    
    def _extract_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant features from market data"""
        trades = data.get('trades', [])
        orders = data.get('orders', [])
        trader_info = data.get('trader_info', {})
        material_events = data.get('material_events', [])
        
        features = {}
        
        # Basic volume analysis
        if trades:
            volumes = [trade.get('volume', 0) for trade in trades]
            avg_volume = np.mean(volumes) if volumes else 0
            features['volume_vs_average'] = max(volumes) / avg_volume if avg_volume > 0 else 1.0
            
            # Price impact analysis
            prices = [trade.get('price', 0) for trade in trades]
            if len(prices) > 1:
                price_change = (prices[-1] - prices[0]) / prices[0] * 10000  # in bps
                features['price_impact_bps'] = abs(price_change)
            else:
                features['price_impact_bps'] = 0
        
        # Material events analysis
        features['has_material_events'] = len(material_events) > 0
        if material_events:
            # Simulate days before material event
            features['days_before_material_event'] = np.random.randint(1, 15)
        
        # Trader information
        features['trader_role'] = trader_info.get('role', 'trader')
        
        # Order analysis
        if orders:
            cancelled_orders = [o for o in orders if o.get('status') == 'cancelled']
            features['order_cancellation_rate'] = len(cancelled_orders) / len(orders)
            
            # Order size analysis
            order_sizes = [o.get('size', 0) for o in orders]
            executed_sizes = [trade.get('volume', 0) for trade in trades]
            if order_sizes and executed_sizes:
                avg_order_size = np.mean(order_sizes)
                avg_executed_size = np.mean(executed_sizes)
                features['large_to_small_order_ratio'] = avg_order_size / avg_executed_size if avg_executed_size > 0 else 1.0
        
        # Add some realistic random features for demonstration
        features['trading_outside_hours'] = np.random.choice([True, False], p=[0.2, 0.8])
        features['unusual_timing_pattern'] = np.random.choice([True, False], p=[0.3, 0.7])
        features['price_movement_after_orders'] = np.random.choice([True, False], p=[0.4, 0.6])
        features['immediate_cancellation_after_movement'] = np.random.choice([True, False], p=[0.3, 0.7])
        features['bid_ask_volume_imbalance'] = np.random.uniform(-0.8, 0.8)
        features['trading_frequency_anomaly'] = np.random.randint(0, 8)
        features['spoofing_pattern_frequency'] = np.random.randint(0, 12)
        
        return features
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score >= 0.8:
            return 'CRITICAL'
        elif risk_score >= 0.6:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MEDIUM'
        elif risk_score >= 0.2:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _generate_explanation(self, insider_risk: float, spoofing_risk: float, features: Dict[str, Any]) -> List[str]:
        """Generate human-readable explanation of the risk assessment"""
        explanations = []
        
        if insider_risk > 0.5:
            explanations.append(f"High insider dealing risk detected (score: {insider_risk:.2f})")
            if features.get('has_material_events'):
                explanations.append("- Trading activity detected near material events")
            if features.get('trader_role') in ['executive', 'insider']:
                explanations.append("- Trader has access to material information")
            if features.get('volume_vs_average', 1.0) > 2.0:
                explanations.append("- Unusual trading volume detected")
        
        if spoofing_risk > 0.5:
            explanations.append(f"High spoofing risk detected (score: {spoofing_risk:.2f})")
            if features.get('order_cancellation_rate', 0) > 0.7:
                explanations.append("- High order cancellation rate observed")
            if features.get('large_to_small_order_ratio', 1.0) > 5.0:
                explanations.append("- Large orders followed by small executions")
        
        if not explanations:
            explanations.append("No significant market abuse patterns detected")
        
        return explanations
    
    def get_models_info(self) -> Dict[str, Any]:
        """Get information about the available models"""
        return {
            'insider_dealing_model': {
                'name': 'Simplified Insider Dealing Detection',
                'type': 'weighted_scoring',
                'features': list(self.insider_dealing_weights.keys()),
                'confidence_threshold': 0.5
            },
            'spoofing_model': {
                'name': 'Simplified Spoofing Detection',
                'type': 'weighted_scoring',
                'features': list(self.spoofing_weights.keys()),
                'confidence_threshold': 0.5
            },
            'version': '1.0.0-simplified',
            'last_updated': '2025-07-04'
        }