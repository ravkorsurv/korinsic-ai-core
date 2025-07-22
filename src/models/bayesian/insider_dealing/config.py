"""
Insider dealing model configuration.

This module contains configuration management for the insider dealing
detection model, including thresholds, parameters, and model settings.
"""

from typing import Any, Dict, Optional


class InsiderDealingConfig:
    """
    Configuration manager for insider dealing model.

    This class manages all configuration parameters specific to the
    insider dealing detection model.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration.

        Args:
            config: Optional configuration dictionary
        """
        # Default configuration
        self.default_config = {
            "risk_thresholds": {"low_risk": 0.3, "medium_risk": 0.6, "high_risk": 0.8},
            "model_parameters": {
                "use_latent_intent": False,
                "inference_method": "variable_elimination",
                "fallback_enabled": True,
                "esi_enabled": True,
            },
            "evidence_weights": {
                "trade_pattern": 1.0,
                "comms_intent": 1.0,
                "pnl_drift": 1.0,
                "profit_motivation": 0.8,
                "access_pattern": 0.9,
                "order_behavior": 0.7,
                "comms_metadata": 0.6,
            },
            "validation_rules": {
                "min_evidence_nodes": 2,
                "max_fallback_ratio": 0.7,
                "min_confidence_threshold": 0.5,
            },
            "output_settings": {
                "include_esi": True,
                "include_fallback_report": True,
                "include_confidence_scores": True,
                "decimal_precision": 3,
            },
        }

        # Merge with provided configuration
        self.config = self._merge_config(self.default_config, config or {})

    def _merge_config(
        self, default: Dict[str, Any], custom: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge custom configuration with defaults.

        Args:
            default: Default configuration
            custom: Custom configuration

        Returns:
            Merged configuration
        """
        merged = default.copy()

        for key, value in custom.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self._merge_config(merged[key], value)
            else:
                merged[key] = value

        return merged

    def get_risk_thresholds(self) -> Dict[str, float]:
        """
        Get risk threshold configuration.

        Returns:
            Risk thresholds dictionary
        """
        return self.config["risk_thresholds"].copy()

    def get_model_parameters(self) -> Dict[str, Any]:
        """
        Get model parameters configuration.

        Returns:
            Model parameters dictionary
        """
        return self.config["model_parameters"].copy()

    def get_evidence_weights(self) -> Dict[str, float]:
        """
        Get evidence weights configuration.

        Returns:
            Evidence weights dictionary
        """
        return self.config["evidence_weights"].copy()

    def get_validation_rules(self) -> Dict[str, Any]:
        """
        Get validation rules configuration.

        Returns:
            Validation rules dictionary
        """
        return self.config["validation_rules"].copy()

    def get_output_settings(self) -> Dict[str, Any]:
        """
        Get output settings configuration.

        Returns:
            Output settings dictionary
        """
        return self.config["output_settings"].copy()

    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration.

        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()

    def update_config(self, updates: Dict[str, Any]):
        """
        Update configuration with new values.

        Args:
            updates: Configuration updates
        """
        self.config = self._merge_config(self.config, updates)

    def set_risk_threshold(self, risk_level: str, threshold: float):
        """
        Set a specific risk threshold.

        Args:
            risk_level: Risk level name (low_risk, medium_risk, high_risk)
            threshold: Threshold value
        """
        if risk_level in self.config["risk_thresholds"]:
            self.config["risk_thresholds"][risk_level] = threshold
        else:
            raise ValueError(f"Unknown risk level: {risk_level}")

    def set_evidence_weight(self, evidence_name: str, weight: float):
        """
        Set weight for a specific evidence type.

        Args:
            evidence_name: Name of the evidence
            weight: Weight value
        """
        if weight < 0 or weight > 1:
            raise ValueError("Weight must be between 0 and 1")

        self.config["evidence_weights"][evidence_name] = weight

    def enable_latent_intent(self, enabled: bool = True):
        """
        Enable or disable latent intent modeling.

        Args:
            enabled: Whether to enable latent intent
        """
        self.config["model_parameters"]["use_latent_intent"] = enabled

    def enable_esi(self, enabled: bool = True):
        """
        Enable or disable Evidence Sufficiency Index calculation.

        Args:
            enabled: Whether to enable ESI
        """
        self.config["model_parameters"]["esi_enabled"] = enabled
        self.config["output_settings"]["include_esi"] = enabled

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate the current configuration.

        Returns:
            Validation report
        """
        validation_report = {"is_valid": True, "errors": [], "warnings": []}

        # Validate risk thresholds
        thresholds = self.config["risk_thresholds"]
        if thresholds["low_risk"] >= thresholds["medium_risk"]:
            validation_report["is_valid"] = False
            validation_report["errors"].append(
                "Low risk threshold must be less than medium risk threshold"
            )

        if thresholds["medium_risk"] >= thresholds["high_risk"]:
            validation_report["is_valid"] = False
            validation_report["errors"].append(
                "Medium risk threshold must be less than high risk threshold"
            )

        # Validate evidence weights
        for evidence, weight in self.config["evidence_weights"].items():
            if not 0 <= weight <= 1:
                validation_report["is_valid"] = False
                validation_report["errors"].append(
                    f"Evidence weight for {evidence} must be between 0 and 1"
                )

        # Validate validation rules
        validation_rules = self.config["validation_rules"]
        if validation_rules["min_evidence_nodes"] < 1:
            validation_report["warnings"].append(
                "Minimum evidence nodes should be at least 1"
            )

        if validation_rules["max_fallback_ratio"] > 1:
            validation_report["is_valid"] = False
            validation_report["errors"].append(
                "Maximum fallback ratio cannot exceed 1.0"
            )

        return validation_report

    def get_config_summary(self) -> str:
        """
        Get a human-readable summary of the configuration.

        Returns:
            Configuration summary string
        """
        summary = "Insider Dealing Model Configuration:\n"
        summary += (
            f"  Risk Thresholds: Low={self.config['risk_thresholds']['low_risk']}, "
        )
        summary += f"Medium={self.config['risk_thresholds']['medium_risk']}, "
        summary += f"High={self.config['risk_thresholds']['high_risk']}\n"
        summary += (
            f"  Latent Intent: {self.config['model_parameters']['use_latent_intent']}\n"
        )
        summary += f"  ESI Enabled: {self.config['model_parameters']['esi_enabled']}\n"
        summary += f"  Fallback Enabled: {self.config['model_parameters']['fallback_enabled']}\n"
        summary += (
            f"  Evidence Weights: {len(self.config['evidence_weights'])} configured\n"
        )

        return summary
