"""
OpenInference Tracer for Korinsic AI Surveillance Platform

This module provides comprehensive AI observability and tracing capabilities
using OpenInference standards for the Bayesian inference models and ML operations.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from contextlib import contextmanager

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

logger = logging.getLogger(__name__)


class KorinsicOpenInferenceTracer:
    """
    OpenInference tracer specifically designed for Korinsic's AI surveillance operations.
    
    This tracer captures:
    - Bayesian inference operations
    - Risk calculation processes
    - Model predictions and confidence scores
    - Evidence processing and sufficiency calculations
    - API request/response flows
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OpenInference tracer.
        
        Args:
            config: Configuration dictionary with tracing settings
        """
        self.config = config or {}
        self.tracer_provider = None
        self.tracer = None
        self.enabled = OPENTELEMETRY_AVAILABLE and self.config.get('enabled', True)
        
        if self.enabled:
            self._setup_tracing()
        else:
            logger.warning("OpenTelemetry not available or tracing disabled")
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing with OpenInference semantic conventions."""
        if not OPENTELEMETRY_AVAILABLE:
            return
            
        try:
            # Initialize tracer provider
            self.tracer_provider = TracerProvider()
            trace.set_tracer_provider(self.tracer_provider)
            
            # Setup exporters based on configuration
            self._setup_exporters()
            
            # Get tracer instance
            self.tracer = trace.get_tracer(
                "korinsic.surveillance.platform",
                version="1.0.0"
            )
            
            # Auto-instrument Flask, requests, and logging
            self._setup_auto_instrumentation()
            
            logger.info("OpenInference tracing initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenInference tracing: {e}")
            self.enabled = False
    
    def _setup_exporters(self):
        """Setup trace exporters based on configuration."""
        if not OPENTELEMETRY_AVAILABLE:
            return
            
        exporters = []
        
        # Console exporter for development
        if self.config.get('console_exporter', os.getenv('OTEL_CONSOLE_EXPORTER', 'false').lower() == 'true'):
            exporters.append(ConsoleSpanExporter())
        
        # OTLP exporter for production observability platforms
        otlp_endpoint = self.config.get('otlp_endpoint', os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT'))
        if otlp_endpoint:
            exporters.append(OTLPSpanExporter(endpoint=otlp_endpoint))
        
        # Phoenix/Arize exporter (for AI-specific observability)
        phoenix_endpoint = self.config.get('phoenix_endpoint', os.getenv('PHOENIX_ENDPOINT'))
        if phoenix_endpoint:
            exporters.append(OTLPSpanExporter(endpoint=f"{phoenix_endpoint}/v1/traces"))
        
        # Add span processors for each exporter
        for exporter in exporters:
            span_processor = BatchSpanProcessor(exporter)
            self.tracer_provider.add_span_processor(span_processor)
    
    def _setup_auto_instrumentation(self):
        """Setup automatic instrumentation for common libraries."""
        if not OPENTELEMETRY_AVAILABLE:
            return
            
        try:
            # Instrument Flask
            FlaskInstrumentor().instrument()
            
            # Instrument requests
            RequestsInstrumentor().instrument()
            
            # Instrument logging
            LoggingInstrumentor().instrument()
            
        except Exception as e:
            logger.warning(f"Some auto-instrumentation failed: {e}")
    
    @contextmanager
    def trace_bayesian_inference(
        self, 
        model_name: str, 
        model_version: str = "1.0.0",
        input_data: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for tracing Bayesian inference operations.
        
        Args:
            model_name: Name of the Bayesian model
            model_version: Version of the model
            input_data: Input data for the inference
        """
        if not self.enabled or not self.tracer:
            yield None
            return
            
        with self.tracer.start_as_current_span(
            f"bayesian_inference.{model_name}",
            kind=trace.SpanKind.INTERNAL
        ) as span:
            try:
                # Set OpenInference semantic attributes
                span.set_attribute("openinference.span.kind", "LLM")
                span.set_attribute("model.name", model_name)
                span.set_attribute("model.version", model_version)
                span.set_attribute("model.type", "bayesian_network")
                span.set_attribute("inference.start_time", datetime.utcnow().isoformat())
                
                if input_data:
                    span.set_attribute("input.trade_count", len(input_data.get("trades", [])))
                    span.set_attribute("input.order_count", len(input_data.get("orders", [])))
                    span.set_attribute("input.has_material_events", bool(input_data.get("material_events")))
                
                yield span
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
            finally:
                span.set_attribute("inference.end_time", datetime.utcnow().isoformat())


# Global tracer instance
_tracer_instance: Optional[KorinsicOpenInferenceTracer] = None


def get_tracer(config: Optional[Dict[str, Any]] = None) -> KorinsicOpenInferenceTracer:
    """
    Get the global OpenInference tracer instance.
    
    Args:
        config: Optional configuration for the tracer
        
    Returns:
        KorinsicOpenInferenceTracer instance
    """
    global _tracer_instance
    
    if _tracer_instance is None:
        _tracer_instance = KorinsicOpenInferenceTracer(config)
    
    return _tracer_instance


def initialize_tracing(config: Optional[Dict[str, Any]] = None):
    """
    Initialize OpenInference tracing for the Korinsic platform.
    
    Args:
        config: Optional configuration for tracing
    """
    try:
        get_tracer(config)
        logger.info("OpenInference tracing initialized for Korinsic platform")
    except Exception as e:
        logger.error(f"Failed to initialize OpenInference tracing: {e}")
        raise
