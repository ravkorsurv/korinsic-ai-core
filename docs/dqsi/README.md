# Data Quality Sufficiency Index (DQSI) Documentation

## Overview

The Data Quality Sufficiency Index (DQSI) is a comprehensive, modular data quality assessment system integrated into the Kor.ai surveillance platform. It provides multi-dimensional analysis of data quality across six key dimensions: completeness, accuracy, consistency, validity, uniqueness, and timeliness.

## Features

### Core Capabilities

- **Multi-dimensional Quality Assessment**: Evaluates data across 6 standard quality dimensions
- **Role-aware Assessment**: Tailored quality standards for producers vs consumers
- **Comparison Type Support**: Multiple validation approaches (None, Reference Table, Golden Source, Cross-System, Trend)
- **Sub-dimension Analysis**: Detailed breakdown with measurement and comparison types
- **Quality Level Modes**: Foundational vs Enhanced assessment capabilities
- **Configurable Scoring**: Customizable weights and thresholds for different use cases
- **Flexible Data Input**: Supports DataFrames, dictionaries, lists, and various data formats
- **Real-time Monitoring**: Time-series analysis and alerting capabilities
- **Batch Processing**: Efficient analysis of multiple datasets
- **Improvement Recommendations**: Actionable suggestions for quality enhancement

### Quality Dimensions

1. **Completeness** (Default weight: 25%)
   - Measures missing or null values
   - Supports column-specific weights
   - Configurable missing value definitions

2. **Accuracy** (Default weight: 20%)
   - Data correctness and precision
   - Reference data comparison
   - Rule-based validation

3. **Consistency** (Default weight: 15%)
   - Data uniformity across sources/time
   - Pattern matching and outlier detection
   - Format standardization checks

4. **Validity** (Default weight: 15%)
   - Adherence to defined formats and constraints
   - Built-in validators (email, phone, date)
   - Custom regex pattern matching

5. **Uniqueness** (Default weight: 15%)
   - Duplicate record detection
   - Configurable key columns
   - Composite key support

6. **Timeliness** (Default weight: 10%)
   - Data freshness and currency
   - Configurable age thresholds
   - Timestamp-based analysis

### Role-Aware Quality Assessment

The DQSI system supports role-aware quality assessment, allowing different quality standards based on whether the system is acting as a data producer or consumer, and the level of quality assurance required.

#### Roles

- **Producer**: Systems that generate or output data (e.g., alert generation systems, case management)
  - Implements comprehensive quality checks including golden source validation
  - Responsible for data accuracy and completeness at the source
  - Enhanced quality standards with cross-system and trend-based validation

- **Consumer**: Systems that receive and process data (e.g., downstream analysis, reporting)
  - Focuses on foundational data quality for processing needs
  - Emphasizes data completeness, validity, and timeliness
  - Streamlined checks optimized for data consumption workflows

#### Quality Levels

- **Foundational**: Basic data quality checks essential for operations
  - Core dimensions: Completeness, Validity, Timeliness
  - Comparison types: None, Reference Table
  - Suitable for most consumer applications

- **Enhanced**: Comprehensive quality assessment for critical systems
  - All dimensions: Completeness, Accuracy, Consistency, Validity, Uniqueness, Timeliness
  - All comparison types: None, Reference Table, Golden Source, Cross-System, Trend
  - Required for producer systems and critical data flows

#### Comparison Types

1. **None**: Basic profiling without external validation
   - Consumer profiles only (count, shape, violations)
   - No baseline comparison required
   - Suitable for foundational quality checks

2. **Reference Table**: Validation against static lookup tables
   - Checked against predefined lists (e.g., valid desk codes, instrument types)
   - Applicable when local reference data is available
   - Common for data standardization checks

3. **Golden Source**: Validation against authoritative system-of-record
   - Compared with upstream master systems (e.g., FO platform, CRM)
   - Highest level of accuracy validation
   - Typically used by producer systems

4. **Cross-System**: Consistency validation across multiple feeds
   - Compared across different data sources for consistency
   - Validates timestamps, trade IDs, and other cross-cutting data
   - Important for data integration scenarios

5. **Trend**: Historical comparison and anomaly detection
   - Compared to rolling averages and historical patterns
   - Detects volume anomalies, latency spikes, and quality degradation
   - Useful for monitoring and alerting

## API Endpoints

### Calculate DQSI Score

```http
POST /api/v1/dqsi/calculate
```

Calculate DQSI score for a single dataset.

