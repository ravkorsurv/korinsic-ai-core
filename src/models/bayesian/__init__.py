"""
Bayesian models package for market abuse detection.

This package contains Bayesian network models organized by abuse type:
- insider_dealing/: Insider dealing detection models
- spoofing/: Market manipulation detection models  
- latent_intent/: Advanced latent intent models
- shared/: Shared Bayesian components and utilities
"""

from .registry import BayesianModelRegistry
from .insider_dealing import InsiderDealingModel
from .spoofing import SpoofingModel
from .latent_intent import LatentIntentModel
from .shared import BayesianNodeLibrary, ModelBuilder

__all__ = [
    'BayesianModelRegistry',
    'InsiderDealingModel',
    'SpoofingModel', 
    'LatentIntentModel',
    'BayesianNodeLibrary',
    'ModelBuilder'
]