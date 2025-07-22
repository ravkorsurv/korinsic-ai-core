"""
AI Observability Module for Korinsic Platform

This module provides OpenInference instrumentation for AI/ML model observability,
specifically designed for Bayesian inference engines and risk analysis models.
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource

try:
    from openinference.semconv.trace import SpanAttributes
except ImportError:
    # Fallback if OpenInference not available
    class SpanAttributes:
        LLM_MODEL_NAME = "llm.model_name"
        LLM_INPUT_MESSAGES = "llm.input_messages"
        LLM_OUTPUT_MESSAGES = "llm.output_messages"

logger = logging.getLogger(__name__)

class KorinsicAIObservability:
    """OpenInference observability setup for Korinsic AI platform"""
    
    def __init__(self, 
                 service_name: str = "korinsic-ai-surveillance",
                 service_version: str = "1.0.0",
                 otlp_endpoint: Optional[str] = None):
        """Initialize AI observability for Korinsic"""
        self.service_name = service_name
        self.service_version = service_version
        self.otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        
        self._setup_tracing()
        self.tracer = trace.get_tracer(__name__)
        
        logger.info(f"Korinsic AI observability initialized - service: {service_name}")
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing with OpenInference conventions"""
        resource = Resource(attributes={
            SERVICE_NAME: self.service_name,
            SERVICE_VERSION: self.service_version,
            "ai.system.type": "bayesian_inference",
            "ai.domain": "financial_surveillance"
        })
        
        tracer_provider = TracerProvider(resource=resource)
        
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.otlp_endpoint,
            insecure=True
        )
        
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)
    
    def trace_bayesian_inference(self, model_name: str, analysis_type: str = "risk_assessment"):
        """Context manager for tracing Bayesian inference operations"""
        return BayesianInferenceTracer(self.tracer, model_name, analysis_type)

class BayesianInferenceTracer:
    """Context manager for tracing Bayesian inference operations"""
    
    def __init__(self, tracer, model_name: str, analysis_type: str):
        self.tracer = tracer
        self.model_name = model_name
        self.analysis_type = analysis_type
        self.span = None
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.span = self.tracer.start_span(f"bayesian_inference.{self.model_name}")
        
        # Set OpenInference attributes
        self.span.set_attribute(SpanAttributes.LLM_MODEL_NAME, self.model_name)
        self.span.set_attribute("ai.model.type", "bayesian_network")
        self.span.set_attribute("ai.analysis.type", self.analysis_type)
        self.span.set_attribute("ai.system", "korinsic_surveillance")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            inference_time = (time.time() - self.start_time) * 1000
            self.span.set_attribute("ai.inference.latency_ms", inference_time)
            
            if exc_type:
                self.span.record_exception(exc_val)
                self.span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc_val)))
            else:
                self.span.set_status(trace.Status(trace.StatusCode.OK))
            
            self.span.end()
    
    def set_evidence(self, evidence: Dict[str, Any]):
        """Set evidence data in the trace"""
        if self.span:
            self.span.set_attribute("ai.evidence.keys", list(evidence.keys()))
            self.span.set_attribute("ai.evidence.count", len(evidence))
            self.span.set_attribute(SpanAttributes.LLM_INPUT_MESSAGES, str(evidence))
    
    def set_result(self, risk_score: float, confidence: str):
        """Set inference results in the trace"""
        if self.span:
            self.span.set_attribute("ai.risk.score", risk_score)
            self.span.set_attribute("ai.confidence", confidence)
            self.span.set_attribute(SpanAttributes.LLM_OUTPUT_MESSAGES, f"Risk Score: {risk_score}, Confidence: {confidence}")

# Global instance
_ai_observability: Optional[KorinsicAIObservability] = None

def get_ai_observability() -> KorinsicAIObservability:
    """Get the global AI observability instance"""
    global _ai_observability
    if _ai_observability is None:
        _ai_observability = KorinsicAIObservability()
    return _ai_observability
