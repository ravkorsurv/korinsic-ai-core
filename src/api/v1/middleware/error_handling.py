"""
Error handling middleware for API v1.

This module provides decorators and utilities for handling exceptions
and errors in a consistent manner across all API endpoints.
"""

from functools import wraps
from flask import jsonify
from datetime import datetime
import logging
import traceback
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def handle_api_errors(f):
    """
    Decorator to handle API errors consistently.
    
    This decorator catches exceptions and returns standardized error responses.
    
    Returns:
        Decorated function with error handling
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Validation error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': f.__name__
            }), 400
        except AuthenticationError as e:
            logger.warning(f"Authentication error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Authentication error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': f.__name__
            }), 401
        except AuthorizationError as e:
            logger.warning(f"Authorization error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Authorization error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': f.__name__
            }), 403
        except NotFoundError as e:
            logger.warning(f"Not found error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Resource not found',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': f.__name__
            }), 404
        except RateLimitError as e:
            logger.warning(f"Rate limit error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': f.__name__
            }), 429
        except BusinessLogicError as e:
            logger.error(f"Business logic error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Business logic error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': f.__name__
            }), 422
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred',
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': f.__name__
            }), 500
    
    return decorated_function


def handle_validation_errors(f):
    """
    Decorator specifically for handling validation errors.
    
    Returns:
        Decorated function with validation error handling
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (ValueError, TypeError) as e:
            logger.warning(f"Validation error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Validation error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        except Exception as e:
            # Re-raise non-validation exceptions
            raise e
    
    return decorated_function


def create_error_response(error_type: str, message: str, 
                         status_code: int, 
                         details: Optional[Dict[str, Any]] = None) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        error_type: Type of error
        message: Error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        Tuple of (response, status_code)
    """
    response = {
        'error': error_type,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'status_code': status_code
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code


# Custom exception classes for API errors
class APIError(Exception):
    """Base exception class for API errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIError):
    """Exception for validation errors."""
    def __init__(self, message: str):
        super().__init__(message, 400)


class AuthenticationError(APIError):
    """Exception for authentication errors."""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)


class AuthorizationError(APIError):
    """Exception for authorization errors."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, 403)


class NotFoundError(APIError):
    """Exception for resource not found errors."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class RateLimitError(APIError):
    """Exception for rate limiting errors."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, 429)


class BusinessLogicError(APIError):
    """Exception for business logic errors."""
    def __init__(self, message: str):
        super().__init__(message, 422)


class ConfigurationError(APIError):
    """Exception for configuration errors."""
    def __init__(self, message: str):
        super().__init__(message, 500)


class ModelError(APIError):
    """Exception for model-related errors."""
    def __init__(self, message: str):
        super().__init__(message, 500)


class DataProcessingError(APIError):
    """Exception for data processing errors."""
    def __init__(self, message: str):
        super().__init__(message, 422)