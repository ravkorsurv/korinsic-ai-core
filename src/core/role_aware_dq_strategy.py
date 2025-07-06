"""
Role-Aware Data Quality Strategy

Implements role-aware data quality scoring that includes DQSI trust bucket
categorization for improved analyst interpretation and filtering.
"""

import logging
from typing import Dict, Any, List
from .evidence_sufficiency_index import EvidenceSufficiencyIndex
from .dq_sufficiency_index import DQSufficiencyIndex

logger = logging.getLogger(__name__)

class RoleAwareDQStrategy:
    """
    Role-aware data quality strategy that adjusts scoring based on user roles
    and includes DQSI trust bucket categorization in output.
    """
    
    def __init__(self):
        """Initialize role-aware DQ strategy."""
        self.esi_calculator = EvidenceSufficiencyIndex()
        self.dqsi_calculator = DQSufficiencyIndex()
        logger.info("Role-aware DQ strategy initialized")
    
    def calculate_dq_score(self, evidence: Dict[str, Any], node_states: Dict[str, str],
                          fallback_usage: Dict[str, bool], user_role: str = "analyst",
                          confidence_scores: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Calculate data quality score with role-aware adjustments.
        
        Args:
            evidence: Raw evidence data
            node_states: Current states of Bayesian network nodes
            fallback_usage: Whether each node used fallback logic
            user_role: User role for role-aware scoring
            confidence_scores: Confidence scores for each input
            
        Returns:
            Dictionary containing DQ score with DQSI trust bucket
        """
        try:
            # Calculate base ESI score
            esi_result = self.esi_calculator.calculate_esi(
                evidence, node_states, fallback_usage, confidence_scores
            )
            
            # Apply role-aware adjustments
            adjusted_result = self._apply_role_adjustments(esi_result, user_role)
            
            # Add DQSI trust bucket to result
            final_result = self.dqsi_calculator.add_trust_bucket_to_result(adjusted_result)
            
            # Add strategy metadata
            final_result['dq_strategy'] = 'role_aware'
            final_result['user_role'] = user_role
            
            logger.info(f"Role-aware DQ score calculated for {user_role}: "
                       f"confidence={final_result['dqsi_confidence_index']:.3f}, "
                       f"trust_bucket={final_result['dqsi_trust_bucket']}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in role-aware DQ calculation: {e}")
            return self._get_default_result(user_role)
    
    def _apply_role_adjustments(self, esi_result: Dict[str, Any], user_role: str) -> Dict[str, Any]:
        """
        Apply role-specific adjustments to ESI result.
        
        Args:
            esi_result: Base ESI calculation result
            user_role: User role for adjustments
            
        Returns:
            Adjusted ESI result
        """
        role_adjustments = {
            'analyst': 1.0,      # No adjustment for analysts
            'supervisor': 0.95,  # Slightly more conservative
            'compliance': 0.9,   # More conservative for compliance
            'auditor': 0.85,     # Most conservative for auditors
            'trader': 1.05,      # Slightly less conservative for traders
            'manager': 0.98      # Slightly more conservative for managers
        }
        
        adjustment_factor = role_adjustments.get(user_role, 1.0)
        
        # Adjust the evidence sufficiency index
        original_esi = esi_result['evidence_sufficiency_index']
        adjusted_esi = min(original_esi * adjustment_factor, 1.0)  # Cap at 1.0
        
        esi_result['evidence_sufficiency_index'] = round(adjusted_esi, 3)
        esi_result['role_adjustment_factor'] = adjustment_factor
        esi_result['original_esi'] = round(original_esi, 3)
        
        logger.debug(f"Applied {user_role} adjustment: {original_esi:.3f} -> {adjusted_esi:.3f}")
        
        return esi_result
    
    def get_supported_roles(self) -> List[str]:
        """
        Get list of supported user roles.
        
        Returns:
            List of supported role names
        """
        return ['analyst', 'supervisor', 'compliance', 'auditor', 'trader', 'manager']
    
    def _get_default_result(self, user_role: str) -> Dict[str, Any]:
        """
        Get default result when calculation fails.
        
        Args:
            user_role: User role for the result
            
        Returns:
            Default DQ result with DQSI trust bucket
        """
        default_result = {
            'evidence_sufficiency_index': 0.0,
            'esi_badge': 'Sparse',
            'dqsi_confidence_index': 0.0,
            'dqsi_trust_bucket': 'Low',
            'dq_strategy': 'role_aware',
            'user_role': user_role,
            'role_adjustment_factor': 1.0,
            'original_esi': 0.0,
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
        
        return default_result