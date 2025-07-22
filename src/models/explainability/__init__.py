"""
Model Explainability Module

This module provides comprehensive explainability features for all models
in the Kor.ai surveillance platform, ensuring regulatory compliance and
transparent decision-making processes.
"""

from .audit_logger import ModelAuditLogger
from .counterfactual_generator import CounterfactualGenerator
from .decision_path_visualizer import DecisionPathVisualizer
from .enhanced_base_model import EnhancedBaseModel
from .evidence_sufficiency_index import ESIResult, EvidenceSufficiencyIndex
from .explainability_engine import ModelExplainabilityEngine
from .feature_attribution import FeatureAttributor
from .governance_tracker import ModelGovernanceTracker
from .uncertainty_quantifier import UncertaintyQuantifier

__all__ = [
    "ModelExplainabilityEngine",
    "FeatureAttributor",
    "CounterfactualGenerator",
    "DecisionPathVisualizer",
    "UncertaintyQuantifier",
    "EvidenceSufficiencyIndex",
    "ESIResult",
    "ModelAuditLogger",
    "ModelGovernanceTracker",
    "EnhancedBaseModel",
]
