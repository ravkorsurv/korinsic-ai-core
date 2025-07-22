"""
Wash Trade Detection Model

This module provides Bayesian network-based detection of wash trades
and signal distortion patterns as specified in KOR.AI Model Enhancement.
"""

from .config import WashTradeDetectionConfig
from .model import WashTradeDetectionModel
from .nodes import WashTradeDetectionNodes

__all__ = [
    "WashTradeDetectionModel",
    "WashTradeDetectionNodes",
    "WashTradeDetectionConfig",
]
