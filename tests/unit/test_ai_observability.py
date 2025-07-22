#!/usr/bin/env python3
"""
Unit Tests for AI Observability Module

Tests the OpenInference integration components including:
- AI observability initialization
- Bayesian inference tracing
- Evidence mapping observability
- Performance metrics collection
- Error handling with tracing
"""

import pytest
import time
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from utils.ai_observability import (
    KorinsicAIObservability, 
    BayesianInferenceTracer,
    get_ai_observability,
    initialize_ai_observability
)

class TestKorinsicAIObservability:
    """Test suite for KorinsicAIObservability class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.service_name = "test-service"
        self.service_version = "1.0.0-test"
        self.otlp_endpoint = "http://localhost:4317"
    
    @patch('utils.ai_observability.OTLPSpanExporter')
    @patch('utils.ai_observability.TracerProvider')
    @patch('utils.ai_observability.trace.set_tracer_provider')
    def test_initialization(self, mock_set_tracer, mock_tracer_provider, mock_exporter):
        """Test AI observability initialization"""
        # Setup mocks
        mock_provider_instance = Mock()
        mock_tracer_provider.return_value = mock_provider_instance
        mock_exporter_instance = Mock()
        mock_exporter.return_value = mock_exporter_instance
        
        # Initialize observability
        ai_obs = KorinsicAIObservability(
            service_name=self.service_name,
            service_version=self.service_version,
            otlp_endpoint=self.otlp_endpoint
        )
        
        # Verify initialization
        assert ai_obs.service_name == self.service_name
        assert ai_obs.service_version == self.service_version
        assert ai_obs.otlp_endpoint == self.otlp_endpoint
        
        # Verify OpenTelemetry setup
        mock_tracer_provider.assert_called_once()
        mock_exporter.assert_called_once_with(endpoint=self.otlp_endpoint, insecure=True)
        mock_set_tracer.assert_called_once_with(mock_provider_instance)
    
    def test_trace_bayesian_inference_context_manager(self):
        """Test Bayesian inference tracing context manager"""
        with patch('utils.ai_observability.trace') as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_tracer.start_span.return_value = mock_span
            
            ai_obs = KorinsicAIObservability()
            ai_obs.tracer = mock_tracer
            
            # Test context manager
            with ai_obs.trace_bayesian_inference("test_model", "test_analysis") as tracer:
                assert isinstance(tracer, BayesianInferenceTracer)
                assert tracer.model_name == "test_model"
                assert tracer.analysis_type == "test_analysis"
            
            # Verify span was started and ended
            mock_tracer.start_span.assert_called_once_with("bayesian_inference.test_model")

class TestBayesianInferenceTracer:
    """Test suite for BayesianInferenceTracer class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.mock_tracer = Mock()
        self.mock_span = Mock()
        self.mock_tracer.start_span.return_value = self.mock_span
        
        self.tracer = BayesianInferenceTracer(
            self.mock_tracer,
            "test_model",
            "test_analysis"
        )
    
    def test_context_manager_entry(self):
        """Test context manager entry"""
        with patch('time.time', return_value=1000.0):
            result = self.tracer.__enter__()
            
            assert result == self.tracer
            assert self.tracer.start_time == 1000.0
            assert self.tracer.span == self.mock_span
            
            # Verify span attributes were set
            expected_calls = [
                (('llm.model_name', 'test_model'),),
                (('ai.model.type', 'bayesian_network'),),
                (('ai.analysis.type', 'test_analysis'),),
                (('ai.system', 'korinsic_surveillance'),)
            ]
            
            actual_calls = self.mock_span.set_attribute.call_args_list
            assert len(actual_calls) >= len(expected_calls)
    
    def test_context_manager_exit_success(self):
        """Test context manager exit on success"""
        self.tracer.span = self.mock_span
        self.tracer.start_time = 1000.0
        
        with patch('time.time', return_value=1000.1):  # 100ms later
            self.tracer.__exit__(None, None, None)
            
            # Verify latency was recorded
            self.mock_span.set_attribute.assert_any_call('ai.inference.latency_ms', 100.0)
            self.mock_span.end.assert_called_once()
    
    def test_context_manager_exit_with_error(self):
        """Test context manager exit with error"""
        self.tracer.span = self.mock_span
        self.tracer.start_time = 1000.0
        
        test_exception = Exception("Test error")
        
        with patch('time.time', return_value=1000.05):  # 50ms later
            self.tracer.__exit__(Exception, test_exception, None)
            
            # Verify error handling
            self.mock_span.record_exception.assert_called_once_with(test_exception)
            self.mock_span.end.assert_called_once()
    
    def test_set_evidence(self):
        """Test setting evidence data"""
        self.tracer.span = self.mock_span
        
        evidence = {
            'trade_pattern': 1,
            'comms_intent': 2,
            'pnl_drift': 1
        }
        
        self.tracer.set_evidence(evidence)
        
        # Verify evidence attributes were set
        expected_calls = [
            (('ai.evidence.keys', ['trade_pattern', 'comms_intent', 'pnl_drift']),),
            (('ai.evidence.count', 3),),
            (('llm.input_messages', str(evidence)),)
        ]
        
        actual_calls = self.mock_span.set_attribute.call_args_list
        for expected_call in expected_calls:
            assert expected_call in actual_calls
    
    def test_set_result(self):
        """Test setting inference results"""
        self.tracer.span = self.mock_span
        
        risk_score = 0.75
        confidence = "high"
        
        self.tracer.set_result(risk_score, confidence)
        
        # Verify result attributes were set
        expected_calls = [
            (('ai.risk.score', 0.75),),
            (('ai.confidence', 'high'),),
            (('llm.output_messages', 'Risk Score: 0.75, Confidence: high'),)
        ]
        
        actual_calls = self.mock_span.set_attribute.call_args_list
        for expected_call in expected_calls:
            assert expected_call in actual_calls

