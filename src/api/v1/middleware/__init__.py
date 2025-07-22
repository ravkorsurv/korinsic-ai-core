"""
API v1 middleware package.

This package contains middleware components for request/response processing,
validation, error handling, and other cross-cutting concerns.

Middleware:
- validation: Request validation middleware
- error_handling: Error handling and exception management
- auth: Authentication and authorization middleware
- rate_limiting: Rate limiting and throttling
- logging: Request/response logging middleware
"""

from .auth import require_auth
from .error_handling import handle_api_errors
from .logging import log_requests
from .rate_limiting import rate_limit
from .validation import validate_request

__all__ = [
    "validate_request",
    "handle_api_errors",
    "require_auth",
    "rate_limit",
    "log_requests",
]
