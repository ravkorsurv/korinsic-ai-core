"""
API Package for Korinsic AI Surveillance Platform.

This package contains versioned API endpoints, middleware, and schemas
for the comprehensive market abuse detection and surveillance system.

API Versioning Strategy:
The API follows semantic versioning with backward compatibility guarantees.
Each major version is maintained in its own namespace to ensure stable
integration for existing clients while allowing evolution of new features.

Current Versions:
- **v1**: Initial stable API with core surveillance capabilities
  - Market abuse analysis endpoints
  - Alert management and retrieval
  - Data export and reporting
  - Health monitoring and status
  - Model management and configuration

Backward Compatibility:
- v1 API will remain stable with no breaking changes
- New features added as optional parameters or new endpoints
- Deprecation warnings provided 6 months before removal
- Migration guides provided for major version transitions

Design Principles:
- **RESTful Design**: Standard HTTP methods and status codes
- **Consistent Response Format**: Standardized success/error responses
- **Comprehensive Validation**: Request/response schema validation
- **Security First**: Authentication, authorization, and audit logging
- **Performance Optimized**: Efficient data serialization and caching
- **Regulatory Compliant**: Built-in compliance features and audit trails

Future Roadmap:
- v2: Enhanced real-time streaming capabilities
- v3: Advanced ML model integration and explainable AI features
- Enterprise features: Multi-tenancy, advanced analytics, custom models

Version: 1.0.0 - Stable API with core surveillance functionality
Compliance: Designed for regulatory reporting and audit requirements
"""

from .v1 import api_v1

__all__ = ["api_v1"]
