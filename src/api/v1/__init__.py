"""
Version 1 API for Kor.ai Surveillance Platform.

This module contains all v1 API endpoints, organized by functional area.
"""

from flask import Blueprint

# Create the main v1 blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import route modules to register them with the blueprint
from .routes import analysis, alerts, models, simulation, exports, health

__all__ = ['api_v1']