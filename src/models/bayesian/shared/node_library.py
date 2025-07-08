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

# NEW: Enhanced nodes for insider dealing model
class NewsTimingNode(EvidenceNode):
    """
    Node representing news-trade timing analysis evidence.
    Detects suspicious timing patterns between trades and market-moving announcements.
    """
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["normal_timing", "suspicious_timing", "highly_suspicious_timing"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)

class StateInformationNode(EvidenceNode):
    """
    Node representing state-level information access evidence.
    Detects access to material non-public information from government or state sources.
    """
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["no_access", "potential_access", "clear_access"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)

class AnnouncementCorrelationNode(EvidenceNode):
    """
    Node representing trading correlation with government/regulatory announcements.
    Analyzes statistical correlation between trading patterns and public announcements.
    """
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["no_correlation", "weak_correlation", "strong_correlation"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)

# Utility for CPT normalization

def normalize_cpt(cpt: Dict[str, List[float]]) -> Dict[str, List[float]]:
    norm_cpt = {}
    for k, v in cpt.items():
        total = sum(v)
        norm_cpt[k] = [x / total if total > 0 else 1.0 / len(v) for x in v]
    return norm_cpt


class BayesianNodeLibrary:
    """
    Library class for managing Bayesian network nodes and templates.
    
    This class provides a centralized way to access and create different
    types of Bayesian network nodes for the surveillance platform.
    """
    
    def __init__(self):
        """Initialize the node library."""
        self.node_classes = {
            'evidence': EvidenceNode,
            'risk_factor': RiskFactorNode,
            'outcome': OutcomeNode,
            'comms_intent': CommsIntentNode,
            'variance_tuned': VarianceTunedIndicatorNode,
            'latent_intent': LatentIntentNode,
            'profit_motivation': ProfitMotivationNode,
            'access_pattern': AccessPatternNode,
            'order_behavior': OrderBehaviorNode,
            'comms_metadata': CommsMetadataNode,
            'news_timing': NewsTimingNode,
            'state_information': StateInformationNode,
            'announcement_correlation': AnnouncementCorrelationNode
        }
        
        self.node_templates = {
            'insider_dealing': {
                'material_info': {
                    'class': 'evidence',
                    'states': ['No access', 'Potential access', 'Clear access'],
                    'description': 'Access to material non-public information'
                },
                'trading_activity': {
                    'class': 'evidence', 
                    'states': ['Normal', 'Unusual', 'Highly unusual'],
                    'description': 'Unusualness of trading patterns'
                },
                'timing': {
                    'class': 'evidence',
                    'states': ['Normal', 'Suspicious', 'Highly suspicious'], 
                    'description': 'Timing relative to material events'
                },
                'price_impact': {
                    'class': 'evidence',
                    'states': ['Low', 'Medium', 'High'],
                    'description': 'Price impact of trades'
                },
                'risk': {
                    'class': 'outcome',
                    'states': ['Low', 'Medium', 'High'],
                    'description': 'Overall insider dealing risk'
                }
            },
            'spoofing': {
                'order_pattern': {
                    'class': 'evidence',
                    'states': ['Normal', 'Layered', 'Excessive layering'],
                    'description': 'Pattern of order placement'
                },
                'cancellation_rate': {
                    'class': 'evidence',
                    'states': ['Low', 'Medium', 'High'],
                    'description': 'Rate of order cancellations'
                },
                'price_movement': {
                    'class': 'evidence',
                    'states': ['Minimal', 'Moderate', 'Significant'],
                    'description': 'Price movement during activity'
                },
                'volume_ratio': {
                    'class': 'evidence',
                    'states': ['Normal', 'Imbalanced', 'Highly imbalanced'],
                    'description': 'Volume imbalance ratio'
                },
                'risk': {
                    'class': 'outcome',
                    'states': ['Low', 'Medium', 'High'],
                    'description': 'Overall spoofing risk'
                }
            }
        }
    
    def create_node(self, node_type: str, name: str, **kwargs) -> BayesianNode:
        """
        Create a node of the specified type.
        
        Args:
            node_type: Type of node to create
            name: Name for the node
            **kwargs: Additional arguments for node creation
            
        Returns:
            BayesianNode instance
        """
        if node_type not in self.node_classes:
            raise ValueError(f"Unknown node type: {node_type}")
        
        node_class = self.node_classes[node_type]
        
        # Filter out parameters that specialized nodes don't accept
        # Specialized nodes have predefined states, so they don't accept 'states' parameter
        specialized_nodes = {
            'comms_intent', 'variance_tuned', 'latent_intent', 'profit_motivation',
            'access_pattern', 'order_behavior', 'comms_metadata', 'news_timing',
            'state_information', 'announcement_correlation'
        }
        
        if node_type in specialized_nodes:
            # Remove 'states' from kwargs for specialized nodes
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'states'}
            return node_class(name, **filtered_kwargs)
        else:
            # For basic nodes (evidence, risk_factor, outcome), pass all kwargs
            return node_class(name, **kwargs)
    
    def create_from_template(self, model_type: str, node_name: str) -> BayesianNode:
        """
        Create a node from a predefined template.
        
        Args:
            model_type: Type of model (insider_dealing, spoofing)
            node_name: Name of the node template
            
        Returns:
            BayesianNode instance
        """
        if model_type not in self.node_templates:
            raise ValueError(f"Unknown model type: {model_type}")
        
        if node_name not in self.node_templates[model_type]:
            raise ValueError(f"Unknown node template: {node_name} for model {model_type}")
        
        template = self.node_templates[model_type][node_name]
        node_class = self.node_classes[template['class']]
        
        return node_class(
            name=node_name,
            states=template['states'],
            description=template['description']
        )
    
    def get_available_templates(self, model_type: str = None) -> Dict[str, Any]:
        """
        Get available node templates.
        
        Args:
            model_type: Optional model type filter
            
        Returns:
            Dictionary of available templates
        """
        if model_type:
            return self.node_templates.get(model_type, {})
        return self.node_templates
    
    def get_node_classes(self) -> Dict[str, type]:
        """Get all available node classes."""
        return self.node_classes.copy() 