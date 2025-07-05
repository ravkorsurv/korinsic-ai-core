"""
DQSI (Data Quality Sufficiency Index) Demonstration Script

This script demonstrates the key features and capabilities of the DQSI system
including basic calculation, custom configuration, batch processing, and 
monitoring capabilities.
"""

import json
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

try:
    from src.core.dqsi_score import DataQualitySufficiencyIndex, DQSIConfig, DQSIMetrics
    from tests.fixtures.dqsi_test_data import DQSITestDataGenerator, DQSITestScenarios
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the project root and dependencies are installed")
    sys.exit(1)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_metrics(metrics: DQSIMetrics, title: str = "DQSI Metrics"):
    """Print formatted DQSI metrics."""
    print(f"\n{title}:")
    print(f"  Overall Score: {metrics.overall_score:.3f}")
    print(f"  Dimension Scores:")
    for dimension, score in metrics.dimension_scores.items():
        status = get_status_from_score(score)
        print(f"    {dimension.capitalize()}: {score:.3f} ({status})")


def get_status_from_score(score: float) -> str:
    """Get status label from score."""
    if score >= 0.9:
        return 'excellent'
    elif score >= 0.8:
        return 'good'
    elif score >= 0.6:
        return 'fair'
    elif score >= 0.4:
        return 'poor'
    else:
        return 'critical'


def demo_basic_usage():
    """Demonstrate basic DQSI usage."""
    print_section("Basic DQSI Usage")
    
    # Create test data generator
    generator = DQSITestDataGenerator()
    
    # Generate perfect quality data
    perfect_data = generator.generate_perfect_data(50)
    
    # Create DQSI calculator with default configuration
    dqsi = DataQualitySufficiencyIndex()
    
    # Basic dimension configuration
    dimension_configs = {
        'timeliness': {
            'timestamp_field': 'timestamp',
            'max_age_hours': 24
        },
        'validity': {
            'validation_rules': [
                {
                    'type': 'email',
                    'field': 'email'
                }
            ]
        },
        'uniqueness': {
            'key_columns': ['id']
        }
    }
    
    print("Processing perfect quality data...")
    
    # Process the data for DQSI calculation (convert to appropriate format)
    data_records = perfect_data['data']
    
    # Calculate DQSI metrics
    metrics = dqsi.calculate_dqsi(data_records, dimension_configs)
    
    print_metrics(metrics, "Perfect Data Results")
    
    # Generate report
    report = dqsi.generate_report(metrics)
    print(f"\nOverall Status: {report['overall_status']}")
    print(f"Report Timestamp: {report['timestamp']}")


def demo_quality_issues():
    """Demonstrate DQSI with various quality issues."""
    print_section("DQSI with Quality Issues")
    
    generator = DQSITestDataGenerator()
    dqsi = DataQualitySufficiencyIndex()
    
    dimension_configs = {
        'validity': {
            'validation_rules': [
                {
                    'type': 'email',
                    'field': 'email'
                }
            ]
        },
        'uniqueness': {
            'key_columns': ['id']
        },
        'timeliness': {
            'timestamp_field': 'timestamp',
            'max_age_hours': 24
        }
    }
    
    # Test different types of quality issues
    quality_scenarios = [
        ("Perfect Data", generator.generate_perfect_data(30)),
        ("Completeness Issues", generator.generate_completeness_issues(30, 0.2)),
        ("Accuracy Issues", generator.generate_accuracy_issues(30, 0.15)),
        ("Validity Issues", generator.generate_validity_issues(30, 0.2)),
        ("Uniqueness Issues", generator.generate_uniqueness_issues(30, 0.1)),
        ("Mixed Issues", generator.generate_mixed_quality_data(30))
    ]
    
    for scenario_name, data in quality_scenarios:
        print(f"\n--- {scenario_name} ---")
        data_records = data['data']
        metrics = dqsi.calculate_dqsi(data_records, dimension_configs)
        
        print(f"Overall Score: {metrics.overall_score:.3f} ({get_status_from_score(metrics.overall_score)})")
        
        # Show top issues
        low_dimensions = [(dim, score) for dim, score in metrics.dimension_scores.items() if score < 0.8]
        if low_dimensions:
            print("Dimensions needing attention:")
            for dim, score in sorted(low_dimensions, key=lambda x: x[1]):
                print(f"  {dim}: {score:.3f}")


