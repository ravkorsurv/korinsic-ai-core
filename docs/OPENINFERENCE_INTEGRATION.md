# OpenInference Integration for Korinsic AI Platform

This document describes the OpenInference integration for the Korinsic AI surveillance platform, providing comprehensive observability for Bayesian inference models and risk analysis workflows.

## Overview

OpenInference is an open standard for capturing and storing AI model inferences. Our integration provides:

- **AI-specific tracing** for Bayesian inference operations
- **Evidence mapping visibility** with completeness tracking
- **Model performance metrics** including latency and confidence
- **Fallback logic monitoring** for robust inference
- **End-to-end request tracing** for complete workflow visibility

## Architecture

```
┌─────────────────────────────────────────┐
│ Korinsic AI Platform                    │
├─────────────────────────────────────────┤
│ Flask API (/api/v1/analyze)            │
│ ├── Data Processing (traced)           │
│ ├── Bayesian Engine (traced)           │
│ │   ├── Evidence Mapping               │
│ │   ├── Insider Dealing Model          │
│ │   ├── Spoofing Model                 │
│ │   └── Fallback Logic                 │
│ ├── Risk Aggregation (traced)          │
│ └── Alert Generation (traced)          │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│ OpenInference Instrumentation          │
├─────────────────────────────────────────┤
│ • AI-specific semantic conventions     │
│ • Model inference tracing              │
│ • Evidence and result tracking         │
│ • Performance metrics                  │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│ OpenTelemetry Collector                │
├─────────────────────────────────────────┤
│ • OTLP ingestion                       │
│ • Data processing                      │
│ • Export to observability backends     │
└─────────────────────────────────────────┘
```

## Key Features

### 1. Bayesian Model Tracing

Every Bayesian inference operation is traced with:

```python
with ai_observability.trace_bayesian_inference("insider_dealing", "market_abuse_detection") as tracer:
    # Evidence mapping
    tracer.set_evidence(evidence_dict)
    
    # Inference execution  
    risk_score = model.infer(evidence)
    
    # Results tracking
    tracer.set_result(risk_score, confidence_level)
```

**Captured Attributes:**
- `ai.model.name`: Model identifier (e.g., "insider_dealing")
- `ai.model.type`: "bayesian_network"
- `ai.evidence.count`: Number of evidence nodes
- `ai.evidence.keys`: Evidence node names
- `ai.risk.score`: Final risk probability
- `ai.confidence`: High/Medium/Low confidence
- `ai.inference.latency_ms`: Inference time
- `ai.fallback.used`: Whether fallback logic was applied
- `ai.esi.score`: Evidence Sufficiency Index

### 2. Evidence Quality Monitoring

Track data completeness and quality:

```python
# Evidence completeness tracking
completeness_score = calculate_completeness(evidence)
tracer.span.set_attribute("ai.data.completeness_score", completeness_score)
tracer.span.set_attribute("ai.data.missing_sources", missing_sources)

# Fallback usage monitoring
if fallback_nodes:
    tracer.span.set_attribute("ai.fallback.nodes", fallback_nodes)
    tracer.span.set_attribute("ai.fallback.count", len(fallback_nodes))
```

### 3. End-to-End Request Tracing

Complete workflow visibility:

```
Request: /api/v1/analyze [trace_id: abc123...]
├── data_processing [15ms]
│   └── ai.data.processed_fields: 5
├── risk_analysis [120ms]
│   ├── bayesian_inference.insider_dealing [45ms]
│   │   ├── ai.risk.score: 0.73
│   │   ├── ai.evidence.count: 5
│   │   └── ai.fallback.used: true
│   └── bayesian_inference.spoofing [38ms]
├── risk_aggregation [12ms]
└── alert_generation [8ms]
    └── ai.alerts.count: 2
```

## Installation

### Quick Setup

```bash
# Run the automated setup script
./setup_openinference.sh
```

### Manual Installation

1. **Install Dependencies:**
```bash
pip install openinference-instrumentation==0.1.12
pip install openinference-semantic-conventions==0.1.9
```

2. **Optional - Install Arize Phoenix:**
```bash
pip install arize-phoenix==4.0.0
```

3. **Set Environment Variables:**
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_SERVICE_NAME=korinsic-ai-surveillance
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | `http://localhost:4317` |
| `OTEL_SERVICE_NAME` | Service name for traces | `korinsic-ai-surveillance` |
| `OTEL_SERVICE_VERSION` | Service version | `1.0.0` |
| `KORINSIC_AI_OBSERVABILITY_ENABLED` | Enable AI observability | `true` |

### Programmatic Configuration

