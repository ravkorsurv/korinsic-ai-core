"""
Wash Trade Detection Model Package.

This package provides comprehensive Bayesian network-based detection of wash trades
and signal distortion patterns for financial market surveillance.

Wash trading involves executing trades with oneself or coordinated parties to create
artificial trading volume and mislead other market participants. This model detects
such patterns through analysis of:
- Trading patterns between related parties
- Volume and timing correlations
- Price impact inconsistencies
- Account relationship networks

Design Rationale:
- Uses Bayesian networks to model complex relationships between traders
- Incorporates temporal analysis for pattern detection
- Provides probabilistic risk scoring with confidence intervals
- Supports regulatory reporting with explainable decision paths

Version: 1.0.0 - Initial implementation with core detection capabilities
Compliance: Designed for MiFID II, MAR, and EMIR regulatory requirements
"""

# Wrap the imports in a try-except block to handle potential import failures gracefully
try:
    from .config import WashTradeDetectionConfig
    from .model import WashTradeDetectionModel
    from .nodes import WashTradeDetectionNodes
except ImportError as e:
    raise ImportError(f"Failed to import required wash trade detection modules: {str(e)}")

__all__ = [
    "WashTradeDetectionModel",
    "WashTradeDetectionNodes",
    "WashTradeDetectionConfig",
]
