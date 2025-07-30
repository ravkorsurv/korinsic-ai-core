"""
Test suite for Economic Withholding Detection model configuration.

This module tests the configuration management for the economic withholding
detection model including validation, parameter access, and ARERA compliance settings.
"""

import pytest
import sys
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, 'src')

from models.bayesian.economic_withholding.config import EconomicWithholdingConfig


class TestEconomicWithholdingConfig:
    """Test the EconomicWithholdingConfig class."""
    
    def test_default_initialization(self):
        """Test initialization with default configuration."""
        config = EconomicWithholdingConfig()
        
        # Test that all required sections exist
        assert 'risk_thresholds' in config.config
        assert 'arera_compliance' in config.config
        assert 'model_parameters' in config.config
        assert 'plant_types' in config.config
        assert 'evidence_weights' in config.config
        assert 'simulation_parameters' in config.config
        assert 'validation_rules' in config.config
        assert 'output_settings' in config.config
        assert 'regulatory_frameworks' in config.config
        assert 'alert_settings' in config.config
    
    def test_custom_initialization(self):
        """Test initialization with custom configuration."""
        custom_config = {
            'risk_thresholds': {
                'low_risk': 0.2,
                'medium_risk': 0.5,
                'high_risk': 0.7
            },
            'arera_compliance': {
                'confidence_threshold': 0.95,
                'markup_threshold': 0.20
            }
        }
        
        config = EconomicWithholdingConfig(custom_config)
        
        # Test that custom values are used
        assert config.get('risk_thresholds.low_risk') == 0.2
        assert config.get('risk_thresholds.medium_risk') == 0.5
        assert config.get('risk_thresholds.high_risk') == 0.7
        assert config.get('arera_compliance.confidence_threshold') == 0.95
        assert config.get('arera_compliance.markup_threshold') == 0.20
        
        # Test that other defaults are preserved
        assert config.get('model_parameters.use_latent_intent') == False
        assert config.get('model_parameters.esi_enabled') == True
    
    def test_config_merging(self):
        """Test that configuration merging works correctly."""
        custom_config = {
            'arera_compliance': {
                'confidence_threshold': 0.95  # Override this
                # markup_threshold should remain default
            },
            'new_section': {
                'new_param': 'test_value'
            }
        }
        
        config = EconomicWithholdingConfig(custom_config)
        
        # Test override
        assert config.get('arera_compliance.confidence_threshold') == 0.95
        # Test default preserved
        assert config.get('arera_compliance.markup_threshold') == 0.15
        # Test new section added
        assert config.get('new_section.new_param') == 'test_value'
    
    def test_get_method(self):
        """Test the get method with dot notation."""
        config = EconomicWithholdingConfig()
        
        # Test simple get
        assert config.get('model_parameters') is not None
        
        # Test dot notation
        assert config.get('risk_thresholds.low_risk') == 0.3
        assert config.get('arera_compliance.confidence_threshold') == 0.90
        assert config.get('plant_types.gas.default_heat_rate') == 7500
        
        # Test with default value
        assert config.get('nonexistent.key', 'default') == 'default'
        assert config.get('nonexistent.key') is None
    
    def test_set_method(self):
        """Test the set method with dot notation."""
        config = EconomicWithholdingConfig()
        
        # Test simple set
        config.set('test_param', 'test_value')
        assert config.get('test_param') == 'test_value'
        
        # Test dot notation set
        config.set('new_section.new_param', 42)
        assert config.get('new_section.new_param') == 42
        
        # Test overriding existing value
        config.set('risk_thresholds.low_risk', 0.25)
        assert config.get('risk_thresholds.low_risk') == 0.25
    
    def test_get_risk_thresholds(self):
        """Test getting risk thresholds."""
        config = EconomicWithholdingConfig()
        thresholds = config.get_risk_thresholds()
        
        assert isinstance(thresholds, dict)
        assert 'low_risk' in thresholds
        assert 'medium_risk' in thresholds
        assert 'high_risk' in thresholds
        assert thresholds['low_risk'] == 0.3
        assert thresholds['medium_risk'] == 0.6
        assert thresholds['high_risk'] == 0.8
    
    def test_get_arera_config(self):
        """Test getting ARERA compliance configuration."""
        config = EconomicWithholdingConfig()
        arera_config = config.get_arera_config()
        
        assert isinstance(arera_config, dict)
        assert 'confidence_threshold' in arera_config
        assert 'markup_threshold' in arera_config
        assert 'statistical_method' in arera_config
        assert arera_config['confidence_threshold'] == 0.90
        assert arera_config['markup_threshold'] == 0.15
        assert arera_config['statistical_method'] == 'bayesian'
    
    def test_get_plant_config(self):
        """Test getting plant configuration for specific fuel types."""
        config = EconomicWithholdingConfig()
        
        # Test gas plant config
        gas_config = config.get_plant_config('gas')
        assert isinstance(gas_config, dict)
        assert 'default_heat_rate' in gas_config
        assert 'efficiency_range' in gas_config
        assert gas_config['default_heat_rate'] == 7500
        assert gas_config['efficiency_range'] == [0.35, 0.60]
        
        # Test coal plant config
        coal_config = config.get_plant_config('coal')
        assert isinstance(coal_config, dict)
        assert coal_config['default_heat_rate'] == 9500
        assert coal_config['efficiency_range'] == [0.30, 0.45]
        
        # Test nonexistent fuel type
        unknown_config = config.get_plant_config('unknown')
        assert unknown_config == {}
    
    def test_get_evidence_weights(self):
        """Test getting evidence node weights."""
        config = EconomicWithholdingConfig()
        weights = config.get_evidence_weights()
        
        assert isinstance(weights, dict)
        assert 'marginal_cost_deviation' in weights
        assert 'fuel_cost_variance' in weights
        assert 'plant_efficiency' in weights
        assert weights['marginal_cost_deviation'] == 1.0  # Highest weight
        assert weights['fuel_cost_variance'] == 0.9
        assert weights['plant_efficiency'] == 0.8
    
    def test_get_simulation_config(self):
        """Test getting simulation parameters."""
        config = EconomicWithholdingConfig()
        sim_config = config.get_simulation_config()
        
        assert isinstance(sim_config, dict)
        assert 'benchmark_scenarios' in sim_config
        assert 'cost_curve_methods' in sim_config
        assert 'statistical_tests' in sim_config
        assert sim_config['benchmark_scenarios'] == ["min_cost", "median_cost", "max_cost"]
        assert 'linear' in sim_config['cost_curve_methods']
        assert 'quadratic' in sim_config['cost_curve_methods']
    
    def test_get_validation_rules(self):
        """Test getting validation rules."""
        config = EconomicWithholdingConfig()
        rules = config.get_validation_rules()
        
        assert isinstance(rules, dict)
        assert 'min_evidence_nodes' in rules
        assert 'max_fallback_ratio' in rules
        assert 'required_plant_data' in rules
        assert 'required_offer_data' in rules
        assert rules['min_evidence_nodes'] == 3
        assert 'unit_id' in rules['required_plant_data']
        assert 'price_eur_mwh' in rules['required_offer_data']
    
    def test_get_output_settings(self):
        """Test getting output configuration."""
        config = EconomicWithholdingConfig()
        output = config.get_output_settings()
        
        assert isinstance(output, dict)
        assert 'include_esi' in output
        assert 'include_regulatory_rationale' in output
        assert 'include_cost_curve_analysis' in output
        assert 'arera_compliance_report' in output
        assert output['include_esi'] == True
        assert output['arera_compliance_report'] == True
    
    def test_get_regulatory_framework(self):
        """Test getting regulatory framework configuration."""
        config = EconomicWithholdingConfig()
        
        # Test ARERA framework
        arera = config.get_regulatory_framework('arera')
        assert isinstance(arera, dict)
        assert 'methodology' in arera
        assert 'statistical_significance' in arera
        assert arera['methodology'] == 'counterfactual_simulation'
        assert arera['statistical_significance'] == 0.05
        
        # Test FERC framework
        ferc = config.get_regulatory_framework('ferc')
        assert isinstance(ferc, dict)
        assert 'methodology' in ferc
        assert ferc['methodology'] == 'market_power_analysis'
        
        # Test nonexistent framework
        unknown = config.get_regulatory_framework('unknown')
        assert unknown == {}
    
    def test_get_alert_settings(self):
        """Test getting alert configuration."""
        config = EconomicWithholdingConfig()
        alerts = config.get_alert_settings()
        
        assert isinstance(alerts, dict)
        assert 'enable_real_time_alerts' in alerts
        assert 'alert_thresholds' in alerts
        assert 'notification_channels' in alerts
        assert alerts['enable_real_time_alerts'] == True
        assert 'high_markup_threshold' in alerts['alert_thresholds']
    
    def test_boolean_getters(self):
        """Test boolean getter methods."""
        config = EconomicWithholdingConfig()
        
        assert config.is_latent_intent_enabled() == False
        assert config.is_scenario_simulation_enabled() == True
        assert config.is_esi_enabled() == True
        
        # Test with custom config
        custom_config = {
            'model_parameters': {
                'use_latent_intent': True,
                'scenario_simulation_enabled': False
            }
        }
        config = EconomicWithholdingConfig(custom_config)
        assert config.is_latent_intent_enabled() == True
        assert config.is_scenario_simulation_enabled() == False
    
    def test_numeric_getters(self):
        """Test numeric getter methods."""
        config = EconomicWithholdingConfig()
        
        assert config.get_inference_method() == 'variable_elimination'
        assert config.get_confidence_threshold() == 0.90
        assert config.get_markup_threshold() == 0.15
        assert config.get_monte_carlo_iterations() == 1000
    
    def test_validate_config_valid(self):
        """Test configuration validation with valid config."""
        config = EconomicWithholdingConfig()
        errors = config.validate_config()
        
        assert isinstance(errors, list)
        assert len(errors) == 0  # Should be no errors for default config
    
    def test_validate_config_missing_sections(self):
        """Test configuration validation with missing sections."""
        # Create config with missing sections
        incomplete_config = {
            'risk_thresholds': {
                'low_risk': 0.3
            }
            # Missing other required sections
        }
        
        config = EconomicWithholdingConfig()
        config.config = incomplete_config  # Override with incomplete config
        errors = config.validate_config()
        
        assert isinstance(errors, list)
        assert len(errors) > 0
        # Should have errors for missing sections
        error_text = ' '.join(errors)
        assert 'Missing required configuration section' in error_text
    
    def test_validate_config_invalid_thresholds(self):
        """Test configuration validation with invalid threshold values."""
        invalid_config = {
            'risk_thresholds': {
                'low_risk': 1.5,  # Invalid: > 1.0
                'medium_risk': -0.1,  # Invalid: < 0.0
                'high_risk': 0.8
            },
            'arera_compliance': {
                'confidence_threshold': 1.5,  # Invalid: > 1.0
                'markup_threshold': -0.1  # Invalid: < 0.0
            }
        }
        
        config = EconomicWithholdingConfig(invalid_config)
        errors = config.validate_config()
        
        assert isinstance(errors, list)
        assert len(errors) > 0
        error_text = ' '.join(errors)
        assert 'must be between 0 and 1' in error_text or 'must be non-negative' in error_text
    
    def test_validate_config_invalid_efficiency_ranges(self):
        """Test configuration validation with invalid efficiency ranges."""
        invalid_config = {
            'plant_types': {
                'gas': {
                    'efficiency_range': [0.6, 0.4]  # Invalid: min > max
                },
                'coal': {
                    'efficiency_range': [0.3]  # Invalid: not 2 elements
                }
            }
        }
        
        config = EconomicWithholdingConfig(invalid_config)
        errors = config.validate_config()
        
        assert isinstance(errors, list)
        assert len(errors) > 0
        error_text = ' '.join(errors)
        assert 'Invalid efficiency_range' in error_text
    
    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = EconomicWithholdingConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'risk_thresholds' in config_dict
        assert 'arera_compliance' in config_dict
        assert 'model_parameters' in config_dict
        
        # Test that it's a copy, not the original
        config_dict['test_key'] = 'test_value'
        assert 'test_key' not in config.config
    
    def test_string_representation(self):
        """Test string representation methods."""
        config = EconomicWithholdingConfig()
        
        str_repr = str(config)
        assert 'EconomicWithholdingConfig' in str_repr
        assert 'sections=' in str_repr
        
        repr_str = repr(config)
        assert 'EconomicWithholdingConfig' in repr_str
    
    def test_plant_type_configurations(self):
        """Test that all plant type configurations are valid."""
        config = EconomicWithholdingConfig()
        plant_types = config.get('plant_types', {})
        
        expected_types = ['gas', 'coal', 'oil', 'nuclear']
        for plant_type in expected_types:
            assert plant_type in plant_types
            plant_config = plant_types[plant_type]
            
            # Check required fields
            assert 'default_heat_rate' in plant_config
            assert 'efficiency_range' in plant_config
            assert 'typical_variable_costs' in plant_config
            
            # Check efficiency range validity
            eff_range = plant_config['efficiency_range']
            assert len(eff_range) == 2
            assert eff_range[0] < eff_range[1]
            assert 0 < eff_range[0] < 1
            assert 0 < eff_range[1] < 1
            
            # Check variable costs structure
            var_costs = plant_config['typical_variable_costs']
            assert 'fuel_cost_ratio' in var_costs
            assert 'vom_cost' in var_costs
            assert 'emission_cost' in var_costs
    
    def test_evidence_weights_completeness(self):
        """Test that evidence weights cover all expected nodes."""
        config = EconomicWithholdingConfig()
        weights = config.get_evidence_weights()
        
        # Core cost analysis nodes (should have highest weights)
        core_nodes = ['marginal_cost_deviation', 'fuel_cost_variance', 'plant_efficiency']
        for node in core_nodes:
            assert node in weights
            assert weights[node] >= 0.8  # High weights for core indicators
        
        # Market context nodes
        market_nodes = ['market_tightness', 'load_factor', 'competitive_context']
        for node in market_nodes:
            assert node in weights
            assert 0.5 <= weights[node] <= 1.0
        
        # Behavioral indicators
        behavior_nodes = ['bid_shape_anomaly', 'offer_withdrawal_pattern', 'capacity_utilization']
        for node in behavior_nodes:
            assert node in weights
            assert 0.5 <= weights[node] <= 1.0
        
        # Reused nodes
        reused_nodes = ['price_impact_ratio', 'volume_participation', 'profit_motivation']
        for node in reused_nodes:
            assert node in weights
            assert 0.5 <= weights[node] <= 1.0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])