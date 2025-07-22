"""
Enhanced Spoofing Model Nodes.

This module provides node definitions and management for the spoofing detection model,
including evidence nodes and latent intent nodes for spoofing behavior detection.
"""

import logging
from typing import Any, Dict, Optional

from ..shared.node_library import BayesianNodeLibrary

logger = logging.getLogger(__name__)


class SpoofingNodes:
    """
    Node management class for spoofing detection model.

    This class manages all node definitions and provides methods for creating
    and configuring nodes used in the spoofing detection Bayesian network.
    """

    def __init__(self):
        """Initialize the node manager."""
        self.node_library = BayesianNodeLibrary()
        self.node_definitions = self._get_node_definitions()

        logger.info("Spoofing nodes initialized")

    def _get_node_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get node definitions for spoofing detection model.

        Returns:
            Dictionary of node definitions
        """
        return {
            "order_clustering": {
                "type": "order_clustering",
                "states": [
                    "normal_distribution",
                    "moderate_clustering",
                    "high_clustering",
                ],
                "description": "Order layering pattern detection",
                "fallback_prior": [0.70, 0.25, 0.05],
                "evidence_type": "order_pattern",
            },
            "price_impact_ratio": {
                "type": "price_impact_ratio",
                "states": ["normal_impact", "elevated_impact", "excessive_impact"],
                "description": "Market impact analysis of spoofing activity",
                "fallback_prior": [0.75, 0.20, 0.05],
                "evidence_type": "market_impact",
            },
            "volume_participation": {
                "type": "volume_participation",
                "states": [
                    "normal_participation",
                    "high_participation",
                    "dominant_participation",
                ],
                "description": "Volume impact and participation analysis",
                "fallback_prior": [0.72, 0.23, 0.05],
                "evidence_type": "volume_pattern",
            },
            "order_behavior": {
                "type": "order_behavior",
                "states": [
                    "normal_behavior",
                    "unusual_behavior",
                    "suspicious_behavior",
                ],
                "description": "Order behavior pattern analysis",
                "fallback_prior": [0.70, 0.25, 0.05],
                "evidence_type": "behavior_pattern",
            },
            "intent_to_execute": {
                "type": "intent_to_execute",
                "states": ["genuine_intent", "uncertain_intent", "no_intent"],
                "description": "Genuine intent to execute order analysis",
                "fallback_prior": [0.80, 0.15, 0.05],
                "evidence_type": "execution_intent",
            },
            "order_cancellation": {
                "type": "order_cancellation",
                "states": [
                    "normal_cancellation",
                    "suspicious_cancellation",
                    "manipulative_cancellation",
                ],
                "description": "Order cancellation pattern analysis",
                "fallback_prior": [0.75, 0.20, 0.05],
                "evidence_type": "cancellation_pattern",
            },
            "spoofing_latent_intent": {
                "type": "spoofing_latent_intent",
                "states": [
                    "legitimate_trading",
                    "potential_spoofing",
                    "clear_spoofing",
                ],
                "description": "Hidden spoofing intent inference",
                "fallback_prior": [0.92, 0.06, 0.02],
                "evidence_type": "latent",
            },
            "risk_factor": {
                "type": "risk_factor",
                "states": ["low_risk", "medium_risk", "high_risk"],
                "description": "Intermediate risk assessment factor",
                "fallback_prior": [0.80, 0.15, 0.05],
                "evidence_type": "intermediate",
            },
            "spoofing": {
                "type": "outcome",
                "states": ["no_spoofing", "spoofing_detected"],
                "description": "Spoofing detection outcome",
                "fallback_prior": [0.95, 0.05],
                "evidence_type": "outcome",
            },
        }

    def create_node(
        self,
        node_name: str,
        description: str = "",
        fallback_prior: Optional[list] = None,
    ) -> Any:
        """
        Create a node instance.

        Args:
            node_name: Name of the node to create
            description: Optional description override
            fallback_prior: Optional fallback prior override

        Returns:
            Node instance
        """
        if node_name not in self.node_definitions:
            raise ValueError(f"Unknown node: {node_name}")

        node_def = self.node_definitions[node_name]

        # Use provided parameters or defaults
        final_description = description or node_def["description"]
        final_fallback_prior = fallback_prior or node_def["fallback_prior"]

        # Create node using the library
        node = self.node_library.create_node(
            node_type=node_def["type"],
            name=node_name,
            states=node_def["states"],
            description=final_description,
            fallback_prior=final_fallback_prior,
        )

        logger.debug(f"Created node: {node_name}")
        return node

    def get_node(self, node_name: str) -> Any:
        """
        Get a node instance (creates if not exists).

        Args:
            node_name: Name of the node

        Returns:
            Node instance
        """
        return self.create_node(node_name)

    def get_evidence_nodes(self) -> Dict[str, Any]:
        """
        Get all evidence nodes for the model.

        Returns:
            Dictionary of evidence nodes
        """
        evidence_nodes = {}

        for node_name, node_def in self.node_definitions.items():
            if node_def["evidence_type"] in [
                "order_pattern",
                "market_impact",
                "volume_pattern",
                "behavior_pattern",
                "execution_intent",
                "cancellation_pattern",
            ]:
                evidence_nodes[node_name] = self.create_node(node_name)

        return evidence_nodes

    def get_latent_nodes(self) -> Dict[str, Any]:
        """
        Get all latent nodes for the model.

        Returns:
            Dictionary of latent nodes
        """
        latent_nodes = {}

        for node_name, node_def in self.node_definitions.items():
            if node_def["evidence_type"] == "latent":
                latent_nodes[node_name] = self.create_node(node_name)

        return latent_nodes

    def get_outcome_nodes(self) -> Dict[str, Any]:
        """
        Get all outcome nodes for the model.

        Returns:
            Dictionary of outcome nodes
        """
        outcome_nodes = {}

        for node_name, node_def in self.node_definitions.items():
            if node_def["evidence_type"] == "outcome":
                outcome_nodes[node_name] = self.create_node(node_name)

        return outcome_nodes

    def get_required_evidence_nodes(self) -> list:
        """
        Get list of required evidence nodes.

        Returns:
            List of required evidence node names
        """
        return [
            "order_clustering",
            "price_impact_ratio",
            "volume_participation",
            "order_behavior",
            "intent_to_execute",
            "order_cancellation",
        ]

    def get_node_definition(self, node_name: str) -> Dict[str, Any]:
        """
        Get definition for a specific node.

        Args:
            node_name: Name of the node

        Returns:
            Node definition dictionary
        """
        if node_name not in self.node_definitions:
            raise ValueError(f"Unknown node: {node_name}")

        return self.node_definitions[node_name].copy()

    def get_all_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all node definitions.

        Returns:
            Dictionary of all node definitions
        """
        return self.node_definitions.copy()

    def validate_node_compatibility(self, node_name: str) -> bool:
        """
        Validate if a node is compatible with the model.

        Args:
            node_name: Name of the node to validate

        Returns:
            True if compatible, False otherwise
        """
        try:
            node_def = self.get_node_definition(node_name)

            # Check if node type is available in library
            if node_def["type"] not in self.node_library.get_node_classes():
                logger.error(f"Node type {node_def['type']} not available in library")
                return False

            # Check if states are properly defined
            if not node_def.get("states") or not isinstance(node_def["states"], list):
                logger.error(f"Invalid states definition for node {node_name}")
                return False

            # Check if fallback prior matches states
            if len(node_def["fallback_prior"]) != len(node_def["states"]):
                logger.error(
                    f"Fallback prior length doesn't match states for node {node_name}"
                )
                return False

            logger.debug(f"Node {node_name} is compatible")
            return True

        except Exception as e:
            logger.error(f"Error validating node {node_name}: {str(e)}")
            return False

    def get_node_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the nodes.

        Returns:
            Dictionary of node statistics
        """
        stats = {
            "total_nodes": len(self.node_definitions),
            "evidence_nodes": 0,
            "latent_nodes": 0,
            "outcome_nodes": 0,
            "intermediate_nodes": 0,
        }

        for node_def in self.node_definitions.values():
            evidence_type = node_def["evidence_type"]
            if evidence_type in [
                "order_pattern",
                "market_impact",
                "volume_pattern",
                "behavior_pattern",
                "execution_intent",
                "cancellation_pattern",
            ]:
                stats["evidence_nodes"] += 1
            elif evidence_type == "latent":
                stats["latent_nodes"] += 1
            elif evidence_type == "outcome":
                stats["outcome_nodes"] += 1
            elif evidence_type == "intermediate":
                stats["intermediate_nodes"] += 1

        return stats

    def __repr__(self) -> str:
        """String representation of the nodes manager."""
        stats = self.get_node_statistics()
        return f"SpoofingNodes(total_nodes={stats['total_nodes']}, evidence_nodes={stats['evidence_nodes']})"
