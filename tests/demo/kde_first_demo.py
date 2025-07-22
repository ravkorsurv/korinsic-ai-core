"""
KDE-First Data Quality Framework Demonstration

This demo shows the new 2-tier, 7-dimension KDE-first approach vs the old
dimension-averaged approach. It demonstrates:

1. KDE-specific scoring across dimensions
2. Risk-weighted aggregation
3. Role-aware KDE scope filtering
4. Tier-based weighting (foundational vs enhanced)
5. Synthetic KDE scoring (timeliness, coverage)
"""

import sys
import os
import traceback
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from datetime import datetime, timedelta
from core.kde_first_dq_calculator import KDEFirstDQCalculator
from core.kde_first_role_aware_strategy import KDEFirstRoleAwareStrategy
import json


def create_sample_evidence():
    """Create sample evidence data for demonstration."""
    return {
        # High-risk KDEs
        'trader_id': 'TR123456',
        'notional': 1500000.50,
        'price': 102.75,
        'quantity': 1000,
        'trade_date': datetime.now() - timedelta(hours=2),
        
        # Medium-risk KDEs
        'settlement_date': datetime.now() + timedelta(days=2),
        'product_code': 'USD_BOND_10Y',
        'desk_code': 'RATES_NY',
        'counterparty': 'BANK_ABC',
        
        # Low-risk KDEs
        'currency': 'USD',
        'venue': 'NYSE',
        
        # Additional fields for completeness
        'timestamp': datetime.now() - timedelta(minutes=30),
        'message_id': 'MSG_789',
        'staff_id': 'EMP001'
    }


def create_sample_baseline():
    """Create sample baseline data for coverage calculations."""
    return {
        'volume': 50,  # Normal volume is 50 trades per day
        'value': 75000000,  # Normal value is $75M per day
        'role_analyst': {
            'volume': 30,
            'value': 45000000
        },
        'role_compliance': {
            'volume': 60,
            'value': 90000000
        }
    }


def demo_kde_first_calculator():
    """Demonstrate basic KDE-first calculator."""
    print("=" * 80)
    print("KDE-FIRST DATA QUALITY CALCULATOR DEMONSTRATION")
    print("=" * 80)
    
    # Initialize calculator
    calculator = KDEFirstDQCalculator()
    
    # Sample evidence
    evidence = create_sample_evidence()
    baseline = create_sample_baseline()
    
    print("\n📊 SAMPLE EVIDENCE DATA:")
    print("-" * 40)
    for kde, value in evidence.items():
        risk_level = calculator.config['kde_risk'].get(kde, 'unknown')
        print(f"  {kde:20} = {str(value):20} (risk: {risk_level})")
    
    # Calculate DQSI
    result = calculator.calculate_dqsi(
        evidence=evidence,
        baseline_data=baseline,
        user_role="analyst",
        alert_timestamp=datetime.now()
    )
    
    print(f"\n🎯 DQSI RESULTS:")
    print("-" * 40)
    print(f"  DQSI Score:        {result['dqsi_score']}")
    print(f"  Trust Bucket:      {result['dqsi_trust_bucket']}")
    print(f"  Framework:         {result['dq_framework']}")
    print(f"  KDEs Assessed:     {result['quality_metadata']['total_kdes_assessed']}")
    print(f"  Foundational Score: {result['quality_metadata']['foundational_score']:.3f}")
    print(f"  Enhanced Score:     {result['quality_metadata']['enhanced_score']:.3f}")
    
    print(f"\n📋 KDE SCORES BY DIMENSION:")
    print("-" * 40)
    for kde, scores in result['kde_scores'].items():
        print(f"  {kde}:")
        for dimension, score in scores.items():
            tier = calculator.config['dimension_tiers'][dimension]
            print(f"    {dimension:15} = {score:.3f} (tier: {tier})")
        print()
    
    print(f"\n🔄 SYNTHETIC KDE SCORES:")
    print("-" * 40)
    for synthetic_kde, score in result['synthetic_scores'].items():
        print(f"  {synthetic_kde:15} = {score:.3f}")
    
    print(f"\n📈 DIMENSION SUMMARY:")
    print("-" * 40)
    for dimension, stats in result['dimension_summary'].items():
        print(f"  {dimension:15} = avg:{stats['average']:.3f}, min:{stats['min']:.3f}, max:{stats['max']:.3f}")
    
    return result


