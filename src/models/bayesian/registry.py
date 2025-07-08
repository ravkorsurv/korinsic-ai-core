"""
Bayesian Model Registry.

This module provides a registry for managing different types of
Bayesian models used in market abuse detection.
"""

from typing import Dict, Any, Type, Optional, List
import logging

from .insider_dealing import InsiderDealingModel
from .spoofing import SpoofingModel
from .latent_intent import LatentIntentModel
from .commodity_manipulation import CommodityManipulationModel

logger = logging.getLogger(__name__)


class BayesianModelRegistry:
    """
    Registry for managing Bayesian models.
    
    This class provides a centralized way to create, manage, and access
    different types of Bayesian models for market abuse detection.
    """
    
    def __init__(self):
        """Initialize the model registry."""
        self.registered_models = {
            'insider_dealing': InsiderDealingModel,
            'spoofing': SpoofingModel,
            'latent_intent': LatentIntentModel,
            'commodity_manipulation': CommodityManipulationModel
        }
        
        self.model_instances = {}
        self.model_configs = {}
        
        logger.info("Bayesian model registry initialized")
    
    def register_model(self, model_name: str, model_class: Type):
        """
        Register a new model type.
        
        Args:
            model_name: Name of the model
            model_class: Model class
        """
        self.registered_models[model_name] = model_class
        logger.info(f"Registered model: {model_name}")
    
    def create_model(self, model_type: str, config: Dict[str, Any] = None) -> Any:
        """
        Create a model instance.
        
        Args:
            model_type: Type of model to create
            config: Optional model configuration
            
        Returns:
            Model instance
        """
        if model_type not in self.registered_models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model_class = self.registered_models[model_type]
        
        # Create instance based on model type
        if model_type in ['insider_dealing', 'commodity_manipulation']:
            use_latent_intent = config.get('use_latent_intent', True) if config else True
            model_instance = model_class(use_latent_intent=use_latent_intent, config=config)
        else:
            model_instance = model_class(config=config)
        
        # Store in registry
        instance_key = f"{model_type}_{id(model_instance)}"
        self.model_instances[instance_key] = model_instance
        self.model_configs[instance_key] = config or {}
        
        logger.info(f"Created {model_type} model instance: {instance_key}")
        return model_instance
    
    def get_model(self, model_type: str, use_cached: bool = True) -> Any:
        """
        Get a model instance.
        
        Args:
            model_type: Type of model to get
            use_cached: Whether to use cached instance
            
        Returns:
            Model instance
        """
        if use_cached:
            # Look for existing instance of this type
            for key, instance in self.model_instances.items():
                if key.startswith(model_type):
                    return instance
        
        # Create new instance if not cached or not found
        return self.create_model(model_type)
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available model types.
        
        Returns:
            List of available model names
        """
        return list(self.registered_models.keys())
    
    def get_model_info(self, model_type: str) -> Dict[str, Any]:
        """
        Get information about a model type.
        
        Args:
            model_type: Type of model
            
        Returns:
            Model information
        """
        if model_type not in self.registered_models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model_class = self.registered_models[model_type]
        
        # Get basic information
        info = {
            'model_type': model_type,
            'class_name': model_class.__name__,
            'module': model_class.__module__,
            'available': True
        }
        
        # Try to get additional info from a model instance
        try:
            temp_instance = self.create_model(model_type, {})
            if hasattr(temp_instance, 'get_model_info'):
                model_specific_info = temp_instance.get_model_info()
                info.update(model_specific_info)
        except Exception as e:
            logger.warning(f"Could not get detailed info for {model_type}: {str(e)}")
            info['error'] = str(e)
        
        return info
    
    def list_instances(self) -> Dict[str, Any]:
        """
        List all created model instances.
        
        Returns:
            Dictionary of instance information
        """
        instances_info = {}
        
        for instance_key, instance in self.model_instances.items():
            model_type = instance_key.split('_')[0]
            instances_info[instance_key] = {
                'model_type': model_type,
                'class_name': instance.__class__.__name__,
                'config': self.model_configs.get(instance_key, {})
            }
        
        return instances_info
    
    def clear_instances(self):
        """Clear all cached model instances."""
        self.model_instances.clear()
        self.model_configs.clear()
        logger.info("Cleared all model instances")
    
    def remove_instance(self, instance_key: str):
        """
        Remove a specific model instance.
        
        Args:
            instance_key: Key of instance to remove
        """
        if instance_key in self.model_instances:
            del self.model_instances[instance_key]
            del self.model_configs[instance_key]
            logger.info(f"Removed model instance: {instance_key}")
        else:
            logger.warning(f"Instance not found: {instance_key}")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Registry statistics
        """
        return {
            'registered_models_count': len(self.registered_models),
            'active_instances_count': len(self.model_instances),
            'registered_models': list(self.registered_models.keys()),
            'active_instance_types': [key.split('_')[0] for key in self.model_instances.keys()]
        }