"""
Comprehensive tests for Advanced Drift Detection System

This test suite validates:
- Multiple statistical drift detection methods
- Root cause analysis capabilities
- Predictive drift modeling
- Integration with OpenInference tracing
- Alert handling and routing
"""

import pytest
import asyncio
import numpy as np
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import asdict

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from src.analytics.drift_detection import (
    AdvancedDriftAnalyzer,
    DriftAnalysisResult,
    DriftForecast,
    DriftVisualizationData
)
from src.analytics.drift_integration import (
    DriftMonitoringService,
    DriftAlertManager
)


class TestAdvancedDriftAnalyzer:
    """Test suite for AdvancedDriftAnalyzer."""
    
    @pytest.fixture
    def drift_analyzer(self):
        """Create a drift analyzer instance for testing."""
        config = {
            "drift_thresholds": {
                "ks_test": 0.1,
                "psi": 0.2,
                "js_divergence": 0.3,
                "concept_drift": 0.15,
                "temporal_acceleration": 0.05,
                "evidence_pattern": 0.25
            }
        }
        return AdvancedDriftAnalyzer(config)
    
    @pytest.fixture
    def sample_current_data(self):
        """Sample current data for testing."""
        return {
            "feature_1": [1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0],
            "feature_2": [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4],
            "predictions": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            "evidence": {
                "material_info": {"value": 2, "confidence": "High"},
                "trading_activity": {"value": 1, "confidence": "Medium"},
                "timing": {"value": 2, "confidence": "High"}
            }
        }
    
    @pytest.fixture
    def sample_reference_data(self):
        """Sample reference data for testing."""
        return {
            "feature_1": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6],
            "feature_2": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
            "predictions": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
            "evidence": {
                "material_info": {"value": 1, "confidence": "Medium"},
                "trading_activity": {"value": 0, "confidence": "Low"},
                "timing": {"value": 1, "confidence": "Medium"}
            }
        }
    
    @pytest.fixture
    def sample_trace_data(self):
        """Sample trace data for testing."""
        return {
            "performance_metrics": [
                {"accuracy": 0.85, "precision": 0.80, "recall": 0.75},
                {"accuracy": 0.83, "precision": 0.78, "recall": 0.73},
                {"accuracy": 0.81, "precision": 0.76, "recall": 0.71},
                {"accuracy": 0.79, "precision": 0.74, "recall": 0.69},
                {"accuracy": 0.77, "precision": 0.72, "recall": 0.67},
                {"accuracy": 0.75, "precision": 0.70, "recall": 0.65},
                {"accuracy": 0.73, "precision": 0.68, "recall": 0.63},
                {"accuracy": 0.71, "precision": 0.66, "recall": 0.61},
                {"accuracy": 0.69, "precision": 0.64, "recall": 0.59},
                {"accuracy": 0.67, "precision": 0.62, "recall": 0.57},
                {"accuracy": 0.65, "precision": 0.60, "recall": 0.55}
            ]
        }
    
    def test_initialization(self, drift_analyzer):
        """Test drift analyzer initialization."""
        assert drift_analyzer is not None
        assert drift_analyzer.drift_thresholds is not None
        assert drift_analyzer.drift_history == []
        assert len(drift_analyzer.drift_thresholds) == 6
    
    def test_extract_numeric_values(self, drift_analyzer):
        """Test numeric value extraction from various data formats."""
        # Test list input
        list_data = [1.0, 2.0, 3.0, 4.0]
        result = drift_analyzer._extract_numeric_values(list_data)
        assert result == [1.0, 2.0, 3.0, 4.0]
        
        # Test single numeric value
        single_value = 5.5
        result = drift_analyzer._extract_numeric_values(single_value)
        assert result == [5.5]
        
        # Test dictionary input
        dict_data = {"a": 1.0, "b": 2.0, "c": "string"}
        result = drift_analyzer._extract_numeric_values(dict_data)
        assert set(result) == {1.0, 2.0}
        
        # Test empty input
        result = drift_analyzer._extract_numeric_values([])
        assert result == []
    
    def test_calculate_psi(self, drift_analyzer):
        """Test Population Stability Index calculation."""
        current_vals = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        reference_vals = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        
        psi_score = drift_analyzer._calculate_psi(current_vals, reference_vals)
        
        assert isinstance(psi_score, float)
        assert psi_score >= 0.0
        assert psi_score < 10.0  # Reasonable upper bound
    
    def test_calculate_js_divergence(self, drift_analyzer):
        """Test Jensen-Shannon divergence calculation."""
        current_vals = [1.0, 2.0, 3.0, 4.0, 5.0]
        reference_vals = [0.5, 1.5, 2.5, 3.5, 4.5]
        
        js_divergence = drift_analyzer._calculate_js_divergence(current_vals, reference_vals)
        
        assert isinstance(js_divergence, float)
        assert js_divergence >= 0.0
        assert js_divergence <= 1.0  # JS divergence is bounded
    
    def test_calculate_evidence_sufficiency_pattern(self, drift_analyzer):
        """Test evidence sufficiency pattern calculation."""
        evidence = {
            "material_info": {"value": 2, "confidence": "High"},
            "trading_activity": {"value": 1, "confidence": "Medium"},
            "timing": {"value": 0, "confidence": "Low"}
        }
        
        sufficiency = drift_analyzer._calculate_evidence_sufficiency_pattern(evidence)
        
        assert isinstance(sufficiency, float)
        assert 0.0 <= sufficiency <= 3.0  # Based on our weighting scheme
    
    def test_determine_severity(self, drift_analyzer):
        """Test drift severity determination."""
        # Test high severity
        high_score = 0.8
        severity = drift_analyzer._determine_severity(high_score, "ks_test")
        assert severity == "high"
        
        # Test medium severity
        medium_score = 0.2
        severity = drift_analyzer._determine_severity(medium_score, "ks_test")
        assert severity == "medium"
        
        # Test low severity
        low_score = 0.05
        severity = drift_analyzer._determine_severity(low_score, "ks_test")
        assert severity == "low"
    
    def test_detect_distribution_drift_ks(self, drift_analyzer, sample_current_data, sample_reference_data):
        """Test Kolmogorov-Smirnov drift detection."""
        model_id = "test_model_ks"
        
        results = drift_analyzer._detect_distribution_drift_ks(
            sample_current_data, sample_reference_data, model_id
        )
        
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, DriftAnalysisResult)
            assert result.model_id == model_id
            assert result.statistical_method == "kolmogorov_smirnov"
            assert result.drift_type == "feature_distribution_drift"
            assert result.p_value is not None
            assert result.confidence_interval is not None
    
    def test_detect_psi_drift(self, drift_analyzer, sample_current_data, sample_reference_data):
        """Test PSI drift detection."""
        model_id = "test_model_psi"
        
        results = drift_analyzer._detect_psi_drift(
            sample_current_data, sample_reference_data, model_id
        )
        
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, DriftAnalysisResult)
            assert result.model_id == model_id
            assert result.statistical_method == "population_stability_index"
            assert result.drift_type == "population_stability_drift"
    
    def test_detect_js_divergence_drift(self, drift_analyzer, sample_current_data, sample_reference_data):
        """Test Jensen-Shannon divergence drift detection."""
        model_id = "test_model_js"
        
        results = drift_analyzer._detect_js_divergence_drift(
            sample_current_data, sample_reference_data, model_id
        )
        
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, DriftAnalysisResult)
            assert result.model_id == model_id
            assert result.statistical_method == "jensen_shannon_divergence"
            assert result.drift_type == "distribution_divergence_drift"
    
    def test_detect_concept_drift(self, drift_analyzer, sample_trace_data):
        """Test concept drift detection."""
        model_id = "test_model_concept"
        
        results = drift_analyzer._detect_concept_drift(sample_trace_data, model_id)
        
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, DriftAnalysisResult)
            assert result.model_id == model_id
            assert result.statistical_method == "performance_degradation"
            assert result.drift_type == "concept_drift"
    
    def test_detect_evidence_pattern_drift(self, drift_analyzer, sample_current_data, sample_reference_data):
        """Test evidence pattern drift detection."""
        model_id = "test_model_evidence"
        
        results = drift_analyzer._detect_evidence_pattern_drift(
            sample_current_data, sample_reference_data, model_id
        )
        
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, DriftAnalysisResult)
            assert result.model_id == model_id
            assert result.statistical_method == "evidence_sufficiency_comparison"
            assert result.drift_type == "evidence_pattern_drift"
    
    @patch('src.analytics.drift_detection.get_tracer')
    def test_detect_comprehensive_drift(self, mock_tracer, drift_analyzer, 
                                       sample_current_data, sample_reference_data, sample_trace_data):
        """Test comprehensive drift detection."""
        # Mock tracer
        mock_span = Mock()
        mock_tracer.return_value.trace_bayesian_inference.return_value.__enter__.return_value = mock_span
        mock_tracer.return_value.trace_bayesian_inference.return_value.__exit__.return_value = None
        
        model_id = "test_model_comprehensive"
        
        results = drift_analyzer.detect_comprehensive_drift(
            model_id=model_id,
            current_data=sample_current_data,
            reference_data=sample_reference_data,
            trace_data=sample_trace_data
        )
        
        assert isinstance(results, list)
        assert len(results) > 0  # Should detect some drift
        
        # Verify all results have required attributes
        for result in results:
            assert isinstance(result, DriftAnalysisResult)
            assert result.model_id == model_id
            assert result.timestamp is not None
            assert result.drift_score >= 0.0
            assert result.severity in ["low", "medium", "high"]
            assert isinstance(result.affected_features, list)
            assert isinstance(result.recommendation, str)
    
    def test_analyze_drift_root_causes(self, drift_analyzer, sample_current_data, sample_reference_data):
        """Test root cause analysis."""
        # Create sample drift results
        drift_results = [
            DriftAnalysisResult(
                model_id="test_model",
                timestamp=datetime.now(timezone.utc).isoformat(),
                drift_type="feature_distribution_drift",
                drift_score=0.5,
                severity="medium",
                statistical_method="kolmogorov_smirnov",
                p_value=0.01,
                confidence_interval=(0.3, 0.7),
                affected_features=["feature_1"],
                root_cause_analysis={},
                recommendation="Test recommendation"
            )
        ]
        
        root_cause = drift_analyzer.analyze_drift_root_causes(
            drift_results, sample_current_data, sample_reference_data
        )
        
        assert isinstance(root_cause, dict)
        assert "primary_cause" in root_cause
        assert "contributing_factors" in root_cause
        assert "confidence_score" in root_cause
        assert isinstance(root_cause["contributing_factors"], list)
        assert 0.0 <= root_cause["confidence_score"] <= 1.0
    
    def test_predict_future_drift_insufficient_data(self, drift_analyzer):
        """Test drift prediction with insufficient data."""
        model_id = "test_model_prediction"
        
        forecast = drift_analyzer.predict_future_drift(model_id, forecast_horizon_days=7)
        
        assert isinstance(forecast, DriftForecast)
        assert forecast.model_id == model_id
        assert forecast.forecast_horizon_days == 7
        assert forecast.predicted_drift_score == 0.0
        assert "more historical data" in forecast.recommended_actions[0]
    
    def test_predict_future_drift_with_data(self, drift_analyzer):
        """Test drift prediction with sufficient historical data."""
        model_id = "test_model_prediction_data"
        
        # Add historical drift data
        for i in range(15):
            drift_result = DriftAnalysisResult(
                model_id=model_id,
                timestamp=(datetime.now(timezone.utc) - timedelta(days=i)).isoformat(),
                drift_type="feature_distribution_drift",
                drift_score=0.3 + (i * 0.02),  # Increasing drift over time
                severity="medium",
                statistical_method="kolmogorov_smirnov",
                p_value=0.05,
                confidence_interval=(0.2, 0.6),
                affected_features=["feature_1"],
                root_cause_analysis={},
                recommendation="Test recommendation"
            )
            drift_analyzer.drift_history.append(drift_result)
        
        forecast = drift_analyzer.predict_future_drift(model_id, forecast_horizon_days=7)
        
        assert isinstance(forecast, DriftForecast)
        assert forecast.model_id == model_id
        assert forecast.forecast_horizon_days == 7
        assert forecast.predicted_drift_score > 0.0
        assert forecast.confidence_lower >= 0.0
        assert forecast.confidence_upper <= 1.0
        assert forecast.confidence_lower <= forecast.confidence_upper
        assert len(forecast.contributing_factors) > 0
        assert len(forecast.recommended_actions) > 0
    
    def test_generate_drift_visualization_data(self, drift_analyzer):
        """Test drift visualization data generation."""
        model_id = "test_model_viz"
        
        # Add some drift history
        for i in range(5):
            drift_result = DriftAnalysisResult(
                model_id=model_id,
                timestamp=(datetime.now(timezone.utc) - timedelta(days=i)).isoformat(),
                drift_type="feature_distribution_drift",
                drift_score=0.4 + (i * 0.1),
                severity="medium",
                statistical_method="kolmogorov_smirnov",
                p_value=0.05,
                confidence_interval=(0.2, 0.6),
                affected_features=[f"feature_{i}"],
                root_cause_analysis={},
                recommendation="Test recommendation"
            )
            drift_analyzer.drift_history.append(drift_result)
        
        viz_data = drift_analyzer.generate_drift_visualization_data(model_id, days=30)
        
        assert isinstance(viz_data, DriftVisualizationData)
        assert viz_data.model_id == model_id
        assert isinstance(viz_data.time_series_data, list)
        assert isinstance(viz_data.feature_importance, dict)
        assert isinstance(viz_data.distribution_comparisons, dict)
        assert isinstance(viz_data.trend_analysis, dict)
        assert isinstance(viz_data.alert_timeline, list)


