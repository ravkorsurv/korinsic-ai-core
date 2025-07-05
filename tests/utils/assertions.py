"""
Custom assertion functions for test validation.
"""

from typing import Dict, Any, List, Optional, Union


def assert_risk_score_valid(risk_score: Dict[str, Any], 
                           min_score: float = 0.0, 
                           max_score: float = 1.0) -> None:
    """
    Assert that a risk score dictionary has valid structure and values.
    
    Args:
        risk_score: Risk score dictionary to validate
        min_score: Minimum valid score value
        max_score: Maximum valid score value
        
    Raises:
        AssertionError: If risk score is invalid
    """
    # Check required fields
    required_fields = ['overall_score', 'risk_level']
    for field in required_fields:
        assert field in risk_score, f"Missing required field: {field}"
    
    # Validate overall score
    overall_score = risk_score['overall_score']
    assert isinstance(overall_score, (int, float)), "overall_score must be numeric"
    assert min_score <= overall_score <= max_score, \
        f"overall_score {overall_score} not in valid range [{min_score}, {max_score}]"
    
    # Validate risk level
    risk_level = risk_score['risk_level']
    valid_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    assert risk_level in valid_levels, \
        f"risk_level '{risk_level}' not in valid levels: {valid_levels}"
    
    # Validate evidence factors if present
    if 'evidence_factors' in risk_score:
        evidence_factors = risk_score['evidence_factors']
        assert isinstance(evidence_factors, dict), "evidence_factors must be a dictionary"
        
        for factor_name, factor_value in evidence_factors.items():
            assert isinstance(factor_value, (int, float)), \
                f"Evidence factor '{factor_name}' must be numeric"
            assert 0.0 <= factor_value <= 1.0, \
                f"Evidence factor '{factor_name}' value {factor_value} not in range [0, 1]"


def assert_alert_fields_present(alert: Dict[str, Any], 
                               required_fields: Optional[List[str]] = None) -> None:
    """
    Assert that an alert has all required fields.
    
    Args:
        alert: Alert dictionary to validate
        required_fields: List of required fields (uses default if None)
        
    Raises:
        AssertionError: If required fields are missing
    """
    if required_fields is None:
        required_fields = [
            'id', 'timestamp', 'type', 'severity', 'risk_score', 
            'description', 'trader_id'
        ]
    
    for field in required_fields:
        assert field in alert, f"Alert missing required field: {field}"
    
    # Validate specific field types and values
    assert isinstance(alert['risk_score'], (int, float)), "risk_score must be numeric"
    assert 0.0 <= alert['risk_score'] <= 1.0, "risk_score must be between 0 and 1"
    
    valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    assert alert['severity'] in valid_severities, \
        f"Invalid severity '{alert['severity']}', must be one of: {valid_severities}"
    
    valid_types = ['INSIDER_DEALING', 'SPOOFING', 'GENERAL']
    assert alert['type'] in valid_types, \
        f"Invalid alert type '{alert['type']}', must be one of: {valid_types}"


def assert_regulatory_rationale_complete(rationale: Dict[str, Any]) -> None:
    """
    Assert that a regulatory rationale has all required components.
    
    Args:
        rationale: Regulatory rationale dictionary to validate
        
    Raises:
        AssertionError: If rationale is incomplete
    """
    required_fields = [
        'alert_id', 'deterministic_narrative', 'inference_paths',
        'voi_analysis', 'sensitivity_report', 'regulatory_frameworks'
    ]
    
    for field in required_fields:
        assert field in rationale, f"Regulatory rationale missing field: {field}"
    
    # Validate deterministic narrative
    narrative = rationale['deterministic_narrative']
    assert isinstance(narrative, str), "deterministic_narrative must be a string"
    assert len(narrative) > 0, "deterministic_narrative cannot be empty"
    
    # Validate inference paths
    inference_paths = rationale['inference_paths']
    assert isinstance(inference_paths, list), "inference_paths must be a list"
    
    for i, path in enumerate(inference_paths):
        assert isinstance(path, dict), f"inference_path[{i}] must be a dictionary"
        
        path_required_fields = ['node_name', 'evidence_value', 'probability', 'contribution']
        for field in path_required_fields:
            assert field in path, f"inference_path[{i}] missing field: {field}"
        
        # Validate probability and contribution are numeric and in valid range
        assert isinstance(path['probability'], (int, float)), \
            f"inference_path[{i}] probability must be numeric"
        assert 0.0 <= path['probability'] <= 1.0, \
            f"inference_path[{i}] probability must be between 0 and 1"
        
        assert isinstance(path['contribution'], (int, float)), \
            f"inference_path[{i}] contribution must be numeric"
    
    # Validate VoI analysis
    voi_analysis = rationale['voi_analysis']
    assert isinstance(voi_analysis, dict), "voi_analysis must be a dictionary"
    
    # Validate sensitivity report
    sensitivity_report = rationale['sensitivity_report']
    assert isinstance(sensitivity_report, dict), "sensitivity_report must be a dictionary"


