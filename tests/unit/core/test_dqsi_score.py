"""
Unit tests for Data Quality Sufficiency Index (DQSI) module.

This module contains comprehensive tests for all DQSI components including:
- Individual dimension calculators
- Overall DQSI scoring
- Configuration handling
- Report generation
- Improvement recommendations
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.core.dqsi_score import (
    DataQualitySufficiencyIndex,
    DQSIConfig,
    DQSIMetrics,
    CompletenessCalculator,
    AccuracyCalculator,
    ConsistencyCalculator,
    ValidityCalculator,
    UniquenessCalculator,
    TimelinessCalculator
)


class TestDQSIConfig:
    """Test cases for DQSI configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = DQSIConfig()
        
        # Check default weights
        assert config.weights['completeness'] == 0.25
        assert config.weights['accuracy'] == 0.20
        assert config.weights['consistency'] == 0.15
        assert config.weights['validity'] == 0.15
        assert config.weights['uniqueness'] == 0.15
        assert config.weights['timeliness'] == 0.10
        
        # Check sum of weights
        assert sum(config.weights.values()) == 1.0
        
        # Check default thresholds
        assert 'excellent' in config.thresholds
        assert 'good' in config.thresholds
        assert 'fair' in config.thresholds
        assert 'poor' in config.thresholds
        assert 'critical' in config.thresholds
        
        # Check enabled dimensions
        assert len(config.enabled_dimensions) == 6
        assert 'completeness' in config.enabled_dimensions
        assert 'timeliness' in config.enabled_dimensions
    
    def test_custom_config(self):
        """Test custom configuration values."""
        custom_weights = {
            'completeness': 0.4,
            'accuracy': 0.3,
            'consistency': 0.1,
            'validity': 0.1,
            'uniqueness': 0.05,
            'timeliness': 0.05
        }
        
        config = DQSIConfig(
            weights=custom_weights,
            enabled_dimensions=['completeness', 'accuracy']
        )
        
        assert config.weights['completeness'] == 0.4
        assert len(config.enabled_dimensions) == 2


