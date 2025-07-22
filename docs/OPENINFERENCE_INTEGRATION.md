# OpenInference Integration for Korinsic AI Surveillance Platform

This document provides comprehensive guidance on the OpenInference observability integration for the Korinsic surveillance platform.

## Overview

OpenInference provides AI-specific observability and tracing capabilities that are crucial for monitoring and debugging complex Bayesian inference models used in market abuse detection. This integration enables:

- **Comprehensive AI Model Tracing**: Track every Bayesian inference operation
- **Performance Monitoring**: Monitor model execution times and resource usage
- **Evidence Sufficiency Tracking**: Trace how evidence impacts risk calculations
- **Regulatory Compliance**: Maintain audit trails for financial surveillance
- **Production Debugging**: Identify and resolve AI model issues in real-time

## Architecture

### Components

1. **KorinsicOpenInferenceTracer**: Core tracing utility
2. **EnhancedBayesianEngine**: Bayesian models with integrated tracing
3. **Enhanced API Routes**: API endpoints with comprehensive observability
4. **Integration Tests**: Validation of tracing functionality

### Tracing Hierarchy

```
surveillance_analysis (ROOT SPAN)
├── data_processing
├── bayesian_inference.insider_dealing
│   ├── evidence_analysis
│   └── risk_calculation
├── bayesian_inference.spoofing
│   ├── evidence_analysis
│   └── risk_calculation
├── risk_aggregation
├── alert_generation
└── regulatory_rationale
```

## Configuration

### Environment Variables

```bash
# Enable/disable tracing
OTEL_TRACING_ENABLED=true

# Console exporter for development
OTEL_CONSOLE_EXPORTER=true

# OTLP endpoint for production
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4318

# Phoenix/Arize endpoint for AI observability
PHOENIX_ENDPOINT=http://phoenix:6006

# Jaeger endpoint
JAEGER_ENDPOINT=jaeger:6831

# Sampling rate (0.0 to 1.0)
OTEL_SAMPLING_RATE=1.0
```

### Configuration File

See `config/openinference_config.json` for detailed configuration options.

## Usage

### Basic Initialization

```python
from src.utils.openinference_tracer import initialize_tracing

# Initialize tracing with default configuration
initialize_tracing()

# Or with custom configuration
config = {
    'enabled': True,
    'console_exporter': True,
    'otlp_endpoint': 'http://collector:4318'
}
initialize_tracing(config)
```

### Enhanced Bayesian Engine

```python
from src.core.engines.enhanced_bayesian_engine import EnhancedBayesianEngine

# Initialize with tracing
engine = EnhancedBayesianEngine()

# Perform risk analysis with automatic tracing
processed_data = {...}
insider_result = engine.calculate_insider_dealing_risk(processed_data)

# Result includes tracing metadata
print(insider_result['tracing_metadata'])
```

### API Endpoints with Tracing

```python
# Use enhanced analysis endpoints
POST /api/v1/analyze/enhanced
POST /api/v1/analyze/batch/enhanced

# Response includes tracing metadata
{
  "status": "success",
  "data": {
    "analysis_id": "uuid",
    "risk_scores": {...},
    "tracing_metadata": {
      "session_id": "uuid",
      "trace_id": "hex_string",
      "span_id": "hex_string",
      "openinference_enabled": true
    }
  }
}
```

### Custom Tracing

```python
from src.utils.openinference_tracer import get_tracer

tracer = get_tracer()

# Trace custom operations
with tracer.trace_bayesian_inference("custom_model", "1.0.0", input_data) as span:
    # Your model inference code here
    result = perform_inference(input_data)
    
    # Add custom attributes
    if span:
        span.set_attribute("custom.attribute", "value")
```

## Observability Platforms

### Arize Phoenix

Arize Phoenix is specifically designed for AI observability and provides:

- AI model performance monitoring
- Drift detection
- Model comparison and analysis
- Real-time inference monitoring

**Setup:**
```bash
# Install Phoenix
pip install arize-phoenix

# Set endpoint
export PHOENIX_ENDPOINT=http://phoenix:6006

# Phoenix will automatically receive traces via OTLP
```

### Jaeger

For distributed tracing and request flow analysis:

```bash
# Set Jaeger endpoint
export JAEGER_ENDPOINT=jaeger:6831

# View traces at http://jaeger:16686
```

### Custom OTLP Collectors

For integration with other observability platforms:

```bash
# Set OTLP endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318

# Supports: DataDog, New Relic, Honeycomb, etc.
```

## Trace Attributes

### Standard Attributes

