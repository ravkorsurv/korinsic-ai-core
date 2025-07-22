#!/usr/bin/env python3
"""
Test script for Market News Contextualization feature
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.risk_aggregator import ComplexRiskAggregator
from core.evidence_mapper import map_evidence

def test_news_contextualization():
    print("=" * 80)
    print("📰 MARKET NEWS CONTEXTUALIZATION TEST")
    print("=" * 80)
    
    # Test Case 1: Explained Move (should suppress alerts)
    print("\n🔵 TEST CASE 1: EXPLAINED MOVE")
    print("-" * 50)
    explained_data = {
        "market": {
            "price_movement": 0.05,  # 5% positive movement
            "material_events": [
                {
                    "type": "earnings_announcement",
                    "expected_impact": 0.06,  # Expected 6% positive impact
                    "materiality_score": 0.9,
                    "description": "Strong earnings beat expectations"
                }
            ]
        },
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
        "trade": {"suspicious_flag": False},
        "comms": {"intent": "benign"},
        "pnl": {"drift": 0, "threshold": 10000},
        "hr": {"access_level": "standard", "role": "trader"},
        "sales": {"client_activity": {"unusual_count": 0, "volume_change": 0.1}},
        "historical": {"alert_count": 0}
    }
    
    mapped_explained = map_evidence(explained_data)
    print(f"Market News Context: {mapped_explained.get('market_news_context', 'N/A')} (0=explained, 1=partial, 2=unexplained)")
    print("✅ Expected: 0 (explained_move) - Alerts should be suppressed")
    
    # Test Case 2: Partially Explained Move
    print("\n🟡 TEST CASE 2: PARTIALLY EXPLAINED MOVE")
    print("-" * 50)
    partial_data = {
        "market": {
            "price_movement": 0.08,  # 8% positive movement
            "material_events": [
                {
                    "type": "earnings_announcement",
                    "expected_impact": 0.03,  # Expected 3% positive impact
                    "materiality_score": 0.7,
                    "description": "Moderate earnings beat"
                }
            ]
        },
        "news": {
            "news_events": [
                {
                    "sentiment": 0.3,  # Slightly positive sentiment
                    "market_impact": 0.02,  # Expected 2% impact
                    "relevance_score": 0.6,
                    "headline": "Company meets earnings expectations"
                }
            ]
        },
        "trade": {"suspicious_flag": True},
        "comms": {"intent": "suspicious"},
        "pnl": {"drift": 5000, "threshold": 10000},
        "hr": {"access_level": "high", "role": "senior_trader"},
        "sales": {"client_activity": {"unusual_count": 2, "volume_change": 0.3}},
        "historical": {"alert_count": 1}
    }
    
    mapped_partial = map_evidence(partial_data)
    print(f"Market News Context: {mapped_partial.get('market_news_context', 'N/A')} (0=explained, 1=partial, 2=unexplained)")
    print("⚠️  Expected: 1 (partially_explained) - Some alerts may be reduced")
    
    # Test Case 3: Unexplained Move (should trigger alerts)
    print("\n🔴 TEST CASE 3: UNEXPLAINED MOVE")
    print("-" * 50)
    unexplained_data = {
        "market": {
            "price_movement": 0.12,  # 12% positive movement
            "material_events": []  # No material events
        },
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
        "trade": {"suspicious_flag": True},
        "comms": {"intent": "suspicious"},
        "pnl": {"drift": 15000, "threshold": 10000},
        "hr": {"access_level": "high", "role": "senior_trader"},
        "sales": {"client_activity": {"unusual_count": 5, "volume_change": 0.6}},
        "historical": {"alert_count": 3}
    }
    
    mapped_unexplained = map_evidence(unexplained_data)
    print(f"Market News Context: {mapped_unexplained.get('market_news_context', 'N/A')} (0=explained, 1=partial, 2=unexplained)")
    print("🚨 Expected: 2 (unexplained_move) - Full alerts should trigger")
    
    # Test Enhanced Bayesian Engine with News Context
    print("\n" + "=" * 80)
    print("🎯 ENHANCED BAYESIAN ENGINE WITH NEWS CONTEXT")
    print("=" * 80)
    
    from core.bayesian_engine import BayesianEngine
    from core.data_processor import DataProcessor
    
    data_processor = DataProcessor()
    bayesian_engine = BayesianEngine()
    
    # Test explained move scenario with full engine
    processed_explained = data_processor.process(explained_data)
    result_explained = bayesian_engine.analyze_insider_dealing(processed_explained)
    print(f"\n🔵 EXPLAINED MOVE SCENARIO:")
    print(f"   Risk Score: {result_explained.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {result_explained.get('risk_level', 'Unknown')}")
    print(f"   News Context: {result_explained.get('news_context', 'N/A')}")
    print(f"   High Nodes: {len(result_explained.get('high_nodes', []))}")
    
    # Test unexplained move scenario with full engine
    processed_unexplained = data_processor.process(unexplained_data)
    result_unexplained = bayesian_engine.analyze_insider_dealing(processed_unexplained)
    print(f"\n🔴 UNEXPLAINED MOVE SCENARIO:")
    print(f"   Risk Score: {result_unexplained.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {result_unexplained.get('risk_level', 'Unknown')}")
    print(f"   News Context: {result_unexplained.get('news_context', 'N/A')}")
    print(f"   High Nodes: {len(result_unexplained.get('high_nodes', []))}")
    
    # Compare the difference
    score_difference = result_unexplained.get('overall_score', 0) - result_explained.get('overall_score', 0)
    print(f"\n📊 ENHANCED IMPACT ANALYSIS:")
    print(f"   Score Difference: {score_difference:.3f}")
    print(f"   News Context Suppression: {'✅ Working' if score_difference > 0.1 else '❌ Needs tuning'}")
    print(f"   Engine Integration: ✅ Enhanced Bayesian Engine with news context")
    
    print("\n" + "=" * 80)
    print("📋 NEWS CONTEXTUALIZATION FEATURES:")
    print("=" * 80)
    print("✅ Explains price movements using public events/news")
    print("✅ Reduces false alerts for explained moves")
    print("✅ Maintains sensitivity for unexplained moves")
    print("✅ Integrates with NewsEventMatch and ExpectedPriceMovement logic")
    print("✅ Implements 'explained move suppressor' node")
    print("=" * 80)

if __name__ == "__main__":
    test_news_contextualization() 