"""
Data Quality Sufficiency Index (DQSI) - Main Scoring Engine

This module orchestrates the DQSI scoring process using strategy-based configurations
and metadata-driven calculations. It provides the main interface for generating
dqsi_score and dqsi_confidence_index for alerts and cases.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from .dq_strategy_base import DQScoringStrategy, DQSIOutput, DQConfig, KDEResult
from .fallback_dq_strategy import FallbackDQScoringStrategy
from .role_aware_dq_strategy import RoleAwareDQScoringStrategy

logger = logging.getLogger(__name__)


class DataQualitySufficiencyIndex:
    """
    Main DQSI scoring engine
    
    Provides KDE-level scoring, strategy-based configurations, and metadata-driven
    calculations for surveillance platform alerts and cases.
    """
    
    def __init__(self, config: Optional[DQConfig] = None):
        """
        Initialize DQSI scoring engine
        
        Args:
            config: Configuration object (defaults to standard config)
        """
        self.config = config or DQConfig()
        self.strategy = self._create_strategy()
        
        logger.info(f"DQSI engine initialized with strategy: {self.strategy.get_strategy_name()}")
    
    def _create_strategy(self) -> DQScoringStrategy:
        """Create scoring strategy based on configuration"""
        strategy_name = self.config.dq_strategy
        
        if strategy_name == 'fallback':
            return FallbackDQScoringStrategy(self.config)
        elif strategy_name == 'role_aware':
            return RoleAwareDQScoringStrategy(self.config)
        else:
            logger.warning(f"Unknown strategy '{strategy_name}', falling back to 'fallback' strategy")
            return FallbackDQScoringStrategy(self.config)
    
    def calculate_dqsi(self, data: Dict[str, Any], 
                      metadata: Optional[Dict[str, Any]] = None) -> DQSIOutput:
        """
        Calculate complete DQSI score and confidence index
        
        Args:
            data: Input data containing KDEs
            metadata: Optional metadata (role info, reference data, etc.)
            
        Returns:
            Complete DQSI output for injection into alerts/cases
        """
        try:
            # Score individual KDEs using selected strategy
            kde_results = self.strategy.score_kdes(data, metadata)
            
            # Calculate overall DQSI score
            dqsi_score = self.strategy.calculate_dqsi_score(kde_results)
            
            # Calculate confidence index
            confidence_index, confidence_note = self.strategy.calculate_confidence_index(
                kde_results, dqsi_score
            )
            
            # Calculate dimension sub-scores
            sub_scores = self.strategy.calculate_dimension_scores(kde_results)
            
            # Extract critical KDEs missing
            critical_kdes_missing = [
                kde.kde_name for kde in kde_results 
                if kde.kde_name in self.config.critical_kdes and kde.score == 0.0
            ]
            
            # Build KDE weights dictionary
            kde_weights = {
                kde.kde_name: kde.risk_weight for kde in kde_results
            }
            
            # Create output
            output = DQSIOutput(
                dqsi_score=dqsi_score,
                dqsi_confidence_index=confidence_index,
                dqsi_mode=self.strategy.get_strategy_name(),
                dqsi_critical_kdes_missing=critical_kdes_missing,
                dqsi_sub_scores=sub_scores,
                dqsi_kde_weights=kde_weights,
                dqsi_confidence_note=confidence_note,
                kde_results=kde_results
            )
            
            logger.info(f"DQSI calculated: score={dqsi_score:.3f}, confidence={confidence_index:.3f}")
            
            return output
            
        except Exception as e:
            logger.error(f"Error calculating DQSI: {e}")
            return self._create_error_output(str(e))
    
    def calculate_dqsi_for_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate DQSI specifically for alert injection
        
        Args:
            alert_data: Alert data containing KDEs and metadata
            
        Returns:
            Dictionary with DQSI fields for alert injection
        """
        # Extract metadata from alert structure
        metadata = {
            'role': alert_data.get('producer_role', 'producer'),
            'typology': alert_data.get('typology', 'unknown'),
            'reference_data': alert_data.get('reference_data', {}),
            'reconciliation_data': alert_data.get('reconciliation_data', {}),
            'baseline_volume': alert_data.get('baseline_volume'),
            'current_volume': alert_data.get('current_volume')
        }
        
        # Extract KDE data
        kde_data = self._extract_kde_data(alert_data)
        
        # Calculate DQSI
        dqsi_output = self.calculate_dqsi(kde_data, metadata)
        
        # Return fields for alert injection
        return {
            'dqsi_score': dqsi_output.dqsi_score,
            'dqsi_confidence_index': dqsi_output.dqsi_confidence_index,
            'dqsi_mode': dqsi_output.dqsi_mode,
            'dqsi_critical_kdes_missing': dqsi_output.dqsi_critical_kdes_missing,
            'dqsi_sub_scores': dqsi_output.dqsi_sub_scores,
            'dqsi_kde_weights': dqsi_output.dqsi_kde_weights,
            'dqsi_confidence_note': dqsi_output.dqsi_confidence_note
        }
    
    def calculate_dqsi_for_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate DQSI specifically for case injection
        
        Args:
            case_data: Case data containing multiple alerts and KDEs
            
        Returns:
            Dictionary with DQSI fields for case injection
        """
        # For cases, we might aggregate across multiple alerts
        alerts = case_data.get('alerts', [])
        
        if not alerts:
            # Single case without sub-alerts
            return self.calculate_dqsi_for_alert(case_data)
        
        # Aggregate DQSI across multiple alerts
        all_kde_results = []
        all_metadata = []
        
        for alert in alerts:
            alert_kde_data = self._extract_kde_data(alert)
            alert_metadata = {
                'role': alert.get('producer_role', 'producer'),
                'reference_data': alert.get('reference_data', {}),
                'reconciliation_data': alert.get('reconciliation_data', {})
            }
            
            kde_results = self.strategy.score_kdes(alert_kde_data, alert_metadata)
            all_kde_results.extend(kde_results)
            all_metadata.append(alert_metadata)
        
        # Calculate aggregated scores
        if all_kde_results:
            dqsi_score = self.strategy.calculate_dqsi_score(all_kde_results)
            confidence_index, confidence_note = self.strategy.calculate_confidence_index(
                all_kde_results, dqsi_score
            )
            sub_scores = self.strategy.calculate_dimension_scores(all_kde_results)
            
            critical_kdes_missing = [
                kde.kde_name for kde in all_kde_results 
                if kde.kde_name in self.config.critical_kdes and kde.score == 0.0
            ]
            
            kde_weights = {
                kde.kde_name: kde.risk_weight for kde in all_kde_results
            }
        else:
            dqsi_score = 0.0
            confidence_index = 0.0
            confidence_note = "No KDEs available for case-level scoring"
            sub_scores = {}
            critical_kdes_missing = []
            kde_weights = {}
        
        return {
            'dqsi_score': dqsi_score,
            'dqsi_confidence_index': confidence_index,
            'dqsi_mode': self.strategy.get_strategy_name(),
            'dqsi_critical_kdes_missing': list(set(critical_kdes_missing)),
            'dqsi_sub_scores': sub_scores,
            'dqsi_kde_weights': kde_weights,
            'dqsi_confidence_note': confidence_note,
            'case_alert_count': len(alerts)
        }
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about current strategy configuration"""
        return {
            'strategy_name': self.strategy.get_strategy_name(),
            'strategy_mode': self.config.dq_strategy,
            'dimensions': self.config.dimensions,
            'kde_risk_tiers': self.config.kde_risk_tiers,
            'critical_kdes': self.config.critical_kdes,
            'critical_cap': self.config.dqsi_critical_cap,
            'synthetic_kdes': list(self.config.synthetic_kdes.keys())
        }
    
    def validate_kde_coverage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate KDE coverage against expected KDEs
        
        Args:
            data: Input data
            
        Returns:
            Coverage analysis
        """
        expected_kdes = set(self.config.kde_risk_tiers.keys())
        present_kdes = set(data.keys())
        
        missing_kdes = expected_kdes - present_kdes
        unexpected_kdes = present_kdes - expected_kdes
        
        # Categorize missing KDEs by risk tier
        missing_by_tier = {'high': [], 'medium': [], 'low': []}
        for kde in missing_kdes:
            tier = self.config.kde_risk_tiers.get(kde, 'low')
            missing_by_tier[tier].append(kde)
        
        coverage_ratio = len(present_kdes) / len(expected_kdes) if expected_kdes else 0.0
        
        return {
            'coverage_ratio': coverage_ratio,
            'expected_kdes': list(expected_kdes),
            'present_kdes': list(present_kdes),
            'missing_kdes': list(missing_kdes),
            'missing_by_tier': missing_by_tier,
            'unexpected_kdes': list(unexpected_kdes),
            'critical_missing': [kde for kde in missing_kdes if kde in self.config.critical_kdes]
        }
    
    def simulate_dqsi_impact(self, data: Dict[str, Any], 
                           kde_modifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate impact of KDE modifications on DQSI score
        
        Args:
            data: Original data
            kde_modifications: KDE modifications to simulate
            
        Returns:
            Before/after comparison
        """
        # Calculate original DQSI
        original_output = self.calculate_dqsi(data)
        
        # Apply modifications
        modified_data = data.copy()
        modified_data.update(kde_modifications)
        
        # Calculate modified DQSI
        modified_output = self.calculate_dqsi(modified_data)
        
        # Calculate impact
        score_delta = modified_output.dqsi_score - original_output.dqsi_score
        confidence_delta = modified_output.dqsi_confidence_index - original_output.dqsi_confidence_index
        
        return {
            'original_score': original_output.dqsi_score,
            'modified_score': modified_output.dqsi_score,
            'score_delta': score_delta,
            'original_confidence': original_output.dqsi_confidence_index,
            'modified_confidence': modified_output.dqsi_confidence_index,
            'confidence_delta': confidence_delta,
            'modifications_applied': kde_modifications,
            'impact_analysis': self._analyze_impact(score_delta, confidence_delta)
        }
    
    def get_improvement_recommendations(self, dqsi_output: DQSIOutput) -> List[Dict[str, Any]]:
        """
        Generate improvement recommendations based on DQSI results
        
        Args:
            dqsi_output: DQSI calculation results
            
        Returns:
            List of improvement recommendations
        """
        recommendations = []
        
        # Analyze each KDE result
        for kde_result in dqsi_output.kde_results:
            if kde_result.score < 0.8:  # Below good threshold
                recommendation = {
                    'kde_name': kde_result.kde_name,
                    'current_score': kde_result.score,
                    'risk_tier': kde_result.risk_tier,
                    'dimension': kde_result.dimension,
                    'priority': self._get_recommendation_priority(kde_result),
                    'suggestions': self._get_kde_specific_suggestions(kde_result),
                    'expected_impact': self._estimate_improvement_impact(kde_result)
                }
                recommendations.append(recommendation)
        
        # Sort by priority and impact
        recommendations.sort(key=lambda x: (
            x['priority'] == 'high',
            x['risk_tier'] == 'high',
            -x['expected_impact']
        ), reverse=True)
        
        return recommendations
    
    def _extract_kde_data(self, alert_or_case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract KDE data from alert or case structure"""
        kde_data = {}
        
        # Common KDE fields that might be in alert/case data
        kde_fields = list(self.config.kde_risk_tiers.keys())
        
        for field in kde_fields:
            if field in alert_or_case_data:
                kde_data[field] = alert_or_case_data[field]
        
        # Also check nested structures
        if 'trade_data' in alert_or_case_data:
            trade_data = alert_or_case_data['trade_data']
            for field in kde_fields:
                if field in trade_data:
                    kde_data[field] = trade_data[field]
        
        if 'order_data' in alert_or_case_data:
            order_data = alert_or_case_data['order_data']
            for field in kde_fields:
                if field in order_data:
                    kde_data[field] = order_data[field]
        
        return kde_data
    
    def _create_error_output(self, error_message: str) -> DQSIOutput:
        """Create error output when DQSI calculation fails"""
        return DQSIOutput(
            dqsi_score=0.0,
            dqsi_confidence_index=0.0,
            dqsi_mode=self.strategy.get_strategy_name(),
            dqsi_critical_kdes_missing=[],
            dqsi_sub_scores={},
            dqsi_kde_weights={},
            dqsi_confidence_note=f"Error calculating DQSI: {error_message}",
            kde_results=[]
        )
    
    def _analyze_impact(self, score_delta: float, confidence_delta: float) -> str:
        """Analyze impact of modifications"""
        if abs(score_delta) < 0.01 and abs(confidence_delta) < 0.01:
            return "minimal_impact"
        elif score_delta > 0.1 or confidence_delta > 0.1:
            return "significant_improvement"
        elif score_delta < -0.1 or confidence_delta < -0.1:
            return "significant_degradation"
        elif score_delta > 0 or confidence_delta > 0:
            return "moderate_improvement"
        else:
            return "moderate_degradation"
    
    def _get_recommendation_priority(self, kde_result: KDEResult) -> str:
        """Get priority level for improvement recommendation"""
        if kde_result.kde_name in self.config.critical_kdes and kde_result.score < 0.5:
            return "critical"
        elif kde_result.risk_tier == "high" and kde_result.score < 0.6:
            return "high"
        elif kde_result.score < 0.4:
            return "high"
        elif kde_result.score < 0.7:
            return "medium"
        else:
            return "low"
    
    def _get_kde_specific_suggestions(self, kde_result: KDEResult) -> List[str]:
        """Get specific improvement suggestions for a KDE"""
        suggestions = []
        
        kde_name = kde_result.kde_name
        score = kde_result.score
        
        if score == 0.0:
            suggestions.append(f"Ensure {kde_name} is captured and populated")
            suggestions.append(f"Check data source connectivity for {kde_name}")
        
        elif score < 0.6:
            suggestions.append(f"Improve data quality validation for {kde_name}")
            suggestions.append(f"Review data transformation logic for {kde_name}")
        
        if kde_result.imputed:
            suggestions.append(f"Reduce dependency on imputed values for {kde_name}")
            suggestions.append(f"Improve upstream data capture for {kde_name}")
        
        # Dimension-specific suggestions
        if kde_result.dimension == "timeliness":
            suggestions.append("Implement real-time data processing")
            suggestions.append("Add data freshness monitoring")
        
        elif kde_result.dimension == "completeness":
            suggestions.append("Add mandatory field validation")
            suggestions.append("Implement data completeness checks")
        
        elif kde_result.dimension == "accuracy":
            suggestions.append("Add reference data validation")
            suggestions.append("Implement reconciliation processes")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _estimate_improvement_impact(self, kde_result: KDEResult) -> float:
        """Estimate potential improvement impact"""
        # Impact is based on risk weight and current score gap
        max_score = 1.0
        score_gap = max_score - kde_result.score
        impact = score_gap * kde_result.risk_weight
        
        # Normalize to 0-1 scale
        max_possible_impact = max_score * max(self.config.risk_weights.values())
        normalized_impact = impact / max_possible_impact if max_possible_impact > 0 else 0.0
        
        return normalized_impact