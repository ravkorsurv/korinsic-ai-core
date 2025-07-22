"""
Configuration for Wash Trade Detection Model.

This module provides configuration settings and parameters for the
wash trade detection Bayesian model.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WashTradeDetectionConfig:
    """
    Configuration class for wash trade detection model.

    This class manages all configuration parameters for the wash trade detection
    model including node parameters, CPT settings, and model hyperparameters.
    """

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration.

        Args:
            config_dict: Optional configuration dictionary
        """
        self.config = config_dict or {}
        self._default_config = self._get_default_config()
        self._merge_configs()

        logger.info("Wash trade detection model configuration initialized")

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration for the model.

        Returns:
            Default configuration dictionary
        """
        return {
            # Model metadata
            "model_name": "wash_trade_detection",
            "model_version": "1.0.0",
            "description": "KOR.AI Model Enhancement: Wash Trades & Signal Distortion Detection",
            "created_date": "2025-01-01",
            "updated_date": "2025-01-01",
            # Model parameters
            "use_latent_intent": True,
            "enable_signal_distortion": True,
            "enable_algo_reaction_detection": True,
            "enable_commodity_derivatives": True,
            "enable_implied_liquidity_detection": True,
            # Detection thresholds
            "wash_trade_probability_threshold": 0.7,
            "signal_distortion_threshold": 0.6,
            "algo_reaction_threshold": 0.65,
            "entity_match_threshold": 0.8,
            "price_impact_threshold": 0.7,
            "implied_liquidity_threshold": 0.75,
            # Time window parameters
            "algo_reaction_window_ms": 100,
            "price_impact_window_seconds": 60,
            "mean_reversion_window_seconds": 30,
            "order_book_snapshot_window_ms": 50,
            # Entity matching parameters
            "lei_exact_match_weight": 1.0,
            "lei_affiliate_match_weight": 0.8,
            "entity_name_match_weight": 0.6,
            "beneficial_ownership_threshold": 0.25,
            # Algorithmic framework detection
            "algo_framework_similarity_threshold": 0.7,
            "ptf_framework_match_weight": 0.9,
            "execution_venue_match_weight": 0.6,
            # Signal distortion parameters
            "order_book_imbalance_threshold": 0.3,
            "quote_frequency_change_threshold": 2.0,
            "spread_manipulation_threshold": 0.15,
            "volume_distortion_threshold": 0.4,
            # Commodity derivatives parameters
            "time_spread_detection_enabled": True,
            "commodity_leg_matching_enabled": True,
            "implied_strategy_detection_enabled": True,
            "cross_contract_analysis_enabled": True,
            # Price impact anomaly detection
            "price_spike_threshold": 0.02,
            "price_fade_threshold": 0.02,
            "volatility_baseline_window_days": 30,
            "extreme_deviation_threshold": 3.0,
            # Venue and execution parameters
            "venue_implied_matching_enabled": True,
            "execution_source_tracking_enabled": True,
            "cross_venue_analysis_enabled": True,
            # Risk assessment weights
            "risk_factor_weights": {
                "wash_trade_likelihood": 0.25,
                "signal_distortion_index": 0.20,
                "algo_reaction_sensitivity": 0.15,
                "strategy_leg_overlap": 0.15,
                "price_impact_anomaly": 0.15,
                "implied_liquidity_conflict": 0.10,
            },
            # Latent intent inference parameters
            "latent_intent_enabled": True,
            "wash_trade_intent_threshold": 0.6,
            "signal_distortion_intent_threshold": 0.65,
            "convergence_evidence_threshold": 0.7,
            # Model validation parameters
            "validation_enabled": True,
            "cross_validation_folds": 5,
            "test_split_ratio": 0.2,
            "performance_metrics": ["precision", "recall", "f1_score", "auc_roc"],
            # Logging and monitoring
            "logging_level": "INFO",
            "enable_performance_monitoring": True,
            "enable_model_explanations": True,
            "enable_audit_trail": True,
            # CPT configuration
            "cpt_learning_enabled": True,
            "cpt_update_frequency": "daily",
            "cpt_smoothing_factor": 0.1,
            "cpt_minimum_samples": 100,
            # Node-specific configurations
            "node_configs": {
                "wash_trade_likelihood": {
                    "detection_logic": {
                        "counterparty_analysis": True,
                        "algo_framework_analysis": True,
                        "implied_strategy_analysis": True,
                        "time_delta_analysis": True,
                    },
                    "data_inputs": [
                        "counterparty_id",
                        "strategy_execution_flags",
                        "trade_linkage_data",
                        "time_delta_data",
                        "match_source_data",
                    ],
                },
                "signal_distortion_index": {
                    "affected_dimensions": [
                        "volume_at_best_bid_ask",
                        "order_book_imbalance",
                        "short_term_volatility",
                        "quote_frequency",
                    ],
                    "signal_check_logic": {
                        "pre_post_comparison": True,
                        "spread_analysis": True,
                        "size_signal_analysis": True,
                        "misleading_signal_detection": True,
                    },
                },
                "algo_reaction_sensitivity": {
                    "derived_from": [
                        "order_flow_clustering",
                        "reaction_time_delta",
                        "passive_aggressive_ratio",
                    ],
                    "reaction_time_threshold_ms": 100,
                    "order_clustering_threshold": 0.7,
                },
                "strategy_leg_overlap": {
                    "use_cases": [
                        "commodity_derivatives_spreads",
                        "time_spread_analysis",
                        "cross_contract_matching",
                    ],
                    "implementation": {
                        "leg_level_matching": True,
                        "third_party_risk_validation": True,
                        "time_separated_contracts": True,
                    },
                },
                "price_impact_anomaly": {
                    "factors": [
                        "immediate_mean_reversion",
                        "price_spike_fade",
                        "volatility_baseline_comparison",
                    ],
                    "time_windows": {
                        "immediate_window_seconds": 10,
                        "short_term_window_seconds": 60,
                        "baseline_window_days": 30,
                    },
                },
                "implied_liquidity_conflict": {
                    "focus_areas": [
                        "venue_implied_matching",
                        "strategy_leg_interaction",
                        "artificial_matching_detection",
                    ],
                    "detection_methods": [
                        "leg_execution_source_comparison",
                        "participant_book_analysis",
                        "strategy_order_matching",
                    ],
                },
            },
        }

    def _merge_configs(self):
        """Merge default configuration with provided configuration."""

        def merge_dict(
            default: Dict[str, Any], provided: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Recursively merge two dictionaries."""
            result = default.copy()
            for key, value in provided.items():
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result

        self.config = merge_dict(self._default_config, self.config)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """
        Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config_dict = self.config

        for k in keys[:-1]:
            if k not in config_dict:
                config_dict[k] = {}
            config_dict = config_dict[k]

        config_dict[keys[-1]] = value

    def get_model_metadata(self) -> Dict[str, Any]:
        """
        Get model metadata.

        Returns:
            Model metadata dictionary
        """
        return {
            "model_name": self.get("model_name"),
            "model_version": self.get("model_version"),
            "description": self.get("description"),
            "created_date": self.get("created_date"),
            "updated_date": self.get("updated_date"),
        }

    def get_detection_thresholds(self) -> Dict[str, float]:
        """
        Get detection thresholds.

        Returns:
            Detection thresholds dictionary
        """
        return {
            "wash_trade_probability_threshold": self.get(
                "wash_trade_probability_threshold"
            ),
            "signal_distortion_threshold": self.get("signal_distortion_threshold"),
            "algo_reaction_threshold": self.get("algo_reaction_threshold"),
            "entity_match_threshold": self.get("entity_match_threshold"),
            "price_impact_threshold": self.get("price_impact_threshold"),
            "implied_liquidity_threshold": self.get("implied_liquidity_threshold"),
        }

    def get_time_parameters(self) -> Dict[str, int]:
        """
        Get time window parameters.

        Returns:
            Time parameters dictionary
        """
        return {
            "algo_reaction_window_ms": self.get("algo_reaction_window_ms"),
            "price_impact_window_seconds": self.get("price_impact_window_seconds"),
            "mean_reversion_window_seconds": self.get("mean_reversion_window_seconds"),
            "order_book_snapshot_window_ms": self.get("order_book_snapshot_window_ms"),
        }

    def get_node_config(self, node_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific node.

        Args:
            node_name: Name of the node

        Returns:
            Node configuration dictionary
        """
        return self.get(f"node_configs.{node_name}", {})

    def get_risk_factor_weights(self) -> Dict[str, float]:
        """
        Get risk factor weights.

        Returns:
            Risk factor weights dictionary
        """
        return self.get("risk_factor_weights", {})

    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature_name: Name of the feature

        Returns:
            True if enabled, False otherwise
        """
        return self.get(feature_name, False)

    def validate_configuration(self) -> bool:
        """
        Validate the configuration.

        Returns:
            True if valid, False otherwise
        """
        try:
            # Validate required fields
            required_fields = [
                "model_name",
                "model_version",
                "wash_trade_probability_threshold",
                "signal_distortion_threshold",
                "algo_reaction_threshold",
            ]

            for field in required_fields:
                if self.get(field) is None:
                    logger.error(f"Missing required configuration field: {field}")
                    return False

            # Validate threshold ranges
            thresholds = self.get_detection_thresholds()
            for threshold_name, threshold_value in thresholds.items():
                if not (0.0 <= threshold_value <= 1.0):
                    logger.error(
                        f"Invalid threshold value for {threshold_name}: {threshold_value}"
                    )
                    return False

            # Validate risk factor weights
            weights = self.get_risk_factor_weights()
            total_weight = sum(weights.values())
            if not (0.9 <= total_weight <= 1.1):  # Allow small tolerance
                logger.error(f"Risk factor weights don't sum to 1.0: {total_weight}")
                return False

            # Validate time parameters
            time_params = self.get_time_parameters()
            for param_name, param_value in time_params.items():
                if param_value <= 0:
                    logger.error(f"Invalid time parameter {param_name}: {param_value}")
                    return False

            logger.info("Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()

    def __str__(self) -> str:
        """String representation of the configuration."""
        return f"WashTradeDetectionConfig(model={self.get('model_name')}, version={self.get('model_version')})"

    def __repr__(self) -> str:
        """Detailed string representation of the configuration."""
        return f"WashTradeDetectionConfig({self.get_model_metadata()})"
