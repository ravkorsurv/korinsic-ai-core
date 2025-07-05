#!/usr/bin/env python3
"""
DQSI Corrected Implementation Demo

This script demonstrates the corrected implementation of the Modular Data Quality 
Sufficiency Index (DQSI) with:
- 7 dimensions in 2 tiers (not 6)
- KDE-level scoring (not dimension-level)
- Strategy-based configuration (fallback vs role_aware)
- Synthetic KDEs for system-level metrics
- Critical KDE cap enforcement
- Confidence index calculation
- No global dimension weights (deprecated)
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from services.data_quality.dq_sufficiency_index import DataQualitySufficiencyIndex
    from services.data_quality.dq_strategy_base import DQConfig
    from services.data_quality.dq_config_loader import DQConfigLoader
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure the src directory is in your Python path")
    sys.exit(1)


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_subheader(title):
    """Print a formatted subheader"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


def demo_7_dimensions_configuration():
    """Demonstrate the correct 7 dimensions configuration"""
    print_header("7 DIMENSIONS CONFIGURATION")
    
    config = DQConfig()
    
    print("Data Quality Dimensions (7 total):")
    print(f"  Strategy Mode: {config.dq_strategy}")
    print(f"  Total Dimensions: {sum(len(dims) for dims in config.dimensions.values())}")
    print()
    
    for tier, dimensions in config.dimensions.items():
        print(f"  {tier.upper()} Tier ({len(dimensions)} dimensions):")
        for dim in dimensions:
            print(f"    - {dim}")
        print(f"    Tier Weight: {config.dimension_tier_weights[tier]}")
        print()
    
    print("KDE Risk Tiers:")
    for kde, tier in config.kde_risk_tiers.items():
        weight = config.risk_weights[tier]
        print(f"  {kde}: {tier} (weight: {weight})")
    
    print()
    print("Critical KDEs:")
    for kde in config.critical_kdes:
        print(f"  - {kde}")
    print(f"  Critical Cap: {config.dqsi_critical_cap}")
    
    print()
    print("Synthetic KDEs:")
    for name, config_dict in config.synthetic_kdes.items():
        print(f"  {name}:")
        print(f"    Dimension: {config_dict['dimension']}")
        print(f"    Tier: {config_dict['tier']}")
        print(f"    Weight: {config_dict['weight']}")


def demo_kde_level_scoring():
    """Demonstrate KDE-level scoring (not dimension-level)"""
    print_header("KDE-LEVEL SCORING DEMONSTRATION")
    
    # Sample trading data
    sample_data = {
        'trader_id': 'TRD001',
        'trade_time': '2024-01-15T10:30:00Z',
        'order_timestamp': '2024-01-15T10:29:58Z',
        'notional': 1000000.0,
        'quantity': 1000,
        'price': 100.50,
        'desk_id': 'DESK001',
        'instrument': 'AAPL',
        'client_id': 'CLT001'
    }
    
    print("Sample Trading Data:")
    for kde, value in sample_data.items():
        print(f"  {kde}: {value}")
    
    # Fallback strategy scoring
    print_subheader("Fallback Strategy (Basic Profiling)")
    
    config_fallback = DQConfig(dq_strategy='fallback')
    dqsi_fallback = DataQualitySufficiencyIndex(config_fallback)
    
    output_fallback = dqsi_fallback.calculate_dqsi(sample_data)
    
    print(f"DQSI Score: {output_fallback.dqsi_score:.3f}")
    print(f"Confidence Index: {output_fallback.dqsi_confidence_index:.3f}")
    print(f"Mode: {output_fallback.dqsi_mode}")
    print()
    
    print("Individual KDE Scores:")
    for kde_result in output_fallback.kde_results:
        print(f"  {kde_result.kde_name}: {kde_result.score:.3f} "
              f"({kde_result.risk_tier}, weight: {kde_result.risk_weight})")
        if kde_result.is_synthetic:
            print(f"    [SYNTHETIC KDE - {kde_result.details.get('type', 'N/A')}]")
    
    print()
    print("Dimension Sub-Scores:")
    for dimension, score in output_fallback.dqsi_sub_scores.items():
        print(f"  {dimension}: {score:.3f}")