- `model.name`: Name of the Bayesian model
- `model.version`: Version of the model
- `model.type`: Type of model (e.g., "bayesian_network")
- `inference.start_time`: Start time of inference
- `inference.end_time`: End time of inference

### Input Attributes

- `input.trade_count`: Number of trades in input
- `input.order_count`: Number of orders in input
- `input.has_material_events`: Whether material events are present
- `input.total_volume`: Total trading volume
- `input.total_value`: Total trading value

### Prediction Attributes

- `prediction.risk_score`: Calculated risk score
- `prediction.risk_level`: Risk level (HIGH/MEDIUM/LOW)
- `prediction.confidence`: Model confidence
- `prediction.evidence_sufficiency`: Evidence sufficiency index
- `prediction.alert_count`: Number of alerts generated

### Performance Attributes

- `performance.processing_time_seconds`: Processing time in seconds
- `performance.processing_time_ms`: Processing time in milliseconds

## Regulatory Compliance

### Audit Trail

The OpenInference integration provides comprehensive audit trails for regulatory compliance:

1. **Complete Request Tracking**: Every analysis request is fully traced
2. **Model Decision Tracking**: All Bayesian inference decisions are recorded
3. **Evidence Tracking**: How evidence influences risk calculations
4. **Performance Monitoring**: System performance and reliability metrics
5. **Error Tracking**: Complete error context and stack traces

### Data Retention

Configure trace retention based on regulatory requirements:

```json
{
  "retention": {
    "traces": "7_years",
    "metrics": "5_years",
    "logs": "10_years"
  }
}
```

## Performance Considerations

### Sampling

In production, use sampling to reduce overhead:

```bash
# Sample 10% of requests
export OTEL_SAMPLING_RATE=0.1
```

### Batch Export

Configure batch export for better performance:

```python
{
  "batch_export": {
    "max_export_batch_size": 512,
    "export_timeout_millis": 30000,
    "max_queue_size": 2048
  }
}
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Model Performance**
   - Inference latency
   - Throughput (requests/second)
   - Error rate

2. **Risk Detection**
   - Risk score distribution
   - Alert generation rate
   - False positive rate

3. **Evidence Quality**
   - Evidence sufficiency scores
   - Missing evidence patterns
   - Data quality issues

### Alert Configuration

```yaml
alerts:
  - name: "High Inference Latency"
    condition: "p95_latency > 5s"
    severity: "warning"
  
  - name: "Model Error Rate"
    condition: "error_rate > 1%"
    severity: "critical"
  
  - name: "Low Evidence Sufficiency"
    condition: "avg_evidence_sufficiency < 0.5"
    severity: "warning"
```

## Troubleshooting

### Common Issues

1. **Tracing Not Working**
   - Check `OTEL_TRACING_ENABLED=true`
   - Verify OpenTelemetry dependencies are installed
   - Check exporter endpoints are accessible

2. **High Overhead**
   - Reduce sampling rate
   - Increase batch export size
   - Disable console exporter in production

3. **Missing Traces**
   - Check span processor configuration
   - Verify exporter connectivity
   - Review sampling configuration

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.getLogger("opentelemetry").setLevel(logging.DEBUG)
```

## Best Practices

1. **Use Appropriate Sampling**: Don't trace 100% in production
2. **Add Context**: Include relevant business context in spans
3. **Monitor Performance**: Track the overhead of tracing
4. **Secure Traces**: Ensure sensitive data is not logged
5. **Regular Review**: Periodically review trace data for insights

## Integration with Existing Logging

The OpenInference integration works alongside existing logging:

```python
import logging
from src.utils.openinference_tracer import get_tracer

logger = logging.getLogger(__name__)
tracer = get_tracer()

def analyze_risk(data):
    with tracer.trace_bayesian_inference("model", "1.0", data) as span:
        logger.info("Starting risk analysis")
        
        # Analysis code here
        result = perform_analysis(data)
        
        logger.info(f"Risk analysis completed: {result['risk_score']}")
        return result
```

## Future Enhancements

1. **Custom Metrics**: Add business-specific metrics
2. **Anomaly Detection**: Detect unusual patterns in traces
3. **Model Comparison**: Compare different model versions
4. **Real-time Dashboards**: Create real-time monitoring dashboards
5. **Automated Alerts**: Set up intelligent alerting based on trace patterns

## Support

For questions about OpenInference integration:

1. Check the troubleshooting section
2. Review OpenTelemetry documentation
3. Consult Arize Phoenix documentation for AI-specific features
4. Create an issue in the project repository
