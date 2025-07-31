#!/usr/bin/env python3
"""
Evidence Chain Example - Regulatory Explainability System

This example demonstrates how the regulatory explainability system creates
a comprehensive evidence chain for a person-centric insider dealing alert.

Scenario: John Smith (PersonID: person_12345678) suspected of insider dealing
across multiple linked accounts before a major earnings announcement.

SECURITY NOTE: This example uses secure data handling with proper authorization
and sanitization for sensitive regulatory evidence.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from src.core.evidence.evidence_types import EvidenceType, RegulatoryFramework
    from src.core.security.data_sanitizer import secure_print_evidence
    from src.core.reporting.narrative_generator import NarrativeGenerator, OptimizedOutputFormatter
    REAL_IMPORTS = True
except ImportError:
    # Fallback to mock classes for standalone execution
    from enum import Enum
    
    class EvidenceType(Enum):
        TRADING_PATTERN = "trading_pattern"
        TIMING_ANOMALY = "timing_anomaly"
        COMMUNICATION = "communication"
        CROSS_ACCOUNT_CORRELATION = "cross_account_correlation"

    class RegulatoryFramework(Enum):
        MAR_ARTICLE_8 = "mar_article_8"
        STOR_REQUIREMENTS = "stor_requirements"
    
    REAL_IMPORTS = False

def create_evidence_chain_example():
    """
    Create a comprehensive evidence chain example for insider dealing detection.
    
    This shows the complete audit trail from individual evidence items to
    cross-account patterns and regulatory conclusions.
    """
    
    # Base timestamp for the scenario (2 days before earnings announcement)
    base_time = datetime(2025, 1, 10, 9, 30, 0)  # Market open
    earnings_announcement = datetime(2025, 1, 12, 16, 0, 0)  # After market close
    
    # Person and account information
    person_info = {
        "person_id": "person_12345678",
        "person_name": "John Smith",
        "linked_accounts": ["ACC_JS_001", "ACC_JS_002", "ACC_SPOUSE_003"],
        "employment": "Senior Financial Analyst at TechCorp Inc.",
        "access_level": "Material Non-Public Information"
    }
    
    # Evidence chain - chronological sequence of evidence items
    evidence_chain = [
        {
            "sequence_id": 1,
            "evidence_type": EvidenceType.COMMUNICATION.value if REAL_IMPORTS else "communication",
            "timestamp": (base_time - timedelta(hours=2)).isoformat(),
            "account_id": "ACC_JS_001",
            "evidence_category": "communication_pattern",
            "strength": 0.85,
            "reliability": 0.90,
            "description": "Unusual communication pattern detected: 15 internal calls to IR department 2 hours before trading activity",
            "regulatory_frameworks": [RegulatoryFramework.MAR_ARTICLE_8.value if REAL_IMPORTS else "mar_article_8"],
            "raw_data": {
                "communication_type": "internal_calls",
                "call_count": 15,
                "departments_contacted": ["investor_relations", "finance", "legal"],
                "call_duration_total_minutes": 127,
                "timing_before_trades": "2 hours",
                "participants": ["john.smith@techcorp.com", "ir.team@techcorp.com"]
            },
            "cross_references": [1, 3] if REAL_IMPORTS else ["evidence_2", "evidence_4"]  # Use indices for O(1) lookup
        },
        {
            "sequence_id": 2,
            "evidence_type": "timing_anomaly",
            "timestamp": base_time.isoformat(),
            "account_id": "ACC_JS_001",
            "evidence_category": "timing_anomaly",
            "strength": 0.92,
            "reliability": 0.88,
            "description": "Highly suspicious timing: Large position initiated exactly 48 hours before earnings announcement",
            "regulatory_frameworks": ["mar_article_8", "stor_requirements"],
            "raw_data": {
                "hours_before_announcement": 48,
                "position_size_usd": 2850000,
                "historical_pattern_deviation": 4.2,  # Standard deviations from normal
                "timing_precision_score": 0.96,
                "market_context": "pre_earnings_quiet_period"
            },
            "cross_references": ["evidence_1", "evidence_3", "evidence_5"]
        },
        {
            "sequence_id": 3,
            "evidence_type": "trading_pattern",
            "timestamp": (base_time + timedelta(minutes=15)).isoformat(),
            "account_id": "ACC_JS_001",
            "evidence_category": "trading_pattern",
            "strength": 0.89,
            "reliability": 0.85,
            "description": "Abnormal trading pattern: 340% increase in position size compared to historical average",
            "regulatory_frameworks": ["mar_article_8", "stor_requirements"],
            "raw_data": {
                "position_increase_percentage": 340,
                "historical_average_position": 425000,
                "current_position": 1870000,
                "instrument": "TECHCORP_COMMON_STOCK",
                "order_pattern": "aggressive_accumulation",
                "price_impact": "minimal_due_to_iceberg_orders",
                "order_types": ["iceberg", "hidden", "limit"]
            },
            "cross_references": ["evidence_2", "evidence_4", "evidence_6"]
        },
        {
            "sequence_id": 4,
            "evidence_type": "cross_account_correlation",
            "timestamp": (base_time + timedelta(minutes=30)).isoformat(),
            "account_id": "ACC_JS_002",
            "evidence_category": "cross_account_correlation",
            "strength": 0.94,
            "reliability": 0.91,
            "description": "Strong cross-account correlation: Secondary account initiated similar position 30 minutes after primary account",
            "regulatory_frameworks": ["mar_article_8", "stor_requirements"],
            "raw_data": {
                "correlation_coefficient": 0.94,
                "time_lag_minutes": 30,
                "position_size_correlation": 0.89,
                "order_pattern_similarity": 0.92,
                "accounts_involved": ["ACC_JS_001", "ACC_JS_002"],
                "coordination_probability": 0.87
            },
            "cross_references": ["evidence_1", "evidence_3", "evidence_7"]
        },
        {
            "sequence_id": 5,
            "evidence_type": "timing_anomaly",
            "timestamp": (base_time + timedelta(hours=1)).isoformat(),
            "account_id": "ACC_SPOUSE_003",
            "evidence_category": "timing_anomaly",
            "strength": 0.78,
            "reliability": 0.82,
            "description": "Family account timing anomaly: Spouse account purchased same security 1 hour after primary trades",
            "regulatory_frameworks": ["mar_article_8"],
            "raw_data": {
                "family_relationship": "spouse",
                "time_lag_after_primary": 60,  # minutes
                "position_size": 450000,
                "same_security": True,
                "historical_trading_frequency": "rare",
                "account_holder": "Sarah Smith"
            },
            "cross_references": ["evidence_2", "evidence_6", "evidence_8"]
        },
        {
            "sequence_id": 6,
            "evidence_type": "trading_pattern",
            "timestamp": (base_time + timedelta(hours=2)).isoformat(),
            "account_id": "ACC_JS_002",
            "evidence_category": "trading_pattern",
            "strength": 0.86,
            "reliability": 0.84,
            "description": "Coordinated trading pattern: Options strategy implemented across accounts suggesting sophisticated planning",
            "regulatory_frameworks": ["mar_article_8", "stor_requirements"],
            "raw_data": {
                "strategy_type": "protective_collar",
                "options_volume": 850,
                "underlying_position": 1870000,
                "sophistication_score": 0.91,
                "implementation_precision": 0.88,
                "accounts_coordinated": ["ACC_JS_001", "ACC_JS_002"]
            },
            "cross_references": ["evidence_3", "evidence_4", "evidence_7"]
        },
        {
            "sequence_id": 7,
            "evidence_type": "cross_account_correlation",
            "timestamp": (base_time + timedelta(hours=3)).isoformat(),
            "account_id": "ALL_ACCOUNTS",
            "evidence_category": "cross_account_pattern",
            "strength": 0.91,
            "reliability": 0.89,
            "description": "Multi-account coordination pattern: All three linked accounts show synchronized trading behavior with high correlation",
            "regulatory_frameworks": ["mar_article_8", "stor_requirements"],
            "raw_data": {
                "accounts_in_pattern": ["ACC_JS_001", "ACC_JS_002", "ACC_SPOUSE_003"],
                "overall_correlation": 0.91,
                "temporal_synchronization": 0.87,
                "position_size_coordination": 0.83,
                "total_exposure": 3170000,
                "pattern_complexity": "high"
            },
            "cross_references": ["evidence_4", "evidence_5", "evidence_6"]
        },
        {
            "sequence_id": 8,
            "evidence_type": "timing_anomaly",
            "timestamp": earnings_announcement.isoformat(),
            "account_id": "ALL_ACCOUNTS",
            "evidence_category": "outcome_correlation",
            "strength": 0.96,
            "reliability": 0.93,
            "description": "Perfect timing correlation: Earnings announcement resulted in 23% stock price increase, validating insider information theory",
            "regulatory_frameworks": ["mar_article_8", "stor_requirements"],
            "raw_data": {
                "stock_price_increase": 23.4,
                "unrealized_gains": 741380,
                "announcement_impact": "strongly_positive",
                "market_surprise_factor": 0.89,
                "information_value_confirmation": 0.96,
                "timing_precision_validation": 0.94
            },
            "cross_references": ["evidence_2", "evidence_5", "evidence_7"]
        }
    ]
    
    return {
        "person_info": person_info,
        "evidence_chain": evidence_chain,
        "scenario_summary": {
            "alert_type": "insider_dealing",
            "detection_confidence": 0.91,
            "stor_eligible": True,
            "regulatory_frameworks_triggered": ["MAR Article 8", "STOR Requirements"],
            "total_evidence_items": len(evidence_chain),
            "evidence_time_span_hours": 51,
            "accounts_involved": 3,
            "total_financial_exposure": 3170000,
            "unrealized_gains": 741380
        }
    }

def generate_regulatory_narrative(evidence_data: Dict[str, Any]) -> str:
    """
    Generate human-readable regulatory narrative from evidence chain.
    
    This shows how the evidence chain translates into regulatory reporting.
    """
    
    person = evidence_data["person_info"]
    chain = evidence_data["evidence_chain"]
    summary = evidence_data["scenario_summary"]
    
    narrative = f"""
