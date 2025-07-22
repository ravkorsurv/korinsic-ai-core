"""
Fallback Logic for Kor.ai Bayesian Risk Engine
Handles missing or partial evidence using node fallback priors.

Usage:
    from models.bayesian.shared.fallback_logic import FallbackLogic
    fallback = FallbackLogic()
    completed_evidence = fallback.apply_fallback_evidence(evidence, node_defs)
"""

import logging
from typing import Any, Dict, List

from .node_library import BayesianNode

logger = logging.getLogger(__name__)


def apply_fallback_evidence(
    evidence: Dict[str, Any], node_defs: Dict[str, BayesianNode]
) -> Dict[str, Any]:
    """
    For each node in node_defs, if evidence is missing, use the node's fallback prior (as the most probable state).
    Returns a complete evidence dict for inference.
    Logs when fallback is used for traceability.
    """
    completed_evidence = evidence.copy()
    for node_name, node in node_defs.items():
        if node_name not in completed_evidence or completed_evidence[node_name] is None:
            # Use the most probable state from fallback prior
            fallback = node.get_fallback_prior()
            max_idx = fallback.index(max(fallback))
            completed_evidence[node_name] = max_idx
            log_fallback_usage(node_name, max_idx, fallback)
    return completed_evidence


def get_fallback_state(node: BayesianNode) -> int:
    """
    Returns the index of the most probable state from the node's fallback prior.
    """
    fallback = node.get_fallback_prior()
    return fallback.index(max(fallback))


def log_fallback_usage(node_name: str, state_idx: int, fallback_prior: List[float]):
    """
    Log when fallback is used for a node, including the chosen state and prior.
    """
    logger.info(
        f"Fallback used for node '{node_name}': state index {state_idx}, prior={fallback_prior}"
    )


class FallbackLogic:
    """
    Fallback logic handler for Bayesian models.

    This class manages fallback mechanisms when evidence is missing
    or incomplete, using node-specific priors to fill gaps.
    """

    def __init__(self):
        """Initialize the fallback logic handler."""
        self.fallback_usage_log = {}
        self.fallback_stats = {
            "total_nodes_processed": 0,
            "fallback_nodes_used": 0,
            "fallback_rate": 0.0,
        }

    def apply_fallback_evidence(
        self, evidence: Dict[str, Any], node_defs: Dict[str, BayesianNode]
    ) -> Dict[str, Any]:
        """
        Apply fallback logic to complete missing evidence.

        Args:
            evidence: Observed evidence data
            node_defs: Dictionary of node definitions

        Returns:
            Complete evidence dictionary with fallbacks applied
        """
        completed_evidence = evidence.copy()
        fallback_used_count = 0

        for node_name, node in node_defs.items():
            self.fallback_stats["total_nodes_processed"] += 1

            if (
                node_name not in completed_evidence
                or completed_evidence[node_name] is None
            ):
                # Use the most probable state from fallback prior
                fallback_state = self._get_fallback_state(node)
                completed_evidence[node_name] = fallback_state

                # Log fallback usage
                self._log_fallback_usage(
                    node_name, fallback_state, node.get_fallback_prior()
                )
                fallback_used_count += 1
                self.fallback_stats["fallback_nodes_used"] += 1

        # Update fallback rate
        if self.fallback_stats["total_nodes_processed"] > 0:
            self.fallback_stats["fallback_rate"] = (
                self.fallback_stats["fallback_nodes_used"]
                / self.fallback_stats["total_nodes_processed"]
            )

        logger.info(f"Fallback applied to {fallback_used_count}/{len(node_defs)} nodes")
        return completed_evidence

    def _get_fallback_state(self, node: BayesianNode) -> int:
        """
        Get the most probable state from the node's fallback prior.

        Args:
            node: Bayesian node

        Returns:
            Index of most probable state
        """
        fallback_prior = node.get_fallback_prior()
        return fallback_prior.index(max(fallback_prior))

    def _log_fallback_usage(
        self, node_name: str, state_idx: int, fallback_prior: List[float]
    ):
        """
        Log fallback usage for a specific node.

        Args:
            node_name: Name of the node
            state_idx: Selected state index
            fallback_prior: Fallback prior probabilities
        """
        self.fallback_usage_log[node_name] = {
            "state_index": state_idx,
            "fallback_prior": fallback_prior,
            "selected_probability": fallback_prior[state_idx],
        }

        logger.info(
            f"Fallback used for node '{node_name}': "
            f"state index {state_idx}, prior={fallback_prior}"
        )

    def get_fallback_report(self) -> Dict[str, Any]:
        """
        Get a report of fallback usage.

        Returns:
            Dictionary containing fallback usage statistics
        """
        return {
            "fallback_usage_log": self.fallback_usage_log.copy(),
            "statistics": self.fallback_stats.copy(),
            "nodes_with_fallback": list(self.fallback_usage_log.keys()),
            "fallback_count": len(self.fallback_usage_log),
        }

    def reset_statistics(self):
        """Reset fallback usage statistics."""
        self.fallback_usage_log.clear()
        self.fallback_stats = {
            "total_nodes_processed": 0,
            "fallback_nodes_used": 0,
            "fallback_rate": 0.0,
        }

    def validate_evidence_completeness(
        self, evidence: Dict[str, Any], required_nodes: List[str]
    ) -> Dict[str, Any]:
        """
        Validate evidence completeness against required nodes.

        Args:
            evidence: Evidence to validate
            required_nodes: List of required node names

        Returns:
            Validation report
        """
        missing_nodes = []
        present_nodes = []

        for node_name in required_nodes:
            if node_name not in evidence or evidence[node_name] is None:
                missing_nodes.append(node_name)
            else:
                present_nodes.append(node_name)

        return {
            "is_complete": len(missing_nodes) == 0,
            "completeness_ratio": len(present_nodes) / len(required_nodes),
            "missing_nodes": missing_nodes,
            "present_nodes": present_nodes,
            "total_required": len(required_nodes),
        }
