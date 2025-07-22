"""
Circular Trading Detection Model Package.

This package contains the complete implementation of the circular trading
detection model for identifying coordinated trading schemes in financial markets.

Circular trading involves a series of trades between multiple parties that
ultimately return to the original position, creating artificial volume and
misleading market activity. This model detects such patterns through:
- Multi-party transaction flow analysis
- Temporal sequence pattern recognition
- Volume and price correlation analysis
- Network topology detection of trading relationships

Design Rationale:
- Graph-based analysis of trading networks to identify circular patterns
- Bayesian inference for probabilistic risk assessment
- Temporal windowing for pattern detection across time periods
- Configurable sensitivity thresholds for different market conditions

Version: 1.0.0 - Core circular trading detection with network analysis
Compliance: Supports regulatory requirements for market manipulation detection
"""

# Wrap the imports in a try-except block to handle potential import failures gracefully
try:
    from .config import CircularTradingConfig
    from .model import CircularTradingModel
    from .nodes import CircularTradingNodes
except ImportError as e:
    raise ImportError(f"Failed to import required circular trading modules: {str(e)}")

__all__ = ["CircularTradingModel", "CircularTradingNodes", "CircularTradingConfig"]