class TestCompletenessCalculator:
    """Test cases for completeness calculator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = CompletenessCalculator()
    
    def test_get_dimension_name(self):
        """Test dimension name."""
        assert self.calculator.get_dimension_name() == "completeness"
    
    def test_dataframe_completeness_perfect(self):
        """Test perfect completeness with DataFrame."""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c'],
            'col3': [1.1, 2.2, 3.3]
        })
        
        score = self.calculator.calculate(df)
        assert score == 1.0
    
    def test_dataframe_completeness_with_nulls(self):
        """Test completeness with null values."""
        df = pd.DataFrame({
            'col1': [1, 2, None],
            'col2': ['a', None, 'c'],
            'col3': [1.1, 2.2, 3.3]
        })
        
        score = self.calculator.calculate(df)
        expected = 7 / 9  # 7 non-null values out of 9 total
        assert abs(score - expected) < 0.001
    
    def test_dataframe_completeness_with_weights(self):
        """Test completeness with column weights."""
        df = pd.DataFrame({
            'col1': [1, 2, None],
            'col2': ['a', None, 'c'],
            'col3': [1.1, 2.2, 3.3]
        })
        
        config = {'column_weights': {'col1': 0.5, 'col2': 0.3, 'col3': 0.2}}
        score = self.calculator.calculate(df, config)
        
        # col1: 2/3, col2: 2/3, col3: 3/3
        expected = (2/3 * 0.5) + (2/3 * 0.3) + (3/3 * 0.2)
        assert abs(score - expected) < 0.001
    
    def test_dict_completeness(self):
        """Test completeness with dictionary data."""
        data = {
            'field1': 'value1',
            'field2': None,
            'field3': 'value3',
            'field4': ''
        }
        
        score = self.calculator.calculate(data)
        # 2 complete fields out of 4 (None and '' are considered incomplete)
        assert score == 0.5
    
    def test_list_completeness(self):
        """Test completeness with list data."""
        data = [1, 2, None, 4, 5]
        
        score = self.calculator.calculate(data)
        assert score == 0.8  # 4 non-null values out of 5
    
    def test_empty_data(self):
        """Test completeness with empty data."""
        assert self.calculator.calculate(pd.DataFrame()) == 0.0
        assert self.calculator.calculate({}) == 0.0
        assert self.calculator.calculate([]) == 0.0


class TestAccuracyCalculator:
    """Test cases for accuracy calculator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = AccuracyCalculator()
    
    def test_get_dimension_name(self):
        """Test dimension name."""
        assert self.calculator.get_dimension_name() == "accuracy"
    
    def test_accuracy_with_reference_data(self):
        """Test accuracy against reference data."""
        data = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        reference = pd.DataFrame({
            'col1': [1, 2, 4],
            'col2': ['a', 'b', 'c']
        })
        
        config = {'reference_data': reference}
        score = self.calculator.calculate(data, config)
        
        # 5 matches out of 6 total values
        assert score == 5/6
    
    def test_accuracy_with_validation_rules(self):
        """Test accuracy with validation rules."""
        data = pd.DataFrame({
            'email': ['test@example.com', 'invalid-email', 'user@domain.org'],
            'age': [25, 30, 35]
        })
        
        config = {
            'validation_rules': [
                {
                    'type': 'regex',
                    'field': 'email',
                    'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                },
                {
                    'type': 'range',
                    'field': 'age',
                    'min': 18,
                    'max': 65
                }
            ]
        }
        
        score = self.calculator.calculate(data, config)
        
        # 2 valid emails + 3 valid ages = 5 out of 6 total checks
        assert score == 5/6
    
    def test_accuracy_no_config(self):
        """Test accuracy with no configuration."""
        data = pd.DataFrame({'col1': [1, 2, 3]})
        score = self.calculator.calculate(data)
        
        # Should return default score
        assert score == 0.5


class TestConsistencyCalculator:
    """Test cases for consistency calculator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = ConsistencyCalculator()
    
    def test_get_dimension_name(self):
        """Test dimension name."""
        assert self.calculator.get_dimension_name() == "consistency"
    
    def test_dataframe_consistency(self):
        """Test consistency with DataFrame."""
        df = pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 5],
            'string_col': ['AAA-111', 'BBB-222', 'CCC-333', 'DDD-444', 'EEE-555']
        })
        
        score = self.calculator.calculate(df)
        
        # Should be high consistency (no outliers, consistent patterns)
        assert score > 0.8
    
    def test_dataframe_consistency_with_outliers(self):
        """Test consistency with outliers."""
        df = pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 1000],  # 1000 is an outlier
            'string_col': ['AAA-111', 'BBB-222', 'CCC-333', 'DDD-444', 'different']
        })
        
        score = self.calculator.calculate(df)
        
        # Should be lower consistency due to outliers
        assert score < 0.8
    
    def test_dict_consistency(self):
        """Test consistency with dictionary data."""
        data = {
            'field1': 'string_value',
            'field2': 'another_string',
            'field3': 123,
            'field4': 456
        }
        
        score = self.calculator.calculate(data)
        
        # 4 items with 2 string types and 2 int types = 4 consistent items
        assert score == 1.0


class TestValidityCalculator:
    """Test cases for validity calculator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = ValidityCalculator()
    
    def test_get_dimension_name(self):
        """Test dimension name."""
        assert self.calculator.get_dimension_name() == "validity"
    
    def test_email_validation(self):
        """Test email validation."""
        data = pd.DataFrame({
            'email': ['valid@example.com', 'invalid-email', 'test@domain.co.uk']
        })
        
        config = {
            'validation_rules': [
                {
                    'type': 'email',
                    'field': 'email'
                }
            ]
        }
        
        score = self.calculator.calculate(data, config)
        
        # 2 valid emails out of 3
        assert score == 2/3
    
    def test_phone_validation(self):
        """Test phone validation."""
        data = pd.DataFrame({
            'phone': ['1234567890', '123-456-7890', '12345']
        })
        
        config = {
            'validation_rules': [
                {
                    'type': 'phone',
                    'field': 'phone'
                }
            ]
        }
        
        score = self.calculator.calculate(data, config)
        
        # At least 1 valid phone number
        assert score > 0
    
    def test_date_validation(self):
        """Test date validation."""
        data = pd.DataFrame({
            'date': ['2024-01-01', '2024-13-01', '2024-02-15']
        })
        
        config = {
            'validation_rules': [
                {
                    'type': 'date',
                    'field': 'date',
                    'format': '%Y-%m-%d'
                }
            ]
        }
        
        score = self.calculator.calculate(data, config)
        
        # 2 valid dates out of 3
        assert score == 2/3
    
    def test_custom_regex_validation(self):
        """Test custom regex validation."""
        data = pd.DataFrame({
            'code': ['ABC123', 'XYZ789', 'invalid']
        })
        
        config = {
            'validation_rules': [
                {
                    'type': 'custom_regex',
                    'field': 'code',
                    'pattern': r'^[A-Z]{3}\d{3}$'
                }
            ]
        }
        
        score = self.calculator.calculate(data, config)
        
        # 2 valid codes out of 3
        assert score == 2/3


class TestUniquenessCalculator:
    """Test cases for uniqueness calculator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = UniquenessCalculator()
    
    def test_get_dimension_name(self):
        """Test dimension name."""
        assert self.calculator.get_dimension_name() == "uniqueness"
    
    def test_dataframe_uniqueness_perfect(self):
        """Test perfect uniqueness with DataFrame."""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        score = self.calculator.calculate(df)
        assert score == 1.0
    
    def test_dataframe_uniqueness_with_duplicates(self):
        """Test uniqueness with duplicates."""
        df = pd.DataFrame({
            'col1': [1, 1, 2],
            'col2': ['a', 'a', 'b']
        })
        
        score = self.calculator.calculate(df)
        
        # 2 unique rows out of 3 total
        assert score == 2/3
    
    def test_dataframe_uniqueness_with_key_columns(self):
        """Test uniqueness with specified key columns."""
        df = pd.DataFrame({
            'id': [1, 2, 2],
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35]
        })
        
        config = {'key_columns': ['id']}
        score = self.calculator.calculate(df, config)
        
        # 2 unique IDs out of 3 total
        assert score == 2/3
    
    def test_list_uniqueness(self):
        """Test uniqueness with list data."""
        data = [1, 2, 2, 3, 3, 3]
        
        score = self.calculator.calculate(data)
        
        # 3 unique values out of 6 total
        assert score == 0.5


class TestTimelinessCalculator:
    """Test cases for timeliness calculator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = TimelinessCalculator()
    
    def test_get_dimension_name(self):
        """Test dimension name."""
        assert self.calculator.get_dimension_name() == "timeliness"
    
    def test_dataframe_timeliness_fresh(self):
        """Test timeliness with fresh data."""
        current_time = datetime.now()
        fresh_times = [
            current_time - timedelta(hours=1),
            current_time - timedelta(hours=2),
            current_time - timedelta(hours=3)
        ]
        
        df = pd.DataFrame({
            'timestamp': fresh_times,
            'value': [1, 2, 3]
        })
        
        config = {
            'timestamp_field': 'timestamp',
            'max_age_hours': 24
        }
        
        score = self.calculator.calculate(df, config)
        assert score == 1.0
    
    def test_dataframe_timeliness_stale(self):
        """Test timeliness with stale data."""
        current_time = datetime.now()
        mixed_times = [
            current_time - timedelta(hours=1),    # fresh
            current_time - timedelta(hours=25),   # stale
            current_time - timedelta(hours=30)    # stale
        ]
        
        df = pd.DataFrame({
            'timestamp': mixed_times,
            'value': [1, 2, 3]
        })
        
        config = {
            'timestamp_field': 'timestamp',
            'max_age_hours': 24
        }
        
        score = self.calculator.calculate(df, config)
        
        # 1 fresh record out of 3
        assert score == 1/3
    
    def test_dict_timeliness(self):
        """Test timeliness with dictionary data."""
        current_time = datetime.now()
        fresh_time = current_time - timedelta(hours=1)
        
        data = {
            'timestamp': fresh_time,
            'value': 123
        }
        
        config = {
            'timestamp_field': 'timestamp',
            'max_age_hours': 24
        }
        
        score = self.calculator.calculate(data, config)
        assert score == 1.0
    
    def test_no_timestamp_config(self):
        """Test timeliness with no timestamp configuration."""
        data = pd.DataFrame({'value': [1, 2, 3]})
        
        score = self.calculator.calculate(data)
        
        # Should return default score
        assert score == 0.5


class TestDataQualitySufficiencyIndex:
    """Test cases for main DQSI calculator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.dqsi = DataQualitySufficiencyIndex()
        
        # Create test data
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 
                     'david@example.com', 'eve@example.com'],
            'age': [25, 30, 35, 40, 45],
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='H')
        })
    
    def test_initialization(self):
        """Test DQSI initialization."""
        assert self.dqsi.config is not None
        assert len(self.dqsi.calculators) == 6
        assert 'completeness' in self.dqsi.calculators
        assert 'timeliness' in self.dqsi.calculators
    
    def test_calculate_dqsi_perfect_data(self):
        """Test DQSI calculation with perfect data."""
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
        
        metrics = self.dqsi.calculate_dqsi(self.test_data, dimension_configs)
        
        assert isinstance(metrics, DQSIMetrics)
        assert metrics.overall_score > 0.8  # Should be high quality
        assert metrics.completeness > 0.9   # Perfect completeness
        assert metrics.uniqueness == 1.0    # Perfect uniqueness
    
    def test_calculate_dqsi_with_issues(self):
        """Test DQSI calculation with data quality issues."""
        # Create problematic data
        problematic_data = pd.DataFrame({
            'id': [1, 2, 2, 3, 4],  # Duplicate ID
            'name': ['Alice', None, 'Charlie', 'David', 'Eve'],  # Missing name
            'email': ['alice@example.com', 'invalid-email', 'charlie@example.com', 
                     'david@example.com', 'eve@example.com'],  # Invalid email
            'age': [25, 30, 35, 40, 1000],  # Outlier age
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='H')
        })
        
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
            }
        }
        
        metrics = self.dqsi.calculate_dqsi(problematic_data, dimension_configs)
        
        assert metrics.overall_score < 0.8  # Should be lower quality
        assert metrics.completeness < 1.0   # Has missing values
        assert metrics.uniqueness < 1.0     # Has duplicates
        assert metrics.validity < 1.0       # Has invalid email
    
    def test_calculate_weighted_score(self):
        """Test weighted score calculation."""
        dimension_scores = {
            'completeness': 0.9,
            'accuracy': 0.8,
            'consistency': 0.7,
            'validity': 0.6,
            'uniqueness': 0.5,
            'timeliness': 0.4
        }
        
        weighted_score = self.dqsi._calculate_weighted_score(dimension_scores)
        
        # Calculate expected score manually
        expected = (0.9 * 0.25) + (0.8 * 0.20) + (0.7 * 0.15) + (0.6 * 0.15) + (0.5 * 0.15) + (0.4 * 0.10)
        
        assert abs(weighted_score - expected) < 0.001
    
    def test_get_dimension_status(self):
        """Test dimension status labels."""
        assert self.dqsi._get_dimension_status(0.95) == 'excellent'
        assert self.dqsi._get_dimension_status(0.85) == 'good'
        assert self.dqsi._get_dimension_status(0.65) == 'fair'
        assert self.dqsi._get_dimension_status(0.45) == 'poor'
        assert self.dqsi._get_dimension_status(0.25) == 'critical'
    
    def test_generate_report(self):
        """Test report generation."""
        metrics = DQSIMetrics(
            completeness=0.9,
            accuracy=0.8,
            consistency=0.7,
            validity=0.6,
            uniqueness=0.5,
            timeliness=0.4,
            overall_score=0.7
        )
        
        report = self.dqsi.generate_report(metrics)
        
        assert 'overall_score' in report
        assert 'overall_status' in report
        assert 'dimension_scores' in report
        assert 'dimension_statuses' in report
        assert 'weights_used' in report
        assert 'timestamp' in report
        
        assert report['overall_score'] == 0.7
        assert report['overall_status'] == 'fair'
    
    def test_get_improvement_recommendations(self):
        """Test improvement recommendations."""
        metrics = DQSIMetrics(
            completeness=0.6,  # Below 0.8 threshold
            accuracy=0.9,      # Above threshold
            consistency=0.4,   # Below 0.8 threshold
            validity=0.7,      # Below 0.8 threshold
            uniqueness=0.3,    # Below 0.8 threshold
            timeliness=0.8,    # At threshold
            overall_score=0.6
        )
        
        recommendations = self.dqsi.get_improvement_recommendations(metrics)
        
        # Should have recommendations for dimensions below 0.8
        assert len(recommendations) >= 4
        
        # Check that recommendations are sorted by priority
        high_priority_recs = [r for r in recommendations if r['priority'] == 'high']
        medium_priority_recs = [r for r in recommendations if r['priority'] == 'medium']
        
        # uniqueness (0.3) and consistency (0.4) should be high priority
        assert len(high_priority_recs) >= 2
    
    def test_custom_config(self):
        """Test DQSI with custom configuration."""
        custom_config = DQSIConfig(
            weights={
                'completeness': 0.5,
                'accuracy': 0.3,
                'consistency': 0.1,
                'validity': 0.1,
                'uniqueness': 0.0,
                'timeliness': 0.0
            },
            enabled_dimensions=['completeness', 'accuracy']
        )
        
        custom_dqsi = DataQualitySufficiencyIndex(custom_config)
        
        metrics = custom_dqsi.calculate_dqsi(self.test_data)
        
        # Should only have scores for enabled dimensions
        assert metrics.completeness > 0
        assert metrics.accuracy > 0
        assert metrics.uniqueness == 0  # Not enabled
        assert metrics.timeliness == 0  # Not enabled
    
    def test_empty_data(self):
        """Test DQSI with empty data."""
        empty_data = pd.DataFrame()
        
        metrics = self.dqsi.calculate_dqsi(empty_data)
        
        assert metrics.overall_score == 0.0
        assert all(score == 0.0 for score in metrics.dimension_scores.values())
    
    def test_error_handling(self):
        """Test error handling in DQSI calculation."""
        # Test with invalid data type
        invalid_data = "not a valid data type"
        
        metrics = self.dqsi.calculate_dqsi(invalid_data)
        
        # Should return default metrics without crashing
        assert isinstance(metrics, DQSIMetrics)
        assert metrics.overall_score >= 0.0