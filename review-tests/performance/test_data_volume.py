#!/usr/bin/env python3
"""
Test script to show data volume and processing details
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.risk_aggregator import ComplexRiskAggregator
from core.evidence_mapper import map_evidence

def test_data_volume():
    print("=== DATA VOLUME TEST ===")
    
    # Test data with specific volumes
    test_data = {
        "trades": [
            {"id": "trade_001", "volume": 50000, "side": "buy"},
            {"id": "trade_002", "volume": 75000, "side": "buy"},
            {"id": "trade_003", "volume": 100000, "side": "buy"}
        ],
        "orders": [
            {"id": "order_001", "size": 10000, "status": "cancelled"},
            {"id": "order_002", "size": 15000, "status": "cancelled"},
            {"id": "order_003", "size": 5000, "status": "filled"}
        ],
        "hr": {
            "access_level": "high",
            "role": "senior_trader",
            "insider_indicators": ["board_meeting_access", "earnings_call_access"],
            "disciplinary_actions": 1,
            "compliance_violations": 2
        },
        "pnl": {
            "drift": 5000,
            "threshold": 10000,
            "recent_pnl": [
                {"value": -50000, "timestamp": "2024-01-01T10:00:00Z"},
                {"value": -30000, "timestamp": "2024-01-02T10:00:00Z"},
                {"value": -20000, "timestamp": "2024-01-03T10:00:00Z"},
                {"value": 10000, "timestamp": "2024-01-04T10:00:00Z"}
            ]
        },
        "sales": {
            "client_activity": {
                "unusual_count": 5,
                "volume_change": 0.6
            }
        },
        "comms": {
            "intent": "suspicious",
            "messages": [
                {"text": "suspicious message 1", "sentiment": "negative"},
                {"text": "suspicious message 2", "sentiment": "negative"}
            ]
        },
        "trade": {
            "suspicious_flag": True
        },
        "market": {
            "price_movement": 0.08,
            "material_events": [
                {"timestamp": "2024-01-05T10:00:00Z", "type": "earnings"}
            ]
        },
        "historical": {
            "alert_count": 3,
            "avg_volume": 20000
        }
    }
    
    print(f"📊 DATA VOLUME:")
    print(f"   • Trades: {len(test_data['trades'])} records")
    print(f"   • Orders: {len(test_data['orders'])} records")
    print(f"   • PnL records: {len(test_data['pnl']['recent_pnl'])} entries")
    print(f"   • Communications: {len(test_data['comms']['messages'])} messages")
    print(f"   • Material events: {len(test_data['market']['material_events'])} events")
    print(f"   • HR indicators: {len(test_data['hr']['insider_indicators'])} indicators")
    
    total_records = (len(test_data['trades']) + len(test_data['orders']) + 
                    len(test_data['pnl']['recent_pnl']) + len(test_data['comms']['messages']) +
                    len(test_data['market']['material_events']) + len(test_data['hr']['insider_indicators']))
    
    print(f"\n📈 TOTAL RECORDS PROCESSED: {total_records}")
    
    # Process the data using enhanced Bayesian engine
    print(f"\n🔄 PROCESSING DATA WITH ENHANCED BAYESIAN ENGINE...")
    from core.bayesian_engine import BayesianEngine
    from core.data_processor import DataProcessor
    
    data_processor = DataProcessor()
    bayesian_engine = BayesianEngine()
    
    processed_data = data_processor.process(test_data)
    result = bayesian_engine.analyze_insider_dealing(processed_data)
    
    print(f"\n✅ ENHANCED PROCESSING COMPLETE:")
    print(f"   • Data processed through Bayesian engine")
    print(f"   • News context analysis applied")
    print(f"   • Complex risk aggregation performed")
    
    print(f"\n🚨 RISK ANALYSIS RESULTS:")
    print(f"   • Overall Score: {result.get('overall_score', 0):.3f}")
    print(f"   • Risk Level: {result.get('risk_level', 'Unknown')}")
    print(f"   • High Nodes: {len(result.get('high_nodes', []))}")
    print(f"   • Critical Nodes: {len(result.get('critical_nodes', []))}")
    print(f"   • News Context: {result.get('news_context', 'N/A')}")
    
    print(f"\n🎯 DATA PROCESSING COMPLETE!")
    print(f"   Processed {total_records} records across multiple data sources")
    print(f"   Enhanced Bayesian engine with news context analysis")
    print(f"   Computed complex risk score with {len(result.get('high_nodes', []))} high-risk indicators")
    print(f"   News context analysis: {result.get('news_context', 'N/A')}")

if __name__ == "__main__":
    test_data_volume() 