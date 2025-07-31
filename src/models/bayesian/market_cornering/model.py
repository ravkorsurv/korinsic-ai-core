"""
Market Cornering Detection Model.

This module contains the main MarketCorneringModel class that encapsulates
the Bayesian network for detecting market cornering activities.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .config import MarketCorneringConfig
from .nodes import MarketCorneringNodes

# Add regulatory explainability import
from ....core.regulatory_explainability import (
    RegulatoryExplainabilityEngine,
    EvidenceItem,
    EvidenceType,
    RegulatoryFramework
)

logger = logging.getLogger(__name__)


class MarketCorneringModel:
    """
    Market cornering detection model using Bayesian networks.

    This class provides a complete interface for market cornering risk assessment,
    including model building, inference, and evidence sufficiency analysis.
    """

    def __init__(
        self, use_latent_intent: bool = True, config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the market cornering model.

        Args:
            use_latent_intent: Whether to use latent intent modeling
            config: Optional model configuration
        """
        self.use_latent_intent = use_latent_intent
        self.config = MarketCorneringConfig(config or {})
        self.nodes = MarketCorneringNodes()
        
        # Initialize regulatory explainability engine
        self.explainability_engine = RegulatoryExplainabilityEngine(config or {})

        logger.info(
            f"Market cornering model initialized (latent_intent={use_latent_intent})"
        )

    def calculate_risk(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate market cornering risk based on evidence.

        Args:
            evidence: Dictionary of evidence variables

        Returns:
            Risk assessment results
        """
        try:
            # Simple risk calculation for testing
            risk_score = 0.0
            evidence_count = 0

            weights = self.config.get_evidence_weights()

            for evidence_type, weight in weights.items():
                if evidence_type in evidence:
                    evidence_value = evidence[evidence_type]
                    if isinstance(evidence_value, (int, float)):
                        risk_score += weight * evidence_value
                        evidence_count += 1

            # Normalize by evidence count
            if evidence_count > 0:
                risk_score = risk_score / evidence_count

            # Determine risk level
            thresholds = self.config.get_risk_thresholds()
            if risk_score >= thresholds["high_risk"]:
                risk_level = "HIGH"
            elif risk_score >= thresholds["medium_risk"]:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            return {
                "risk_scores": {
                    "overall_score": risk_score,
                    "confidence": 0.8,
                    "evidence_nodes": list(evidence.keys()),
                },
                "risk_assessment": {
                    "risk_level": risk_level,
                    "adjusted_score": risk_score,
                    "recommendation": f"{risk_level} risk detected",
                },
                "model_metadata": {
                    "model_type": "market_cornering",
                    "use_latent_intent": self.use_latent_intent,
                    "inference_method": "simple_calculation",
                },
            }

        except Exception as e:
            logger.error(f"Error calculating market cornering risk: {str(e)}")
            raise

    def get_required_nodes(self) -> List[str]:
        """
        Get list of required nodes for this model.

        Returns:
            List of required node names
        """
        return [
            "market_concentration",
            "position_accumulation",
            "supply_control",
            "liquidity_manipulation",
            "price_distortion",
            "delivery_constraint",
        ]

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Model information dictionary
        """
        return {
            "model_type": "market_cornering",
            "use_latent_intent": self.use_latent_intent,
            "required_nodes": self.get_required_nodes(),
            "config": self.config.get_config(),
        }

    def validate_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate evidence against model requirements.

        Args:
            evidence: Evidence to validate

        Returns:
            Validation report
        """
        required_nodes = self.get_required_nodes()

        valid_nodes = []
        missing_nodes = []

        for node_name in required_nodes:
            if node_name in evidence:
                if self.nodes.validate_node_value(node_name, evidence[node_name]):
                    valid_nodes.append(node_name)
            else:
                missing_nodes.append(node_name)

        return {
            "valid": len(missing_nodes) == 0,
            "valid_nodes": valid_nodes,
            "missing_nodes": missing_nodes,
            "completeness": len(valid_nodes) / len(required_nodes),
        }

    def generate_regulatory_explanation(
        self, 
        evidence: Dict[str, Any], 
        inference_result: Dict[str, float],
        account_id: str,
        timestamp: str
    ) -> List[EvidenceItem]:
        """
        Generate regulatory explainability evidence for market cornering detection.
        
        Args:
            evidence: Input evidence dictionary
            inference_result: Model inference results
            account_id: Account identifier
            timestamp: Evidence timestamp
            
        Returns:
            List of evidence items for regulatory explanation
        """
        evidence_items = []
        
        # Generate evidence items based on model-specific patterns
        for evidence_key, evidence_value in evidence.items():
            if isinstance(evidence_value, (int, float)) and evidence_value > 0.1:
                # Determine evidence type based on key
                evidence_type = EvidenceType.TRADING_PATTERN
                if 'communication' in evidence_key.lower():
                    evidence_type = EvidenceType.COMMUNICATION
                elif 'timing' in evidence_key.lower() or 'temporal' in evidence_key.lower():
                    evidence_type = EvidenceType.TIMING_ANOMALY
                elif 'cross' in evidence_key.lower() or 'correlation' in evidence_key.lower():
                    evidence_type = EvidenceType.CROSS_ACCOUNT_CORRELATION
                
                evidence_items.append(EvidenceItem(
                    evidence_type=evidence_type,
                    account_id=account_id,
                    timestamp=datetime.fromisoformat(timestamp),
                    description=f"Market Cornering indicator: {evidence_key} = {evidence_value:.2f}",
                    strength=min(float(evidence_value), 1.0),
                    reliability=0.85,
                    regulatory_relevance={
                        RegulatoryFramework.MAR_ARTICLE_12: 0.9,
                        RegulatoryFramework.STOR_REQUIREMENTS: 0.8
                    },
                    raw_data={
                        'model_type': 'market_cornering',
                        'evidence_node': evidence_key,
                        'score': evidence_value,
                        'inference_result': inference_result
                    }
                ))
        
        return evidence_items
    
    def get_regulatory_framework_mapping(self) -> Dict[RegulatoryFramework, Dict[str, Any]]:
        """
        Get regulatory framework mapping for market cornering detection.
        
        Returns:
            Dictionary mapping regulatory frameworks to their requirements
        """
        return {
            RegulatoryFramework.MAR_ARTICLE_12: {
                "description": "Market Cornering detection and analysis",
                "key_indicators": ['Market concentration activities', 'Price manipulation through volume', 'Coordinated position building'],
                "evidence_threshold": 0.7,
                "reporting_requirements": "Detailed pattern analysis required"
            },
            RegulatoryFramework.STOR_REQUIREMENTS: {
                "description": "Suspicious transaction reporting for market cornering behavior",
                "key_indicators": ['Market concentration activities', 'Price manipulation through volume'],
                "evidence_threshold": 0.6,
                "reporting_requirements": "Transaction-level details required"
            }
        }

