"""
Configuration for the circular trading detection model.

This module contains configuration settings, thresholds, and parameters
for the circular trading detection model.
"""

from typing import Dict, Any, Optional


class CircularTradingConfig:
    """
    Configuration class for circular trading detection model.
    
    This class manages all configuration parameters including risk thresholds,
    model parameters, and other settings for the circular trading model.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration.
        
        Args:
            config: Optional configuration dictionary to override defaults
        """
        self.default_config = {
            'risk_thresholds': {
                'low_risk': 0.30,
                'medium_risk': 0.60,
                'high_risk': 0.80
            },
            'model_parameters': {
                'use_latent_intent': True,
                'counterparty_relationship_weight': 0.20,
                'risk_transfer_sensitivity': 0.8,
                'price_coordination_threshold': 0.7,
                'settlement_timing_correlation': 0.6,
                'ownership_overlap_threshold': 0.5,
                'sequence_pattern_detection': 0.75
            },
            'evidence_weights': {
                'counterparty_relationship': 0.20,
                'risk_transfer_analysis': 0.25,
                'price_negotiation_pattern': 0.15,
                'settlement_coordination': 0.15,
                'beneficial_ownership': 0.15,
                'trade_sequence_analysis': 0.10
            },
            'inference_parameters': {
                'method': 'variable_elimination',
                'max_iterations': 100,
                'convergence_threshold': 1e-6
            },
            'fallback_parameters': {
                'use_fallback_priors': True,
                'fallback_penalty': 0.15,
                'minimum_evidence_threshold': 0.25
            }
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
        return self.default_config['risk_thresholds']
    
    def get_model_parameters(self) -> Dict[str, Any]:
        """
        Get model parameter settings.
        
        Returns:
            Dictionary of model parameters
        """
        return self.default_config['model_parameters']
    
    def get_evidence_weights(self) -> Dict[str, float]:
        """
        Get evidence weight settings.
        
        Returns:
            Dictionary of evidence weights
        """
        return self.default_config['evidence_weights']
    
    def get_inference_parameters(self) -> Dict[str, Any]:
        """
        Get inference parameter settings.
        
        Returns:
            Dictionary of inference parameters
        """
        return self.default_config['inference_parameters']
    
    def get_fallback_parameters(self) -> Dict[str, Any]:
        """
        Get fallback parameter settings.
        
        Returns:
            Dictionary of fallback parameters
        """
        return self.default_config['fallback_parameters']
    
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
        if risk_level in self.default_config['risk_thresholds']:
            self.default_config['risk_thresholds'][risk_level] = threshold
        else:
            raise ValueError(f"Unknown risk level: {risk_level}")
    
    def set_model_parameter(self, parameter: str, value: Any):
        """
        Set a specific model parameter.
        
        Args:
            parameter: Parameter name
            value: Parameter value
        """
        self.default_config['model_parameters'][parameter] = value
    
    def get_counterparty_relationship_weight(self) -> float:
        """
        Get counterparty relationship weight parameter.
        
        Returns:
            Counterparty relationship weight value
        """
        return self.default_config['model_parameters']['counterparty_relationship_weight']
    
    def get_risk_transfer_sensitivity(self) -> float:
        """
        Get risk transfer sensitivity parameter.
        
        Returns:
            Risk transfer sensitivity value
        """
        return self.default_config['model_parameters']['risk_transfer_sensitivity']
    
    def get_price_coordination_threshold(self) -> float:
        """
        Get price coordination threshold parameter.
        
        Returns:
            Price coordination threshold value
        """
        return self.default_config['model_parameters']['price_coordination_threshold']
    
    def get_settlement_timing_correlation(self) -> float:
        """
        Get settlement timing correlation parameter.
        
        Returns:
            Settlement timing correlation value
        """
        return self.default_config['model_parameters']['settlement_timing_correlation']
    
    def get_ownership_overlap_threshold(self) -> float:
        """
        Get ownership overlap threshold parameter.
        
        Returns:
            Ownership overlap threshold value
        """
        return self.default_config['model_parameters']['ownership_overlap_threshold']
    
    def get_sequence_pattern_detection(self) -> float:
        """
        Get sequence pattern detection parameter.
        
        Returns:
            Sequence pattern detection value
        """
        return self.default_config['model_parameters']['sequence_pattern_detection']
    
    def is_latent_intent_enabled(self) -> bool:
        """
        Check if latent intent modeling is enabled.
        
        Returns:
            True if latent intent is enabled, False otherwise
        """
        return self.default_config['model_parameters']['use_latent_intent']
    
    def validate_config(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Check required sections
        required_sections = ['risk_thresholds', 'model_parameters', 'evidence_weights', 
                           'inference_parameters', 'fallback_parameters']
        
        for section in required_sections:
            if section not in self.default_config:
                return False
        
        # Check risk thresholds
        thresholds = self.default_config['risk_thresholds']
        if not (0 <= thresholds['low_risk'] <= thresholds['medium_risk'] <= thresholds['high_risk'] <= 1):
            return False
        
        # Check evidence weights sum to 1
        weights = self.default_config['evidence_weights']
        if abs(sum(weights.values()) - 1.0) > 1e-6:
            return False
        
        return True