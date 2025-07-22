"""
Response schemas for API v1 response formatting.

This module contains schema classes for formatting API responses consistently.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class BaseResponseSchema:
    """Base class for response schemas."""

    def build_response(self, **kwargs) -> Dict[str, Any]:
        """
        Build a standardized response.

        Returns:
            Dictionary containing formatted response
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            **self._build_specific_response(**kwargs),
        }

    def _build_specific_response(self, **kwargs) -> Dict[str, Any]:
        """Build specific response content. Override in subclasses."""
        return {}


class AnalysisResponseSchema(BaseResponseSchema):
    """Schema for analysis response formatting."""

    def build_response(
        self,
        analysis_result=None,
        regulatory_rationales=None,
        include_rationale=False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Build analysis response.

        Args:
            analysis_result: AnalysisResult object
            regulatory_rationales: List of regulatory rationales
            include_rationale: Whether to include regulatory rationale

        Returns:
            Formatted analysis response
        """
        if not analysis_result:
            return self._build_error_response("No analysis result provided")

        response = {
            "timestamp": analysis_result.timestamp,
            "analysis_id": analysis_result.analysis_id,
            "risk_scores": analysis_result.risk_scores,
            "alerts": analysis_result.alerts,
            "processed_data_summary": {
                "trades_analyzed": len(
                    analysis_result.processed_data.get("trades", [])
                ),
                "timeframe": analysis_result.processed_data.get("timeframe", "unknown"),
                "instruments": analysis_result.processed_data.get("instruments", []),
            },
        }

        # Add regulatory rationales if requested
        if include_rationale:
            response["regulatory_rationales"] = regulatory_rationales or []

        # Add processing metadata if available
        if analysis_result.processing_time_ms is not None:
            response["processing_time_ms"] = analysis_result.processing_time_ms

        if analysis_result.metadata:
            response["metadata"] = analysis_result.metadata

        return response

    def _build_error_response(self, error_message: str) -> Dict[str, Any]:
        """Build error response for analysis."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": error_message,
            "analysis_id": None,
            "risk_scores": {},
            "alerts": [],
        }


class BatchAnalysisResponseSchema(BaseResponseSchema):
    """Schema for batch analysis response formatting."""

    def build_response(
        self, batch_results=None, batch_id=None, **kwargs
    ) -> Dict[str, Any]:
        """
        Build batch analysis response.

        Args:
            batch_results: List of batch analysis results
            batch_id: Batch identifier

        Returns:
            Formatted batch response
        """
        if not batch_results:
            batch_results = []

        if not batch_id:
            batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "batch_id": batch_id,
            "results": batch_results,
            "summary": {
                "total_analyses": len(batch_results),
                "successful_analyses": len(
                    [r for r in batch_results if "error" not in r]
                ),
                "failed_analyses": len([r for r in batch_results if "error" in r]),
                "total_alerts": sum(
                    len(r.get("alerts", [])) for r in batch_results if "alerts" in r
                ),
            },
        }

        return response


class SimulationResponseSchema(BaseResponseSchema):
    """Schema for simulation response formatting."""

    def build_response(
        self,
        scenario_type=None,
        parameters=None,
        risk_score=None,
        simulated_data=None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Build simulation response.

        Args:
            scenario_type: Type of scenario simulated
            parameters: Simulation parameters
            risk_score: Calculated risk score
            simulated_data: Generated simulation data

        Returns:
            Formatted simulation response
        """
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "scenario_type": scenario_type,
            "parameters": parameters or {},
            "risk_score": risk_score or {},
            "simulated_data": simulated_data or {},
        }

        return response


class AlertsResponseSchema(BaseResponseSchema):
    """Schema for alerts response formatting."""

    def build_response(
        self, alerts=None, count=None, filters=None, **kwargs
    ) -> Dict[str, Any]:
        """
        Build alerts response.

        Args:
            alerts: List of alerts
            count: Total count of alerts
            filters: Applied filters

        Returns:
            Formatted alerts response
        """
        if alerts is None:
            alerts = []

        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "alerts": alerts,
            "count": count if count is not None else len(alerts),
            "filters": filters or {},
        }

        return response


class ModelsInfoResponseSchema(BaseResponseSchema):
    """Schema for models info response formatting."""

    def build_response(self, models_info=None, **kwargs) -> Dict[str, Any]:
        """
        Build models info response.

        Args:
            models_info: Information about available models

        Returns:
            Formatted models info response
        """
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "models": models_info or {},
        }

        return response


class ExportResponseSchema(BaseResponseSchema):
    """Schema for export response formatting."""

    def build_response(
        self, export_type=None, filename=None, export_data=None, **kwargs
    ) -> Dict[str, Any]:
        """
        Build export response.

        Args:
            export_type: Type of export (STOR, CSV, etc.)
            filename: Generated filename
            export_data: Exported data

        Returns:
            Formatted export response
        """
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "export_type": export_type,
            "filename": filename,
            "message": f"Export completed successfully",
        }

        if export_data:
            response["export_data"] = export_data

        return response


class ErrorResponseSchema(BaseResponseSchema):
    """Schema for error response formatting."""

    def build_response(
        self, error_type=None, message=None, status_code=None, details=None, **kwargs
    ) -> Dict[str, Any]:
        """
        Build error response.

        Args:
            error_type: Type of error
            message: Error message
            status_code: HTTP status code
            details: Additional error details

        Returns:
            Formatted error response
        """
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": error_type or "Unknown error",
            "message": message or "An error occurred",
            "status_code": status_code or 500,
        }

        if details:
            response["details"] = details

        return response


class DQSIResponseSchema(BaseResponseSchema):
    """Schema for DQSI response formatting."""

    def build_response(
        self, metrics=None, report=None, recommendations=None, **kwargs
    ) -> Dict[str, Any]:
        """
        Build DQSI response.

        Args:
            metrics: DQSI metrics object
            report: DQSI report
            recommendations: Improvement recommendations

        Returns:
            Formatted DQSI response
        """
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "dqsi_score": metrics.overall_score if metrics else 0.0,
            "dimension_scores": metrics.dimension_scores if metrics else {},
            "report": report or {},
            "recommendations": recommendations or [],
        }

        if metrics:
            response["status"] = self._get_status_from_score(metrics.overall_score)

        return response

    def _get_status_from_score(self, score: float) -> str:
        """Get status label from score."""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.8:
            return "good"
        elif score >= 0.6:
            return "fair"
        elif score >= 0.4:
            return "poor"
        else:
            return "critical"


class HealthResponseSchema(BaseResponseSchema):
    """Schema for health check response formatting."""

    def build_response(
        self, status=None, service_name=None, version=None, **kwargs
    ) -> Dict[str, Any]:
        """
        Build health check response.

        Args:
            status: Health status
            service_name: Name of the service
            version: Service version

        Returns:
            Formatted health response
        """
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": status or "healthy",
            "service": service_name or "kor-ai-surveillance-platform",
        }

        if version:
            response["version"] = version

        return response
