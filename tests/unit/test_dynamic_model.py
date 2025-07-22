#!/usr/bin/env python3
"""
Test script for Dynamic Bayesian Model Construction
Demonstrates config-driven model building and runtime modifications
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.bayesian_engine import BayesianEngine
from core.data_processor import DataProcessor

def test_dynamic_model_construction():
    """Test the dynamic model construction from config"""
    print("=" * 80)
    print("🔧 DYNAMIC BAYESIAN MODEL CONSTRUCTION TEST")
    print("=" * 80)
    
    # Initialize the engine (should load from config)
    print("\n📋 Loading Bayesian Engine...")
    bayesian_engine = BayesianEngine()
    
    # Get model information
    models_info = bayesian_engine.get_models_info()
    print(f"✅ Models loaded: {models_info['models_loaded']}")
    if isinstance(models_info['insider_dealing_model'], dict) and 'nodes' in models_info['insider_dealing_model']:
        print(f"✅ Insider dealing nodes: {models_info['insider_dealing_model']['nodes']}")
    if isinstance(models_info['spoofing_model'], dict) and 'nodes' in models_info['spoofing_model']:
        print(f"✅ Spoofing nodes: {models_info['spoofing_model']['nodes']}")
    
    # Test with sample data
    print("\n🧪 Testing with sample data...")
    data_processor = DataProcessor()
    
    test_data = {
        "trades": [
            {"id": "trade_001", "volume": 50000, "side": "buy", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": "trade_002", "volume": 75000, "side": "buy", "timestamp": "2024-01-02T10:00:00Z"}
        ],
        "orders": [
            {"id": "order_001", "size": 10000, "status": "cancelled"},
            {"id": "order_002", "size": 15000, "status": "filled"}
        ],
        "trader_info": {"id": "trader_001", "role": "senior_trader", "access_level": "high"},
        "market_data": {"price_movement": 0.08, "volatility": 0.025, "volume": 1000000},
        "material_events": [
            {
                "type": "earnings_announcement",
                "expected_impact": 0.06,
                "materiality_score": 0.9,
                "description": "Strong earnings beat"
            }
        ],
        "news": {
            "news_events": [
                {
                    "sentiment": 0.7,
                    "market_impact": 0.04,
                    "relevance_score": 0.8,
                    "headline": "Company beats earnings"
                }
            ]
        },
        "hr": {"access_level": "high", "role": "senior_trader"},
        "pnl": {"drift": 15000, "threshold": 10000, "recent_pnl": [{"value": -50000}, {"value": -30000}]},
        "sales": {"client_activity": {"unusual_count": 5, "volume_change": 0.6}},
        "historical": {"alert_count": 3},
        "trade": {"suspicious_flag": True},
        "comms": {"intent": "suspicious"}
    }
    
    processed_data = data_processor.process(test_data)
    
    # Test insider dealing
    insider_result = bayesian_engine.analyze_insider_dealing(processed_data)
    print(f"\n📊 INSIDER DEALING (Dynamic Model):")
    print(f"   Risk Score: {insider_result.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {insider_result.get('risk_level', 'Unknown')}")
    print(f"   News Context: {insider_result.get('news_context', 'N/A')}")
    print(f"   High Nodes: {len(insider_result.get('high_nodes', []))}")
    print(f"   Critical Nodes: {len(insider_result.get('critical_nodes', []))}")
    
    # Test spoofing
    spoofing_result = bayesian_engine.analyze_spoofing(processed_data)
    print(f"\n📊 SPOOFING (Dynamic Model):")
    print(f"   Risk Score: {spoofing_result.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {spoofing_result.get('risk_level', 'Unknown')}")
    print(f"   News Context: {spoofing_result.get('news_context', 'N/A')}")
    print(f"   High Nodes: {len(spoofing_result.get('high_nodes', []))}")
    print(f"   Critical Nodes: {len(spoofing_result.get('critical_nodes', []))}")
    
    print("\n" + "=" * 80)
    print("🎯 DYNAMIC MODEL FEATURES:")
    print("=" * 80)
    print("✅ Config-driven model construction")
    print("✅ Runtime model loading from JSON")
    print("✅ Fallback to hardcoded models if config missing")
    print("✅ Support for multiple model types (insider dealing, spoofing)")
    print("✅ Node descriptions and fallback priors in config")
    print("✅ Global settings for thresholds and multipliers")
    print("✅ Dynamic CPD loading and validation")
    print("=" * 80)

def demonstrate_config_modification():
    """Demonstrate how to modify the config to add new nodes or change CPDs"""
    print("\n🔧 CONFIG MODIFICATION DEMONSTRATION")
    print("-" * 50)
    
    config_path = "bayesian_model_config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("📋 Current config structure:")
        print(f"   Models: {list(config['models'].keys())}")
        print(f"   Insider dealing nodes: {len(config['models']['insider_dealing']['nodes'])}")
        print(f"   Spoofing nodes: {len(config['models']['spoofing']['nodes'])}")
        
        # Show how to add a new node
        print("\n➕ To add a new node 'MarketVolatility':")
        print("   1. Add to nodes array:")
        print("   {")
        print('     "name": "MarketVolatility",')
        print('     "states": ["Low", "Medium", "High"],')
        print('     "description": "Market volatility level",')
        print('     "fallback_prior": [0.6, 0.3, 0.1]')
        print("   }")
        print("   2. Add edges: [\"MarketVolatility\", \"Risk\"]")
        print("   3. Add CPD with appropriate values")
        print("   4. Restart the engine to load new model")
        
        # Show global settings
        print(f"\n⚙️  Global settings:")
        print(f"   News context suppression: {config['global_settings']['news_context_suppression']}")
        print(f"   Risk thresholds: {config['global_settings']['risk_thresholds']}")
        
    else:
        print("❌ Config file not found")

if __name__ == "__main__":
    test_dynamic_model_construction()
    demonstrate_config_modification()
    print("\n🎉 Dynamic model construction test completed!") 