"""
Cross-Desk Collusion Detection Model Package.

This package provides a comprehensive Bayesian network model for detecting
collusive behavior between trading desks or entities.
"""

from .model import CrossDeskCollusionModel
from .nodes import CrossDeskCollusionNodes
from .config import CrossDeskCollusionConfig

__all__ = ['CrossDeskCollusionModel', 'CrossDeskCollusionNodes', 'CrossDeskCollusionConfig']