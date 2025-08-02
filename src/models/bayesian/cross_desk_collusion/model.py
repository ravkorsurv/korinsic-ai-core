"""
Cross-Desk Collusion Detection Model.

This module contains the main CrossDeskCollusionModel class that encapsulates
the Bayesian network for detecting collusive behavior between trading desks.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork

from ..shared.esi import EvidenceSufficiencyIndex
from ..shared.fallback_logic import FallbackLogic

# Add intermediate nodes import
from ..shared.intermediate_nodes import (
    MarketImpactIntermediateNode,
    BehavioralIntentIntermediateNode,
    create_intermediate_cpt
)

# Add regulatory explainability import
from ....core.regulatory_explainability import (
    RegulatoryExplainabilityEngine,
    EvidenceItem,
    EvidenceType,
    RegulatoryFramework
)
from .config import CrossDeskCollusionConfig
from .nodes import CrossDeskCollusionNodes

logger = logging.getLogger(__name__)


class CrossDeskCollusionModel:
    """
    Cross-desk collusion detection model using Bayesian networks.

    This class provides a complete interface for cross-desk collusion risk assessment,
    including model building, inference, and evidence sufficiency analysis.
    
    REFACTORED: Now uses 2 intermediate nodes to reduce fan-in from 6→2 parents.
    """

    def __init__(
        self, use_latent_intent: bool = True, config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the cross-desk collusion model.

        Args:
            use_latent_intent: Whether to use latent intent modeling
            config: Optional model configuration
        """
        self.use_latent_intent = use_latent_intent
        self.config = CrossDeskCollusionConfig(config or {})
        self.nodes = CrossDeskCollusionNodes()
        self.fallback_logic = FallbackLogic()
        self.esi_calculator = EvidenceSufficiencyIndex()

        # Initialize regulatory explainability engine
        self.explainability_engine = RegulatoryExplainabilityEngine(config or {})

        # Initialize intermediate nodes for fan-in reduction
        self.intermediate_nodes = self._initialize_intermediate_nodes()

        # Build the Bayesian network
        self.model = self._build_model()
        self.inference_engine = VariableElimination(self.model)

        logger.info(
            f"Cross-desk collusion model initialized (latent_intent={use_latent_intent}, "
            f"intermediate_nodes={len(self.intermediate_nodes)})"
        )

    def _initialize_intermediate_nodes(self) -> Dict[str, Any]:
        """Initialize intermediate nodes for cross-desk collusion model fan-in reduction."""
        return {
            "coordination_patterns": MarketImpactIntermediateNode(
                name="coordination_patterns_intermediate",
                parent_nodes=["cross_venue_coordination", "access_pattern", "market_segmentation"],
                description="Cross-desk coordination pattern indicators"
            ),
            "communication_intent": BehavioralIntentIntermediateNode(
                name="communication_intent_intermediate", 
                parent_nodes=["comms_metadata", "profit_motivation", "order_behavior"],
                description="Communication and behavioral intent indicators"
            )
        }

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
        Build the standard cross-desk collusion Bayesian network.

        Returns:
            Standard Bayesian network
        """
        # Create the network structure
        model = DiscreteBayesianNetwork()

        # Add nodes
        nodes = [
            "comms_metadata",
            "profit_motivation",
            "order_behavior",
            "cross_venue_coordination",
            "access_pattern",
            "market_segmentation",
            "risk_factor",
            "cross_desk_collusion",
        ]

        model.add_nodes_from(nodes)

        # Add edges - evidence nodes to risk factor
        evidence_nodes = [
            "comms_metadata",
            "profit_motivation",
            "order_behavior",
            "cross_venue_coordination",
            "access_pattern",
            "market_segmentation",
        ]

        for evidence_node in evidence_nodes:
            model.add_edge(evidence_node, "risk_factor")

        # Add edge from risk factor to outcome
        model.add_edge("risk_factor", "cross_desk_collusion")

        # Add CPDs (placeholder - would need proper CPDs in production)
        self._add_cpds(model, use_latent_intent=False)

        return model

    def _build_latent_intent_model(self) -> DiscreteBayesianNetwork:
        """
        Build the latent intent cross-desk collusion Bayesian network.
        REFACTORED: Uses 2 intermediate nodes instead of 6 direct parents to latent intent.

        Returns:
            Latent intent Bayesian network
        """
        # Create the network structure
        model = DiscreteBayesianNetwork()

        # Add nodes (evidence + intermediate + latent + outcome)
        nodes = [
            # Evidence nodes
            "comms_metadata",
            "profit_motivation",
            "order_behavior",
            "cross_venue_coordination",
            "access_pattern",
            "market_segmentation",
            # Intermediate nodes
            "coordination_patterns_intermediate",
            "communication_intent_intermediate",
            # Latent and outcome nodes
            "collusion_latent_intent",
            "risk_factor",
            "cross_desk_collusion",
        ]

        model.add_nodes_from(nodes)

        # Add edges - evidence nodes to intermediate nodes
        coordination_evidence = ["cross_venue_coordination", "access_pattern", "market_segmentation"]
        for evidence_node in coordination_evidence:
            model.add_edge(evidence_node, "coordination_patterns_intermediate")

        communication_evidence = ["comms_metadata", "profit_motivation", "order_behavior"]
        for evidence_node in communication_evidence:
            model.add_edge(evidence_node, "communication_intent_intermediate")

        # Add edges - intermediate nodes to latent intent (2 parents instead of 6)
        model.add_edge("coordination_patterns_intermediate", "collusion_latent_intent")
        model.add_edge("communication_intent_intermediate", "collusion_latent_intent")

        # Add edge from latent intent to risk factor
        model.add_edge("collusion_latent_intent", "risk_factor")

        # Add edge from risk factor to outcome
        model.add_edge("risk_factor", "cross_desk_collusion")

        # Add CPDs
        self._add_cpds(model, use_latent_intent=True)

        return model

    def _add_cpds(
        self, model: DiscreteBayesianNetwork, use_latent_intent: bool = False
    ):
        """
        Add Conditional Probability Distributions to the model.
        REFACTORED: Uses intermediate nodes with noisy-OR CPTs.
        """
        import numpy as np
        from pgmpy.factors.discrete import TabularCPD

        # Evidence node CPDs (prior probabilities)
        evidence_cpds = [
            TabularCPD(variable="comms_metadata", variable_card=3, values=[[0.75], [0.20], [0.05]]),
            TabularCPD(variable="profit_motivation", variable_card=3, values=[[0.70], [0.25], [0.05]]),
            TabularCPD(variable="order_behavior", variable_card=3, values=[[0.70], [0.25], [0.05]]),
            TabularCPD(variable="cross_venue_coordination", variable_card=3, values=[[0.80], [0.15], [0.05]]),
            TabularCPD(variable="access_pattern", variable_card=3, values=[[0.75], [0.20], [0.05]]),
            TabularCPD(variable="market_segmentation", variable_card=3, values=[[0.85], [0.12], [0.03]]),
        ]
        model.add_cpds(*evidence_cpds)

        # Intermediate node CPDs using noisy-OR
        coordination_cpd = create_intermediate_cpt(
            self.intermediate_nodes["coordination_patterns"],
            ["cross_venue_coordination", "access_pattern", "market_segmentation"],
            cpt_type="noisy_or"
        )
        model.add_cpds(coordination_cpd)

        communication_cpd = create_intermediate_cpt(
            self.intermediate_nodes["communication_intent"],
            ["comms_metadata", "profit_motivation", "order_behavior"],
            cpt_type="noisy_or"
        )
        model.add_cpds(communication_cpd)

        if use_latent_intent:
            # Latent intent CPD (2 intermediate parents → 9 combinations vs 729)
            collusion_intent_cpd = TabularCPD(
                variable="collusion_latent_intent",
                variable_card=3,
                values=np.array([
                    # coordination_patterns: low, medium, high
                    # communication_intent: benign, suspicious, malicious
                    [0.95, 0.80, 0.50, 0.70, 0.40, 0.20, 0.30, 0.15, 0.05],  # no_collusion
                    [0.04, 0.15, 0.35, 0.25, 0.40, 0.45, 0.40, 0.35, 0.25],  # potential_collusion
                    [0.01, 0.05, 0.15, 0.05, 0.20, 0.35, 0.30, 0.50, 0.70],  # clear_collusion
                ]),
                evidence=["coordination_patterns_intermediate", "communication_intent_intermediate"],
                evidence_card=[3, 3],
            )
            model.add_cpds(collusion_intent_cpd)

            # Risk factor CPD (depends on latent intent)
            risk_factor_cpd = TabularCPD(
                variable="risk_factor",
                variable_card=3,
                values=np.array(
                    [
                        [0.88, 0.50, 0.15],  # Low risk
                        [0.10, 0.35, 0.35],  # Medium risk
                        [0.02, 0.15, 0.50],  # High risk
                    ]
                ),
                evidence=["collusion_latent_intent"],
                evidence_card=[3],
            )
            model.add_cpds(risk_factor_cpd)
        else:
            # Standard risk factor CPD (corrected: evidence matches parents)
            risk_factor_cpd = TabularCPD(
                variable="risk_factor",
                variable_card=3,
                values=np.full(
                    (3, 729), 1 / 3
                ),  # 6 evidence nodes, 3^6=729 combinations
                evidence=[
                    "comms_metadata",
                    "profit_motivation",
                    "order_behavior",
                    "cross_venue_coordination",
                    "access_pattern",
                    "market_segmentation",
                ],
                evidence_card=[3, 3, 3, 3, 3, 3],
            )
            model.add_cpds(risk_factor_cpd)

        # Outcome CPD
        outcome_cpd = TabularCPD(
            variable="cross_desk_collusion",
            variable_card=2,
            values=np.array(
                [
                    [0.98, 0.80, 0.25],  # No collusion
                    [0.02, 0.20, 0.75],  # Collusion detected
                ]
            ),
            evidence=["risk_factor"],
            evidence_card=[3],
        )
        model.add_cpds(outcome_cpd)

    def calculate_risk(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate cross-desk collusion risk based on evidence.

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
                    "model_type": "cross_desk_collusion",
                    "use_latent_intent": self.use_latent_intent,
                    "inference_method": "variable_elimination",
                },
            }

        except Exception as e:
            logger.error(f"Error calculating cross-desk collusion risk: {str(e)}")
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
        outcome_var = "cross_desk_collusion"

        # Perform inference
        result = self.inference_engine.query(variables=[outcome_var], evidence=evidence)

        # Extract risk scores
        risk_scores = {
            "overall_score": float(result.values[1]),  # Probability of collusion
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
                return "Immediate investigation required - potential cross-desk collusion detected"
            else:
                return "Investigation required with additional evidence collection"
        elif risk_level == "MEDIUM":
            return "Enhanced monitoring recommended - elevated collusion risk"
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
                "comms_metadata",
                "profit_motivation",
                "order_behavior",
                "cross_venue_coordination",
                "access_pattern",
                "market_segmentation",
            ]
        else:
            return [
                "comms_metadata",
                "profit_motivation",
                "order_behavior",
                "cross_venue_coordination",
                "access_pattern",
                "market_segmentation",
            ]

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Model information dictionary
        """
        return {
            "model_type": "cross_desk_collusion",
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
        Generate regulatory explainability evidence for cross desk collusion detection.
        
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
                    description=f"Cross Desk Collusion indicator: {evidence_key} = {evidence_value:.2f}",
                    strength=min(float(evidence_value), 1.0),
                    reliability=0.85,
                    regulatory_relevance={
                        RegulatoryFramework.MAR_ARTICLE_8: 0.9,
                        RegulatoryFramework.STOR_REQUIREMENTS: 0.8
                    },
                    raw_data={
                        'model_type': 'cross_desk_collusion',
                        'evidence_node': evidence_key,
                        'score': evidence_value,
                        'inference_result': inference_result
                    }
                ))
        
        return evidence_items
    
    def get_regulatory_framework_mapping(self) -> Dict[RegulatoryFramework, Dict[str, Any]]:
        """
        Get regulatory framework mapping for cross desk collusion detection.
        
        Returns:
            Dictionary mapping regulatory frameworks to their requirements
        """
        return {
            RegulatoryFramework.MAR_ARTICLE_8: {
                "description": "Cross Desk Collusion detection and analysis",
                "key_indicators": ['Inter-desk communication patterns', 'Coordinated trading strategies', 'Information sharing evidence'],
                "evidence_threshold": 0.7,
                "reporting_requirements": "Detailed pattern analysis required"
            },
            RegulatoryFramework.STOR_REQUIREMENTS: {
                "description": "Suspicious transaction reporting for cross desk collusion behavior",
                "key_indicators": ['Inter-desk communication patterns', 'Coordinated trading strategies'],
                "evidence_threshold": 0.6,
                "reporting_requirements": "Transaction-level details required"
            }
        }

