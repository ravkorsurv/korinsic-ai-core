"""
API v1 routes package.

This package contains all API route handlers organized by functional area:
- analysis: Risk analysis endpoints
- alerts: Alert management endpoints  
- models: Model information endpoints
- simulation: Scenario simulation endpoints
- exports: Data export endpoints
- health: Health check endpoints
"""

# Import all route modules
from . import analysis
from . import alerts
from . import models
from . import simulation
from . import exports
from . import health

__all__ = [
    'analysis',
    'alerts', 
    'models',
    'simulation',
    'exports',
    'health'
]