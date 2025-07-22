"""
Test helper utilities for common test operations.
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


def create_test_scenario(scenario_type: str, **kwargs) -> Dict[str, Any]:
    """
    Create standardized test scenarios for different types of market abuse.
    
    Args:
        scenario_type: Type of scenario ('insider_dealing', 'spoofing', 'normal')
        **kwargs: Additional parameters to customize the scenario
        
    Returns:
        Complete test scenario data
    """
    base_time = datetime.now()
    
    if scenario_type == 'insider_dealing':
        return {
            "trades": [
                {
                    "id": "insider_trade_001",
                    "timestamp": base_time.isoformat() + "Z",
                    "instrument": kwargs.get("instrument", "ACME_CORP"),
                    "volume": kwargs.get("volume", 500000),
                    "price": kwargs.get("price", 45.50),
                    "side": "buy",
                    "trader_id": kwargs.get("trader_id", "exec_001"),
                    "execution_venue": "NYSE",
                    "order_type": "market"
                }
            ],
            "trader_info": {
                "id": kwargs.get("trader_id", "exec_001"),
                "role": "executive",
                "access_level": "high",
                "department": "management"
            },
            "material_events": [
                {
                    "id": "material_event_001",
                    "timestamp": (base_time + timedelta(minutes=15)).isoformat() + "Z",
                    "type": "earnings_announcement",
                    "description": "Unexpected earnings beat",
                    "instruments_affected": [kwargs.get("instrument", "ACME_CORP")],
                    "expected_impact": kwargs.get("impact", 0.15),
                    "materiality_score": 0.95
                }
            ],
            "market_data": {
                "volatility": 0.08,
                "price_movement": kwargs.get("price_movement", 0.12),
                "volume": 2000000
            }
        }
    
    elif scenario_type == 'spoofing':
        return {
            "orders": [
                {
                    "id": "spoof_order_001",
                    "timestamp": base_time.isoformat() + "Z",
                    "instrument": kwargs.get("instrument", "COMMODITY_X"),
                    "volume": 100000,
                    "price": 50.00,
                    "side": "buy",
                    "status": "cancelled",
                    "trader_id": kwargs.get("trader_id", "trader_002"),
                    "order_type": "limit"
                },
                {
                    "id": "spoof_order_002",
                    "timestamp": (base_time + timedelta(seconds=30)).isoformat() + "Z",
                    "instrument": kwargs.get("instrument", "COMMODITY_X"),
                    "volume": 150000,
                    "price": 50.10,
                    "side": "buy",
                    "status": "cancelled",
                    "trader_id": kwargs.get("trader_id", "trader_002"),
                    "order_type": "limit"
                },
                {
                    "id": "real_trade_001",
                    "timestamp": (base_time + timedelta(minutes=1)).isoformat() + "Z",
                    "instrument": kwargs.get("instrument", "COMMODITY_X"),
                    "volume": 5000,
                    "price": 49.95,
                    "side": "sell",
                    "status": "filled",
                    "trader_id": kwargs.get("trader_id", "trader_002"),
                    "order_type": "market"
                }
            ],
            "trader_info": {
                "id": kwargs.get("trader_id", "trader_002"),
                "role": "trader",
                "access_level": "medium"
            },
            "market_data": {
                "volatility": 0.03,
                "price_movement": 0.01,
                "volume": 800000
            }
        }
    
    elif scenario_type == 'normal':
        return {
            "trades": [
                {
                    "id": "normal_trade_001",
                    "timestamp": base_time.isoformat() + "Z",
                    "instrument": kwargs.get("instrument", "NORMAL_STOCK"),
                    "volume": kwargs.get("volume", 10000),
                    "price": kwargs.get("price", 25.50),
                    "side": "buy",
                    "trader_id": kwargs.get("trader_id", "trader_003"),
                    "execution_venue": "NASDAQ",
                    "order_type": "limit"
                }
            ],
            "trader_info": {
                "id": kwargs.get("trader_id", "trader_003"),
                "role": "trader",
                "access_level": "low"
            },
            "market_data": {
                "volatility": 0.02,
                "price_movement": 0.005,
                "volume": 500000
            }
        }
    
    else:
        raise ValueError(f"Unknown scenario type: {scenario_type}")


def validate_api_response(response_data: Dict[str, Any]) -> bool:
    """
    Validate that an API response has the expected structure.
    
    Args:
        response_data: API response data to validate
        
    Returns:
        True if valid, raises AssertionError if invalid
    """
    required_fields = ['timestamp', 'analysis_id', 'risk_scores']
    
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"
    
    # Validate risk scores structure
    risk_scores = response_data['risk_scores']
    assert 'insider_dealing' in risk_scores, "Missing insider_dealing risk score"
    assert 'spoofing' in risk_scores, "Missing spoofing risk score"
    
    # Validate risk score fields
    for risk_type in ['insider_dealing', 'spoofing']:
        risk_data = risk_scores[risk_type]
        assert 'overall_score' in risk_data, f"Missing overall_score in {risk_type}"
        assert 0 <= risk_data['overall_score'] <= 1, f"Invalid score range in {risk_type}"
    
    return True


def compare_risk_scores(score1: Dict[str, Any], score2: Dict[str, Any], 
                       tolerance: float = 0.001) -> bool:
    """
    Compare two risk score dictionaries within a tolerance.
    
    Args:
        score1: First risk score dictionary
        score2: Second risk score dictionary  
        tolerance: Tolerance for floating point comparison
        
    Returns:
        True if scores are similar within tolerance
    """
    if set(score1.keys()) != set(score2.keys()):
        return False
    
    for key in score1:
        if isinstance(score1[key], (int, float)) and isinstance(score2[key], (int, float)):
            if abs(score1[key] - score2[key]) > tolerance:
                return False
        elif score1[key] != score2[key]:
            return False
    
    return True


def assert_alert_generated(alerts: List[Dict[str, Any]], 
                          alert_type: str, 
                          min_severity: str = "LOW") -> Dict[str, Any]:
    """
    Assert that an alert of a specific type was generated.
    
    Args:
        alerts: List of generated alerts
        alert_type: Expected alert type (e.g., 'INSIDER_DEALING')
        min_severity: Minimum expected severity level
        
    Returns:
        The matching alert if found
        
    Raises:
        AssertionError: If no matching alert is found
    """
    severity_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    min_level = severity_levels.get(min_severity, 1)
    
    for alert in alerts:
        if alert.get('type') == alert_type:
            alert_severity = alert.get('severity', 'LOW')
            alert_level = severity_levels.get(alert_severity, 1)
            
            if alert_level >= min_level:
                return alert
    
    raise AssertionError(
        f"No {alert_type} alert found with minimum severity {min_severity}. "
        f"Available alerts: {[a.get('type') for a in alerts]}"
    )


def wait_for_condition(condition_func, timeout: float = 5.0, 
                      interval: float = 0.1) -> bool:
    """
    Wait for a condition to become true within a timeout.
    
    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        interval: Check interval in seconds
        
    Returns:
        True if condition was met, False if timeout occurred
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    
    return False