def demo_role_aware_strategy():
    """Demonstrate role-aware strategy with different user roles."""
    print("\n" + "=" * 80)
    print("ROLE-AWARE STRATEGY DEMONSTRATION")
    print("=" * 80)
    
    strategy = KDEFirstRoleAwareStrategy()
    evidence = create_sample_evidence()
    baseline = create_sample_baseline()
    
    roles_to_test = ['analyst', 'compliance', 'trader_role', 'auditor']
    
    for role in roles_to_test:
        print(f"\n👤 ROLE: {role.upper()}")
        print("-" * 50)
        
        result = strategy.calculate_dq_score(
            evidence=evidence,
            baseline_data=baseline,
            user_role=role,
            alert_timestamp=datetime.now()
        )
        
        role_meta = result['role_metadata']
        role_validation = result['role_validation']
        
        print(f"  DQSI Score:          {result['dqsi_score']}")
        print(f"  Trust Bucket:        {result['dqsi_trust_bucket']}")
        print(f"  KDEs in Scope:       {len(role_meta['role_kde_scope'])}")
        print(f"  KDEs Assessed:       {len(result['applicable_kdes'])}")
        print(f"  Scope Coverage:      {role_meta['scope_coverage']:.1%}")
        print(f"  Completeness Level:  {role_meta['assessment_completeness']['completeness_level']}")
        print(f"  Role Compliant:      {role_validation['compliant']}")
        print(f"  Overall Assessment:  {role_validation['overall_assessment']}")
        
        # Show missing KDEs if any
        if role_meta['missing_kdes']:
            print(f"  Missing KDEs:        {', '.join(role_meta['missing_kdes'])}")


def demo_dimension_scoring():
    """Demonstrate how different dimensions are scored."""
    print("\n" + "=" * 80)
    print("DIMENSION SCORING DEMONSTRATION")
    print("=" * 80)
    
    calculator = KDEFirstDQCalculator()
    
    # Test different data quality scenarios
    scenarios = {
        'perfect_data': {
            'trader_id': 'TR123456',
            'notional': 1000000.00,
            'price': 100.5000,
            'currency': 'USD'
        },
        'incomplete_data': {
            'trader_id': 'TR123456',
            'notional': None,  # Missing value
            'price': 100.5000,
            'currency': 'USD'
        },
        'non_conformant_data': {
            'trader_id': 'X',  # Too short
            'notional': -1000000.00,  # Negative (invalid range)
            'price': 100.50001234,  # Too many decimal places
            'currency': 'DOLLAR'  # Wrong format
        },
        'mixed_quality_data': {
            'trader_id': 'TR123456',  # Good
            'notional': 1000000.00,  # Good
            'price': None,  # Missing
            'currency': 'USD'  # Good
        }
    }
    
    for scenario_name, evidence in scenarios.items():
        print(f"\n📊 SCENARIO: {scenario_name.upper()}")
        print("-" * 50)
        
        result = calculator.calculate_dqsi(
            evidence=evidence,
            user_role="analyst"
        )
        
        print(f"  Overall DQSI Score: {result['dqsi_score']}")
        print(f"  Trust Bucket:       {result['dqsi_trust_bucket']}")
        
        print("  \nKDE Dimension Scores:")
        for kde, scores in result['kde_scores'].items():
            kde_risk = calculator.config['kde_risk'].get(kde, 'medium')
            print(f"    {kde} (risk: {kde_risk}):")
            for dimension, score in scores.items():
                print(f"      {dimension:12} = {score:.3f}")