def demo_custom_configuration():
    """Demonstrate custom DQSI configuration."""
    print_section("Custom DQSI Configuration")
    
    # Create custom configuration focusing on completeness and validity
    custom_config = DQSIConfig(
        weights={
            'completeness': 0.4,
            'accuracy': 0.2,
            'validity': 0.3,
            'uniqueness': 0.1,
            'consistency': 0.0,  # Disabled
            'timeliness': 0.0     # Disabled
        },
        enabled_dimensions=['completeness', 'accuracy', 'validity', 'uniqueness']
    )
    
    # Create DQSI calculator with custom config
    dqsi = DataQualitySufficiencyIndex(custom_config)
    
    generator = DQSITestDataGenerator()
    data = generator.generate_mixed_quality_data(50)
    
    dimension_configs = {
        'validity': {
            'validation_rules': [
                {
                    'type': 'email',
                    'field': 'email'
                },
                {
                    'type': 'range',
                    'field': 'age',
                    'min': 18,
                    'max': 65
                }
            ]
        }
    }
    
    print("Using custom weights:")
    print(f"  Completeness: {custom_config.weights['completeness']}")
    print(f"  Accuracy: {custom_config.weights['accuracy']}")
    print(f"  Validity: {custom_config.weights['validity']}")
    print(f"  Uniqueness: {custom_config.weights['uniqueness']}")
    print(f"  Enabled dimensions: {custom_config.enabled_dimensions}")
    
    metrics = dqsi.calculate_dqsi(data['data'], dimension_configs)
    print_metrics(metrics, "Custom Configuration Results")


def demo_batch_processing():
    """Demonstrate batch processing capabilities."""
    print_section("Batch Processing")
    
    generator = DQSITestDataGenerator()
    dqsi = DataQualitySufficiencyIndex()
    
    # Generate multiple datasets with different quality levels
    datasets = [
        ("High Quality", generator.generate_perfect_data(30)),
        ("Medium Quality", generator.generate_mixed_quality_data(30)),
        ("Low Quality", generator.generate_completeness_issues(30, 0.4))
    ]
    
    dimension_configs = {
        'validity': {
            'validation_rules': [
                {
                    'type': 'email',
                    'field': 'email'
                }
            ]
        }
    }
    
    batch_results = []
    
    for name, data in datasets:
        print(f"\nProcessing {name} dataset...")
        metrics = dqsi.calculate_dqsi(data['data'], dimension_configs)
        
        batch_results.append({
            'name': name,
            'score': metrics.overall_score,
            'status': get_status_from_score(metrics.overall_score)
        })
        
        print(f"  Score: {metrics.overall_score:.3f} ({get_status_from_score(metrics.overall_score)})")
    
    # Summary
    print(f"\nBatch Processing Summary:")
    avg_score = sum(r['score'] for r in batch_results) / len(batch_results)
    print(f"  Total datasets: {len(batch_results)}")
    print(f"  Average score: {avg_score:.3f}")
    print(f"  Best performer: {max(batch_results, key=lambda x: x['score'])['name']}")
    print(f"  Worst performer: {min(batch_results, key=lambda x: x['score'])['name']}")


def demo_improvement_recommendations():
    """Demonstrate improvement recommendations."""
    print_section("Improvement Recommendations")
    
    generator = DQSITestDataGenerator()
    dqsi = DataQualitySufficiencyIndex()
    
    # Generate data with mixed quality issues
    problematic_data = generator.generate_mixed_quality_data(50, {
        'completeness': 0.3,  # High probability of completeness issues
        'accuracy': 0.2,
        'validity': 0.25,
        'uniqueness': 0.15
    })
    
    dimension_configs = {
        'validity': {
            'validation_rules': [
                {
                    'type': 'email',
                    'field': 'email'
                }
            ]
        }
    }
    
    print("Analyzing data with multiple quality issues...")
    metrics = dqsi.calculate_dqsi(problematic_data['data'], dimension_configs)
    print_metrics(metrics, "Problematic Data Analysis")
    
    # Get improvement recommendations
    recommendations = dqsi.get_improvement_recommendations(metrics)
    
    if recommendations:
        print(f"\nImprovement Recommendations ({len(recommendations)} issues found):")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['dimension'].upper()} (Priority: {rec['priority'].upper()})")
            print(f"   Current Score: {rec['current_score']:.3f}")
            print(f"   Target Score: {rec['target_score']:.3f}")
            print(f"   Suggestions:")
            for suggestion in rec['suggestions'][:2]:  # Show first 2 suggestions
                print(f"     • {suggestion}")
    else:
        print("\nNo improvement recommendations needed - data quality is good!")


