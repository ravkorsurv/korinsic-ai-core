"""
Shared model components and base classes.

This module contains shared components and base classes used
across different model types in the surveillance platform.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from abc import ABC, abstractmethod


class BaseModel(ABC):
    """
    Abstract base class for surveillance models.
    
    This class defines the common interface that all surveillance
    models should implement.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the base model.
        
        Args:
            config: Optional model configuration
        """
        self.config = config if config is not None else {}
        self.metadata = ModelMetadata()
    
    @abstractmethod
    def calculate_risk(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk based on evidence.
        
        Args:
            evidence: Evidence dictionary
            
        Returns:
            Risk assessment results
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.
        
        Returns:
            Model information dictionary
        """
        pass
    
    def validate_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate evidence (default implementation).
        
        Args:
            evidence: Evidence to validate
            
        Returns:
            Validation results
        """
        return {
            'is_valid': True,
            'message': 'Basic validation passed',
            'evidence_count': len(evidence)
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get model configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def update_config(self, updates: Dict[str, Any]):
        """
        Update model configuration.
        
        Args:
            updates: Configuration updates
        """
        self.config.update(updates)


class ModelMetadata:
    """
    Model metadata management.
    
    This class manages metadata information for models including
    version, creation time, performance metrics, etc.
    """
    
    def __init__(self):
        """Initialize model metadata."""
        self.creation_time = datetime.now(timezone.utc).isoformat()
        self.version = "1.0.0"
        self.performance_metrics = {}
        self.usage_stats = {
            'prediction_count': 0,
            'success_count': 0,
            'failure_count': 0
        }
    
    def record_prediction(self, success: bool = True):
        """
        Record a prediction event.
        
        Args:
            success: Whether the prediction was successful
        """
        self.usage_stats['prediction_count'] += 1
        if success:
            self.usage_stats['success_count'] += 1
        else:
            self.usage_stats['failure_count'] += 1
    
    def update_performance_metric(self, metric_name: str, value: float):
        """
        Update a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        self.performance_metrics[metric_name] = value
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get all metadata.
        
        Returns:
            Metadata dictionary
        """
        return {
            'creation_time': self.creation_time,
            'version': self.version,
            'performance_metrics': self.performance_metrics.copy(),
            'usage_stats': self.usage_stats.copy()
        }
    
    def get_success_rate(self) -> float:
        """
        Calculate success rate.
        
        Returns:
            Success rate as a percentage
        """
        total = self.usage_stats['prediction_count']
        if total == 0:
            return 0.0
        return (self.usage_stats['success_count'] / total) * 100.0


class ModelRegistry:
    """
    Generic model registry for managing model instances.
    
    This class provides a generic registry implementation that can
    be extended for specific model types.
    """
    
    def __init__(self):
        """Initialize the model registry."""
        self.models = {}
        self.metadata = {}
    
    def register_model(self, name: str, model_instance: Any):
        """
        Register a model instance.
        
        Args:
            name: Model name
            model_instance: Model instance
        """
        self.models[name] = model_instance
        self.metadata[name] = {
            'registration_time': datetime.now(timezone.utc).isoformat(),
            'model_class': model_instance.__class__.__name__
        }
    
    def get_model(self, name: str) -> Optional[Any]:
        """
        Get a registered model.
        
        Args:
            name: Model name
            
        Returns:
            Model instance or None
        """
        return self.models.get(name)
    
    def list_models(self) -> List[str]:
        """
        List all registered model names.
        
        Returns:
            List of model names
        """
        return list(self.models.keys())
    
    def remove_model(self, name: str):
        """
        Remove a model from the registry.
        
        Args:
            name: Model name
        """
        if name in self.models:
            del self.models[name]
            del self.metadata[name]
    
    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get registry information.
        
        Returns:
            Registry information
        """
        return {
            'total_models': len(self.models),
            'model_names': list(self.models.keys()),
            'metadata': self.metadata.copy()
        }