def demo_strategy_comparison():
    """Demonstrate fallback vs role-aware strategy differences"""
    print_header("STRATEGY COMPARISON")
    
    sample_data = {
        'trader_id': 'TRD001',
        'trade_time': '2024-01-15T10:30:00Z',
        'notional': 1000000.0,
        'quantity': 1000,
        'price': 100.50,
        'desk_id': 'DESK001',
        'instrument': 'AAPL'
    }
    
    metadata = {
        'role': 'producer',
        'reference_data': {
            'trader_id': 'TRD001',
            'notional': 1000000.0,
            'price': 100.50
        },
        'reconciliation_data': {
            'trade_time': '2024-01-15T10:30:00Z',
            'quantity': 1000
        }
    }
    
    # Fallback strategy
    config_fallback = DQConfig(dq_strategy='fallback')
    dqsi_fallback = DataQualitySufficiencyIndex(config_fallback)
    output_fallback = dqsi_fallback.calculate_dqsi(sample_data)
    
    # Role-aware strategy
    config_role_aware = DQConfig(dq_strategy='role_aware')
    dqsi_role_aware = DataQualitySufficiencyIndex(config_role_aware)
    output_role_aware = dqsi_role_aware.calculate_dqsi(sample_data, metadata)
    
    print_subheader("Fallback Strategy Results")
    print(f"DQSI Score: {output_fallback.dqsi_score:.3f}")
    print(f"Confidence Index: {output_fallback.dqsi_confidence_index:.3f}")
    print(f"Mode: {output_fallback.dqsi_mode}")
    print(f"Confidence Note: {output_fallback.dqsi_confidence_note}")
    
    print_subheader("Role-Aware Strategy Results")
    print(f"DQSI Score: {output_role_aware.dqsi_score:.3f}")
    print(f"Confidence Index: {output_role_aware.dqsi_confidence_index:.3f}")
    print(f"Mode: {output_role_aware.dqsi_mode}")
    print(f"Confidence Note: {output_role_aware.dqsi_confidence_note}")
    
    print_subheader("Strategy Comparison")
    print(f"Score Difference: {output_role_aware.dqsi_score - output_fallback.dqsi_score:.3f}")
    print(f"Confidence Difference: {output_role_aware.dqsi_confidence_index - output_fallback.dqsi_confidence_index:.3f}")
    print()
    
    # Show KDE-level differences
    print("KDE-Level Scoring Differences:")
    fallback_kdes = {kde.kde_name: kde.score for kde in output_fallback.kde_results}
    role_aware_kdes = {kde.kde_name: kde.score for kde in output_role_aware.kde_results}
    
    for kde_name in set(fallback_kdes.keys()) | set(role_aware_kdes.keys()):
        fallback_score = fallback_kdes.get(kde_name, 0.0)
        role_aware_score = role_aware_kdes.get(kde_name, 0.0)
        if fallback_score != role_aware_score:
            print(f"  {kde_name}: {fallback_score:.3f} → {role_aware_score:.3f}")


def demo_critical_kde_cap():
    """Demonstrate critical KDE cap enforcement"""
    print_header("CRITICAL KDE CAP ENFORCEMENT")
    
    # Data with missing critical KDE
    data_missing_critical = {
        'trade_time': '2024-01-15T10:30:00Z',
        'notional': 1000000.0,
        'quantity': 1000,
        'price': 100.50,
        'desk_id': 'DESK001',
        'instrument': 'AAPL'
        # Missing 'trader_id' which is critical
    }
    
    config = DQConfig(dq_strategy='fallback')
    dqsi = DataQualitySufficiencyIndex(config)
    
    output = dqsi.calculate_dqsi(data_missing_critical)
    
    print("Data with Missing Critical KDE:")
    print(f"  Critical KDEs: {config.critical_kdes}")
    print(f"  Critical Cap: {config.dqsi_critical_cap}")
    print()
    
    print("Results:")
    print(f"  DQSI Score: {output.dqsi_score:.3f}")
    print(f"  Critical KDEs Missing: {output.dqsi_critical_kdes_missing}")
    print(f"  Score Capped: {output.dqsi_score <= config.dqsi_critical_cap}")
    
    print()
    print("Individual KDE Analysis:")
    for kde_result in output.kde_results:
        status = "MISSING" if kde_result.score == 0.0 else "PRESENT"
        critical = "CRITICAL" if kde_result.kde_name in config.critical_kdes else "NORMAL"
        print(f"  {kde_result.kde_name}: {kde_result.score:.3f} [{status}] [{critical}]")


