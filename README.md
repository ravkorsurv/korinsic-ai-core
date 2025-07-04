# Kor.ai – Surveillance Platform Core

Kor.ai is an AI-powered surveillance platform built to detect market abuse risks such as insider dealing and spoofing, with a focus on commodities and energy trading. This repository contains the core logic, Bayesian inference engine, data mapping, and service orchestration for alert generation.

---

## 🚀 Features

- **Bayesian Risk Scoring**: Probabilistic models using pgmpy for insider dealing and spoofing detection
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

## � Alert System

### Alert Types
- `INSIDER_DEALING`: Potential insider trading detected
- `SPOOFING`: Market manipulation patterns identified
- `OVERALL_RISK`: Combined risk exceeds thresholds

### Severity Levels
- `CRITICAL`: Immediate investigation required (≥0.8)
- `HIGH`: Urgent review needed (≥0.6)
- `MEDIUM`: Enhanced monitoring (≥0.4)

### Alert Actions
Each alert includes recommended actions based on severity and evidence.

---

## 🧪 Testing & Simulation

The platform includes comprehensive testing capabilities:

```bash
# Test with sample data
python tests/test_sample_data.py

# Test API endpoints
python sample_request.py
```

Built-in scenario simulation for:
- Insider dealing patterns
- Spoofing behaviors
- Mixed abuse scenarios

---

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t kor-ai-surveillance .

# Run container
docker run -p 5000:5000 -e ENVIRONMENT=production kor-ai-surveillance
```

### Production Configuration
- Set `ENVIRONMENT=production`
- Configure proper logging directory
- Set up database for alert persistence
- Enable monitoring and health checks

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
