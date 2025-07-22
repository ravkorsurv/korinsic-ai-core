"""
Test data generators for DQSI testing.

This module provides comprehensive test data generators for testing
Data Quality Sufficiency Index calculations across various scenarios.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json


class DQSITestDataGenerator:
    """Generate test data for DQSI testing with controlled quality issues."""
    
    def __init__(self, seed: int = 42):
        """Initialize with random seed for reproducible results."""
        random.seed(seed)
    
    def generate_perfect_data(self, num_records: int = 100) -> Dict[str, Any]:
        """Generate perfect quality data with no issues."""
        current_time = datetime.now()
        
        data = {
            'format': 'dataframe',
            'data': []
        }
        
        for i in range(num_records):
            record = {
                'id': i + 1,
                'name': f'User_{i+1:03d}',
                'email': f'user{i+1}@example.com',
                'phone': f'+1555{i+1:07d}',
                'age': random.randint(18, 65),
                'department': random.choice(['Engineering', 'Marketing', 'Sales', 'HR']),
                'salary': random.randint(50000, 150000),
                'join_date': (current_time - timedelta(days=random.randint(30, 3650))).strftime('%Y-%m-%d'),
                'timestamp': (current_time - timedelta(hours=random.randint(1, 12))).isoformat(),
                'status': 'active'
            }
            data['data'].append(record)
        
        return data
    
    def generate_completeness_issues(self, num_records: int = 100, 
                                   missing_percentage: float = 0.2) -> Dict[str, Any]:
        """Generate data with completeness issues (missing values)."""
        perfect_data = self.generate_perfect_data(num_records)
        
        # Introduce missing values
        missing_fields = ['name', 'email', 'phone', 'department']
        num_missing = int(num_records * missing_percentage)
        
        for i in range(num_missing):
            record_idx = random.randint(0, num_records - 1)
            field_to_remove = random.choice(missing_fields)
            perfect_data['data'][record_idx][field_to_remove] = None
        
        return perfect_data
    
    def generate_accuracy_issues(self, num_records: int = 100,
                               error_percentage: float = 0.15) -> Dict[str, Any]:
        """Generate data with accuracy issues (invalid formats, incorrect values)."""
        perfect_data = self.generate_perfect_data(num_records)
        
        num_errors = int(num_records * error_percentage)
        
        for i in range(num_errors):
            record_idx = random.randint(0, num_records - 1)
            error_type = random.choice(['invalid_email', 'invalid_phone', 'invalid_age'])
            
            if error_type == 'invalid_email':
                perfect_data['data'][record_idx]['email'] = 'invalid-email-format'
            elif error_type == 'invalid_phone':
                perfect_data['data'][record_idx]['phone'] = '123'
            elif error_type == 'invalid_age':
                perfect_data['data'][record_idx]['age'] = random.choice([-5, 200, 'invalid'])
        
        return perfect_data
    
    def generate_consistency_issues(self, num_records: int = 100,
                                  inconsistency_percentage: float = 0.1) -> Dict[str, Any]:
        """Generate data with consistency issues (format variations, outliers)."""
        perfect_data = self.generate_perfect_data(num_records)
        
        num_inconsistent = int(num_records * inconsistency_percentage)
        
        for i in range(num_inconsistent):
            record_idx = random.randint(0, num_records - 1)
            inconsistency_type = random.choice(['name_format', 'salary_outlier', 'phone_format'])
            
            if inconsistency_type == 'name_format':
                perfect_data['data'][record_idx]['name'] = 'John Smith Jr.'  # Different format
            elif inconsistency_type == 'salary_outlier':
                perfect_data['data'][record_idx]['salary'] = 1000000  # Extreme outlier
            elif inconsistency_type == 'phone_format':
                perfect_data['data'][record_idx]['phone'] = '(555) 123-4567'  # Different format
        
        return perfect_data
    
    def generate_validity_issues(self, num_records: int = 100,
                               invalid_percentage: float = 0.2) -> Dict[str, Any]:
        """Generate data with validity issues (constraint violations)."""
        perfect_data = self.generate_perfect_data(num_records)
        
        num_invalid = int(num_records * invalid_percentage)
        
        for i in range(num_invalid):
            record_idx = random.randint(0, num_records - 1)
            violation_type = random.choice(['email_format', 'date_format', 'negative_salary'])
            
            if violation_type == 'email_format':
                perfect_data['data'][record_idx]['email'] = 'not-an-email'
            elif violation_type == 'date_format':
                perfect_data['data'][record_idx]['join_date'] = '2024-13-45'  # Invalid date
            elif violation_type == 'negative_salary':
                perfect_data['data'][record_idx]['salary'] = -1000
        
        return perfect_data
    
    def generate_uniqueness_issues(self, num_records: int = 100,
                                 duplicate_percentage: float = 0.1) -> Dict[str, Any]:
        """Generate data with uniqueness issues (duplicates)."""
        perfect_data = self.generate_perfect_data(num_records)
        
        num_duplicates = int(num_records * duplicate_percentage)
        
        # Create duplicates by copying existing records
        for i in range(num_duplicates):
            source_idx = random.randint(0, num_records - 1)
            duplicate_record = perfect_data['data'][source_idx].copy()
            perfect_data['data'].append(duplicate_record)
        
        return perfect_data
    
    def generate_timeliness_issues(self, num_records: int = 100,
                                 stale_percentage: float = 0.3) -> Dict[str, Any]:
        """Generate data with timeliness issues (old timestamps)."""
        perfect_data = self.generate_perfect_data(num_records)
        
        num_stale = int(num_records * stale_percentage)
        
        for i in range(num_stale):
            record_idx = random.randint(0, num_records - 1)
            # Make timestamp very old (more than 30 days)
            old_time = datetime.now() - timedelta(days=random.randint(31, 365))
            perfect_data['data'][record_idx]['timestamp'] = old_time.isoformat()
        
        return perfect_data
    
    def generate_mixed_quality_data(self, num_records: int = 100,
                                  issue_probabilities: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Generate data with mixed quality issues."""
        if issue_probabilities is None:
            issue_probabilities = {
                'completeness': 0.1,
                'accuracy': 0.1,
                'consistency': 0.05,
                'validity': 0.1,
                'uniqueness': 0.05,
                'timeliness': 0.15
            }
        
        # Start with perfect data
        data = self.generate_perfect_data(num_records)
        
        # Apply each type of issue based on probabilities
        for issue_type, probability in issue_probabilities.items():
            if random.random() < probability:
                if issue_type == 'completeness':
                    data = self._apply_completeness_issues(data, 0.1)
                elif issue_type == 'accuracy':
                    data = self._apply_accuracy_issues(data, 0.1)
                elif issue_type == 'consistency':
                    data = self._apply_consistency_issues(data, 0.05)
                elif issue_type == 'validity':
                    data = self._apply_validity_issues(data, 0.1)
                elif issue_type == 'uniqueness':
                    data = self._apply_uniqueness_issues(data, 0.05)
                elif issue_type == 'timeliness':
                    data = self._apply_timeliness_issues(data, 0.15)
        
        return data
    
    def _apply_completeness_issues(self, data: Dict[str, Any], percentage: float) -> Dict[str, Any]:
        """Apply completeness issues to existing data."""
        num_records = len(data['data'])
        num_missing = int(num_records * percentage)
        missing_fields = ['name', 'email', 'phone']
        
        for i in range(num_missing):
            record_idx = random.randint(0, num_records - 1)
            field = random.choice(missing_fields)
            data['data'][record_idx][field] = None
        
        return data
    
    def _apply_accuracy_issues(self, data: Dict[str, Any], percentage: float) -> Dict[str, Any]:
        """Apply accuracy issues to existing data."""
        num_records = len(data['data'])
        num_errors = int(num_records * percentage)
        
        for i in range(num_errors):
            record_idx = random.randint(0, num_records - 1)
            data['data'][record_idx]['email'] = 'invalid-email'
        
        return data
    
    def _apply_consistency_issues(self, data: Dict[str, Any], percentage: float) -> Dict[str, Any]:
        """Apply consistency issues to existing data."""
        num_records = len(data['data'])
        num_inconsistent = int(num_records * percentage)
        
        for i in range(num_inconsistent):
            record_idx = random.randint(0, num_records - 1)
            data['data'][record_idx]['salary'] = 999999  # Outlier
        
        return data
    
    def _apply_validity_issues(self, data: Dict[str, Any], percentage: float) -> Dict[str, Any]:
        """Apply validity issues to existing data."""
        num_records = len(data['data'])
        num_invalid = int(num_records * percentage)
        
        for i in range(num_invalid):
            record_idx = random.randint(0, num_records - 1)
            data['data'][record_idx]['age'] = -10  # Invalid age
        
        return data
    
    def _apply_uniqueness_issues(self, data: Dict[str, Any], percentage: float) -> Dict[str, Any]:
        """Apply uniqueness issues to existing data."""
        num_records = len(data['data'])
        num_duplicates = int(num_records * percentage)
        
        for i in range(num_duplicates):
            source_idx = random.randint(0, num_records - 1)
            duplicate = data['data'][source_idx].copy()
            data['data'].append(duplicate)
        
        return data
    
    def _apply_timeliness_issues(self, data: Dict[str, Any], percentage: float) -> Dict[str, Any]:
        """Apply timeliness issues to existing data."""
        num_records = len(data['data'])
        num_stale = int(num_records * percentage)
        
        for i in range(num_stale):
            record_idx = random.randint(0, num_records - 1)
            old_time = datetime.now() - timedelta(days=60)
            data['data'][record_idx]['timestamp'] = old_time.isoformat()
        
        return data
    
    def generate_dimension_config(self, data_format: str = 'dataframe') -> Dict[str, Dict[str, Any]]:
        """Generate dimension configuration for test data."""
        return {
            'completeness': {
                'column_weights': {
                    'name': 0.3,
                    'email': 0.3,
                    'phone': 0.2,
                    'department': 0.2
                }
            },
            'accuracy': {
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
                    },
                    {
                        'type': 'range',
                        'field': 'salary',
                        'min': 0,
                        'max': 500000
                    }
                ]
            },
            'validity': {
                'validation_rules': [
                    {
                        'type': 'email',
                        'field': 'email'
                    },
                    {
                        'type': 'phone',
                        'field': 'phone'
                    },
                    {
                        'type': 'date',
                        'field': 'join_date',
                        'format': '%Y-%m-%d'
                    }
                ]
            },
            'uniqueness': {
                'key_columns': ['id', 'email']
            },
            'timeliness': {
                'timestamp_field': 'timestamp',
                'max_age_hours': 24
            }
        }
    
    def generate_batch_test_data(self, num_datasets: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple datasets for batch testing."""
        batch_data = []
        
        for i in range(num_datasets):
            if i == 0:
                # Perfect data
                dataset = self.generate_perfect_data(50)
            elif i == 1:
                # Data with multiple issues
                dataset = self.generate_mixed_quality_data(50)
            else:
                # Data with specific issues
                dataset = self.generate_completeness_issues(50, 0.3)
            
            batch_data.append({
                'id': f'dataset_{i+1}',
                'dataset': dataset
            })
        
        return batch_data
    
    def generate_time_series_data(self, num_periods: int = 7) -> List[Dict[str, Any]]:
        """Generate time series data for monitoring tests."""
        time_series = []
        base_time = datetime.now() - timedelta(days=num_periods)
        
        for i in range(num_periods):
            timestamp = base_time + timedelta(days=i)
            
            # Gradually degrade quality over time
            quality_degradation = i * 0.1
            
            if quality_degradation < 0.2:
                dataset = self.generate_perfect_data(30)
            elif quality_degradation < 0.4:
                dataset = self.generate_completeness_issues(30, quality_degradation)
            else:
                dataset = self.generate_mixed_quality_data(30)
            
            time_series.append({
                'timestamp': timestamp.isoformat(),
                'dataset': dataset
            })
        
        return time_series


class DQSITestScenarios:
    """Predefined test scenarios for comprehensive DQSI testing."""
    
    def __init__(self):
        self.generator = DQSITestDataGenerator()
    
    def get_scenario_perfect_quality(self) -> Dict[str, Any]:
        """Scenario: Perfect data quality (should score ~1.0)."""
        return {
            'name': 'Perfect Quality Data',
            'description': 'Data with no quality issues across all dimensions',
            'expected_score_range': (0.9, 1.0),
            'data': self.generator.generate_perfect_data(100),
            'dimension_configs': self.generator.generate_dimension_config()
        }
    
    def get_scenario_critical_quality(self) -> Dict[str, Any]:
        """Scenario: Critical data quality (should score < 0.4)."""
        # Generate data with severe issues in all dimensions
        data = self.generator.generate_perfect_data(100)
        data = self.generator._apply_completeness_issues(data, 0.4)
        data = self.generator._apply_accuracy_issues(data, 0.3)
        data = self.generator._apply_consistency_issues(data, 0.2)
        data = self.generator._apply_validity_issues(data, 0.3)
        data = self.generator._apply_uniqueness_issues(data, 0.2)
        data = self.generator._apply_timeliness_issues(data, 0.5)
        
        return {
            'name': 'Critical Quality Data',
            'description': 'Data with severe quality issues across all dimensions',
            'expected_score_range': (0.0, 0.4),
            'data': data,
            'dimension_configs': self.generator.generate_dimension_config()
        }
    
    def get_scenario_mixed_quality(self) -> Dict[str, Any]:
        """Scenario: Mixed data quality (should score 0.6-0.8)."""
        return {
            'name': 'Mixed Quality Data',
            'description': 'Data with moderate quality issues',
            'expected_score_range': (0.6, 0.8),
            'data': self.generator.generate_mixed_quality_data(100),
            'dimension_configs': self.generator.generate_dimension_config()
        }
    
    def get_scenario_single_dimension_issue(self, dimension: str) -> Dict[str, Any]:
        """Scenario: Issue in single dimension only."""
        data = self.generator.generate_perfect_data(100)
        
        if dimension == 'completeness':
            data = self.generator._apply_completeness_issues(data, 0.3)
        elif dimension == 'accuracy':
            data = self.generator._apply_accuracy_issues(data, 0.3)
        elif dimension == 'consistency':
            data = self.generator._apply_consistency_issues(data, 0.3)
        elif dimension == 'validity':
            data = self.generator._apply_validity_issues(data, 0.3)
        elif dimension == 'uniqueness':
            data = self.generator._apply_uniqueness_issues(data, 0.3)
        elif dimension == 'timeliness':
            data = self.generator._apply_timeliness_issues(data, 0.5)
        
        return {
            'name': f'Single Dimension Issue: {dimension}',
            'description': f'Data with issues only in {dimension} dimension',
            'expected_score_range': (0.7, 0.9),
            'data': data,
            'dimension_configs': self.generator.generate_dimension_config()
        }
    
    def get_all_scenarios(self) -> List[Dict[str, Any]]:
        """Get all predefined test scenarios."""
        scenarios = [
            self.get_scenario_perfect_quality(),
            self.get_scenario_critical_quality(),
            self.get_scenario_mixed_quality()
        ]
        
        # Add single dimension scenarios
        dimensions = ['completeness', 'accuracy', 'consistency', 'validity', 'uniqueness', 'timeliness']
        for dim in dimensions:
            scenarios.append(self.get_scenario_single_dimension_issue(dim))
        
        return scenarios


def save_test_data_to_json(filename: str, data: Dict[str, Any]) -> None:
    """Save test data to JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_test_data_from_json(filename: str) -> Dict[str, Any]:
    """Load test data from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


# Example usage and data generation
if __name__ == "__main__":
    generator = DQSITestDataGenerator()
    scenarios = DQSITestScenarios()
    
    # Generate sample datasets
    perfect_data = generator.generate_perfect_data(100)
    mixed_quality_data = generator.generate_mixed_quality_data(100)
    batch_data = generator.generate_batch_test_data(5)
    time_series_data = generator.generate_time_series_data(14)
    
    # Save test data
    save_test_data_to_json('tests/fixtures/perfect_data.json', perfect_data)
    save_test_data_to_json('tests/fixtures/mixed_quality_data.json', mixed_quality_data)
    save_test_data_to_json('tests/fixtures/batch_test_data.json', {'batch_data': batch_data})
    save_test_data_to_json('tests/fixtures/time_series_data.json', {'time_series_data': time_series_data})
    
    print("Test data files generated successfully!")
    print("- perfect_data.json: Perfect quality dataset")
    print("- mixed_quality_data.json: Mixed quality dataset")
    print("- batch_test_data.json: Batch processing test data")
    print("- time_series_data.json: Time series monitoring test data")