class TestGlobalObservabilityFunctions:
    """Test suite for global observability functions"""
    
    def test_get_ai_observability_singleton(self):
        """Test that get_ai_observability returns singleton instance"""
        # Clear any existing instance
        import utils.ai_observability
        utils.ai_observability._ai_observability = None
        
        with patch.object(utils.ai_observability, 'KorinsicAIObservability') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            # First call should create instance
            result1 = get_ai_observability()
            assert result1 == mock_instance
            mock_class.assert_called_once()
            
            # Second call should return same instance
            result2 = get_ai_observability()
            assert result2 == mock_instance
            assert result1 is result2
            # Should not create new instance
            assert mock_class.call_count == 1
    
    def test_initialize_ai_observability(self):
        """Test initialize_ai_observability function"""
        with patch.object(utils.ai_observability, 'KorinsicAIObservability') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            result = initialize_ai_observability(
                service_name="test-service",
                service_version="2.0.0",
                otlp_endpoint="http://test:4317"
            )
            
            assert result == mock_instance
            mock_class.assert_called_once_with(
                service_name="test-service",
                service_version="2.0.0",
                otlp_endpoint="http://test:4317"
            )

class TestIntegrationScenarios:
    """Integration test scenarios for AI observability"""
    
    @patch('utils.ai_observability.OTLPSpanExporter')
    @patch('utils.ai_observability.TracerProvider')
    @patch('utils.ai_observability.trace.set_tracer_provider')
    def test_full_bayesian_inference_tracing_flow(self, mock_set_tracer, mock_tracer_provider, mock_exporter):
        """Test complete Bayesian inference tracing flow"""
        # Setup mocks
        mock_provider_instance = Mock()
        mock_tracer_provider.return_value = mock_provider_instance
        mock_tracer_instance = Mock()
        mock_span = Mock()
        mock_tracer_instance.start_span.return_value = mock_span
        
        with patch('utils.ai_observability.trace.get_tracer', return_value=mock_tracer_instance):
            # Initialize AI observability
            ai_obs = KorinsicAIObservability()
            
            # Simulate Bayesian inference tracing
            evidence = {'trade_pattern': 1, 'comms_intent': 0}
            risk_score = 0.65
            confidence = "medium"
            
            with ai_obs.trace_bayesian_inference("insider_dealing", "market_abuse") as tracer:
                tracer.set_evidence(evidence)
                # Simulate some processing time
                time.sleep(0.001)
                tracer.set_result(risk_score, confidence)
            
            # Verify the complete flow
            mock_tracer_instance.start_span.assert_called_once_with("bayesian_inference.insider_dealing")
            
            # Verify evidence was set
            mock_span.set_attribute.assert_any_call('ai.evidence.count', 2)
            mock_span.set_attribute.assert_any_call('ai.evidence.keys', ['trade_pattern', 'comms_intent'])
            
            # Verify result was set
            mock_span.set_attribute.assert_any_call('ai.risk.score', 0.65)
            mock_span.set_attribute.assert_any_call('ai.confidence', 'medium')
            
            # Verify span was ended
            mock_span.end.assert_called_once()

# Pytest fixtures and configuration
@pytest.fixture
def mock_ai_observability():
    """Fixture providing a mocked AI observability instance"""
    with patch('utils.ai_observability.KorinsicAIObservability') as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        yield mock_instance

def test_performance_impact():
    """Test that AI observability has minimal performance impact"""
    # This is a basic performance test to ensure tracing doesn't add significant overhead
    
    def dummy_inference():
        time.sleep(0.001)  # Simulate 1ms inference
        return {"risk_score": 0.5}
    
    # Measure without tracing
    start_time = time.time()
    for _ in range(10):
        dummy_inference()
    baseline_time = time.time() - start_time
    
    # Measure with tracing (mocked)
    with patch('utils.ai_observability.KorinsicAIObservability') as mock_class:
        mock_instance = Mock()
        mock_tracer = Mock()
        mock_span = Mock()
        mock_tracer.start_span.return_value = mock_span
        mock_instance.tracer = mock_tracer
        mock_class.return_value = mock_instance
        
        ai_obs = KorinsicAIObservability()
        
        start_time = time.time()
        for _ in range(10):
            with ai_obs.trace_bayesian_inference("test", "test") as tracer:
                dummy_inference()
                tracer.set_result(0.5, "medium")
        traced_time = time.time() - start_time
    
    # Tracing overhead should be minimal (less than 50% overhead)
    overhead_ratio = (traced_time - baseline_time) / baseline_time
    assert overhead_ratio < 0.5, f"Tracing overhead too high: {overhead_ratio:.2%}"

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
