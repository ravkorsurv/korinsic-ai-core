"""
Configuration for Market Cornering Detection Model.

This module contains the configuration class for the market cornering model,
including risk thresholds, evidence weights, and model parameters.
"""

from typing import Dict, Any, Optional


class MarketCorneringConfig:
    """
    Configuration class for the market cornering detection model.
    
    This class manages configuration parameters for the market cornering
    detection model including risk thresholds, evidence weights, and
    model-specific parameters.
    """
    
    def __init__(self, custom_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the market cornering configuration.
        
        Args:
            custom_config: Optional custom configuration dictionary
        """
        self.config = self._get_default_config()
        
        # Apply custom configuration if provided
        if custom_config:
            self._apply_custom_config(custom_config)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration for market cornering detection.
        
        Returns:
            Default configuration dictionary
        """
        return {
            # Risk thresholds for market cornering assessment
            'risk_thresholds': {
                'low_risk': 0.25,     # Lower threshold - cornering is serious
                'medium_risk': 0.50,   # Medium threshold
                'high_risk': 0.75      # High threshold
            },
            
            # Evidence weights for different types of evidence
            'evidence_weights': {
                'market_concentration': 0.18,      # Market concentration analysis
                'position_accumulation': 0.18,     # Position accumulation patterns
                'supply_control': 0.25,            # Supply control (highest weight)
                'liquidity_manipulation': 0.16,    # Liquidity manipulation
                'price_distortion': 0.16,          # Price distortion analysis
                'delivery_constraint': 0.07        # Delivery constraints
            },
            
            # Model parameters
            'model_parameters': {
                'use_latent_intent': True,                      # Use latent intent modeling
                'concentration_threshold': 0.4,                # HHI threshold for concentration
                'position_accumulation_threshold': 0.3,        # Position accumulation threshold
                'supply_control_threshold': 0.5,               # Supply control threshold
                'liquidity_manipulation_threshold': 0.3,       # Liquidity manipulation threshold
                'price_distortion_threshold': 0.2,             # Price distortion threshold
                'delivery_constraint_threshold': 0.4,          # Delivery constraint threshold
                'intent_inference_threshold': 0.6,             # Intent inference threshold
                'coordination_strength_threshold': 0.7,        # Coordination strength threshold
                'market_dominance_threshold': 0.6,             # Market dominance threshold
                'cornering_probability_threshold': 0.8         # Cornering probability threshold
            },
            
            # Inference parameters
            'inference_parameters': {
                'algorithm': 'variable_elimination',           # Inference algorithm
                'max_iterations': 100,                        # Maximum iterations
                'convergence_threshold': 1e-6,                # Convergence threshold
                'normalize_evidence': True,                    # Normalize evidence values
                'use_log_probabilities': False                # Use log probabilities
            },
            
            # Fallback parameters
            'fallback_parameters': {
                'use_fallback_logic': True,                   # Enable fallback logic
                'fallback_confidence_penalty': 0.2,          # Confidence penalty for fallback
                'minimum_evidence_threshold': 0.3,           # Minimum evidence threshold
                'fallback_evidence_weight': 0.5              # Weight for fallback evidence
            },
            
            # Market cornering specific parameters
            'cornering_parameters': {
                'market_concentration_weights': {
                    'dispersed': 0.1,
                    'concentrated': 0.5,
                    'highly_concentrated': 0.9
                },
                'position_accumulation_weights': {
                    'normal_accumulation': 0.1,
                    'systematic_accumulation': 0.6,
                    'aggressive_accumulation': 0.95
                },
                'supply_control_weights': {
                    'limited_control': 0.1,
                    'significant_control': 0.7,
                    'dominant_control': 0.95
                },
                'liquidity_manipulation_weights': {
                    'normal_liquidity': 0.1,
                    'constrained_liquidity': 0.6,
                    'manipulated_liquidity': 0.9
                },
                'price_distortion_weights': {
                    'fair_pricing': 0.1,
                    'moderate_distortion': 0.6,
                    'extreme_distortion': 0.95
                },
                'delivery_constraint_weights': {
                    'normal_delivery': 0.1,
                    'constrained_delivery': 0.6,
                    'blocked_delivery': 0.9
                }
            }
        }
    
    def _apply_custom_config(self, custom_config: Dict[str, Any]):
        """
        Apply custom configuration settings.
        
        Args:
            custom_config: Custom configuration dictionary
        """
        for key, value in custom_config.items():
            if key in self.config:
                if isinstance(self.config[key], dict) and isinstance(value, dict):
                    # Recursively update nested dictionaries
                    self.config[key].update(value)
                else:
                    # Replace the value
                    self.config[key] = value
            else:
                # Add new configuration key
                self.config[key] = value
    
    def get_risk_thresholds(self) -> Dict[str, float]:
        """
        Get risk thresholds for market cornering assessment.
        
        Returns:
            Risk thresholds dictionary
        """
        return self.config['risk_thresholds']
    
    def get_evidence_weights(self) -> Dict[str, float]:
        """
        Get evidence weights for different types of evidence.
        
        Returns:
            Evidence weights dictionary
        """
        return self.config['evidence_weights']
    
    def get_model_parameters(self) -> Dict[str, Any]:
        """
        Get model parameters for market cornering detection.
        
        Returns:
            Model parameters dictionary
        """
        return self.config['model_parameters']
    
    def get_inference_parameters(self) -> Dict[str, Any]:
        """
        Get inference parameters for the model.
        
        Returns:
            Inference parameters dictionary
        """
        return self.config['inference_parameters']
    
    def get_fallback_parameters(self) -> Dict[str, Any]:
        """
        Get fallback parameters for the model.
        
        Returns:
            Fallback parameters dictionary
        """
        return self.config['fallback_parameters']
    
    def get_cornering_parameters(self) -> Dict[str, Any]:
        """
        Get market cornering specific parameters.
        
        Returns:
            Cornering parameters dictionary
        """
        return self.config['cornering_parameters']
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
    
    def set_risk_threshold(self, risk_level: str, threshold: float):
        """
        Set a specific risk threshold.
        
        Args:
            risk_level: Risk level (low_risk, medium_risk, high_risk)
            threshold: Threshold value
        """
        if risk_level not in self.config['risk_thresholds']:
            raise ValueError(f"Invalid risk level: {risk_level}")
        
        self.config['risk_thresholds'][risk_level] = threshold
    
    def set_evidence_weight(self, evidence_type: str, weight: float):
        """
        Set weight for a specific evidence type.
        
        Args:
            evidence_type: Evidence type
            weight: Weight value
        """
        if evidence_type not in self.config['evidence_weights']:
            raise ValueError(f"Invalid evidence type: {evidence_type}")
        
        self.config['evidence_weights'][evidence_type] = weight
    
    def set_model_parameter(self, parameter_name: str, value: Any):
        """
        Set a specific model parameter.
        
        Args:
            parameter_name: Parameter name
            value: Parameter value
        """
        self.config['model_parameters'][parameter_name] = value
    
    def validate_config(self) -> bool:
        """
        Validate the configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate risk thresholds
            thresholds = self.config['risk_thresholds']
            if not (0 <= thresholds['low_risk'] <= thresholds['medium_risk'] <= thresholds['high_risk'] <= 1):
                return False
            
            # Validate evidence weights sum to 1
            weights = self.config['evidence_weights']
            if abs(sum(weights.values()) - 1.0) > 1e-6:
                return False
            
            # Validate weight values are between 0 and 1
            for weight in weights.values():
                if not (0 <= weight <= 1):
                    return False
            
            # Validate model parameters
            params = self.config['model_parameters']
            for threshold_param in [
                'concentration_threshold', 'position_accumulation_threshold',
                'supply_control_threshold', 'liquidity_manipulation_threshold',
                'price_distortion_threshold', 'delivery_constraint_threshold',
                'intent_inference_threshold', 'coordination_strength_threshold',
                'market_dominance_threshold', 'cornering_probability_threshold'
            ]:
                if threshold_param in params:
                    if not (0 <= params[threshold_param] <= 1):
                        return False
            
            return True
            
        except Exception:
            return False
    
    def get_state_weight(self, evidence_type: str, state: str) -> float:
        """
        Get weight for a specific evidence state.
        
        Args:
            evidence_type: Evidence type
            state: Evidence state
            
        Returns:
            Weight for the state
        """
        cornering_params = self.config['cornering_parameters']
        
        # Map evidence types to parameter keys
        param_mapping = {
            'market_concentration': 'market_concentration_weights',
            'position_accumulation': 'position_accumulation_weights',
            'supply_control': 'supply_control_weights',
            'liquidity_manipulation': 'liquidity_manipulation_weights',
            'price_distortion': 'price_distortion_weights',
            'delivery_constraint': 'delivery_constraint_weights'
        }
        
        if evidence_type in param_mapping:
            param_key = param_mapping[evidence_type]
            if param_key in cornering_params:
                return cornering_params[param_key].get(state, 0.5)
        
        return 0.5  # Default weight
    
    def get_evidence_threshold(self, evidence_type: str) -> float:
        """
        Get threshold for a specific evidence type.
        
        Args:
            evidence_type: Evidence type
            
        Returns:
            Threshold value
        """
        model_params = self.config['model_parameters']
        
        # Map evidence types to threshold parameters
        threshold_mapping = {
            'market_concentration': 'concentration_threshold',
            'position_accumulation': 'position_accumulation_threshold',
            'supply_control': 'supply_control_threshold',
            'liquidity_manipulation': 'liquidity_manipulation_threshold',
            'price_distortion': 'price_distortion_threshold',
            'delivery_constraint': 'delivery_constraint_threshold'
        }
        
        if evidence_type in threshold_mapping:
            threshold_key = threshold_mapping[evidence_type]
            return model_params.get(threshold_key, 0.5)
        
        return 0.5  # Default threshold
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return f"MarketCorneringConfig(thresholds={self.config['risk_thresholds']}, weights={self.config['evidence_weights']})"
    
    def __repr__(self) -> str:
        """Representation of the configuration."""
        return self.__str__()