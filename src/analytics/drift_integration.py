"""
Drift Detection Integration with OpenInference Tracing

This module integrates the advanced drift detection capabilities with:
- OpenInference tracing infrastructure
- Enhanced Bayesian Engine monitoring
- Real-time drift alerting system
- Automated drift response mechanisms
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Callable
from dataclasses import asdict

from .drift_detection import AdvancedDriftAnalyzer, DriftAnalysisResult, DriftForecast
from ..utils.openinference_tracer import get_tracer
from ..models.explainability.governance_tracker import ModelGovernanceTracker

logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_MONITORING_INTERVAL_SECONDS = 300  # 5 minutes
DEFAULT_ALERT_THRESHOLDS = {
    "high_severity_drift": 0.7,    # 70% confidence threshold
    "medium_severity_drift": 0.4,  # 40% confidence threshold  
    "drift_acceleration": 0.1       # 10% change rate threshold
}
DEFAULT_MAX_REFERENCE_CACHE_SIZE = 1000  # Maximum reference data entries
DEFAULT_MAX_ALERT_HISTORY_SIZE = 1000    # Maximum alert history entries


class DriftMonitoringService:
    """
    Service for continuous drift monitoring with OpenInference integration.
    
    This service provides:
    - Real-time drift detection from trace data
    - Automated alerting for drift events
    - Integration with model governance workflows
    - Predictive drift forecasting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the drift monitoring service.
        
        Args:
            config: Configuration dictionary for drift monitoring
        """
        self.config = config or {}
        self.tracer = get_tracer()
        self.drift_analyzer = AdvancedDriftAnalyzer(self.config.get("drift_analyzer", {}))
        self.governance_tracker = ModelGovernanceTracker(self.config.get("governance", {}))
        
        # Monitoring configuration
        self.monitoring_interval = self.config.get("monitoring_interval_seconds", DEFAULT_MONITORING_INTERVAL_SECONDS)
        self.alert_thresholds = self.config.get("alert_thresholds", DEFAULT_ALERT_THRESHOLDS)
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Monitoring state
        self.is_monitoring = False
        self.last_analysis_time = {}
        
        # Initialize bounded reference data cache
        max_cache_size = self.config.get("max_reference_cache_size", DEFAULT_MAX_REFERENCE_CACHE_SIZE)
        self.reference_data_cache = {}
        self._cache_access_order = []  # Track access order for LRU
        self.max_cache_size = max_cache_size
        
        logger.info("Drift monitoring service initialized")
    
    async def start_continuous_monitoring(self, model_ids: List[str]):
        """
        Start continuous drift monitoring for specified models.
        
        Args:
            model_ids: List of model IDs to monitor
        """
        self.is_monitoring = True
        logger.info(f"Starting continuous drift monitoring for models: {model_ids}")
        
        while self.is_monitoring:
            try:
                # Process multiple models concurrently for better performance
                await asyncio.gather(*[
                    self._monitor_model_drift(model_id) 
                    for model_id in model_ids
                ])
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in drift monitoring cycle: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    def stop_monitoring(self):
        """Stop continuous drift monitoring."""
        self.is_monitoring = False
        logger.info("Drift monitoring stopped")
    
    async def _monitor_model_drift(self, model_id: str):
        """Core drift monitoring logic for a single model iteration.
        
        Performs one complete cycle of drift detection including:
        - Collecting current model performance data from traces
        - Comparing against baseline reference data using statistical methods
        - Analyzing root causes for any detected drift patterns
        - Triggering alerts for significant drift events
        - Updating reference data when appropriate for future comparisons
        
        This method is called for each model in the monitoring cycle and
        integrates with OpenInference tracing for comprehensive observability.
        """
        try:
            with self.tracer.trace_bayesian_inference(
                model_name="drift_monitoring",
                model_version="1.0.0",
                input_data={"model_id": model_id}
            ) as span:
                if span:
                    span.set_attribute("monitoring.model_id", model_id)
                    span.set_attribute("monitoring.type", "continuous")
                
                # Get current trace data for the model
                current_data = await self._collect_current_trace_data(model_id)
                
                if not current_data:
                    logger.debug(f"No current data available for model {model_id}")
                    return
                
                # Get reference data
                reference_data = await self._get_reference_data(model_id)
                
                if not reference_data:
                    # Store current data as reference for future comparisons
                    await self._update_reference_data(model_id, current_data)
                    logger.debug(f"Stored reference data for model {model_id}")
                    return
                
                # Perform comprehensive drift analysis
                drift_results = self.drift_analyzer.detect_comprehensive_drift(
                    model_id=model_id,
                    current_data=current_data,
                    reference_data=reference_data,
                    trace_data=current_data.get("trace_metadata", {})
                )
                
                if span:
                    span.set_attribute("monitoring.drift_detections", len(drift_results))
                
                # Process drift results
                await self._process_drift_results(model_id, drift_results)
                
                # Update reference data periodically
                if await self._should_update_reference(model_id):
                    await self._update_reference_data(model_id, current_data)
                
                # Enhanced debug logging with drift metrics
                max_drift_score = max(d.drift_score for d in drift_results) if drift_results else 0
                affected_features = list(set(f for d in drift_results for f in d.affected_features))
                logger.debug(
                    f"Drift monitoring completed for {model_id}: "
                    f"detections={len(drift_results)}, "
                    f"max_drift_score={max_drift_score:.3f}, "
                    f"affected_features={affected_features[:5]}{'...' if len(affected_features) > 5 else ''}"
                )
                
        except Exception as e:
            logger.error(
                f"Error monitoring drift for model {model_id}",
                exc_info=True,
                extra={
                    "model_id": model_id,
                    "monitoring_state": self.is_monitoring,
                    "last_analysis": self.last_analysis_time.get(model_id),
                    "cache_size": len(self.reference_data_cache)
                }
            )
    
    async def _collect_current_trace_data(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Collect current trace data for drift analysis."""
        try:
            # In a real implementation, this would collect data from:
            # - OpenInference trace spans
            # - Model prediction logs
            # - Performance metrics
            # - Evidence patterns from Bayesian models
            
            # For now, we'll simulate collecting trace data
            current_time = datetime.now(timezone.utc)
            
            # Simulate trace data collection
            trace_data = {
                "timestamp": current_time.isoformat(),
                "model_id": model_id,
                "predictions": await self._get_recent_predictions(model_id),
                "performance_metrics": await self._get_recent_performance_metrics(model_id),
                "evidence_patterns": await self._get_recent_evidence_patterns(model_id),
                "trace_metadata": {
                    "span_count": 100,  # Simulated
                    "processing_time_avg": 0.25,  # Simulated
                    "error_rate": 0.02  # Simulated
                }
            }
            
            return trace_data
            
        except Exception as e:
            logger.error(f"Error collecting trace data for {model_id}: {e}")
            return None
    
    async def _get_recent_predictions(self, model_id: str) -> List[float]:
        """Get recent model predictions for drift analysis."""
        # In production, this would query the trace data store
        # For demo, return simulated predictions
        import random
        return [random.uniform(0.0, 1.0) for _ in range(50)]
    
    async def _get_recent_performance_metrics(self, model_id: str) -> List[Dict[str, Any]]:
        """Get recent performance metrics from traces."""
        # In production, this would extract from OpenInference traces
        # For demo, return simulated metrics
        import random
        return [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=i)).isoformat(),
                "accuracy": random.uniform(0.7, 0.95),
                "precision": random.uniform(0.6, 0.9),
                "recall": random.uniform(0.65, 0.85),
                "processing_time": random.uniform(0.1, 0.5)
            }
            for i in range(20)
        ]
    
    async def _get_recent_evidence_patterns(self, model_id: str) -> Dict[str, Any]:
        """Get recent evidence patterns for Bayesian models."""
        # In production, this would extract evidence data from traces
        # For demo, return simulated evidence patterns
        import random
        return {
            "material_info": {"value": random.randint(0, 2), "confidence": "High"},
            "trading_activity": {"value": random.randint(0, 2), "confidence": "Medium"},
            "timing": {"value": random.randint(0, 2), "confidence": "High"},
            "price_impact": {"value": random.randint(0, 2), "confidence": "Low"},
            "volume_anomaly": {"value": random.randint(0, 2), "confidence": "Medium"}
        }
    
    async def _get_reference_data(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get reference data for drift comparison."""
        return self.reference_data_cache.get(model_id)
    
    async def _update_reference_data(self, model_id: str, current_data: Dict[str, Any]):
        """Update reference data for future drift comparisons with LRU cache management."""
        # Implement LRU cache with size limits
        if model_id in self.reference_data_cache:
            # Move to end (most recently used)
            self._cache_access_order.remove(model_id)
        elif len(self.reference_data_cache) >= self.max_cache_size:
            # Remove least recently used item
            oldest_model = self._cache_access_order.pop(0)
            del self.reference_data_cache[oldest_model]
            logger.debug(f"Evicted reference data for model {oldest_model} from cache")
        
        self.reference_data_cache[model_id] = current_data.copy()
        self._cache_access_order.append(model_id)
        logger.debug(f"Updated reference data for model {model_id} (cache size: {len(self.reference_data_cache)})")
    
    async def _should_update_reference(self, model_id: str) -> bool:
        """Determine if reference data should be updated."""
        last_update = self.last_analysis_time.get(model_id)
        if not last_update:
            self.last_analysis_time[model_id] = datetime.now(timezone.utc)
            return False
        
        # Update reference data weekly
        time_since_update = datetime.now(timezone.utc) - last_update
        should_update = time_since_update > timedelta(days=7)
        
        if should_update:
            self.last_analysis_time[model_id] = datetime.now(timezone.utc)
        
        return should_update
    
    async def _process_drift_results(self, model_id: str, drift_results: List[DriftAnalysisResult]):
        """Process drift detection results and trigger appropriate actions."""
        if not drift_results:
            return
        
        # Categorize drift results by severity
        high_severity = [d for d in drift_results if d.severity == "high"]
        medium_severity = [d for d in drift_results if d.severity == "medium"]
        
        # Trigger alerts for significant drift
        if high_severity:
            await self._trigger_high_severity_alert(model_id, high_severity)
        
        if medium_severity:
            await self._trigger_medium_severity_alert(model_id, medium_severity)
        
        # Update governance tracker
        await self._update_governance_tracker(model_id, drift_results)
        
        # Generate drift forecast
        if len(drift_results) > 0:
            forecast = self.drift_analyzer.predict_future_drift(model_id, forecast_horizon_days=7)
            await self._process_drift_forecast(model_id, forecast)
    
    async def _trigger_high_severity_alert(self, model_id: str, drift_results: List[DriftAnalysisResult]):
        """Trigger high severity drift alert."""
        alert_data = {
            "alert_type": "high_severity_drift",
            "model_id": model_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "drift_count": len(drift_results),
            "max_drift_score": max(d.drift_score for d in drift_results),
            "affected_features": list(set(f for d in drift_results for f in d.affected_features)),
            "recommendations": [d.recommendation for d in drift_results]
        }
        
        logger.warning(f"HIGH SEVERITY DRIFT DETECTED for model {model_id}: {alert_data}")
        
        # Notify alert callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    async def _trigger_medium_severity_alert(self, model_id: str, drift_results: List[DriftAnalysisResult]):
        """Trigger medium severity drift alert."""
        alert_data = {
            "alert_type": "medium_severity_drift",
            "model_id": model_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "drift_count": len(drift_results),
            "max_drift_score": max(d.drift_score for d in drift_results),
            "affected_features": list(set(f for d in drift_results for f in d.affected_features))
        }
        
        logger.info(f"Medium severity drift detected for model {model_id}: {alert_data}")
        
        # Notify alert callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    async def _update_governance_tracker(self, model_id: str, drift_results: List[DriftAnalysisResult]):
        """Update the model governance tracker with drift results."""
        try:
            # Convert drift results to governance tracker format
            drift_metadata = {
                "drift_detections": len(drift_results),
                "high_severity_count": len([d for d in drift_results if d.severity == "high"]),
                "max_drift_score": max(d.drift_score for d in drift_results) if drift_results else 0.0,
                "drift_types": list(set(d.drift_type for d in drift_results))
            }
            
            # Track lifecycle event
            self.governance_tracker.track_model_lifecycle(
                model_id=model_id,
                event="drift_detection",
                metadata={
                    "current_data": {"drift_analysis": drift_metadata},
                    "reference_data": {"baseline": "reference_data_summary"}
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating governance tracker: {e}")
    
    async def _process_drift_forecast(self, model_id: str, forecast: DriftForecast):
        """Process drift forecast and trigger proactive actions."""
        if forecast.likelihood_high_drift > 0.7:
            logger.warning(
                f"High drift likelihood predicted for model {model_id}: "
                f"{forecast.likelihood_high_drift:.2%} in {forecast.forecast_horizon_days} days"
            )
            
            # Trigger proactive alert
            proactive_alert = {
                "alert_type": "predictive_drift_warning",
                "model_id": model_id,
                "timestamp": forecast.forecast_timestamp,
                "predicted_score": forecast.predicted_drift_score,
                "likelihood": forecast.likelihood_high_drift,
                "horizon_days": forecast.forecast_horizon_days,
                "recommended_actions": forecast.recommended_actions
            }
            
            for callback in self.alert_callbacks:
                try:
                    await callback(proactive_alert)
                except Exception as e:
                    logger.error(f"Error in proactive alert callback: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Add a callback function for drift alerts."""
        self.alert_callbacks.append(callback)
        logger.info("Alert callback added to drift monitoring service")
    
    def remove_alert_callback(self, callback: Callable):
        """Remove a callback function from drift alerts."""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
            logger.info("Alert callback removed from drift monitoring service")
    
    async def get_drift_dashboard_data(self, model_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive drift data for dashboard visualization."""
        try:
            # Get visualization data from drift analyzer
            viz_data = self.drift_analyzer.generate_drift_visualization_data(model_id, days)
            
            # Get recent forecast
            forecast = self.drift_analyzer.predict_future_drift(model_id, forecast_horizon_days=7)
            
            # Get governance status
            governance_status = self.governance_tracker.get_governance_status(model_id)
            
            return {
                "model_id": model_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "visualization_data": asdict(viz_data),
                "drift_forecast": asdict(forecast),
                "governance_status": governance_status,
                "monitoring_status": {
                    "is_active": self.is_monitoring,
                    "last_analysis": self.last_analysis_time.get(model_id),
                    "monitoring_interval": self.monitoring_interval,
                    "alert_thresholds": self.alert_thresholds
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return {
                "model_id": model_id,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def perform_manual_drift_analysis(
        self, 
        model_id: str,
        current_data: Dict[str, Any],
        reference_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform manual drift analysis on provided data."""
        try:
            with self.tracer.trace_bayesian_inference(
                model_name="manual_drift_analysis",
                model_version="1.0.0",
                input_data={"model_id": model_id}
            ) as span:
                if span:
                    span.set_attribute("analysis.model_id", model_id)
                    span.set_attribute("analysis.type", "manual")
                
                # Perform comprehensive drift analysis
                drift_results = self.drift_analyzer.detect_comprehensive_drift(
                    model_id=model_id,
                    current_data=current_data,
                    reference_data=reference_data,
                    trace_data=current_data.get("trace_metadata", {})
                )
                
                # Generate forecast
                forecast = self.drift_analyzer.predict_future_drift(model_id)
                
                # Get visualization data
                viz_data = self.drift_analyzer.generate_drift_visualization_data(model_id)
                
                if span:
                    span.set_attribute("analysis.drift_detections", len(drift_results))
                    span.set_attribute("analysis.forecast_score", forecast.predicted_drift_score)
                
                return {
                    "model_id": model_id,
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                    "drift_results": [asdict(d) for d in drift_results],
                    "drift_forecast": asdict(forecast),
                    "visualization_data": asdict(viz_data),
                    "summary": {
                        "total_detections": len(drift_results),
                        "high_severity_count": len([d for d in drift_results if d.severity == "high"]),
                        "medium_severity_count": len([d for d in drift_results if d.severity == "medium"]),
                        "max_drift_score": max(d.drift_score for d in drift_results) if drift_results else 0.0,
                        "predicted_drift_score": forecast.predicted_drift_score,
                        "high_drift_likelihood": forecast.likelihood_high_drift
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in manual drift analysis: {e}")
            return {
                "model_id": model_id,
                "error": str(e),
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }


class DriftAlertManager:
    """
    Manager for drift alert handling and routing.
    
    This class provides:
    - Alert prioritization and routing
    - Integration with external notification systems
    - Alert history and analytics
    - Automated response coordination
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the drift alert manager."""
        self.config = config or {}
        self.max_alert_history_size = self.config.get('max_alert_history', DEFAULT_MAX_ALERT_HISTORY_SIZE)
        self.alert_history = []
        self.notification_handlers = {}
        
        # Default notification handlers
        self._setup_default_handlers()
        
        logger.info("Drift alert manager initialized")
    
    def _setup_default_handlers(self):
        """Setup default notification handlers."""
        self.notification_handlers = {
            "console": self._console_notification_handler,
            "email": self._email_notification_handler,
            "slack": self._slack_notification_handler,
            "webhook": self._webhook_notification_handler
        }
    
    async def handle_drift_alert(self, alert_data: Dict[str, Any]):
        """Handle incoming drift alert."""
        try:
            # Store alert in history with size limits
            alert_data["alert_id"] = f"drift_alert_{len(self.alert_history) + 1}"
            alert_data["processed_timestamp"] = datetime.now(timezone.utc).isoformat()
            
            # Maintain size-limited history
            if len(self.alert_history) >= self.max_alert_history_size:
                self.alert_history.pop(0)  # Remove oldest alert
                
            self.alert_history.append(alert_data)
            
            # Determine alert priority
            priority = self._determine_alert_priority(alert_data)
            alert_data["priority"] = priority
            
            # Route alert to appropriate handlers
            await self._route_alert(alert_data)
            
            logger.info(f"Processed drift alert {alert_data['alert_id']} with priority {priority}")
            
        except Exception as e:
            logger.error(f"Error handling drift alert: {e}")
    
    def _determine_alert_priority(self, alert_data: Dict[str, Any]) -> str:
        """Determine alert priority based on alert data."""
        alert_type = alert_data.get("alert_type", "")
        
        if alert_type == "high_severity_drift":
            return "critical"
        elif alert_type == "predictive_drift_warning":
            return "high"
        elif alert_type == "medium_severity_drift":
            return "medium"
        else:
            return "low"
    
    async def _route_alert(self, alert_data: Dict[str, Any]):
        """Routes alerts to notification handlers based on priority level.
        
        Critical alerts go to all available handlers (console, email, slack, webhook)
        to ensure immediate attention, while lower priority alerts use a subset of 
        handlers to avoid notification fatigue and reduce operational overhead.
        
        Priority-based routing logic:
        - Critical: All handlers (console, email, slack, webhook)
        - High: Console, email, slack  
        - Medium: Console, email
        - Low: Console only
        """
        priority = alert_data.get("priority", "low")
        
        # Determine which handlers to use based on priority
        handlers_to_use = []
        
        if priority == "critical":
            handlers_to_use = ["console", "email", "slack", "webhook"]
        elif priority == "high":
            handlers_to_use = ["console", "email", "slack"]
        elif priority == "medium":
            handlers_to_use = ["console", "slack"]
        else:
            handlers_to_use = ["console"]
        
        # Send notifications
        for handler_name in handlers_to_use:
            handler = self.notification_handlers.get(handler_name)
            if handler:
                try:
                    await handler(alert_data)
                except Exception as e:
                    logger.error(f"Error in {handler_name} notification handler: {e}")
    
    async def _console_notification_handler(self, alert_data: Dict[str, Any]):
        """Handle console notifications."""
        priority = alert_data.get("priority", "low")
        model_id = alert_data.get("model_id", "unknown")
        alert_type = alert_data.get("alert_type", "unknown")
        
        message = f"[{priority.upper()}] Drift Alert - Model: {model_id}, Type: {alert_type}"
        
        if priority == "critical":
            logger.critical(message)
        elif priority == "high":
            logger.warning(message)
        else:
            logger.info(message)
    
    async def _email_notification_handler(self, alert_data: Dict[str, Any]):
        """Handle email notifications."""
        # In production, this would send actual emails
        logger.info(f"EMAIL NOTIFICATION: {alert_data.get('alert_type')} for model {alert_data.get('model_id')}")
    
    async def _slack_notification_handler(self, alert_data: Dict[str, Any]):
        """Handle Slack notifications."""
        # In production, this would send to Slack
        logger.info(f"SLACK NOTIFICATION: {alert_data.get('alert_type')} for model {alert_data.get('model_id')}")
    
    async def _webhook_notification_handler(self, alert_data: Dict[str, Any]):
        """Handle webhook notifications."""
        # In production, this would call external webhooks
        logger.info(f"WEBHOOK NOTIFICATION: {alert_data.get('alert_type')} for model {alert_data.get('model_id')}")
    
    def get_alert_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get alert statistics for the specified time period."""
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.get("timestamp", "") >= cutoff_date
        ]
        
        if not recent_alerts:
            return {
                "total_alerts": 0,
                "alert_breakdown": {},
                "priority_breakdown": {},
                "model_breakdown": {}
            }
        
        # Calculate statistics
        alert_breakdown = {}
        priority_breakdown = {}
        model_breakdown = {}
        
        for alert in recent_alerts:
            alert_type = alert.get("alert_type", "unknown")
            priority = alert.get("priority", "unknown")
            model_id = alert.get("model_id", "unknown")
            
            alert_breakdown[alert_type] = alert_breakdown.get(alert_type, 0) + 1
            priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
            model_breakdown[model_id] = model_breakdown.get(model_id, 0) + 1
        
        return {
            "total_alerts": len(recent_alerts),
            "alert_breakdown": alert_breakdown,
            "priority_breakdown": priority_breakdown,
            "model_breakdown": model_breakdown,
            "time_period_days": days
        }