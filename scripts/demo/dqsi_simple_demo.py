#!/usr/bin/env python3
"""
Simple Role-Aware DQSI Demo Script

A simplified demonstration of the enhanced DQSI functionality
that works without pandas/numpy dependencies.

Features demonstrated:
1. Role-aware quality assessment (Producer vs Consumer)
2. Quality level differentiation (Foundational vs Enhanced)
3. Basic configuration and usage examples

Usage:
    python3 scripts/demo/dqsi_simple_demo.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from datetime import datetime, timedelta
import json
from typing import Dict, Any, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample data for demo without pandas dependency"""
    current_time = datetime.now()
    
    # Generate sample trading/surveillance data as dictionary format
    data = {
        'format': 'dict',
        'data': {
            'trade_id': 'TRD001',
            'trader_id': 'TR123',
            'instrument': 'AAPL',
            'quantity': 1000,
            'price': 150.25,
            'timestamp': current_time.isoformat(),
            'desk': 'EQUITY',
            'client_id': 'CLI456',
            'order_type': 'MARKET',
            'status': 'EXECUTED'
        }
    }
    
    return data

def create_test_config():
    """Create test configuration for DQSI"""
    return {
        'completeness': {
            'column_weights': {
                'trade_id': 0.3,
                'trader_id': 0.3,
                'instrument': 0.2,
                'price': 0.2
            }
        },
        'validity': {
            'validation_rules': [
                {
                    'type': 'range',
                    'field': 'quantity',
                    'min': 1,
                    'max': 1000000
                },
                {
                    'type': 'range',
                    'field': 'price',
                    'min': 0.01,
                    'max': 10000
                }
            ]
        },
        'timeliness': {
            'timestamp_field': 'timestamp',
            'max_age_hours': 1
        }
    }

def demo_role_configuration():
    """Demonstrate role-aware configuration"""
    print("=" * 60)
    print("ROLE-AWARE DQSI CONFIGURATION DEMO")
    print("=" * 60)
    
    # Producer configuration
    producer_config = {
        'role_aware': True,
        'role': 'producer',
        'quality_level': 'enhanced',
        'weights': {
            'completeness': 0.30,
            'accuracy': 0.25,
            'validity': 0.20,
            'consistency': 0.15,
            'uniqueness': 0.05,
            'timeliness': 0.05
        },
        'comparison_types': {
            'completeness': {
                'data_presence': 'none',
                'field_coverage': 'reference_table',
                'mandatory_fields': 'golden_source'
            },
            'accuracy': {
                'data_type': 'none',
                'format': 'reference_table',
                'cross_validation': 'cross_system'
            },
            'validity': {
                'format_check': 'reference_table',
                'constraint_check': 'golden_source'
            }
        }
    }
    
    # Consumer configuration
    consumer_config = {
        'role_aware': True,
        'role': 'consumer',
        'quality_level': 'foundational',
        'weights': {
            'completeness': 0.50,
            'validity': 0.30,
            'timeliness': 0.20
        },
        'comparison_types': {
            'completeness': {
                'data_presence': 'none',
                'field_coverage': 'reference_table'
            },
            'validity': {
                'format_check': 'reference_table'
            },
            'timeliness': {
                'freshness': 'none'
            }
        }
    }
    
    print("Producer Configuration (Enhanced):")
    print(f"  Role: {producer_config['role']}")
    print(f"  Quality Level: {producer_config['quality_level']}")
    print(f"  Dimensions: {len(producer_config['weights'])} total")
    print(f"  Weights: {producer_config['weights']}")
    print(f"  Comparison Types: {len(producer_config['comparison_types'])} dimensions configured")
    
    print("\nConsumer Configuration (Foundational):")
    print(f"  Role: {consumer_config['role']}")
    print(f"  Quality Level: {consumer_config['quality_level']}")
    print(f"  Dimensions: {len(consumer_config['weights'])} total")
    print(f"  Weights: {consumer_config['weights']}")
    print(f"  Comparison Types: {len(consumer_config['comparison_types'])} dimensions configured")
    
    # Show dimension differences
    producer_dims = set(producer_config['weights'].keys())
    consumer_dims = set(consumer_config['weights'].keys())
    additional_dims = producer_dims - consumer_dims
    
    print(f"\nDimension Differences:")
    print(f"  Producer-only dimensions: {additional_dims}")
    print(f"  Coverage ratio: Consumer covers {len(consumer_dims)}/{len(producer_dims)} dimensions")
    
    return producer_config, consumer_config

