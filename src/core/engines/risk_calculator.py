import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class RiskCalculator:
    """
    Risk calculation engine for overall market abuse risk assessment
    """
    
    def __init__(self):
        self.risk_weights = {
            'insider_dealing': 0.6,
            'spoofing': 0.4
        }
        
        self.contextual_factors = {
            'trader_role_multipliers': {
                'executive': 1.5,
                'board_member': 1.8,
                'senior_trader': 1.2,
                'trader': 1.0,
                'analyst': 1.1
            },
            'volume_multipliers': {
                'high': 1.3,
                'medium': 1.1,
                'low': 1.0
            },
            'timeframe_multipliers': {
                'intraday': 1.2,
                'daily': 1.0,
                'weekly': 0.9,
                'extended': 0.8
            }
        }
    
    def calculate_overall_risk(self, insider_score: Dict, spoofing_score: Dict, 
                             processed_data: Dict) -> float:
        """Calculate overall market abuse risk score"""
        try:
            # Extract base risk scores
            insider_risk = insider_score.get('overall_score', 0) if 'error' not in insider_score else 0
            spoofing_risk = spoofing_score.get('overall_score', 0) if 'error' not in spoofing_score else 0
            
            # Calculate weighted base score
            base_score = (
                insider_risk * self.risk_weights['insider_dealing'] +
                spoofing_risk * self.risk_weights['spoofing']
            )
            
            # Apply contextual multipliers
            contextual_multiplier = self._calculate_contextual_multiplier(processed_data)
            
            # Calculate final risk score
            overall_risk = min(base_score * contextual_multiplier, 1.0)
            
            logger.debug(f"Overall risk calculated: base={base_score:.3f}, "
                        f"multiplier={contextual_multiplier:.3f}, final={overall_risk:.3f}")
            
            return overall_risk
            
        except Exception as e:
            logger.error(f"Error calculating overall risk: {str(e)}")
            return 0.0
    
    def _calculate_contextual_multiplier(self, data: Dict) -> float:
        """Calculate contextual risk multiplier based on various factors"""
        multiplier = 1.0
        
        try:
            # Trader role multiplier
            trader_role = data.get('trader_info', {}).get('role', 'trader')
            role_multiplier = self.contextual_factors['trader_role_multipliers'].get(
                trader_role, 1.0
            )
            multiplier *= role_multiplier
            
            # Volume-based multiplier
            volume_category = self._categorize_volume(data)
            volume_multiplier = self.contextual_factors['volume_multipliers'].get(
                volume_category, 1.0
            )
            multiplier *= volume_multiplier
            
            # Timeframe multiplier
            timeframe = data.get('timeframe', 'daily')
            timeframe_multiplier = self.contextual_factors['timeframe_multipliers'].get(
                timeframe, 1.0
            )
            multiplier *= timeframe_multiplier
            
            # Market conditions multiplier
            market_multiplier = self._calculate_market_conditions_multiplier(data)
            multiplier *= market_multiplier
            
            # Behavioral pattern multiplier
            behavioral_multiplier = self._calculate_behavioral_multiplier(data)
            multiplier *= behavioral_multiplier
            
            return multiplier
            
        except Exception as e:
            logger.error(f"Error calculating contextual multiplier: {str(e)}")
            return 1.0
    
    def _categorize_volume(self, data: Dict) -> str:
        """Categorize trading volume as high, medium, or low"""
        try:
            current_volume = data.get('metrics', {}).get('total_volume', 0)
            historical_avg = data.get('historical_metrics', {}).get('avg_volume', 1000)
            
            if current_volume > historical_avg * 3:
                return 'high'
            elif current_volume > historical_avg * 1.5:
                return 'medium'
            else:
                return 'low'
                
        except Exception:
            return 'medium'
    
    def _calculate_market_conditions_multiplier(self, data: Dict) -> float:
        """Calculate multiplier based on market conditions"""
        try:
            market_data = data.get('market_data', {})
            volatility = market_data.get('volatility', 0.02)
            liquidity = market_data.get('liquidity', 0.5)
            
            # Higher volatility increases risk
            volatility_factor = 1.0 + (volatility * 5)  # Scale volatility impact
            
            # Lower liquidity increases risk
            liquidity_factor = 1.0 + (1.0 - liquidity) * 0.3
            
            # Combine factors
            multiplier = (volatility_factor + liquidity_factor) / 2
            
            # Cap the multiplier
            return min(max(multiplier, 0.5), 2.0)
            
        except Exception:
            return 1.0
    
    def _calculate_behavioral_multiplier(self, data: Dict) -> float:
        """Calculate multiplier based on behavioral patterns"""
        try:
            multiplier = 1.0
            
            # Insider indicators
            insider_indicators = data.get('insider_indicators', [])
            if len(insider_indicators) > 0:
                multiplier += len(insider_indicators) * 0.1
            
            # Pre-event trading
            pre_event_trading = data.get('metrics', {}).get('pre_event_trading', 0)
            if pre_event_trading > 0:
                multiplier += min(pre_event_trading * 0.05, 0.3)
            
            # Timing concentration
            timing_concentration = data.get('metrics', {}).get('timing_concentration', 0)
            if timing_concentration > 5:  # High frequency
                multiplier += 0.2
            
            # Order patterns
            cancellation_ratio = data.get('metrics', {}).get('cancellation_ratio', 0)
            if cancellation_ratio > 0.7:
                multiplier += 0.3
            
            return min(multiplier, 2.0)
            
        except Exception:
            return 1.0
    
    def calculate_risk_breakdown(self, insider_score: Dict, spoofing_score: Dict, 
                               processed_data: Dict) -> Dict:
        """Provide detailed risk breakdown for analysis"""
        try:
            breakdown = {
                'base_scores': {
                    'insider_dealing': insider_score.get('overall_score', 0) if 'error' not in insider_score else 0,
                    'spoofing': spoofing_score.get('overall_score', 0) if 'error' not in spoofing_score else 0
                },
                'weighted_scores': {},
                'contextual_factors': {},
                'overall_risk': 0.0
            }
            
            # Calculate weighted scores
            breakdown['weighted_scores']['insider_dealing'] = (
                breakdown['base_scores']['insider_dealing'] * 
                self.risk_weights['insider_dealing']
            )
            breakdown['weighted_scores']['spoofing'] = (
                breakdown['base_scores']['spoofing'] * 
                self.risk_weights['spoofing']
            )
            
            # Calculate contextual factors
            trader_role = processed_data.get('trader_info', {}).get('role', 'trader')
            breakdown['contextual_factors']['trader_role'] = {
                'role': trader_role,
                'multiplier': self.contextual_factors['trader_role_multipliers'].get(trader_role, 1.0)
            }
            
            volume_category = self._categorize_volume(processed_data)
            breakdown['contextual_factors']['volume'] = {
                'category': volume_category,
                'multiplier': self.contextual_factors['volume_multipliers'].get(volume_category, 1.0)
            }
            
            timeframe = processed_data.get('timeframe', 'daily')
            breakdown['contextual_factors']['timeframe'] = {
                'timeframe': timeframe,
                'multiplier': self.contextual_factors['timeframe_multipliers'].get(timeframe, 1.0)
            }
            
            breakdown['contextual_factors']['market_conditions'] = {
                'multiplier': self._calculate_market_conditions_multiplier(processed_data)
            }
            
            breakdown['contextual_factors']['behavioral_patterns'] = {
                'multiplier': self._calculate_behavioral_multiplier(processed_data)
            }
            
            # Calculate overall risk
            breakdown['overall_risk'] = self.calculate_overall_risk(
                insider_score, spoofing_score, processed_data
            )
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error calculating risk breakdown: {str(e)}")
            return {'error': str(e)}
    
    def get_risk_interpretation(self, risk_score: float) -> Dict:
        """Provide interpretation of risk score"""
        if risk_score >= 0.8:
            level = 'CRITICAL'
            description = 'Extremely high probability of market abuse'
            urgency = 'IMMEDIATE'
        elif risk_score >= 0.6:
            level = 'HIGH'
            description = 'High probability of market abuse requiring investigation'
            urgency = 'URGENT'
        elif risk_score >= 0.4:
            level = 'MEDIUM'
            description = 'Moderate probability of market abuse requiring monitoring'
            urgency = 'NORMAL'
        elif risk_score >= 0.2:
            level = 'LOW'
            description = 'Low probability of market abuse'
            urgency = 'ROUTINE'
        else:
            level = 'MINIMAL'
            description = 'Minimal probability of market abuse'
            urgency = 'NONE'
        
        return {
            'risk_level': level,
            'description': description,
            'urgency': urgency,
            'score': risk_score,
            'percentage': f"{risk_score * 100:.1f}%"
        }
    
    def calculate_confidence_interval(self, insider_score: Dict, spoofing_score: Dict) -> Dict:
        """Calculate confidence intervals for risk assessment"""
        try:
            # Simple confidence calculation based on evidence strength
            insider_confidence = self._calculate_score_confidence(insider_score)
            spoofing_confidence = self._calculate_score_confidence(spoofing_score)
            
            # Overall confidence is weighted average
            overall_confidence = (
                insider_confidence * self.risk_weights['insider_dealing'] +
                spoofing_confidence * self.risk_weights['spoofing']
            )
            
            return {
                'insider_dealing_confidence': insider_confidence,
                'spoofing_confidence': spoofing_confidence,
                'overall_confidence': overall_confidence,
                'confidence_level': self._interpret_confidence(overall_confidence)
            }
            
        except Exception as e:
            logger.error(f"Error calculating confidence interval: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_score_confidence(self, score_dict: Dict) -> float:
        """Calculate confidence for individual score"""
        if 'error' in score_dict:
            return 0.0
        
        # Confidence based on probability distribution
        high_risk = score_dict.get('high_risk', 0)
        medium_risk = score_dict.get('medium_risk', 0)
        low_risk = score_dict.get('low_risk', 0)
        
        # Higher confidence when probabilities are more concentrated
        entropy = 0
        for prob in [high_risk, medium_risk, low_risk]:
            if prob > 0:
                entropy -= prob * np.log2(prob)
        
        # Normalize entropy (max entropy for 3 categories is log2(3))
        max_entropy = np.log2(3)
        confidence = 1.0 - (entropy / max_entropy)
        
        return max(0.0, min(1.0, confidence))
    
    def _interpret_confidence(self, confidence: float) -> str:
        """Interpret confidence level"""
        if confidence >= 0.8:
            return 'HIGH'
        elif confidence >= 0.6:
            return 'MEDIUM'
        elif confidence >= 0.4:
            return 'LOW'
        else:
            return 'VERY_LOW'