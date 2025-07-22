"""
Enhanced Spoofing Detection Model.

This module contains the enhanced spoofing detection model
for comprehensive market manipulation detection.
"""

from typing import Dict, Any
import logging

from .spoofing.model import SpoofingModel
from .spoofing.config import SpoofingConfig
from .spoofing.nodes import SpoofingNodes

logger = logging.getLogger(__name__)

# Re-export the main classes for compatibility
__all__ = ['SpoofingModel', 'SpoofingConfig', 'SpoofingNodes']