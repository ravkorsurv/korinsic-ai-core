"""
Cross-Desk Collusion Model Nodes.

This module provides node definitions and management for the cross-desk collusion
detection model, including evidence nodes and latent intent nodes.
"""

import logging
from typing import Any, Dict, Optional

from ..shared.node_library import BayesianNodeLibrary

logger = logging.getLogger(__name__)


class CrossDeskCollusionNodes:
    """
    Node management class for cross-desk collusion detection model.

    This class manages all node definitions and provides methods for creating
    and configuring nodes used in the cross-desk collusion Bayesian network.
    """

    def __init__(self):
        """Initialize the node manager."""
        self.node_library = BayesianNodeLibrary()
        self.node_definitions = self._get_node_definitions()

        logger.info("Cross-desk collusion nodes initialized")

    def _get_node_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get node definitions for cross-desk collusion model.

        Returns:
            Dictionary of node definitions
        """
        return {
            "comms_metadata": {
                "type": "comms_metadata",
                "states": ["normal_comms", "unusual_comms", "suspicious_comms"],
                "description": "Cross-desk communication patterns analysis",
                "fallback_prior": [0.80, 0.15, 0.05],
                "evidence_type": "communication",
            },
            "profit_motivation": {
                "type": "profit_motivation",
                "states": ["normal_profit", "unusual_profit", "suspicious_profit"],
                "description": "Unusual profit sharing indicators across desks",
                "fallback_prior": [0.75, 0.20, 0.05],
                "evidence_type": "financial",
            },
            "order_behavior": {
                "type": "order_behavior",
                "states": [
                    "normal_behavior",
                    "unusual_behavior",
                    "suspicious_behavior",
                ],
                "description": "Order synchronization patterns across desks",
                "fallback_prior": [0.70, 0.25, 0.05],
                "evidence_type": "trading",
            },
            "cross_venue_coordination": {
                "type": "cross_venue_coordination",
                "states": [
                    "no_coordination",
                    "weak_coordination",
                    "strong_coordination",
                ],
                "description": "Trading correlation across desks and venues",
                "fallback_prior": [0.85, 0.12, 0.03],
                "evidence_type": "trading",
            },
            "access_pattern": {
                "type": "access_pattern",
                "states": ["normal_access", "unusual_access", "suspicious_access"],
                "description": "Information sharing patterns between desks",
                "fallback_prior": [0.78, 0.18, 0.04],
                "evidence_type": "information",
            },
            "market_segmentation": {
                "type": "market_segmentation",
                "states": ["competitive", "segmented", "coordinated_division"],
                "description": "Market division patterns indicating collusion",
                "fallback_prior": [0.82, 0.15, 0.03],
                "evidence_type": "market",
            },
            "collusion_latent_intent": {
                "type": "collusion_latent_intent",
                "states": [
                    "independent_trading",
                    "coordinated_trading",
                    "collusive_trading",
                ],
                "description": "Hidden collusion intent across trading desks",
                "fallback_prior": [0.90, 0.08, 0.02],
                "evidence_type": "latent",
            },
            "risk_factor": {
                "type": "risk_factor",
                "states": ["low_risk", "medium_risk", "high_risk"],
                "description": "Intermediate risk assessment factor",
                "fallback_prior": [0.85, 0.12, 0.03],
                "evidence_type": "intermediate",
            },
            "cross_desk_collusion": {
                "type": "outcome",
                "states": ["no_collusion", "collusion_detected"],
                "description": "Cross-desk collusion detection outcome",
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
                "communication",
                "financial",
                "trading",
                "information",
                "market",
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
            "comms_metadata",
            "profit_motivation",
            "order_behavior",
            "cross_venue_coordination",
            "access_pattern",
            "market_segmentation",
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
            raise ValueError(f"Error validating node {node_name}: {str(e)}")

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
                "communication",
                "financial",
                "trading",
                "information",
                "market",
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
        return f"CrossDeskCollusionNodes(total_nodes={stats['total_nodes']}, evidence_nodes={stats['evidence_nodes']})"