**Request Body:**
```json
{
  "dataset": {
    "format": "dataframe",
    "data": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "timestamp": "2024-01-01T10:00:00Z"
      }
    ]
  },
  "dimension_configs": {
    "timeliness": {
      "timestamp_field": "timestamp",
      "max_age_hours": 24
    },
    "validity": {
      "validation_rules": [
        {
          "type": "email",
          "field": "email"
        }
      ]
    }
  },
  "custom_weights": {
    "completeness": 0.3,
    "accuracy": 0.3,
    "validity": 0.4
  },
  "enabled_dimensions": ["completeness", "accuracy", "validity"],
  "include_recommendations": true,
  "role_aware": true,
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
  }
}
```

**Response (Traditional):**
```json
{
  "timestamp": "2024-01-01T10:00:00Z",
  "calculation_type": "traditional",
  "dqsi_score": 0.85,
  "dimension_scores": {
    "completeness": 1.0,
    "accuracy": 0.8,
    "validity": 0.9
  },
  "status": "good",
  "recommendations": []
}
```

**Response (Role-Aware Enhanced):**
```json
{
  "success": true,
  "calculation_type": "enhanced",
  "role": "producer",
  "quality_level": "enhanced",
  "enhanced_results": {
    "overall_score": 0.85,
    "overall_status": "good",
    "role": "producer",
    "quality_level": "enhanced",
    "role_aware": true,
    "dimension_results": {
      "completeness": {
        "dimension": "completeness",
        "overall_score": 1.0,
        "sub_dimensions": [
          {
            "name": "data_presence",
            "score": 1.0,
            "comparison_type": "none",
            "measurement_type": "presence_check",
            "details": {"missing_count": 0}
          },
          {
            "name": "field_coverage", 
            "score": 0.95,
            "comparison_type": "reference_table",
            "measurement_type": "coverage_check",
            "details": {"coverage_ratio": 0.95}
          }
        ],
        "role": "producer",
        "quality_level": "enhanced"
      }
    },
    "dimension_scores": {
      "completeness": 1.0,
      "accuracy": 0.8,
      "validity": 0.9
    },
    "weights_used": {
      "completeness": 0.3,
      "accuracy": 0.3,
      "validity": 0.4
    },
    "comparison_types_used": {
      "completeness": {
        "data_presence": "none",
        "field_coverage": "reference_table"
      }
    },
    "timestamp": "2024-01-01T10:00:00Z"
  },
  "recommendations": [
    {
      "dimension": "accuracy",
      "current_score": 0.8,
      "target_score": 0.9,
      "priority": "medium",
      "role": "producer", 
      "quality_level": "enhanced",
      "suggestions": [
        "Implement data validation rules with golden source validation"
      ],
      "sub_dimension_details": [
        {
          "name": "format",
          "score": 0.75,
          "comparison_type": "reference_table",
          "measurement_type": "format_check"
        }
      ]
    }
  ],
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Batch Processing

```http
POST /api/v1/dqsi/batch
```

Process multiple datasets in a single request.

**Request Body:**
```json
{
  "batch_data": [
    {
      "id": "dataset_1",
      "dataset": {
        "format": "dataframe",
        "data": [...]
      }
    },
    {
      "id": "dataset_2", 
      "dataset": {
        "format": "csv",
        "csv_data": "name,email\nJohn,john@example.com"
      }
    }
  ],
  "include_comparison": true
}
```

### Monitoring and Trends

```http
POST /api/v1/dqsi/monitor
```

Monitor DQSI trends over time with alerting.

**Request Body:**
```json
{
  "time_series_data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "dataset": {...}
    },
    {
      "timestamp": "2024-01-02T00:00:00Z", 
      "dataset": {...}
    }
  ],
  "alerting_thresholds": {
    "critical": 0.4,
    "warning": 0.6,
    "target": 0.8
  },
  "trend_analysis_window": 7
}
```

### Data Quality Validation

```http
POST /api/v1/dqsi/validate
```

Validate data quality against specified thresholds.

**Request Body:**
```json
{
  "dataset": {...},
  "validation_thresholds": {
    "overall_minimum": 0.8,
    "dimension_minimums": {
      "completeness": 0.9,
      "accuracy": 0.8,
      "validity": 0.9
    }
  }
}
```

### Configuration

```http
GET /api/v1/dqsi/config
```

Get current DQSI configuration settings.

## Configuration

### Default Configuration

```json
{
  "dqsi": {
    "enabled": true,
    "weights": {
      "completeness": 0.25,
      "accuracy": 0.20,
      "consistency": 0.15,
      "validity": 0.15,
      "uniqueness": 0.15,
      "timeliness": 0.10
    },
    "thresholds": {
      "excellent": {"min": 0.9, "max": 1.0},
      "good": {"min": 0.8, "max": 0.9},
      "fair": {"min": 0.6, "max": 0.8},
      "poor": {"min": 0.4, "max": 0.6},
      "critical": {"min": 0.0, "max": 0.4}
    },
    "enabled_dimensions": [
      "completeness",
      "accuracy", 
      "consistency",
      "validity",
      "uniqueness",
      "timeliness"
    ],
    "alerting_thresholds": {
      "critical": 0.4,
      "warning": 0.6,
      "target": 0.8
    }
  }
}
```

### Dimension Configuration Examples

#### Completeness Configuration
```json
{
  "completeness": {
    "column_weights": {
      "critical_field": 0.5,
      "important_field": 0.3,
      "optional_field": 0.2
    }
  }
}
```

#### Accuracy Configuration
```json
{
  "accuracy": {
    "reference_data": {...},
    "validation_rules": [
      {
        "type": "regex",
        "field": "product_code",
        "pattern": "^[A-Z]{3}\\d{3}$"
      },
      {
        "type": "range",
        "field": "price",
        "min": 0,
        "max": 10000
      }
    ]
  }
}
```

#### Validity Configuration
```json
{
  "validity": {
    "validation_rules": [
      {
        "type": "email",
        "field": "email_address"
      },
      {
        "type": "phone", 
        "field": "phone_number"
      },
      {
        "type": "date",
        "field": "birth_date",
        "format": "%Y-%m-%d"
      },
      {
        "type": "custom_regex",
        "field": "custom_field",
        "pattern": "^CUSTOM-\\d{6}$"
      }
    ]
  }
}
```

#### Uniqueness Configuration
```json
{
  "uniqueness": {
    "key_columns": ["customer_id", "email"]
  }
}
```

#### Timeliness Configuration
```json
{
  "timeliness": {
    "timestamp_field": "last_updated",
    "max_age_hours": 24
  }
}
```

## Programming Interface

### Basic Usage

```python
from src.core.dqsi_score import DataQualitySufficiencyIndex, DQSIConfig
import pandas as pd