def demo_weighting_impact():
    """Demonstrate the impact of risk and tier weighting."""
    print("\n" + "=" * 80)
    print("WEIGHTING IMPACT DEMONSTRATION")
    print("=" * 80)
    
    calculator = KDEFirstDQCalculator()
    
    # Sample evidence with known quality issues
    evidence = {
        'trader_id': 'TR123456',     # High risk, good quality
        'notional': None,            # High risk, poor quality (missing)
        'product_code': 'BOND_10Y',  # Medium risk, good quality
        'currency': 'USD',           # Low risk, good quality
        'venue': None                # Low risk, poor quality (missing)
    }
    
    # Create sample baseline data for consistent parameter usage
    def create_sample_baseline():
        return {
            'trade_count': 1000,
            'avg_volume': 50000,
            'price_volatility': 0.02,
            'market_conditions': 'normal'
        }
    
    result = calculator.calculate_dqsi(
        evidence=evidence,
        baseline_data=create_sample_baseline(),
        user_role="analyst",
        alert_timestamp=datetime.now()
    )
    
    print("📊 WEIGHTING ANALYSIS:")
    print("-" * 40)
    print(f"Overall DQSI Score: {result['dqsi_score']}")
    print(f"Trust Bucket: {result['dqsi_trust_bucket']}")
    
    print("\n📋 KDE IMPACT ANALYSIS:")
    print("-" * 40)
    
    # Show how each KDE contributes to final score
    for kde_name, dimension_scores in result['kde_scores'].items():
        kde_risk = calculator.config['kde_risk'].get(kde_name, 'medium')
        risk_weight = calculator.config['risk_weights'][kde_risk]
        
        print(f"\n  {kde_name} (risk: {kde_risk}, weight: {risk_weight}):")
        for dimension, score in dimension_scores.items():
            tier = calculator.config['dimension_tiers'][dimension]
            tier_weight = calculator.config['tier_weights'][tier]
            weighted_contribution = score * risk_weight * tier_weight
            print(f"    {dimension:12} = {score:.3f} × {risk_weight} × {tier_weight:.2f} = {weighted_contribution:.3f}")
    
    print(f"\n🔄 SYNTHETIC KDE CONTRIBUTIONS:")
    print("-" * 40)
    synthetic_weight = calculator.config['synthetic_kde_weight']
    for synthetic_name, score in result['synthetic_scores'].items():
        tier_weight = calculator.config['tier_weights']['foundational']
        weighted_contribution = score * synthetic_weight * tier_weight
        print(f"  {synthetic_name:12} = {score:.3f} × {synthetic_weight} × {tier_weight:.2f} = {weighted_contribution:.3f}")
    
    print(f"\n📈 TIER BREAKDOWN:")
    print("-" * 40)
    breakdown = result['score_breakdown']
    print(f"  Foundational Score:   {breakdown['foundational_weighted_score']:.3f}")
    print(f"  Enhanced Score:       {breakdown['enhanced_weighted_score']:.3f}")
    print(f"  Foundational %:       {breakdown['foundational_contribution']:.1f}%")
    print(f"  Enhanced %:           {breakdown['enhanced_contribution']:.1f}%")


def main():
    """Run all demonstrations."""
    print("🚀 KDE-FIRST DATA QUALITY FRAMEWORK DEMO")
    print("=" * 80)
    print("This demonstration shows the new 2-tier, 7-dimension framework")
    print("that replaces the old 5-dimension averaged approach.")
    print()
    
    try:
        # Run demonstrations
        demo_kde_first_calculator()
        demo_role_aware_strategy()
        demo_dimension_scoring()
        demo_weighting_impact()
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("Key benefits of the new KDE-first approach:")
        print("• More granular quality assessment per KDE")
        print("• Risk-based weighting respects business criticality")
        print("• Tier-based scoring balances foundational vs enhanced quality")
        print("• Role-aware scope filtering provides relevant assessments")
        print("• Synthetic KDEs capture system-level quality metrics")
        print("• Backward compatibility with trust bucket categorization")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()