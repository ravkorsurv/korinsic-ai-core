"""
Integration tests for OpenInference tracing in Korinsic surveillance platform.

These tests validate that OpenInference observability is properly integrated
with the Bayesian inference models and API endpoints.
"""

import pytest
import json
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from src.utils.openinference_tracer import KorinsicOpenInferenceTracer, get_tracer, initialize_tracing
from src.core.engines.enhanced_bayesian_engine import EnhancedBayesianEngine
from src.api.v1.routes.enhanced_analysis import enhanced_analysis_bp


class TestOpenInferenceTracer:
    """Test the OpenInference tracer implementation."""
    
    def test_tracer_initialization(self):
        """Test that the tracer initializes correctly."""
        config = {
            'enabled': True,
            'console_exporter': True
        }
        tracer = KorinsicOpenInferenceTracer(config)
        
        assert tracer.config == config
        assert tracer.enabled in [True, False]  # Depends on OpenTelemetry availability
    
    def test_tracer_singleton_pattern(self):
        """Test that get_tracer returns the same instance."""
        tracer1 = get_tracer()
        tracer2 = get_tracer()
        
        assert tracer1 is tracer2
    
    @patch('src.utils.openinference_tracer.OPENTELEMETRY_AVAILABLE', True)
    @patch('src.utils.openinference_tracer.trace')
    def test_bayesian_inference_tracing(self, mock_trace):
        """Test tracing of Bayesian inference operations."""
        # Setup mock span
        mock_span = Mock()
        mock_tracer = Mock()
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
        mock_trace.get_tracer.return_value = mock_tracer
        
        # Create tracer and test
        tracer = KorinsicOpenInferenceTracer({'enabled': True})
        tracer.tracer = mock_tracer
        tracer.enabled = True
        
        input_data = {
            "trades": [{"id": 1, "volume": 100}],
            "orders": [{"id": 1, "quantity": 50}],
            "material_events": [{"event": "earnings"}]
        }
        
        with tracer.trace_bayesian_inference("test_model", "1.0.0", input_data):
            pass
        
        # Verify span was created and attributes were set
        mock_tracer.start_as_current_span.assert_called_once()
        mock_span.set_attribute.assert_called()
    
    def test_disabled_tracer_fallback(self):
        """Test that disabled tracer falls back gracefully."""
        tracer = KorinsicOpenInferenceTracer({'enabled': False})
        
        with tracer.trace_bayesian_inference("test_model") as span:
            assert span is None