REGULATORY EXPLAINABILITY REPORT
================================

Person Under Investigation: {person['person_name']} (ID: {person['person_id']})
Risk Typology: Insider Dealing (MAR Article 8)
Alert Confidence: {summary['detection_confidence']:.1%}
STOR Eligible: {'Yes' if summary['stor_eligible'] else 'No'}

EXECUTIVE SUMMARY:
The surveillance system has detected a high-probability insider dealing pattern involving 
{person['person_name']}, a {person['employment']} with {person['access_level']} access. 
The evidence shows coordinated trading across {summary['accounts_involved']} linked accounts 
with total exposure of ${summary['total_financial_exposure']:,} initiated exactly 48 hours 
before a material earnings announcement.

EVIDENCE CHAIN ANALYSIS:
========================

The following evidence items form a compelling chain of suspicious activity:

1. COMMUNICATION PATTERN (Strength: {chain[0]['strength']:.2f})
   Time: {chain[0]['timestamp']}
   Account: {chain[0]['account_id']}
   Evidence: {chain[0]['description']}
   Regulatory Significance: Demonstrates potential access to material non-public information

2. TIMING ANOMALY (Strength: {chain[1]['strength']:.2f})
   Time: {chain[1]['timestamp']}
   Account: {chain[1]['account_id']}
   Evidence: {chain[1]['description']}
   Regulatory Significance: Highly suspicious timing suggests advance knowledge

