"""
Data Sanitization Module for Regulatory Explainability System

This module provides secure handling of sensitive regulatory evidence data
including authorization checks and data sanitization for logging and output.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from enum import Enum
import copy

logger = logging.getLogger(__name__)

class AccessLevel(Enum):
    """User access levels for regulatory data"""
    PUBLIC = "public"
    ANALYST = "analyst"
    COMPLIANCE = "compliance"
    ADMIN = "admin"
    REGULATOR = "regulator"

class SensitiveDataType(Enum):
    """Types of sensitive data that require protection"""
    ACCOUNT_ID = "account_id"
    PERSON_ID = "person_id"
    PERSON_NAME = "person_name"
    FINANCIAL_AMOUNT = "financial_amount"
    COMMUNICATION_CONTENT = "communication_content"
    PARTICIPANT_EMAIL = "participant_email"
    PHONE_NUMBER = "phone_number"

class DataSanitizer:
    """Sanitizes sensitive regulatory data based on user access levels"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sensitive_fields = self._load_sensitive_fields()
        
    def _load_sensitive_fields(self) -> Dict[SensitiveDataType, Set[str]]:
        """Load configuration of sensitive field mappings"""
        return {
            SensitiveDataType.ACCOUNT_ID: {
                "account_id", "account", "accounts_involved", "accounts_in_pattern"
            },
            SensitiveDataType.PERSON_ID: {
                "person_id", "person_name", "trader_name", "account_holder"
            },
            SensitiveDataType.FINANCIAL_AMOUNT: {
                "position_size_usd", "current_position", "historical_average_position",
                "total_exposure", "unrealized_gains", "position_size"
            },
            SensitiveDataType.COMMUNICATION_CONTENT: {
                "participants", "call_participants", "email_content", "message_content"
            },
            SensitiveDataType.PARTICIPANT_EMAIL: {
                "participants", "email_addresses", "contact_info"
            }
        }
    
    def sanitize_evidence_item(
        self, 
        evidence_item: Dict[str, Any], 
        access_level: AccessLevel,
        preserve_structure: bool = True
    ) -> Dict[str, Any]:
        """
        Sanitize a single evidence item based on user access level.
        
        Args:
            evidence_item: Evidence item to sanitize
            access_level: User's access level
            preserve_structure: Whether to preserve the original structure
            
        Returns:
            Sanitized evidence item
        """
        if access_level == AccessLevel.REGULATOR:
            # Regulators get full access
            return evidence_item
            
        sanitized = copy.deepcopy(evidence_item) if preserve_structure else {}
        
        # Apply sanitization rules based on access level
        if access_level == AccessLevel.PUBLIC:
            sanitized = self._apply_public_sanitization(sanitized)
        elif access_level == AccessLevel.ANALYST:
            sanitized = self._apply_analyst_sanitization(sanitized)
        elif access_level == AccessLevel.COMPLIANCE:
            sanitized = self._apply_compliance_sanitization(sanitized)
        elif access_level == AccessLevel.ADMIN:
            sanitized = self._apply_admin_sanitization(sanitized)
            
        return sanitized
    
    def _apply_public_sanitization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply public-level sanitization (most restrictive)"""
        # Remove all sensitive identifiers
        sanitized = {
            "evidence_type": data.get("evidence_type", "REDACTED"),
            "timestamp": data.get("timestamp", "REDACTED"),
            "strength": self._round_score(data.get("strength", 0.0)),
            "description": self._sanitize_description(data.get("description", "")),
            "regulatory_frameworks": data.get("regulatory_frameworks", [])
        }
        return sanitized
    
    def _apply_analyst_sanitization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply analyst-level sanitization"""
        sanitized = copy.deepcopy(data)
        
        # Mask account IDs
        sanitized["account_id"] = self._mask_account_id(data.get("account_id", ""))
        
        # Sanitize raw data
        if "raw_data" in sanitized:
            sanitized["raw_data"] = self._sanitize_raw_data(
                sanitized["raw_data"], AccessLevel.ANALYST
            )
            
        return sanitized
    
    def _apply_compliance_sanitization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply compliance-level sanitization (minimal restrictions)"""
        sanitized = copy.deepcopy(data)
        
        # Only sanitize external communication details
        if "raw_data" in sanitized:
            sanitized["raw_data"] = self._sanitize_raw_data(
                sanitized["raw_data"], AccessLevel.COMPLIANCE
            )
            
        return sanitized
    
    def _apply_admin_sanitization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply admin-level sanitization (very minimal restrictions)"""
        sanitized = copy.deepcopy(data)
        
        # Only redact external email addresses
        if "raw_data" in sanitized and "participants" in sanitized["raw_data"]:
            sanitized["raw_data"]["participants"] = [
                self._mask_external_email(email) 
                for email in sanitized["raw_data"]["participants"]
            ]
            
        return sanitized
    
    def _sanitize_raw_data(self, raw_data: Dict[str, Any], access_level: AccessLevel) -> Dict[str, Any]:
        """Sanitize raw data fields based on access level"""
        sanitized = copy.deepcopy(raw_data)
        
        for field_name, field_value in raw_data.items():
            if self._is_sensitive_field(field_name):
                if access_level == AccessLevel.PUBLIC:
                    sanitized[field_name] = "REDACTED"
                elif access_level == AccessLevel.ANALYST:
                    sanitized[field_name] = self._mask_sensitive_value(field_value, field_name)
                # Compliance and Admin get most data
                    
        return sanitized
    
    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if a field contains sensitive data"""
        for sensitive_type, field_set in self.sensitive_fields.items():
            if field_name in field_set:
                return True
        return False
    
    def _mask_account_id(self, account_id: str) -> str:
        """Mask account ID for privacy"""
        if not account_id or len(account_id) < 4:
            return "ACC_***"
        return f"{account_id[:3]}***{account_id[-2:]}"
    
    def _mask_sensitive_value(self, value: Any, field_name: str) -> Any:
        """Mask sensitive values based on field type"""
        if isinstance(value, str):
            if "@" in value:  # Email
                return self._mask_email(value)
            elif field_name in self.sensitive_fields[SensitiveDataType.ACCOUNT_ID]:
                return self._mask_account_id(value)
            else:
                return f"***{len(str(value))} chars***"
        elif isinstance(value, (int, float)):
            # Round financial amounts
            return round(value, -3)  # Round to nearest thousand
        elif isinstance(value, list):
            return [self._mask_sensitive_value(item, field_name) for item in value]
        else:
            return "***MASKED***"
    
    def _mask_email(self, email: str) -> str:
        """Mask email address"""
        if "@" not in email:
            return "***@***.com"
        local, domain = email.split("@", 1)
        return f"{local[0]}***@{domain}"
    
    def _mask_external_email(self, email: str) -> str:
        """Mask external email addresses only"""
        if "@" not in email:
            return email
        local, domain = email.split("@", 1)
        # Only mask external domains (not internal company domains)
        internal_domains = self.config.get("internal_domains", ["techcorp.com"])
        if any(domain.endswith(internal) for internal in internal_domains):
            return email  # Keep internal emails
        return f"{local[0]}***@{domain}"
    
    def _sanitize_description(self, description: str) -> str:
        """Sanitize description text"""
        # Remove specific account references
        import re
        # Replace account patterns
        description = re.sub(r'ACC_[A-Z0-9_]+', 'ACC_***', description)
        # Replace dollar amounts
        description = re.sub(r'\$[\d,]+', '$***', description)
        # Replace percentages over 100%
        description = re.sub(r'(\d{3,})%', '***%', description)
        return description
    
    def _round_score(self, score: float) -> float:
        """Round scores to prevent inference attacks"""
        return round(score, 2)

class AuthorizationManager:
    """Manages user authorization for regulatory data access"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.user_access_levels = self._load_user_access_levels()
    
    def _load_user_access_levels(self) -> Dict[str, AccessLevel]:
        """Load user access level mappings"""
        # In production, this would come from a secure user management system
        return {
            "public_user": AccessLevel.PUBLIC,
            "analyst_user": AccessLevel.ANALYST,
            "compliance_user": AccessLevel.COMPLIANCE,
            "admin_user": AccessLevel.ADMIN,
            "regulator_user": AccessLevel.REGULATOR
        }
    
    def is_authorized_user(self, user_id: str, required_permission: str) -> bool:
        """
        Check if user is authorized for specific permissions.
        
        Args:
            user_id: User identifier
            required_permission: Required permission level
            
        Returns:
            True if authorized, False otherwise
        """
        user_level = self.user_access_levels.get(user_id, AccessLevel.PUBLIC)
        
        permission_requirements = {
            "view_evidence_summary": [AccessLevel.ANALYST, AccessLevel.COMPLIANCE, AccessLevel.ADMIN, AccessLevel.REGULATOR],
            "view_evidence_details": [AccessLevel.COMPLIANCE, AccessLevel.ADMIN, AccessLevel.REGULATOR],
            "view_raw_data": [AccessLevel.ADMIN, AccessLevel.REGULATOR],
            "export_stor_reports": [AccessLevel.COMPLIANCE, AccessLevel.ADMIN, AccessLevel.REGULATOR],
            "view_full_audit_trail": [AccessLevel.REGULATOR]
        }
        
        required_levels = permission_requirements.get(required_permission, [AccessLevel.REGULATOR])
        return user_level in required_levels
    
    def get_user_access_level(self, user_id: str) -> AccessLevel:
        """Get user's access level"""
        return self.user_access_levels.get(user_id, AccessLevel.PUBLIC)

def secure_print_evidence(
    evidence_data: Dict[str, Any], 
    user_id: str = "public_user",
    permission: str = "view_evidence_details"
) -> None:
    """
    Securely print evidence data with proper authorization and sanitization.
    
    Args:
        evidence_data: Evidence data to print
        user_id: User requesting the data
        permission: Required permission level
    """
    auth_manager = AuthorizationManager()
    sanitizer = DataSanitizer()
    
    if not auth_manager.is_authorized_user(user_id, permission):
        logger.warning(f"Unauthorized access attempt by user {user_id} for permission {permission}")
        print("ERROR: Insufficient permissions to view evidence details")
        return
    
    user_level = auth_manager.get_user_access_level(user_id)
    
    # Sanitize the data based on user access level
    if "evidence_chain" in evidence_data:
        sanitized_chain = [
            sanitizer.sanitize_evidence_item(item, user_level)
            for item in evidence_data["evidence_chain"]
        ]
        evidence_data["evidence_chain"] = sanitized_chain
    
    # Log the access for audit trail
    logger.info(f"Evidence data accessed by user {user_id} with level {user_level.value}")
    
    # Print sanitized data
    import json
    print(json.dumps(evidence_data, indent=2, default=str))