def demo_monitoring_simulation():
    """Demonstrate monitoring and trend analysis simulation."""
    print_section("Monitoring and Trend Analysis")
    
    generator = DQSITestDataGenerator()
    dqsi = DataQualitySufficiencyIndex()
    
    dimension_configs = {
        'timeliness': {
            'timestamp_field': 'timestamp',
            'max_age_hours': 24
        }
    }
    
    print("Simulating data quality monitoring over time...")
    
    # Simulate quality degradation over time
    time_series_results = []
    base_time = datetime.now() - timedelta(days=7)
    
    for day in range(7):
        timestamp = base_time + timedelta(days=day)
        
        # Gradually degrade quality
        degradation = day * 0.1
        
        if degradation < 0.2:
            data = generator.generate_perfect_data(20)
        elif degradation < 0.4:
            data = generator.generate_completeness_issues(20, degradation)
        else:
            data = generator.generate_mixed_quality_data(20)
        
        metrics = dqsi.calculate_dqsi(data['data'], dimension_configs)
        
        time_series_results.append({
            'day': day + 1,
            'timestamp': timestamp.strftime('%Y-%m-%d'),
            'score': metrics.overall_score,
            'status': get_status_from_score(metrics.overall_score)
        })
        
        print(f"  Day {day + 1}: {metrics.overall_score:.3f} ({get_status_from_score(metrics.overall_score)})")
    
    # Trend analysis
    scores = [r['score'] for r in time_series_results]
    if len(scores) >= 2:
        trend = scores[-1] - scores[0]
        trend_direction = "improving" if trend > 0.05 else "declining" if trend < -0.05 else "stable"
        
        print(f"\nTrend Analysis:")
        print(f"  Trend Direction: {trend_direction}")
        print(f"  Score Change: {trend:+.3f}")
        print(f"  Current Score: {scores[-1]:.3f}")
        
        # Simulate alerts
        alerts = []
        for result in time_series_results:
            if result['score'] < 0.6:
                alerts.append(f"Day {result['day']}: Quality below warning threshold ({result['score']:.3f})")
        
        if alerts:
            print(f"\nAlerts Generated:")
            for alert in alerts:
                print(f"  ⚠️  {alert}")
        else:
            print(f"\n✅ No alerts - quality maintained above thresholds")


def demo_scenario_testing():
    """Demonstrate predefined test scenarios."""
    print_section("Predefined Test Scenarios")
    
    scenarios = DQSITestScenarios()
    dqsi = DataQualitySufficiencyIndex()
    
    # Test a few key scenarios
    test_scenarios = [
        scenarios.get_scenario_perfect_quality(),
        scenarios.get_scenario_mixed_quality(),
        scenarios.get_scenario_single_dimension_issue('completeness')
    ]
    
    print("Testing predefined scenarios:")
    
    for scenario in test_scenarios:
        print(f"\n--- {scenario['name']} ---")
        print(f"Description: {scenario['description']}")
        print(f"Expected Range: {scenario['expected_score_range'][0]:.1f} - {scenario['expected_score_range'][1]:.1f}")
        
        metrics = dqsi.calculate_dqsi(
            scenario['data']['data'], 
            scenario['dimension_configs']
        )
        
        actual_score = metrics.overall_score
        expected_min, expected_max = scenario['expected_score_range']
        
        print(f"Actual Score: {actual_score:.3f}")
        
        if expected_min <= actual_score <= expected_max:
            print("✅ Result within expected range")
        else:
            print("❌ Result outside expected range")


def main():
    """Run all DQSI demonstrations."""
    print("DQSI (Data Quality Sufficiency Index) Demonstration")
    print("==================================================")
    print("This demo showcases the key features of the DQSI system.")
    
    try:
        # Run all demonstrations
        demo_basic_usage()
        demo_quality_issues()
        demo_custom_configuration()
        demo_batch_processing()
        demo_improvement_recommendations()
        demo_monitoring_simulation()
        demo_scenario_testing()
        
        print_section("Demo Complete")
        print("All DQSI demonstrations completed successfully!")
        print("\nNext steps:")
        print("- Review the generated results above")
        print("- Try the API endpoints with real data")
        print("- Customize configurations for your use case")
        print("- Set up monitoring for your data pipelines")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())