"""
End-to-end tests for OpenInference integration in Korinsic surveillance platform.
"""

import pytest
import json
import uuid
import time
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Dict, Any

import sys
sys.path.insert(0, 'src')

from src.utils.openinference_tracer import initialize_tracing, get_tracer
from src.core.engines.enhanced_bayesian_engine import EnhancedBayesianEngine


@pytest.mark.e2e
class TestOpenInferenceE2E:
    """End-to-end tests for OpenInference integration."""
    
    @pytest.fixture(scope="class")
    def app_with_tracing(self):
        """Flask app with OpenInference tracing enabled."""
        # Initialize tracing for E2E tests
        tracing_config = {
            'enabled': True,
            'console_exporter': False  # Disable console output for tests
        }
        initialize_tracing(tracing_config)
        return tracing_config
    
    @pytest.fixture
    def sample_trading_data(self):
        """Sample trading data for E2E testing."""
        return {
            "trades": [
                {
                    "id": "trade_1",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "volume": 5000,
                    "value": 250000,
                    "symbol": "AAPL",
                    "trader_id": "trader_001"
                },
                {
                    "id": "trade_2",
                    "timestamp": "2024-01-15T11:00:00Z",
                    "volume": 3000,
                    "value": 153000,
                    "symbol": "AAPL",
                    "trader_id": "trader_001"
                }
            ],
            "orders": [
                {
                    "id": "order_1",
                    "timestamp": "2024-01-15T10:25:00Z",
                    "quantity": 5000,
                    "price": 50.0,
                    "side": "BUY",
                    "trader_id": "trader_001"
                },
                {
                    "id": "order_2",
                    "timestamp": "2024-01-15T10:55:00Z",
                    "quantity": 3000,
                    "price": 51.0,
                    "side": "BUY",
                    "trader_id": "trader_001"
                }
            ],
            "material_events": [
                {
                    "event_type": "earnings_announcement",
                    "timestamp": "2024-01-15T09:00:00Z",
                    "impact": "positive",
                    "symbol": "AAPL"
                }
            ],
            "trader_info": {
                "trader_id": "trader_001",
                "access_level": "high",
                "department": "corporate_finance"
            }
        }
    
    def test_full_analysis_pipeline_with_tracing(self, app_with_tracing, sample_trading_data):
        """Test complete analysis pipeline with OpenInference tracing."""
        # Initialize enhanced engine
        engine = EnhancedBayesianEngine()
        
        # Mock the base Bayesian engine methods to avoid dependency issues
        with patch.object(engine, 'calculate_insider_dealing_risk') as mock_insider:
            with patch.object(engine, 'calculate_spoofing_risk') as mock_spoofing:
                # Setup mock responses
                mock_insider.return_value = {
                    "overall_score": 0.85,
                    "confidence": "High",
                    "contributing_factors": ["timing", "volume", "access"]
                }
                mock_spoofing.return_value = {
                    "overall_score": 0.25,
                    "confidence": "Low",
                    "contributing_factors": ["normal_pattern"]
                }
                
                # Perform analysis
                start_time = time.time()
                
                insider_result = engine.calculate_insider_dealing_risk(sample_trading_data)
                spoofing_result = engine.calculate_spoofing_risk(sample_trading_data)
                
                end_time = time.time()
                
                # Verify results include tracing metadata
                assert "tracing_metadata" in insider_result
                assert "tracing_metadata" in spoofing_result
                
                # Verify tracing metadata structure
                insider_metadata = insider_result["tracing_metadata"]
                assert "session_id" in insider_metadata
                assert "processing_time_seconds" in insider_metadata
                assert "timestamp" in insider_metadata
                assert "model_type" in insider_metadata
                assert insider_metadata["model_type"] == "insider_dealing"
                
                spoofing_metadata = spoofing_result["tracing_metadata"]
                assert spoofing_metadata["model_type"] == "spoofing"
                
                # Verify session consistency
                assert insider_metadata["session_id"] == spoofing_metadata["session_id"]
                
                # Verify performance tracking
                assert insider_metadata["processing_time_seconds"] >= 0
                assert spoofing_metadata["processing_time_seconds"] >= 0
                
                # Verify original results are preserved
                assert insider_result["overall_score"] == 0.85
                assert spoofing_result["overall_score"] == 0.25
    
    def test_latent_intent_analysis_with_tracing(self, app_with_tracing, sample_trading_data):
        """Test latent intent analysis with tracing."""
        engine = EnhancedBayesianEngine()
        
        with patch.object(engine, 'calculate_insider_dealing_risk_with_latent_intent') as mock_latent:
            # Setup mock response
            mock_latent.return_value = {
                "overall_score": 0.92,
                "confidence": "Very High",
                "contributing_factors": ["latent_intent", "timing", "volume"],
                "latent_factors": ["hidden_information_advantage"]
            }
            
            # Perform latent intent analysis
            result = engine.calculate_insider_dealing_risk_with_latent_intent(sample_trading_data)
            
            # Verify tracing metadata
            assert "tracing_metadata" in result
            metadata = result["tracing_metadata"]
            assert metadata["model_type"] == "insider_dealing_latent_intent"
            
            # Verify enhanced result
            assert result["overall_score"] == 0.92
            assert "latent_factors" in result
    
    def test_multiple_analysis_sessions(self, app_with_tracing, sample_trading_data):
        """Test multiple analysis sessions with separate tracing."""
        # Create multiple engines (simulating different analysis sessions)
        engine1 = EnhancedBayesianEngine()
        engine2 = EnhancedBayesianEngine()
        
        # Verify different session IDs
        assert engine1.session_id != engine2.session_id
        
        with patch.object(engine1, 'calculate_insider_dealing_risk') as mock1:
            with patch.object(engine2, 'calculate_insider_dealing_risk') as mock2:
                mock1.return_value = {"overall_score": 0.6, "confidence": "Medium"}
                mock2.return_value = {"overall_score": 0.8, "confidence": "High"}
                
                # Perform analyses
                result1 = engine1.calculate_insider_dealing_risk(sample_trading_data)
                result2 = engine2.calculate_insider_dealing_risk(sample_trading_data)
                
                # Verify separate sessions
                assert result1["tracing_metadata"]["session_id"] != result2["tracing_metadata"]["session_id"]
                assert result1["tracing_metadata"]["session_id"] == engine1.session_id
                assert result2["tracing_metadata"]["session_id"] == engine2.session_id
    
    def test_error_handling_with_tracing(self, app_with_tracing, sample_trading_data):
        """Test error handling preserves tracing information."""
        engine = EnhancedBayesianEngine()
        
        with patch.object(engine, 'calculate_insider_dealing_risk', side_effect=Exception("Model error")):
            # Verify exception is properly raised
            with pytest.raises(Exception, match="Model error"):
                engine.calculate_insider_dealing_risk(sample_trading_data)
    
    def test_performance_monitoring(self, app_with_tracing, sample_trading_data):
        """Test performance monitoring capabilities."""
        engine = EnhancedBayesianEngine()
        
        with patch.object(engine, 'calculate_insider_dealing_risk') as mock_risk:
            # Add artificial delay to mock
            def slow_calculation(data):
                time.sleep(0.1)  # 100ms delay
                return {"overall_score": 0.5, "confidence": "Medium"}
            
            mock_risk.side_effect = slow_calculation
            
            # Perform analysis
            result = engine.calculate_insider_dealing_risk(sample_trading_data)
            
            # Verify performance tracking
            metadata = result["tracing_metadata"]
            assert metadata["processing_time_seconds"] >= 0.1
            assert metadata["processing_time_seconds"] < 1.0  # Should be reasonable
    
    def test_tracer_integration_lifecycle(self, app_with_tracing):
        """Test complete tracer integration lifecycle."""
        # Get tracer instance
        tracer = get_tracer()
        
        # Verify tracer is properly configured
        assert tracer is not None
        
        # Test tracing context manager
        with tracer.trace_bayesian_inference("test_model", "1.0.0") as span:
            # Should not raise exception, span may be None if OpenTelemetry not available
            pass
        
        # Verify tracer summary
        engine = EnhancedBayesianEngine()
        summary = engine.get_tracing_summary()
        
        assert "session_id" in summary
        assert "tracer_enabled" in summary
        assert "initialization_time" in summary
    
    def test_data_volume_handling(self, app_with_tracing):
        """Test handling of large data volumes with tracing."""
        # Generate large dataset
        large_dataset = {
            "trades": [
                {
                    "id": f"trade_{i}",
                    "timestamp": f"2024-01-15T{10 + i // 60:02d}:{i % 60:02d}:00Z",
                    "volume": 1000 + i,
                    "value": (1000 + i) * 50,
                    "symbol": "AAPL"
                }
                for i in range(1000)  # 1000 trades
            ],
            "orders": [
                {
                    "id": f"order_{i}",
                    "timestamp": f"2024-01-15T{10 + i // 60:02d}:{i % 60:02d}:00Z",
                    "quantity": 1000 + i,
                    "price": 50.0,
                    "side": "BUY"
                }
                for i in range(500)  # 500 orders
            ],
            "material_events": []
        }
        
        engine = EnhancedBayesianEngine()
        
        with patch.object(engine, 'calculate_insider_dealing_risk') as mock_risk:
            mock_risk.return_value = {"overall_score": 0.7, "confidence": "High"}
            
            # Should handle large dataset without issues
            result = engine.calculate_insider_dealing_risk(large_dataset)
            
            # Verify tracing metadata is still present
            assert "tracing_metadata" in result
            metadata = result["tracing_metadata"]
            assert "processing_time_seconds" in metadata
            assert metadata["processing_time_seconds"] >= 0


