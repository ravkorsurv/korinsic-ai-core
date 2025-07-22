"""
Advanced Analytics Module for Korinsic Surveillance Platform

This module provides enhanced analytics capabilities including:
- Advanced drift detection with multiple statistical methods
- Performance intelligence and optimization
- Trace anomaly detection and prediction
- Root cause analysis and forecasting
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