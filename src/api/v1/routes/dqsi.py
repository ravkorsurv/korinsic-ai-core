"""
Data Quality Sufficiency Index (DQSI) API routes.

This module contains endpoints for calculating data quality scores
and providing data quality assessments using the DQSI framework.
"""

from flask import request, jsonify
from datetime import datetime
import logging
import pandas as pd
from typing import Dict, Any, List
import json

from ....core.dqsi_score import DataQualitySufficiencyIndex, DQSIConfig
from ....utils.logger import setup_logger
from ..schemas.request_schemas import DQSIRequestSchema
from ..schemas.response_schemas import DQSIResponseSchema
from ..middleware.validation import validate_request
from ..middleware.error_handling import handle_api_errors
from .. import api_v1

logger = setup_logger()

# Initialize DQSI service
dqsi_service = DataQualitySufficiencyIndex()


@api_v1.route('/dqsi/calculate', methods=['POST'])
@handle_api_errors
@validate_request(DQSIRequestSchema)
def calculate_dqsi_score():
    """
    Calculate Data Quality Sufficiency Index score for provided data.
    
    This endpoint processes data through various quality dimensions
    (completeness, accuracy, consistency, validity, uniqueness, timeliness)
    to provide a comprehensive data quality assessment.
    
    Returns:
        JSON response with DQSI scores, dimension details, and recommendations
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract request parameters
        dataset = data.get('dataset', {})
        dimension_configs = data.get('dimension_configs', {})
        custom_weights = data.get('custom_weights', {})
        enabled_dimensions = data.get('enabled_dimensions', [])
        include_recommendations = data.get('include_recommendations', True)
        
        # Create DQSI configuration
        config = DQSIConfig()
        if custom_weights:
            config.weights.update(custom_weights)
        if enabled_dimensions:
            config.enabled_dimensions = enabled_dimensions
        
        # Initialize DQSI calculator with custom config
        dqsi_calculator = DataQualitySufficiencyIndex(config)
        
        # Process data
        processed_data = _process_input_data(dataset)
        
        # Calculate DQSI metrics
        metrics = dqsi_calculator.calculate_dqsi(processed_data, dimension_configs)
        
        # Generate comprehensive report
        report = dqsi_calculator.generate_report(metrics, include_details=True)
        
        # Get improvement recommendations if requested
        recommendations = []
        if include_recommendations:
            recommendations = dqsi_calculator.get_improvement_recommendations(metrics)
        
        # Build response
        response = DQSIResponseSchema().build_response(
            metrics=metrics,
            report=report,
            recommendations=recommendations
        )
        
        logger.info(f"DQSI calculated: {metrics.overall_score:.3f} for dataset with {_get_data_size(processed_data)} records")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in calculate_dqsi_score: {str(e)}")
        raise


@api_v1.route('/dqsi/batch', methods=['POST'])
@handle_api_errors
@validate_request(DQSIRequestSchema)
def calculate_batch_dqsi():
    """
    Calculate DQSI scores for multiple datasets in batch.
    
    This endpoint allows for efficient processing of multiple datasets
    in a single request, with optional comparison analysis.
    
    Returns:
        JSON response with batch DQSI results and comparisons
    """
    try:
        data = request.get_json()
        batch_data = data.get('batch_data', [])
        
        if not batch_data:
            return jsonify({'error': 'No batch data provided'}), 400
        
        # Extract configuration
        dimension_configs = data.get('dimension_configs', {})
        custom_weights = data.get('custom_weights', {})
        include_comparison = data.get('include_comparison', True)
        
        # Create DQSI configuration
        config = DQSIConfig()
        if custom_weights:
            config.weights.update(custom_weights)
        
        dqsi_calculator = DataQualitySufficiencyIndex(config)
        
        # Process batch analysis
        batch_results = []
        for i, dataset_info in enumerate(batch_data):
            dataset_id = dataset_info.get('id', f'dataset_{i}')
            dataset = dataset_info.get('dataset', {})
            
            # Process data
            processed_data = _process_input_data(dataset)
            
            # Calculate DQSI metrics
            metrics = dqsi_calculator.calculate_dqsi(processed_data, dimension_configs)
            
            # Generate report
            report = dqsi_calculator.generate_report(metrics)
            
            batch_results.append({
                'dataset_id': dataset_id,
                'dqsi_score': metrics.overall_score,
                'dimension_scores': metrics.dimension_scores,
                'report': report
            })
        
        # Generate comparison analysis if requested
        comparison_analysis = {}
        if include_comparison and len(batch_results) > 1:
            comparison_analysis = _generate_comparison_analysis(batch_results)
        
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'batch_id': f"dqsi_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'results': batch_results,
            'summary': {
                'total_datasets': len(batch_results),
                'average_dqsi': sum(r['dqsi_score'] for r in batch_results) / len(batch_results),
                'best_performer': max(batch_results, key=lambda x: x['dqsi_score'])['dataset_id'],
                'worst_performer': min(batch_results, key=lambda x: x['dqsi_score'])['dataset_id']
            },
            'comparison_analysis': comparison_analysis
        }
        
        logger.info(f"Batch DQSI analysis completed for {len(batch_data)} datasets")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in calculate_batch_dqsi: {str(e)}")
        raise


@api_v1.route('/dqsi/monitor', methods=['POST'])
@handle_api_errors
@validate_request(DQSIRequestSchema)
def monitor_dqsi_trends():
    """
    Monitor DQSI trends over time for data quality tracking.
    
    This endpoint calculates DQSI scores for time-series data
    and provides trend analysis and alerting capabilities.
    
    Returns:
        JSON response with DQSI trends and quality alerts
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract request parameters
        time_series_data = data.get('time_series_data', [])
        alerting_thresholds = data.get('alerting_thresholds', {
            'critical': 0.4,
            'warning': 0.6,
            'target': 0.8
        })
        trend_analysis_window = data.get('trend_analysis_window', 7)  # days
        
        # Create DQSI configuration
        config = DQSIConfig()
        if data.get('custom_weights'):
            config.weights.update(data['custom_weights'])
        
        dqsi_calculator = DataQualitySufficiencyIndex(config)
        
        # Process time series analysis
        time_series_results = []
        for entry in time_series_data:
            timestamp = entry.get('timestamp', datetime.utcnow().isoformat())
            dataset = entry.get('dataset', {})
            
            # Process data
            processed_data = _process_input_data(dataset)
            
            # Calculate DQSI metrics
            metrics = dqsi_calculator.calculate_dqsi(processed_data, data.get('dimension_configs', {}))
            
            time_series_results.append({
                'timestamp': timestamp,
                'dqsi_score': metrics.overall_score,
                'dimension_scores': metrics.dimension_scores,
                'status': dqsi_calculator._get_overall_status(metrics.overall_score)
            })
        
        # Generate trend analysis
        trend_analysis = _generate_trend_analysis(time_series_results, trend_analysis_window)
        
        # Generate alerts
        alerts = _generate_dqsi_alerts(time_series_results, alerting_thresholds)
        
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'monitoring_id': f"dqsi_monitor_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'time_series_results': time_series_results,
            'trend_analysis': trend_analysis,
            'alerts': alerts,
            'summary': {
                'total_data_points': len(time_series_results),
                'current_score': time_series_results[-1]['dqsi_score'] if time_series_results else 0.0,
                'trend_direction': trend_analysis.get('trend_direction', 'stable'),
                'alert_count': len(alerts)
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in monitor_dqsi_trends: {str(e)}")
        raise


@api_v1.route('/dqsi/config', methods=['GET'])
@handle_api_errors
def get_dqsi_configuration():
    """
    Get current DQSI configuration settings.
    
    Returns:
        JSON response with DQSI configuration details
    """
    try:
        config = DQSIConfig()
        
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'configuration': {
                'weights': config.weights,
                'thresholds': config.thresholds,
                'enabled_dimensions': config.enabled_dimensions
            },
            'available_dimensions': [
                {
                    'name': 'completeness',
                    'description': 'Measure of missing or null values',
                    'weight': config.weights.get('completeness', 0.0)
                },
                {
                    'name': 'accuracy',
                    'description': 'Data correctness and precision',
                    'weight': config.weights.get('accuracy', 0.0)
                },
                {
                    'name': 'consistency',
                    'description': 'Data uniformity across sources/time',
                    'weight': config.weights.get('consistency', 0.0)
                },
                {
                    'name': 'validity',
                    'description': 'Adherence to defined formats and constraints',
                    'weight': config.weights.get('validity', 0.0)
                },
                {
                    'name': 'uniqueness',
                    'description': 'Duplicate record detection',
                    'weight': config.weights.get('uniqueness', 0.0)
                },
                {
                    'name': 'timeliness',
                    'description': 'Data freshness and currency',
                    'weight': config.weights.get('timeliness', 0.0)
                }
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_dqsi_configuration: {str(e)}")
        raise


@api_v1.route('/dqsi/validate', methods=['POST'])
@handle_api_errors
@validate_request(DQSIRequestSchema)
def validate_data_quality():
    """
    Validate data quality against specified thresholds.
    
    This endpoint performs data quality validation and returns
    pass/fail status along with detailed assessment results.
    
    Returns:
        JSON response with validation results and recommendations
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract request parameters
        dataset = data.get('dataset', {})
        validation_thresholds = data.get('validation_thresholds', {
            'overall_minimum': 0.8,
            'dimension_minimums': {
                'completeness': 0.9,
                'accuracy': 0.8,
                'consistency': 0.7,
                'validity': 0.9,
                'uniqueness': 0.95,
                'timeliness': 0.8
            }
        })
        
        # Create DQSI configuration
        config = DQSIConfig()
        if data.get('custom_weights'):
            config.weights.update(data['custom_weights'])
        
        dqsi_calculator = DataQualitySufficiencyIndex(config)
        
        # Process data
        processed_data = _process_input_data(dataset)
        
        # Calculate DQSI metrics
        metrics = dqsi_calculator.calculate_dqsi(processed_data, data.get('dimension_configs', {}))
        
        # Perform validation
        validation_results = _perform_validation(metrics, validation_thresholds)
        
        # Generate recommendations for failed validations
        recommendations = []
        if not validation_results['overall_pass']:
            recommendations = dqsi_calculator.get_improvement_recommendations(metrics)
        
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'validation_id': f"dqsi_validation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'validation_results': validation_results,
            'dqsi_metrics': {
                'overall_score': metrics.overall_score,
                'dimension_scores': metrics.dimension_scores
            },
            'recommendations': recommendations,
            'thresholds_used': validation_thresholds
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in validate_data_quality: {str(e)}")
        raise


# Helper functions

def _process_input_data(dataset: Dict[str, Any]) -> Any:
    """Process input data into appropriate format for DQSI calculation"""
    try:
        # If dataset contains 'format' field, process accordingly
        data_format = dataset.get('format', 'dict')
        
        if data_format == 'dataframe' and 'data' in dataset:
            # Convert to pandas DataFrame
            return pd.DataFrame(dataset['data'])
        elif data_format == 'csv' and 'csv_data' in dataset:
            # Process CSV data
            import io
            return pd.read_csv(io.StringIO(dataset['csv_data']))
        elif data_format == 'json' and 'json_data' in dataset:
            # Process JSON data
            return dataset['json_data']
        else:
            # Return as-is for dict format
            return dataset.get('data', dataset)
    
    except Exception as e:
        logger.error(f"Error processing input data: {e}")
        return dataset


def _get_data_size(data: Any) -> int:
    """Get the size of the data"""
    try:
        if isinstance(data, pd.DataFrame):
            return len(data)
        elif isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return len(data)
        else:
            return 0
    except:
        return 0


def _generate_comparison_analysis(batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate comparison analysis for batch results"""
    try:
        scores = [r['dqsi_score'] for r in batch_results]
        
        # Calculate statistics
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        std_dev = (sum((x - avg_score) ** 2 for x in scores) / len(scores)) ** 0.5
        
        # Find dimension with highest variance
        dimension_variances = {}
        for dim in ['completeness', 'accuracy', 'consistency', 'validity', 'uniqueness', 'timeliness']:
            dim_scores = [r['dimension_scores'].get(dim, 0) for r in batch_results]
            if dim_scores:
                dim_avg = sum(dim_scores) / len(dim_scores)
                dim_var = sum((x - dim_avg) ** 2 for x in dim_scores) / len(dim_scores)
                dimension_variances[dim] = dim_var
        
        highest_variance_dim = max(dimension_variances.keys(), key=lambda x: dimension_variances[x]) if dimension_variances else None
        
        return {
            'statistics': {
                'average_score': avg_score,
                'minimum_score': min_score,
                'maximum_score': max_score,
                'standard_deviation': std_dev,
                'score_range': max_score - min_score
            },
            'insights': {
                'highest_variance_dimension': highest_variance_dim,
                'performance_consistency': 'high' if std_dev < 0.1 else 'medium' if std_dev < 0.2 else 'low',
                'overall_quality_level': 'excellent' if avg_score >= 0.9 else 'good' if avg_score >= 0.8 else 'needs_improvement'
            }
        }
    
    except Exception as e:
        logger.error(f"Error generating comparison analysis: {e}")
        return {}


def _generate_trend_analysis(time_series_results: List[Dict[str, Any]], window: int) -> Dict[str, Any]:
    """Generate trend analysis for time series data"""
    try:
        if len(time_series_results) < 2:
            return {'trend_direction': 'insufficient_data'}
        
        # Calculate trend over the window
        recent_scores = [r['dqsi_score'] for r in time_series_results[-window:]]
        
        if len(recent_scores) < 2:
            return {'trend_direction': 'insufficient_data'}
        
        # Simple linear trend calculation
        x = list(range(len(recent_scores)))
        n = len(recent_scores)
        
        # Calculate slope
        sum_x = sum(x)
        sum_y = sum(recent_scores)
        sum_xy = sum(x[i] * recent_scores[i] for i in range(n))
        sum_x2 = sum(xi ** 2 for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Determine trend direction
        if slope > 0.01:
            trend_direction = 'improving'
        elif slope < -0.01:
            trend_direction = 'declining'
        else:
            trend_direction = 'stable'
        
        return {
            'trend_direction': trend_direction,
            'trend_slope': slope,
            'window_size': window,
            'recent_average': sum(recent_scores) / len(recent_scores),
            'volatility': (sum((x - sum(recent_scores) / len(recent_scores)) ** 2 for x in recent_scores) / len(recent_scores)) ** 0.5
        }
    
    except Exception as e:
        logger.error(f"Error generating trend analysis: {e}")
        return {'trend_direction': 'error'}


def _generate_dqsi_alerts(time_series_results: List[Dict[str, Any]], thresholds: Dict[str, float]) -> List[Dict[str, Any]]:
    """Generate alerts based on DQSI scores and thresholds"""
    alerts = []
    
    try:
        for i, result in enumerate(time_series_results):
            score = result['dqsi_score']
            timestamp = result['timestamp']
            
            # Check for threshold violations
            if score <= thresholds.get('critical', 0.4):
                alerts.append({
                    'timestamp': timestamp,
                    'severity': 'critical',
                    'message': f'DQSI score ({score:.3f}) below critical threshold ({thresholds.get("critical", 0.4)})',
                    'dimension_details': result['dimension_scores']
                })
            elif score <= thresholds.get('warning', 0.6):
                alerts.append({
                    'timestamp': timestamp,
                    'severity': 'warning',
                    'message': f'DQSI score ({score:.3f}) below warning threshold ({thresholds.get("warning", 0.6)})',
                    'dimension_details': result['dimension_scores']
                })
            
            # Check for sudden drops
            if i > 0:
                prev_score = time_series_results[i-1]['dqsi_score']
                if score < prev_score - 0.1:  # 10% drop
                    alerts.append({
                        'timestamp': timestamp,
                        'severity': 'warning',
                        'message': f'Sudden DQSI drop detected: {prev_score:.3f} → {score:.3f}',
                        'dimension_details': result['dimension_scores']
                    })
    
    except Exception as e:
        logger.error(f"Error generating DQSI alerts: {e}")
    
    return alerts


def _perform_validation(metrics: Any, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    """Perform data quality validation against thresholds"""
    try:
        overall_minimum = thresholds.get('overall_minimum', 0.8)
        dimension_minimums = thresholds.get('dimension_minimums', {})
        
        # Check overall score
        overall_pass = metrics.overall_score >= overall_minimum
        
        # Check dimension scores
        dimension_results = {}
        for dimension, score in metrics.dimension_scores.items():
            required_minimum = dimension_minimums.get(dimension, 0.8)
            dimension_pass = score >= required_minimum
            dimension_results[dimension] = {
                'score': score,
                'required_minimum': required_minimum,
                'pass': dimension_pass
            }
        
        # Calculate pass/fail counts
        dimension_passes = sum(1 for r in dimension_results.values() if r['pass'])
        dimension_fails = len(dimension_results) - dimension_passes
        
        return {
            'overall_pass': overall_pass,
            'overall_score': metrics.overall_score,
            'overall_minimum': overall_minimum,
            'dimension_results': dimension_results,
            'summary': {
                'dimensions_passed': dimension_passes,
                'dimensions_failed': dimension_fails,
                'overall_validation_status': 'PASS' if overall_pass else 'FAIL'
            }
        }
    
    except Exception as e:
        logger.error(f"Error performing validation: {e}")
        return {'overall_pass': False, 'error': str(e)}