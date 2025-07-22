"""
Unit tests for OpenInference tracer implementation.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

import sys
sys.path.insert(0, 'src')

from src.utils.openinference_tracer import (
    KorinsicOpenInferenceTracer,
    get_tracer,
    initialize_tracing
)


@pytest.mark.unit
class TestKorinsicOpenInferenceTracer:
    """Unit tests for the KorinsicOpenInferenceTracer class."""
    
    def test_tracer_initialization_disabled(self):
        """Test tracer initialization when OpenTelemetry is not available."""
        with patch('src.utils.openinference_tracer.OPENTELEMETRY_AVAILABLE', False):
            tracer = KorinsicOpenInferenceTracer()
            assert tracer.enabled is False
            assert tracer.tracer is None
            assert tracer.tracer_provider is None
    
    @patch('src.utils.openinference_tracer.OPENTELEMETRY_AVAILABLE', True)
    @patch('src.utils.openinference_tracer.TracerProvider')
    @patch('src.utils.openinference_tracer.trace')
    def test_tracer_initialization_enabled(self, mock_trace, mock_tracer_provider):
        """Test tracer initialization when OpenTelemetry is available."""
        mock_provider = Mock()
        mock_tracer_provider.return_value = mock_provider
        mock_tracer = Mock()
        mock_trace.get_tracer.return_value = mock_tracer
        
        config = {'enabled': True}
        tracer = KorinsicOpenInferenceTracer(config)
        
        assert tracer.enabled is True
        assert tracer.config == config
    
    def test_trace_bayesian_inference_disabled(self):
        """Test Bayesian inference tracing when tracer is disabled."""
        tracer = KorinsicOpenInferenceTracer({'enabled': False})
        tracer.enabled = False
        tracer.tracer = None
        
        with tracer.trace_bayesian_inference("test_model") as span:
            assert span is None
    
    def test_get_tracer_singleton(self):
        """Test that get_tracer returns the same instance."""
        # Reset singleton
        import src.utils.openinference_tracer
        src.utils.openinference_tracer._tracer_instance = None
        
        tracer1 = get_tracer()
        tracer2 = get_tracer()
        
        assert tracer1 is tracer2
    
    def test_initialize_tracing(self):
        """Test initialize_tracing function."""
        config = {'enabled': True}
        
        # Should not raise exception
        initialize_tracing(config)
        
        # Should create tracer instance
        tracer = get_tracer()
        assert tracer is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