```python
from src.utils.ai_observability import initialize_ai_observability

# Initialize with custom settings
ai_obs = initialize_ai_observability(
    service_name="korinsic-ai-prod",
    service_version="2.0.0",
    otlp_endpoint="https://your-collector:4317"
)
```

## Usage Examples

### Testing the Integration

```bash
# Run the test script
python test_ai_observability.py
```

### Making Traced API Calls

```bash
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "trader_info": {
      "trader_id": "TRADER_001",
      "access_level": "high"
    },
    "market_data": {
      "volatility": 0.25,
      "price_movement": 0.12
    },
    "pnl_data": {
      "daily_loss": -150000
    }
  }'
```

The response will include a `trace_id` for correlation:

```json
{
  "analysis_id": "analysis_20241201_143022_TRADER_001",
  "trace_id": "abc123def456...",
  "risk_scores": {
    "insider_dealing": {
      "risk_score": 0.73,
      "confidence": "high"
    }
  }
}
```

## Observability Dashboard

### Key Metrics to Monitor

1. **Model Performance:**
   - Average inference latency by model
   - P95/P99 latency distributions
   - Error rates and exceptions

2. **Evidence Quality:**
   - Data completeness scores
   - Fallback usage frequency
   - Missing evidence patterns

3. **Risk Assessment:**
   - Risk score distributions
   - Alert generation rates
   - High-risk scenario frequency

4. **System Health:**
   - Request throughput
   - Model availability
   - Resource utilization

### Sample Queries

**Average Inference Latency by Model:**
```sql
SELECT 
  ai.model.name,
  AVG(ai.inference.latency_ms) as avg_latency
FROM traces 
WHERE span.name LIKE 'bayesian_inference.%'
GROUP BY ai.model.name
```

**Fallback Usage Frequency:**
```sql
SELECT 
  COUNT(*) as total_inferences,
  SUM(CASE WHEN ai.fallback.used = true THEN 1 ELSE 0 END) as fallback_used,
  AVG(ai.fallback.count) as avg_fallback_nodes
FROM traces
WHERE span.name LIKE 'bayesian_inference.%'
```

## Troubleshooting

### Common Issues

1. **No traces appearing:**
   - Check OTLP endpoint configuration
   - Verify collector is running
   - Check firewall/network connectivity

2. **Missing AI attributes:**
   - Ensure OpenInference dependencies are installed
   - Check import statements in instrumented code
   - Verify semantic conventions version compatibility

3. **High latency:**
   - Review batch processing settings
   - Check network latency to collector
   - Consider sampling for high-volume scenarios

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger("opentelemetry").setLevel(logging.DEBUG)
```

### Validation

Run the validation script:

```bash
python test_ai_observability.py
```

Expected output:
```
✅ AI observability initialized
✅ Bayesian engine loaded successfully  
✅ Analysis completed in 45.23ms
🎯 Risk Score: 0.730
📊 ESI Score: 0.850
```

## Security Considerations

### Data Privacy

- **Evidence Sanitization:** Sensitive evidence is hashed before tracing
- **PII Filtering:** Personal identifiers are excluded from traces
- **Access Control:** Trace data inherits platform security controls

### Compliance

- **Audit Trails:** Complete inference decision paths for regulatory review
- **Data Retention:** Configurable trace retention policies
- **Encryption:** TLS encryption for trace data transmission

## Performance Impact

### Overhead Analysis

- **Latency Impact:** < 5ms additional latency per request
- **Memory Usage:** ~10MB additional memory for trace buffers
- **CPU Overhead:** < 2% additional CPU utilization
- **Network:** Minimal bandwidth for trace export

### Optimization

- **Sampling:** Configure sampling rates for high-volume scenarios
- **Batching:** Optimize batch sizes for export efficiency
- **Filtering:** Filter low-value traces to reduce volume

## Future Enhancements

### Planned Features

1. **Advanced Metrics:**
   - Model drift detection
   - Evidence pattern analysis
   - Confidence calibration tracking

2. **Enhanced Tracing:**
   - Cross-model correlation analysis
   - Regulatory compliance reporting
   - Performance optimization suggestions

3. **Integration Expansion:**
   - Additional model types (wash trading, market manipulation)
   - Real-time alerting integration
   - Advanced visualization dashboards

### Roadmap

- **Q1 2024:** Model drift detection
- **Q2 2024:** Advanced evidence analytics  
- **Q3 2024:** Regulatory reporting integration
- **Q4 2024:** Real-time model optimization

## Support

For questions and support:

- **Technical Issues:** Create GitHub issue with `observability` label
- **Integration Help:** Check troubleshooting section above
- **Feature Requests:** Submit enhancement proposals via GitHub

---

*This documentation is maintained alongside the OpenInference integration. For the latest updates, see the repository.*
