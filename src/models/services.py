"""
Model Service for Kor.ai Surveillance Platform.

This module provides a high-level service interface for managing
and coordinating different types of models in the surveillance platform.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
	from .bayesian.registry import BayesianModelRegistry  # type: ignore
except Exception:
	BayesianModelRegistry = None  # type: ignore

logger = logging.getLogger(__name__)


class ModelService:
    """
    High-level service for managing surveillance models.

    This service provides a unified interface for working with different
    types of models (Bayesian, ML, etc.) in the surveillance platform.
    """

    def __init__(self):
        """Initialize the model service."""
        self.bayesian_registry = BayesianModelRegistry()
        self.service_stats = {
            "requests_processed": 0,
            "successful_predictions": 0,
            "failed_predictions": 0,
            "start_time": datetime.utcnow().isoformat(),
        }

        logger.info("Model service initialized")

    def predict_risk(
        self, model_type: str, evidence: Dict[str, Any], config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Predict risk using the specified model.

        Args:
            model_type: Type of model to use
            evidence: Evidence data for prediction
            config: Optional model configuration

        Returns:
            Risk prediction results
        """
        try:
            self.service_stats["requests_processed"] += 1

            # Get model instance
            model = self.bayesian_registry.get_model(model_type)

            # Apply configuration if provided
            if config and hasattr(model, "update_config"):
                model.update_config(config)

            # Perform risk calculation
            result = model.calculate_risk(evidence)

            # Add service metadata
            result["service_metadata"] = {
                "service": "ModelService",
                "timestamp": datetime.utcnow().isoformat(),
                "model_type": model_type,
                "evidence_fields": list(evidence.keys()),
                "processing_time": "calculated",  # Placeholder
            }

            self.service_stats["successful_predictions"] += 1
            logger.info(f"Successfully processed {model_type} prediction")

            return result

        except Exception as e:
            self.service_stats["failed_predictions"] += 1
            logger.error(f"Error in risk prediction: {str(e)}")

            return {
                "error": str(e),
                "service_metadata": {
                    "service": "ModelService",
                    "timestamp": datetime.utcnow().isoformat(),
                    "model_type": model_type,
                    "status": "failed",
                },
            }

    def get_available_models(self) -> Dict[str, Any]:
        """
        Get information about available models.

        Returns:
            Dictionary of available models and their information
        """
        try:
            bayesian_models = self.bayesian_registry.get_available_models()

            models_info = {}
            for model_type in bayesian_models:
                try:
                    model_info = self.bayesian_registry.get_model_info(model_type)
                    models_info[model_type] = model_info
                except Exception as e:
                    models_info[model_type] = {
                        "model_type": model_type,
                        "status": "error",
                        "error": str(e),
                    }

            return {
                "bayesian_models": models_info,
                "total_models": len(models_info),
                "service_info": {
                    "service": "ModelService",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            return {
                "error": str(e),
                "service_info": {
                    "service": "ModelService",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "failed",
                },
            }

    def validate_evidence(
        self, model_type: str, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate evidence for a specific model.

        Args:
            model_type: Type of model
            evidence: Evidence to validate

        Returns:
            Validation results
        """
        try:
            model = self.bayesian_registry.get_model(model_type)

            if hasattr(model, "validate_evidence"):
                validation_result = model.validate_evidence(evidence)
            else:
                # Basic validation
                validation_result = {
                    "is_valid": True,
                    "message": "Basic validation passed",
                }

            validation_result["service_metadata"] = {
                "service": "ModelService",
                "timestamp": datetime.utcnow().isoformat(),
                "model_type": model_type,
            }

            return validation_result

        except Exception as e:
            logger.error(f"Error validating evidence: {str(e)}")
            return {
                "is_valid": False,
                "error": str(e),
                "service_metadata": {
                    "service": "ModelService",
                    "timestamp": datetime.utcnow().isoformat(),
                    "model_type": model_type,
                    "status": "validation_failed",
                },
            }

    def get_model_configuration(self, model_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific model.

        Args:
            model_type: Type of model

        Returns:
            Model configuration
        """
        try:
            model = self.bayesian_registry.get_model(model_type)

            if hasattr(model, "get_config"):
                config = model.get_config()
            elif hasattr(model, "config"):
                config = model.config
            else:
                config = {"message": "No configuration available"}

            return {
                "model_type": model_type,
                "configuration": config,
                "service_metadata": {
                    "service": "ModelService",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting model configuration: {str(e)}")
            return {
                "error": str(e),
                "model_type": model_type,
                "service_metadata": {
                    "service": "ModelService",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "failed",
                },
            }

    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get service statistics.

        Returns:
            Service statistics
        """
        registry_stats = self.bayesian_registry.get_registry_stats()

        return {
            "service_stats": self.service_stats.copy(),
            "registry_stats": registry_stats,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the model service.

        Returns:
            Health check results
        """
        try:
            # Check if we can access the registry
            available_models = self.bayesian_registry.get_available_models()

            # Try to create a test model
            test_model = None
            if "insider_dealing" in available_models:
                test_model = self.bayesian_registry.create_model("insider_dealing", {})

            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "ModelService",
                "available_models_count": len(available_models),
                "registry_accessible": True,
                "test_model_creation": test_model is not None,
            }

            # Clean up test model
            if test_model:
                self.bayesian_registry.clear_instances()

            return health_status

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "ModelService",
                "error": str(e),
            }
