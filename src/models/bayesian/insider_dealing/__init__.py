"""
Insider Dealing Detection Model Package.

This package contains the Bayesian network model for detecting
insider dealing activities, including standard and latent intent variants.

Insider dealing involves trading on material non-public information, 
which provides an unfair advantage. This model detects such patterns 
through analysis of trading timing, access levels, and information flow.
"""

# Wrap the imports in a try-except block to handle potential import failures gracefully
try:
    from .config import InsiderDealingConfig
    from .model import InsiderDealingModel
    from .nodes import InsiderDealingNodes
except ImportError as e:
    raise ImportError(f"Failed to import required insider dealing modules: {str(e)}")

__all__ = ["InsiderDealingModel", "InsiderDealingNodes", "InsiderDealingConfig"]
