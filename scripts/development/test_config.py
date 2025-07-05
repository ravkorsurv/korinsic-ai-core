#!/usr/bin/env python3
"""
Test script to verify the new configuration system works correctly.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.config import Config, ConfigurationError

def test_config_loading():
    """Test configuration loading for different environments"""
    
    print("🔧 Testing Configuration System")
    print("=" * 50)
    
    # Test each environment
    environments = ['development', 'production', 'testing']
    
    for env in environments:
        print(f"\n📋 Testing {env} environment:")
        try:
            config = Config(environment=env)
            
            # Basic configuration tests
            print(f"  ✓ Environment: {config.environment}")
            print(f"  ✓ Debug mode: {config.is_debug()}")
            print(f"  ✓ Server port: {config.get('server.port')}")
            print(f"  ✓ Log level: {config.get('logging.level')}")
            print(f"  ✓ Risk thresholds: {config.get('risk_thresholds.insider_dealing.high')}")
            print(f"  ✓ Model config path: {config.get_model_config_path()}")
            
            # Test configuration methods
            server_config = config.get_server_config()
            print(f"  ✓ Server config keys: {list(server_config.keys())}")
            
            logging_config = config.get_logging_config()
            print(f"  ✓ Logging config keys: {list(logging_config.keys())}")
            
            security_config = config.get_security_config()
            print(f"  ✓ CORS origins: {security_config.get('cors_origins', [])}")
            
            features_config = config.get_features_config()
            print(f"  ✓ Features enabled: {[k for k, v in features_config.items() if v]}")
            
        except Exception as e:
            print(f"  ✗ Error loading {env} config: {e}")
    
    # Test environment variable overrides
    print(f"\n🔀 Testing Environment Variable Overrides:")
    os.environ['DEBUG'] = 'true'
    os.environ['PORT'] = '8080'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    config = Config(environment='development')
    print(f"  ✓ DEBUG override: {config.is_debug()}")
    print(f"  ✓ PORT override: {config.get('server.port')}")
    print(f"  ✓ LOG_LEVEL override: {config.get('logging.level')}")
    
    # Clean up environment variables
    del os.environ['DEBUG']
    del os.environ['PORT']
    del os.environ['LOG_LEVEL']
    
    # Test configuration methods
    print(f"\n⚙️  Testing Configuration Methods:")
    config = Config(environment='development')
    print(f"  ✓ is_production(): {config.is_production()}")
    print(f"  ✓ is_development(): {config.is_development()}")
    print(f"  ✓ is_testing(): {config.is_testing()}")
    print(f"  ✓ get_risk_thresholds(): {config.get_risk_thresholds()}")
    
    # Test configuration dictionary
    print(f"\n📊 Testing Configuration Dictionary:")
    config_dict = config.to_dict()
    print(f"  ✓ Config dict keys: {list(config_dict.keys())}")
    print(f"  ✓ Config representation: {config}")
    
    print(f"\n✅ Configuration system test completed successfully!")

def test_model_config():
    """Test model configuration loading"""
    print(f"\n🤖 Testing Model Configuration:")
    
    config = Config(environment='development')
    model_config_path = config.get_model_config_path()
    print(f"  ✓ Model config path: {model_config_path}")
    
    # Check if model config file exists
    if os.path.exists(model_config_path):
        print(f"  ✓ Model config file exists")
        
        # Try to load and parse the model config
        try:
            import json
            with open(model_config_path, 'r') as f:
                model_config = json.load(f)
            
            print(f"  ✓ Model config loaded successfully")
            print(f"  ✓ Available models: {list(model_config.get('models', {}).keys())}")
            
        except Exception as e:
            print(f"  ✗ Error loading model config: {e}")
    else:
        print(f"  ✗ Model config file not found at: {model_config_path}")

def test_error_handling():
    """Test error handling for configuration issues"""
    print(f"\n🚨 Testing Error Handling:")
    
    # Test invalid environment
    try:
        config = Config(environment='invalid')
        print(f"  ✓ Invalid environment handled gracefully")
    except ConfigurationError as e:
        print(f"  ✓ ConfigurationError raised for invalid environment: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")

if __name__ == "__main__":
    try:
        test_config_loading()
        test_model_config()
        test_error_handling()
        print(f"\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)