def format_test_data_for_api(test_data: Dict[str, Any]) -> str:
    """
    Format test data as JSON string for API requests.
    
    Args:
        test_data: Test data dictionary
        
    Returns:
        JSON string formatted for API requests
    """
    return json.dumps(test_data, indent=2, default=str)


def extract_risk_factors(risk_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and normalize risk factors from a risk analysis result.
    
    Args:
        risk_result: Risk analysis result dictionary
        
    Returns:
        Normalized risk factors dictionary
    """
    return {
        'overall_score': risk_result.get('overall_score', 0.0),
        'risk_level': risk_result.get('risk_level', 'UNKNOWN'),
        'evidence_factors': risk_result.get('evidence_factors', {}),
        'model_type': risk_result.get('model_type', 'standard'),
        'high_nodes': risk_result.get('high_nodes', []),
        'critical_nodes': risk_result.get('critical_nodes', [])
    }


def create_performance_test_data(num_trades: int = 1000, 
                                num_instruments: int = 50,
                                num_traders: int = 20) -> Dict[str, Any]:
    """
    Create large dataset for performance testing.
    
    Args:
        num_trades: Number of trades to generate
        num_instruments: Number of different instruments
        num_traders: Number of different traders
        
    Returns:
        Large test dataset
    """
    base_time = datetime(2024, 1, 1, 9, 0, 0)
    
    trades = []
    for i in range(num_trades):
        trades.append({
            "id": f"perf_trade_{i:06d}",
            "timestamp": (base_time + timedelta(minutes=i)).isoformat() + "Z",
            "instrument": f"STOCK_{i % num_instruments:03d}",
            "volume": 1000 + (i % 100000),
            "price": 50.0 + (i % 100) * 0.1,
            "side": "buy" if i % 2 == 0 else "sell",
            "trader_id": f"trader_{i % num_traders:03d}",
            "execution_venue": "NYSE" if i % 2 == 0 else "NASDAQ",
            "order_type": "market" if i % 3 == 0 else "limit"
        })
    
    return {
        "trades": trades,
        "trader_info": {
            "id": "trader_000",
            "role": "trader",
            "access_level": "medium"
        },
        "market_data": {
            "volatility": 0.02,
            "volume": num_trades * 1000,
            "price_movement": 0.01
        },
        "timeframe": "daily"
    }