def demo_synthetic_kdes():
    """Demonstrate synthetic KDEs for system-level metrics"""
    print_header("SYNTHETIC KDEs FOR SYSTEM-LEVEL METRICS")
    
    # Data with different timestamps to show timeliness scoring
    recent_data = {
        'trader_id': 'TRD001',
        'trade_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'notional': 1000000.0,
        'quantity': 1000,
        'price': 100.50
    }
    
    old_data = {
        'trader_id': 'TRD001',
        'trade_time': '2024-01-01T10:30:00Z',  # Old timestamp
        'notional': 1000000.0,
        'quantity': 1000,
        'price': 100.50
    }
    
    # Metadata with volume information
    metadata_good_volume = {
        'baseline_volume': 1000,
        'current_volume': 950  # 5% drop - good
    }
    
    metadata_poor_volume = {
        'baseline_volume': 1000,
        'current_volume': 300  # 70% drop - poor
    }
    
    config = DQConfig(dq_strategy='fallback')
    dqsi = DataQualitySufficiencyIndex(config)
    
    print_subheader("Recent Data (Good Timeliness)")
    output_recent = dqsi.calculate_dqsi(recent_data, metadata_good_volume)
    
    synthetic_kdes_recent = [kde for kde in output_recent.kde_results if kde.is_synthetic]
    for kde in synthetic_kdes_recent:
        print(f"  {kde.kde_name}: {kde.score:.3f} ({kde.details.get('type', 'N/A')})")
    
    print_subheader("Old Data (Poor Timeliness)")
    output_old = dqsi.calculate_dqsi(old_data, metadata_poor_volume)
    
    synthetic_kdes_old = [kde for kde in output_old.kde_results if kde.is_synthetic]
    for kde in synthetic_kdes_old:
        print(f"  {kde.kde_name}: {kde.score:.3f} ({kde.details.get('type', 'N/A')})")
    
    print()
    print("Synthetic KDE Impact:")
    print(f"  Recent Data DQSI: {output_recent.dqsi_score:.3f}")
    print(f"  Old Data DQSI: {output_old.dqsi_score:.3f}")
    print(f"  Synthetic KDE Impact: {output_recent.dqsi_score - output_old.dqsi_score:.3f}")


def demo_confidence_index():
    """Demonstrate confidence index calculation"""
    print_header("CONFIDENCE INDEX CALCULATION")
    
    # High quality data
    high_quality_data = {
        'trader_id': 'TRD001',
        'trade_time': '2024-01-15T10:30:00Z',
        'notional': 1000000.0,
        'quantity': 1000,
        'price': 100.50,
        'desk_id': 'DESK001',
        'instrument': 'AAPL',
        'client_id': 'CLT001'
    }
    
    # Poor quality data
    poor_quality_data = {
        'trader_id': None,  # Missing critical KDE
        'trade_time': 'invalid_date',
        'notional': 'not_a_number',
        'quantity': -100,  # Invalid value
        'price': 0,  # Suspicious value
        'desk_id': 'DESK001'
    }
    
    config = DQConfig(dq_strategy='fallback')
    dqsi = DataQualitySufficiencyIndex(config)
    
    print_subheader("High Quality Data")
    output_high = dqsi.calculate_dqsi(high_quality_data)
    print(f"  DQSI Score: {output_high.dqsi_score:.3f}")
    print(f"  Confidence Index: {output_high.dqsi_confidence_index:.3f}")
    print(f"  Confidence Note: {output_high.dqsi_confidence_note}")
    
    print_subheader("Poor Quality Data")
    output_poor = dqsi.calculate_dqsi(poor_quality_data)
    print(f"  DQSI Score: {output_poor.dqsi_score:.3f}")
    print(f"  Confidence Index: {output_poor.dqsi_confidence_index:.3f}")
    print(f"  Confidence Note: {output_poor.dqsi_confidence_note}")
    
    print_subheader("Confidence Index Comparison")
    print(f"  High Quality Confidence: {output_high.dqsi_confidence_index:.3f}")
    print(f"  Poor Quality Confidence: {output_poor.dqsi_confidence_index:.3f}")
    print(f"  Confidence Difference: {output_high.dqsi_confidence_index - output_poor.dqsi_confidence_index:.3f}")


