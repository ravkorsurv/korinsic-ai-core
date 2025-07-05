"""
Insider dealing detection model package.

This package contains the Bayesian network model for detecting
insider dealing activities, including standard and latent intent variants.
"""

from .model import InsiderDealingModel
from .nodes import InsiderDealingNodes
from .config import InsiderDealingConfig

__all__ = [
    'InsiderDealingModel',
    'InsiderDealingNodes',
    'InsiderDealingConfig'
]