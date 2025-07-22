"""
Enhanced Spoofing Detection Model Package.

This package provides a comprehensive Bayesian network model for detecting
spoofing and layering behavior in financial markets.

Spoofing involves placing large orders with the intent to cancel them 
before execution, creating false market signals. This model detects 
such patterns through analysis of order placement, cancellation rates, 
and market impact.
"""

# Wrap the imports in a try-except block to handle potential import failures gracefully
try:
    from .config import SpoofingConfig
    from .model import SpoofingModel
    from .nodes import SpoofingNodes
except ImportError as e:
    raise ImportError(f"Failed to import required spoofing detection modules: {str(e)}")

__all__ = ["SpoofingModel", "SpoofingNodes", "SpoofingConfig"]