class TestEnhancedBayesianEngine:
    """Test the enhanced Bayesian engine with tracing."""
    
    @pytest.fixture
    def sample_processed_data(self):
        """Sample processed trading data for testing."""
        return {
            "trades": [
                {
                    "id": "trade_1",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "volume": 1000,
                    "value": 50000,
                    "price": 50.0
                },
                {
                    "id": "trade_2", 
                    "timestamp": "2024-01-15T11:00:00Z",
                    "volume": 2000,
                    "value": 102000,
                    "price": 51.0
                }
            ],
            "orders": [
                {
                    "id": "order_1",
                    "timestamp": "2024-01-15T10:25:00Z",
                    "quantity": 1000,
                    "price": 50.0,
                    "side": "BUY"
                }
            ],
            "material_events": [
                {
                    "event_type": "earnings_announcement",
                    "timestamp": "2024-01-15T09:00:00Z",
                    "impact": "positive"
                }
            ]
        }
    
    @patch('src.core.engines.enhanced_bayesian_engine.BayesianEngine')
    def test_enhanced_engine_initialization(self, mock_base_engine):
        """Test that enhanced engine initializes with tracing."""
        tracing_config = {'enabled': True, 'console_exporter': True}
        engine = EnhancedBayesianEngine(tracing_config)
        
        assert engine.session_id is not None
        assert len(engine.session_id) == 36  # UUID format
    
    @patch('src.core.engines.enhanced_bayesian_engine.BayesianEngine.calculate_insider_dealing_risk')
    def test_insider_dealing_risk_with_tracing(self, mock_calculate_risk, sample_processed_data):
        """Test insider dealing risk calculation with tracing metadata."""
        # Setup mock return value
        mock_risk_result = {
            "overall_score": 0.75,
            "confidence": "High",
            "contributing_factors": ["unusual_timing", "large_volume"]
        }
        mock_calculate_risk.return_value = mock_risk_result
        
        # Create enhanced engine
        engine = EnhancedBayesianEngine()
        
        # Calculate risk
        result = engine.calculate_insider_dealing_risk(sample_processed_data)
        
        # Verify enhanced result structure
        assert "tracing_metadata" in result
        assert "session_id" in result["tracing_metadata"]
        assert "processing_time_seconds" in result["tracing_metadata"]
        assert "timestamp" in result["tracing_metadata"]
        assert "model_type" in result["tracing_metadata"]
        
        # Verify original result is preserved
        assert result["overall_score"] == 0.75
        assert result["confidence"] == "High"
        assert result["contributing_factors"] == ["unusual_timing", "large_volume"]
    
    @patch('src.core.engines.enhanced_bayesian_engine.BayesianEngine.calculate_spoofing_risk')
    def test_spoofing_risk_with_tracing(self, mock_calculate_risk, sample_processed_data):
        """Test spoofing risk calculation with tracing metadata."""
        # Setup mock return value
        mock_risk_result = {
            "overall_score": 0.45,
            "confidence": "Medium",
            "contributing_factors": ["order_clustering"]
        }
        mock_calculate_risk.return_value = mock_risk_result
        
        # Create enhanced engine
        engine = EnhancedBayesianEngine()
        
        # Calculate risk
        result = engine.calculate_spoofing_risk(sample_processed_data)
        
        # Verify enhanced result structure
        assert "tracing_metadata" in result
        assert result["tracing_metadata"]["model_type"] == "spoofing"
        
        # Verify original result is preserved
        assert result["overall_score"] == 0.45
        assert result["confidence"] == "Medium"
    
    def test_tracing_summary(self):
        """Test tracing summary functionality."""
        engine = EnhancedBayesianEngine()
        summary = engine.get_tracing_summary()
        
        assert "session_id" in summary
        assert "tracer_enabled" in summary
        assert "initialization_time" in summary
        assert "models_loaded" in summary


