import requests
import json

API_URL = "http://127.0.0.1:5000/api/v1/analyze"

payload = {
    "trades": [{"volume": 1000, "price": 50.0}],
    "orders": [{"size": 1000, "status": "filled"}],
    "trader_info": {"role": "trader"},
    "historical_data": {"avg_volume": 500},
    "pnl_metrics": {"drift_score": 0.05, "profit_ratio": 0.1},
    "access_logs": [],
    "comms_data": {"unusual_patterns": 0},
    "comms_indicators": [],
    "use_latent_intent": True
}

print(f"POST {API_URL}\nPayload:")
print(json.dumps(payload, indent=2))

try:
    response = requests.post(API_URL, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    data = response.json()
    print("\nFull Response:")
    print(json.dumps(data, indent=2))
    
    # Highlight latent intent results
    insider = data.get("risk_scores", {}).get("insider_dealing", {})
    if insider.get("model_type") == "latent_intent":
        print("\nLatent Intent Results:")
        print(f"  Probability (insider_dealing): {insider.get('insider_dealing_probability')}")
        print(f"  Latent Intent (no): {insider.get('latent_intent_no')}")
        print(f"  Latent Intent (potential): {insider.get('latent_intent_potential')}")
        print(f"  Latent Intent (clear): {insider.get('latent_intent_clear')}")
    else:
        print("\nLatent intent model was not used in the response.")
except Exception as e:
    print(f"Error during API test: {e}") 