"""
Circular Trading Detection Model.

This module contains the main CircularTradingModel class that encapsulates
the Bayesian network for detecting circular trading activities.
"""

import logging
from typing import Any, Dict, List, Optional

from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork

from ..shared.esi import EvidenceSufficiencyIndex
from ..shared.fallback_logic import FallbackLogic
from .config import CircularTradingConfig
from .nodes import CircularTradingNodes

logger = logging.getLogger(__name__)


class CircularTradingModel:
    """
    Circular trading detection model using Bayesian networks.

    This class provides a complete interface for circular trading risk assessment,
    including model building, inference, and evidence sufficiency analysis.
    """

    def __init__(
        self, use_latent_intent: bool = True, config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the circular trading model.

        Args:
            use_latent_intent: Whether to use latent intent modeling
            config: Optional model configuration
        """
        self.use_latent_intent = use_latent_intent
        self.config = CircularTradingConfig(config or {})
        self.nodes = CircularTradingNodes()
        self.fallback_logic = FallbackLogic()
        self.esi_calculator = EvidenceSufficiencyIndex()

        # Build the Bayesian network
        self.model = self._build_model()
        self.inference_engine = VariableElimination(self.model)

        logger.info(
            f"Circular trading model initialized (latent_intent={use_latent_intent})"
        )

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
        Build the standard circular trading Bayesian network.

        Returns:
            Standard Bayesian network
        """
        # Create the network structure
        model = DiscreteBayesianNetwork()

        # Add nodes
        nodes = [
            "counterparty_relationship",
            "risk_transfer_analysis",
            "price_negotiation_pattern",
            "settlement_coordination",
            "beneficial_ownership",
            "trade_sequence_analysis",
            "risk_factor",
            "circular_trading",
        ]

        model.add_nodes_from(nodes)

        # Add edges - evidence nodes to risk factor
        evidence_nodes = [
            "counterparty_relationship",
            "risk_transfer_analysis",
            "price_negotiation_pattern",
            "settlement_coordination",
            "beneficial_ownership",
            "trade_sequence_analysis",
        ]

        for evidence_node in evidence_nodes:
            model.add_edge(evidence_node, "risk_factor")

        # Add edge from risk factor to outcome
        model.add_edge("risk_factor", "circular_trading")

        # Add CPDs (placeholder - would need proper CPDs in production)
        self._add_cpds(model, use_latent_intent=False)

        return model

    def _build_latent_intent_model(self) -> DiscreteBayesianNetwork:
        """
        Build the latent intent circular trading Bayesian network.

        Returns:
            Latent intent Bayesian network
        """
        # Create the network structure
        model = DiscreteBayesianNetwork()

        # Add nodes
        nodes = [
            "counterparty_relationship",
            "risk_transfer_analysis",
            "price_negotiation_pattern",
            "settlement_coordination",
            "beneficial_ownership",
            "trade_sequence_analysis",
            "coordination_latent_intent",
            "risk_factor",
            "circular_trading",
        ]

        model.add_nodes_from(nodes)

        # Add edges - evidence nodes to latent intent
        evidence_nodes = [
            "counterparty_relationship",
            "risk_transfer_analysis",
            "price_negotiation_pattern",
            "settlement_coordination",
            "beneficial_ownership",
            "trade_sequence_analysis",
        ]

        for evidence_node in evidence_nodes:
            model.add_edge(evidence_node, "coordination_latent_intent")

        # Add edge from latent intent to risk factor
        model.add_edge("coordination_latent_intent", "risk_factor")

        # Add edge from risk factor to outcome
        model.add_edge("risk_factor", "circular_trading")

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
            "counterparty_relationship",
            "risk_transfer_analysis",
            "price_negotiation_pattern",
            "settlement_coordination",
            "beneficial_ownership",
            "trade_sequence_analysis",
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

        # Add CPDs for latent intent or risk factor
        if use_latent_intent:
            # Latent intent CPD (corrected: evidence matches parents)
            coordination_intent_cpd = TabularCPD(
                variable="coordination_latent_intent",
                variable_card=3,
                values=np.full(
                    (3, 729), 1 / 3
                ),  # 6 evidence nodes, 3^6=729 combinations
                evidence=[
                    "counterparty_relationship",
                    "risk_transfer_analysis",
                    "price_negotiation_pattern",
                    "settlement_coordination",
                    "beneficial_ownership",
                    "trade_sequence_analysis",
                ],
                evidence_card=[3, 3, 3, 3, 3, 3],
            )
            model.add_cpds(coordination_intent_cpd)

            # Risk factor CPD (depends on latent intent)
            risk_factor_cpd = TabularCPD(
                variable="risk_factor",
                variable_card=3,
                values=np.array(
                    [
                        [0.85, 0.4, 0.1],  # Low risk
                        [0.12, 0.35, 0.3],  # Medium risk
                        [0.03, 0.25, 0.6],  # High risk
                    ]
                ),
                evidence=["coordination_latent_intent"],
                evidence_card=[3],
            )
            model.add_cpds(risk_factor_cpd)
        else:
            # Standard risk factor CPD
            risk_factor_cpd = TabularCPD(
                variable="risk_factor",
                variable_card=3,
                values=np.array([[0.8, 0.15, 0.05]]).T,
            )
            model.add_cpds(risk_factor_cpd)

        # Outcome CPD
        outcome_cpd = TabularCPD(
            variable="circular_trading",
            variable_card=2,
            values=np.array(
                [
                    [0.97, 0.75, 0.15],  # No circular trading
                    [0.03, 0.25, 0.85],  # Circular trading
                ]
            ),
            evidence=["risk_factor"],
            evidence_card=[3],
        )
        model.add_cpds(outcome_cpd)

    def calculate_risk(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate circular trading risk based on evidence.

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
                    "model_type": "circular_trading",
                    "use_latent_intent": self.use_latent_intent,
                    "inference_method": "variable_elimination",
                },
            }

        except Exception as e:
            logger.error(f"Error calculating circular trading risk: {str(e)}")
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
        outcome_var = "circular_trading"

        # Perform inference
        result = self.inference_engine.query(variables=[outcome_var], evidence=evidence)

        # Extract risk scores
        risk_scores = {
            "overall_score": float(result.values[1]),  # Probability of circular trading
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
                return "Immediate investigation required - potential circular trading detected"
            else:
                return "Investigation required with additional evidence collection"
        elif risk_level == "MEDIUM":
            return "Enhanced monitoring recommended - elevated circular trading risk"
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
                "counterparty_relationship",
                "risk_transfer_analysis",
                "price_negotiation_pattern",
                "settlement_coordination",
                "beneficial_ownership",
                "trade_sequence_analysis",
            ]
        else:
            return [
                "counterparty_relationship",
                "risk_transfer_analysis",
                "price_negotiation_pattern",
                "settlement_coordination",
                "beneficial_ownership",
                "trade_sequence_analysis",
            ]

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Model information dictionary
        """
        return {
            "model_type": "circular_trading",
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
