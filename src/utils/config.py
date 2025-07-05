import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Exception raised for configuration-related errors"""
    pass

class Config:
    """Enhanced configuration management for the surveillance platform"""
    
    def __init__(self, environment: Optional[str] = None):
        """
        Initialize configuration with environment-specific settings.
        
        Args:
            environment: Environment name (development, production, testing)
                        If None, uses ENVIRONMENT env var or defaults to 'development'
        """
        self.environment = environment or os.getenv('ENVIRONMENT', 'development')
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.settings = {}
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from JSON files with environment-specific overrides"""
        try:
            # Load base configuration
            base_config = self._load_config_file('base.json')
            
            # Load environment-specific configuration
            env_config = self._load_config_file(f'{self.environment}.json')
            
            # Merge configurations (environment overrides base)
            self.settings = self._deep_merge(base_config, env_config)
            
            # Apply environment variable overrides
            self._apply_env_overrides()
            
            logger.info(f"Configuration loaded for environment: {self.environment}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigurationError(f"Configuration loading failed: {e}")
    
    def _load_config_file(self, filename: str) -> Dict[str, Any]:
        """Load and parse a JSON configuration file"""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            if filename == 'base.json':
                raise ConfigurationError(f"Base configuration file not found: {config_path}")
            else:
                logger.warning(f"Environment config file not found: {config_path}, using base only")
                return {}
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Process any environment variable substitutions
            return self._process_env_vars(config)
            
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {filename}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load {filename}: {e}")
    
    def _process_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process environment variable substitutions in config values"""
        if isinstance(config, dict):
            return {k: self._process_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._process_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            # Extract environment variable name
            env_var = config[2:-1]
            return os.getenv(env_var, config)  # Return original if env var not found
        else:
            return config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with override taking precedence"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration"""
        env_overrides = {
            'DEBUG': ('server.debug', lambda x: x.lower() == 'true'),
            'PORT': ('server.port', int),
            'HOST': ('server.host', str),
            'LOG_LEVEL': ('logging.level', str),
            'INSIDER_HIGH_THRESHOLD': ('risk_thresholds.insider_dealing.high', float),
            'INSIDER_MEDIUM_THRESHOLD': ('risk_thresholds.insider_dealing.medium', float),
            'SPOOFING_HIGH_THRESHOLD': ('risk_thresholds.spoofing.high', float),
            'SPOOFING_MEDIUM_THRESHOLD': ('risk_thresholds.spoofing.medium', float),
            'DATABASE_URL': ('database.url', str),
            'REDIS_URL': ('redis.url', str),
            'MODEL_UPDATE_INTERVAL': ('models.model_update_interval', int),
        }
        
        for env_var, (config_path, converter) in env_overrides.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    converted_value = converter(env_value)
                    self.set(config_path, converted_value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert env var {env_var}={env_value}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'server.port')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'server.port')
            value: Value to set
        """
        keys = key.split('.')
        config = self.settings
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_risk_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get risk thresholds for all models"""
        return self.get('risk_thresholds', {})
    
    def get_model_config_path(self) -> str:
        """Get path to model configuration file"""
        return str(self.config_dir / self.get('models.model_config_path', 'models/bayesian_models.json'))
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == 'development'
    
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment == 'testing'
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get('server.debug', False)
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration"""
        return self.get('server', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.get('logging', {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.get('database', {})
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return self.get('redis', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return self.get('security', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return self.get('performance', {})
    
    def get_features_config(self) -> Dict[str, Any]:
        """Get features configuration"""
        return self.get('features', {})
    
    def get_alerts_config(self) -> Dict[str, Any]:
        """Get alerts configuration"""
        return self.get('alerts', {})
    
    def reload(self):
        """Reload configuration from files"""
        self._load_configuration()
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self.settings.copy()
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"Config(environment={self.environment})"
    
    def __repr__(self) -> str:
        """Detailed representation of configuration"""
        return f"Config(environment={self.environment}, settings_keys={list(self.settings.keys())})"

# Global configuration instance
config = Config()

# Convenience functions for backward compatibility
def get_config():
    """Get the global configuration instance"""
    return config