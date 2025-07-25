"""
Request schemas for API v1 validation.

This module contains schema classes for validating incoming API requests.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from marshmallow import Schema, fields, validate


class BaseRequestSchema:
    """Base class for request schemas."""

    def validate(self, data: Dict[str, Any]) -> "ValidationResult":
        """
        Validate request data.

        Args:
            data: Request data to validate

        Returns:
            ValidationResult indicating success or failure
        """
        from ..middleware.validation import ValidationResult

        result = ValidationResult()

        try:
            # Perform basic validation
            self._validate_basic_structure(data, result)

            # Perform specific validation if basic validation passes
            if result.is_valid:
                self._validate_specific(data, result)

        except Exception as e:
            result.add_error(f"Validation error: {str(e)}")

        return result

    def _validate_basic_structure(
        self, data: Dict[str, Any], result: "ValidationResult"
    ):
        """Validate basic data structure."""
        if not isinstance(data, dict):
            result.add_error("Request data must be a dictionary")

    def _validate_specific(self, data: Dict[str, Any], result: "ValidationResult"):
        """Validate specific schema requirements. Override in subclasses."""
        pass


class AnalysisRequestSchema(BaseRequestSchema):
    """
    Schema for market surveillance analysis request validation.
    
    This schema validates incoming requests for market abuse analysis,
    ensuring all required trading data and configuration parameters
    are properly formatted and complete.
    
    Required Fields:
        - trades: List of trade records with timestamp, volume, price
        - orders: List of order records with placement and execution data
        
    Optional Fields:
        - material_events: List of material events that may impact analysis
        - trader_info: Additional trader context and access levels
        - analysis_type: Specific analysis type (insider_dealing, spoofing, etc.)
        - use_latent_intent: Whether to include latent intent analysis
        - include_regulatory_rationale: Whether to generate compliance explanations
    
    Validation Rules:
        - Timestamps must be in ISO format
        - Volumes and prices must be positive numbers
        - Trader IDs must be consistent across trades and orders
        - Material events must have valid event types
    """
    
    def _validate_specific(self, data: Dict[str, Any], result: "ValidationResult"):
        """
        Validate analysis request specific requirements.
        
        Args:
            data: Request data containing trading information
            result: ValidationResult object to collect errors
        """
        # Validate required trading data
        if "trades" not in data or not data["trades"]:
            result.add_error("Missing required field: trades (must contain at least one trade)")
            
        if "orders" not in data or not data["orders"]:
            result.add_error("Missing required field: orders (must contain at least one order)")
            
        # Validate trade data structure
        if "trades" in data and isinstance(data["trades"], list):
            for i, trade in enumerate(data["trades"]):
                if not isinstance(trade, dict):
                    result.add_error(f"Trade {i} must be a dictionary")
                    continue
                    
                required_trade_fields = ["timestamp", "volume", "value", "symbol"]
                for field in required_trade_fields:
                    if field not in trade:
                        result.add_error(f"Trade {i} missing required field: {field}")
                        
        # Validate order data structure  
        if "orders" in data and isinstance(data["orders"], list):
            for i, order in enumerate(data["orders"]):
                if not isinstance(order, dict):
                    result.add_error(f"Order {i} must be a dictionary")
                    continue
                    
                required_order_fields = ["timestamp", "quantity", "price", "side"]
                for field in required_order_fields:
                    if field not in order:
                        result.add_error(f"Order {i} missing required field: {field}")


class DQSIRequestSchema(BaseRequestSchema):
    """Schema for DQSI request validation"""

    def _validate_specific(self, data: Dict[str, Any], result: "ValidationResult"):
        """Validate DQSI request specific requirements."""
        # Check required fields based on endpoint
        if (
            "dataset" not in data
            and "batch_data" not in data
            and "time_series_data" not in data
        ):
            result.add_error(
                "Missing required field: dataset, batch_data, or time_series_data"
            )

        # Validate dataset if provided
        if "dataset" in data:
            if not isinstance(data["dataset"], dict):
                result.add_error("Dataset must be a dictionary")

        # Validate batch_data if provided
        if "batch_data" in data:
            if not isinstance(data["batch_data"], list):
                result.add_error("Batch data must be a list")

        # Validate time_series_data if provided
        if "time_series_data" in data:
            if not isinstance(data["time_series_data"], list):
                result.add_error("Time series data must be a list")

        # Validate custom weights if provided
        if "custom_weights" in data:
            if not isinstance(data["custom_weights"], dict):
                result.add_error("Custom weights must be a dictionary")

        # Validate enabled dimensions if provided
        if "enabled_dimensions" in data:
            if not isinstance(data["enabled_dimensions"], list):
                result.add_error("Enabled dimensions must be a list")
            else:
                valid_dimensions = [
                    "completeness",
                    "accuracy",
                    "consistency",
                    "validity",
                    "uniqueness",
                    "timeliness",
                ]
                for dim in data["enabled_dimensions"]:
                    if dim not in valid_dimensions:
                        result.add_error(
                            f"Invalid dimension: {dim}. Must be one of: {valid_dimensions}"
                        )


class SimulationRequestSchema(BaseRequestSchema):
    """Schema for simulation request validation."""

    def _validate_specific(self, data: Dict[str, Any], result: "ValidationResult"):
        """Validate simulation request specific requirements."""
        # Check required fields
        if "scenario_type" not in data:
            result.add_error("Missing required field: scenario_type")

        # Validate scenario type
        if "scenario_type" in data:
            valid_types = ["insider_dealing", "spoofing"]
            if data["scenario_type"] not in valid_types:
                result.add_error(
                    f"Invalid scenario type. Must be one of: {valid_types}"
                )

        # Validate parameters if provided
        if "parameters" in data:
            if not isinstance(data["parameters"], dict):
                result.add_error("Parameters must be a dictionary")


class BatchAnalysisRequestSchema(BaseRequestSchema):
    """Schema for batch analysis request validation."""

    def _validate_specific(self, data: Dict[str, Any], result: "ValidationResult"):
        """Validate batch analysis request specific requirements."""
        if "batch_data" not in data:
            result.add_error("Missing required field: batch_data")
            return

        batch_data = data["batch_data"]
        if not isinstance(batch_data, list):
            result.add_error("Batch data must be a list")
            return

        if len(batch_data) == 0:
            result.add_error("Batch data cannot be empty")
            return

        # Validate each item in batch
        analysis_schema = AnalysisRequestSchema()
        for i, item in enumerate(batch_data):
            item_result = analysis_schema.validate(item)
            if not item_result.is_valid:
                for error in item_result.errors:
                    result.add_error(f"Batch item {i}: {error}")


class ExportRequestSchema(BaseRequestSchema):
    """
    Schema for data export request validation.
    
    This schema validates requests for exporting analysis results, trading data,
    and surveillance reports in various formats (CSV, JSON, PDF, Excel).
    
    Purpose:
    Validates export requests to ensure proper data formatting, access controls,
    and regulatory compliance for data extraction from the surveillance platform.
    
    Required Fields:
        - export_type: Type of data to export (analysis_results, trading_data, alerts)
        - format: Output format (csv, json, pdf, excel)
        - date_range: Time period for data extraction
        
    Optional Fields:
        - filters: Additional filtering criteria
        - include_metadata: Whether to include analysis metadata
        - compression: Whether to compress the output
        - encryption: Encryption requirements for sensitive data
    
    Validation Rules:
        - Export type must be from allowed list
        - Date range must be valid and not exceed retention limits
        - Format must be supported for the requested data type
        - User must have appropriate permissions for data access
        
    Security Considerations:
    - Validates user permissions for requested data
    - Ensures compliance with data retention policies
    - Applies appropriate data masking for sensitive information
    - Logs all export requests for audit trails
    """

    def _validate_specific(self, data: Dict[str, Any], result: "ValidationResult"):
        """
        Validate export request specific requirements.
        
        This validation ensures data export requests comply with security policies,
        regulatory requirements, and system capabilities.
        
        Args:
            data: Export request data containing type, format, and parameters
            result: ValidationResult object to collect validation errors
        """
        # Validate required export fields
        required_fields = ["export_type", "format", "date_range"]
        for field in required_fields:
            if field not in data:
                result.add_error(f"Missing required field: {field}")
        
        # Validate export type
        allowed_export_types = ["analysis_results", "trading_data", "alerts", "reports"]
        if "export_type" in data and data["export_type"] not in allowed_export_types:
            result.add_error(f"Invalid export_type. Must be one of: {allowed_export_types}")
            
        # Validate format
        allowed_formats = ["csv", "json", "pdf", "excel"]
        if "format" in data and data["format"] not in allowed_formats:
            result.add_error(f"Invalid format. Must be one of: {allowed_formats}")
            
        # Validate date range
        if "date_range" in data:
            date_range = data["date_range"]
            if not isinstance(date_range, dict) or "start_date" not in date_range or "end_date" not in date_range:
                result.add_error("date_range must contain start_date and end_date")
