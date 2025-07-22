"""
Cross-Desk Collusion Detection Model Package.

This package provides a comprehensive Bayesian network model for detecting
collusive behavior between trading desks or entities.
"""

from .config import CrossDeskCollusionConfig
from .model import CrossDeskCollusionModel
from .nodes import CrossDeskCollusionNodes

__all__ = [
    "CrossDeskCollusionModel",
    "CrossDeskCollusionNodes",
    "CrossDeskCollusionConfig",
]
