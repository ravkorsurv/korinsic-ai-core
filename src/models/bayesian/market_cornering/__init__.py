"""
Market Cornering Detection Model Package.

This package contains the complete implementation of the market cornering
detection model including nodes, configuration, and the main model class.

Market cornering involves attempting to control a significant portion of a 
market to manipulate prices. This model detects such patterns through 
Bayesian analysis of trading behavior and market concentration.
"""

# Wrap the imports in a try-except block to handle potential import failures gracefully
try:
    from .config import MarketCorneringConfig
    from .model import MarketCorneringModel
    from .nodes import MarketCorneringNodes
except ImportError as e:
    raise ImportError(f"Failed to import required market cornering modules: {str(e)}")

__all__ = ["MarketCorneringModel", "MarketCorneringNodes", "MarketCorneringConfig"]