3. TRADING PATTERN (Strength: {chain[2]['strength']:.2f})
   Time: {chain[2]['timestamp']}
   Account: {chain[2]['account_id']}
   Evidence: {chain[2]['description']}
   Regulatory Significance: Abnormal position size indicates confidence in outcome

4. CROSS-ACCOUNT CORRELATION (Strength: {chain[3]['strength']:.2f})
   Time: {chain[3]['timestamp']}
   Account: {chain[3]['account_id']}
   Evidence: {chain[3]['description']}
   Regulatory Significance: Coordination across accounts suggests deliberate strategy

5. FAMILY ACCOUNT INVOLVEMENT (Strength: {chain[4]['strength']:.2f})
   Time: {chain[4]['timestamp']}
   Account: {chain[4]['account_id']}
   Evidence: {chain[4]['description']}
   Regulatory Significance: Family member involvement indicates information sharing

6. SOPHISTICATED STRATEGY (Strength: {chain[5]['strength']:.2f})
   Time: {chain[5]['timestamp']}
   Account: {chain[5]['account_id']}
   Evidence: {chain[5]['description']}
   Regulatory Significance: Complex options strategy shows planning and sophistication

7. MULTI-ACCOUNT COORDINATION (Strength: {chain[6]['strength']:.2f})
   Time: {chain[6]['timestamp']}
   Account: {chain[6]['account_id']}
   Evidence: {chain[6]['description']}
   Regulatory Significance: Systematic coordination across all linked accounts

8. OUTCOME VALIDATION (Strength: {chain[7]['strength']:.2f})
   Time: {chain[7]['timestamp']}
   Account: {chain[7]['account_id']}
   Evidence: {chain[7]['description']}
   Regulatory Significance: Perfect timing correlation validates insider information theory

REGULATORY CONCLUSIONS:
======================

MAR Article 8 Assessment:
- Information Access: CONFIRMED (employment position provides access)
- Trading Activity: HIGHLY SUSPICIOUS (340% position increase)
- Timing Correlation: EXTREMELY SUSPICIOUS (48 hours before announcement)
- Financial Benefit: SIGNIFICANT (${summary['unrealized_gains']:,} unrealized gains)
- Recommendation: IMMEDIATE STOR FILING REQUIRED

Cross-Reference Analysis:
- Evidence items show strong interconnection (8 cross-references)
- Temporal sequence supports deliberate planning hypothesis
- Multiple evidence types corroborate insider dealing theory
- Pattern sophistication suggests experienced trader with inside knowledge

