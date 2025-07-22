"""
Advanced Analytics Module for Korinsic Surveillance Platform

This module provides comprehensive analytics capabilities for financial surveillance
and regulatory compliance, built on top of OpenInference tracing infrastructure.

Core Capabilities:
- Advanced drift detection with multiple statistical methods (KS test, PSI, JS divergence)
- Performance intelligence and optimization with ML-based anomaly detection
- Trace anomaly detection and prediction using clustering and pattern recognition
- Root cause analysis and forecasting for proactive risk management

The module integrates seamlessly with existing model governance frameworks and
provides real-time monitoring, alerting, and visualization capabilities for
production-grade financial surveillance systems.

Architecture:
- drift_detection.py: Statistical drift analysis engine
- drift_integration.py: OpenInference integration and monitoring service
- performance_intelligence.py: ML-based performance optimization (Phase 2)
- trace_anomaly.py: Distributed trace anomaly detection (Phase 3)

Usage:
    from src.analytics import AdvancedDriftAnalyzer, DriftMonitoringService
    
    analyzer = AdvancedDriftAnalyzer()
    service = DriftMonitoringService()
    await service.start_continuous_monitoring(['model_1', 'model_2'])
"""

from .drift_detection import (
    AdvancedDriftAnalyzer,
    DriftAnalysisResult,
    DriftForecast,
    RootCauseAnalysis,
    DriftVisualizationData,
)

from .performance_intelligence import (
    IntelligentBenchmarkSystem,
    PerformanceAnomaly,
    OptimizationPlan,
    BenchmarkSuite,
)

from .trace_anomaly import (
    TraceAnomalyDetector,
    TraceAnomaly,
    TraceClusters,
    PredictedIssue,
)

__version__ = "1.0.0"
__author__ = "Korinsic Analytics Team"
__license__ = "Proprietary"
__maintainer__ = "analytics-team@korinsic.com"
__contact__ = "support@korinsic.com"
__status__ = "Production"

__all__ = [
    # Drift Detection
    "AdvancedDriftAnalyzer",
    "DriftAnalysisResult", 
    "DriftForecast",
    "RootCauseAnalysis",
    "DriftVisualizationData",
    
    # Performance Intelligence
    "IntelligentBenchmarkSystem",
    "PerformanceAnomaly",
    "OptimizationPlan", 
    "BenchmarkSuite",
    
    # Trace Anomaly Detection
    "TraceAnomalyDetector",
    "TraceAnomaly",
    "TraceClusters",
    "PredictedIssue",
]