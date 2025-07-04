# Kor.ai – Surveillance Platform Core

Kor.ai is an AI-powered surveillance platform built to detect market abuse risks such as insider dealing and spoofing, with a focus on commodities and energy trading. This repository contains the core logic, Bayesian inference engine, data mapping, and service orchestration for alert generation.

---

## 🚀 Features

- **Bayesian Risk Scoring**: Probabilistic models using pgmpy for insider dealing and spoofing detection
- **Evidence Sufficiency Index (ESI)**: Measure how well-supported risk scores are based on input diversity, quality, and distribution
- **Real-time Analysis**: REST API for analyzing trading data and generating risk scores
- **Alert Generation**: Automated alert system with configurable thresholds and severity levels
- **Scenario Simulation**: Built-in simulation capabilities for testing and validation
- **Modular Architecture**: Clean separation of data processing, risk calculation, and alert generation
- **Comprehensive Logging**: Structured logging with multiple levels and file rotation
- **Cloud-Ready**: Designed for deployment in microservice or serverless environments

---

## 📁 Project Structure

```
kor-ai-core/
├── src/
│   ├── app.py                 # Main Flask application
│   │   ├── core/
│   │   │   ├── bayesian_engine.py # Bayesian inference engine
│   │   │   ├── data_processor.py  # Data processing pipeline
│   │   │   ├── alert_generator.py # Alert generation system
│   │   │   └── risk_calculator.py # Risk calculation engine
│   │   └── utils/
│   │       ├── config.py          # Configuration management
│   │       └── logger.py          # Logging setup
│   ├── tests/
│   │   └── test_sample_data.py    # Sample test data and scenarios
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example              # Environment configuration template
│   ├── run_server.py             # Server runner script
│   └── sample_request.py         # API testing script
```

---

## 🧪 Quick Start

### 1. Installation

```bash
git clone https://github.com/your-org/kor-ai-core.git
cd kor-ai-core

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration as needed
nano .env
```

### 3. Run the Server

```bash
# Using the runner script
python run_server.py

# Or directly
python src/app.py
```

The server will start on `http://localhost:5000`

### 4. Test the API

```bash
# Run sample API tests
python sample_request.py

# Or test individual components
python tests/test_sample_data.py
```

---

## 📖 API Endpoints

### Health Check
```http
GET /health
```

### Analyze Trading Data
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "trades": [...],
  "orders": [...],
  "trader_info": {...},
  "material_events": [...],
  "market_data": {...}
}
```

### Simulate Scenarios
```http
POST /api/v1/simulate
Content-Type: application/json

{
  "scenario_type": "insider_dealing",
  "parameters": {
    "num_trades": 50,
    "seed": 42
  }
}
```

### Get Model Information
```http
GET /api/v1/models/info
```

### Get Alert History
```http
GET /api/v1/alerts/history?limit=100&type=INSIDER_DEALING
```

---

## 🔬 Example Usage

### Analyzing Insider Dealing

```python
import requests

data = {
    "trades": [
        {
            "id": "trade_001",
            "timestamp": "2024-01-15T10:30:00Z",
            "instrument": "ENERGY_CORP",
            "volume": 100000,
            "price": 50.25,
            "side": "buy",
            "trader_id": "exec_trader_001"
        }
    ],
    "trader_info": {
        "id": "exec_trader_001",
        "role": "executive",
        "access_level": "high"
    },
    "material_events": [
        {
            "id": "event_001",
            "timestamp": "2024-01-16T09:00:00Z",
            "type": "earnings_announcement",
            "instruments_affected": ["ENERGY_CORP"]
        }
    ]
}

response = requests.post(
    "http://localhost:5000/api/v1/analyze",
    json=data
)