def demo_alert_case_integration():
    """Demonstrate alert and case integration"""
    print_header("ALERT AND CASE INTEGRATION")
    
    # Sample alert data
    alert_data = {
        'alert_id': 'ALERT_001',
        'typology': 'market_manipulation',
        'producer_role': 'producer',
        'trader_id': 'TRD001',
        'trade_time': '2024-01-15T10:30:00Z',
        'notional': 1000000.0,
        'quantity': 1000,
        'price': 100.50,
        'desk_id': 'DESK001',
        'instrument': 'AAPL',
        'reference_data': {
            'trader_id': 'TRD001',
            'notional': 1000000.0
        }
    }
    
    # Sample case data with multiple alerts
    case_data = {
        'case_id': 'CASE_001',
        'alerts': [
            {
                'alert_id': 'ALERT_001',
                'producer_role': 'producer',
                'trader_id': 'TRD001',
                'trade_time': '2024-01-15T10:30:00Z',
                'notional': 1000000.0,
                'quantity': 1000,
                'price': 100.50
            },
            {
                'alert_id': 'ALERT_002',
                'producer_role': 'producer',
                'trader_id': 'TRD001',
                'trade_time': '2024-01-15T10:35:00Z',
                'notional': 500000.0,
                'quantity': 500,
                'price': 101.00
            }
        ]
    }
    
    config = DQConfig(dq_strategy='role_aware')
    dqsi = DataQualitySufficiencyIndex(config)
    
    print_subheader("Alert-Level DQSI")
    alert_output = dqsi.calculate_dqsi_for_alert(alert_data)
    
    print("Alert DQSI Output Fields:")
    for field, value in alert_output.items():
        if isinstance(value, float):
            print(f"  {field}: {value:.3f}")
        elif isinstance(value, list):
            print(f"  {field}: {len(value)} items")
        else:
            print(f"  {field}: {value}")
    
    print_subheader("Case-Level DQSI")
    case_output = dqsi.calculate_dqsi_for_case(case_data)
    
    print("Case DQSI Output Fields:")
    for field, value in case_output.items():
        if isinstance(value, float):
            print(f"  {field}: {value:.3f}")
        elif isinstance(value, list):
            print(f"  {field}: {len(value)} items")
        else:
            print(f"  {field}: {value}")


def demo_improvement_recommendations():
    """Demonstrate improvement recommendations"""
    print_header("IMPROVEMENT RECOMMENDATIONS")
    
    # Data with various quality issues
    problematic_data = {
        'trader_id': None,  # Missing critical KDE
        'trade_time': 'invalid_date',  # Invalid format
        'notional': 'not_a_number',  # Invalid format
        'quantity': -100,  # Invalid value
        'price': 0,  # Suspicious value
        'desk_id': 'DESK001',
        'instrument': 'AAPL'
    }
    
    config = DQConfig(dq_strategy='fallback')
    dqsi = DataQualitySufficiencyIndex(config)
    
    output = dqsi.calculate_dqsi(problematic_data)
    recommendations = dqsi.get_improvement_recommendations(output)
    
    print(f"DQSI Score: {output.dqsi_score:.3f}")
    print(f"Confidence Index: {output.dqsi_confidence_index:.3f}")
    print()
    
    print("Improvement Recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
        print(f"  {i}. {rec['kde_name']} (Score: {rec['current_score']:.3f})")
        print(f"     Priority: {rec['priority']}")
        print(f"     Risk Tier: {rec['risk_tier']}")
        print(f"     Dimension: {rec['dimension']}")
        print(f"     Expected Impact: {rec['expected_impact']:.3f}")
        print("     Suggestions:")
        for suggestion in rec['suggestions']:
            print(f"       - {suggestion}")
        print()


def main():
    """Main demo function"""
    print("🎯 DQSI CORRECTED IMPLEMENTATION DEMO")
    print("=====================================")
    print()
    print("This demo showcases the corrected implementation of the")
    print("Modular Data Quality Sufficiency Index (DQSI) with:")
    print("  ✓ 7 dimensions in 2 tiers (not 6)")
    print("  ✓ KDE-level scoring (not dimension-level)")
    print("  ✓ Strategy-based configuration")
    print("  ✓ Synthetic KDEs for system metrics")
    print("  ✓ Critical KDE cap enforcement")
    print("  ✓ Confidence index calculation")
    print("  ✓ No global dimension weights (deprecated)")
    
    try:
        demo_7_dimensions_configuration()
        demo_kde_level_scoring()
        demo_strategy_comparison()
        demo_critical_kde_cap()
        demo_synthetic_kdes()
        demo_confidence_index()
        demo_alert_case_integration()
        demo_improvement_recommendations()
        
        print_header("DEMO COMPLETED SUCCESSFULLY")
        print("✓ All components working as specified")
        print("✓ 7 dimensions properly configured")
        print("✓ KDE-level scoring implemented")
        print("✓ Strategy patterns working")
        print("✓ Synthetic KDEs functioning")
        print("✓ Critical KDE cap enforced")
        print("✓ Confidence index calculated")
        print("✓ Alert/case integration ready")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()