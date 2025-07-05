"""
Core processors package for Kor.ai Surveillance Platform.

This package contains data processing components that prepare and
transform data for analysis.

Processors:
- DataProcessor: Main data processing and validation
- EvidenceMapper: Evidence mapping and transformation
"""

from .data_processor import DataProcessor
from .evidence_mapper import EvidenceMapper

__all__ = [
    'DataProcessor',
    'EvidenceMapper'
]