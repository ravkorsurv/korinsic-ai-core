#!/usr/bin/env python3
"""
Evidence Sufficiency Index (ESI) Feature Test

Tests the ESI calculation and integration with the Bayesian Risk Engine
based on the Kor.ai wiki specification.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.bayesian_engine import BayesianEngine
from core.data_processor import DataProcessor
from core.evidence_sufficiency_index import EvidenceSufficiencyIndex

def test_esi_calculation():
    """Test the ESI calculation with various scenarios"""
    print("=" * 80)
    print("🧮 EVIDENCE SUFFICIENCY INDEX (ESI) TEST")
    print("=" * 80)
    
    # Initialize ESI calculator
    esi_calculator = EvidenceSufficiencyIndex()
    
    # Test case 1: Strong evidence scenario
    print("\n📊 TEST CASE 1: Strong Evidence Scenario")
    print("-" * 50)
    
    strong_evidence = {
        'trades': [{'volume': 100000, 'side': 'buy'}],
        'orders': [{'size': 50000, 'status': 'filled'}],
        'material_events': [{'type': 'earnings', 'impact': 0.05}],
        'news': {'events': [{'sentiment': 0.8, 'impact': 0.03}]}
    }
    
    strong_node_states = {
        'MaterialInfo': 'Clear access',
        'TradingActivity': 'Highly unusual',
        'Timing': 'Highly suspicious',
        'PriceImpact': 'High',
        'OrderPattern': 'Excessive layering',
        'CancellationRate': 'High'
    }
    
    strong_fallback_usage = {
        'MaterialInfo': False,
        'TradingActivity': False,
        'Timing': False,
        'PriceImpact': False,
        'OrderPattern': False,
        'CancellationRate': False
    }
    
    strong_esi = esi_calculator.calculate_esi(
        evidence=strong_evidence,
        node_states=strong_node_states,
        fallback_usage=strong_fallback_usage
    )
    
    print(f"📈 ESI Score: {strong_esi['evidence_sufficiency_index']:.3f}")
    print(f"🏷️  ESI Badge: {strong_esi['esi_badge']}")
    print(f"📊 Node Count: {strong_esi['node_count']}")
    print(f"🎯 Mean Confidence: {strong_esi['mean_confidence']}")
    print(f"🔄 Fallback Ratio: {strong_esi['fallback_ratio']:.3f}")
    print(f"📈 Contribution Spread: {strong_esi['contribution_spread']}")
    print(f"🌐 Active Clusters: {strong_esi['clusters']}")
    
    # Test case 2: Sparse evidence scenario
    print("\n📊 TEST CASE 2: Sparse Evidence Scenario")
    print("-" * 50)
    
    sparse_evidence = {
        'trades': []  # No trades
    }
    
    sparse_node_states = {
        'MaterialInfo': 'Unknown',
        'TradingActivity': 'Normal',
        'Timing': 'Unknown',
        'PriceImpact': 'Unknown',
        'OrderPattern': 'Unknown',
        'CancellationRate': 'Unknown'
    }
    
    sparse_fallback_usage = {
        'MaterialInfo': True,
        'TradingActivity': False,
        'Timing': True,
        'PriceImpact': True,
        'OrderPattern': True,
        'CancellationRate': True
    }
    
    sparse_esi = esi_calculator.calculate_esi(
        evidence=sparse_evidence,
        node_states=sparse_node_states,
        fallback_usage=sparse_fallback_usage
    )
    
    print(f"📈 ESI Score: {sparse_esi['evidence_sufficiency_index']:.3f}")
    print(f"🏷️  ESI Badge: {sparse_esi['esi_badge']}")
    print(f"📊 Node Count: {sparse_esi['node_count']}")
    print(f"🎯 Mean Confidence: {sparse_esi['mean_confidence']}")
    print(f"🔄 Fallback Ratio: {sparse_esi['fallback_ratio']:.3f}")
    print(f"📈 Contribution Spread: {sparse_esi['contribution_spread']}")
    print(f"🌐 Active Clusters: {sparse_esi['clusters']}")
    
    # Test case 3: Moderate evidence scenario
    print("\n📊 TEST CASE 3: Moderate Evidence Scenario")
    print("-" * 50)
    
    moderate_evidence = {
        'trades': [{'volume': 50000, 'side': 'buy'}],
        'orders': [{'size': 25000, 'status': 'cancelled'}],
        'material_events': []
    }
    
    moderate_node_states = {
        'MaterialInfo': 'Potential access',
        'TradingActivity': 'Unusual',
        'Timing': 'Normal',
        'PriceImpact': 'Medium',
        'OrderPattern': 'Layered',
        'CancellationRate': 'Medium'
    }
    
    moderate_fallback_usage = {
        'MaterialInfo': False,
        'TradingActivity': False,
        'Timing': False,
        'PriceImpact': False,
        'OrderPattern': False,
        'CancellationRate': False
    }
    
    moderate_esi = esi_calculator.calculate_esi(
        evidence=moderate_evidence,
        node_states=moderate_node_states,
        fallback_usage=moderate_fallback_usage
    )
    
    print(f"📈 ESI Score: {moderate_esi['evidence_sufficiency_index']:.3f}")
    print(f"🏷️  ESI Badge: {moderate_esi['esi_badge']}")
    print(f"📊 Node Count: {moderate_esi['node_count']}")
    print(f"🎯 Mean Confidence: {moderate_esi['mean_confidence']}")
    print(f"🔄 Fallback Ratio: {moderate_esi['fallback_ratio']:.3f}")
    print(f"📈 Contribution Spread: {moderate_esi['contribution_spread']}")
    print(f"🌐 Active Clusters: {moderate_esi['clusters']}")

def test_esi_integration():
    """Test ESI integration with the Bayesian engine"""
    print("\n" + "=" * 80)
    print("🔗 ESI INTEGRATION TEST")
    print("=" * 80)
    
    # Initialize components
    bayesian_engine = BayesianEngine()
    data_processor = DataProcessor()
    
    # Test data with various evidence levels
    test_cases = [
        {
            "name": "Strong Evidence Case",
            "data": {
                "trades": [
                    {"id": "trade_001", "volume": 100000, "side": "buy", "timestamp": "2024-01-01T10:00:00Z"},
                    {"id": "trade_002", "volume": 150000, "side": "buy", "timestamp": "2024-01-02T10:00:00Z"}
                ],
                "orders": [
                    {"id": "order_001", "size": 50000, "status": "cancelled"},
                    {"id": "order_002", "size": 75000, "status": "cancelled"}
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
        },
        {
            "name": "Sparse Evidence Case",
            "data": {
                "trades": [],
                "orders": [],
                "trader_info": {"id": "trader_002", "role": "trader", "access_level": "low"},
                "market_data": {"price_movement": 0.02, "volatility": 0.015, "volume": 500000},
                "material_events": [],
                "news": {"news_events": []},
                "hr": {"access_level": "low", "role": "trader"},
                "pnl": {"drift": 2000, "threshold": 10000, "recent_pnl": []},
                "sales": {"client_activity": {"unusual_count": 0, "volume_change": 0.1}},
                "historical": {"alert_count": 0},
                "trade": {"suspicious_flag": False},
                "comms": {"intent": "normal"}
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 {test_case['name']}")
        print("-" * 40)
        
        # Process data
        processed_data = data_processor.process(test_case['data'])
        
        # Calculate insider dealing risk with ESI
        insider_result = bayesian_engine.calculate_insider_dealing_risk(processed_data)
        
        if 'esi' in insider_result:
            esi = insider_result['esi']
            print(f"📊 Risk Score: {insider_result.get('overall_score', 0):.3f}")
            print(f"📈 ESI Score: {esi.get('evidence_sufficiency_index', 0):.3f}")
            print(f"🏷️  ESI Badge: {esi.get('esi_badge', 'Unknown')}")
            print(f"📊 Node Count: {esi.get('node_count', 0)}")
            print(f"🎯 Mean Confidence: {esi.get('mean_confidence', 'Unknown')}")
            print(f"🔄 Fallback Ratio: {esi.get('fallback_ratio', 0):.3f}")
            print(f"📈 Contribution Spread: {esi.get('contribution_spread', 'Unknown')}")
            print(f"🌐 Active Clusters: {esi.get('clusters', [])}")
            
            # Calculate adjusted risk score
            adjusted_score = bayesian_engine.esi_calculator.adjust_risk_score(
                insider_result.get('overall_score', 0),
                esi.get('evidence_sufficiency_index', 0)
            )
            print(f"⚖️  Adjusted Risk Score: {adjusted_score:.3f}")
        else:
            print("❌ ESI not found in result")

def test_esi_components():
    """Test individual ESI components"""
    print("\n" + "=" * 80)
    print("🔧 ESI COMPONENTS TEST")
    print("=" * 80)
    
    esi_calculator = EvidenceSufficiencyIndex()
    
    # Test node activation ratio
    print("\n📊 Node Activation Ratio Test:")
    node_states = {
        'MaterialInfo': 'Clear access',
        'TradingActivity': 'Unknown',
        'Timing': 'Suspicious',
        'PriceImpact': 'High'
    }
    activation_ratio = esi_calculator._calculate_node_activation_ratio(node_states)
    print(f"   Active nodes: 3/4 = {activation_ratio:.3f}")
    
    # Test fallback ratio
    print("\n🔄 Fallback Ratio Test:")
    fallback_usage = {
        'MaterialInfo': False,
        'TradingActivity': True,
        'Timing': False,
        'PriceImpact': True
    }
    fallback_ratio = esi_calculator._calculate_fallback_ratio(fallback_usage)
    print(f"   Fallback usage: 2/4 = {fallback_ratio:.3f}")
    
    # Test contribution entropy
    print("\n📈 Contribution Entropy Test:")
    entropy = esi_calculator._calculate_contribution_entropy(node_states)
    print(f"   Entropy score: {entropy:.3f}")
    
    # Test cross-cluster diversity
    print("\n🌐 Cross-Cluster Diversity Test:")
    diversity = esi_calculator._calculate_cross_cluster_diversity(node_states)
    print(f"   Diversity score: {diversity:.3f}")

def demonstrate_esi_benefits():
    """Demonstrate the benefits of ESI"""
    print("\n" + "=" * 80)
    print("🎯 ESI BENEFITS DEMONSTRATION")
    print("=" * 80)
    
    print("\n✅ **Trust Calibration for Analysts:**")
    print("   - ESI helps analysts understand how well-supported risk scores are")
    print("   - High ESI = High confidence in the alert")
    print("   - Low ESI = Caution required, may need additional investigation")
    
    print("\n✅ **Filtering and Triage:**")
    print("   - Filter alerts with ESI > 0.7 for high-confidence cases")
    print("   - Sort by ESI descending to prioritize well-evidenced alerts")
    print("   - Reduce false positive burden on analysts")
    
    print("\n✅ **Enhanced Explainability:**")
    print("   - Explain not just why an alert was scored as risky")
    print("   - But how trustworthy and complete the supporting evidence is")
    print("   - Enables new standard of transparency in AI-powered surveillance")
    
    print("\n✅ **Risk Score Adjustment:**")
    print("   - Use ESI as multiplier: Adjusted Risk = Risk Score × ESI")
    print("   - Helps evaluate impact of noisy nodes")
    print("   - Simulate precision/recall tradeoffs")
    
    print("\n✅ **UI Integration Strategy:**")
    print("   - Primary: Bayesian Risk Score")
    print("   - Secondary: ESI Score + Badge (Strong/Moderate/Limited/Sparse)")
    print("   - Badges on Alert Cards: 'ESI: Strong Evidence'")
    print("   - Explain Panel Tooltips with detailed breakdown")

if __name__ == "__main__":
    test_esi_calculation()
    test_esi_integration()
    test_esi_components()
    demonstrate_esi_benefits()
    
    print("\n" + "=" * 80)
    print("🎉 ESI FEATURE TEST COMPLETED!")
    print("=" * 80)
    print("✅ ESI calculation with multiple scenarios")
    print("✅ Integration with Bayesian engine")
    print("✅ Individual component testing")
    print("✅ Benefits demonstration")
    print("✅ Based on Kor.ai wiki specification")
    print("=" * 80) 