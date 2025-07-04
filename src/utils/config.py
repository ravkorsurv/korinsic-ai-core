import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the surveillance platform"""
    
    def __init__(self):
        self.settings = {
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'debug': os.getenv('DEBUG', 'False').lower() == 'true',
            'host': os.getenv('HOST', '0.0.0.0'),
            'port': int(os.getenv('PORT', 5000)),
            
            # Risk thresholds
            'risk_thresholds': {
                'insider_dealing': {
                    'high': float(os.getenv('INSIDER_HIGH_THRESHOLD', '0.7')),
                    'medium': float(os.getenv('INSIDER_MEDIUM_THRESHOLD', '0.4'))
                },
                'spoofing': {
                    'high': float(os.getenv('SPOOFING_HIGH_THRESHOLD', '0.8')),
                    'medium': float(os.getenv('SPOOFING_MEDIUM_THRESHOLD', '0.5'))
                }
            },
            
            # Model settings
            'models': {
                'bayesian_engine': os.getenv('BAYESIAN_ENGINE', 'pgmpy'),
                'model_update_interval': int(os.getenv('MODEL_UPDATE_INTERVAL', '86400'))
            },
            
            # Logging
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'format': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            },
            
            # Database (if needed for persistence)
            'database': {
                'url': os.getenv('DATABASE_URL', 'sqlite:///surveillance.db')
            },
            
            # Redis (if needed for caching)
            'redis': {
                'url': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self.settings
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.settings['environment'] == 'production'
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.settings['debug']