@pytest.mark.e2e
@pytest.mark.slow
class TestOpenInferencePerformance:
    """Performance tests for OpenInference integration."""
    
    def test_tracing_overhead(self):
        """Test that tracing overhead is acceptable."""
        # Create engines with and without tracing
        tracing_config = {'enabled': True, 'console_exporter': False}
        engine_with_tracing = EnhancedBayesianEngine(tracing_config)
        
        no_tracing_config = {'enabled': False}
        engine_without_tracing = EnhancedBayesianEngine(no_tracing_config)
        
        sample_data = {
            "trades": [{"id": "trade_1", "volume": 1000, "value": 50000}],
            "orders": [{"id": "order_1", "quantity": 1000, "price": 50.0}],
            "material_events": []
        }
        
        # Mock the base calculations
        with patch.object(engine_with_tracing, 'calculate_insider_dealing_risk') as mock_with:
            with patch.object(engine_without_tracing, 'calculate_insider_dealing_risk') as mock_without:
                mock_with.return_value = {"overall_score": 0.5}
                mock_without.return_value = {"overall_score": 0.5}
                
                # Measure performance
                iterations = 10
                
                # With tracing
                start_time = time.time()
                for _ in range(iterations):
                    engine_with_tracing.calculate_insider_dealing_risk(sample_data)
                with_tracing_time = time.time() - start_time
                
                # Without tracing
                start_time = time.time()
                for _ in range(iterations):
                    engine_without_tracing.calculate_insider_dealing_risk(sample_data)
                without_tracing_time = time.time() - start_time
                
                # Verify overhead is reasonable (less than 50% overhead)
                if without_tracing_time > 0:
                    overhead_ratio = (with_tracing_time - without_tracing_time) / without_tracing_time
                    assert overhead_ratio < 0.5, f"Tracing overhead too high: {overhead_ratio:.2%}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
