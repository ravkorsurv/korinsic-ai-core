"""
KDE-First Data Quality Calculator

Implements the new 2-tier, 7-dimension data quality framework using KDE-first scoring
rather than dimension averaging. Each KDE gets individual quality assessment across
applicable dimensions, then aggregated using risk and tier weights.

Framework:
- Tier 1 (Foundational): completeness, coverage, conformity, timeliness (weight: 1.0)
- Tier 2 (Enhanced): accuracy, uniqueness, consistency (weight: 0.75)
- Risk Weights: high=3, medium=2, low=1
- Synthetic KDEs: always weight=3
"""

import yaml
import numpy as np
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import redis
import json

logger = logging.getLogger(__name__)

class KDEFirstDQCalculator:
    """
    KDE-First Data Quality calculator implementing 2-tier, 7-dimension framework.
    
    This replaces the old dimension-averaged approach with KDE-specific scoring
    that respects both risk levels and dimension tiers.
    """
    
    def __init__(self, config_path: str = "config/dq_config.yaml", redis_client=None):
        """
        Initialize KDE-First DQ calculator.
        
        Args:
            config_path: Path to DQ configuration YAML
            redis_client: Redis client for golden source lookups
        """
        self.config = self._load_config(config_path)
        self.redis_client = redis_client
        self._validate_config()
        
        logger.info("KDE-First DQ calculator initialized with 2-tier framework")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return self._get_default_config()
    
    def _validate_config(self):
        """Validate configuration structure."""
        required_sections = [
            'tier_weights', 'risk_weights', 'kde_risk', 'dimension_tiers',
            'timeliness_buckets', 'coverage_scoring', 'role_kde_scope'
        ]
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
    
    def calculate_dqsi(self, 
                      evidence: Dict[str, Any],
                      baseline_data: Dict[str, Any] = None,
                      user_role: str = "analyst",
                      alert_timestamp: datetime = None) -> Dict[str, Any]:
        """
        Calculate DQSI score using KDE-first approach.
        
        Args:
            evidence: Raw evidence data with KDE values
            baseline_data: Historical baseline for coverage calculations
            user_role: User role for KDE scope filtering
            alert_timestamp: Alert timestamp for timeliness calculations
            
        Returns:
            Dictionary containing DQSI score, trust bucket, and detailed breakdown
        """
        try:
            # Filter KDEs based on user role
            applicable_kdes = self._get_applicable_kdes(evidence, user_role)
            
            # Calculate scores for each KDE across all applicable dimensions
            kde_scores = {}
            synthetic_scores = {}
            
            for kde_name in applicable_kdes:
                kde_value = evidence.get(kde_name)
                kde_scores[kde_name] = self._calculate_kde_scores(kde_name, kde_value, evidence)
            
            # Calculate synthetic KDE scores (timeliness, coverage)
            synthetic_scores['timeliness'] = self._calculate_timeliness_score(evidence, alert_timestamp)
            synthetic_scores['coverage'] = self._calculate_coverage_score(evidence, baseline_data)
            
            # Aggregate final DQSI score using weighted average
            dqsi_score, score_breakdown = self._aggregate_dqsi_score(kde_scores, synthetic_scores)
            
            # Determine trust bucket
            trust_bucket = self._get_trust_bucket(dqsi_score)
            
            # Include legacy score for backward compatibility
            legacy_score = self._calculate_legacy_score(kde_scores, synthetic_scores) if self.config.get('legacy_support', {}).get('enabled', False) else None
            
            result = {
                'dqsi_score': round(dqsi_score, 3),
                'dqsi_trust_bucket': trust_bucket,
                'dq_framework': 'kde_first_v2',
                'user_role': user_role,
                'kde_scores': {k: {dim: round(v, 3) for dim, v in scores.items()} for k, scores in kde_scores.items()},
                'synthetic_scores': {k: round(v, 3) for k, v in synthetic_scores.items()},
                'score_breakdown': score_breakdown,
                'applicable_kdes': applicable_kdes,
                'dimension_summary': self._get_dimension_summary(kde_scores, synthetic_scores),
                'quality_metadata': {
                    'total_kdes_assessed': len(applicable_kdes),
                    'synthetic_kdes_count': len(synthetic_scores),
                    'foundational_score': score_breakdown.get('foundational_weighted_score', 0.0),
                    'enhanced_score': score_breakdown.get('enhanced_weighted_score', 0.0)
                }
            }
            
            if legacy_score is not None:
                result['legacy_dq_score'] = round(legacy_score, 3)
            
            logger.info(f"KDE-First DQSI calculated: score={dqsi_score:.3f}, "
                       f"trust_bucket={trust_bucket}, kdes_assessed={len(applicable_kdes)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in KDE-First DQSI calculation: {e}")
            return self._get_default_result(user_role)
    
    def _get_applicable_kdes(self, evidence: Dict[str, Any], user_role: str) -> List[str]:
        """Get list of KDEs applicable for the given user role."""
        role_scope = self.config['role_kde_scope'].get(user_role, [])
        
        # Filter to only KDEs that exist in evidence and are in role scope
        applicable = [kde for kde in role_scope if kde in evidence]
        
        logger.debug(f"Role {user_role}: {len(applicable)} applicable KDEs out of {len(role_scope)} in scope")
        return applicable
    
    def _calculate_kde_scores(self, kde_name: str, kde_value: Any, evidence: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate quality scores for a single KDE across all applicable dimensions.
        
        Args:
            kde_name: Name of the KDE
            kde_value: Value of the KDE
            evidence: Full evidence dictionary for context
            
        Returns:
            Dictionary mapping dimension names to scores (0.0 to 1.0)
        """
        scores = {}
        
        # Foundational dimensions
        scores['completeness'] = self._score_completeness(kde_value)
        scores['conformity'] = self._score_conformity(kde_name, kde_value)
        
        # Enhanced dimensions
        scores['accuracy'] = self._score_accuracy(kde_name, kde_value)
        scores['uniqueness'] = self._score_uniqueness(kde_name, kde_value, evidence)
        scores['consistency'] = self._score_consistency(kde_name, kde_value, evidence)
        
        return scores
    
    def _score_completeness(self, value: Any) -> float:
        """Score completeness dimension (null values, empty indicators)."""
        if value is None:
            return 0.0
        if isinstance(value, str) and (value == '' or value.lower() in ['null', 'none', 'unknown', 'n/a']):
            return 0.0
        if isinstance(value, (int, float)) and np.isnan(value):
            return 0.0
        return 1.0
    
    def _score_conformity(self, kde_name: str, value: Any) -> float:
        """Score conformity dimension (length, range, min/max)."""
        if value is None:
            return 0.0
        
        conformity_rules = self.config.get('conformity_rules', {}).get(kde_name, {})
        if not conformity_rules:
            return 1.0  # No rules = assume conformant
        
        score = 1.0
        
        # Length check
        if 'length' in conformity_rules and isinstance(value, str):
            length_rule = conformity_rules['length']
            min_len = length_rule.get('min', 0)
            max_len = length_rule.get('max', float('inf'))
            if not (min_len <= len(value) <= max_len):
                score = 0.0
        
        # Range check
        if 'range' in conformity_rules and isinstance(value, (int, float)):
            range_rule = conformity_rules['range']
            min_val = range_rule.get('min', float('-inf'))
            max_val = range_rule.get('max', float('inf'))
            if not (min_val <= value <= max_val):
                score = 0.0
        
        # Pattern check
        if 'pattern' in conformity_rules and isinstance(value, str):
            pattern = conformity_rules['pattern']
            if not re.match(pattern, value):
                score = 0.0
        
        return score
    
    def _score_accuracy(self, kde_name: str, value: Any) -> float:
        """Score accuracy dimension (precision, validity)."""
        if value is None:
            return 0.0
        
        accuracy_rules = self.config.get('accuracy_rules', {})
        precision_score = self._score_precision(kde_name, value, accuracy_rules.get('precision_rules', {}))
        validity_score = self._score_validity(kde_name, value, accuracy_rules.get('validity_rules', {}))
        
        # Combined score: (precision + validity) / 2
        return (precision_score + validity_score) / 2.0
    
    def _score_precision(self, kde_name: str, value: Any, precision_rules: Dict[str, Any]) -> float:
        """Score precision subdimension."""
        if kde_name not in precision_rules:
            return 1.0  # No rules = assume precise
        
        expected_precision = precision_rules[kde_name]
        
        if isinstance(value, float):
            # Check decimal places
            decimal_places = len(str(value).split('.')[-1]) if '.' in str(value) else 0
            return 1.0 if decimal_places <= expected_precision else 0.0
        
        return 1.0  # Non-numeric values pass precision check
    
    def _score_validity(self, kde_name: str, value: Any, validity_rules: Dict[str, Any]) -> float:
        """Score validity subdimension."""
        if kde_name not in validity_rules:
            return 1.0  # No rules = assume valid
        
        validity_rule = validity_rules[kde_name]
        reference_source = validity_rule['reference_source']
        
        # Get reference data
        reference_data = self._get_reference_data(reference_source)
        if not reference_data:
            return 0.5  # Can't validate = moderate score
        
        return 1.0 if value in reference_data else 0.0
    
    def _score_uniqueness(self, kde_name: str, value: Any, evidence: Dict[str, Any]) -> float:
        """Score uniqueness dimension (duplicate detection, key violations)."""
        if value is None:
            return 0.0
        
        # Simple uniqueness check within current evidence
        # In practice, this would check against historical data or within batch
        max_duplicate_rate = self.config.get('max_duplicate_rate', 0.02)
        
        # For now, return 1.0 (unique) unless we implement historical duplicate checking
        # This would be enhanced with actual duplicate detection logic
        return 1.0
    
    def _score_consistency(self, kde_name: str, value: Any, evidence: Dict[str, Any]) -> float:
        """Score consistency dimension (golden source matching)."""
        if value is None:
            return 0.0
        
        # Find applicable golden source mappings
        consistency_score = 1.0
        golden_sources = self.config.get('golden_sources', {})
        
        for source_name, source_config in golden_sources.items():
            if kde_name in source_config.get('fields', []):
                # Perform consistency check against golden source
                reference_value = self._lookup_golden_source(source_name, kde_name, value, evidence)
                if reference_value is not None:
                    consistency_score = 1.0 if value == reference_value else 0.0
                    break
        
        return consistency_score
    
    def _calculate_timeliness_score(self, evidence: Dict[str, Any], alert_timestamp: datetime = None) -> float:
        """Calculate timeliness synthetic KDE score."""
        if alert_timestamp is None:
            alert_timestamp = datetime.now()
        
        # Find the most critical timestamp field
        timestamp_fields = ['trade_date', 'timestamp', 'event_timestamp', 'created_at']
        most_delayed_hours = 0
        
        for field in timestamp_fields:
            if field in evidence:
                try:
                    field_timestamp = evidence[field]
                    if isinstance(field_timestamp, str):
                        field_timestamp = datetime.fromisoformat(field_timestamp)
                    elif isinstance(field_timestamp, (int, float)):
                        field_timestamp = datetime.fromtimestamp(field_timestamp)
                    
                    delay_hours = (alert_timestamp - field_timestamp).total_seconds() / 3600
                    most_delayed_hours = max(most_delayed_hours, delay_hours)
                except Exception as e:
                    logger.warning(f"Error parsing timestamp field {field}: {e}")
                    continue
        
        # Map delay to score using configured buckets
        return self._map_delay_to_score(most_delayed_hours)
    
    def _map_delay_to_score(self, delay_hours: float) -> float:
        """Map delay in hours to timeliness score using configured buckets."""
        buckets = self.config.get('timeliness_buckets', [])
        
        for bucket in buckets:
            if delay_hours <= bucket['max_hours']:
                return bucket['score']
        
        return 0.3  # Default for delays beyond all buckets
    
    def _calculate_coverage_score(self, evidence: Dict[str, Any], baseline_data: Dict[str, Any] = None) -> float:
        """Calculate coverage synthetic KDE score based on volume/value vs baseline."""
        if not baseline_data:
            return 0.0  # No baseline = score 0.0
        
        # Calculate current volume/value metrics
        current_volume = len(evidence)
        current_value = sum(float(v) for v in evidence.values() if isinstance(v, (int, float)))
        
        # Get baseline metrics
        baseline_volume = baseline_data.get('volume', 0)
        baseline_value = baseline_data.get('value', 0)
        
        if baseline_volume == 0 and baseline_value == 0:
            return 0.0
        
        # Calculate drop percentages
        volume_drop = max(0, (baseline_volume - current_volume) / baseline_volume * 100) if baseline_volume > 0 else 0
        value_drop = max(0, (baseline_value - current_value) / baseline_value * 100) if baseline_value > 0 else 0
        
        # Use the worse drop percentage
        max_drop = max(volume_drop, value_drop)
        
        # Map drop to score using configured buckets
        return self._map_coverage_drop_to_score(max_drop)
    
    def _map_coverage_drop_to_score(self, drop_percent: float) -> float:
        """Map coverage drop percentage to score using configured buckets."""
        coverage_scoring = self.config.get('coverage_scoring', [])
        
        for bucket in coverage_scoring:
            if drop_percent <= bucket['max_drop_percent']:
                return bucket['score']
        
        return 0.25  # Default for drops beyond all buckets
    
    def _aggregate_dqsi_score(self, kde_scores: Dict[str, Dict[str, float]], 
                             synthetic_scores: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """
        Aggregate final DQSI score using weighted average formula:
        dqsi_score = sum(kde_score * risk_weight * tier_weight) / sum(risk_weight * tier_weight)
        """
        total_weighted_score = 0.0
        total_weights = 0.0
        
        # Breakdown tracking
        foundational_score = 0.0
        foundational_weights = 0.0
        enhanced_score = 0.0
        enhanced_weights = 0.0
        
        # Process real KDEs
        for kde_name, dimension_scores in kde_scores.items():
            kde_risk = self.config['kde_risk'].get(kde_name, 'medium')
            risk_weight = self.config['risk_weights'][kde_risk]
            
            for dimension, score in dimension_scores.items():
                tier = self.config['dimension_tiers'][dimension]
                tier_weight = self.config['tier_weights'][tier]
                
                weighted_score = score * risk_weight * tier_weight
                weight = risk_weight * tier_weight
                
                total_weighted_score += weighted_score
                total_weights += weight
                
                # Track by tier
                if tier == 'foundational':
                    foundational_score += weighted_score
                    foundational_weights += weight
                else:
                    enhanced_score += weighted_score
                    enhanced_weights += weight
        
        # Process synthetic KDEs (always high risk weight)
        synthetic_weight = self.config['synthetic_kde_weight']
        for synthetic_name, score in synthetic_scores.items():
            # Synthetic KDEs are foundational tier
            tier_weight = self.config['tier_weights']['foundational']
            
            weighted_score = score * synthetic_weight * tier_weight
            weight = synthetic_weight * tier_weight
            
            total_weighted_score += weighted_score
            total_weights += weight
            
            foundational_score += weighted_score
            foundational_weights += weight
        
        # Calculate final score
        final_score = total_weighted_score / total_weights if total_weights > 0 else 0.0
        
        # Prepare breakdown
        breakdown = {
            'total_weighted_score': total_weighted_score,
            'total_weights': total_weights,
            'foundational_weighted_score': foundational_score / foundational_weights if foundational_weights > 0 else 0.0,
            'enhanced_weighted_score': enhanced_score / enhanced_weights if enhanced_weights > 0 else 0.0,
            'foundational_contribution': (foundational_score / total_weighted_score * 100) if total_weighted_score > 0 else 0.0,
            'enhanced_contribution': (enhanced_score / total_weighted_score * 100) if total_weighted_score > 0 else 0.0
        }
        
        return final_score, breakdown
    
    def _get_trust_bucket(self, dqsi_score: float) -> str:
        """Map DQSI score to trust bucket."""
        thresholds = self.config.get('trust_bucket_thresholds', {'high': 0.85, 'moderate': 0.65})
        
        if dqsi_score >= thresholds['high']:
            return "High"
        elif dqsi_score >= thresholds['moderate']:
            return "Moderate"
        else:
            return "Low"
    
    def _get_dimension_summary(self, kde_scores: Dict[str, Dict[str, float]], 
                              synthetic_scores: Dict[str, float]) -> Dict[str, Any]:
        """Generate summary statistics by dimension."""
        dimension_stats = defaultdict(list)
        
        # Collect scores by dimension
        for kde_name, scores in kde_scores.items():
            for dimension, score in scores.items():
                dimension_stats[dimension].append(score)
        
        # Add synthetic scores
        for synthetic_name, score in synthetic_scores.items():
            dimension_stats[synthetic_name].append(score)
        
        # Calculate summary statistics
        summary = {}
        for dimension, scores in dimension_stats.items():
            summary[dimension] = {
                'average': round(np.mean(scores), 3),
                'min': round(min(scores), 3),
                'max': round(max(scores), 3),
                'count': len(scores)
            }
        
        return summary
    
    def _get_reference_data(self, reference_source: str) -> List[Any]:
        """Get reference data for validity checks."""
        golden_sources = self.config.get('golden_sources', {})
        
        if reference_source in golden_sources:
            source_config = golden_sources[reference_source]
            if source_config['source_type'] == 'static':
                return source_config.get('values', [])
            # For Redis/DB sources, would implement lookup here
        
        return []
    
    def _lookup_golden_source(self, source_name: str, kde_name: str, value: Any, 
                             evidence: Dict[str, Any]) -> Any:
        """Lookup value in golden source for consistency checking."""
        # This would implement actual golden source lookups
        # For now, return None (no reference data available)
        return None
    
    def _calculate_legacy_score(self, kde_scores: Dict[str, Dict[str, float]], 
                               synthetic_scores: Dict[str, float]) -> float:
        """Calculate legacy DQ score for backward compatibility."""
        if not self.config.get('legacy_support', {}).get('enabled', False):
            return None
        
        # Simple average of all dimension scores (old method)
        all_scores = []
        for scores in kde_scores.values():
            all_scores.extend(scores.values())
        all_scores.extend(synthetic_scores.values())
        
        return np.mean(all_scores) if all_scores else 0.0
    
    def _get_default_result(self, user_role: str) -> Dict[str, Any]:
        """Get default result when calculation fails."""
        return {
            'dqsi_score': 0.0,
            'dqsi_trust_bucket': 'Low',
            'dq_framework': 'kde_first_v2',
            'user_role': user_role,
            'kde_scores': {},
            'synthetic_scores': {'timeliness': 0.0, 'coverage': 0.0},
            'score_breakdown': {
                'total_weighted_score': 0.0,
                'total_weights': 0.0,
                'foundational_weighted_score': 0.0,
                'enhanced_weighted_score': 0.0
            },
            'applicable_kdes': [],
            'dimension_summary': {},
            'quality_metadata': {
                'total_kdes_assessed': 0,
                'synthetic_kdes_count': 2,
                'foundational_score': 0.0,
                'enhanced_score': 0.0
            },
            'error': 'Calculation failed'
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when file loading fails."""
        return {
            'tier_weights': {'foundational': 1.0, 'enhanced': 0.75},
            'risk_weights': {'high': 3, 'medium': 2, 'low': 1},
            'synthetic_kde_weight': 3,
            'kde_risk': {'trader_id': 'high', 'notional': 'medium', 'product_code': 'low'},
            'dimension_tiers': {
                'completeness': 'foundational', 'coverage': 'foundational',
                'conformity': 'foundational', 'timeliness': 'foundational',
                'accuracy': 'enhanced', 'uniqueness': 'enhanced', 'consistency': 'enhanced'
            },
            'timeliness_buckets': [
                {'max_hours': 1, 'score': 1.0},
                {'max_hours': 24, 'score': 0.75},
                {'max_hours': 999999, 'score': 0.3}
            ],
            'coverage_scoring': [
                {'max_drop_percent': 10, 'score': 1.0},
                {'max_drop_percent': 50, 'score': 0.5},
                {'max_drop_percent': 100, 'score': 0.25}
            ],
            'role_kde_scope': {
                'analyst': ['trader_id', 'notional', 'price']
            },
            'trust_bucket_thresholds': {'high': 0.85, 'moderate': 0.65}
        }