class TestDriftMonitoringService:
    """Test suite for DriftMonitoringService."""
    
    @pytest.fixture
    def monitoring_service(self):
        """Create a drift monitoring service for testing."""
        config = {
            "monitoring_interval_seconds": 1,  # Short interval for testing
            "alert_thresholds": {
                "high_severity_drift": 0.7,
                "medium_severity_drift": 0.4,
                "drift_acceleration": 0.1
            }
        }
        return DriftMonitoringService(config)
    
    def test_initialization(self, monitoring_service):
        """Test monitoring service initialization."""
        assert monitoring_service is not None
        assert monitoring_service.monitoring_interval == 1
        assert not monitoring_service.is_monitoring
        assert len(monitoring_service.alert_callbacks) == 0
    
    def test_add_remove_alert_callback(self, monitoring_service):
        """Test adding and removing alert callbacks."""
        async def test_callback(alert_data):
            pass
        
        # Add callback
        monitoring_service.add_alert_callback(test_callback)
        assert len(monitoring_service.alert_callbacks) == 1
        assert test_callback in monitoring_service.alert_callbacks
        
        # Remove callback
        monitoring_service.remove_alert_callback(test_callback)
        assert len(monitoring_service.alert_callbacks) == 0
        assert test_callback not in monitoring_service.alert_callbacks
    
    @pytest.mark.asyncio
    async def test_collect_current_trace_data(self, monitoring_service):
        """Test trace data collection."""
        model_id = "test_model"
        
        trace_data = await monitoring_service._collect_current_trace_data(model_id)
        
        assert trace_data is not None
        assert isinstance(trace_data, dict)
        assert trace_data["model_id"] == model_id
        assert "timestamp" in trace_data
        assert "predictions" in trace_data
        assert "performance_metrics" in trace_data
        assert "evidence_patterns" in trace_data
        assert "trace_metadata" in trace_data
    
    @pytest.mark.asyncio
    async def test_get_recent_predictions(self, monitoring_service):
        """Test recent predictions retrieval."""
        model_id = "test_model"
        
        predictions = await monitoring_service._get_recent_predictions(model_id)
        
        assert isinstance(predictions, list)
        assert len(predictions) == 50  # As defined in the method
        assert all(isinstance(p, float) for p in predictions)
        assert all(0.0 <= p <= 1.0 for p in predictions)
    
    @pytest.mark.asyncio
    async def test_get_recent_performance_metrics(self, monitoring_service):
        """Test recent performance metrics retrieval."""
        model_id = "test_model"
        
        metrics = await monitoring_service._get_recent_performance_metrics(model_id)
        
        assert isinstance(metrics, list)
        assert len(metrics) == 20  # As defined in the method
        for metric in metrics:
            assert isinstance(metric, dict)
            assert "timestamp" in metric
            assert "accuracy" in metric
            assert "precision" in metric
            assert "recall" in metric
            assert "processing_time" in metric
    
    @pytest.mark.asyncio
    async def test_get_recent_evidence_patterns(self, monitoring_service):
        """Test recent evidence patterns retrieval."""
        model_id = "test_model"
        
        evidence = await monitoring_service._get_recent_evidence_patterns(model_id)
        
        assert isinstance(evidence, dict)
        assert "material_info" in evidence
        assert "trading_activity" in evidence
        assert "timing" in evidence
        assert "price_impact" in evidence
        assert "volume_anomaly" in evidence
        
        for key, value in evidence.items():
            assert isinstance(value, dict)
            assert "value" in value
            assert "confidence" in value
    
    @pytest.mark.asyncio
    async def test_reference_data_operations(self, monitoring_service):
        """Test reference data get/set operations."""
        model_id = "test_model"
        test_data = {"test_key": "test_value"}
        
        # Initially no reference data
        ref_data = await monitoring_service._get_reference_data(model_id)
        assert ref_data is None
        
        # Update reference data
        await monitoring_service._update_reference_data(model_id, test_data)
        
        # Retrieve reference data
        ref_data = await monitoring_service._get_reference_data(model_id)
        assert ref_data == test_data
    
    @pytest.mark.asyncio
    async def test_should_update_reference(self, monitoring_service):
        """Test reference data update logic."""
        model_id = "test_model"
        
        # First call should return False and set timestamp
        should_update = await monitoring_service._should_update_reference(model_id)
        assert should_update is False
        assert model_id in monitoring_service.last_analysis_time
        
        # Subsequent call within 7 days should return False
        should_update = await monitoring_service._should_update_reference(model_id)
        assert should_update is False
        
        # Simulate 8 days passing
        monitoring_service.last_analysis_time[model_id] = datetime.now(timezone.utc) - timedelta(days=8)
        should_update = await monitoring_service._should_update_reference(model_id)
        assert should_update is True
    
    @pytest.mark.asyncio
    async def test_manual_drift_analysis(self, monitoring_service):
        """Test manual drift analysis."""
        model_id = "test_model_manual"
        current_data = {
            "feature_1": [2.0, 2.5, 3.0, 3.5, 4.0],
            "predictions": [0.6, 0.7, 0.8, 0.9, 1.0]
        }
        reference_data = {
            "feature_1": [1.0, 1.5, 2.0, 2.5, 3.0],
            "predictions": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        with patch('src.analytics.drift_integration.get_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.return_value.trace_bayesian_inference.return_value.__enter__.return_value = mock_span
            mock_tracer.return_value.trace_bayesian_inference.return_value.__exit__.return_value = None
            
            result = await monitoring_service.perform_manual_drift_analysis(
                model_id, current_data, reference_data
            )
        
        assert isinstance(result, dict)
        assert result["model_id"] == model_id
        assert "analysis_timestamp" in result
        assert "drift_results" in result
        assert "drift_forecast" in result
        assert "visualization_data" in result
        assert "summary" in result
        
        summary = result["summary"]
        assert "total_detections" in summary
        assert "high_severity_count" in summary
        assert "medium_severity_count" in summary
        assert "max_drift_score" in summary
        assert "predicted_drift_score" in summary
        assert "high_drift_likelihood" in summary


class TestDriftAlertManager:
    """Test suite for DriftAlertManager."""
    
    @pytest.fixture
    def alert_manager(self):
        """Create an alert manager for testing."""
        return DriftAlertManager()
    
    def test_initialization(self, alert_manager):
        """Test alert manager initialization."""
        assert alert_manager is not None
        assert len(alert_manager.alert_history) == 0
        assert len(alert_manager.notification_handlers) == 4  # console, email, slack, webhook
    
    def test_determine_alert_priority(self, alert_manager):
        """Test alert priority determination."""
        # Test critical priority
        alert_data = {"alert_type": "high_severity_drift"}
        priority = alert_manager._determine_alert_priority(alert_data)
        assert priority == "critical"
        
        # Test high priority
        alert_data = {"alert_type": "predictive_drift_warning"}
        priority = alert_manager._determine_alert_priority(alert_data)
        assert priority == "high"
        
        # Test medium priority
        alert_data = {"alert_type": "medium_severity_drift"}
        priority = alert_manager._determine_alert_priority(alert_data)
        assert priority == "medium"
        
        # Test low priority (default)
        alert_data = {"alert_type": "unknown_type"}
        priority = alert_manager._determine_alert_priority(alert_data)
        assert priority == "low"
    
    @pytest.mark.asyncio
    async def test_handle_drift_alert(self, alert_manager):
        """Test drift alert handling."""
        alert_data = {
            "alert_type": "high_severity_drift",
            "model_id": "test_model",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "drift_count": 3,
            "max_drift_score": 0.8
        }
        
        await alert_manager.handle_drift_alert(alert_data)
        
        # Check that alert was stored
        assert len(alert_manager.alert_history) == 1
        stored_alert = alert_manager.alert_history[0]
        
        assert "alert_id" in stored_alert
        assert "processed_timestamp" in stored_alert
        assert "priority" in stored_alert
        assert stored_alert["priority"] == "critical"
        assert stored_alert["model_id"] == "test_model"
    
    @pytest.mark.asyncio
    async def test_console_notification_handler(self, alert_manager, caplog):
        """Test console notification handler."""
        alert_data = {
            "priority": "critical",
            "model_id": "test_model",
            "alert_type": "high_severity_drift"
        }
        
        await alert_manager._console_notification_handler(alert_data)
        
        # Check that appropriate log level was used
        assert any("CRITICAL" in record.levelname for record in caplog.records)
    
    def test_get_alert_statistics_empty(self, alert_manager):
        """Test alert statistics with no alerts."""
        stats = alert_manager.get_alert_statistics(days=30)
        
        assert stats["total_alerts"] == 0
        assert stats["alert_breakdown"] == {}
        assert stats["priority_breakdown"] == {}
        assert stats["model_breakdown"] == {}
    
    def test_get_alert_statistics_with_data(self, alert_manager):
        """Test alert statistics with alert data."""
        # Add some test alerts
        test_alerts = [
            {
                "alert_type": "high_severity_drift",
                "priority": "critical",
                "model_id": "model_1",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "alert_type": "medium_severity_drift",
                "priority": "medium",
                "model_id": "model_1",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "alert_type": "high_severity_drift",
                "priority": "critical",
                "model_id": "model_2",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        alert_manager.alert_history = test_alerts
        
        stats = alert_manager.get_alert_statistics(days=30)
        
        assert stats["total_alerts"] == 3
        assert stats["alert_breakdown"]["high_severity_drift"] == 2
        assert stats["alert_breakdown"]["medium_severity_drift"] == 1
        assert stats["priority_breakdown"]["critical"] == 2
        assert stats["priority_breakdown"]["medium"] == 1
        assert stats["model_breakdown"]["model_1"] == 2
        assert stats["model_breakdown"]["model_2"] == 1


class TestIntegration:
    """Integration tests for the complete drift detection system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_drift_detection(self):
        """Test end-to-end drift detection workflow."""
        # Setup monitoring service with alert manager
        monitoring_service = DriftMonitoringService({
            "monitoring_interval_seconds": 1
        })
        alert_manager = DriftAlertManager()
        
        # Connect alert manager to monitoring service
        monitoring_service.add_alert_callback(alert_manager.handle_drift_alert)
        
        # Perform manual drift analysis that should trigger alerts
        model_id = "integration_test_model"
        current_data = {
            "feature_1": [5.0, 6.0, 7.0, 8.0, 9.0],  # Significantly different from reference
            "predictions": [0.9, 0.95, 1.0, 1.0, 1.0]  # High predictions
        }
        reference_data = {
            "feature_1": [1.0, 1.5, 2.0, 2.5, 3.0],  # Lower values
            "predictions": [0.1, 0.2, 0.3, 0.4, 0.5]  # Lower predictions
        }
        
        with patch('src.analytics.drift_integration.get_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.return_value.trace_bayesian_inference.return_value.__enter__.return_value = mock_span
            mock_tracer.return_value.trace_bayesian_inference.return_value.__exit__.return_value = None
            
            # Perform analysis
            result = await monitoring_service.perform_manual_drift_analysis(
                model_id, current_data, reference_data
            )
        
        # Wait a moment for async alert processing
        await asyncio.sleep(0.1)
        
        # Verify analysis results
        assert result["model_id"] == model_id
        assert result["summary"]["total_detections"] > 0
        
        # Verify alerts were generated and processed
        # Note: In a real scenario, alerts would be triggered if drift scores exceed thresholds
        # This test validates the integration works without errors
        
        # Clean up
        monitoring_service.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_continuous_monitoring_workflow(self):
        """Test continuous monitoring workflow."""
        monitoring_service = DriftMonitoringService({
            "monitoring_interval_seconds": 0.1  # Very short for testing
        })
        
        alert_received = asyncio.Event()
        received_alerts = []
        
        async def test_alert_callback(alert_data):
            received_alerts.append(alert_data)
            alert_received.set()
        
        monitoring_service.add_alert_callback(test_alert_callback)
        
        with patch('src.analytics.drift_integration.get_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.return_value.trace_bayesian_inference.return_value.__enter__.return_value = mock_span
            mock_tracer.return_value.trace_bayesian_inference.return_value.__exit__.return_value = None
            
            # Start monitoring in background
            monitoring_task = asyncio.create_task(
                monitoring_service.start_continuous_monitoring(["test_model"])
            )
            
            # Let it run for a short time
            await asyncio.sleep(0.5)
            
            # Stop monitoring
            monitoring_service.stop_monitoring()
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(monitoring_task, timeout=1.0)
            except asyncio.TimeoutError:
                monitoring_task.cancel()
        
        # Verify monitoring ran without errors
        assert not monitoring_service.is_monitoring
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks for drift detection."""
        import time
        
        # Create analyzer with realistic data sizes
        analyzer = AdvancedDriftAnalyzer()
        
        # Generate larger datasets for performance testing
        current_data = {
            f"feature_{i}": np.random.normal(2.0, 1.0, 1000).tolist()
            for i in range(10)
        }
        reference_data = {
            f"feature_{i}": np.random.normal(1.0, 1.0, 1000).tolist()
            for i in range(10)
        }
        
        # Measure performance
        start_time = time.time()
        
        with patch('src.analytics.drift_detection.get_tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.return_value.trace_bayesian_inference.return_value.__enter__.return_value = mock_span
            mock_tracer.return_value.trace_bayesian_inference.return_value.__exit__.return_value = None
            
            results = analyzer.detect_comprehensive_drift(
                model_id="performance_test",
                current_data=current_data,
                reference_data=reference_data
            )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance assertions
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert len(results) > 0  # Should detect some drift with this data
        
        print(f"Drift detection completed in {processing_time:.3f} seconds for 10 features with 1000 samples each")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])