def assert_api_response_structure(response: Dict[str, Any], 
                                response_type: str = "analysis") -> None:
    """
    Assert that an API response has the expected structure.
    
    Args:
        response: API response dictionary to validate
        response_type: Type of response ('analysis', 'simulation', 'models_info')
        
    Raises:
        AssertionError: If response structure is invalid
    """
    # Common fields for all responses
    common_fields = ['timestamp']
    for field in common_fields:
        assert field in response, f"Response missing common field: {field}"
    
    if response_type == "analysis":
        required_fields = ['analysis_id', 'risk_scores', 'alerts', 'processed_data_summary']
        for field in required_fields:
            assert field in response, f"Analysis response missing field: {field}"
        
        # Validate risk scores structure
        risk_scores = response['risk_scores']
        assert 'insider_dealing' in risk_scores, "Missing insider_dealing risk score"
        assert 'spoofing' in risk_scores, "Missing spoofing risk score"
        
        # Validate each risk score
        for risk_type in ['insider_dealing', 'spoofing']:
            assert_risk_score_valid(risk_scores[risk_type])
        
        # Validate alerts
        alerts = response['alerts']
        assert isinstance(alerts, list), "alerts must be a list"
        for alert in alerts:
            assert_alert_fields_present(alert)
    
    elif response_type == "simulation":
        required_fields = ['scenario_type', 'parameters', 'risk_score', 'simulated_data']
        for field in required_fields:
            assert field in response, f"Simulation response missing field: {field}"
        
        # Validate risk score
        assert_risk_score_valid(response['risk_score'])
        
        # Validate simulated data
        simulated_data = response['simulated_data']
        assert isinstance(simulated_data, dict), "simulated_data must be a dictionary"
    
    elif response_type == "models_info":
        required_fields = ['models']
        for field in required_fields:
            assert field in response, f"Models info response missing field: {field}"
        
        models = response['models']
        assert isinstance(models, dict), "models must be a dictionary"


def assert_performance_metrics(metrics: Dict[str, Any], 
                             max_response_time: float = 5.0,
                             max_memory_mb: float = 500.0) -> None:
    """
    Assert that performance metrics are within acceptable limits.
    
    Args:
        metrics: Performance metrics dictionary
        max_response_time: Maximum acceptable response time in seconds
        max_memory_mb: Maximum acceptable memory usage in MB
        
    Raises:
        AssertionError: If performance metrics exceed limits
    """
    if 'response_time' in metrics:
        response_time = metrics['response_time']
        assert response_time <= max_response_time, \
            f"Response time {response_time}s exceeds limit {max_response_time}s"
    
    if 'memory_usage_mb' in metrics:
        memory_usage = metrics['memory_usage_mb']
        assert memory_usage <= max_memory_mb, \
            f"Memory usage {memory_usage}MB exceeds limit {max_memory_mb}MB"
    
    if 'cpu_usage_percent' in metrics:
        cpu_usage = metrics['cpu_usage_percent']
        assert 0 <= cpu_usage <= 100, \
            f"CPU usage {cpu_usage}% not in valid range [0, 100]"


def assert_data_quality(data: Dict[str, Any], 
                       min_trades: int = 1,
                       required_fields: Optional[List[str]] = None) -> None:
    """
    Assert that test data meets quality requirements.
    
    Args:
        data: Test data dictionary to validate
        min_trades: Minimum number of trades required
        required_fields: List of required top-level fields
        
    Raises:
        AssertionError: If data quality is insufficient
    """
    if required_fields is None:
        required_fields = ['trades', 'trader_info']
    
    for field in required_fields:
        assert field in data, f"Test data missing required field: {field}"
    
    # Validate trades
    if 'trades' in data:
        trades = data['trades']
        assert isinstance(trades, list), "trades must be a list"
        assert len(trades) >= min_trades, \
            f"Insufficient trades: {len(trades)} < {min_trades}"
        
        for i, trade in enumerate(trades):
            trade_required_fields = ['id', 'timestamp', 'instrument', 'volume', 'price']
            for field in trade_required_fields:
                assert field in trade, f"Trade[{i}] missing field: {field}"
    
    # Validate trader info
    if 'trader_info' in data:
        trader_info = data['trader_info']
        assert isinstance(trader_info, dict), "trader_info must be a dictionary"
        
        trader_required_fields = ['id', 'role', 'access_level']
        for field in trader_required_fields:
            assert field in trader_info, f"trader_info missing field: {field}"


