"""
Data Quality Services Package

This package implements the Modular Data Quality Sufficiency Index (DQSI)
with KDE-level scoring, strategy-based configurations, and metadata-driven
calculations for the Kor.ai Surveillance Platform.
"""

from .dq_config_loader import DQConfigLoader
from .dq_strategy_base import DQScoringStrategy
from .dq_sufficiency_index import DataQualitySufficiencyIndex
from .fallback_dq_strategy import FallbackDQScoringStrategy
from .role_aware_dq_strategy import RoleAwareDQScoringStrategy

__all__ = [
    "DataQualitySufficiencyIndex",
    "DQScoringStrategy",
    "FallbackDQScoringStrategy",
    "RoleAwareDQScoringStrategy",
    "DQConfigLoader",
]
