"""
Cross-Desk Collusion Model Configuration.

This module provides configuration settings for the cross-desk collusion
detection model, including risk thresholds, model parameters, and evidence weights.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CrossDeskCollusionConfig:
    """
    Configuration class for cross-desk collusion detection model.

    This class manages all configuration parameters for the cross-desk collusion
    model including risk thresholds, evidence weights, and model parameters.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration.

        Args:
            config: Optional configuration dictionary to override defaults
        """
        self.config = config or {}
        self.default_config = self._get_default_config()

        # Merge user config with defaults
        self.merged_config = self._merge_configs(self.default_config, self.config)

        logger.info("Cross-desk collusion configuration initialized")

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values.

        Returns:
            Default configuration dictionary
        """
        return {
            "risk_thresholds": {
                "low_risk": 0.35,
                "medium_risk": 0.65,
                "high_risk": 0.85,
            },
            "evidence_weights": {
                "comms_metadata": 0.20,  # Communication patterns
                "profit_motivation": 0.18,  # Unusual profit sharing
                "order_behavior": 0.18,  # Order synchronization
                "cross_venue_coordination": 0.15,  # Trading correlation
                "access_pattern": 0.15,  # Information sharing
                "market_segmentation": 0.14,  # Market division
            },
            "model_parameters": {
                "use_latent_intent": True,
                "communication_sensitivity": 0.8,
                "profit_sharing_threshold": 0.7,
                "order_synchronization_window": 300,  # seconds
                "market_division_threshold": 0.6,
            },
            "inference_parameters": {
                "method": "variable_elimination",
                "max_iterations": 1000,
                "convergence_threshold": 1e-6,
                "evidence_combination_method": "weighted_average",
            },
            "fallback_parameters": {
                "communication_fallback_prior": [0.80, 0.15, 0.05],
                "profit_fallback_prior": [0.75, 0.20, 0.05],
                "order_behavior_fallback_prior": [0.70, 0.25, 0.05],
                "coordination_fallback_prior": [0.85, 0.12, 0.03],
                "access_pattern_fallback_prior": [0.78, 0.18, 0.04],
                "market_segmentation_fallback_prior": [0.82, 0.15, 0.03],
            },
            "validation_parameters": {
                "min_evidence_nodes": 3,
                "required_data_quality": 0.7,
                "fallback_tolerance": 0.4,
                "confidence_threshold": 0.6,
            },
        }

    def _merge_configs(
        self, default: Dict[str, Any], user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge user configuration with default configuration.

        Args:
            default: Default configuration
            user: User configuration

        Returns:
            Merged configuration
        """
        merged = default.copy()

        for key, value in user.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value

        return merged

    def get_risk_thresholds(self) -> Dict[str, float]:
        """
        Get risk threshold values.

        Returns:
            Risk thresholds dictionary
        """
        return self.merged_config["risk_thresholds"]

    def get_evidence_weights(self) -> Dict[str, float]:
        """
        Get evidence weight values.

        Returns:
            Evidence weights dictionary
        """
        return self.merged_config["evidence_weights"]

    def get_model_parameters(self) -> Dict[str, Any]:
        """
        Get model parameters.

        Returns:
            Model parameters dictionary
        """
        return self.merged_config["model_parameters"]

    def get_inference_parameters(self) -> Dict[str, Any]:
        """
        Get inference parameters.

        Returns:
            Inference parameters dictionary
        """
        return self.merged_config["inference_parameters"]

    def get_fallback_parameters(self) -> Dict[str, Any]:
        """
        Get fallback parameters.

        Returns:
            Fallback parameters dictionary
        """
        return self.merged_config["fallback_parameters"]

    def get_validation_parameters(self) -> Dict[str, Any]:
        """
        Get validation parameters.

        Returns:
            Validation parameters dictionary
        """
        return self.merged_config["validation_parameters"]

    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete merged configuration.

        Returns:
            Complete configuration dictionary
        """
        return self.merged_config.copy()

    def update_config(self, updates: Dict[str, Any]):
        """
        Update configuration with new values.

        Args:
            updates: Dictionary of configuration updates
        """
        self.merged_config = self._merge_configs(self.merged_config, updates)
        logger.info("Configuration updated")

    def validate_config(self) -> bool:
        """
        Validate the configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate risk thresholds
            thresholds = self.get_risk_thresholds()
            if not (
                0
                <= thresholds["low_risk"]
                <= thresholds["medium_risk"]
                <= thresholds["high_risk"]
                <= 1
            ):
                logger.error(
                    "Invalid risk thresholds: must be in ascending order between 0 and 1"
                )
                return False

            # Validate evidence weights
            weights = self.get_evidence_weights()
            weight_sum = sum(weights.values())
            if not (0.95 <= weight_sum <= 1.05):  # Allow small floating point errors
                logger.error(
                    f"Evidence weights sum to {weight_sum}, should be approximately 1.0"
                )
                return False

            # Validate model parameters
            model_params = self.get_model_parameters()
            if not isinstance(model_params.get("use_latent_intent"), bool):
                logger.error("use_latent_intent must be a boolean")
                return False

            logger.info("Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            return False

    def get_node_fallback_prior(self, node_name: str) -> Optional[list]:
        """
        Get fallback prior for a specific node.

        Args:
            node_name: Name of the node

        Returns:
            Fallback prior list or None if not found
        """
        fallback_params = self.get_fallback_parameters()
        fallback_key = f"{node_name}_fallback_prior"
        return fallback_params.get(fallback_key)

    def __repr__(self) -> str:
        """String representation of the configuration."""
        return f"CrossDeskCollusionConfig(use_latent_intent={self.merged_config['model_parameters']['use_latent_intent']})"