result = response.json()
print(f"Risk Score: {result['risk_scores']['insider_dealing']['overall_score']}")
print(f"Alerts: {len(result['alerts'])}")
```

---

## ⚙️ Configuration Options

Key environment variables in `.env`:

- `ENVIRONMENT`: development/production
- `DEBUG`: Enable debug mode
- `PORT`: Server port (default: 5000)
- `INSIDER_HIGH_THRESHOLD`: High risk threshold for insider dealing
- `SPOOFING_HIGH_THRESHOLD`: High risk threshold for spoofing
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

---

## 🧠 Bayesian Models

### Insider Dealing Model
- **Nodes**: MaterialInfo, TradingActivity, Timing, PriceImpact, Risk
- **Features**: Access to material information, unusual trading patterns, suspicious timing
- **Inference**: Variable elimination using pgmpy

### Spoofing Model  
- **Nodes**: OrderPattern, CancellationRate, PriceMovement, VolumeRatio, Risk
- **Features**: Layered orders, high cancellation rates, volume imbalances
- **Inference**: Probabilistic assessment of market manipulation

---

## 📊 Evidence Sufficiency Index (ESI)

The Evidence Sufficiency Index (ESI) is a key feature that complements Bayesian risk scores by measuring how well-supported those scores are based on:

- **Node Activation Ratio**: Proportion of active (populated) nodes in the Bayesian network
- **Mean Confidence Score**: Average confidence level of inputs
- **Fallback Ratio**: Proportion of nodes relying on priors or latent defaults
- **Contribution Entropy**: Entropy of node contributions - measures distribution evenness
- **Cross-Cluster Diversity**: Evidence spread across distinct node groups (trade, comms, PnL, etc.)

### ESI Benefits

- **Trust Calibration**: Helps analysts understand how well-supported risk scores are
- **Filtering & Triage**: Filter alerts by ESI score to prioritize well-evidenced cases
- **Enhanced Explainability**: Explain not just why an alert was scored as risky, but how trustworthy the evidence is
- **Risk Score Adjustment**: Use ESI as multiplier: `Adjusted Risk = Risk Score × ESI`

### Example ESI Output

```json
{
  "evidence_sufficiency_index": 0.84,
  "esi_badge": "Strong",
  "node_count": 6,
  "mean_confidence": "High",
  "fallback_ratio": 0.0,
  "contribution_spread": "Balanced",
  "clusters": ["PnL", "MNPI", "TradePattern"],
  "components": {
    "node_activation_ratio": 0.83,
    "mean_confidence_score": 0.85,
    "fallback_ratio": 0.0,
    "contribution_entropy": 0.92,
    "cross_cluster_diversity": 0.71
  }
}
```

### UI Integration

ESI is integrated into alerts and can be used for:
- **Badges**: `ESI: Strong Evidence` on alert cards
- **Filtering**: Show only alerts with `ESI > 0.7`
- **Sorting**: Sort by ESI descending to prioritize well-evidenced alerts
- **Explainability**: Detailed breakdown of evidence quality in tooltips

---

## 🔍 Risk Assessment

The platform calculates risk scores across multiple dimensions:

1. **Base Risk Scores** (0.0 - 1.0)
   - Insider Dealing Risk
   - Spoofing Risk

2. **Contextual Multipliers**
   - Trader role and access level
   - Trading volume patterns
   - Market conditions
   - Behavioral indicators

3. **Overall Risk Score**
   - Weighted combination of base scores
   - Applied contextual adjustments
   - Final score capped at 1.0

---

## 🧠 Bayesian Risk Engine Pipeline Modules

### Evidence Mapping
Maps raw input data/events to Bayesian Network node states for risk models.

**Usage:**
```python
from src.core.evidence_mapper import map_evidence
mapped = map_evidence(raw_data)
```

### Fallback Logic
Handles missing or partial evidence using node fallback priors. Ensures robust inference even with incomplete data.

**Usage:**
```python
from src.core.fallback_logic import apply_fallback_evidence
completed_evidence = apply_fallback_evidence(mapped, node_defs)
```

### Complex Risk Aggregation & Scoring
Computes overall risk scores from multiple evidence nodes using complex aggregation algorithms and configurable multi-node triggers.

**Features:**
- **Multi-source evidence**: Trades, market data, HR, sales, communications, PnL
- **Configurable node weights**: Different importance for different risk factors
- **Multi-node triggers**: Alerts when multiple nodes are in high/critical states
- **PnL loss detection**: Special handling for recent PnL spikes resulting in losses
- **Exponential penalties**: Increased risk when multiple high-risk indicators are present

**Usage:**
```python
from src.core.bayesian_engine import BayesianEngine
from src.core.risk_aggregator import ComplexRiskAggregator

engine = BayesianEngine()
risk_result = engine.calculate_insider_dealing_risk(processed_data, node_defs=node_defs)

# Access complex risk analysis
print(f"Overall Score: {risk_result['overall_score']}")
print(f"Risk Level: {risk_result['risk_level']}")
print(f"High Nodes: {risk_result['high_nodes']}")
print(f"Triggers: {risk_result['triggers']}")
print(risk_result['explanation'])

# Configure node weights
aggregator = ComplexRiskAggregator()
aggregator.update_node_config("pnl_loss_spike", weight=3.0)
```

### Testing
Unit tests for evidence mapping, fallback logic, scoring, and explainability are in `tests/test_sample_data.py`.

**Run tests:**
```bash
python tests/test_sample_data.py
```

---

## 📊 Monitoring & Logging

- **Structured Logging**: JSON format for production environments
- **Log Rotation**: Automatic file rotation and cleanup
- **Error Tracking**: Separate error logs for debugging
- **Performance Metrics**: Request timing and resource usage

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Review the documentation and examples

---

## 🔮 Roadmap

- [ ] Enhanced ML models with deep learning
- [ ] Real-time streaming data processing
- [ ] Advanced visualization dashboard  
- [ ] Integration with major trading platforms
- [ ] Regulatory reporting automation
- [ ] Multi-language support

## Hidden Causality & Latent Intent (Kor.ai Approach)

### Overview

Traditional risk models can only use observable evidence. The Kor.ai approach introduces **latent intent nodes** to model unobservable abusive intent, inferred from converging evidence paths (e.g., profit, access, order behavior, comms metadata).

- **LatentIntentNode**: Represents unobservable intent to manipulate/abuse.
- **Converging Evidence Nodes**: ProfitMotivationNode, AccessPatternNode, OrderBehaviorNode, CommsMetadataNode.
- **Hidden Causality**: The model infers intent from indirect evidence, improving detection of sophisticated abuse.

### API Usage

To use the latent intent model in risk analysis, add the `use_latent_intent` flag to your request:

```json
POST /api/v1/analyze
{
  "trades": [...],
  "orders": [...],
  ...,
  "use_latent_intent": true
}
```

- If `use_latent_intent` is `true`, the system uses the advanced model with hidden causality and latent intent.
- The response will include latent intent probabilities and enhanced risk assessment.

### Example Response

```json
{
  "risk_scores": {
    "insider_dealing": {
      "insider_dealing_probability": 0.03,
      "latent_intent_no": 0.95,
      "latent_intent_potential": 0.04,
      "latent_intent_clear": 0.01,
      "overall_score": 0.03,
      "evidence_factors": { ... },
      "model_type": "latent_intent"
    },
    ...
  },
  ...
}
```

### Model Structure

- Evidence nodes (profit, access, order behavior, comms) → **latent_intent** (hidden node) → risk_factor → outcome
- The model can be extended for other abuse types (e.g., spoofing) in the future.

### Benefits
- Detects sophisticated abuse where intent is not directly observable
- Models indirect, converging evidence
- More robust to adversarial evasion
