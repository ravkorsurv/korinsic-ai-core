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
    """Schema for analysis request validation"""

    pass


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
    """Schema for export request validation."""

    def _validate_specific(self, data: Dict[str, Any], result: "ValidationResult"):
        """Validate export request specific requirements."""
        # This would be similar to analysis request but might have different requirements
        # For now, use the same validation as analysis request
        analysis_schema = AnalysisRequestSchema()
        analysis_result = analysis_schema.validate(data)

        if not analysis_result.is_valid:
            for error in analysis_result.errors:
                result.add_error(error)
