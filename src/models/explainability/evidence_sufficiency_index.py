"""
Evidence Sufficiency Index (ESI) Component

This module implements the Evidence Sufficiency Index as specified in wiki section 12.2.
ESI complements the Bayesian risk score by measuring evidence quality, diversity, and completeness.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import math
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ESIResult:
    """Evidence Sufficiency Index result matching wiki specification"""
    evidence_sufficiency_index: float
    node_count: int
    mean_confidence: str
    fallback_ratio: float
    contribution_spread: str
    clusters: List[str]
    calculation_details: Dict[str, Any]

class EvidenceSufficiencyIndex:
    """
    Evidence Sufficiency Index Calculator
    
    Implements the ESI specification from wiki 12.2 to measure evidence quality
    and support analyst trust calibration and filtering.
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize ESI calculator with configurable weights
        
        Args:
            weights: Component weights for ESI calculation
        """
        # Default weights from wiki specification
        self.weights = weights or {
            'W1': 0.2,   # node_activation_ratio
            'W2': 0.25,  # mean_confidence_score  
            'W3': 0.2,   # (1 - fallback_ratio)
            'W4': 0.15,  # contribution_entropy
            'W5': 0.2    # cross_cluster_diversity
        }
        
        # Node cluster definitions for cross-cluster diversity
        self.node_clusters = {
            'PnL': ['Q20_PnLDeviation', 'Q19_HRIncentiveAlignment', 'trader_pnl'],
            'MNPI': ['Q75_CommsIntentInfluence', 'Q44_EntityRiskScore', 'access_to_mnpi'],
            'TradePattern': ['Q35_TradeClustering', 'Q21_PriceSensitivityAbuse', 'trade_pattern'],
            'Market': ['Q51_NewsSentimentImpact', 'market_data', 'price_volatility'],
            'System': ['Q99_KDEIntegrityFlag', 'data_quality', 'system_health']
        }
    
    def calculate_esi(self, evidence: Dict[str, Any], result: Dict[str, Any]) -> ESIResult:
        """
        Calculate Evidence Sufficiency Index exactly as specified in wiki
        
        Args:
            evidence: Input evidence dictionary
            result: Model inference result with active nodes and posteriors
            
        Returns:
            ESIResult with complete ESI calculation and metadata
        """
        try:
            # Core inputs for ESI calculation (from wiki specification)
            node_activation_ratio = self._calculate_node_activation_ratio(result)
            mean_confidence_score = self._calculate_mean_confidence(evidence)
            fallback_ratio = self._calculate_fallback_ratio(result)
            contribution_entropy = self._calculate_contribution_entropy(result)
            cross_cluster_diversity = self._calculate_cross_cluster_diversity(result)
            
            # ESI calculation using exact formula from wiki
            esi = (self.weights['W1'] * node_activation_ratio +
                   self.weights['W2'] * mean_confidence_score +
                   self.weights['W3'] * (1 - fallback_ratio) +
                   self.weights['W4'] * contribution_entropy +
                   self.weights['W5'] * cross_cluster_diversity)
            
            # Ensure ESI is between 0 and 1
            esi = max(0.0, min(1.0, esi))
            
            # Generate result matching wiki output format
            return ESIResult(
                evidence_sufficiency_index=round(esi, 2),
                node_count=len(result.get('active_nodes', [])),
                mean_confidence=self._confidence_to_label(mean_confidence_score),
                fallback_ratio=round(fallback_ratio, 2),
                contribution_spread="Balanced" if contribution_entropy > 0.7 else "Concentrated",
                clusters=self._get_evidence_clusters(result),
                calculation_details={
                    'node_activation_ratio': round(node_activation_ratio, 3),
                    'mean_confidence_score': round(mean_confidence_score, 3),
                    'fallback_ratio': round(fallback_ratio, 3),
                    'contribution_entropy': round(contribution_entropy, 3),
                    'cross_cluster_diversity': round(cross_cluster_diversity, 3),
                    'weighted_components': {
                        'activation_component': round(self.weights['W1'] * node_activation_ratio, 3),
                        'confidence_component': round(self.weights['W2'] * mean_confidence_score, 3),
                        'fallback_component': round(self.weights['W3'] * (1 - fallback_ratio), 3),
                        'entropy_component': round(self.weights['W4'] * contribution_entropy, 3),
                        'diversity_component': round(self.weights['W5'] * cross_cluster_diversity, 3)
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"ESI calculation failed: {e}")
            # Return conservative ESI on failure
            return self._fallback_esi_result(evidence, result)
    
    def _calculate_node_activation_ratio(self, result: Dict[str, Any]) -> float:
        """Calculate proportion of active (populated) nodes in the BN"""
        active_nodes = result.get('active_nodes', [])
        all_nodes = result.get('all_nodes', active_nodes)
        
        if not all_nodes:
            return 0.0
            
        return len(active_nodes) / len(all_nodes)
    
    def _calculate_mean_confidence(self, evidence: Dict[str, Any]) -> float:
        """Calculate average confidence level of inputs (mapped to numeric)"""
        confidence_values = []
        
        for key, value in evidence.items():
            if isinstance(value, dict) and 'confidence' in value:
                confidence = value['confidence']
            else:
                # Infer confidence from evidence quality
                confidence = self._infer_confidence_from_evidence(key, value)
            
            # Map confidence labels to numeric values
            confidence_numeric = self._confidence_to_numeric(confidence)
            confidence_values.append(confidence_numeric)
        
        return sum(confidence_values) / len(confidence_values) if confidence_values else 0.5
    
    def _calculate_fallback_ratio(self, result: Dict[str, Any]) -> float:
        """Calculate proportion of nodes relying on priors or latent defaults"""
        active_nodes = result.get('active_nodes', [])
        fallback_count = result.get('fallback_count', 0)
        
        if not active_nodes:
            return 1.0  # All fallback if no active nodes
            
        return fallback_count / len(active_nodes)
    
    def _calculate_contribution_entropy(self, result: Dict[str, Any]) -> float:
        """Calculate entropy of node contributions - measures distribution evenness"""
        posteriors = result.get('posteriors', {})
        
        if not posteriors:
            return 0.0
        
        # Get contribution values
        contributions = list(posteriors.values())
        
        if not contributions:
            return 0.0
        
        # Normalize contributions to probabilities
        total = sum(abs(c) for c in contributions)
        if total == 0:
            return 0.0
            
        probabilities = [abs(c) / total for c in contributions]
        
        # Calculate Shannon entropy
        entropy = -sum(p * math.log2(p + 1e-10) for p in probabilities if p > 0)
        
        # Normalize to [0, 1] range
        max_entropy = math.log2(len(probabilities))
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def _calculate_cross_cluster_diversity(self, result: Dict[str, Any]) -> float:
        """Calculate evidence spread across distinct node groups"""
        active_nodes = result.get('active_nodes', [])
        
        if not active_nodes:
            return 0.0
        
        # Count active clusters
        active_clusters = set()
        for node in active_nodes:
            for cluster_name, cluster_nodes in self.node_clusters.items():
                if any(cluster_node in str(node) for cluster_node in cluster_nodes):
                    active_clusters.add(cluster_name)
                    break
        
        # Diversity is proportion of clusters with evidence
        total_clusters = len(self.node_clusters)
        return len(active_clusters) / total_clusters if total_clusters > 0 else 0.0
    
    def _confidence_to_numeric(self, confidence: str) -> float:
        """Convert confidence labels to numeric values"""
        confidence_map = {
            'High': 1.0,
            'Medium': 0.7,
            'Low': 0.4,
            'Very Low': 0.2,
            'Unknown': 0.5
        }
        
        if isinstance(confidence, (int, float)):
            return float(confidence)
            
        return confidence_map.get(str(confidence), 0.5)
    
    def _confidence_to_label(self, numeric_confidence: float) -> str:
        """Convert numeric confidence to label"""
        if numeric_confidence >= 0.8:
            return "High"
        elif numeric_confidence >= 0.6:
            return "Medium"
        elif numeric_confidence >= 0.4:
            return "Low"
        else:
            return "Very Low"
    
    def _infer_confidence_from_evidence(self, key: str, value: Any) -> str:
        """Infer confidence level from evidence characteristics"""
        if value is None:
            return "Very Low"
        
        # Check for data quality indicators
        if isinstance(value, dict):
            if value.get('quality_score', 0) > 0.8:
                return "High"
            elif value.get('quality_score', 0) > 0.6:
                return "Medium"
            else:
                return "Low"
        
        # Check for numeric precision
        if isinstance(value, (int, float)):
            return "High" if abs(value) > 0.1 else "Medium"
        
        # Check for string completeness
        if isinstance(value, str):
            return "High" if len(value) > 10 else "Medium"
        
        return "Medium"  # Default confidence
    
    def _get_evidence_clusters(self, result: Dict[str, Any]) -> List[str]:
        """Get list of evidence clusters represented in active nodes"""
        active_nodes = result.get('active_nodes', [])
        represented_clusters = set()
        
        for node in active_nodes:
            for cluster_name, cluster_nodes in self.node_clusters.items():
                if any(cluster_node in str(node) for cluster_node in cluster_nodes):
                    represented_clusters.add(cluster_name)
                    break
        
        return sorted(list(represented_clusters))
    
    def _fallback_esi_result(self, evidence: Dict[str, Any], result: Dict[str, Any]) -> ESIResult:
        """Generate conservative ESI result when calculation fails"""
        return ESIResult(
            evidence_sufficiency_index=0.5,
            node_count=len(result.get('active_nodes', [])),
            mean_confidence="Medium",
            fallback_ratio=1.0,
            contribution_spread="Unknown",
            clusters=["System"],
            calculation_details={
                'error': 'ESI calculation failed, using fallback values',
                'fallback_applied': True
            }
        )
    
    def calculate_adjusted_risk_score(self, risk_score: float, esi_result: ESIResult) -> float:
        """
        Calculate adjusted risk score using ESI as multiplier (from wiki 12.2)
        
        Args:
            risk_score: Original Bayesian risk score
            esi_result: ESI calculation result
            
        Returns:
            Adjusted risk score = Risk Score * ESI
        """
        return risk_score * esi_result.evidence_sufficiency_index
    
    def generate_esi_explanation(self, esi_result: ESIResult) -> str:
        """Generate human-readable explanation for ESI score"""
        esi_score = esi_result.evidence_sufficiency_index
        
        if esi_score >= 0.8:
            quality = "Strong"
            detail = "high-quality evidence from multiple sources"
        elif esi_score >= 0.6:
            quality = "Moderate"
            detail = "reasonable evidence quality with some gaps"
        elif esi_score >= 0.4:
            quality = "Weak"
            detail = "limited evidence with significant gaps"
        else:
            quality = "Sparse"
            detail = "very limited evidence quality"
        
        cluster_info = f"spanning {len(esi_result.clusters)} evidence clusters" if esi_result.clusters else "from limited sources"
        
        return (f"ESI: {quality} Evidence ({esi_score}) - This alert is supported by "
                f"{detail} {cluster_info} with {esi_result.mean_confidence.lower()} confidence "
                f"and {100-int(esi_result.fallback_ratio*100)}% primary evidence.")

    def get_esi_badge(self, esi_score: float) -> Dict[str, str]:
        """Get UI badge information for ESI score"""
        if esi_score >= 0.8:
            return {"label": "Strong Evidence", "color": "green", "icon": "shield-check"}
        elif esi_score >= 0.6:
            return {"label": "Moderate Evidence", "color": "orange", "icon": "shield"}
        elif esi_score >= 0.4:
            return {"label": "Weak Evidence", "color": "yellow", "icon": "shield-alert"}
        else:
            return {"label": "Sparse Evidence", "color": "red", "icon": "shield-x"}