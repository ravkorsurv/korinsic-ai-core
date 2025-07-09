"""
Enhanced Spoofing Detection Model Package.

This package provides a comprehensive Bayesian network model for detecting
spoofing and layering behavior in financial markets.
"""

from .model import SpoofingModel
from .nodes import SpoofingNodes
from .config import SpoofingConfig

__all__ = ['SpoofingModel', 'SpoofingNodes', 'SpoofingConfig']