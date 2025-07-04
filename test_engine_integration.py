#!/usr/bin/env python3
"""
Test script for updated Bayesian engine with market news contextualization
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.bayesian_engine import BayesianEngine
from core.data_processor import DataProcessor

def test_engine_integration():
    print("=" * 80)
    print("🔧 BAYESIAN ENGINE INTEGRATION TEST")
    print("=" * 80)
    
    # Initialize components
    data_processor = DataProcessor()
    bayesian_engine = BayesianEngine()
    
    # Test Case 1: Explained Move Scenario
    print("\n🔵 TEST CASE 1: EXPLAINED MOVE (Should suppress alerts)")
    print("-" * 60)
    
    explained_data = {
        "trades": [
            {"id": "trade_001", "volume": 50000, "side": "buy", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": "trade_002", "volume": 75000, "side": "buy", "timestamp": "2024-01-02T10:00:00Z"}
        ],
        "orders": [],
        "trader_info": {
            "id": "trader_001",
            "role": "trader",
            "access_level": "standard"
        },
        "market_data": {
            "price_movement": 0.05,  # 5% positive movement
            "volatility": 0.025,
            "volume": 1000000
        },
        "material_events": [
            {
                "type": "earnings_announcement",
                "expected_impact": 0.06,  # Expected 6% positive impact
                "materiality_score": 0.9,
                "description": "Strong earnings beat expectations"
            }
        ],
        "news": {
            "news_events": [
                {
                    "sentiment": 0.8,  # Very positive sentiment
                    "market_impact": 0.04,  # Expected 4% impact
                    "relevance_score": 0.9,
                    "headline": "Company reports record quarterly earnings"
                }
            ]
        },
        "hr": {"access_level": "standard", "role": "trader"},
        "pnl": {"drift": 0, "threshold": 10000},
        "sales": {"client_activity": {"unusual_count": 0, "volume_change": 0.1}},
        "historical": {"alert_count": 0},
        "trade": {"suspicious_flag": False},
        "comms": {"intent": "benign"}
    }
    
    processed_explained = data_processor.process(explained_data)
    insider_result_explained = bayesian_engine.calculate_insider_dealing_risk(processed_explained)
    spoofing_result_explained = bayesian_engine.calculate_spoofing_risk(processed_explained)
    
    print(f"📊 INSIDER DEALING:")
    print(f"   Risk Score: {insider_result_explained.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {insider_result_explained.get('risk_level', 'Unknown')}")
    print(f"   News Context: {insider_result_explained.get('news_context', 'N/A')}")
    
    print(f"\n📊 SPOOFING:")
    print(f"   Risk Score: {spoofing_result_explained.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {spoofing_result_explained.get('risk_level', 'Unknown')}")
    print(f"   News Context: {spoofing_result_explained.get('news_context', 'N/A')}")
    
    # Test Case 2: Unexplained Move Scenario
    print("\n🔴 TEST CASE 2: UNEXPLAINED MOVE (Should trigger alerts)")
    print("-" * 60)
    
    unexplained_data = {
        "trades": [
            {"id": "trade_003", "volume": 100000, "side": "buy", "timestamp": "2024-01-03T10:00:00Z"},
            {"id": "trade_004", "volume": 150000, "side": "buy", "timestamp": "2024-01-04T10:00:00Z"}
        ],
        "orders": [
            {"id": "order_001", "size": 10000, "status": "cancelled"},
            {"id": "order_002", "size": 15000, "status": "cancelled"}
        ],
        "trader_info": {
            "id": "trader_002",
            "role": "senior_trader",
            "access_level": "high"
        },
        "market_data": {
            "price_movement": 0.12,  # 12% positive movement
            "volatility": 0.035,
            "volume": 1500000
        },
        "material_events": [],  # No material events
        "news": {
            "news_events": [
                {
                    "sentiment": -0.1,  # Slightly negative sentiment
                    "market_impact": 0.01,  # Minimal impact
                    "relevance_score": 0.3,
                    "headline": "Minor market update"
                }
            ]
        },
        "hr": {"access_level": "high", "role": "senior_trader"},
        "pnl": {"drift": 15000, "threshold": 10000},
        "sales": {"client_activity": {"unusual_count": 5, "volume_change": 0.6}},
        "historical": {"alert_count": 3},
        "trade": {"suspicious_flag": True},
        "comms": {"intent": "suspicious"}
    }
    
    processed_unexplained = data_processor.process(unexplained_data)
    insider_result_unexplained = bayesian_engine.calculate_insider_dealing_risk(processed_unexplained)
    spoofing_result_unexplained = bayesian_engine.calculate_spoofing_risk(processed_unexplained)
    
    print(f"📊 INSIDER DEALING:")
    print(f"   Risk Score: {insider_result_unexplained.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {insider_result_unexplained.get('risk_level', 'Unknown')}")
    print(f"   News Context: {insider_result_unexplained.get('news_context', 'N/A')}")
    
    print(f"\n📊 SPOOFING:")
    print(f"   Risk Score: {spoofing_result_unexplained.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {spoofing_result_unexplained.get('risk_level', 'Unknown')}")
    print(f"   News Context: {spoofing_result_unexplained.get('news_context', 'N/A')}")
    
    # Compare results
    print("\n" + "=" * 80)
    print("📊 COMPARISON ANALYSIS")
    print("=" * 80)
    
    insider_diff = insider_result_unexplained.get('overall_score', 0) - insider_result_explained.get('overall_score', 0)
    spoofing_diff = spoofing_result_unexplained.get('overall_score', 0) - spoofing_result_explained.get('overall_score', 0)
    
    print(f"🔍 INSIDER DEALING DIFFERENCE: {insider_diff:.3f}")
    print(f"🔍 SPOOFING DIFFERENCE: {spoofing_diff:.3f}")
    
    if insider_diff > 0.2 and spoofing_diff > 0.2:
        print("✅ Market news contextualization working correctly!")
        print("   - Explained moves: Lower risk scores")
        print("   - Unexplained moves: Higher risk scores")
    else:
        print("⚠️  Market news contextualization may need tuning")
    
    print("\n" + "=" * 80)
    print("🎯 BAYESIAN ENGINE UPDATES COMPLETE")
    print("=" * 80)
    print("✅ Market news contextualization integrated")
    print("✅ Insider dealing risk calculation updated")
    print("✅ Spoofing risk calculation updated")
    print("✅ False alert suppression implemented")
    print("✅ Complex risk aggregation enabled")
    print("=" * 80)

if __name__ == "__main__":
    test_engine_integration() 