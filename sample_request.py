#!/usr/bin/env python3
"""
Sample API requests for testing the Kor.ai Surveillance Platform
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_analyze_insider_dealing():
    """Test insider dealing analysis"""
    print("Testing insider dealing analysis...")
    
    # Sample data for insider dealing
    data = {
        "trades": [
            {
                "id": "trade_001",
                "timestamp": (datetime.utcnow() - timedelta(days=3)).isoformat() + "Z",
                "instrument": "ENERGY_CORP",
                "volume": 100000,
                "price": 50.25,
                "side": "buy",
                "trader_id": "exec_trader_001"
            },
            {
                "id": "trade_002",
                "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
                "instrument": "ENERGY_CORP", 
                "volume": 150000,
                "price": 51.10,
                "side": "buy",
                "trader_id": "exec_trader_001"
            }
        ],
        "orders": [],
        "trader_info": {
            "id": "exec_trader_001",
            "name": "Executive Trader",
            "role": "executive",
            "access_level": "high"
        },
        "material_events": [
            {
                "id": "event_001",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "type": "merger_announcement",
                "description": "Major acquisition announced",
                "instruments_affected": ["ENERGY_CORP"],
                "materiality_score": 0.9
            }
        ],
        "market_data": {
            "volatility": 0.03,
            "liquidity": 0.7
        },
        "historical_data": {
            "avg_volume": 25000,
            "avg_frequency": 5
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Analysis ID: {result['analysis_id']}")
        print(f"Insider Dealing Risk: {result['risk_scores']['insider_dealing']['overall_score']:.3f}")
        print(f"Overall Risk: {result['risk_scores']['overall_risk']:.3f}")
        print(f"Alerts Generated: {len(result['alerts'])}")
        
        if result['alerts']:
            for alert in result['alerts']:
                print(f"  - {alert['type']}: {alert['severity']} risk")
    else:
        print(f"Error: {response.text}")
    
    print("-" * 50)

def test_analyze_spoofing():
    """Test spoofing analysis"""
    print("Testing spoofing analysis...")
    
    # Generate sample spoofing data
    base_time = datetime.utcnow() - timedelta(hours=1)
    orders = []
    
    for i in range(20):
        if i % 5 == 0:
            # Real orders
            orders.append({
                "id": f"order_{i}",
                "timestamp": (base_time + timedelta(minutes=i)).isoformat() + "Z",
                "instrument": "CRUDE_FUTURE",
                "size": 1000,
                "price": 70.0 + i*0.01,
                "side": "buy",
                "status": "filled",
                "trader_id": "spoof_trader_001"
            })
        else:
            # Spoofing orders (large, cancelled)
            orders.append({
                "id": f"order_{i}",
                "timestamp": (base_time + timedelta(minutes=i)).isoformat() + "Z",
                "instrument": "CRUDE_FUTURE", 
                "size": 20000,
                "price": 70.0 + i*0.01,
                "side": "sell",
                "status": "cancelled",
                "trader_id": "spoof_trader_001",
                "cancellation_time": (base_time + timedelta(minutes=i, seconds=30)).isoformat() + "Z"
            })
    
    data = {
        "trades": [
            {
                "id": "trade_001",
                "timestamp": base_time.isoformat() + "Z",
                "instrument": "CRUDE_FUTURE",
                "volume": 1000,
                "price": 70.0,
                "side": "buy",
                "trader_id": "spoof_trader_001"
            }
        ],
        "orders": orders,
        "trader_info": {
            "id": "spoof_trader_001",
            "name": "Spoof Trader",
            "role": "trader",
            "access_level": "standard"
        },
        "material_events": [],
        "market_data": {
            "volatility": 0.02,
            "liquidity": 0.6
        },
        "historical_data": {
            "avg_volume": 5000,
            "avg_frequency": 10
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Analysis ID: {result['analysis_id']}")
        print(f"Spoofing Risk: {result['risk_scores']['spoofing']['overall_score']:.3f}")
        print(f"Overall Risk: {result['risk_scores']['overall_risk']:.3f}")
        print(f"Alerts Generated: {len(result['alerts'])}")
        
        if result['alerts']:
            for alert in result['alerts']:
                print(f"  - {alert['type']}: {alert['severity']} risk")
    else:
        print(f"Error: {response.text}")
    
    print("-" * 50)

def test_simulation():
    """Test scenario simulation"""
    print("Testing scenario simulation...")
    
    # Test insider dealing simulation
    simulation_data = {
        "scenario_type": "insider_dealing",
        "parameters": {
            "num_trades": 10,
            "seed": 42
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/simulate",
        json=simulation_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Scenario: {result['scenario_type']}")
        print(f"Risk Score: {result['risk_score']['overall_score']:.3f}")
        print(f"Simulated Trades: {len(result['simulated_data']['trades'])}")
    else:
        print(f"Error: {response.text}")
    
    print("-" * 50)

def test_models_info():
    """Test models info endpoint"""
    print("Testing models info...")
    
    response = requests.get(f"{BASE_URL}/api/v1/models/info")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Models Loaded: {result['models_loaded']}")
        print(f"Insider Model Nodes: {result['insider_dealing_model']['nodes']}")
        print(f"Spoofing Model Nodes: {result['spoofing_model']['nodes']}")
    else:
        print(f"Error: {response.text}")
    
    print("-" * 50)

def main():
    """Run all test requests"""
    print("Kor.ai Surveillance Platform - API Testing")
    print("=" * 60)
    
    try:
        test_health_check()
        test_models_info()
        test_analyze_insider_dealing()
        test_analyze_spoofing()
        test_simulation()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()