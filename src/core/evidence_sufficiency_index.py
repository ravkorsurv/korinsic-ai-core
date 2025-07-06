"""
Evidence Sufficiency Index (ESI) Module

Calculates how well-supported Bayesian risk scores are based on:
- Input diversity and quality
- Node activation ratios
- Confidence scores
- Fallback usage
- Contribution entropy
- Cross-cluster diversity
"""

import numpy as np
import logging
from typing import Dict, List, Any, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

class EvidenceSufficiencyIndex:
    """
    Calculates Evidence Sufficiency Index (ESI) to complement Bayesian risk scores.
    
    ESI provides a measure of how well-supported a risk score is based on:
    - Node activation ratio
    - Mean confidence score
    - Fallback ratio
    - Contribution entropy
    - Cross-cluster diversity
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize ESI calculator with configurable weights.
        
        Args:
            weights: Dictionary of weights for ESI components
        """
        self.weights = weights or {
            'node_activation_ratio': 0.25,
            'mean_confidence_score': 0.25,
            'fallback_ratio': 0.20,
            'contribution_entropy': 0.15,
            'cross_cluster_diversity': 0.15
        }
        
        # Node clusters for diversity calculation
        self.node_clusters = {
            'trade': ['TradingActivity', 'PriceImpact', 'VolumeRatio', 'OrderPattern'],
            'mnpi': ['MaterialInfo', 'Timing'],
            'pnl': ['PnLDrift', 'PnLLossSpike'],
            'comms': ['CommsIntent', 'CommsVolume'],
            'hr': ['AccessLevel', 'Role'],
            'sales': ['ClientActivity', 'UnusualVolume'],
            'market': ['MarketVolatility', 'PriceMovement']
        }
        
        logger.info("Evidence Sufficiency Index calculator initialized")
    
    def calculate_esi(self, evidence: Dict[str, Any], node_states: Dict[str, str], 
                     fallback_usage: Dict[str, bool], confidence_scores: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Calculate the Evidence Sufficiency Index.
        
        Args:
            evidence: Raw evidence data
            node_states: Current states of Bayesian network nodes
            fallback_usage: Whether each node used fallback logic
            confidence_scores: Confidence scores for each input (optional)
            
        Returns:
            Dictionary containing ESI score and detailed breakdown
        """
        try:
            # Calculate individual components
            node_activation_ratio = self._calculate_node_activation_ratio(node_states)
            mean_confidence_score = self._calculate_mean_confidence_score(confidence_scores)
            fallback_ratio = self._calculate_fallback_ratio(fallback_usage)
            contribution_entropy = self._calculate_contribution_entropy(node_states)
            cross_cluster_diversity = self._calculate_cross_cluster_diversity(node_states)
            
            # Calculate weighted ESI score
            esi_score = (
                self.weights['node_activation_ratio'] * node_activation_ratio +
                self.weights['mean_confidence_score'] * mean_confidence_score +
                self.weights['fallback_ratio'] * (1 - fallback_ratio) +
                self.weights['contribution_entropy'] * contribution_entropy +
                self.weights['cross_cluster_diversity'] * cross_cluster_diversity
            )
            
            # Determine ESI badge
            esi_badge = self._get_esi_badge(esi_score)
            
            # Get active clusters
            active_clusters = self._get_active_clusters(node_states)
            
            result = {
                'evidence_sufficiency_index': round(esi_score, 3),
                'esi_badge': esi_badge,
                'node_count': len([n for n in node_states.values() if n != 'Unknown']),
                'mean_confidence': self._get_confidence_label(mean_confidence_score),
                'fallback_ratio': round(fallback_ratio, 3),
                'contribution_spread': self._get_entropy_label(contribution_entropy),
                'clusters': active_clusters,
                'components': {
                    'node_activation_ratio': round(node_activation_ratio, 3),
                    'mean_confidence_score': round(mean_confidence_score, 3),
                    'fallback_ratio': round(fallback_ratio, 3),
                    'contribution_entropy': round(contribution_entropy, 3),
                    'cross_cluster_diversity': round(cross_cluster_diversity, 3)
                }
            }
            
            logger.info(f"ESI calculated: {esi_score:.3f} ({esi_badge})")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating ESI: {e}")
            return self._get_default_esi_result()
    
    def _calculate_node_activation_ratio(self, node_states: Dict[str, str]) -> float:
        """Calculate proportion of active (populated) nodes."""
        if not node_states:
            return 0.0
        
        active_nodes = sum(1 for state in node_states.values() 
                          if state and state != 'Unknown' and state != 'None')
        return active_nodes / len(node_states)
    
    def _calculate_mean_confidence_score(self, confidence_scores: Dict[str, float]) -> float:
        """Calculate average confidence level of inputs."""
        if not confidence_scores:
            return 0.5  # Default moderate confidence
        
        scores = list(confidence_scores.values())
        return np.mean(scores) if scores else 0.5
    
    def _calculate_fallback_ratio(self, fallback_usage: Dict[str, bool]) -> float:
        """Calculate proportion of nodes relying on fallback logic."""
        if not fallback_usage:
            return 0.0
        
        fallback_count = sum(1 for used in fallback_usage.values() if used)
        return fallback_count / len(fallback_usage)
    
    def _calculate_contribution_entropy(self, node_states: Dict[str, str]) -> float:
        """Calculate entropy of node contributions - measures distribution evenness."""
        if not node_states:
            return 0.0
        
        # Count states (simplified contribution measure)
        state_counts = defaultdict(int)
        for state in node_states.values():
            if state and state != 'Unknown':
                state_counts[state] += 1
        
        if not state_counts:
            return 0.0
        
        # Calculate entropy
        total = sum(state_counts.values())
        probabilities = [count / total for count in state_counts.values()]
        
        # Shannon entropy
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        
        # Normalize to [0, 1] range
        max_entropy = np.log2(len(state_counts))
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def _calculate_cross_cluster_diversity(self, node_states: Dict[str, str]) -> float:
        """Calculate evidence spread across distinct node clusters."""
        if not node_states:
            return 0.0
        
        active_clusters = set()
        total_nodes = 0
        
        for node_name, state in node_states.items():
            if state and state != 'Unknown':
                total_nodes += 1
                # Find which cluster this node belongs to
                for cluster_name, cluster_nodes in self.node_clusters.items():
                    if node_name in cluster_nodes:
                        active_clusters.add(cluster_name)
                        break
        
        if total_nodes == 0:
            return 0.0
        
        # Diversity is the ratio of active clusters to total possible clusters
        return len(active_clusters) / len(self.node_clusters)
    
    def _get_esi_badge(self, esi_score: float) -> str:
        """Get ESI badge based on score."""
        if esi_score >= 0.8:
            return "Strong"
        elif esi_score >= 0.6:
            return "Moderate"
        elif esi_score >= 0.4:
            return "Limited"
        else:
            return "Sparse"
    
    def _get_confidence_label(self, confidence_score: float) -> str:
        """Get human-readable confidence label."""
        if confidence_score >= 0.8:
            return "High"
        elif confidence_score >= 0.6:
            return "Medium"
        else:
            return "Low"
    
    def _get_entropy_label(self, entropy_score: float) -> str:
        """Get human-readable entropy label."""
        if entropy_score >= 0.7:
            return "Balanced"
        elif entropy_score >= 0.4:
            return "Moderate"
        else:
            return "Concentrated"
    
    def _get_active_clusters(self, node_states: Dict[str, str]) -> List[str]:
        """Get list of active clusters."""
        active_clusters = set()
        
        for node_name, state in node_states.items():
            if state and state != 'Unknown':
                for cluster_name, cluster_nodes in self.node_clusters.items():
                    if node_name in cluster_nodes:
                        active_clusters.add(cluster_name)
                        break
        
        return list(active_clusters)
    
    def _get_default_esi_result(self) -> Dict[str, Any]:
        """Return default ESI result when calculation fails."""
        return {
            'evidence_sufficiency_index': 0.0,
            'esi_badge': 'Sparse',
            'node_count': 0,
            'mean_confidence': 'Low',
            'fallback_ratio': 1.0,
            'contribution_spread': 'Concentrated',
            'clusters': [],
            'components': {
                'node_activation_ratio': 0.0,
                'mean_confidence_score': 0.0,
                'fallback_ratio': 1.0,
                'contribution_entropy': 0.0,
                'cross_cluster_diversity': 0.0
            }
        }
    
    def adjust_risk_score(self, risk_score: float, esi_score: float) -> float:
        """
        Adjust risk score using ESI as a multiplier.
        
        Args:
            risk_score: Original Bayesian risk score
            esi_score: Evidence sufficiency index
            
        Returns:
            Adjusted risk score
        """
        adjusted_score = risk_score * esi_score
        logger.info(f"Risk score adjusted: {risk_score:.3f} -> {adjusted_score:.3f} (ESI: {esi_score:.3f})")
        return adjusted_score 