"""
Commodity manipulation model nodes definitions.

This module contains node definitions and helpers specific to the
commodity manipulation detection model.
"""

from typing import Any, Dict, Optional

from ..shared.node_library import BayesianNode, BayesianNodeLibrary


class CommodityManipulationNodes:
    """
    Helper class for managing commodity manipulation model nodes.

    This class provides easy access to node definitions and templates
    specific to commodity manipulation detection.
    """

    def __init__(self):
        """Initialize the commodity manipulation nodes helper."""
        self.node_library = BayesianNodeLibrary()

        # Define commodity manipulation specific nodes
        self.node_definitions = {
            "liquidity_context": {
                "type": "liquidity_context",
                "states": ["liquid", "moderate", "illiquid"],
                "description": "Market liquidity conditions",
                "fallback_prior": [0.6, 0.3, 0.1],
            },
            "benchmark_timing": {
                "type": "benchmark_timing",
                "states": ["outside_window", "near_window", "during_window"],
                "description": "Benchmark window activity",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            "order_clustering": {
                "type": "order_clustering",
                "states": [
                    "normal_distribution",
                    "moderate_clustering",
                    "high_clustering",
                ],
                "description": "Order clustering analysis",
                "fallback_prior": [0.7, 0.25, 0.05],
            },
            "price_impact_ratio": {
                "type": "price_impact_ratio",
                "states": ["normal_impact", "elevated_impact", "excessive_impact"],
                "description": "Price impact ratio analysis",
                "fallback_prior": [0.75, 0.2, 0.05],
            },
            "volume_participation": {
                "type": "volume_participation",
                "states": [
                    "normal_participation",
                    "high_participation",
                    "dominant_participation",
                ],
                "description": "Volume participation analysis",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            "cross_venue_coordination": {
                "type": "cross_venue_coordination",
                "states": [
                    "no_coordination",
                    "weak_coordination",
                    "strong_coordination",
                ],
                "description": "Cross-venue coordination patterns",
                "fallback_prior": [0.85, 0.12, 0.03],
            },
            "manipulation_latent_intent": {
                "type": "manipulation_latent_intent",
                "states": ["no_intent", "potential_intent", "clear_intent"],
                "description": "Latent manipulation intent",
                "fallback_prior": [0.95, 0.04, 0.01],
            },
            "risk_factor": {
                "type": "risk_factor",
                "states": ["low", "medium", "high"],
                "description": "Latent risk factor",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            "commodity_manipulation": {
                "type": "outcome",
                "states": ["no", "yes"],
                "description": "Commodity manipulation outcome",
                "fallback_prior": [0.99, 0.01],
            },
        }

    def get_node(self, node_name: str) -> Optional[BayesianNode]:
        """
        Get a node by name.

        Args:
            node_name: Name of the node

        Returns:
            BayesianNode instance or None
        """
        if node_name not in self.node_definitions:
            return None

        node_def = self.node_definitions[node_name]

        # Create the node using the library
        node = self.node_library.create_node(
            node_type=node_def["type"],
            name=node_name,
            states=node_def["states"],
            description=node_def["description"],
            fallback_prior=node_def["fallback_prior"],
        )

        return node

    def get_all_nodes(self) -> Dict[str, BayesianNode]:
        """
        Get all nodes for the commodity manipulation model.

        Returns:
            Dictionary of all nodes
        """
        nodes = {}
        for node_name in self.node_definitions.keys():
            nodes[node_name] = self.get_node(node_name)

        return nodes

    def get_evidence_nodes(self) -> Dict[str, BayesianNode]:
        """
        Get only the evidence nodes.

        Returns:
            Dictionary of evidence nodes
        """
        evidence_nodes = {}

        for node_name, node_def in self.node_definitions.items():
            if node_def["type"] in [
                "liquidity_context",
                "benchmark_timing",
                "order_clustering",
                "price_impact_ratio",
                "volume_participation",
                "cross_venue_coordination",
            ]:
                evidence_nodes[node_name] = self.get_node(node_name)

        return evidence_nodes

    def get_node_states(self, node_name: str) -> Optional[list]:
        """
        Get the states for a specific node.

        Args:
            node_name: Name of the node

        Returns:
            List of node states or None
        """
        if node_name in self.node_definitions:
            return self.node_definitions[node_name]["states"]
        return None

    def get_standard_nodes(self) -> list:
        """Get the standard (non-latent intent) node names."""
        return [
            "liquidity_context",
            "benchmark_timing",
            "order_clustering",
            "price_impact_ratio",
            "volume_participation",
            "cross_venue_coordination",
            "risk_factor",
            "commodity_manipulation",
        ]

    def get_latent_intent_nodes(self) -> list:
        """Get the latent intent model node names."""
        return [
            "liquidity_context",
            "benchmark_timing",
            "order_clustering",
            "price_impact_ratio",
            "volume_participation",
            "cross_venue_coordination",
            "manipulation_latent_intent",
            "risk_factor",
            "commodity_manipulation",
        ]

    def validate_node_value(self, node_name: str, value: Any) -> bool:
        """
        Validate a value for a specific node.

        Args:
            node_name: Name of the node
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        if node_name not in self.node_definitions:
            return False

        states = self.node_definitions[node_name]["states"]

        # Check if value is a valid state index
        if isinstance(value, int):
            return 0 <= value < len(states)

        # Check if value is a valid state name
        if isinstance(value, str):
            return value in states

        return False
