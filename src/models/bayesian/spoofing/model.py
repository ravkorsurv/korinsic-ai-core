"""
Enhanced Spoofing Detection Model.

This module contains the main SpoofingModel class that encapsulates
the Bayesian network for detecting spoofing and layering behavior.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork

from ..shared.esi import EvidenceSufficiencyIndex
from ..shared.fallback_logic import FallbackLogic
from .config import SpoofingConfig
from .nodes import SpoofingNodes

# Add regulatory explainability import
from ....core.regulatory_explainability import (
    RegulatoryExplainabilityEngine,
    EvidenceItem,
    EvidenceType,
    RegulatoryFramework
)

logger = logging.getLogger(__name__)


class SpoofingModel:
    """
    Enhanced spoofing detection model using Bayesian networks.

    This class provides a complete interface for spoofing risk assessment,
    including model building, inference, and evidence sufficiency analysis.
    """

    def __init__(
        self, use_latent_intent: bool = True, config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the spoofing model.

        Args:
            use_latent_intent: Whether to use latent intent modeling
            config: Optional model configuration
        """
        self.use_latent_intent = use_latent_intent
        self.config = SpoofingConfig(config or {})
        self.nodes = SpoofingNodes()
        self.fallback_logic = FallbackLogic()
        self.esi_calculator = EvidenceSufficiencyIndex()
        
        # Initialize regulatory explainability engine
        self.explainability_engine = RegulatoryExplainabilityEngine(config or {})

        # Build the Bayesian network
        self.model = self._build_model()
        self.inference_engine = VariableElimination(self.model)

        logger.info(f"Spoofing model initialized (latent_intent={use_latent_intent})")

    def _build_model(self) -> DiscreteBayesianNetwork:
        """
        Build the Bayesian network model.

        Returns:
            Configured Bayesian network
        """
        if self.use_latent_intent:
            return self._build_latent_intent_model()
        else:
            return self._build_standard_model()

    def _build_standard_model(self) -> DiscreteBayesianNetwork:
        """
        Build the standard spoofing Bayesian network.

        Returns:
            Standard Bayesian network
        """
        # Create the network structure
        model = DiscreteBayesianNetwork()

        # Add nodes
        nodes = [
            "order_clustering",
            "price_impact_ratio",
            "volume_participation",
            "order_behavior",
            "intent_to_execute",
            "order_cancellation",
            "risk_factor",
            "spoofing",
        ]

        model.add_nodes_from(nodes)

        # Add edges - evidence nodes to risk factor
        evidence_nodes = [
            "order_clustering",
            "price_impact_ratio",
            "volume_participation",
            "order_behavior",
            "intent_to_execute",
            "order_cancellation",
        ]

        for evidence_node in evidence_nodes:
            model.add_edge(evidence_node, "risk_factor")

        # Add edge from risk factor to outcome
        model.add_edge("risk_factor", "spoofing")

        # Add CPDs (placeholder - would need proper CPDs in production)
        self._add_cpds(model, use_latent_intent=False)

        return model

    def _build_latent_intent_model(self) -> DiscreteBayesianNetwork:
        """
        Build the latent intent spoofing Bayesian network.

        Returns:
            Latent intent Bayesian network
        """
        # Create the network structure
        model = DiscreteBayesianNetwork()

        # Add nodes
        nodes = [
            "order_clustering",
            "price_impact_ratio",
            "volume_participation",
            "order_behavior",
            "intent_to_execute",
            "order_cancellation",
            "spoofing_latent_intent",
            "risk_factor",
            "spoofing",
        ]

        model.add_nodes_from(nodes)

        # Add edges - evidence nodes to latent intent
        evidence_nodes = [
            "order_clustering",
            "price_impact_ratio",
            "volume_participation",
            "order_behavior",
            "intent_to_execute",
            "order_cancellation",
        ]

        for evidence_node in evidence_nodes:
            model.add_edge(evidence_node, "spoofing_latent_intent")

        # Add edge from latent intent to risk factor
        model.add_edge("spoofing_latent_intent", "risk_factor")

        # Add edge from risk factor to outcome
        model.add_edge("risk_factor", "spoofing")

        # Add CPDs (placeholder - would need proper CPDs in production)
        self._add_cpds(model, use_latent_intent=True)

        return model

    def _add_cpds(
        self, model: DiscreteBayesianNetwork, use_latent_intent: bool = False
    ):
        """
        Add Conditional Probability Distributions to the model.

        Args:
            model: Bayesian network model
            use_latent_intent: Whether to use latent intent structure
        """
        # This is a placeholder implementation
        # In production, you would add proper CPDs here
        # For now, we'll use simple fallback priors

        import numpy as np
        from pgmpy.factors.discrete import TabularCPD

        # Add CPDs for evidence nodes (using fallback priors)
        evidence_nodes = [
            "order_clustering",
            "price_impact_ratio",
            "volume_participation",
            "order_behavior",
            "intent_to_execute",
            "order_cancellation",
        ]

        for node_name in evidence_nodes:
            node = self.nodes.get_node(node_name)
            if node:
                cpd = TabularCPD(
                    variable=node_name,
                    variable_card=len(node.states),
                    values=np.array([node.fallback_prior]).T,
                )
                model.add_cpds(cpd)

        if use_latent_intent:
            # Latent intent CPD (corrected: 6 parents, 3 states each)
            spoofing_intent_cpd = TabularCPD(
                variable="spoofing_latent_intent",
                variable_card=3,
                values=np.full((3, 729), 1 / 3),
                evidence=[
                    "order_clustering",
                    "price_impact_ratio",
                    "volume_participation",
                    "order_behavior",
                    "intent_to_execute",
                    "order_cancellation",
                ],
                evidence_card=[3, 3, 3, 3, 3, 3],
            )
            model.add_cpds(spoofing_intent_cpd)
            # Risk factor CPD (depends on latent intent)
            risk_factor_cpd = TabularCPD(
                variable="risk_factor",
                variable_card=3,
                values=np.array(
                    [
                        [0.90, 0.45, 0.10],  # Low risk
                        [0.08, 0.35, 0.30],  # Medium risk
                        [0.02, 0.20, 0.60],  # High risk
                    ]
                ),
                evidence=["spoofing_latent_intent"],
                evidence_card=[3],
            )
            model.add_cpds(risk_factor_cpd)
        else:
            # Standard risk factor CPD (6 parents, 3 states each)
            risk_factor_cpd = TabularCPD(
                variable="risk_factor",
                variable_card=3,
                values=np.full((3, 729), 1 / 3),
                evidence=[
                    "order_clustering",
                    "price_impact_ratio",
                    "volume_participation",
                    "order_behavior",
                    "intent_to_execute",
                    "order_cancellation",
                ],
                evidence_card=[3, 3, 3, 3, 3, 3],
            )
            model.add_cpds(risk_factor_cpd)
        # Outcome CPD (depends on risk_factor)
        outcome_cpd = TabularCPD(
            variable="spoofing",
            variable_card=2,
            values=np.array(
                [
                    [0.97, 0.70, 0.20],  # No spoofing
                    [0.03, 0.30, 0.80],  # Spoofing detected
                ]
            ),
            evidence=["risk_factor"],
            evidence_card=[3],
        )
        model.add_cpds(outcome_cpd)

    def calculate_risk(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate spoofing risk based on evidence.

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
                    "model_type": "spoofing",
                    "use_latent_intent": self.use_latent_intent,
                    "inference_method": "variable_elimination",
                },
            }

        except Exception as e:
            logger.error(f"Error calculating spoofing risk: {str(e)}")
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
        node_defs = {
            name: node
            for name in required_nodes
            if (node := self.nodes.get_node(name)) is not None
        }
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
        outcome_var = "spoofing"

        # Perform inference
        result = self.inference_engine.query(variables=[outcome_var], evidence=evidence)

        # Extract risk scores
        risk_scores = {
            "overall_score": float(result.values[1]),  # Probability of spoofing
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
                return "Immediate investigation required - potential spoofing detected"
            else:
                return "Investigation required with additional evidence collection"
        elif risk_level == "MEDIUM":
            return "Enhanced monitoring recommended - elevated spoofing risk"
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
                "order_clustering",
                "price_impact_ratio",
                "volume_participation",
                "order_behavior",
                "intent_to_execute",
                "order_cancellation",
            ]
        else:
            return [
                "order_clustering",
                "price_impact_ratio",
                "volume_participation",
                "order_behavior",
                "intent_to_execute",
                "order_cancellation",
            ]

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Model information dictionary
        """
        return {
            "model_type": "spoofing",
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
        Generate regulatory explainability evidence for spoofing detection.
        
        Args:
            evidence: Input evidence dictionary
            inference_result: Model inference results
            account_id: Account identifier
            timestamp: Evidence timestamp
            
        Returns:
            List of evidence items for regulatory explanation
        """
        evidence_items = []
        
        # Trading pattern evidence
        if 'order_pattern_anomaly' in evidence:
            evidence_items.append(EvidenceItem(
                evidence_type=EvidenceType.TRADING_PATTERN,
                account_id=account_id,
                timestamp=datetime.fromisoformat(timestamp),
                description=f"Spoofing pattern detected: Order pattern anomaly score {evidence['order_pattern_anomaly']:.2f}",
                strength=evidence['order_pattern_anomaly'],
                reliability=0.85,
                regulatory_relevance={
                    RegulatoryFramework.MAR_ARTICLE_12: 0.9,
                    RegulatoryFramework.STOR_REQUIREMENTS: 0.8
                },
                raw_data={
                    'model_type': 'spoofing_detection',
                    'evidence_node': 'order_pattern_anomaly',
                    'score': evidence['order_pattern_anomaly'],
                    'inference_result': inference_result
                }
            ))
        
        # Timing anomaly evidence
        if 'temporal_clustering' in evidence:
            evidence_items.append(EvidenceItem(
                evidence_type=EvidenceType.TIMING_ANOMALY,
                account_id=account_id,
                timestamp=datetime.fromisoformat(timestamp),
                description=f"Temporal clustering in spoofing behavior: {evidence['temporal_clustering']:.2f}",
                strength=evidence['temporal_clustering'],
                reliability=0.80,
                regulatory_relevance={
                    RegulatoryFramework.MAR_ARTICLE_12: 0.8,
                    RegulatoryFramework.STOR_REQUIREMENTS: 0.7
                },
                raw_data={
                    'model_type': 'spoofing_detection',
                    'evidence_node': 'temporal_clustering',
                    'score': evidence['temporal_clustering'],
                    'inference_result': inference_result
                }
            ))
        
        # Market impact evidence
        if 'market_impact' in evidence:
            evidence_items.append(EvidenceItem(
                evidence_type=EvidenceType.TRADING_PATTERN,
                account_id=account_id,
                timestamp=datetime.fromisoformat(timestamp),
                description=f"Market impact from spoofing activity: {evidence['market_impact']:.2f}",
                strength=evidence['market_impact'],
                reliability=0.90,
                regulatory_relevance={
                    RegulatoryFramework.MAR_ARTICLE_12: 0.95,
                    RegulatoryFramework.STOR_REQUIREMENTS: 0.85
                },
                raw_data={
                    'model_type': 'spoofing_detection',
                    'evidence_node': 'market_impact',
                    'score': evidence['market_impact'],
                    'inference_result': inference_result
                }
            ))
        
        return evidence_items
    
    def get_regulatory_framework_mapping(self) -> Dict[RegulatoryFramework, Dict[str, Any]]:
        """
        Get regulatory framework mapping for spoofing detection.
        
        Returns:
            Dictionary mapping regulatory frameworks to their requirements
        """
        return {
            RegulatoryFramework.MAR_ARTICLE_12: {
                "description": "Market manipulation through spoofing and layering",
                "key_indicators": [
                    "Order pattern anomalies",
                    "Market impact assessment", 
                    "Temporal clustering of orders",
                    "Intent to mislead other market participants"
                ],
                "evidence_threshold": 0.7,
                "reporting_requirements": "Detailed pattern analysis required"
            },
            RegulatoryFramework.STOR_REQUIREMENTS: {
                "description": "Suspicious order reporting for spoofing behavior",
                "key_indicators": [
                    "Systematic order placement and cancellation",
                    "Price manipulation intent",
                    "Market distortion effects"
                ],
                "evidence_threshold": 0.6,
                "reporting_requirements": "Order-level transaction details"
            }
        }
