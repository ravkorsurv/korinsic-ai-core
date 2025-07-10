"""
Model Explainability Module

This module provides comprehensive explainability features for all models
in the Kor.ai surveillance platform, ensuring regulatory compliance and
transparent decision-making processes.
"""

from .explainability_engine import ModelExplainabilityEngine
from .feature_attribution import FeatureAttributor
from .counterfactual_generator import CounterfactualGenerator
from .decision_path_visualizer import DecisionPathVisualizer
from .uncertainty_quantifier import UncertaintyQuantifier
from .audit_logger import ModelAuditLogger
from .governance_tracker import ModelGovernanceTracker
from .enhanced_base_model import EnhancedBaseModel

__all__ = [
    'ModelExplainabilityEngine',
    'FeatureAttributor',
    'CounterfactualGenerator',
    'DecisionPathVisualizer',
    'UncertaintyQuantifier',
    'ModelAuditLogger',
    'ModelGovernanceTracker',
    'EnhancedBaseModel'
]