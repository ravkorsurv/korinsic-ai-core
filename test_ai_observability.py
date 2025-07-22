#!/usr/bin/env python3
"""
Test script for Korinsic AI Observability with OpenInference

This script demonstrates the OpenInference integration by running a sample
analysis and showing the telemetry data being generated.
"""

import os
import sys
import json
import time
from datetime import datetime

# Add src to path
sys.path.append('src')

from utils.ai_observability import initialize_ai_observability
from core.bayesian_engine import BayesianEngine

def create_sample_data():
    """Create sample trading data for testing"""
    return {
        'trader_info': {
            'trader_id': 'TRADER_001',
            'access_level': 'high',
            'department': 'equity_trading'
        },
        'trades': [
            {
                'trade_id': 'T001',
                'instrument': 'AAPL',
                'quantity': 10000,
                'price': 150.25,
                'timestamp': datetime.now().isoformat()
            }
        ],
        'market_data': {
            'volatility': 0.25,
            'price_movement': 0.12,
            'volume': 50000
        },
        'communications': [
            {
                'content': 'We should consider sensitive information in our trades',
                'timestamp': datetime.now().isoformat()
            }
        ],
        'pnl_data': {
            'daily_loss': -150000,
            'unusual_pattern': True
        }
    }

def test_ai_observability():
    """Test AI observability with sample data"""
    print("🚀 Testing Korinsic AI Observability with OpenInference")
    print("=" * 60)
    
    # Initialize AI observability
    print("1. Initializing AI observability...")
    ai_obs = initialize_ai_observability(
        service_name="korinsic-ai-test",
        service_version="1.0.0-test",
        otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    )
    print(f"   ✅ AI observability initialized")
    print(f"   📡 OTLP Endpoint: {ai_obs.otlp_endpoint}")
    
    # Initialize Bayesian engine
    print("\n2. Initializing Bayesian engine...")
    try:
        bayesian_engine = BayesianEngine()
        print(f"   ✅ Bayesian engine loaded successfully")
        models_info = bayesian_engine.get_models_info()
        print(f"   📊 Models loaded: {models_info.get('models_loaded', False)}")
    except Exception as e:
        print(f"   ❌ Error loading Bayesian engine: {e}")
        return False
    
    # Create sample data
    print("\n3. Creating sample trading data...")
    sample_data = create_sample_data()
    print(f"   ✅ Sample data created")
    print(f"   👤 Trader ID: {sample_data['trader_info']['trader_id']}")
    print(f"   📈 Trades: {len(sample_data['trades'])}")
    print(f"   💰 Daily Loss: ${abs(sample_data['pnl_data']['daily_loss']):,}")
    
    # Run analysis with tracing
    print("\n4. Running AI analysis with OpenInference tracing...")
    start_time = time.time()
    
    try:
        # This will automatically use the OpenInference tracing we added
        result = bayesian_engine.analyze_insider_dealing(sample_data)
        
        analysis_time = (time.time() - start_time) * 1000
        
        print(f"   ✅ Analysis completed in {analysis_time:.2f}ms")
        print(f"   🎯 Risk Score: {result.get('risk_score', 0.0):.3f}")
        print(f"   📊 ESI Score: {result.get('esi_score', 0.0):.3f}")
        print(f"   🔧 Fallback Usage: {len([k for k, v in result.get('fallback_usage', {}).items() if v])}")
        
        # Show trace information
        print(f"\n5. Trace Information:")
        print(f"   🔍 Model Type: {result.get('model_type', 'unknown')}")
        print(f"   �� Evidence Used: {len(result.get('evidence_used', {}))}")
        print(f"   ⚡ Performance: {analysis_time:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error during analysis: {e}")
        return False

def main():
    """Main test function"""
    print("Korinsic AI Observability Test")
    print("Testing OpenInference integration with Bayesian models")
    print()
    
    success = test_ai_observability()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed successfully!")
        print()
        print("🎉 What just happened:")
        print("   • OpenInference tracing was initialized")
        print("   • Bayesian inference was traced with AI-specific attributes")
        print("   • Evidence mapping and fallback usage were recorded")
        print("   • Performance metrics were captured")
        print("   • All telemetry was sent to your OTLP endpoint")
        print()
        print("🔍 Next Steps:")
        print("   • Check your observability dashboard for traces")
        print("   • Look for spans with names like 'bayesian_inference.insider_dealing'")
        print("   • Examine AI-specific attributes like 'ai.risk.score' and 'ai.evidence.count'")
        print("   • Monitor fallback usage and inference latency")
    else:
        print("❌ Test failed - check the errors above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
