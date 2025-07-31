"""
Insider Dealing Detection Model.

This module contains the main InsiderDealingModel class that encapsulates
the Bayesian network for detecting insider dealing activities.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork

from ..shared.esi import EvidenceSufficiencyIndex
from ..shared.fallback_logic import FallbackLogic

# Add regulatory explainability import
from ....core.regulatory_explainability import (
    RegulatoryExplainabilityEngine,
    EvidenceItem,
    EvidenceType,
    RegulatoryFramework
)
from ..shared.model_builder import (
    ModelBuilder,
    build_insider_dealing_bn,
    build_insider_dealing_bn_with_latent_intent,
)
from .config import InsiderDealingConfig
from .nodes import InsiderDealingNodes

logger = logging.getLogger(__name__)


class InsiderDealingModel:
    """
    Insider dealing detection model using Bayesian networks.

    This class provides a complete interface for insider dealing risk assessment,
    including model building, inference, and evidence sufficiency analysis.
    """

    def __init__(
        self, use_latent_intent: bool = False, config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the insider dealing model.

        Args:
            use_latent_intent: Whether to use latent intent modeling
            config: Optional model configuration
        """
        self.use_latent_intent = use_latent_intent
        self.config = InsiderDealingConfig(config or {})
        self.nodes = InsiderDealingNodes()
        self.fallback_logic = FallbackLogic()
        self.esi_calculator = EvidenceSufficiencyIndex()

        # Initialize regulatory explainability engine
        self.explainability_engine = RegulatoryExplainabilityEngine(config or {})

        # Build the Bayesian network
        self.model = self._build_model()
        self.inference_engine = VariableElimination(self.model)

        logger.info(
            f"Insider dealing model initialized (latent_intent={use_latent_intent})"
        )

    def _build_model(self) -> DiscreteBayesianNetwork:
        """
        Build the Bayesian network model.

        Returns:
            Configured Bayesian network
        """
        if self.use_latent_intent:
            return build_insider_dealing_bn_with_latent_intent()
        else:
            return build_insider_dealing_bn()

    def calculate_risk(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate insider dealing risk based on evidence.

        Args:
            evidence: Dictionary of evidence variables

        Returns:
            Risk assessment results
        """
        try:
            # Validate and complete evidence
            processed_evidence = self._process_evidence(evidence)

            # Perform Bayesian inference
            risk_scores = self._perform_inference(processed_evidence)

            # Calculate evidence sufficiency index
            esi_result = self._calculate_esi(evidence, processed_evidence)

            # Generate risk assessment
            risk_assessment = self._generate_risk_assessment(risk_scores, esi_result)

            return {
                "risk_scores": risk_scores,
                "evidence_sufficiency": esi_result,
                "risk_assessment": risk_assessment,
                "fallback_report": self.fallback_logic.get_fallback_report(),
                "model_metadata": {
                    "model_type": "insider_dealing",
                    "use_latent_intent": self.use_latent_intent,
                    "inference_method": "variable_elimination",
                },
            }

        except Exception as e:
            logger.error(f"Error calculating insider dealing risk: {str(e)}")
            raise

    def _process_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate evidence, applying fallback logic if needed.

        Args:
            evidence: Raw evidence data

        Returns:
            Processed evidence dictionary
        """
        # Get required nodes for this model
        required_nodes = self.get_required_nodes()

        # Apply fallback logic for missing evidence
        node_defs = {name: self.nodes.get_node(name) for name in required_nodes}
        processed_evidence = self.fallback_logic.apply_fallback_evidence(
            evidence, node_defs
        )

        return processed_evidence

    def _perform_inference(self, evidence: Dict[str, Any]) -> Dict[str, float]:
        """
        Perform Bayesian inference to calculate risk scores.

        Args:
            evidence: Evidence dictionary

        Returns:
            Risk scores dictionary
        """
        # Query the outcome variable
        outcome_var = "insider_dealing"

        # Perform inference
        result = self.inference_engine.query(variables=[outcome_var], evidence=evidence)

        # Extract risk scores
        risk_scores = {
            "overall_score": float(result.values[1]),  # Probability of insider dealing
            "confidence": self._calculate_confidence(result),
            "evidence_nodes": list(evidence.keys()),
        }

        return risk_scores

    def _calculate_confidence(self, inference_result) -> float:
        """
        Calculate confidence based on inference result.

        Args:
            inference_result: pgmpy inference result

        Returns:
            Confidence score
        """
        # Simple confidence calculation based on probability spread
        probabilities = inference_result.values
        max_prob = max(probabilities)
        min_prob = min(probabilities)
        confidence = max_prob - min_prob

        return float(confidence)

    def _calculate_esi(
        self, original_evidence: Dict[str, Any], processed_evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate Evidence Sufficiency Index.

        Args:
            original_evidence: Original evidence before fallback
            processed_evidence: Evidence after fallback processing

        Returns:
            ESI calculation results
        """
        # Determine which nodes used fallback
        fallback_usage = {}
        for node_name in processed_evidence.keys():
            fallback_usage[node_name] = node_name not in original_evidence

        # Create node states for ESI calculation
        node_states = {}
        for node_name, value in processed_evidence.items():
            if isinstance(value, int):
                node = self.nodes.get_node(node_name)
                if node and value < len(node.states):
                    node_states[node_name] = node.states[value]
                else:
                    node_states[node_name] = str(value)
            else:
                node_states[node_name] = str(value)

        # Calculate ESI
        esi_result = self.esi_calculator.calculate_esi(
            original_evidence, node_states, fallback_usage
        )

        return esi_result

    def _generate_risk_assessment(
        self, risk_scores: Dict[str, float], esi_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive risk assessment.

        Args:
            risk_scores: Calculated risk scores
            esi_result: Evidence sufficiency results

        Returns:
            Risk assessment dictionary
        """
        overall_score = risk_scores["overall_score"]
        esi_score = esi_result["evidence_sufficiency_index"]

        # Adjust risk score using ESI
        adjusted_score = self.esi_calculator.adjust_risk_score(overall_score, esi_score)

        # Determine risk level
        risk_level = self._determine_risk_level(adjusted_score)

        return {
            "risk_level": risk_level,
            "adjusted_score": adjusted_score,
            "original_score": overall_score,
            "esi_impact": adjusted_score - overall_score,
            "confidence_rating": self._get_confidence_rating(risk_scores["confidence"]),
            "evidence_quality": esi_result["esi_badge"],
            "recommendation": self._get_recommendation(
                risk_level, esi_result["esi_badge"]
            ),
        }

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on score."""
        thresholds = self.config.get_risk_thresholds()

        if risk_score >= thresholds["high_risk"]:
            return "HIGH"
        elif risk_score >= thresholds["medium_risk"]:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_confidence_rating(self, confidence: float) -> str:
        """Get confidence rating label."""
        if confidence >= 0.8:
            return "High"
        elif confidence >= 0.6:
            return "Medium"
        else:
            return "Low"

    def _get_recommendation(self, risk_level: str, evidence_quality: str) -> str:
        """Get recommendation based on risk level and evidence quality."""
        if risk_level == "HIGH":
            if evidence_quality in ["Strong", "Moderate"]:
                return "Immediate investigation required"
            else:
                return "Investigation required with additional evidence collection"
        elif risk_level == "MEDIUM":
            return "Enhanced monitoring recommended"
        else:
            return "Continue routine monitoring"

    def get_required_nodes(self) -> List[str]:
        """
        Get list of required nodes for this model.

        Returns:
            List of required node names
        """
        if self.use_latent_intent:
            return [
                "trade_pattern",
                "comms_intent",
                "pnl_drift",
                "profit_motivation",
                "access_pattern",
                "order_behavior",
                "comms_metadata",
                "news_timing",
                "state_information_access",
                "announcement_correlation",
            ]
        else:
            return [
                "trade_pattern",
                "comms_intent",
                "pnl_drift",
                "news_timing",
                "state_information_access",
            ]

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Model information dictionary
        """
        return {
            "model_type": "insider_dealing",
            "use_latent_intent": self.use_latent_intent,
            "nodes_count": len(self.model.nodes()),
            "edges_count": len(self.model.edges()),
            "required_nodes": self.get_required_nodes(),
            "variables": list(self.model.nodes()),
            "cpds_count": len(self.model.get_cpds()),
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
        return self.fallback_logic.validate_evidence_completeness(
            evidence, required_nodes
        )

    def generate_regulatory_explanation(
        self, 
        evidence: Dict[str, Any], 
        inference_result: Dict[str, float],
        account_id: str,
        timestamp: str
    ) -> List[EvidenceItem]:
        """
        Generate regulatory explainability evidence for insider dealing detection.
        
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
                    description=f"Insider Dealing indicator: {evidence_key} = {evidence_value:.2f}",
                    strength=min(float(evidence_value), 1.0),
                    reliability=0.85,
                    regulatory_relevance={
                        RegulatoryFramework.MAR_ARTICLE_8: 0.9,
                        RegulatoryFramework.STOR_REQUIREMENTS: 0.8
                    },
                    raw_data={
                        'model_type': 'insider_dealing',
                        'evidence_node': evidence_key,
                        'score': evidence_value,
                        'inference_result': inference_result
                    }
                ))
        
        return evidence_items
    
    def get_regulatory_framework_mapping(self) -> Dict[RegulatoryFramework, Dict[str, Any]]:
        """
        Get regulatory framework mapping for insider dealing detection.
        
        Returns:
            Dictionary mapping regulatory frameworks to their requirements
        """
        return {
            RegulatoryFramework.MAR_ARTICLE_8: {
                "description": "Insider Dealing detection and analysis",
                "key_indicators": ['Information asymmetry exploitation', 'Temporal correlation with price-sensitive events', 'Cross-account coordination patterns'],
                "evidence_threshold": 0.7,
                "reporting_requirements": "Detailed pattern analysis required"
            },
            RegulatoryFramework.STOR_REQUIREMENTS: {
                "description": "Suspicious transaction reporting for insider dealing behavior",
                "key_indicators": ['Information asymmetry exploitation', 'Temporal correlation with price-sensitive events'],
                "evidence_threshold": 0.6,
                "reporting_requirements": "Transaction-level details required"
            }
        }

