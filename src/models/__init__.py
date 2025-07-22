"""
Models Package for Korinsic AI Surveillance Platform.

This package contains all model definitions, configurations, and utilities
for the comprehensive market abuse detection system, organized by model type 
and functionality to support regulatory compliance and risk management.

Package Purpose:
Provides a unified framework for financial market surveillance models including
Bayesian networks for market abuse detection, data models for trading information,
and service layers for model management and deployment.

Structure:
- **bayesian/**: Advanced Bayesian network models for market abuse detection
  - insider_dealing/: Insider trading detection with latent intent analysis
  - spoofing/: Market manipulation through false signals
  - wash_trade_detection/: Artificial volume creation detection
  - market_cornering/: Market control and price manipulation
  - circular_trading/: Coordinated trading scheme detection
  - cross_desk_collusion/: Internal coordination detection
- **explainability/**: Model explainability and audit trail components
- **shared/**: Common utilities, base classes, and shared functionality
- **services/**: Model lifecycle management and deployment services
- **trading_data/**: Trading data models and validation schemas

Design Rationale:
- **Modularity**: Each model type is self-contained with its own configuration
- **Extensibility**: Easy addition of new detection models and capabilities
- **Compliance**: Built-in regulatory reporting and explainability features
- **Performance**: Optimized for high-frequency trading data analysis
- **Maintainability**: Clear separation of concerns and standardized interfaces

Version: 1.0.0 - Comprehensive market surveillance model framework
Compliance: Designed for MiFID II, MAR, EMIR, and other regulatory requirements
Dependencies: pgmpy, numpy, pandas, scikit-learn for Bayesian inference
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
