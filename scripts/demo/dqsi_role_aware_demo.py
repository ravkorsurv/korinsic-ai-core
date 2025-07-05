#!/usr/bin/env python3
"""
Role-Aware DQSI Demo Script

This demo showcases the enhanced Data Quality Sufficiency Index (DQSI) functionality
with role-aware configuration and comparison types for surveillance applications.

Features demonstrated:
1. Role-aware quality assessment (Producer vs Consumer)
2. Comparison types (None, Reference Table, Golden Source, Cross-System, Trend)
3. Sub-dimension analysis with measurement types
4. Quality level differentiation (Foundational vs Enhanced)
5. Enhanced recommendations with role-specific suggestions

Usage:
    python scripts/demo/dqsi_role_aware_demo.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from datetime import datetime, timedelta
import json
from typing import Dict, Any, List
import logging
import random

from src.core.dqsi_score import (
    DataQualitySufficiencyIndex, 
    DQSIConfig, 
    DimensionResult,
    SubDimensionResult
)
from tests.fixtures.dqsi_test_data import DQSITestDataGenerator, DQSITestScenarios

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RoleAwareDQSIDemo:
    """Demo class for role-aware DQSI functionality"""
    
    def __init__(self):
        self.test_data_generator = DQSITestDataGenerator()
        self.test_scenarios = DQSITestScenarios()
        
    def run_comprehensive_demo(self):
        """Run comprehensive demo of role-aware DQSI features"""
        print("="*80)
        print("ROLE-AWARE DATA QUALITY SUFFICIENCY INDEX (DQSI) DEMO")
        print("="*80)
        print()
        
        # Demo 1: Basic Role Comparison
        print("1. BASIC ROLE COMPARISON")
        print("-" * 50)
        self._demo_role_comparison()
        
        # Demo 2: Quality Level Comparison
        print("\n2. QUALITY LEVEL COMPARISON")
        print("-" * 50)
        self._demo_quality_level_comparison()
        
        # Demo 3: Comparison Types Demonstration
        print("\n3. COMPARISON TYPES DEMONSTRATION")
        print("-" * 50)
        self._demo_comparison_types()
        
        # Demo 4: Sub-dimension Analysis
        print("\n4. SUB-DIMENSION ANALYSIS")
        print("-" * 50)
        self._demo_sub_dimension_analysis()
        
        # Demo 5: Surveillance Scenario
        print("\n5. SURVEILLANCE SCENARIO")
        print("-" * 50)
        self._demo_surveillance_scenario()
        
        # Demo 6: Role-Aware Recommendations
        print("\n6. ROLE-AWARE RECOMMENDATIONS")
        print("-" * 50)
        self._demo_role_aware_recommendations()
        
        print("\n" + "="*80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
    
    def _demo_role_comparison(self):
        """Demonstrate basic role comparison"""
        print("Comparing Consumer vs Producer role assessments...")
        
        # Generate sample trading data
        trading_data = self.test_data_generator.generate_mixed_quality_data(
            num_records=1000,
            issue_probabilities={
                'completeness': 0.1,
                'accuracy': 0.05,
                'consistency': 0.08,
                'validity': 0.05,
                'uniqueness': 0.03,
                'timeliness': 0.1
            }
        )
        
        # Consumer configuration (foundational)
        consumer_config = DQSIConfig(
            role_aware=True,
            role='consumer',
            quality_level='foundational'
        )
        
        # Producer configuration (enhanced)
        producer_config = DQSIConfig(
            role_aware=True,
            role='producer',
            quality_level='enhanced'
        )
        
        # Calculate DQSI for both roles
        consumer_dqsi = DataQualitySufficiencyIndex(consumer_config)
        producer_dqsi = DataQualitySufficiencyIndex(producer_config)
        
        consumer_results = consumer_dqsi.calculate_dqsi_enhanced(trading_data)
        producer_results = producer_dqsi.calculate_dqsi_enhanced(trading_data)
        
        # Display results
        print(f"\nConsumer Results (Foundational):")
        print(f"  Overall Score: {consumer_results['overall_score']:.3f}")
        print(f"  Dimensions Assessed: {len(consumer_results['dimension_results'])}")
        print(f"  Dimensions: {list(consumer_results['dimension_results'].keys())}")
        
        print(f"\nProducer Results (Enhanced):")
        print(f"  Overall Score: {producer_results['overall_score']:.3f}")
        print(f"  Dimensions Assessed: {len(producer_results['dimension_results'])}")
        print(f"  Dimensions: {list(producer_results['dimension_results'].keys())}")
        
        # Compare dimension coverage
        consumer_dims = set(consumer_results['dimension_results'].keys())
        producer_dims = set(producer_results['dimension_results'].keys())
        additional_dims = producer_dims - consumer_dims
        
        if additional_dims:
            print(f"\nAdditional dimensions for Producer: {additional_dims}")
        
        print(f"\nKey Insight: Producer role assesses {len(producer_dims)} dimensions")
        print(f"while Consumer role focuses on {len(consumer_dims)} foundational dimensions.")
    
    def _demo_quality_level_comparison(self):
        """Demonstrate quality level comparison"""
        print("Comparing Foundational vs Enhanced quality levels...")
        
        # Generate sample data with various quality issues
        sample_data = self.test_data_generator.generate_mixed_quality_data(
            num_records=500,
            issue_probabilities={
                'completeness': 0.15,
                'accuracy': 0.10,
                'uniqueness': 0.05,
                'consistency': 0.08,
                'validity': 0.05,
                'timeliness': 0.12
            }
        )
        
        # Foundational configuration
        foundational_config = DQSIConfig(
            role_aware=True,
            role='consumer',
            quality_level='foundational'
        )
        
        # Enhanced configuration
        enhanced_config = DQSIConfig(
            role_aware=True,
            role='consumer',
            quality_level='enhanced'
        )
        
        # Calculate DQSI for both levels
        foundational_dqsi = DataQualitySufficiencyIndex(foundational_config)
        enhanced_dqsi = DataQualitySufficiencyIndex(enhanced_config)
        
        foundational_results = foundational_dqsi.calculate_dqsi_enhanced(sample_data)
        enhanced_results = enhanced_dqsi.calculate_dqsi_enhanced(sample_data)
        
        # Display comparison
        print(f"\nFoundational Level:")
        print(f"  Overall Score: {foundational_results['overall_score']:.3f}")
        print(f"  Focus: Basic data profiling and validation")
        
        print(f"\nEnhanced Level:")
        print(f"  Overall Score: {enhanced_results['overall_score']:.3f}")
        print(f"  Focus: Advanced cross-system and trend analysis")
        
        # Show sub-dimension counts
        foundational_subdims = self._count_subdimensions(foundational_results)
        enhanced_subdims = self._count_subdimensions(enhanced_results)
        
        print(f"\nSub-dimension Analysis:")
        print(f"  Foundational: {foundational_subdims} sub-dimensions")
        print(f"  Enhanced: {enhanced_subdims} sub-dimensions")
        print(f"  Additional coverage: {enhanced_subdims - foundational_subdims} sub-dimensions")
    
    def _demo_comparison_types(self):
        """Demonstrate different comparison types"""
        print("Showcasing comparison types and their applications...")
        
        # Generate sample data
        sample_data = self.test_data_generator.generate_mixed_quality_data(
            num_records=300,
            issue_probabilities={
                'completeness': 0.12,
                'validity': 0.08,
                'accuracy': 0.05,
                'consistency': 0.04,
                'uniqueness': 0.03,
                'timeliness': 0.10
            }
        )
        
        # Configuration with all comparison types
        config = DQSIConfig(
            role_aware=True,
            role='producer',
            quality_level='enhanced',
            comparison_types={
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
                'timeliness': {
                    'freshness': 'trend',
                    'latency': 'cross_system'
                }
            }
        )
        
        # Add mock reference data
        dimension_configs = {
            'completeness': {
                'sub_dimensions': {
                    'field_coverage': {
                        'reference_table': ['trade_id', 'timestamp', 'symbol', 'quantity', 'price']
                    },
                    'mandatory_fields': {
                        'golden_source': {
                            'required_fields': ['trade_id', 'timestamp', 'symbol']
                        }
                    }
                }
            },
            'timeliness': {
                'sub_dimensions': {
                    'freshness': {
                        'historical_data': self._generate_historical_trend_data()
                    }
                }
            }
        }
        
        # Calculate DQSI
        dqsi = DataQualitySufficiencyIndex(config)
        results = dqsi.calculate_dqsi_enhanced(sample_data, dimension_configs)
        
        # Display comparison type usage
        print("\nComparison Type Usage:")
        comparison_usage = {}
        for dim_name, dim_result in results['dimension_results'].items():
            if hasattr(dim_result, 'sub_dimensions'):
                for sub_dim in dim_result.sub_dimensions:
                    comp_type = sub_dim.comparison_type
                    if comp_type not in comparison_usage:
                        comparison_usage[comp_type] = []
                    comparison_usage[comp_type].append(f"{dim_name}.{sub_dim.name}")
        
        for comp_type, usages in comparison_usage.items():
            print(f"  {comp_type.title().replace('_', ' ')}: {len(usages)} sub-dimensions")
            for usage in usages[:3]:  # Show first 3
                print(f"    - {usage}")
            if len(usages) > 3:
                print(f"    - ... and {len(usages) - 3} more")
        
        print(f"\nOverall Score: {results['overall_score']:.3f}")
    
    def _demo_sub_dimension_analysis(self):
        """Demonstrate sub-dimension analysis"""
        print("Analyzing sub-dimensions and measurement types...")
        
        # Generate data with specific quality issues
        problematic_data = self.test_scenarios.get_scenario_mixed_quality()['data']
        
        # Enhanced configuration for detailed analysis
        config = DQSIConfig(
            role_aware=True,
            role='producer',
            quality_level='enhanced'
        )
        
        dqsi = DataQualitySufficiencyIndex(config)
        results = dqsi.calculate_dqsi_enhanced(problematic_data)
        
        # Analyze sub-dimensions
        print(f"\nDetailed Sub-dimension Analysis:")
        print(f"Overall Score: {results['overall_score']:.3f}")
        
        for dim_name, dim_result in results['dimension_results'].items():
            if hasattr(dim_result, 'sub_dimensions') and dim_result.sub_dimensions:
                print(f"\n{dim_name.title()} Dimension:")
                print(f"  Overall Score: {dim_result.overall_score:.3f}")
                
                for sub_dim in dim_result.sub_dimensions:
                    print(f"    {sub_dim.name}:")
                    print(f"      Score: {sub_dim.score:.3f}")
                    print(f"      Measurement: {sub_dim.measurement_type}")
                    print(f"      Comparison: {sub_dim.comparison_type}")
                    
                    # Show quality issues
                    if sub_dim.score < 0.8:
                        print(f"      ⚠️  Quality Issue Detected!")
    
    def _demo_surveillance_scenario(self):
        """Demonstrate surveillance-specific scenario"""
        print("Surveillance Platform Quality Assessment Scenario...")
        
        # Generate surveillance data (alerts, cases, trades)
        alerts_data = self.test_data_generator.generate_mixed_quality_data(
            num_records=200,
            issue_probabilities={
                'completeness': 0.05,  # High quality expected
                'accuracy': 0.03,
                'timeliness': 0.08,
                'validity': 0.02,
                'consistency': 0.01,
                'uniqueness': 0.01
            }
        )
        
        # Producer configuration (alert generation system)
        producer_config = DQSIConfig(
            role_aware=True,
            role='producer',
            quality_level='enhanced',
            weights={
                'completeness': 0.30,  # Critical for surveillance
                'accuracy': 0.25,      # Essential for compliance
                'timeliness': 0.20,    # Important for real-time
                'validity': 0.15,      # Required for regulatory
                'consistency': 0.10,   # Supporting metric
                'uniqueness': 0.05     # Less critical for alerts
            }
        )
        
        # Consumer configuration (downstream analysis)
        consumer_config = DQSIConfig(
            role_aware=True,
            role='consumer',
            quality_level='foundational',
            weights={
                'completeness': 0.40,  # Most important for analysis
                'validity': 0.35,      # Structure matters
                'timeliness': 0.25     # Currency important
            }
        )
        
        # Calculate both perspectives
        producer_dqsi = DataQualitySufficiencyIndex(producer_config)
        consumer_dqsi = DataQualitySufficiencyIndex(consumer_config)
        
        producer_results = producer_dqsi.calculate_dqsi_enhanced(alerts_data)
        consumer_results = consumer_dqsi.calculate_dqsi_enhanced(alerts_data)
        
        # Display surveillance assessment
        print(f"\nSurveillance Quality Assessment:")
        print(f"  Alert Generation (Producer): {producer_results['overall_score']:.3f}")
        print(f"  Alert Analysis (Consumer): {consumer_results['overall_score']:.3f}")
        
        # Show dimension focus
        print(f"\nProducer Focus Areas:")
        for dim, score in producer_results['dimension_scores'].items():
            weight = producer_config.weights.get(dim, 0)
            print(f"  {dim}: {score:.3f} (weight: {weight:.2f})")
        
        print(f"\nConsumer Focus Areas:")
        for dim, score in consumer_results['dimension_scores'].items():
            weight = consumer_config.weights.get(dim, 0)
            print(f"  {dim}: {score:.3f} (weight: {weight:.2f})")
        
        # Quality recommendations
        if producer_results['overall_score'] < 0.8:
            print(f"\n🚨 Producer Quality Alert: Score below threshold!")
        if consumer_results['overall_score'] < 0.8:
            print(f"\n🚨 Consumer Quality Alert: Score below threshold!")
    
    def _demo_role_aware_recommendations(self):
        """Demonstrate role-aware recommendations"""
        print("Generating role-aware improvement recommendations...")
        
        # Generate data with quality issues
        poor_quality_data = self.test_scenarios.get_scenario_critical_quality()['data']
        
        # Test both roles
        roles = [
            ('consumer', 'foundational'),
            ('consumer', 'enhanced'),
            ('producer', 'foundational'),
            ('producer', 'enhanced')
        ]
        
        for role, quality_level in roles:
            print(f"\n{role.title()} - {quality_level.title()}:")
            
            config = DQSIConfig(
                role_aware=True,
                role=role,
                quality_level=quality_level
            )
            
            dqsi = DataQualitySufficiencyIndex(config)
            results = dqsi.calculate_dqsi_enhanced(poor_quality_data)
            
            # Generate recommendations (simulated)
            recommendations = self._generate_mock_recommendations(results, role, quality_level)
            
            print(f"  Overall Score: {results['overall_score']:.3f}")
            print(f"  Dimensions Assessed: {len(results['dimension_results'])}")
            print(f"  Recommendations Generated: {len(recommendations)}")
            
            # Show top recommendation
            if recommendations:
                top_rec = recommendations[0]
                print(f"  Top Priority: {top_rec['dimension']} ({top_rec['priority']})")
                print(f"    Current: {top_rec['current_score']:.3f}")
                print(f"    Suggestion: {top_rec['suggestions'][0]}")
    
    def _count_subdimensions(self, results: Dict[str, Any]) -> int:
        """Count total sub-dimensions in results"""
        count = 0
        for dim_result in results.get('dimension_results', {}).values():
            if hasattr(dim_result, 'sub_dimensions'):
                count += len(dim_result.sub_dimensions)
        return count
    
    def _generate_historical_trend_data(self) -> List[Dict[str, Any]]:
        """Generate mock historical trend data"""
        historical_data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            score = 0.85 + random.gauss(0, 0.05)  # Trending around 0.85
            historical_data.append({
                'date': date.isoformat(),
                'score': max(0.0, min(1.0, score))
            })
        
        return historical_data
    
    def _generate_mock_recommendations(self, results: Dict[str, Any], role: str, quality_level: str) -> List[Dict[str, Any]]:
        """Generate mock recommendations for demo"""
        recommendations = []
        
        for dim_name, dim_result in results['dimension_results'].items():
            score = dim_result.overall_score if hasattr(dim_result, 'overall_score') else 0.0
            
            if score < 0.8:
                suggestions = self._get_role_specific_suggestions(dim_name, role, quality_level)
                recommendations.append({
                    'dimension': dim_name,
                    'current_score': score,
                    'target_score': 0.9,
                    'priority': 'high' if score < 0.5 else 'medium',
                    'role': role,
                    'quality_level': quality_level,
                    'suggestions': suggestions
                })
        
        return sorted(recommendations, key=lambda x: x['current_score'])
    
    def _get_role_specific_suggestions(self, dimension: str, role: str, quality_level: str) -> List[str]:
        """Get role-specific suggestions"""
        base_suggestions = {
            'completeness': "Implement data validation at ingestion",
            'accuracy': "Add reference data validation",
            'consistency': "Standardize data transformation",
            'validity': "Implement format validation",
            'uniqueness': "Add duplicate detection",
            'timeliness': "Implement real-time processing"
        }
        
        suggestion = base_suggestions.get(dimension, "Review data quality processes")
        
        if role == 'producer':
            if quality_level == 'enhanced':
                suggestion += " with golden source validation"
            else:
                suggestion += " with reference table checks"
        else:
            if quality_level == 'enhanced':
                suggestion += " with trend monitoring"
            else:
                suggestion += " with basic profiling"
        
        return [suggestion]

def main():
    """Main demo function"""
    demo = RoleAwareDQSIDemo()
    
    try:
        demo.run_comprehensive_demo()
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())