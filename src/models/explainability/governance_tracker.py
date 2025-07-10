"""
Model Governance Tracker

This module provides comprehensive model governance capabilities including
performance monitoring, drift detection, and approval workflows.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data."""
    metric_name: str
    value: float
    timestamp: str
    model_id: str
    baseline_value: Optional[float] = None
    threshold: Optional[float] = None
    status: str = 'normal'  # 'normal', 'warning', 'critical'


@dataclass
class DriftDetectionResult:
    """Drift detection result."""
    drift_type: str  # 'feature_drift', 'prediction_drift', 'concept_drift'
    drift_score: float
    timestamp: str
    model_id: str
    affected_features: List[str]
    severity: str  # 'low', 'medium', 'high'
    recommendation: str


@dataclass
class ModelApprovalEvent:
    """Model approval event."""
    event_id: str
    model_id: str
    event_type: str  # 'submitted', 'approved', 'rejected', 'retired'
    timestamp: str
    approver_id: Optional[str] = None
    comments: Optional[str] = None
    approval_criteria: Optional[Dict[str, Any]] = None


class ModelGovernanceTracker:
    """
    Comprehensive model governance tracker.
    
    This class provides governance capabilities including:
    - Model performance monitoring
    - Drift detection and alerting
    - Model approval workflows
    - Lifecycle management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the governance tracker.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.performance_monitor = ModelPerformanceMonitor(self.config.get('performance', {}))
        self.drift_detector = ModelDriftDetector(self.config.get('drift_detection', {}))
        self.approval_workflow = ModelApprovalWorkflow(self.config.get('approval', {}))
        
        # Governance data storage
        self.performance_history = []
        self.drift_history = []
        self.approval_history = []
        
        logger.info("Model governance tracker initialized")
    
    def track_model_lifecycle(
        self, 
        model_id: str, 
        event: str, 
        metadata: Dict[str, Any]
    ) -> None:
        """
        Track model lifecycle events.
        
        Args:
            model_id: Model identifier
            event: Lifecycle event
            metadata: Event metadata
        """
        try:
            timestamp = datetime.utcnow().isoformat()
            
            # Log lifecycle event
            lifecycle_event = {
                'model_id': model_id,
                'event': event,
                'timestamp': timestamp,
                'metadata': metadata
            }
            
            logger.info(f"Model lifecycle event tracked: {model_id} - {event}")
            
            # Trigger specific actions based on event type
            if event == 'performance_evaluation':
                self._handle_performance_evaluation(model_id, metadata)
            elif event == 'drift_detection':
                self._handle_drift_detection(model_id, metadata)
            elif event == 'approval_request':
                self._handle_approval_request(model_id, metadata)
            
        except Exception as e:
            logger.error(f"Error tracking model lifecycle event: {str(e)}")
            raise
    
    def monitor_model_performance(
        self, 
        model_id: str, 
        performance_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Monitor model performance.
        
        Args:
            model_id: Model identifier
            performance_data: Performance metrics
            
        Returns:
            Performance monitoring results
        """
        return self.performance_monitor.evaluate_performance(model_id, performance_data)
    
    def detect_model_drift(
        self, 
        model_id: str, 
        current_data: Dict[str, Any], 
        reference_data: Dict[str, Any]
    ) -> List[DriftDetectionResult]:
        """
        Detect model drift.
        
        Args:
            model_id: Model identifier
            current_data: Current data sample
            reference_data: Reference data sample
            
        Returns:
            List of drift detection results
        """
        return self.drift_detector.detect_drift(model_id, current_data, reference_data)
    
    def submit_for_approval(
        self, 
        model_id: str, 
        approval_type: str, 
        criteria: Dict[str, Any]
    ) -> str:
        """
        Submit model for approval.
        
        Args:
            model_id: Model identifier
            approval_type: Type of approval
            criteria: Approval criteria
            
        Returns:
            Approval request ID
        """
        return self.approval_workflow.submit_approval_request(model_id, approval_type, criteria)
    
    def get_governance_status(self, model_id: str) -> Dict[str, Any]:
        """
        Get comprehensive governance status.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Governance status report
        """
        try:
            # Get recent performance metrics
            recent_performance = self.performance_monitor.get_recent_performance(model_id)
            
            # Get drift status
            drift_status = self.drift_detector.get_drift_status(model_id)
            
            # Get approval status
            approval_status = self.approval_workflow.get_approval_status(model_id)
            
            # Calculate overall governance score
            governance_score = self._calculate_governance_score(
                recent_performance, drift_status, approval_status
            )
            
            return {
                'model_id': model_id,
                'timestamp': datetime.utcnow().isoformat(),
                'governance_score': governance_score,
                'performance_status': recent_performance,
                'drift_status': drift_status,
                'approval_status': approval_status,
                'recommendations': self._generate_governance_recommendations(
                    recent_performance, drift_status, approval_status
                ),
                'compliance_status': {
                    'monitoring_active': True,
                    'drift_detection_enabled': True,
                    'approval_workflow_active': True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting governance status: {str(e)}")
            return {
                'model_id': model_id,
                'timestamp': datetime.utcnow().isoformat(),
                'governance_score': 0.0,
                'error': str(e)
            }
    
    def _handle_performance_evaluation(self, model_id: str, metadata: Dict[str, Any]):
        """Handle performance evaluation event."""
        performance_data = metadata.get('performance_data', {})
        if performance_data:
            self.monitor_model_performance(model_id, performance_data)
    
    def _handle_drift_detection(self, model_id: str, metadata: Dict[str, Any]):
        """Handle drift detection event."""
        current_data = metadata.get('current_data', {})
        reference_data = metadata.get('reference_data', {})
        
        if current_data and reference_data:
            drift_results = self.detect_model_drift(model_id, current_data, reference_data)
            
            # Check for high severity drifts
            high_severity_drifts = [d for d in drift_results if d.severity == 'high']
            if high_severity_drifts:
                logger.warning(f"High severity drift detected for model {model_id}")
    
    def _handle_approval_request(self, model_id: str, metadata: Dict[str, Any]):
        """Handle approval request event."""
        approval_type = metadata.get('approval_type', 'standard')
        criteria = metadata.get('criteria', {})
        
        self.submit_for_approval(model_id, approval_type, criteria)
    
    def _calculate_governance_score(
        self, 
        performance_status: Dict[str, Any], 
        drift_status: Dict[str, Any], 
        approval_status: Dict[str, Any]
    ) -> float:
        """Calculate overall governance score."""
        
        # Performance component (40%)
        performance_score = performance_status.get('overall_score', 0.5)
        
        # Drift component (30%)
        drift_score = 1.0 - drift_status.get('max_drift_score', 0.0)
        
        # Approval component (30%)
        approval_score = 1.0 if approval_status.get('is_approved', False) else 0.5
        
        governance_score = (
            performance_score * 0.4 +
            drift_score * 0.3 +
            approval_score * 0.3
        )
        
        return governance_score
    
    def _generate_governance_recommendations(
        self, 
        performance_status: Dict[str, Any], 
        drift_status: Dict[str, Any], 
        approval_status: Dict[str, Any]
    ) -> List[str]:
        """Generate governance recommendations."""
        
        recommendations = []
        
        # Performance recommendations
        if performance_status.get('overall_score', 1.0) < 0.7:
            recommendations.append("Consider model retraining due to performance degradation")
        
        # Drift recommendations
        if drift_status.get('max_drift_score', 0.0) > 0.5:
            recommendations.append("Investigate data drift and consider model updates")
        
        # Approval recommendations
        if not approval_status.get('is_approved', False):
            recommendations.append("Submit model for approval before production deployment")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("Model governance status is satisfactory")
        
        return recommendations


class ModelPerformanceMonitor:
    """Model performance monitor."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.performance_history = []
        self.thresholds = self._load_performance_thresholds()
    
    def evaluate_performance(
        self, 
        model_id: str, 
        performance_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """Evaluate model performance."""
        
        timestamp = datetime.utcnow().isoformat()
        performance_metrics = []
        
        for metric_name, value in performance_data.items():
            threshold = self.thresholds.get(metric_name, 0.5)
            baseline = self._get_baseline_value(model_id, metric_name)
            
            # Determine status
            if value >= threshold:
                status = 'normal'
            elif value >= threshold * 0.8:
                status = 'warning'
            else:
                status = 'critical'
            
            metric = PerformanceMetric(
                metric_name=metric_name,
                value=value,
                timestamp=timestamp,
                model_id=model_id,
                baseline_value=baseline,
                threshold=threshold,
                status=status
            )
            
            performance_metrics.append(metric)
            self.performance_history.append(metric)
        
        # Calculate overall performance score
        overall_score = sum(m.value for m in performance_metrics) / len(performance_metrics) if performance_metrics else 0.0
        
        return {
            'model_id': model_id,
            'timestamp': timestamp,
            'overall_score': overall_score,
            'metrics': [asdict(m) for m in performance_metrics],
            'status': self._determine_overall_status(performance_metrics)
        }
    
    def get_recent_performance(self, model_id: str, days: int = 7) -> Dict[str, Any]:
        """Get recent performance for a model."""
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        recent_metrics = [
            m for m in self.performance_history 
            if m.model_id == model_id and m.timestamp >= cutoff_date
        ]
        
        if not recent_metrics:
            return {
                'model_id': model_id,
                'overall_score': 0.5,
                'metrics': [],
                'status': 'unknown'
            }
        
        overall_score = sum(m.value for m in recent_metrics) / len(recent_metrics)
        
        return {
            'model_id': model_id,
            'overall_score': overall_score,
            'metrics': [asdict(m) for m in recent_metrics],
            'status': self._determine_overall_status(recent_metrics)
        }
    
    def _load_performance_thresholds(self) -> Dict[str, float]:
        """Load performance thresholds."""
        return {
            'accuracy': 0.8,
            'precision': 0.7,
            'recall': 0.7,
            'f1_score': 0.75,
            'auc_roc': 0.8,
            'overall_score': 0.7
        }
    
    def _get_baseline_value(self, model_id: str, metric_name: str) -> Optional[float]:
        """Get baseline value for a metric."""
        
        # Get historical values for this metric
        historical_values = [
            m.value for m in self.performance_history 
            if m.model_id == model_id and m.metric_name == metric_name
        ]
        
        if not historical_values:
            return None
        
        # Return median as baseline
        sorted_values = sorted(historical_values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2-1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
    
    def _determine_overall_status(self, metrics: List[PerformanceMetric]) -> str:
        """Determine overall status from metrics."""
        
        if not metrics:
            return 'unknown'
        
        statuses = [m.status for m in metrics]
        
        if 'critical' in statuses:
            return 'critical'
        elif 'warning' in statuses:
            return 'warning'
        else:
            return 'normal'


class ModelDriftDetector:
    """Model drift detector."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.drift_history = []
        self.drift_thresholds = self._load_drift_thresholds()
    
    def detect_drift(
        self, 
        model_id: str, 
        current_data: Dict[str, Any], 
        reference_data: Dict[str, Any]
    ) -> List[DriftDetectionResult]:
        """Detect various types of drift."""
        
        drift_results = []
        timestamp = datetime.utcnow().isoformat()
        
        # Feature drift detection
        feature_drift = self._detect_feature_drift(current_data, reference_data)
        if feature_drift['drift_score'] > self.drift_thresholds['feature_drift']:
            drift_results.append(DriftDetectionResult(
                drift_type='feature_drift',
                drift_score=feature_drift['drift_score'],
                timestamp=timestamp,
                model_id=model_id,
                affected_features=feature_drift['affected_features'],
                severity=self._determine_severity(feature_drift['drift_score']),
                recommendation="Investigate feature distribution changes"
            ))
        
        # Prediction drift detection
        pred_drift = self._detect_prediction_drift(current_data, reference_data)
        if pred_drift['drift_score'] > self.drift_thresholds['prediction_drift']:
            drift_results.append(DriftDetectionResult(
                drift_type='prediction_drift',
                drift_score=pred_drift['drift_score'],
                timestamp=timestamp,
                model_id=model_id,
                affected_features=[],
                severity=self._determine_severity(pred_drift['drift_score']),
                recommendation="Review model predictions and consider retraining"
            ))
        
        # Store drift results
        self.drift_history.extend(drift_results)
        
        return drift_results
    
    def get_drift_status(self, model_id: str, days: int = 7) -> Dict[str, Any]:
        """Get drift status for a model."""
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        recent_drifts = [
            d for d in self.drift_history 
            if d.model_id == model_id and d.timestamp >= cutoff_date
        ]
        
        if not recent_drifts:
            return {
                'model_id': model_id,
                'max_drift_score': 0.0,
                'drift_count': 0,
                'high_severity_count': 0,
                'status': 'stable'
            }
        
        max_drift_score = max(d.drift_score for d in recent_drifts)
        high_severity_count = len([d for d in recent_drifts if d.severity == 'high'])
        
        return {
            'model_id': model_id,
            'max_drift_score': max_drift_score,
            'drift_count': len(recent_drifts),
            'high_severity_count': high_severity_count,
            'status': 'unstable' if max_drift_score > 0.7 else 'stable',
            'recent_drifts': [asdict(d) for d in recent_drifts]
        }
    
    def _load_drift_thresholds(self) -> Dict[str, float]:
        """Load drift detection thresholds."""
        return {
            'feature_drift': 0.3,
            'prediction_drift': 0.4,
            'concept_drift': 0.5
        }
    
    def _detect_feature_drift(
        self, 
        current_data: Dict[str, Any], 
        reference_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect feature drift using statistical methods."""
        
        # Simple implementation - would use proper statistical tests in practice
        drift_score = 0.0
        affected_features = []
        
        common_features = set(current_data.keys()) & set(reference_data.keys())
        
        for feature in common_features:
            current_val = current_data.get(feature, 0)
            reference_val = reference_data.get(feature, 0)
            
            if isinstance(current_val, (int, float)) and isinstance(reference_val, (int, float)):
                # Calculate relative difference
                if reference_val != 0:
                    relative_diff = abs(current_val - reference_val) / abs(reference_val)
                    if relative_diff > 0.2:  # 20% threshold
                        drift_score = max(drift_score, relative_diff)
                        affected_features.append(feature)
        
        return {
            'drift_score': min(drift_score, 1.0),
            'affected_features': affected_features
        }
    
    def _detect_prediction_drift(
        self, 
        current_data: Dict[str, Any], 
        reference_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect prediction drift."""
        
        # Simple implementation - would use proper statistical tests in practice
        current_predictions = current_data.get('predictions', [])
        reference_predictions = reference_data.get('predictions', [])
        
        if not current_predictions or not reference_predictions:
            return {'drift_score': 0.0}
        
        # Calculate simple drift score based on prediction distributions
        if isinstance(current_predictions, list) and isinstance(reference_predictions, list):
            current_avg = sum(current_predictions) / len(current_predictions)
            reference_avg = sum(reference_predictions) / len(reference_predictions)
            
            drift_score = abs(current_avg - reference_avg) if reference_avg != 0 else 0.0
        else:
            drift_score = 0.0
        
        return {'drift_score': min(drift_score, 1.0)}
    
    def _determine_severity(self, drift_score: float) -> str:
        """Determine drift severity."""
        
        if drift_score >= 0.7:
            return 'high'
        elif drift_score >= 0.4:
            return 'medium'
        else:
            return 'low'


class ModelApprovalWorkflow:
    """Model approval workflow manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.approval_history = []
        self.pending_approvals = []
    
    def submit_approval_request(
        self, 
        model_id: str, 
        approval_type: str, 
        criteria: Dict[str, Any]
    ) -> str:
        """Submit model for approval."""
        
        event_id = f"approval_{model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        approval_event = ModelApprovalEvent(
            event_id=event_id,
            model_id=model_id,
            event_type='submitted',
            timestamp=datetime.utcnow().isoformat(),
            approval_criteria=criteria
        )
        
        self.approval_history.append(approval_event)
        self.pending_approvals.append(approval_event)
        
        logger.info(f"Approval request submitted: {event_id}")
        return event_id
    
    def get_approval_status(self, model_id: str) -> Dict[str, Any]:
        """Get approval status for a model."""
        
        # Get latest approval events for this model
        model_events = [e for e in self.approval_history if e.model_id == model_id]
        
        if not model_events:
            return {
                'model_id': model_id,
                'is_approved': False,
                'approval_status': 'not_submitted',
                'latest_event': None
            }
        
        # Get most recent event
        latest_event = max(model_events, key=lambda x: x.timestamp)
        
        is_approved = latest_event.event_type == 'approved'
        
        return {
            'model_id': model_id,
            'is_approved': is_approved,
            'approval_status': latest_event.event_type,
            'latest_event': asdict(latest_event),
            'approval_history': [asdict(e) for e in model_events]
        }