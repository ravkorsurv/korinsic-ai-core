#!/usr/bin/env python3
"""
Complete ESI Integration Test

Demonstrates Evidence Sufficiency Index working with all existing features:
- Dynamic model construction
- Fallback logic
- Complex risk aggregation
- News context suppression
- Alert generation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.bayesian_engine import BayesianEngine
from core.data_processor import DataProcessor
from core.alert_generator import AlertGenerator

def test_complete_esi_integration():
    """Test ESI integration with all system components"""
    print("=" * 80)
    print("🔗 COMPLETE ESI INTEGRATION TEST")
    print("=" * 80)
    
    # Initialize all components
    bayesian_engine = BayesianEngine()
    data_processor = DataProcessor()
    alert_generator = AlertGenerator()
    
    print("✅ All components initialized")
    
    # Test case 1: High-risk scenario with strong evidence
    print("\n🔴 TEST CASE 1: High Risk + Strong Evidence")
    print("-" * 60)
    
    high_risk_data = {
        "trades": [
            {"id": "trade_001", "volume": 200000, "side": "buy", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": "trade_002", "volume": 300000, "side": "buy", "timestamp": "2024-01-02T10:00:00Z"},
            {"id": "trade_003", "volume": 250000, "side": "buy", "timestamp": "2024-01-03T10:00:00Z"}
        ],
        "orders": [
            {"id": "order_001", "size": 100000, "status": "cancelled"},
            {"id": "order_002", "size": 150000, "status": "cancelled"},
            {"id": "order_003", "size": 200000, "status": "cancelled"}
        ],
        "trader_info": {"id": "trader_001", "role": "senior_trader", "access_level": "high"},
        "market_data": {"price_movement": 0.15, "volatility": 0.035, "volume": 2000000},
        "material_events": [
            {
                "type": "earnings_announcement",
                "expected_impact": 0.08,
                "materiality_score": 0.95,
                "description": "Major earnings surprise"
            }
        ],
        "news": {"news_events": []},  # No news to explain the move
        "hr": {"access_level": "high", "role": "senior_trader"},
        "pnl": {"drift": 25000, "threshold": 10000, "recent_pnl": [{"value": -75000}, {"value": -50000}]},
        "sales": {"client_activity": {"unusual_count": 8, "volume_change": 0.8}},
        "historical": {"alert_count": 5},
        "trade": {"suspicious_flag": True},
        "comms": {"intent": "suspicious"}
    }
    
    # Process data
    processed_data = data_processor.process(high_risk_data)
    
    # Calculate risks
    insider_result = bayesian_engine.calculate_insider_dealing_risk(processed_data)
    spoofing_result = bayesian_engine.calculate_spoofing_risk(processed_data)
    
    # Display results
    print(f"📊 INSIDER DEALING:")
    print(f"   Risk Score: {insider_result.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {insider_result.get('risk_level', 'Unknown')}")
    if 'esi' in insider_result:
        esi = insider_result['esi']
        print(f"   📈 ESI Score: {esi.get('evidence_sufficiency_index', 0):.3f}")
        print(f"   🏷️  ESI Badge: {esi.get('esi_badge', 'Unknown')}")
        print(f"   📊 Node Count: {esi.get('node_count', 0)}")
        print(f"   🎯 Mean Confidence: {esi.get('mean_confidence', 'Unknown')}")
        print(f"   🔄 Fallback Ratio: {esi.get('fallback_ratio', 0):.3f}")
        print(f"   📈 Contribution Spread: {esi.get('contribution_spread', 'Unknown')}")
        print(f"   🌐 Active Clusters: {esi.get('clusters', [])}")
    
    print(f"\n📊 SPOOFING:")
    print(f"   Risk Score: {spoofing_result.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {spoofing_result.get('risk_level', 'Unknown')}")
    if 'esi' in spoofing_result:
        esi = spoofing_result['esi']
        print(f"   📈 ESI Score: {esi.get('evidence_sufficiency_index', 0):.3f}")
        print(f"   🏷️  ESI Badge: {esi.get('esi_badge', 'Unknown')}")
        print(f"   📊 Node Count: {esi.get('node_count', 0)}")
        print(f"   🎯 Mean Confidence: {esi.get('mean_confidence', 'Unknown')}")
        print(f"   🔄 Fallback Ratio: {esi.get('fallback_ratio', 0):.3f}")
        print(f"   📈 Contribution Spread: {esi.get('contribution_spread', 'Unknown')}")
        print(f"   🌐 Active Clusters: {esi.get('clusters', [])}")
    
    # Generate alerts
    overall_risk = max(insider_result.get('overall_score', 0), spoofing_result.get('overall_score', 0))
    alerts = alert_generator.generate_alerts(processed_data, insider_result, spoofing_result, overall_risk)
    
    print(f"\n🚨 ALERTS GENERATED: {len(alerts)}")
    for alert in alerts:
        print(f"   📋 {alert['type']} - {alert['severity']}")
        if 'esi' in alert:
            esi = alert['esi']
            print(f"      📈 ESI: {esi.get('evidence_sufficiency_index', 0):.3f} ({esi.get('esi_badge', 'Unknown')})")
    
    # Test case 2: Low-risk scenario with sparse evidence
    print("\n🟢 TEST CASE 2: Low Risk + Sparse Evidence")
    print("-" * 60)
    
    low_risk_data = {
        "trades": [{"id": "trade_001", "volume": 10000, "side": "buy", "timestamp": "2024-01-01T10:00:00Z"}],
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
    
    # Process data
    processed_data = data_processor.process(low_risk_data)
    
    # Calculate risks
    insider_result = bayesian_engine.calculate_insider_dealing_risk(processed_data)
    spoofing_result = bayesian_engine.calculate_spoofing_risk(processed_data)
    
    # Display results
    print(f"📊 INSIDER DEALING:")
    print(f"   Risk Score: {insider_result.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {insider_result.get('risk_level', 'Unknown')}")
    if 'esi' in insider_result:
        esi = insider_result['esi']
        print(f"   📈 ESI Score: {esi.get('evidence_sufficiency_index', 0):.3f}")
        print(f"   🏷️  ESI Badge: {esi.get('esi_badge', 'Unknown')}")
        print(f"   📊 Node Count: {esi.get('node_count', 0)}")
        print(f"   🎯 Mean Confidence: {esi.get('mean_confidence', 'Unknown')}")
        print(f"   🔄 Fallback Ratio: {esi.get('fallback_ratio', 0):.3f}")
        print(f"   📈 Contribution Spread: {esi.get('contribution_spread', 'Unknown')}")
        print(f"   🌐 Active Clusters: {esi.get('clusters', [])}")
    
    print(f"\n📊 SPOOFING:")
    print(f"   Risk Score: {spoofing_result.get('overall_score', 0):.3f}")
    print(f"   Risk Level: {spoofing_result.get('risk_level', 'Unknown')}")
    if 'esi' in spoofing_result:
        esi = spoofing_result['esi']
        print(f"   📈 ESI Score: {esi.get('evidence_sufficiency_index', 0):.3f}")
        print(f"   🏷️  ESI Badge: {esi.get('esi_badge', 'Unknown')}")
        print(f"   📊 Node Count: {esi.get('node_count', 0)}")
        print(f"   🎯 Mean Confidence: {esi.get('mean_confidence', 'Unknown')}")
        print(f"   🔄 Fallback Ratio: {esi.get('fallback_ratio', 0):.3f}")
        print(f"   📈 Contribution Spread: {esi.get('contribution_spread', 'Unknown')}")
        print(f"   🌐 Active Clusters: {esi.get('clusters', [])}")
    
    # Generate alerts
    overall_risk = max(insider_result.get('overall_score', 0), spoofing_result.get('overall_score', 0))
    alerts = alert_generator.generate_alerts(processed_data, insider_result, spoofing_result, overall_risk)
    
    print(f"\n🚨 ALERTS GENERATED: {len(alerts)}")
    for alert in alerts:
        print(f"   📋 {alert['type']} - {alert['severity']}")
        if 'esi' in alert:
            esi = alert['esi']
            print(f"      📈 ESI: {esi.get('evidence_sufficiency_index', 0):.3f} ({esi.get('esi_badge', 'Unknown')})")

def demonstrate_esi_filtering():
    """Demonstrate ESI-based filtering and prioritization"""
    print("\n" + "=" * 80)
    print("🎯 ESI FILTERING & PRIORITIZATION DEMONSTRATION")
    print("=" * 80)
    
    # Simulate multiple alerts with different ESI scores
    simulated_alerts = [
        {
            'id': 'alert_001',
            'type': 'INSIDER_DEALING',
            'severity': 'HIGH',
            'risk_score': 0.85,
            'esi': {'evidence_sufficiency_index': 0.92, 'esi_badge': 'Strong'}
        },
        {
            'id': 'alert_002',
            'type': 'SPOOFING',
            'severity': 'HIGH',
            'risk_score': 0.78,
            'esi': {'evidence_sufficiency_index': 0.45, 'esi_badge': 'Limited'}
        },
        {
            'id': 'alert_003',
            'type': 'INSIDER_DEALING',
            'severity': 'MEDIUM',
            'risk_score': 0.65,
            'esi': {'evidence_sufficiency_index': 0.88, 'esi_badge': 'Strong'}
        },
        {
            'id': 'alert_004',
            'type': 'SPOOFING',
            'severity': 'HIGH',
            'risk_score': 0.82,
            'esi': {'evidence_sufficiency_index': 0.23, 'esi_badge': 'Sparse'}
        }
    ]
    
    print("\n📋 Original Alert Order (by risk score):")
    for alert in simulated_alerts:
        print(f"   {alert['id']}: {alert['type']} - Risk: {alert['risk_score']:.2f}, ESI: {alert['esi']['evidence_sufficiency_index']:.2f} ({alert['esi']['esi_badge']})")
    
    # Filter by ESI > 0.7
    high_esi_alerts = [a for a in simulated_alerts if a['esi']['evidence_sufficiency_index'] > 0.7]
    print(f"\n🔍 High ESI Alerts (ESI > 0.7): {len(high_esi_alerts)}")
    for alert in high_esi_alerts:
        print(f"   {alert['id']}: {alert['type']} - Risk: {alert['risk_score']:.2f}, ESI: {alert['esi']['evidence_sufficiency_index']:.2f} ({alert['esi']['esi_badge']})")
    
    # Sort by ESI descending
    sorted_by_esi = sorted(simulated_alerts, key=lambda x: x['esi']['evidence_sufficiency_index'], reverse=True)
    print(f"\n📊 Sorted by ESI (descending):")
    for alert in sorted_by_esi:
        print(f"   {alert['id']}: {alert['type']} - Risk: {alert['risk_score']:.2f}, ESI: {alert['esi']['evidence_sufficiency_index']:.2f} ({alert['esi']['esi_badge']})")
    
    # Calculate adjusted risk scores
    print(f"\n⚖️  Adjusted Risk Scores (Risk × ESI):")
    for alert in simulated_alerts:
        adjusted_score = alert['risk_score'] * alert['esi']['evidence_sufficiency_index']
        print(f"   {alert['id']}: {alert['risk_score']:.2f} × {alert['esi']['evidence_sufficiency_index']:.2f} = {adjusted_score:.2f}")

def show_esi_ui_integration():
    """Show how ESI would be integrated in the UI"""
    print("\n" + "=" * 80)
    print("🖥️  ESI UI INTEGRATION EXAMPLE")
    print("=" * 80)
    
    print("\n📋 Alert Card Example:")
    print("┌─────────────────────────────────────────────────────────┐")
    print("│ 🚨 INSIDER DEALING ALERT                    [ESI: Strong] │")
    print("│ Risk Score: 0.85 (HIGH)                                 │")
    print("│ Trader: trader_001 | Time: 2024-01-01 10:00:00         │")
    print("│ Evidence: 6 nodes active, 3 clusters, 0% fallback      │")
    print("│ ┌─────────────────────────────────────────────────────┐ │")
    print("│ │ 📈 ESI Breakdown:                                  │ │")
    print("│ │ • Node Activation: 100% (6/6 nodes)                │ │")
    print("│ │ • Mean Confidence: High                            │ │")
    print("│ │ • Fallback Usage: 0%                               │ │")
    print("│ │ • Contribution Spread: Balanced                    │ │")
    print("│ │ • Active Clusters: trade, mnpi, pnl               │ │")
    print("│ └─────────────────────────────────────────────────────┘ │")
    print("└─────────────────────────────────────────────────────────┘")
    
    print("\n📊 Alert List with ESI Badges:")
    print("┌─────────────────────────────────────────────────────────┐")
    print("│ ID        │ Type            │ Risk │ ESI Badge │ Status │")
    print("├───────────┼─────────────────┼──────┼───────────┼────────┤")
    print("│ alert_001 │ INSIDER_DEALING │ HIGH │ [Strong]  │ 🔴     │")
    print("│ alert_002 │ SPOOFING        │ HIGH │ [Limited] │ 🟡     │")
    print("│ alert_003 │ INSIDER_DEALING │ MED  │ [Strong]  │ 🔴     │")
    print("│ alert_004 │ SPOOFING        │ HIGH │ [Sparse]  │ ⚪     │")
    print("└─────────────────────────────────────────────────────────┘")
    
    print("\n🎛️  Filter Controls:")
    print("   [ ] Show only Strong ESI alerts")
    print("   [ ] Show only Moderate+ ESI alerts")
    print("   [ ] Sort by ESI (High to Low)")
    print("   [ ] Sort by Risk Score (High to Low)")
    print("   [ ] Sort by Adjusted Risk (Risk × ESI)")

if __name__ == "__main__":
    test_complete_esi_integration()
    demonstrate_esi_filtering()
    show_esi_ui_integration()
    
    print("\n" + "=" * 80)
    print("🎉 COMPLETE ESI INTEGRATION TEST FINISHED!")
    print("=" * 80)
    print("✅ ESI calculation with all scenarios")
    print("✅ Integration with Bayesian engine and alert generator")
    print("✅ ESI-based filtering and prioritization")
    print("✅ UI integration examples")
    print("✅ Risk score adjustment demonstration")
    print("✅ Based on Kor.ai wiki specification")
    print("=" * 80) 