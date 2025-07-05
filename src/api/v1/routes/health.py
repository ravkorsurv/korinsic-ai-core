"""
Health check API routes.

This module contains endpoints for system health monitoring and status checks.
"""

from flask import jsonify
from datetime import datetime

from ..schemas.response_schemas import HealthResponseSchema
from .. import api_v1


@api_v1.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for system monitoring.
    
    Returns:
        JSON response with system health status
    """
    schema = HealthResponseSchema()
    
    response = schema.build_response(
        status='healthy',
        service_name='kor-ai-surveillance-platform',
        version='1.0.0'
    )
    
    return jsonify(response)


@api_v1.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check with component status.
    
    Returns:
        JSON response with detailed system health information
    """
    # Check various system components
    components = {
        'database': 'healthy',  # Would check actual database connectivity
        'models': 'healthy',    # Would check model loading status
        'cache': 'healthy',     # Would check cache connectivity
        'logging': 'healthy'    # Would check logging system
    }
    
    # Determine overall status
    overall_status = 'healthy' if all(status == 'healthy' for status in components.values()) else 'degraded'
    
    response = {
        'timestamp': datetime.utcnow().isoformat(),
        'status': overall_status,
        'service': 'kor-ai-surveillance-platform',
        'version': '1.0.0',
        'components': components,
        'uptime': 'N/A',  # Would calculate actual uptime
        'memory_usage': 'N/A',  # Would get actual memory usage
        'cpu_usage': 'N/A'  # Would get actual CPU usage
    }
    
    return jsonify(response)