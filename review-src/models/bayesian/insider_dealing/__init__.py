"""
Insider dealing detection model package.

This package contains the Bayesian network model for detecting
insider dealing activities, including standard and latent intent variants.
"""

from .config import InsiderDealingConfig
from .model import InsiderDealingModel
from .nodes import InsiderDealingNodes

__all__ = ["InsiderDealingModel", "InsiderDealingNodes", "InsiderDealingConfig"]
