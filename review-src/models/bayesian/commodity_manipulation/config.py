"""
Configuration for the commodity manipulation detection model.

This module contains configuration settings, thresholds, and parameters
for the commodity manipulation detection model.
"""

from typing import Any, Dict, Optional


class CommodityManipulationConfig:
    """
    Configuration class for commodity manipulation detection model.

    This class manages all configuration parameters including risk thresholds,
    model parameters, and other settings for the commodity manipulation model.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration.

        Args:
            config: Optional configuration dictionary to override defaults
        """
        self.default_config = {
            "risk_thresholds": {
                "low_risk": 0.25,
                "medium_risk": 0.55,
                "high_risk": 0.75,
            },
            "model_parameters": {
                "use_latent_intent": True,
                "benchmark_window_sensitivity": 0.8,
                "liquidity_impact_weight": 0.15,
                "price_impact_sensitivity": 0.7,
                "volume_participation_threshold": 0.3,
                "cross_venue_correlation_threshold": 0.6,
            },
            "evidence_weights": {
                "liquidity_context": 0.15,
                "benchmark_timing": 0.25,
                "order_clustering": 0.20,
                "price_impact_ratio": 0.20,
                "volume_participation": 0.15,
                "cross_venue_coordination": 0.05,
            },
            "inference_parameters": {
                "method": "variable_elimination",
                "max_iterations": 100,
                "convergence_threshold": 1e-6,
            },
            "fallback_parameters": {
                "use_fallback_priors": True,
                "fallback_penalty": 0.1,
                "minimum_evidence_threshold": 0.3,
            },
        }

        # Override with provided config
        if config:
            self.default_config.update(config)

    def get_risk_thresholds(self) -> Dict[str, float]:
        """
        Get risk threshold settings.

        Returns:
            Dictionary of risk threshold values
        """
        return self.default_config["risk_thresholds"]

    def get_model_parameters(self) -> Dict[str, Any]:
        """
        Get model parameter settings.

        Returns:
            Dictionary of model parameters
        """
        return self.default_config["model_parameters"]

    def get_evidence_weights(self) -> Dict[str, float]:
        """
        Get evidence weight settings.

        Returns:
            Dictionary of evidence weights
        """
        return self.default_config["evidence_weights"]

    def get_inference_parameters(self) -> Dict[str, Any]:
        """
        Get inference parameter settings.

        Returns:
            Dictionary of inference parameters
        """
        return self.default_config["inference_parameters"]

    def get_fallback_parameters(self) -> Dict[str, Any]:
        """
        Get fallback parameter settings.

        Returns:
            Dictionary of fallback parameters
        """
        return self.default_config["fallback_parameters"]

    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration.

        Returns:
            Complete configuration dictionary
        """
        return self.default_config.copy()

    def update_config(self, updates: Dict[str, Any]):
        """
        Update configuration with new values.

        Args:
            updates: Dictionary of configuration updates
        """
        self.default_config.update(updates)

    def set_risk_threshold(self, risk_level: str, threshold: float):
        """
        Set a specific risk threshold.

        Args:
            risk_level: Risk level (low_risk, medium_risk, high_risk)
            threshold: Threshold value
        """
        if risk_level in self.default_config["risk_thresholds"]:
            self.default_config["risk_thresholds"][risk_level] = threshold
        else:
            raise ValueError(f"Unknown risk level: {risk_level}")

    def set_model_parameter(self, parameter: str, value: Any):
        """
        Set a specific model parameter.

        Args:
            parameter: Parameter name
            value: Parameter value
        """
        self.default_config["model_parameters"][parameter] = value

    def get_benchmark_window_sensitivity(self) -> float:
        """
        Get benchmark window sensitivity parameter.

        Returns:
            Benchmark window sensitivity value
        """
        return self.default_config["model_parameters"]["benchmark_window_sensitivity"]

    def get_liquidity_impact_weight(self) -> float:
        """
        Get liquidity impact weight parameter.

        Returns:
            Liquidity impact weight value
        """
        return self.default_config["model_parameters"]["liquidity_impact_weight"]

    def get_price_impact_sensitivity(self) -> float:
        """
        Get price impact sensitivity parameter.

        Returns:
            Price impact sensitivity value
        """
        return self.default_config["model_parameters"]["price_impact_sensitivity"]

    def get_volume_participation_threshold(self) -> float:
        """
        Get volume participation threshold parameter.

        Returns:
            Volume participation threshold value
        """
        return self.default_config["model_parameters"]["volume_participation_threshold"]

    def get_cross_venue_correlation_threshold(self) -> float:
        """
        Get cross-venue correlation threshold parameter.

        Returns:
            Cross-venue correlation threshold value
        """
        return self.default_config["model_parameters"][
            "cross_venue_correlation_threshold"
        ]

    def is_latent_intent_enabled(self) -> bool:
        """
        Check if latent intent modeling is enabled.

        Returns:
            True if latent intent is enabled, False otherwise
        """
        return self.default_config["model_parameters"]["use_latent_intent"]

    def validate_config(self) -> bool:
        """
        Validate the configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        # Check required sections
        required_sections = [
            "risk_thresholds",
            "model_parameters",
            "evidence_weights",
            "inference_parameters",
            "fallback_parameters",
        ]

        for section in required_sections:
            if section not in self.default_config:
                return False

        # Check risk thresholds
        thresholds = self.default_config["risk_thresholds"]
        if not (
            0
            <= thresholds["low_risk"]
            <= thresholds["medium_risk"]
            <= thresholds["high_risk"]
            <= 1
        ):
            return False

        # Check evidence weights sum to 1
        weights = self.default_config["evidence_weights"]
        if abs(sum(weights.values()) - 1.0) > 1e-6:
            return False

        return True
