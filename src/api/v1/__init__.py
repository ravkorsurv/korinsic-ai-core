"""
Version 1 API for Kor.ai Surveillance Platform.

This module contains all v1 API endpoints, organized by functional area.
Provides comprehensive market surveillance and analysis capabilities.

The v1 API includes endpoints for:
- Health monitoring and system status
- Market surveillance analysis 
- Alert management and notifications
- Model management and configuration
- Data export and reporting
- Simulation and testing capabilities
"""

from flask import Blueprint

# Create the main v1 blueprint
api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# Import route modules - routes are automatically registered via decorators
from .routes import alerts, analysis, exports, health, models, simulation

__all__ = ["api_v1"]
