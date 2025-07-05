"""
API package for Kor.ai Surveillance Platform.

This package contains versioned API endpoints, middleware, and schemas
for the market abuse detection system.
"""

from .v1 import api_v1

__all__ = ['api_v1']