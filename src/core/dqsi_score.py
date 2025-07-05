"""
Data Quality Sufficiency Index (DQSI) Module

A comprehensive, modular data quality assessment system that evaluates:
- Completeness: Measure of missing or null values
- Accuracy: Data correctness and precision
- Consistency: Data uniformity across sources/time
- Validity: Adherence to defined formats and constraints
- Uniqueness: Duplicate record detection
- Timeliness: Data freshness and currency

This module provides a weighted scoring system similar to ESI but focused on data quality dimensions.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import re
import json

logger = logging.getLogger(__name__)

@dataclass
class DQSIMetrics:
    """Data class for DQSI metrics"""
    completeness: float = 0.0
    accuracy: float = 0.0
    consistency: float = 0.0
    validity: float = 0.0
    uniqueness: float = 0.0
    timeliness: float = 0.0
    overall_score: float = 0.0
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    check_results: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DQSIConfig:
    """Configuration for DQSI calculations"""
    weights: Dict[str, float] = field(default_factory=lambda: {
        'completeness': 0.25,
        'accuracy': 0.20,
        'consistency': 0.15,
        'validity': 0.15,
        'uniqueness': 0.15,
        'timeliness': 0.10
    })
    thresholds: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        'excellent': {'min': 0.9, 'max': 1.0},
        'good': {'min': 0.8, 'max': 0.9},
        'fair': {'min': 0.6, 'max': 0.8},
        'poor': {'min': 0.4, 'max': 0.6},
        'critical': {'min': 0.0, 'max': 0.4}
    })
    enabled_dimensions: List[str] = field(default_factory=lambda: [
        'completeness', 'accuracy', 'consistency', 'validity', 'uniqueness', 'timeliness'
    ])

class DQSICalculator(ABC):
    """Abstract base class for DQSI dimension calculators"""
    
    @abstractmethod
    def calculate(self, data: Any, config: Dict[str, Any] = None) -> float:
        """Calculate dimension score"""
        pass
    
    @abstractmethod
    def get_dimension_name(self) -> str:
        """Return dimension name"""
        pass

class CompletenessCalculator(DQSICalculator):
    """Calculator for data completeness dimension"""
    
    def get_dimension_name(self) -> str:
        return "completeness"
    
    def calculate(self, data: Union[pd.DataFrame, Dict, List], config: Dict[str, Any] = None) -> float:
        """
        Calculate completeness score based on missing values
        
        Args:
            data: Input data (DataFrame, Dict, or List)
            config: Configuration parameters
            
        Returns:
            Completeness score between 0 and 1
        """
        try:
            if isinstance(data, pd.DataFrame):
                return self._calculate_dataframe_completeness(data, config)
            elif isinstance(data, dict):
                return self._calculate_dict_completeness(data, config)
            elif isinstance(data, list):
                return self._calculate_list_completeness(data, config)
            else:
                logger.warning(f"Unsupported data type for completeness: {type(data)}")
                return 0.0
        except Exception as e:
            logger.error(f"Error calculating completeness: {e}")
            return 0.0
    
    def _calculate_dataframe_completeness(self, df: pd.DataFrame, config: Dict[str, Any]) -> float:
        """Calculate completeness for DataFrame"""
        if df.empty:
            return 0.0
        
        # Count non-null values
        total_cells = df.size
        non_null_cells = df.count().sum()
        
        # Apply column weights if specified
        if config and 'column_weights' in config:
            weighted_completeness = 0.0
            total_weight = 0.0
            
            for col, weight in config['column_weights'].items():
                if col in df.columns:
                    col_completeness = df[col].count() / len(df)
                    weighted_completeness += col_completeness * weight
                    total_weight += weight
            
            return weighted_completeness / total_weight if total_weight > 0 else 0.0
        
        return non_null_cells / total_cells if total_cells > 0 else 0.0
    
    def _calculate_dict_completeness(self, data: Dict, config: Dict[str, Any]) -> float:
        """Calculate completeness for dictionary data"""
        if not data:
            return 0.0
        
        total_fields = len(data)
        complete_fields = sum(1 for v in data.values() if v is not None and v != "")
        
        return complete_fields / total_fields if total_fields > 0 else 0.0
    
    def _calculate_list_completeness(self, data: List, config: Dict[str, Any]) -> float:
        """Calculate completeness for list data"""
        if not data:
            return 0.0
        
        total_items = len(data)
        complete_items = sum(1 for item in data if item is not None)
        
        return complete_items / total_items if total_items > 0 else 0.0

class AccuracyCalculator(DQSICalculator):
    """Calculator for data accuracy dimension"""
    
    def get_dimension_name(self) -> str:
        return "accuracy"
    
    def calculate(self, data: Any, config: Dict[str, Any] = None) -> float:
        """
        Calculate accuracy score based on reference data or validation rules
        
        Args:
            data: Input data
            config: Configuration with reference data or validation rules
            
        Returns:
            Accuracy score between 0 and 1
        """
        try:
            if not config:
                return 0.5  # Default score when no accuracy measure is available
            
            if 'reference_data' in config:
                return self._calculate_reference_accuracy(data, config['reference_data'])
            elif 'validation_rules' in config:
                return self._calculate_rule_based_accuracy(data, config['validation_rules'])
            else:
                return 0.5
        except Exception as e:
            logger.error(f"Error calculating accuracy: {e}")
            return 0.0
    
    def _calculate_reference_accuracy(self, data: Any, reference_data: Any) -> float:
        """Calculate accuracy against reference data"""
        if isinstance(data, pd.DataFrame) and isinstance(reference_data, pd.DataFrame):
            # Compare DataFrames
            if data.shape != reference_data.shape:
                return 0.0
            
            matches = (data == reference_data).sum().sum()
            total = data.size
            return matches / total if total > 0 else 0.0
        
        elif isinstance(data, dict) and isinstance(reference_data, dict):
            # Compare dictionaries
            matches = sum(1 for k in data.keys() if k in reference_data and data[k] == reference_data[k])
            total = len(data)
            return matches / total if total > 0 else 0.0
        
        return 0.0
    
    def _calculate_rule_based_accuracy(self, data: Any, rules: List[Dict]) -> float:
        """Calculate accuracy based on validation rules"""
        if not rules:
            return 1.0
        
        total_checks = 0
        passed_checks = 0
        
        for rule in rules:
            rule_type = rule.get('type', '')
            
            if rule_type == 'regex':
                pattern = rule.get('pattern', '')
                field = rule.get('field', '')
                
                if isinstance(data, pd.DataFrame) and field in data.columns:
                    total_checks += len(data)
                    passed_checks += data[field].astype(str).str.match(pattern).sum()
                elif isinstance(data, dict) and field in data:
                    total_checks += 1
                    if re.match(pattern, str(data[field])):
                        passed_checks += 1
            
            elif rule_type == 'range':
                field = rule.get('field', '')
                min_val = rule.get('min', float('-inf'))
                max_val = rule.get('max', float('inf'))
                
                if isinstance(data, pd.DataFrame) and field in data.columns:
                    total_checks += len(data)
                    passed_checks += ((data[field] >= min_val) & (data[field] <= max_val)).sum()
                elif isinstance(data, dict) and field in data:
                    total_checks += 1
                    if min_val <= data[field] <= max_val:
                        passed_checks += 1
        
        return passed_checks / total_checks if total_checks > 0 else 1.0

class ConsistencyCalculator(DQSICalculator):
    """Calculator for data consistency dimension"""
    
    def get_dimension_name(self) -> str:
        return "consistency"
    
    def calculate(self, data: Any, config: Dict[str, Any] = None) -> float:
        """
        Calculate consistency score based on data uniformity
        
        Args:
            data: Input data
            config: Configuration parameters
            
        Returns:
            Consistency score between 0 and 1
        """
        try:
            if isinstance(data, pd.DataFrame):
                return self._calculate_dataframe_consistency(data, config)
            elif isinstance(data, dict):
                return self._calculate_dict_consistency(data, config)
            else:
                return 0.5
        except Exception as e:
            logger.error(f"Error calculating consistency: {e}")
            return 0.0
    
    def _calculate_dataframe_consistency(self, df: pd.DataFrame, config: Dict[str, Any]) -> float:
        """Calculate consistency for DataFrame"""
        if df.empty:
            return 0.0
        
        consistency_scores = []
        
        # Check data type consistency
        for col in df.columns:
            if df[col].dtype == 'object':
                # For object columns, check format consistency
                non_null_values = df[col].dropna()
                if len(non_null_values) > 1:
                    # Check if all values follow similar patterns
                    first_value = str(non_null_values.iloc[0])
                    pattern_matches = sum(1 for val in non_null_values.astype(str) 
                                       if self._similar_pattern(first_value, val))
                    consistency_scores.append(pattern_matches / len(non_null_values))
                else:
                    consistency_scores.append(1.0)
            else:
                # For numeric columns, check for outliers
                if df[col].dtype in ['int64', 'float64']:
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                    consistency_scores.append(1 - (outliers / len(df)))
                else:
                    consistency_scores.append(1.0)
        
        return np.mean(consistency_scores) if consistency_scores else 0.0
    
    def _calculate_dict_consistency(self, data: Dict, config: Dict[str, Any]) -> float:
        """Calculate consistency for dictionary data"""
        # For dict data, check if similar keys have consistent value types
        type_groups = defaultdict(list)
        for key, value in data.items():
            type_groups[type(value)].append(key)
        
        # Score based on type consistency
        total_items = len(data)
        consistent_items = sum(len(group) for group in type_groups.values() if len(group) > 1)
        
        return consistent_items / total_items if total_items > 0 else 1.0
    
    def _similar_pattern(self, str1: str, str2: str) -> bool:
        """Check if two strings have similar patterns"""
        # Simple pattern matching - can be enhanced
        pattern1 = re.sub(r'\d+', '#', str1)
        pattern2 = re.sub(r'\d+', '#', str2)
        return pattern1 == pattern2

class ValidityCalculator(DQSICalculator):
    """Calculator for data validity dimension"""
    
    def get_dimension_name(self) -> str:
        return "validity"
    
    def calculate(self, data: Any, config: Dict[str, Any] = None) -> float:
        """
        Calculate validity score based on format and constraint compliance
        
        Args:
            data: Input data
            config: Configuration with validation rules
            
        Returns:
            Validity score between 0 and 1
        """
        try:
            if not config or 'validation_rules' not in config:
                return 0.5  # Default score when no validation rules
            
            return self._validate_against_rules(data, config['validation_rules'])
        except Exception as e:
            logger.error(f"Error calculating validity: {e}")
            return 0.0
    
    def _validate_against_rules(self, data: Any, rules: List[Dict]) -> float:
        """Validate data against specified rules"""
        if not rules:
            return 1.0
        
        total_validations = 0
        passed_validations = 0
        
        for rule in rules:
            rule_type = rule.get('type', '')
            
            if rule_type == 'email':
                field = rule.get('field', '')
                if isinstance(data, pd.DataFrame) and field in data.columns:
                    total_validations += len(data)
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    passed_validations += data[field].astype(str).str.match(email_pattern).sum()
            
            elif rule_type == 'phone':
                field = rule.get('field', '')
                if isinstance(data, pd.DataFrame) and field in data.columns:
                    total_validations += len(data)
                    phone_pattern = r'^\+?1?\d{9,15}$'
                    passed_validations += data[field].astype(str).str.match(phone_pattern).sum()
            
            elif rule_type == 'date':
                field = rule.get('field', '')
                date_format = rule.get('format', '%Y-%m-%d')
                if isinstance(data, pd.DataFrame) and field in data.columns:
                    total_validations += len(data)
                    for val in data[field]:
                        try:
                            datetime.strptime(str(val), date_format)
                            passed_validations += 1
                        except ValueError:
                            pass
            
            elif rule_type == 'custom_regex':
                field = rule.get('field', '')
                pattern = rule.get('pattern', '')
                if isinstance(data, pd.DataFrame) and field in data.columns:
                    total_validations += len(data)
                    passed_validations += data[field].astype(str).str.match(pattern).sum()
        
        return passed_validations / total_validations if total_validations > 0 else 1.0

class UniquenessCalculator(DQSICalculator):
    """Calculator for data uniqueness dimension"""
    
    def get_dimension_name(self) -> str:
        return "uniqueness"
    
    def calculate(self, data: Any, config: Dict[str, Any] = None) -> float:
        """
        Calculate uniqueness score based on duplicate detection
        
        Args:
            data: Input data
            config: Configuration parameters
            
        Returns:
            Uniqueness score between 0 and 1
        """
        try:
            if isinstance(data, pd.DataFrame):
                return self._calculate_dataframe_uniqueness(data, config)
            elif isinstance(data, list):
                return self._calculate_list_uniqueness(data, config)
            else:
                return 1.0
        except Exception as e:
            logger.error(f"Error calculating uniqueness: {e}")
            return 0.0
    
    def _calculate_dataframe_uniqueness(self, df: pd.DataFrame, config: Dict[str, Any]) -> float:
        """Calculate uniqueness for DataFrame"""
        if df.empty:
            return 1.0
        
        if config and 'key_columns' in config:
            # Check uniqueness based on specified key columns
            key_cols = config['key_columns']
            available_cols = [col for col in key_cols if col in df.columns]
            
            if available_cols:
                unique_count = df[available_cols].drop_duplicates().shape[0]
                total_count = df.shape[0]
                return unique_count / total_count if total_count > 0 else 1.0
        
        # Default: check overall row uniqueness
        unique_count = df.drop_duplicates().shape[0]
        total_count = df.shape[0]
        return unique_count / total_count if total_count > 0 else 1.0
    
    def _calculate_list_uniqueness(self, data: List, config: Dict[str, Any]) -> float:
        """Calculate uniqueness for list data"""
        if not data:
            return 1.0
        
        unique_count = len(set(data))
        total_count = len(data)
        return unique_count / total_count if total_count > 0 else 1.0

class TimelinessCalculator(DQSICalculator):
    """Calculator for data timeliness dimension"""
    
    def get_dimension_name(self) -> str:
        return "timeliness"
    
    def calculate(self, data: Any, config: Dict[str, Any] = None) -> float:
        """
        Calculate timeliness score based on data freshness
        
        Args:
            data: Input data
            config: Configuration with timestamp fields and freshness requirements
            
        Returns:
            Timeliness score between 0 and 1
        """
        try:
            if not config or 'timestamp_field' not in config:
                return 0.5  # Default score when no timestamp info
            
            return self._calculate_freshness_score(data, config)
        except Exception as e:
            logger.error(f"Error calculating timeliness: {e}")
            return 0.0
    
    def _calculate_freshness_score(self, data: Any, config: Dict[str, Any]) -> float:
        """Calculate freshness score based on timestamps"""
        timestamp_field = config.get('timestamp_field', '')
        max_age_hours = config.get('max_age_hours', 24)
        
        current_time = datetime.now()
        
        if isinstance(data, pd.DataFrame) and timestamp_field in data.columns:
            # Convert timestamps to datetime
            timestamps = pd.to_datetime(data[timestamp_field], errors='coerce')
            timestamps = timestamps.dropna()
            
            if timestamps.empty:
                return 0.0
            
            # Calculate age in hours
            ages = (current_time - timestamps).dt.total_seconds() / 3600
            
            # Score based on freshness
            fresh_count = (ages <= max_age_hours).sum()
            total_count = len(timestamps)
            
            return fresh_count / total_count if total_count > 0 else 0.0
        
        elif isinstance(data, dict) and timestamp_field in data:
            timestamp = pd.to_datetime(data[timestamp_field], errors='coerce')
            if pd.isna(timestamp):
                return 0.0
            
            age_hours = (current_time - timestamp).total_seconds() / 3600
            return 1.0 if age_hours <= max_age_hours else 0.0
        
        return 0.0

class DataQualitySufficiencyIndex:
    """
    Main DQSI calculator that orchestrates all dimension calculations
    """
    
    def __init__(self, config: DQSIConfig = None):
        """
        Initialize DQSI calculator with configuration
        
        Args:
            config: DQSI configuration object
        """
        self.config = config or DQSIConfig()
        
        # Initialize dimension calculators
        self.calculators = {
            'completeness': CompletenessCalculator(),
            'accuracy': AccuracyCalculator(),
            'consistency': ConsistencyCalculator(),
            'validity': ValidityCalculator(),
            'uniqueness': UniquenessCalculator(),
            'timeliness': TimelinessCalculator()
        }
        
        logger.info("Data Quality Sufficiency Index calculator initialized")
    
    def calculate_dqsi(self, data: Any, dimension_configs: Dict[str, Dict[str, Any]] = None) -> DQSIMetrics:
        """
        Calculate complete DQSI score with all dimensions
        
        Args:
            data: Input data to assess
            dimension_configs: Configuration for each dimension
            
        Returns:
            DQSIMetrics object with all scores and details
        """
        try:
            dimension_configs = dimension_configs or {}
            dimension_scores = {}
            check_results = {}
            
            # Calculate each enabled dimension
            for dimension in self.config.enabled_dimensions:
                if dimension in self.calculators:
                    calculator = self.calculators[dimension]
                    config = dimension_configs.get(dimension, {})
                    
                    score = calculator.calculate(data, config)
                    dimension_scores[dimension] = score
                    
                    # Store detailed results
                    check_results[dimension] = {
                        'score': score,
                        'status': self._get_dimension_status(score),
                        'config_used': config
                    }
                    
                    logger.debug(f"Dimension {dimension}: {score:.3f}")
            
            # Calculate overall weighted score
            overall_score = self._calculate_weighted_score(dimension_scores)
            
            # Create metrics object
            metrics = DQSIMetrics(
                completeness=dimension_scores.get('completeness', 0.0),
                accuracy=dimension_scores.get('accuracy', 0.0),
                consistency=dimension_scores.get('consistency', 0.0),
                validity=dimension_scores.get('validity', 0.0),
                uniqueness=dimension_scores.get('uniqueness', 0.0),
                timeliness=dimension_scores.get('timeliness', 0.0),
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                check_results=check_results
            )
            
            logger.info(f"DQSI calculated: {overall_score:.3f} ({self._get_overall_status(overall_score)})")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating DQSI: {e}")
            return DQSIMetrics()
    
    def _calculate_weighted_score(self, dimension_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for dimension, score in dimension_scores.items():
            weight = self.config.weights.get(dimension, 0.0)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _get_dimension_status(self, score: float) -> str:
        """Get status label for dimension score"""
        for status, thresholds in self.config.thresholds.items():
            if thresholds['min'] <= score <= thresholds['max']:
                return status
        return 'unknown'
    
    def _get_overall_status(self, score: float) -> str:
        """Get overall status label"""
        return self._get_dimension_status(score)
    
    def generate_report(self, metrics: DQSIMetrics, include_details: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive DQSI report
        
        Args:
            metrics: DQSI metrics object
            include_details: Whether to include detailed check results
            
        Returns:
            Dictionary containing formatted report
        """
        report = {
            'overall_score': round(metrics.overall_score, 3),
            'overall_status': self._get_overall_status(metrics.overall_score),
            'dimension_scores': {
                dim: round(score, 3) for dim, score in metrics.dimension_scores.items()
            },
            'dimension_statuses': {
                dim: self._get_dimension_status(score) 
                for dim, score in metrics.dimension_scores.items()
            },
            'weights_used': self.config.weights,
            'timestamp': datetime.now().isoformat()
        }
        
        if include_details:
            report['detailed_results'] = metrics.check_results
        
        return report
    
    def get_improvement_recommendations(self, metrics: DQSIMetrics) -> List[Dict[str, Any]]:
        """
        Generate improvement recommendations based on DQSI results
        
        Args:
            metrics: DQSI metrics object
            
        Returns:
            List of improvement recommendations
        """
        recommendations = []
        
        for dimension, score in metrics.dimension_scores.items():
            if score < 0.8:  # Consider scores below 0.8 as needing improvement
                rec = {
                    'dimension': dimension,
                    'current_score': round(score, 3),
                    'target_score': 0.9,
                    'priority': 'high' if score < 0.5 else 'medium',
                    'suggestions': self._get_dimension_suggestions(dimension, score)
                }
                recommendations.append(rec)
        
        # Sort by priority and score
        recommendations.sort(key=lambda x: (x['priority'] == 'high', -x['current_score']))
        
        return recommendations
    
    def _get_dimension_suggestions(self, dimension: str, score: float) -> List[str]:
        """Get improvement suggestions for specific dimension"""
        suggestions = {
            'completeness': [
                "Implement data validation at source",
                "Add required field constraints",
                "Create data quality monitoring alerts",
                "Review data collection processes"
            ],
            'accuracy': [
                "Implement reference data validation",
                "Add data quality rules and checks",
                "Create data profiling processes",
                "Review data entry procedures"
            ],
            'consistency': [
                "Standardize data formats across systems",
                "Implement master data management",
                "Add data transformation rules",
                "Review data integration processes"
            ],
            'validity': [
                "Add format validation rules",
                "Implement data type constraints",
                "Create data quality checks",
                "Review data schema definitions"
            ],
            'uniqueness': [
                "Implement duplicate detection",
                "Add unique constraints",
                "Create data deduplication processes",
                "Review data collection procedures"
            ],
            'timeliness': [
                "Implement real-time data processing",
                "Add data freshness monitoring",
                "Create data update schedules",
                "Review data pipeline performance"
            ]
        }
        
        return suggestions.get(dimension, ["Review data quality processes"])