# Create DQSI calculator with default configuration
dqsi = DataQualitySufficiencyIndex()

# Prepare your data
data = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com']
})

# Calculate DQSI metrics
metrics = dqsi.calculate_dqsi(data)

print(f"Overall DQSI Score: {metrics.overall_score:.3f}")
print(f"Completeness: {metrics.completeness:.3f}")
print(f"Accuracy: {metrics.accuracy:.3f}")
```

### Custom Configuration

```python
# Create custom configuration
config = DQSIConfig(
    weights={
        'completeness': 0.4,
        'accuracy': 0.3,
        'validity': 0.3
    },
    enabled_dimensions=['completeness', 'accuracy', 'validity']
)

# Create DQSI calculator with custom config
dqsi = DataQualitySufficiencyIndex(config)

# Define dimension-specific configurations
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

# Calculate metrics
metrics = dqsi.calculate_dqsi(data, dimension_configs)
```

### Role-Aware Configuration

```python
# Producer configuration (enhanced quality checks)
producer_config = DQSIConfig(
    role_aware=True,
    role='producer',
    quality_level='enhanced',
    weights={
        'completeness': 0.30,
        'accuracy': 0.25,
        'validity': 0.20,
        'consistency': 0.15,
        'uniqueness': 0.05,
        'timeliness': 0.05
    },
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
        }
    }
)

# Consumer configuration (foundational checks)
consumer_config = DQSIConfig(
    role_aware=True,
    role='consumer',
    quality_level='foundational',
    weights={
        'completeness': 0.50,
        'validity': 0.30,
        'timeliness': 0.20
    }
)

# Create calculators for both roles
producer_dqsi = DataQualitySufficiencyIndex(producer_config)
consumer_dqsi = DataQualitySufficiencyIndex(consumer_config)

# Enhanced calculation with sub-dimensions
producer_results = producer_dqsi.calculate_dqsi_enhanced(data, dimension_configs)
consumer_results = consumer_dqsi.calculate_dqsi_enhanced(data, dimension_configs)

# Access sub-dimension results
for dim_name, dim_result in producer_results['dimension_results'].items():
    print(f"\n{dim_name} Dimension:")
    print(f"  Overall Score: {dim_result.overall_score:.3f}")
    
    for sub_dim in dim_result.sub_dimensions:
        print(f"    {sub_dim.name}: {sub_dim.score:.3f}")
        print(f"      Measurement: {sub_dim.measurement_type}")
        print(f"      Comparison: {sub_dim.comparison_type}")
```

### Report Generation

```python
# Generate comprehensive report
report = dqsi.generate_report(metrics, include_details=True)

# Get improvement recommendations
recommendations = dqsi.get_improvement_recommendations(metrics)

