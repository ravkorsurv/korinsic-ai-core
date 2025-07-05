#!/usr/bin/env python3
"""
Quick test script for complex risk aggregation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.risk_aggregator import ComplexRiskAggregator
from core.evidence_mapper import map_evidence

def test_risk_aggregation():
    print("Testing Enhanced Bayesian Engine Integration...")
    
    # Test with full Bayesian engine
    from core.bayesian_engine import BayesianEngine
    from core.data_processor import DataProcessor
    
    data_processor = DataProcessor()
    bayesian_engine = BayesianEngine()
    
    # Test data with news context
    test_data = {
        "trades": [
            {"id": "trade_001", "volume": 50000, "side": "buy", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": "trade_002", "volume": 75000, "side": "buy", "timestamp": "2024-01-02T10:00:00Z"}
        ],
        "orders": [],
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
    insider_result = bayesian_engine.calculate_insider_dealing_risk(processed_data)
    print(f"\n📊 INSIDER DEALING:")
    print(f"✅ Risk Score: {insider_result.get('overall_score', 0):.3f}")
    print(f"✅ Risk Level: {insider_result.get('risk_level', 'Unknown')}")
    print(f"✅ News Context: {insider_result.get('news_context', 'N/A')}")
    print(f"✅ High Nodes: {len(insider_result.get('high_nodes', []))}")
    print(f"✅ Critical Nodes: {len(insider_result.get('critical_nodes', []))}")
    
    # Test spoofing
    spoofing_result = bayesian_engine.calculate_spoofing_risk(processed_data)
    print(f"\n📊 SPOOFING:")
    print(f"✅ Risk Score: {spoofing_result.get('overall_score', 0):.3f}")
    print(f"✅ Risk Level: {spoofing_result.get('risk_level', 'Unknown')}")
    print(f"✅ News Context: {spoofing_result.get('news_context', 'N/A')}")
    print(f"✅ High Nodes: {len(spoofing_result.get('high_nodes', []))}")
    print(f"✅ Critical Nodes: {len(spoofing_result.get('critical_nodes', []))}")
    
    print("\n🎉 Enhanced Bayesian Engine tests passed!")

if __name__ == "__main__":
    test_risk_aggregation() 