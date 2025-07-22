"""
Data Quality Configuration Loader

Loads YAML configuration files for KDEs, strategies, and DQSI settings.
Supports both environment-specific and default configurations.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .dq_strategy_base import DQConfig

logger = logging.getLogger(__name__)


class DQConfigLoader:
    """
    Configuration loader for DQSI settings

    Loads configuration from YAML files with support for:
    - Environment-specific configs
    - Default fallback configs
    - Configuration validation
    - Hot reload capabilities
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration loader

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or self._get_default_config_dir()
        self.config_cache = {}
        self.last_loaded = {}

        logger.info(f"DQ Config Loader initialized with directory: {self.config_dir}")

    def _get_default_config_dir(self) -> str:
        """Get default configuration directory"""
        # Try to find config directory relative to current file
        current_dir = Path(__file__).parent
        possible_dirs = [
            current_dir / "config",
            current_dir.parent.parent / "config",
            Path.cwd() / "config",
            Path.cwd() / "src/config",
        ]

        for config_dir in possible_dirs:
            if config_dir.exists():
                return str(config_dir)

        # Create default config directory
        default_config_dir = current_dir / "config"
        default_config_dir.mkdir(exist_ok=True)
        return str(default_config_dir)

    def load_config(self, environment: str = "default") -> DQConfig:
        """
        Load DQSI configuration for specified environment

        Args:
            environment: Environment name (default, dev, prod, etc.)

        Returns:
            DQConfig object with loaded configuration
        """
        try:
            config_file = self._get_config_file(environment)

            if config_file and os.path.exists(config_file):
                config_data = self._load_yaml_file(config_file)
                return self._create_dq_config(config_data)
            else:
                logger.warning(
                    f"Config file not found for environment '{environment}', using defaults"
                )
                return DQConfig()  # Return default config

        except Exception as e:
            logger.error(f"Error loading config for environment '{environment}': {e}")
            return DQConfig()  # Return default config on error

    def load_kde_mappings(self, environment: str = "default") -> Dict[str, str]:
        """
        Load KDE to dimension mappings

        Args:
            environment: Environment name

        Returns:
            Dictionary mapping KDE names to dimensions
        """
        try:
            kde_file = os.path.join(self.config_dir, f"kde_mappings_{environment}.yaml")

            if not os.path.exists(kde_file):
                kde_file = os.path.join(self.config_dir, "kde_mappings_default.yaml")

            if os.path.exists(kde_file):
                return self._load_yaml_file(kde_file)
            else:
                return self._get_default_kde_mappings()

        except Exception as e:
            logger.error(f"Error loading KDE mappings: {e}")
            return self._get_default_kde_mappings()

    def load_typology_profiles(self, environment: str = "default") -> Dict[str, Any]:
        """
        Load typology-specific profiles

        Args:
            environment: Environment name

        Returns:
            Dictionary of typology profiles
        """
        try:
            typology_file = os.path.join(
                self.config_dir, f"typology_profiles_{environment}.yaml"
            )

            if not os.path.exists(typology_file):
                typology_file = os.path.join(
                    self.config_dir, "typology_profiles_default.yaml"
                )

            if os.path.exists(typology_file):
                return self._load_yaml_file(typology_file)
            else:
                return self._get_default_typology_profiles()

        except Exception as e:
            logger.error(f"Error loading typology profiles: {e}")
            return self._get_default_typology_profiles()

    def save_config(self, config: DQConfig, environment: str = "default") -> bool:
        """
        Save DQConfig to YAML file

        Args:
            config: DQConfig object to save
            environment: Environment name

        Returns:
            True if saved successfully
        """
        try:
            config_file = self._get_config_file(environment, create=True)
            config_data = self._dq_config_to_dict(config)

            with open(config_file, "w") as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)

            logger.info(f"Config saved to {config_file}")
            return True

        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False

    def validate_config(self, config: DQConfig) -> Dict[str, Any]:
        """
        Validate configuration for completeness and consistency

        Args:
            config: DQConfig object to validate

        Returns:
            Validation results
        """
        validation_results = {"valid": True, "errors": [], "warnings": []}

        # Validate strategy
        if config.dq_strategy not in ["fallback", "role_aware"]:
            validation_results["errors"].append(
                f"Invalid strategy: {config.dq_strategy}"
            )
            validation_results["valid"] = False

        # Validate dimensions
        total_dimensions = sum(len(dims) for dims in config.dimensions.values())
        if total_dimensions != 7:
            validation_results["errors"].append(
                f"Expected 7 dimensions, found {total_dimensions}"
            )
            validation_results["valid"] = False

        # Validate dimension tiers
        expected_foundational = {"completeness", "conformity", "timeliness", "coverage"}
        expected_enhanced = {"accuracy", "uniqueness", "consistency"}

        actual_foundational = set(config.dimensions.get("foundational", []))
        actual_enhanced = set(config.dimensions.get("enhanced", []))

        if actual_foundational != expected_foundational:
            validation_results["errors"].append(
                f"Foundational dimensions mismatch: expected {expected_foundational}, got {actual_foundational}"
            )
            validation_results["valid"] = False

        if actual_enhanced != expected_enhanced:
            validation_results["errors"].append(
                f"Enhanced dimensions mismatch: expected {expected_enhanced}, got {actual_enhanced}"
            )
            validation_results["valid"] = False

        # Validate KDE risk tiers
        if not config.kde_risk_tiers:
            validation_results["errors"].append("No KDE risk tiers defined")
            validation_results["valid"] = False

        # Validate critical KDEs
        for critical_kde in config.critical_kdes:
            if critical_kde not in config.kde_risk_tiers:
                validation_results["warnings"].append(
                    f"Critical KDE '{critical_kde}' not found in risk tiers"
                )

        # Validate risk weights
        expected_risk_tiers = {"high", "medium", "low"}
        actual_risk_tiers = set(config.risk_weights.keys())

        if actual_risk_tiers != expected_risk_tiers:
            validation_results["errors"].append(
                f"Risk weights mismatch: expected {expected_risk_tiers}, got {actual_risk_tiers}"
            )
            validation_results["valid"] = False

        # Validate synthetic KDEs
        for synthetic_kde, config_dict in config.synthetic_kdes.items():
            if "dimension" not in config_dict:
                validation_results["errors"].append(
                    f"Synthetic KDE '{synthetic_kde}' missing dimension"
                )
                validation_results["valid"] = False

            if "tier" not in config_dict:
                validation_results["errors"].append(
                    f"Synthetic KDE '{synthetic_kde}' missing tier"
                )
                validation_results["valid"] = False

        return validation_results

    def create_default_config_files(self):
        """Create default configuration files"""
        try:
            # Create main config file
            default_config = DQConfig()
            self.save_config(default_config, "default")

            # Create KDE mappings file
            kde_mappings = self._get_default_kde_mappings()
            kde_file = os.path.join(self.config_dir, "kde_mappings_default.yaml")
            with open(kde_file, "w") as f:
                yaml.dump(kde_mappings, f, default_flow_style=False, indent=2)

            # Create typology profiles file
            typology_profiles = self._get_default_typology_profiles()
            typology_file = os.path.join(
                self.config_dir, "typology_profiles_default.yaml"
            )
            with open(typology_file, "w") as f:
                yaml.dump(typology_profiles, f, default_flow_style=False, indent=2)

            logger.info("Default configuration files created")

        except Exception as e:
            logger.error(f"Error creating default config files: {e}")

    def _get_config_file(self, environment: str, create: bool = False) -> str:
        """Get configuration file path for environment"""
        config_file = os.path.join(self.config_dir, f"dqsi_{environment}.yaml")

        if create and not os.path.exists(os.path.dirname(config_file)):
            os.makedirs(os.path.dirname(config_file), exist_ok=True)

        return config_file

    def _load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """Load YAML file and return parsed data"""
        try:
            with open(file_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading YAML file {file_path}: {e}")
            return {}

    def _create_dq_config(self, config_data: Dict[str, Any]) -> DQConfig:
        """Create DQConfig object from loaded data"""
        return DQConfig(
            dq_strategy=config_data.get("dq_strategy", "fallback"),
            dimensions=config_data.get("dimensions", {}),
            dimension_tier_weights=config_data.get("dimension_tier_weights", {}),
            kde_risk_tiers=config_data.get("kde_risk_tiers", {}),
            risk_weights=config_data.get("risk_weights", {}),
            critical_kdes=config_data.get("critical_kdes", []),
            dqsi_critical_cap=config_data.get("dqsi_critical_cap", 0.75),
            synthetic_kdes=config_data.get("synthetic_kdes", {}),
            confidence_params=config_data.get("confidence_params", {}),
        )

    def _dq_config_to_dict(self, config: DQConfig) -> Dict[str, Any]:
        """Convert DQConfig object to dictionary for saving"""
        return {
            "dq_strategy": config.dq_strategy,
            "dimensions": config.dimensions,
            "dimension_tier_weights": config.dimension_tier_weights,
            "kde_risk_tiers": config.kde_risk_tiers,
            "risk_weights": config.risk_weights,
            "critical_kdes": config.critical_kdes,
            "dqsi_critical_cap": config.dqsi_critical_cap,
            "synthetic_kdes": config.synthetic_kdes,
            "confidence_params": config.confidence_params,
        }

    def _get_default_kde_mappings(self) -> Dict[str, str]:
        """Get default KDE to dimension mappings"""
        return {
            "trader_id": "completeness",
            "trade_time": "timeliness",
            "order_timestamp": "timeliness",
            "timestamp": "timeliness",
            "notional": "completeness",
            "quantity": "completeness",
            "price": "completeness",
            "desk_id": "completeness",
            "instrument": "completeness",
            "client_id": "completeness",
            "order_id": "completeness",
            "trade_id": "completeness",
            "venue": "completeness",
            "currency": "completeness",
            "side": "completeness",
            "execution_time": "timeliness",
            "settlement_date": "timeliness",
            "counterparty": "completeness",
            "portfolio": "completeness",
            "book": "completeness",
        }

    def _get_default_typology_profiles(self) -> Dict[str, Any]:
        """Get default typology profiles"""
        return {
            "market_manipulation": {
                "critical_kdes": ["trader_id", "order_timestamp", "price", "quantity"],
                "enhanced_dimensions": ["accuracy", "uniqueness", "consistency"],
                "risk_multiplier": 1.2,
            },
            "insider_trading": {
                "critical_kdes": ["trader_id", "trade_time", "instrument", "notional"],
                "enhanced_dimensions": ["accuracy", "consistency"],
                "risk_multiplier": 1.1,
            },
            "spoofing": {
                "critical_kdes": ["trader_id", "order_timestamp", "quantity", "price"],
                "enhanced_dimensions": ["accuracy", "uniqueness"],
                "risk_multiplier": 1.3,
            },
            "layering": {
                "critical_kdes": ["trader_id", "order_timestamp", "quantity"],
                "enhanced_dimensions": ["uniqueness", "consistency"],
                "risk_multiplier": 1.1,
            },
            "wash_trading": {
                "critical_kdes": [
                    "trader_id",
                    "trade_time",
                    "counterparty",
                    "notional",
                ],
                "enhanced_dimensions": ["accuracy", "uniqueness", "consistency"],
                "risk_multiplier": 1.4,
            },
            "default": {
                "critical_kdes": ["trader_id", "order_timestamp"],
                "enhanced_dimensions": ["accuracy"],
                "risk_multiplier": 1.0,
            },
        }
