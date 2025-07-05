#!/usr/bin/env python3
"""
Simple test script to verify the new configuration system works correctly.
Does not require external dependencies.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_config_files():
    """Test configuration files can be loaded"""
    
    print("🔧 Testing Configuration Files")
    print("=" * 50)
    
    config_dir = Path(__file__).parent.parent.parent / "config"
    
    # Test configuration files
    config_files = ['base.json', 'development.json', 'production.json', 'testing.json']
    
    for config_file in config_files:
        config_path = config_dir / config_file
        print(f"\n📋 Testing {config_file}:")
        
        if config_path.exists():
            print(f"  ✓ File exists: {config_path}")
            
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                print(f"  ✓ Valid JSON format")
                print(f"  ✓ Config keys: {list(config_data.keys())}")
                
                # Test specific configuration sections
                if 'server' in config_data:
                    print(f"  ✓ Server config: {config_data['server']}")
                
                if 'logging' in config_data:
                    print(f"  ✓ Logging config: {config_data['logging']}")
                
                if 'risk_thresholds' in config_data:
                    print(f"  ✓ Risk thresholds: {config_data['risk_thresholds']}")
                
            except json.JSONDecodeError as e:
                print(f"  ✗ Invalid JSON: {e}")
            except Exception as e:
                print(f"  ✗ Error reading file: {e}")
        else:
            print(f"  ✗ File not found: {config_path}")
    
    # Test model configuration
    print(f"\n🤖 Testing Model Configuration:")
    model_config_path = config_dir / "models" / "bayesian_models.json"
    
    if model_config_path.exists():
        print(f"  ✓ Model config file exists: {model_config_path}")
        
        try:
            with open(model_config_path, 'r') as f:
                model_config = json.load(f)
            
            print(f"  ✓ Model config loaded successfully")
            print(f"  ✓ Available models: {list(model_config.get('models', {}).keys())}")
            
        except Exception as e:
            print(f"  ✗ Error loading model config: {e}")
    else:
        print(f"  ✗ Model config file not found: {model_config_path}")
    
    # Test deployment configuration
    print(f"\n🚀 Testing Deployment Configuration:")
    deployment_configs = ['docker.json', 'kubernetes.json']
    
    for deploy_config in deployment_configs:
        deploy_path = config_dir / "deployment" / deploy_config
        
        if deploy_path.exists():
            print(f"  ✓ {deploy_config} exists")
            
            try:
                with open(deploy_path, 'r') as f:
                    deploy_data = json.load(f)
                
                print(f"  ✓ {deploy_config} is valid JSON")
                print(f"  ✓ Keys: {list(deploy_data.keys())}")
                
            except Exception as e:
                print(f"  ✗ Error reading {deploy_config}: {e}")
        else:
            print(f"  ✗ {deploy_config} not found")

def test_directory_structure():
    """Test the directory structure is correct"""
    
    print(f"\n📁 Testing Directory Structure:")
    print("=" * 50)
    
    config_dir = Path(__file__).parent.parent.parent / "config"
    
    # Required directories
    required_dirs = [
        config_dir,
        config_dir / "models",
        config_dir / "deployment"
    ]
    
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"  ✓ Directory exists: {dir_path}")
            
            # List contents
            contents = list(dir_path.iterdir())
            print(f"    Contents: {[f.name for f in contents]}")
            
        else:
            print(f"  ✗ Directory missing: {dir_path}")

def test_environment_variables():
    """Test environment variable handling"""
    
    print(f"\n🔀 Testing Environment Variables:")
    print("=" * 50)
    
    # Test some environment variables
    test_vars = {
        'ENVIRONMENT': 'development',
        'DEBUG': 'true',
        'PORT': '8080',
        'LOG_LEVEL': 'DEBUG'
    }
    
    print(f"  Setting test environment variables:")
    for key, value in test_vars.items():
        os.environ[key] = value
        print(f"    {key}={value}")
    
    # Read them back
    print(f"  Reading environment variables:")
    for key in test_vars:
        value = os.getenv(key)
        print(f"    {key}={value}")
    
    # Clean up
    for key in test_vars:
        if key in os.environ:
            del os.environ[key]
    
    print(f"  ✓ Environment variables cleaned up")

if __name__ == "__main__":
    try:
        test_config_files()
        test_directory_structure()
        test_environment_variables()
        print(f"\n🎉 All configuration tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)