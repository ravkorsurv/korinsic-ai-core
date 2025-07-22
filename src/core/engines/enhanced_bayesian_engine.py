"""
Enhanced Bayesian Engine with OpenInference Tracing

This module extends the existing Bayesian engine with comprehensive
OpenInference observability and tracing capabilities.
"""

import json
import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import uuid

from .bayesian_engine import BayesianEngine
from ...utils.openinference_tracer import get_tracer

logger = logging.getLogger(__name__)


class EnhancedBayesianEngine(BayesianEngine):
    """
    Enhanced Bayesian inference engine with OpenInference tracing capabilities.
    
    This engine extends the base BayesianEngine with:
    - Comprehensive tracing of all inference operations
    - Performance monitoring and metrics
    - Evidence sufficiency tracking
    - Detailed model prediction logging
    - Audit trail for regulatory compliance
    """
    
    def __init__(self, tracing_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced Bayesian engine with tracing.
        
        Args:
            tracing_config: Configuration for OpenInference tracing
        """
        super().__init__()
        self.tracer = get_tracer(tracing_config)
        self.session_id = str(uuid.uuid4())
        
        logger.info(f"Enhanced Bayesian engine initialized with session {self.session_id}")
    
    def calculate_insider_dealing_risk(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate insider dealing risk with comprehensive tracing.
        
        Args:
            processed_data: Processed trading data
            
        Returns:
            Risk assessment results with tracing metadata
        """
        with self.tracer.trace_bayesian_inference(
            model_name="insider_dealing",
            model_version="1.0.0",
            input_data=processed_data
        ) as span:
            try:
                # Log input characteristics
                if span:
                    self._log_input_characteristics(span, processed_data, "insider_dealing")
                
                # Perform the actual risk calculation
                start_time = datetime.utcnow()
                risk_result = super().calculate_insider_dealing_risk(processed_data)
                end_time = datetime.utcnow()
                
                # Calculate performance metrics
                processing_time = (end_time - start_time).total_seconds()
                
                # Enhanced result with tracing metadata
                enhanced_result = {
                    **risk_result,
                    "tracing_metadata": {
                        "session_id": self.session_id,
                        "processing_time_seconds": processing_time,
                        "timestamp": end_time.isoformat(),
                        "model_type": "insider_dealing",
                        "trace_id": span.get_span_context().trace_id if span else None
                    }
                }
                
                # Log prediction results
                if span:
                    self._log_prediction_results(span, enhanced_result, processing_time)
                
                logger.info(f"Insider dealing risk calculated in {processing_time:.3f}s")
                return enhanced_result
                
            except Exception as e:
                logger.error(f"Error in insider dealing risk calculation: {e}")
                if span:
                    span.record_exception(e)
                raise
    
    def calculate_spoofing_risk(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate spoofing risk with comprehensive tracing.
        
        Args:
            processed_data: Processed trading data
            
        Returns:
            Risk assessment results with tracing metadata
        """
        with self.tracer.trace_bayesian_inference(
            model_name="spoofing",
            model_version="1.0.0",
            input_data=processed_data
        ) as span:
            try:
                # Log input characteristics
                if span:
                    self._log_input_characteristics(span, processed_data, "spoofing")
                
                # Perform the actual risk calculation
                start_time = datetime.utcnow()
                risk_result = super().calculate_spoofing_risk(processed_data)
                end_time = datetime.utcnow()
                
                # Calculate performance metrics
                processing_time = (end_time - start_time).total_seconds()
                
                # Enhanced result with tracing metadata
                enhanced_result = {
                    **risk_result,
                    "tracing_metadata": {
                        "session_id": self.session_id,
                        "processing_time_seconds": processing_time,
                        "timestamp": end_time.isoformat(),
                        "model_type": "spoofing",
                        "trace_id": span.get_span_context().trace_id if span else None
                    }
                }
                
                # Log prediction results
                if span:
                    self._log_prediction_results(span, enhanced_result, processing_time)
                
                logger.info(f"Spoofing risk calculated in {processing_time:.3f}s")
                return enhanced_result
                
            except Exception as e:
                logger.error(f"Error in spoofing risk calculation: {e}")
                if span:
                    span.record_exception(e)
                raise
    
    def calculate_insider_dealing_risk_with_latent_intent(
        self, 
        processed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate insider dealing risk with latent intent modeling and tracing.
        
        Args:
            processed_data: Processed trading data
            
        Returns:
            Risk assessment results with tracing metadata
        """
        with self.tracer.trace_bayesian_inference(
            model_name="insider_dealing_latent_intent",
            model_version="1.0.0",
            input_data=processed_data
        ) as span:
            try:
                # Log input characteristics
                if span:
                    self._log_input_characteristics(span, processed_data, "insider_dealing_latent_intent")
                    span.set_attribute("model.latent_intent", True)
                
                # Perform the actual risk calculation
                start_time = datetime.utcnow()
                risk_result = super().calculate_insider_dealing_risk_with_latent_intent(processed_data)
                end_time = datetime.utcnow()
                
                # Calculate performance metrics
                processing_time = (end_time - start_time).total_seconds()
                
                # Enhanced result with tracing metadata
                enhanced_result = {
                    **risk_result,
                    "tracing_metadata": {
                        "session_id": self.session_id,
                        "processing_time_seconds": processing_time,
                        "timestamp": end_time.isoformat(),
                        "model_type": "insider_dealing_latent_intent",
                        "trace_id": span.get_span_context().trace_id if span else None
                    }
                }
                
                # Log prediction results
                if span:
                    self._log_prediction_results(span, enhanced_result, processing_time)
                
                logger.info(f"Insider dealing risk (latent intent) calculated in {processing_time:.3f}s")
                return enhanced_result
                
            except Exception as e:
                logger.error(f"Error in latent intent insider dealing risk calculation: {e}")
                if span:
                    span.record_exception(e)
                raise
    
    def _log_input_characteristics(
        self, 
        span: Any, 
        processed_data: Dict[str, Any], 
        model_type: str
    ):
        """
        Log input data characteristics to the trace span.
        
        Args:
            span: OpenTelemetry span
            processed_data: Input data
            model_type: Type of model being used
        """
        try:
            # Basic input statistics
            trades = processed_data.get("trades", [])
            orders = processed_data.get("orders", [])
            material_events = processed_data.get("material_events", [])
            
            span.set_attribute("input.trade_count", len(trades))
            span.set_attribute("input.order_count", len(orders))
            span.set_attribute("input.material_events_count", len(material_events))
            
            # Trading volume and value statistics
            if trades:
                total_volume = sum(trade.get("volume", 0) for trade in trades)
                total_value = sum(trade.get("value", 0) for trade in trades)
                avg_price = total_value / total_volume if total_volume > 0 else 0
                
                span.set_attribute("input.total_volume", total_volume)
                span.set_attribute("input.total_value", total_value)
                span.set_attribute("input.average_price", avg_price)
            
            # Time range analysis
            if trades:
                timestamps = [trade.get("timestamp") for trade in trades if trade.get("timestamp")]
                if timestamps:
                    span.set_attribute("input.time_range_hours", 
                                     self._calculate_time_range_hours(timestamps))
            
            # Model-specific attributes
            span.set_attribute("model.inference_type", model_type)
            span.set_attribute("session.id", self.session_id)
            
        except Exception as e:
            logger.warning(f"Failed to log input characteristics: {e}")
    
    def _log_prediction_results(
        self, 
        span: Any, 
        result: Dict[str, Any], 
        processing_time: float
    ):
        """
        Log prediction results to the trace span.
        
        Args:
            span: OpenTelemetry span
            result: Prediction results
            processing_time: Time taken for processing
        """
        try:
            # Core prediction metrics
            if "overall_score" in result:
                span.set_attribute("prediction.risk_score", result["overall_score"])
            
            if "confidence" in result:
                span.set_attribute("prediction.confidence", result["confidence"])
            
            if "evidence_sufficiency_index" in result:
                span.set_attribute("prediction.evidence_sufficiency", 
                                 result["evidence_sufficiency_index"])
            
            # Risk level classification
            risk_score = result.get("overall_score", 0)
            if risk_score >= 0.8:
                risk_level = "HIGH"
            elif risk_score >= 0.5:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            span.set_attribute("prediction.risk_level", risk_level)
            
            # Performance metrics
            span.set_attribute("performance.processing_time_seconds", processing_time)
            span.set_attribute("performance.processing_time_ms", processing_time * 1000)
            
            # Alert information
            if "alerts" in result:
                alerts = result["alerts"]
                span.set_attribute("prediction.alert_count", len(alerts))
                if alerts:
                    alert_types = [alert.get("type", "unknown") for alert in alerts]
                    span.set_attribute("prediction.alert_types", ",".join(alert_types))
            
            # Contributing factors
            if "contributing_factors" in result:
                factors = result["contributing_factors"]
                span.set_attribute("prediction.contributing_factors_count", len(factors))
                if factors:
                    factor_names = [factor.get("name", "unknown") for factor in factors]
                    span.set_attribute("prediction.contributing_factors", ",".join(factor_names))
            
        except Exception as e:
            logger.warning(f"Failed to log prediction results: {e}")
    
    def _calculate_time_range_hours(self, timestamps: List[str]) -> float:
        """
        Calculate the time range in hours from a list of timestamps.
        
        Args:
            timestamps: List of timestamp strings
            
        Returns:
            Time range in hours
        """
        try:
            parsed_timestamps = []
            for ts in timestamps:
                if isinstance(ts, str):
                    # Assuming ISO format timestamps
                    parsed_timestamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
                elif isinstance(ts, datetime):
                    parsed_timestamps.append(ts)
            
            if len(parsed_timestamps) >= 2:
                min_time = min(parsed_timestamps)
                max_time = max(parsed_timestamps)
                return (max_time - min_time).total_seconds() / 3600
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Failed to calculate time range: {e}")
            return 0.0
    
    def get_tracing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of tracing information for this session.
        
        Returns:
            Tracing summary information
        """
        return {
            "session_id": self.session_id,
            "tracer_enabled": self.tracer.enabled,
            "initialization_time": datetime.utcnow().isoformat(),
            "models_loaded": self.models_loaded
        }
