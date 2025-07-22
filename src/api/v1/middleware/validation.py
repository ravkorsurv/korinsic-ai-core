"""
Request validation middleware for API v1.

This module provides decorators and utilities for validating incoming
API requests against defined schemas.
"""

import logging
from functools import wraps
from typing import Any, Dict, Optional, Type

from flask import jsonify, request

logger = logging.getLogger(__name__)


def validate_request(schema_class: Optional[Type] = None):
    """
    Decorator to validate incoming request data against a schema.

    Args:
        schema_class: Schema class to validate against (optional)

    Returns:
        Decorated function with request validation
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get request data
                data = request.get_json()

                if data is None:
                    return jsonify({"error": "No JSON data provided"}), 400

                # Perform basic validation
                if not isinstance(data, dict):
                    return jsonify({"error": "Request data must be a JSON object"}), 400

                # If schema class is provided, validate against it
                if schema_class:
                    try:
                        # Instantiate schema and validate
                        schema = schema_class()
                        validation_result = schema.validate(data)

                        if not validation_result.is_valid:
                            return (
                                jsonify(
                                    {
                                        "error": "Validation failed",
                                        "details": validation_result.errors,
                                    }
                                ),
                                400,
                            )

                    except Exception as e:
                        logger.error(f"Schema validation error: {str(e)}")
                        return jsonify({"error": "Schema validation failed"}), 400

                # Call the original function
                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"Request validation error: {str(e)}")
                return jsonify({"error": "Request validation failed"}), 400

        return decorated_function

    return decorator


def validate_json_content_type():
    """
    Decorator to ensure request has JSON content type.

    Returns:
        Decorated function with content type validation
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def validate_required_fields(required_fields: list):
    """
    Decorator to validate that required fields are present in request.

    Args:
        required_fields: List of required field names

    Returns:
        Decorated function with field validation
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()

                if not data:
                    return jsonify({"error": "No data provided"}), 400

                missing_fields = []
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)

                if missing_fields:
                    return (
                        jsonify(
                            {
                                "error": "Missing required fields",
                                "missing_fields": missing_fields,
                            }
                        ),
                        400,
                    )

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"Field validation error: {str(e)}")
                return jsonify({"error": "Field validation failed"}), 400

        return decorated_function

    return decorator


def validate_data_types(type_mapping: Dict[str, type]):
    """
    Decorator to validate data types of request fields.

    Args:
        type_mapping: Dictionary mapping field names to expected types

    Returns:
        Decorated function with type validation
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()

                if not data:
                    return jsonify({"error": "No data provided"}), 400

                type_errors = []
                for field, expected_type in type_mapping.items():
                    if field in data:
                        if not isinstance(data[field], expected_type):
                            type_errors.append(
                                {
                                    "field": field,
                                    "expected_type": expected_type.__name__,
                                    "actual_type": type(data[field]).__name__,
                                }
                            )

                if type_errors:
                    return (
                        jsonify(
                            {
                                "error": "Type validation failed",
                                "type_errors": type_errors,
                            }
                        ),
                        400,
                    )

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"Type validation error: {str(e)}")
                return jsonify({"error": "Type validation failed"}), 400

        return decorated_function

    return decorator


class ValidationResult:
    """Result of validation operation."""

    def __init__(self, is_valid: bool = True, errors: Optional[list] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, error: str):
        """Add a validation error."""
        self.is_valid = False
        self.errors.append(error)
