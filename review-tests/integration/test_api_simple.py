#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple API test for regulatory explainability feature
"""

import requests
import json
from datetime import datetime

def test_api():
    """Test the API with regulatory explainability"""
    
    # Test data with higher risk factors
    test_data = {
        "trades": [
            {
                "id": "test_001",
                "timestamp": "2024-01-01T10:00:00Z",
                "instrument": "AAPL",
                "volume": 50000,  # High volume
                "price": 150.0,
                "side": "buy",
                "trader_id": "trader_001"
            }
        ],
        "orders": [
            {
                "id": "order_001",
                "timestamp": "2024-01-01T09:30:00Z",
                "instrument": "AAPL",
                "volume": 100000,
                "price": 148.0,
                "side": "buy",
                "status": "cancelled",  # High cancellation rate
                "trader_id": "trader_001"
            }
        ],
        "trader_info": {
            "id": "trader_001",
            "name": "Test Trader",
            "role": "executive",  # High access level
            "access_level": "high"
        },
        "material_events": [
            {
                "timestamp": "2024-01-01T11:00:00Z",
                "type": "earnings",
                "description": "Strong quarterly earnings announcement",
                "expected_impact": 0.15,
                "materiality_score": 0.9
            }
        ],
        "market_data": {
            "volatility": 0.05,
            "liquidity": 0.6,
            "price_change": 0.12
        },
        "metrics": {
            "volume_ratio": 3.5,  # High volume ratio
            "pre_event_trading": 1,  # Trading before event
            "timing_concentration": 8,  # High timing concentration
            "price_impact": 0.08,  # High price impact
            "cancellation_ratio": 0.8,  # High cancellation rate
            "order_frequency": 25  # High order frequency
        },
        "timeframe": "intraday",
        "instruments": ["AAPL"],
        "include_regulatory_rationale": True
    }
    
    try:
        print("Testing API with regulatory explainability...")
        
        # Make API call
        response = requests.post(
            "http://localhost:5000/api/v1/analyze",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("API call successful!")
            print(f"Alerts generated: {len(result.get('alerts', []))}")
            
            # Print alert details
            for i, alert in enumerate(result.get('alerts', [])):
                print(f"\nAlert {i+1}:")
                print(f"  - Type: {alert.get('type')}")
                print(f"  - Severity: {alert.get('severity')}")
                print(f"  - Risk Score: {alert.get('risk_score', 0):.3f}")
                print(f"  - Description: {alert.get('description', 'N/A')}")
            
            # Check for regulatory rationales (plural)
            rationales = result.get('regulatory_rationales', [])
            if rationales:
                print(f"\n✓ {len(rationales)} regulatory rationale(s) included in response")
                for idx, rationale in enumerate(rationales, 1):
                    print(f"\nRegulatory Rationale {idx} for Alert ID: {rationale.get('alert_id')}")
                    print(f"  - Deterministic Narrative:\n{rationale.get('deterministic_narrative', 'N/A')}")
                    print(f"  - Inference Paths: {len(rationale.get('inference_paths', []))}")
                    print(f"  - VOI Analysis: {json.dumps(rationale.get('voi_analysis', {}), indent=2)}")
                    print(f"  - Sensitivity Report: {json.dumps(rationale.get('sensitivity_report', {}), indent=2)}")
            else:
                print("\n✗ No regulatory rationales in response")
            
            return True
        else:
            print(f"API call failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure the server is running on localhost:5000")
        return False
    except Exception as e:
        print(f"✗ Error testing API: {str(e)}")
        return False

if __name__ == "__main__":
    test_api() 