def assert_model_consistency(model_results: List[Dict[str, Any]], 
                           tolerance: float = 0.1) -> None:
    """
    Assert that multiple model runs produce consistent results.
    
    Args:
        model_results: List of model result dictionaries
        tolerance: Maximum allowed variance in results
        
    Raises:
        AssertionError: If results are inconsistent
    """
    assert len(model_results) >= 2, "Need at least 2 results for consistency check"
    
    # Extract overall scores
    scores = [result.get('overall_score', 0.0) for result in model_results]
    
    # Calculate variance
    mean_score = sum(scores) / len(scores)
    variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
    std_dev = variance ** 0.5
    
    assert std_dev <= tolerance, \
        f"Model results inconsistent: std_dev {std_dev:.4f} > tolerance {tolerance}"


def assert_threshold_behavior(risk_score: float, 
                            threshold: float,
                            alert_generated: bool) -> None:
    """
    Assert that alert generation follows threshold behavior correctly.
    
    Args:
        risk_score: Risk score value
        threshold: Alert threshold
        alert_generated: Whether an alert was generated
        
    Raises:
        AssertionError: If threshold behavior is incorrect
    """
    if risk_score >= threshold:
        assert alert_generated, \
            f"Alert should be generated: risk_score {risk_score} >= threshold {threshold}"
    else:
        assert not alert_generated, \
            f"Alert should not be generated: risk_score {risk_score} < threshold {threshold}"


def assert_temporal_consistency(events: List[Dict[str, Any]], 
                              time_field: str = 'timestamp') -> None:
    """
    Assert that events are in chronological order.
    
    Args:
        events: List of event dictionaries with timestamps
        time_field: Name of the timestamp field
        
    Raises:
        AssertionError: If events are not chronologically ordered
    """
    if len(events) <= 1:
        return  # Single event or empty list is always consistent
    
    for i in range(1, len(events)):
        prev_time = events[i-1][time_field]
        curr_time = events[i][time_field]
        
        assert prev_time <= curr_time, \
            f"Events not in chronological order: {prev_time} > {curr_time} at index {i}"


def assert_evidence_sufficiency_index(esi_result: Dict[str, Any], 
                                     min_esi: float = 0.0,
                                     max_esi: float = 1.0) -> None:
    """
    Assert that Evidence Sufficiency Index result is valid.
    
    Args:
        esi_result: ESI result dictionary
        min_esi: Minimum valid ESI value
        max_esi: Maximum valid ESI value
        
    Raises:
        AssertionError: If ESI result is invalid
    """
    required_fields = [
        'evidence_sufficiency_index', 'esi_badge', 'node_count', 
        'mean_confidence', 'components'
    ]
    
    for field in required_fields:
        assert field in esi_result, f"ESI result missing field: {field}"
    
    # Validate ESI value
    esi_value = esi_result['evidence_sufficiency_index']
    assert isinstance(esi_value, (int, float)), "ESI value must be numeric"
    assert min_esi <= esi_value <= max_esi, \
        f"ESI value {esi_value} not in valid range [{min_esi}, {max_esi}]"
    
    # Validate ESI badge
    valid_badges = ['Weak', 'Moderate', 'Strong', 'Excellent']
    esi_badge = esi_result['esi_badge']
    assert esi_badge in valid_badges, \
        f"Invalid ESI badge '{esi_badge}', must be one of: {valid_badges}"
    
    # Validate components
    components = esi_result['components']
    assert isinstance(components, dict), "ESI components must be a dictionary"
    
    component_fields = [
        'node_activation_ratio', 'mean_confidence_score', 
        'fallback_ratio', 'contribution_entropy'
    ]
    
    for field in component_fields:
        if field in components:
            value = components[field]
            assert isinstance(value, (int, float)), f"Component '{field}' must be numeric"
            assert 0.0 <= value <= 1.0, f"Component '{field}' value {value} not in range [0, 1]"