AUDIT TRAIL:
============
- Total Evidence Items: {summary['total_evidence_items']}
- Evidence Time Span: {summary['evidence_time_span_hours']} hours
- Accounts Analyzed: {summary['accounts_involved']}
- Regulatory Frameworks: {', '.join(summary['regulatory_frameworks_triggered'])}
- Detection Algorithms: Bayesian Network, Temporal Analysis, Cross-Account Correlation
- Data Sources: Trading records, Communication logs, Market data, Corporate announcements

This evidence chain provides a comprehensive audit trail suitable for regulatory 
examination and demonstrates clear insider dealing patterns requiring immediate action.
"""
    
    return narrative.strip()

def demonstrate_evidence_chain_structure():
    """
    Show the technical structure of how evidence chains are built.
    """
    
    print("🔍 EVIDENCE CHAIN EXAMPLE - REGULATORY EXPLAINABILITY SYSTEM")
    print("=" * 70)
    
    # Generate the example
    evidence_data = create_evidence_chain_example()
    
    print("\n📊 SCENARIO OVERVIEW:")
    print("-" * 30)
    person = evidence_data["person_info"]
    summary = evidence_data["scenario_summary"]
    
    print(f"Person: {person['person_name']} ({person['person_id']})")
    print(f"Alert Type: {summary['alert_type'].replace('_', ' ').title()}")
    print(f"Confidence: {summary['detection_confidence']:.1%}")
    print(f"STOR Eligible: {'Yes' if summary['stor_eligible'] else 'No'}")
    print(f"Evidence Items: {summary['total_evidence_items']}")
    print(f"Time Span: {summary['evidence_time_span_hours']} hours")
    print(f"Financial Exposure: ${summary['total_financial_exposure']:,}")
    
    # Use optimized output formatting for better performance
    if REAL_IMPORTS:
        formatted_output = OptimizedOutputFormatter.format_evidence_chain_output(evidence_data)
        print(formatted_output)
    else:
        # Fallback to original formatting
        print("\n🔗 EVIDENCE CHAIN STRUCTURE:")
        print("-" * 35)
        
        for evidence in evidence_data["evidence_chain"]:
            print(f"\n[{evidence['sequence_id']}] {evidence['evidence_type'].upper()}")
            print(f"    Time: {evidence['timestamp']}")
            print(f"    Account: {evidence['account_id']}")
            print(f"    Strength: {evidence['strength']:.2f} | Reliability: {evidence['reliability']:.2f}")
            print(f"    Description: {evidence['description']}")
            print(f"    Frameworks: {', '.join(evidence['regulatory_frameworks'])}")
            if evidence['cross_references']:
                print(f"    Cross-refs: {', '.join(map(str, evidence['cross_references']))}")
    
    print("\n📋 REGULATORY NARRATIVE:")
    print("-" * 30)
    
    # Use modular narrative generation if available
    if REAL_IMPORTS:
        try:
            generator = NarrativeGenerator()
            narrative = generator.generate_regulatory_narrative(evidence_data)
            print(narrative)
        except Exception as e:
            print(f"⚠️  Advanced narrative generation failed: {e}")
            print("Falling back to basic narrative...")
            narrative = generate_regulatory_narrative(evidence_data)
            print(narrative)
    else:
        narrative = generate_regulatory_narrative(evidence_data)
        print(narrative)
    
    print("\n💾 SECURE JSON EXPORT EXAMPLE:")
    print("-" * 35)
    print("# This is how the evidence chain would be securely exported for regulatory filing:")
    
    # Use secure printing with proper authorization
    if REAL_IMPORTS:
        # Demonstrate different access levels
        print("\n🔒 PUBLIC ACCESS LEVEL:")
        secure_print_evidence(
            {"evidence_chain": [evidence_data["evidence_chain"][0]]}, 
            user_id="public_user", 
            permission="view_evidence_summary"
        )
        
        print("\n🔓 COMPLIANCE ACCESS LEVEL:")
        secure_print_evidence(
            {"evidence_chain": [evidence_data["evidence_chain"][0]]}, 
            user_id="compliance_user", 
            permission="view_evidence_details"
        )
    else:
        # Fallback for environments without security modules
        print("⚠️  Security modules not available - using basic output:")
        print(json.dumps(evidence_data["evidence_chain"][0], indent=2))
    
    print("\n✅ EVIDENCE CHAIN COMPLETE")
    print("This example shows how your regulatory explainability system creates")
    print("comprehensive, audit-ready evidence chains for regulatory compliance.")

if __name__ == "__main__":
    demonstrate_evidence_chain_structure()