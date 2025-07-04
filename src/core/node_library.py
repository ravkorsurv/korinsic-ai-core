"""
Node Library for Kor.ai Bayesian Risk Engine
Reusable node classes, templates, and CPT logic for Bayesian Network construction.
"""

from typing import List, Dict, Any, Optional
import numpy as np

class BayesianNode:
    """
    Base class for a Bayesian Network node.
    """
    def __init__(self, name: str, states: List[str], cpt: Optional[Dict] = None, description: str = "", fallback_prior: Optional[List[float]] = None):
        self.name = name
        self.states = states
        self.cpt = cpt or {}
        self.description = description
        self.fallback_prior = fallback_prior or [1.0 / len(states)] * len(states)

    def set_cpt(self, cpt: Dict):
        self.cpt = cpt

    def get_cpt(self) -> Dict:
        return self.cpt

    def get_fallback_prior(self) -> List[float]:
        return self.fallback_prior

    def explain(self) -> str:
        return f"Node: {self.name}\nDescription: {self.description}\nStates: {self.states}\nFallback Prior: {self.fallback_prior}"

class EvidenceNode(BayesianNode):
    """
    Node representing an evidence variable (input from data/events).
    """
    def __init__(self, name: str, states: List[str], description: str = "", fallback_prior: Optional[List[float]] = None):
        super().__init__(name, states, cpt=None, description=description, fallback_prior=fallback_prior)

class RiskFactorNode(BayesianNode):
    """
    Node representing a risk factor (intermediate or latent variable).
    """
    def __init__(self, name: str, states: List[str], cpt: Optional[Dict] = None, description: str = "", fallback_prior: Optional[List[float]] = None):
        super().__init__(name, states, cpt=cpt, description=description, fallback_prior=fallback_prior)

class OutcomeNode(BayesianNode):
    """
    Node representing the outcome (e.g., Insider Dealing, Spoofing, etc.).
    """
    def __init__(self, name: str, states: List[str], cpt: Optional[Dict] = None, description: str = "", fallback_prior: Optional[List[float]] = None):
        super().__init__(name, states, cpt=cpt, description=description, fallback_prior=fallback_prior)

# Example: Template for a comms intent node (specialized evidence node)
class CommsIntentNode(EvidenceNode):
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["benign", "suspicious", "malicious"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)

# Example: Variance-tuned indicator node (for EM-based learning)
class VarianceTunedIndicatorNode(EvidenceNode):
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["normal", "anomalous"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)

# NEW: Latent Intent Nodes for Hidden Causality Modeling
class LatentIntentNode(BayesianNode):
    """
    Node representing latent intent (unobservable core abusive intent).
    This is the key innovation for modeling hidden causality.
    """
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["no_intent", "potential_intent", "clear_intent"]
        super().__init__(name, states, cpt=None, description=description, fallback_prior=fallback_prior)
    
    def get_intent_strength(self, evidence_values: Dict[str, Any]) -> float:
        """
        Calculate intent strength based on converging evidence paths.
        This implements the Kor.ai approach of inferring latent intent.
        """
        # Default implementation - should be overridden with domain-specific logic
        return 0.5

class ProfitMotivationNode(EvidenceNode):
    """
    Node representing profit motivation evidence (PnL drift, profit patterns).
    One of the converging evidence paths for latent intent inference.
    """
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["normal_profit", "unusual_profit", "suspicious_profit"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)

class AccessPatternNode(EvidenceNode):
    """
    Node representing access pattern evidence (information access, timing).
    One of the converging evidence paths for latent intent inference.
    """
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["normal_access", "unusual_access", "suspicious_access"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)

class OrderBehaviorNode(EvidenceNode):
    """
    Node representing order behavior evidence (order patterns, timing).
    One of the converging evidence paths for latent intent inference.
    """
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["normal_behavior", "unusual_behavior", "suspicious_behavior"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)

class CommsMetadataNode(EvidenceNode):
    """
    Node representing communications metadata evidence.
    One of the converging evidence paths for latent intent inference.
    """
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["normal_comms", "unusual_comms", "suspicious_comms"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)

# Utility for CPT normalization

def normalize_cpt(cpt: Dict[str, List[float]]) -> Dict[str, List[float]]:
    norm_cpt = {}
    for k, v in cpt.items():
        total = sum(v)
        norm_cpt[k] = [x / total if total > 0 else 1.0 / len(v) for x in v]
    return norm_cpt 