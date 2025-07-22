"""
Insider dealing model nodes definitions.

This module contains node definitions and helpers specific to the
insider dealing detection model.
"""

from typing import Any, Dict, Optional

from ..shared.node_library import BayesianNode, BayesianNodeLibrary


class InsiderDealingNodes:
    """
    Helper class for managing insider dealing model nodes.

    This class provides easy access to node definitions and templates
    specific to insider dealing detection.
    """

    def __init__(self):
        """Initialize the insider dealing nodes helper."""
        self.node_library = BayesianNodeLibrary()

        # Define insider dealing specific nodes
        self.node_definitions = {
            "trade_pattern": {
                "type": "evidence",
                "states": ["normal", "suspicious"],
                "description": "Trade pattern evidence",
                "fallback_prior": [0.95, 0.05],
            },
            "comms_intent": {
                "type": "comms_intent",
                "states": ["benign", "suspicious", "malicious"],
                "description": "Communications intent evidence",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            "pnl_drift": {
                "type": "variance_tuned",
                "states": ["normal", "anomalous"],
                "description": "PnL drift indicator",
                "fallback_prior": [0.9, 0.1],
            },
            "profit_motivation": {
                "type": "profit_motivation",
                "states": ["normal_profit", "unusual_profit", "suspicious_profit"],
                "description": "Profit motivation evidence",
                "fallback_prior": [0.85, 0.12, 0.03],
            },
            "access_pattern": {
                "type": "access_pattern",
                "states": ["normal_access", "unusual_access", "suspicious_access"],
                "description": "Access pattern evidence",
                "fallback_prior": [0.9, 0.08, 0.02],
            },
            "order_behavior": {
                "type": "order_behavior",
                "states": [
                    "normal_behavior",
                    "unusual_behavior",
                    "suspicious_behavior",
                ],
                "description": "Order behavior evidence",
                "fallback_prior": [0.88, 0.1, 0.02],
            },
            "comms_metadata": {
                "type": "comms_metadata",
                "states": ["normal_comms", "unusual_comms", "suspicious_comms"],
                "description": "Communications metadata evidence",
                "fallback_prior": [0.92, 0.06, 0.02],
            },
            "news_timing": {
                "type": "news_timing",
                "states": [
                    "normal_timing",
                    "suspicious_timing",
                    "highly_suspicious_timing",
                ],
                "description": "News-trade timing analysis",
                "fallback_prior": [0.85, 0.12, 0.03],
            },
            "state_information_access": {
                "type": "state_information",
                "states": ["no_access", "potential_access", "clear_access"],
                "description": "State-level information access",
                "fallback_prior": [0.88, 0.10, 0.02],
            },
            "announcement_correlation": {
                "type": "announcement_correlation",
                "states": ["no_correlation", "weak_correlation", "strong_correlation"],
                "description": "Trading correlation with announcements",
                "fallback_prior": [0.80, 0.15, 0.05],
            },
            "latent_intent": {
                "type": "latent_intent",
                "states": ["no_intent", "potential_intent", "clear_intent"],
                "description": "Latent intent to manipulate",
                "fallback_prior": [0.95, 0.04, 0.01],
            },
            "risk_factor": {
                "type": "risk_factor",
                "states": ["low", "medium", "high"],
                "description": "Latent risk factor",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            "insider_dealing": {
                "type": "outcome",
                "states": ["no", "yes"],
                "description": "Insider dealing outcome",
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
        Get all nodes for the insider dealing model.

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
                "evidence",
                "comms_intent",
                "variance_tuned",
                "profit_motivation",
                "access_pattern",
                "order_behavior",
                "comms_metadata",
                "news_timing",
                "state_information",
                "announcement_correlation",
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
            "trade_pattern",
            "comms_intent",
            "pnl_drift",
            "risk_factor",
            "insider_dealing",
        ]

    def get_latent_intent_nodes(self) -> list:
        """Get the latent intent model node names."""
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
            "latent_intent",
            "risk_factor",
            "insider_dealing",
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
