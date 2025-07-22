"""
Circular trading model nodes definitions.

This module contains node definitions and helpers specific to the
circular trading detection model.
"""

from typing import Any, Dict, Optional

from ..shared.node_library import BayesianNode, BayesianNodeLibrary


class CircularTradingNodes:
    """
    Helper class for managing circular trading model nodes.

    This class provides easy access to node definitions and templates
    specific to circular trading detection.
    """

    def __init__(self):
        """Initialize the circular trading nodes helper."""
        self.node_library = BayesianNodeLibrary()

        # Define circular trading specific nodes
        self.node_definitions = {
            "counterparty_relationship": {
                "type": "counterparty_relationship",
                "states": ["unrelated", "connected", "closely_related"],
                "description": "Counterparty relationship analysis",
                "fallback_prior": [0.7, 0.25, 0.05],
            },
            "risk_transfer_analysis": {
                "type": "risk_transfer_analysis",
                "states": ["genuine_transfer", "limited_transfer", "no_transfer"],
                "description": "Risk transfer analysis",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            "price_negotiation_pattern": {
                "type": "price_negotiation_pattern",
                "states": ["market_driven", "coordinated", "artificial"],
                "description": "Price negotiation pattern analysis",
                "fallback_prior": [0.75, 0.2, 0.05],
            },
            "settlement_coordination": {
                "type": "settlement_coordination",
                "states": ["independent", "synchronized", "coordinated"],
                "description": "Settlement coordination patterns",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            "beneficial_ownership": {
                "type": "beneficial_ownership",
                "states": [
                    "separate_ownership",
                    "shared_interests",
                    "common_ownership",
                ],
                "description": "Beneficial ownership analysis",
                "fallback_prior": [0.85, 0.12, 0.03],
            },
            "trade_sequence_analysis": {
                "type": "trade_sequence_analysis",
                "states": [
                    "random_sequence",
                    "structured_sequence",
                    "circular_sequence",
                ],
                "description": "Trade sequence pattern analysis",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            "coordination_latent_intent": {
                "type": "coordination_latent_intent",
                "states": ["no_intent", "potential_intent", "clear_intent"],
                "description": "Latent coordination intent",
                "fallback_prior": [0.95, 0.04, 0.01],
            },
            "risk_factor": {
                "type": "risk_factor",
                "states": ["low", "medium", "high"],
                "description": "Latent risk factor",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            "circular_trading": {
                "type": "outcome",
                "states": ["no", "yes"],
                "description": "Circular trading outcome",
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
        Get all nodes for the circular trading model.

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
                "counterparty_relationship",
                "risk_transfer_analysis",
                "price_negotiation_pattern",
                "settlement_coordination",
                "beneficial_ownership",
                "trade_sequence_analysis",
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
            "counterparty_relationship",
            "risk_transfer_analysis",
            "price_negotiation_pattern",
            "settlement_coordination",
            "beneficial_ownership",
            "trade_sequence_analysis",
            "risk_factor",
            "circular_trading",
        ]

    def get_latent_intent_nodes(self) -> list:
        """Get the latent intent model node names."""
        return [
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
