"""
Models package for Kor.ai Surveillance Platform.

This package contains all model definitions, configurations, and utilities
for the market abuse detection system, organized by model type and functionality.

Structure:
- bayesian/: Bayesian network models and components
- data/: Data models and validation schemas
- shared/: Shared model utilities and base classes
- services/: Model management services
"""

from .bayesian import BayesianModelRegistry
from .services import ModelService
from .shared import BaseModel, ModelMetadata
from .trading_data import (
    OrderStatus,
    RawOrderData,
    RawTradeData,
    TradeDirection,
    TradingDataSummary,
)

__all__ = [
    "BayesianModelRegistry",
    "ModelService",
    "BaseModel",
    "ModelMetadata",
    "RawTradeData",
    "RawOrderData",
    "TradingDataSummary",
    "TradeDirection",
    "OrderStatus",
]
