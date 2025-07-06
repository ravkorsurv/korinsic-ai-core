"""
Data Quality Sufficiency Index (DQSI) Module

Provides trust bucket categorization for data quality confidence scores
to improve analyst interpretation and regulatory defensibility.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DQSufficiencyIndex:
    """
    Data Quality Sufficiency Index calculator that provides trust bucket
    categorization based on confidence index values.
    
    This module complements the Evidence Sufficiency Index by providing
    human-readable trust categories for UI display and filtering.
    """
    
    def __init__(self):
        """Initialize DQSI calculator."""
        logger.info("DQ Sufficiency Index calculator initialized")
    
    def get_trust_bucket(self, dqsi_confidence_index: float) -> str:
        """
        Map DQSI confidence index to trust bucket category.
        
        Args:
            dqsi_confidence_index: Confidence index value (0.0 to 1.0)
            
        Returns:
            Trust bucket label: "High", "Moderate", or "Low"
        """
        if dqsi_confidence_index >= 0.85:
            return "High"
        elif dqsi_confidence_index >= 0.65:
            return "Moderate"
        else:
            return "Low"
    
    def add_trust_bucket_to_result(self, result: Dict[str, Any], 
                                  confidence_index: float = None) -> Dict[str, Any]:
        """
        Add dqsi_trust_bucket to existing scoring result.
        
        Args:
            result: Existing scoring result dictionary
            confidence_index: Optional confidence index; if not provided, 
                            will use evidence_sufficiency_index from result
            
        Returns:
            Updated result dictionary with dqsi_trust_bucket field
        """
        if confidence_index is None:
            confidence_index = result.get('evidence_sufficiency_index', 0.0)
        
        # Add DQSI fields to result
        result['dqsi_confidence_index'] = round(confidence_index, 3)
        result['dqsi_trust_bucket'] = self.get_trust_bucket(confidence_index)
        
        logger.debug(f"Added DQSI trust bucket: {result['dqsi_trust_bucket']} "
                    f"(confidence: {confidence_index:.3f})")
        
        return result
    
    def validate_trust_bucket(self, trust_bucket: str) -> bool:
        """
        Validate that trust bucket value is one of the allowed values.
        
        Args:
            trust_bucket: Trust bucket value to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_buckets = {"High", "Moderate", "Low"}
        return trust_bucket in valid_buckets
    
    def get_boundary_test_cases(self) -> Dict[str, Dict[str, Any]]:
        """
        Get test cases for boundary values to ensure correct bucket assignment.
        
        Returns:
            Dictionary of test cases with confidence values and expected buckets
        """
        return {
            "high_boundary": {
                "confidence_index": 0.85,
                "expected_bucket": "High",
                "description": "Exact threshold for High bucket"
            },
            "high_above": {
                "confidence_index": 0.86,
                "expected_bucket": "High",
                "description": "Just above High threshold"
            },
            "moderate_boundary": {
                "confidence_index": 0.65,
                "expected_bucket": "Moderate",
                "description": "Exact threshold for Moderate bucket"
            },
            "moderate_above": {
                "confidence_index": 0.66,
                "expected_bucket": "Moderate",
                "description": "Just above Moderate threshold"
            },
            "moderate_below": {
                "confidence_index": 0.64,
                "expected_bucket": "Low",
                "description": "Just below Moderate threshold"
            },
            "low_boundary": {
                "confidence_index": 0.0,
                "expected_bucket": "Low",
                "description": "Minimum confidence value"
            },
            "maximum": {
                "confidence_index": 1.0,
                "expected_bucket": "High",
                "description": "Maximum confidence value"
            }
        }