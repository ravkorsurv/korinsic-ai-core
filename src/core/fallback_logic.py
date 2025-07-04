"""
Fallback Logic for Kor.ai Bayesian Risk Engine
Handles missing or partial evidence using node fallback priors.

Usage:
    from core.fallback_logic import apply_fallback_evidence, get_fallback_state, log_fallback_usage
    completed_evidence = apply_fallback_evidence(evidence, node_defs)
    # evidence: dict of observed evidence
    # node_defs: dict of node_name -> BayesianNode
    # completed_evidence: dict with missing evidence filled by fallback

"""

from typing import Dict, Any, List
from .node_library import BayesianNode
import logging

logger = logging.getLogger(__name__)

def apply_fallback_evidence(evidence: Dict[str, Any], node_defs: Dict[str, BayesianNode]) -> Dict[str, Any]:
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
    logger.info(f"Fallback used for node '{node_name}': state index {state_idx}, prior={fallback_prior}") 