def demo_comparison_types():
    """Demonstrate comparison types and their usage"""
    print("\n" + "=" * 60)
    print("COMPARISON TYPES DEMONSTRATION")
    print("=" * 60)
    
    comparison_types = {
        'none': {
            'description': 'Basic profiling without external validation',
            'applicability': 'Foundational DQ',
            'use_cases': ['Data type checking', 'Basic format validation', 'Missing value detection']
        },
        'reference_table': {
            'description': 'Validation against static lookup tables',
            'applicability': 'Sometimes (if local)',
            'use_cases': ['Valid desk codes', 'Instrument types', 'Currency codes']
        },
        'golden_source': {
            'description': 'Validation against authoritative system-of-record',
            'applicability': 'Typically upstream',
            'use_cases': ['FO platform validation', 'CRM data verification', 'Master data checking']
        },
        'cross_system': {
            'description': 'Consistency validation across multiple feeds',
            'applicability': 'Enhanced scenarios',
            'use_cases': ['Timestamp consistency', 'Trade ID matching', 'Cross-feed validation']
        },
        'trend': {
            'description': 'Historical comparison and anomaly detection',
            'applicability': 'Optional, if baseline captured',
            'use_cases': ['Volume anomalies', 'Latency monitoring', 'Quality degradation detection']
        }
    }
    
    print("Available Comparison Types:\n")
    
    for comp_type, details in comparison_types.items():
        print(f"{comp_type.upper().replace('_', ' ')}:")
        print(f"  Description: {details['description']}")
        print(f"  Applicability: {details['applicability']}")
        print(f"  Use Cases:")
        for use_case in details['use_cases']:
            print(f"    - {use_case}")
        print()

def demo_sub_dimensions():
    """Demonstrate sub-dimension analysis"""
    print("=" * 60)
    print("SUB-DIMENSION ANALYSIS")
    print("=" * 60)
    
    # Example sub-dimensions for different roles and quality levels
    sub_dimensions = {
        'completeness': {
            'consumer_foundational': ['data_presence', 'field_coverage'],
            'consumer_enhanced': ['data_presence', 'field_coverage', 'mandatory_fields'],
            'producer_foundational': ['data_presence', 'field_coverage', 'mandatory_fields'],
            'producer_enhanced': ['data_presence', 'field_coverage', 'mandatory_fields', 'cross_system_coverage']
        },
        'accuracy': {
            'consumer_foundational': ['data_type', 'format'],
            'consumer_enhanced': ['data_type', 'format', 'range', 'cross_validation'],
            'producer_foundational': ['data_type', 'format', 'range', 'business_rules'],
            'producer_enhanced': ['data_type', 'format', 'range', 'business_rules', 'cross_validation']
        },
        'validity': {
            'consumer_foundational': ['format_check', 'constraint_check'],
            'consumer_enhanced': ['format_check', 'constraint_check', 'schema_validation'],
            'producer_foundational': ['format_check', 'constraint_check', 'business_rule_validation'],
            'producer_enhanced': ['format_check', 'constraint_check', 'business_rule_validation', 'regulatory_compliance', 'schema_validation']
        }
    }
    
    roles_levels = [
        ('consumer', 'foundational'),
        ('consumer', 'enhanced'),
        ('producer', 'foundational'),
        ('producer', 'enhanced')
    ]
    
    for dimension, configs in sub_dimensions.items():
        print(f"\n{dimension.upper()} Sub-dimensions:")
        
        for role, level in roles_levels:
            key = f"{role}_{level}"
            if key in configs:
                sub_dims = configs[key]
                print(f"  {role.title()} ({level}): {len(sub_dims)} sub-dimensions")
                for sub_dim in sub_dims:
                    print(f"    - {sub_dim}")

