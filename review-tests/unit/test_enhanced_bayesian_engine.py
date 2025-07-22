"""
Unit tests for Enhanced Bayesian Engine with OpenInference tracing.
"""

import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

import sys
sys.path.insert(0, 'src')

from src.core.engines.enhanced_bayesian_engine import EnhancedBayesianEngine


@pytest.mark.unit
class TestEnhancedBayesianEngine:
    """Unit tests for the EnhancedBayesianEngine class."""
    
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
    
    def test_calculate_time_range_hours(self):
        """Test time range calculation helper method."""
        engine = EnhancedBayesianEngine()
        
        timestamps = [
            "2024-01-15T10:00:00Z",
            "2024-01-15T12:00:00Z"
        ]
        
        time_range = engine._calculate_time_range_hours(timestamps)
        assert time_range == 2.0  # 2 hours difference
    
    def test_calculate_time_range_hours_empty(self):
        """Test time range calculation with empty timestamps."""
        engine = EnhancedBayesianEngine()
        
        time_range = engine._calculate_time_range_hours([])
        assert time_range == 0.0
    
    def test_calculate_time_range_hours_single(self):
        """Test time range calculation with single timestamp."""
        engine = EnhancedBayesianEngine()
        
        timestamps = ["2024-01-15T10:00:00Z"]
        time_range = engine._calculate_time_range_hours(timestamps)
        assert time_range == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