for rec in recommendations:
    print(f"Dimension: {rec['dimension']}")
    print(f"Current Score: {rec['current_score']}")
    print(f"Priority: {rec['priority']}")
    print(f"Suggestions: {rec['suggestions']}")
```

## Testing

### Test Data Generation

The DQSI system includes comprehensive test data generators:

```python
from tests.fixtures.dqsi_test_data import DQSITestDataGenerator, DQSITestScenarios

# Generate test data with specific quality issues
generator = DQSITestDataGenerator()

# Perfect quality data
perfect_data = generator.generate_perfect_data(100)

# Data with completeness issues
incomplete_data = generator.generate_completeness_issues(100, missing_percentage=0.2)

# Mixed quality issues
mixed_data = generator.generate_mixed_quality_data(100)

# Predefined test scenarios
scenarios = DQSITestScenarios()
all_scenarios = scenarios.get_all_scenarios()
```

### Running Tests

```bash
# Run all DQSI tests
python -m pytest tests/unit/core/test_dqsi_score.py -v

# Run specific test class
python -m pytest tests/unit/core/test_dqsi_score.py::TestCompletenessCalculator -v

# Generate test data
python tests/fixtures/dqsi_test_data.py
```

## Integration Examples

### With Surveillance Data

```python
# Example integration with trading data
trading_data = {
    'trades': [...],
    'orders': [...],
    'trader_info': {...}
}

# Configure DQSI for trading data
dimension_configs = {
    'completeness': {
        'column_weights': {
            'trader_id': 0.3,
            'instrument': 0.3,
            'volume': 0.2,
            'price': 0.2
        }
    },
    'timeliness': {
        'timestamp_field': 'trade_timestamp',
        'max_age_hours': 1  # Trading data should be very fresh
    },
    'validity': {
        'validation_rules': [
            {
                'type': 'range',
                'field': 'volume',
                'min': 0,
                'max': 10000000
            },
            {
                'type': 'range', 
                'field': 'price',
                'min': 0.01,
                'max': 100000
            }
        ]
    }
}

# Calculate DQSI for trading data
metrics = dqsi.calculate_dqsi(trading_data, dimension_configs)
```

### Monitoring Pipeline

```python
# Set up continuous monitoring
def monitor_data_quality(data_source):
    dqsi = DataQualitySufficiencyIndex()
    
    while True:
        # Get latest data
        current_data = data_source.get_latest()
        
        # Calculate DQSI
        metrics = dqsi.calculate_dqsi(current_data)
        
        # Check alerts
        if metrics.overall_score < 0.6:
            send_alert(f"Data quality degraded: {metrics.overall_score:.3f}")
        
        # Log metrics
        log_metrics(metrics)
        
        time.sleep(3600)  # Check hourly
```

## Troubleshooting

### Common Issues

1. **Low Completeness Scores**
   - Check for unexpected null values
   - Verify column weights configuration
   - Review data collection processes

2. **Low Accuracy Scores** 
   - Validate reference data is current
   - Review validation rules for correctness
   - Check data transformation logic

3. **Low Consistency Scores**
   - Look for outliers in numeric data
   - Check for format variations in text fields
   - Review data standardization processes

4. **Low Validity Scores**
   - Verify validation rules match data format
   - Check for edge cases in validation logic
   - Review constraint definitions

5. **Low Uniqueness Scores**
   - Identify source of duplicates
   - Check key column configuration
   - Review data deduplication processes

6. **Low Timeliness Scores**
   - Verify timestamp field configuration
   - Check data pipeline latency
   - Review refresh frequency requirements

### Performance Optimization

- Use appropriate data sampling for large datasets
- Configure only necessary dimensions for better performance
- Implement caching for repeated validations
- Use batch processing for multiple datasets

## Best Practices

1. **Configuration Management**
   - Store configurations in version control
   - Use environment-specific settings
   - Document dimension weight rationales

2. **Monitoring Strategy**
   - Set appropriate alert thresholds
   - Monitor trends, not just absolute scores
   - Implement escalation procedures

3. **Data Quality Improvement**
   - Focus on high-impact dimensions first
   - Implement automated fixes where possible
   - Track improvement over time

4. **Testing and Validation**
   - Use test scenarios to validate configurations
   - Implement regression testing for changes
   - Validate against known good datasets

## Changelog

### Version 1.0.0
- Initial DQSI implementation
- Six core quality dimensions
- REST API endpoints
- Configuration system
- Test data generators
- Documentation

## Contributing

When contributing to DQSI:

1. Add unit tests for new calculators
2. Update documentation for new features
3. Maintain backward compatibility
4. Follow existing code patterns
5. Add comprehensive test scenarios

## Support

For issues or questions:
- Check the troubleshooting section
- Review test scenarios for examples
- Consult API documentation
- Check configuration examples