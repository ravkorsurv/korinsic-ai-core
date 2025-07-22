"""
Bayesian models package for market abuse detection.

This package contains Bayesian network models organized by abuse type:
- insider_dealing/: Insider dealing detection models
- spoofing/: Market manipulation detection models
- latent_intent/: Advanced latent intent models
- shared/: Shared Bayesian components and utilities
"""

from .insider_dealing import InsiderDealingModel
from .latent_intent import LatentIntentModel
from .registry import BayesianModelRegistry
from .shared import BayesianNodeLibrary, ModelBuilder
from .spoofing import SpoofingModel

__all__ = [
    "BayesianModelRegistry",
    "InsiderDealingModel",
    "SpoofingModel",
    "LatentIntentModel",
    "BayesianNodeLibrary",
    "ModelBuilder",
]