def demo_surveillance_scenario():
    """Demonstrate surveillance-specific scenario"""
    print("\n" + "=" * 60)
    print("SURVEILLANCE PLATFORM SCENARIO")
    print("=" * 60)
    
    # Alert generation system (Producer)
    alert_system_config = {
        'role': 'producer',
        'quality_level': 'enhanced',
        'focus_areas': [
            'Data completeness for regulatory compliance',
            'Accuracy for false positive reduction',
            'Timeliness for real-time monitoring',
            'Validity for structured data requirements'
        ],
        'weights': {
            'completeness': 0.30,  # Critical for compliance
            'accuracy': 0.25,      # Essential for effectiveness
            'timeliness': 0.20,    # Important for real-time
            'validity': 0.15,      # Required for structure
            'consistency': 0.10    # Supporting metric
        },
        'quality_targets': {
            'completeness': 0.95,
            'accuracy': 0.90,
            'timeliness': 0.90,
            'validity': 0.95
        }
    }
    
    # Analysis system (Consumer)
    analysis_system_config = {
        'role': 'consumer',
        'quality_level': 'foundational',
        'focus_areas': [
            'Data completeness for analysis reliability',
            'Validity for processing requirements',
            'Timeliness for current data analysis'
        ],
        'weights': {
            'completeness': 0.40,  # Most important for analysis
            'validity': 0.35,      # Structure matters for processing
            'timeliness': 0.25     # Currency important for relevance
        },
        'quality_targets': {
            'completeness': 0.90,
            'validity': 0.85,
            'timeliness': 0.80
        }
    }
    
    print("Alert Generation System (Producer):")
    print(f"  Role: {alert_system_config['role']}")
    print(f"  Quality Level: {alert_system_config['quality_level']}")
    print("  Focus Areas:")
    for area in alert_system_config['focus_areas']:
        print(f"    - {area}")
    print(f"  Quality Targets: {alert_system_config['quality_targets']}")
    
    print("\nAnalysis System (Consumer):")
    print(f"  Role: {analysis_system_config['role']}")
    print(f"  Quality Level: {analysis_system_config['quality_level']}")
    print("  Focus Areas:")
    for area in analysis_system_config['focus_areas']:
        print(f"    - {area}")
    print(f"  Quality Targets: {analysis_system_config['quality_targets']}")
    
    # Show the different priorities
    print(f"\nKey Differences:")
    print(f"  Producer assesses {len(alert_system_config['weights'])} dimensions")
    print(f"  Consumer focuses on {len(analysis_system_config['weights'])} core dimensions")
    print(f"  Producer has higher quality targets reflecting source responsibility")
    print(f"  Consumer optimizes for processing efficiency")

def demo_api_usage():
    """Demonstrate API request format"""
    print("\n" + "=" * 60)
    print("API USAGE EXAMPLES")
    print("=" * 60)
    
    # Enhanced API request example
    enhanced_request = {
        "dataset": create_sample_data(),
        "dimension_configs": create_test_config(),
        "role_aware": True,
        "role": "producer",
        "quality_level": "enhanced",
        "comparison_types": {
            "completeness": {
                "data_presence": "none",
                "field_coverage": "reference_table",
                "mandatory_fields": "golden_source"
            },
            "accuracy": {
                "data_type": "none",
                "format": "reference_table",
                "cross_validation": "cross_system"
            }
        },
        "custom_weights": {
            "completeness": 0.30,
            "accuracy": 0.25,
            "validity": 0.20,
            "timeliness": 0.15,
            "consistency": 0.10
        },
        "include_recommendations": True
    }
    
    # Traditional API request example
    traditional_request = {
        "dataset": create_sample_data(),
        "dimension_configs": create_test_config(),
        "custom_weights": {
            "completeness": 0.4,
            "accuracy": 0.3,
            "validity": 0.3
        },
        "enabled_dimensions": ["completeness", "accuracy", "validity"],
        "include_recommendations": True
    }
    
    print("Enhanced Role-Aware API Request:")
    print(json.dumps({
        'endpoint': 'POST /api/v1/dqsi/calculate',
        'role_aware': enhanced_request['role_aware'],
        'role': enhanced_request['role'],
        'quality_level': enhanced_request['quality_level'],
        'dimensions_configured': len(enhanced_request['comparison_types']),
        'weights_specified': len(enhanced_request['custom_weights'])
    }, indent=2))
    
    print("\nTraditional API Request:")
    print(json.dumps({
        'endpoint': 'POST /api/v1/dqsi/calculate',
        'role_aware': False,
        'enabled_dimensions': traditional_request['enabled_dimensions'],
        'weights_specified': len(traditional_request['custom_weights'])
    }, indent=2))
    
    print("\nKey Benefits of Role-Aware Mode:")
    print("  ✓ Tailored quality standards for different system roles")
    print("  ✓ Sub-dimension analysis for detailed insights") 
    print("  ✓ Multiple comparison types for comprehensive validation")
    print("  ✓ Enhanced recommendations with role-specific suggestions")
    print("  ✓ Quality level differentiation (Foundational vs Enhanced)")

def main():
    """Main demo function"""
    print("ROLE-AWARE DATA QUALITY SUFFICIENCY INDEX (DQSI)")
    print("Enhanced Features Demonstration")
    print("=" * 60)
    print("This demo showcases the new role-aware DQSI capabilities")
    print("suitable for surveillance platform requirements.\n")
    
    try:
        # Run demo sections
        demo_role_configuration()
        demo_comparison_types()
        demo_sub_dimensions()
        demo_surveillance_scenario()
        demo_api_usage()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Review the enhanced DQSI documentation")
        print("2. Test with your surveillance data using the API endpoints")
        print("3. Configure role-aware settings for your specific use case")
        print("4. Implement comparison types based on your data sources")
        print("5. Set up monitoring and alerting for quality degradation")
        
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())