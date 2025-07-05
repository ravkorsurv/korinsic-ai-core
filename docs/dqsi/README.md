# Data Quality Sufficiency Index (DQSI) Documentation

## Overview

The Data Quality Sufficiency Index (DQSI) is a comprehensive, modular data quality assessment system integrated into the Kor.ai surveillance platform. It provides multi-dimensional analysis of data quality across six key dimensions: completeness, accuracy, consistency, validity, uniqueness, and timeliness.

## Features

### Core Capabilities

- **Multi-dimensional Quality Assessment**: Evaluates data across 6 standard quality dimensions
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
  "include_recommendations": true
}
```

**Response:**
```json
{
  "timestamp": "2024-01-01T10:00:00Z",
  "dqsi_score": 0.85,
  "dimension_scores": {
    "completeness": 1.0,
    "accuracy": 0.8,
    "validity": 0.9
  },
  "status": "good",
  "report": {
    "overall_score": 0.85,
    "overall_status": "good",
    "dimension_scores": {
      "completeness": 1.0,
      "accuracy": 0.8,
      "validity": 0.9
    },
    "dimension_statuses": {
      "completeness": "excellent",
      "accuracy": "good",
      "validity": "excellent"
    },
    "weights_used": {
      "completeness": 0.3,
      "accuracy": 0.3,
      "validity": 0.4
    }
  },
  "recommendations": []
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