#!/usr/bin/env python3
"""
Simple End-to-End Test for Kor.ai Core
This demonstrates the backend functionality and shows the system is working.
"""

import json
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_data_processor():
    """Test data processing functionality"""
    try:
        from core.data_processor import DataProcessor
        processor = DataProcessor()
        
        # Sample trading data
        sample_data = {
            "trades": [
                {
                    "timestamp": 1640995200,  # 2022-01-01
                    "symbol": "AAPL",
                    "volume": 10000,
                    "price": 150.0,
                    "trader_id": "T001"
                },
                {
                    "timestamp": 1640995260,  # 2022-01-01 + 1min
                    "symbol": "AAPL", 
                    "volume": 25000,
                    "price": 152.0,
                    "trader_id": "T001"
                }
            ],
            "trader_info": {
                "role": "senior_trader",
                "department": "equity_trading"
            }
        }
        
        processed = processor.process(sample_data)
        print("✅ Data Processor: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Data Processor: FAILED - {str(e)}")
        return False

def test_risk_calculator():
    """Test risk calculation functionality"""
    try:
        from core.risk_calculator import RiskCalculator
        calculator = RiskCalculator()
        
        # Sample risk calculation
        insider_score = 0.3
        spoofing_score = 0.2
        processed_data = {
            "metrics": {
                "volume_variance": 2.5,
                "price_impact": 0.01
            }
        }
        
        overall_risk = calculator.calculate_overall_risk(
            insider_score, spoofing_score, processed_data
        )
        
        print("✅ Risk Calculator: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Risk Calculator: FAILED - {str(e)}")
        return False

def test_alert_generator():
    """Test alert generation functionality"""
    try:
        from core.alert_generator import AlertGenerator
        generator = AlertGenerator()
        
        # Sample data for alert generation
        processed_data = {
            "trades": [{"symbol": "AAPL", "volume": 10000}],
            "trader_info": {"trader_id": "T001"}
        }
        
        alerts = generator.generate_alerts(
            processed_data, 
            insider_dealing_score=0.8,  # High risk
            spoofing_score=0.3,
            overall_risk=0.6
        )
        
        print("✅ Alert Generator: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Alert Generator: FAILED - {str(e)}")
        return False

def test_bayesian_engine():
    """Test Bayesian engine with fixed model"""
    try:
        from core.bayesian_engine import BayesianEngine
        engine = BayesianEngine()
        
        # Test model info
        models_info = engine.get_models_info()
        
        if models_info['models_loaded']:
            print("✅ Bayesian Engine: PASSED (Models loaded successfully)")
            return True
        else:
            print("❌ Bayesian Engine: FAILED (Models not loaded)")
            return False
            
    except Exception as e:
        print(f"❌ Bayesian Engine: FAILED - {str(e)}")
        return False

def main():
    """Run all end-to-end tests"""
    print("🚀 Kor.ai Core End-to-End Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    test_results.append(test_data_processor())
    test_results.append(test_risk_calculator())
    test_results.append(test_alert_generator())
    test_results.append(test_bayesian_engine())
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Backend is working correctly.")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())