class TestEnhancedAnalysisAPI:
    """Test the enhanced analysis API with OpenInference integration."""
    
    @pytest.fixture
    def client(self, app):
        """Test client for the Flask app."""
        app.register_blueprint(enhanced_analysis_bp, url_prefix='/api/v1')
        return app.test_client()
    
    @pytest.fixture
    def sample_request_data(self):
        """Sample request data for API testing."""
        return {
            "trades": [
                {
                    "id": "trade_1",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "volume": 1000,
                    "value": 50000,
                    "symbol": "AAPL"
                }
            ],
            "orders": [
                {
                    "id": "order_1",
                    "timestamp": "2024-01-15T10:25:00Z",
                    "quantity": 1000,
                    "price": 50.0,
                    "side": "BUY"
                }
            ],
            "material_events": [
                {
                    "event_type": "earnings_announcement",
                    "timestamp": "2024-01-15T09:00:00Z"
                }
            ],
            "use_latent_intent": False,
            "include_regulatory_rationale": True
        }
    
    @patch('src.api.v1.routes.enhanced_analysis.enhanced_bayesian_engine')
    def test_enhanced_analysis_endpoint(self, mock_engine, client, sample_request_data):
        """Test the enhanced analysis endpoint."""
        # Setup mock engine responses
        mock_insider_result = {
            "overall_score": 0.65,
            "confidence": "High",
            "contributing_factors": ["timing", "volume"],
            "tracing_metadata": {
                "session_id": str(uuid.uuid4()),
                "processing_time_seconds": 0.15,
                "model_type": "insider_dealing"
            }
        }
        
        mock_spoofing_result = {
            "overall_score": 0.30,
            "confidence": "Low",
            "contributing_factors": ["normal_pattern"],
            "tracing_metadata": {
                "session_id": str(uuid.uuid4()),
                "processing_time_seconds": 0.12,
                "model_type": "spoofing"
            }
        }
        
        mock_engine.calculate_insider_dealing_risk.return_value = mock_insider_result
        mock_engine.calculate_spoofing_risk.return_value = mock_spoofing_result
        mock_engine.session_id = str(uuid.uuid4())
        
        # Make request
        response = client.post(
            '/api/v1/analyze/enhanced',
            data=json.dumps(sample_request_data),
            content_type='application/json'
        )
        
        # Verify response
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert "analysis_id" in data["data"]
        assert "risk_scores" in data["data"]
        assert "tracing_metadata" in data["data"]
        
        # Verify tracing metadata
        tracing_metadata = data["data"]["tracing_metadata"]
        assert "session_id" in tracing_metadata
        assert "trace_id" in tracing_metadata
        assert "span_id" in tracing_metadata
        assert "openinference_enabled" in tracing_metadata
    
    @patch('src.api.v1.routes.enhanced_analysis.enhanced_bayesian_engine')
    def test_batch_analysis_endpoint(self, mock_engine, client):
        """Test the enhanced batch analysis endpoint."""
        # Setup mock engine responses
        mock_insider_result = {"overall_score": 0.5, "confidence": "Medium"}
        mock_spoofing_result = {"overall_score": 0.3, "confidence": "Low"}
        
        mock_engine.calculate_insider_dealing_risk.return_value = mock_insider_result
        mock_engine.calculate_spoofing_risk.return_value = mock_spoofing_result
        
        batch_data = {
            "batch_data": [
                {
                    "id": "dataset_1",
                    "trades": [{"id": "trade_1", "volume": 100}],
                    "orders": [{"id": "order_1", "quantity": 50}]
                },
                {
                    "id": "dataset_2", 
                    "trades": [{"id": "trade_2", "volume": 200}],
                    "orders": [{"id": "order_2", "quantity": 100}]
                }
            ]
        }
        
        # Make request
        response = client.post(
            '/api/v1/analyze/batch/enhanced',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # Verify response
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert "batch_id" in data["data"]
        assert "results" in data["data"]
        assert len(data["data"]["results"]) == 2
        assert "batch_metrics" in data["data"]
        assert "tracing_metadata" in data["data"]


class TestOpenInferenceE2E:
    """End-to-end tests for OpenInference integration."""
    
    @pytest.fixture
    def app_with_tracing(self, app):
        """Flask app with OpenInference tracing enabled."""
        # Initialize tracing
        tracing_config = {
            'enabled': True,
            'console_exporter': True
        }
        initialize_tracing(tracing_config)
        
        # Register enhanced routes
        app.register_blueprint(enhanced_analysis_bp, url_prefix='/api/v1')
        
        return app
    
    def test_full_analysis_pipeline_with_tracing(self, app_with_tracing):
        """Test complete analysis pipeline with OpenInference tracing."""
        client = app_with_tracing.test_client()
        
        request_data = {
            "trades": [
                {
                    "id": "trade_1",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "volume": 5000,
                    "value": 250000,
                    "symbol": "AAPL"
                }
            ],
            "orders": [
                {
                    "id": "order_1",
                    "timestamp": "2024-01-15T10:25:00Z",
                    "quantity": 5000,
                    "price": 50.0,
                    "side": "BUY"
                }
            ],
            "material_events": [
                {
                    "event_type": "earnings_announcement",
                    "timestamp": "2024-01-15T09:00:00Z",
                    "impact": "positive"
                }
            ],
            "use_latent_intent": True,
            "include_regulatory_rationale": True
        }
        
        with patch('src.core.engines.enhanced_bayesian_engine.BayesianEngine') as mock_base:
            # Setup mock responses
            mock_base.return_value.calculate_insider_dealing_risk_with_latent_intent.return_value = {
                "overall_score": 0.85,
                "confidence": "High"
            }
            mock_base.return_value.calculate_spoofing_risk.return_value = {
                "overall_score": 0.25,
                "confidence": "Low"
            }
            
            # Make request
            response = client.post(
                '/api/v1/analyze/enhanced',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            # Verify response structure includes tracing
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            
            # Verify comprehensive tracing metadata
            tracing_metadata = data["data"]["tracing_metadata"]
            assert all(key in tracing_metadata for key in [
                "session_id", "trace_id", "span_id", "openinference_enabled"
            ])
            
            # Verify alerts were generated for high-risk scenario
            assert len(data["data"]["alerts"]) > 0
            assert any(alert["type"] == "INSIDER_DEALING" for alert in data["data"]["alerts"])
            
            # Verify regulatory rationale was included
            assert len(data["data"]["regulatory_rationales"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
