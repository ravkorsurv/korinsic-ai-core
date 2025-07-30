"""
Economic withholding model configuration.

This module contains configuration management for the economic withholding
detection model, including ARERA compliance parameters, thresholds, and model settings.
"""

from typing import Any, Dict, List, Optional


class EconomicWithholdingConfig:
    """
    Configuration manager for economic withholding model.

    This class manages all configuration parameters specific to the
    economic withholding detection model for power markets.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration.

        Args:
            config: Optional configuration dictionary
        """
        # Default configuration
        self.default_config = {
            "risk_thresholds": {
                "low_risk": 0.3,
                "medium_risk": 0.6, 
                "high_risk": 0.8
            },
            "arera_compliance": {
                "confidence_threshold": 0.90,
                "markup_threshold": 0.15,  # 15% markup over marginal cost
                "statistical_method": "bayesian",
                "counterfactual_scenarios": 3,
                "monte_carlo_iterations": 1000
            },
            "model_parameters": {
                "use_latent_intent": False,
                "inference_method": "variable_elimination",
                "fallback_enabled": True,
                "esi_enabled": True,
                "scenario_simulation_enabled": True
            },
            "plant_types": {
                "gas": {
                    "default_heat_rate": 7500,  # BTU/kWh
                    "efficiency_range": [0.35, 0.60],
                    "typical_variable_costs": {
                        "fuel_cost_ratio": 0.85,
                        "vom_cost": 3.5,  # $/MWh
                        "emission_cost": 1.2  # $/MWh
                    }
                },
                "coal": {
                    "default_heat_rate": 9500,  # BTU/kWh
                    "efficiency_range": [0.30, 0.45],
                    "typical_variable_costs": {
                        "fuel_cost_ratio": 0.80,
                        "vom_cost": 4.2,  # $/MWh
                        "emission_cost": 2.8  # $/MWh
                    }
                },
                "oil": {
                    "default_heat_rate": 8200,  # BTU/kWh
                    "efficiency_range": [0.32, 0.50],
                    "typical_variable_costs": {
                        "fuel_cost_ratio": 0.88,
                        "vom_cost": 5.1,  # $/MWh
                        "emission_cost": 2.2  # $/MWh
                    }
                },
                "nuclear": {
                    "default_heat_rate": 10500,  # BTU/kWh
                    "efficiency_range": [0.33, 0.35],
                    "typical_variable_costs": {
                        "fuel_cost_ratio": 0.25,
                        "vom_cost": 2.1,  # $/MWh
                        "emission_cost": 0.0  # $/MWh
                    }
                }
            },
            "evidence_weights": {
                # Core cost analysis (highest weights)
                "marginal_cost_deviation": 1.0,
                "fuel_cost_variance": 0.9,
                "plant_efficiency": 0.8,
                
                # Market context
                "market_tightness": 0.9,
                "load_factor": 0.8,
                "competitive_context": 0.7,
                "transmission_constraint": 0.6,
                
                # Behavioral indicators
                "bid_shape_anomaly": 0.8,
                "offer_withdrawal_pattern": 0.9,
                "capacity_utilization": 0.8,
                "markup_consistency": 0.7,
                "opportunity_pricing": 0.8,
                
                # Technical analysis
                "heat_rate_variance": 0.7,
                "fuel_price_correlation": 0.6,
                "cross_plant_coordination": 0.5,
                
                # Reused nodes (from existing library)
                "price_impact_ratio": 0.8,
                "volume_participation": 0.7,
                "liquidity_context": 0.6,
                "order_clustering": 0.5,
                "benchmark_timing": 0.7,
                "profit_motivation": 0.6
            },
            "simulation_parameters": {
                "benchmark_scenarios": ["min_cost", "median_cost", "max_cost"],
                "cost_curve_methods": ["linear", "quadratic", "step_function"],
                "statistical_tests": ["t_test", "mann_whitney", "kolmogorov_smirnov"],
                "confidence_intervals": [0.90, 0.95, 0.99],
                "sensitivity_analysis_enabled": True
            },
            "validation_rules": {
                "min_evidence_nodes": 3,
                "max_fallback_ratio": 0.6,
                "min_confidence_threshold": 0.5,
                "required_plant_data": [
                    "unit_id", "fuel_type", "capacity_mw", "heat_rate"
                ],
                "required_offer_data": [
                    "price_eur_mwh", "quantity_mw", "timestamp"
                ]
            },
            "output_settings": {
                "include_esi": True,
                "include_regulatory_rationale": True,
                "include_cost_curve_analysis": True,
                "include_counterfactual_results": True,
                "include_confidence_intervals": True,
                "arera_compliance_report": True
            },
            "regulatory_frameworks": {
                "arera": {
                    "methodology": "counterfactual_simulation",
                    "statistical_significance": 0.05,
                    "economic_significance": 0.10,  # 10% price impact
                    "documentation_required": True
                },
                "ferc": {
                    "methodology": "market_power_analysis", 
                    "pivotal_supplier_test": True,
                    "residual_supply_index": True
                },
                "ofgem": {
                    "methodology": "conduct_impact_analysis",
                    "market_concentration_test": True,
                    "price_cost_markup_analysis": True
                }
            },
            "alert_settings": {
                "enable_real_time_alerts": True,
                "alert_thresholds": {
                    "high_markup_threshold": 0.20,  # 20% over marginal cost
                    "systematic_pattern_threshold": 0.15,
                    "market_impact_threshold": 0.10  # 10% price impact
                },
                "notification_channels": ["email", "dashboard", "api"],
                "escalation_rules": {
                    "high_risk_escalation": True,
                    "repeated_violations_escalation": True,
                    "market_wide_impact_escalation": True
                }
            }
        }

        # Merge with provided config
        self.config = self._merge_config(self.default_config, config or {})

    def _merge_config(self, default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge configuration dictionaries.

        Args:
            default: Default configuration
            override: Override configuration

        Returns:
            Merged configuration
        """
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
                
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value

    def get_risk_thresholds(self) -> Dict[str, float]:
        """Get risk threshold configuration."""
        return self.get('risk_thresholds', {})

    def get_arera_config(self) -> Dict[str, Any]:
        """Get ARERA compliance configuration."""
        return self.get('arera_compliance', {})

    def get_plant_config(self, fuel_type: str) -> Dict[str, Any]:
        """
        Get plant configuration for specific fuel type.

        Args:
            fuel_type: Fuel type (gas, coal, oil, nuclear)

        Returns:
            Plant configuration dictionary
        """
        return self.get(f'plant_types.{fuel_type}', {})

    def get_evidence_weights(self) -> Dict[str, float]:
        """Get evidence node weights."""
        return self.get('evidence_weights', {})

    def get_simulation_config(self) -> Dict[str, Any]:
        """Get simulation parameters."""
        return self.get('simulation_parameters', {})

    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules."""
        return self.get('validation_rules', {})

    def get_output_settings(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self.get('output_settings', {})

    def get_regulatory_framework(self, framework: str) -> Dict[str, Any]:
        """
        Get regulatory framework configuration.

        Args:
            framework: Framework name (arera, ferc, ofgem)

        Returns:
            Framework configuration
        """
        return self.get(f'regulatory_frameworks.{framework}', {})

    def get_alert_settings(self) -> Dict[str, Any]:
        """Get alert configuration."""
        return self.get('alert_settings', {})

    def is_latent_intent_enabled(self) -> bool:
        """Check if latent intent modeling is enabled."""
        return self.get('model_parameters.use_latent_intent', False)

    def is_scenario_simulation_enabled(self) -> bool:
        """Check if scenario simulation is enabled."""
        return self.get('model_parameters.scenario_simulation_enabled', True)

    def is_esi_enabled(self) -> bool:
        """Check if Evidence Sufficiency Index is enabled."""
        return self.get('model_parameters.esi_enabled', True)

    def get_inference_method(self) -> str:
        """Get the inference method."""
        return self.get('model_parameters.inference_method', 'variable_elimination')

    def get_confidence_threshold(self) -> float:
        """Get ARERA confidence threshold."""
        return self.get('arera_compliance.confidence_threshold', 0.90)

    def get_markup_threshold(self) -> float:
        """Get markup threshold for withholding detection."""
        return self.get('arera_compliance.markup_threshold', 0.15)

    def get_monte_carlo_iterations(self) -> int:
        """Get number of Monte Carlo iterations."""
        return self.get('arera_compliance.monte_carlo_iterations', 1000)

    def validate_config(self) -> List[str]:
        """
        Validate the configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required sections
        required_sections = [
            'risk_thresholds', 'arera_compliance', 'model_parameters',
            'plant_types', 'evidence_weights', 'validation_rules'
        ]
        
        for section in required_sections:
            if section not in self.config:
                errors.append(f"Missing required configuration section: {section}")

        # Validate risk thresholds
        thresholds = self.get_risk_thresholds()
        if thresholds:
            required_thresholds = ['low_risk', 'medium_risk', 'high_risk']
            for threshold in required_thresholds:
                if threshold not in thresholds:
                    errors.append(f"Missing risk threshold: {threshold}")
                elif not 0 <= thresholds[threshold] <= 1:
                    errors.append(f"Risk threshold {threshold} must be between 0 and 1")

        # Validate ARERA config
        arera_config = self.get_arera_config()
        if arera_config:
            if 'confidence_threshold' in arera_config:
                if not 0 <= arera_config['confidence_threshold'] <= 1:
                    errors.append("ARERA confidence_threshold must be between 0 and 1")
            
            if 'markup_threshold' in arera_config:
                if arera_config['markup_threshold'] < 0:
                    errors.append("ARERA markup_threshold must be non-negative")

        # Validate plant types
        plant_types = self.get('plant_types', {})
        for fuel_type, config in plant_types.items():
            if 'efficiency_range' in config:
                eff_range = config['efficiency_range']
                if len(eff_range) != 2 or eff_range[0] >= eff_range[1]:
                    errors.append(f"Invalid efficiency_range for {fuel_type}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration as dictionary
        """
        return self.config.copy()

    def __str__(self) -> str:
        """String representation of the configuration."""
        return f"EconomicWithholdingConfig(sections={list(self.config.keys())})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"EconomicWithholdingConfig({self.config})"