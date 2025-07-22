"""
Advanced Drift Detection for Korinsic Surveillance Platform

This module provides comprehensive drift detection capabilities with:
- Multiple statistical methods (KS test, PSI, Jensen-Shannon divergence)
- Root cause analysis for detected drift
- Predictive drift modeling with time series analysis
- Integration with OpenInference tracing
- Bayesian-specific drift detection for evidence patterns
"""

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from collections import defaultdict
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings

# Import existing components
from ..models.explainability.governance_tracker import (
    DriftDetectionResult,
    ModelDriftDetector
)
from ..utils.openinference_tracer import get_tracer

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore', category=RuntimeWarning)


@dataclass
class DriftAnalysisResult:
    """Comprehensive drift analysis result."""
    
    model_id: str
    timestamp: str
    drift_type: str
    drift_score: float
    severity: str
    statistical_method: str
    p_value: Optional[float]
    confidence_interval: Optional[Tuple[float, float]]
    affected_features: List[str]
    root_cause_analysis: Dict[str, Any]
    recommendation: str
    trace_id: Optional[str] = None


@dataclass
class DriftForecast:
    """Drift prediction forecast."""
    
    model_id: str
    forecast_horizon_days: int
    predicted_drift_score: float
    confidence_lower: float
    confidence_upper: float
    likelihood_high_drift: float
    contributing_factors: List[str]
    recommended_actions: List[str]
    forecast_timestamp: str


@dataclass
class RootCauseAnalysis:
    """Root cause analysis for drift detection."""
    
    primary_cause: str
    contributing_factors: List[Dict[str, Any]]
    market_regime_change: bool
    data_quality_issues: List[str]
    seasonal_patterns: List[str]
    regulatory_changes: List[str]
    confidence_score: float


@dataclass
class DriftVisualizationData:
    """Data for drift visualization dashboards."""
    
    model_id: str
    time_series_data: List[Dict[str, Any]]
    feature_importance: Dict[str, float]
    distribution_comparisons: Dict[str, Dict[str, Any]]
    trend_analysis: Dict[str, Any]
    alert_timeline: List[Dict[str, Any]]


class AdvancedDriftAnalyzer:
    """
    Advanced drift detection with multiple statistical methods and 
    integration with OpenInference tracing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the advanced drift analyzer.
        
        Args:
            config: Configuration dictionary for drift detection
        """
        self.config = config or {}
        self.tracer = get_tracer()
        
        # Enhanced thresholds for different statistical methods
        self.drift_thresholds = self._load_enhanced_thresholds()
        
        # Historical data storage
        self.drift_history = []
        self.reference_distributions = {}
        self.seasonal_patterns = {}
        
        # Statistical models for prediction
        self.drift_predictors = {}
        
        # Initialize base drift detector for compatibility
        self.base_detector = ModelDriftDetector(self.config.get("base_detector", {}))
        
        logger.info("Advanced drift analyzer initialized")
    
    def detect_comprehensive_drift(
        self, 
        model_id: str, 
        current_data: Dict[str, Any],
        reference_data: Dict[str, Any],
        trace_data: Optional[Dict[str, Any]] = None
    ) -> List[DriftAnalysisResult]:
        """
        Multi-dimensional drift detection using advanced statistical methods.
        
        Args:
            model_id: Model identifier
            current_data: Current data sample
            reference_data: Reference data sample
            trace_data: Optional OpenInference trace data
            
        Returns:
            List of comprehensive drift analysis results
        """
        with self.tracer.trace_bayesian_inference(
            model_name="drift_detection",
            model_version="2.0.0",
            input_data={"model_id": model_id, "data_size": len(current_data)}
        ) as span:
            try:
                drift_results = []
                timestamp = datetime.now(timezone.utc).isoformat()
                
                if span:
                    span.set_attribute("drift.model_id", model_id)
                    span.set_attribute("drift.analysis_type", "comprehensive")
                
                # 1. Kolmogorov-Smirnov Test for Feature Distributions
                ks_results = self._detect_distribution_drift_ks(
                    current_data, reference_data, model_id
                )
                drift_results.extend(ks_results)
                
                # 2. Population Stability Index (PSI) for Model Inputs
                psi_results = self._detect_psi_drift(
                    current_data, reference_data, model_id
                )
                drift_results.extend(psi_results)
                
                # 3. Jensen-Shannon Divergence for Complex Distributions
                js_results = self._detect_js_divergence_drift(
                    current_data, reference_data, model_id
                )
                drift_results.extend(js_results)
                
                # 4. Concept Drift Detection using Model Performance
                if trace_data:
                    concept_results = self._detect_concept_drift(
                        trace_data, model_id
                    )
                    drift_results.extend(concept_results)
                
                # 5. Temporal Drift Analysis
                temporal_results = self._detect_temporal_drift(
                    current_data, model_id, timestamp
                )
                drift_results.extend(temporal_results)
                
                # 6. Evidence Pattern Drift for Bayesian Models
                evidence_results = self._detect_evidence_pattern_drift(
                    current_data, reference_data, model_id
                )
                drift_results.extend(evidence_results)
                
                # Perform root cause analysis for significant drifts
                significant_drifts = [d for d in drift_results if d.severity in ['medium', 'high']]
                if significant_drifts:
                    for drift_result in significant_drifts:
                        drift_result.root_cause_analysis = self.analyze_drift_root_causes(
                            [drift_result], current_data, reference_data
                        )
                
                # Store results for historical analysis
                self.drift_history.extend(drift_results)
                
                if span:
                    span.set_attribute("drift.total_detections", len(drift_results))
                    span.set_attribute("drift.significant_count", len(significant_drifts))
                
                logger.info(
                    f"Comprehensive drift analysis completed for {model_id}: "
                    f"{len(drift_results)} total detections, {len(significant_drifts)} significant"
                )
                
                return drift_results
                
            except Exception as e:
                logger.error(f"Error in comprehensive drift detection: {e}")
                if span:
                    span.record_exception(e)
                raise
    
    def _detect_distribution_drift_ks(
        self, 
        current_data: Dict[str, Any], 
        reference_data: Dict[str, Any],
        model_id: str
    ) -> List[DriftAnalysisResult]:
        """Detect drift using Kolmogorov-Smirnov test."""
        results = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        common_features = set(current_data.keys()) & set(reference_data.keys())
        
        for feature in common_features:
            current_vals = self._extract_numeric_values(current_data[feature])
            reference_vals = self._extract_numeric_values(reference_data[feature])
            
            if len(current_vals) > 5 and len(reference_vals) > 5:
                try:
                    # Perform KS test
                    ks_statistic, p_value = stats.ks_2samp(current_vals, reference_vals)
                    
                    # Calculate confidence interval
                    alpha = 0.05
                    critical_value = stats.kstwo.ppf(1 - alpha/2, min(len(current_vals), len(reference_vals)))
                    conf_lower = max(0, ks_statistic - critical_value)
                    conf_upper = min(1, ks_statistic + critical_value)
                    
                    if ks_statistic > self.drift_thresholds["ks_test"]:
                        severity = self._determine_severity(ks_statistic, "ks_test")
                        
                        results.append(DriftAnalysisResult(
                            model_id=model_id,
                            timestamp=timestamp,
                            drift_type="feature_distribution_drift",
                            drift_score=ks_statistic,
                            severity=severity,
                            statistical_method="kolmogorov_smirnov",
                            p_value=p_value,
                            confidence_interval=(conf_lower, conf_upper),
                            affected_features=[feature],
                            root_cause_analysis={},
                            recommendation=f"Feature '{feature}' shows significant distribution change (KS={ks_statistic:.4f}, p={p_value:.4f})"
                        ))
                        
                except Exception as e:
                    logger.warning(f"KS test failed for feature {feature}: {e}")
        
        return results
    
    def _detect_psi_drift(
        self, 
        current_data: Dict[str, Any], 
        reference_data: Dict[str, Any],
        model_id: str
    ) -> List[DriftAnalysisResult]:
        """Detect drift using Population Stability Index (PSI)."""
        results = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        common_features = set(current_data.keys()) & set(reference_data.keys())
        
        for feature in common_features:
            current_vals = self._extract_numeric_values(current_data[feature])
            reference_vals = self._extract_numeric_values(reference_data[feature])
            
            if len(current_vals) > 10 and len(reference_vals) > 10:
                try:
                    psi_score = self._calculate_psi(current_vals, reference_vals)
                    
                    if psi_score > self.drift_thresholds["psi"]:
                        severity = self._determine_severity(psi_score, "psi")
                        
                        results.append(DriftAnalysisResult(
                            model_id=model_id,
                            timestamp=timestamp,
                            drift_type="population_stability_drift",
                            drift_score=psi_score,
                            severity=severity,
                            statistical_method="population_stability_index",
                            p_value=None,
                            confidence_interval=None,
                            affected_features=[feature],
                            root_cause_analysis={},
                            recommendation=f"Feature '{feature}' shows population instability (PSI={psi_score:.4f})"
                        ))
                        
                except Exception as e:
                    logger.warning(f"PSI calculation failed for feature {feature}: {e}")
        
        return results
    
    def _detect_js_divergence_drift(
        self, 
        current_data: Dict[str, Any], 
        reference_data: Dict[str, Any],
        model_id: str
    ) -> List[DriftAnalysisResult]:
        """Detect drift using Jensen-Shannon divergence."""
        results = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        common_features = set(current_data.keys()) & set(reference_data.keys())
        
        for feature in common_features:
            current_vals = self._extract_numeric_values(current_data[feature])
            reference_vals = self._extract_numeric_values(reference_data[feature])
            
            if len(current_vals) > 10 and len(reference_vals) > 10:
                try:
                    js_divergence = self._calculate_js_divergence(current_vals, reference_vals)
                    
                    if js_divergence > self.drift_thresholds["js_divergence"]:
                        severity = self._determine_severity(js_divergence, "js_divergence")
                        
                        results.append(DriftAnalysisResult(
                            model_id=model_id,
                            timestamp=timestamp,
                            drift_type="distribution_divergence_drift",
                            drift_score=js_divergence,
                            severity=severity,
                            statistical_method="jensen_shannon_divergence",
                            p_value=None,
                            confidence_interval=None,
                            affected_features=[feature],
                            root_cause_analysis={},
                            recommendation=f"Feature '{feature}' shows significant divergence (JS={js_divergence:.4f})"
                        ))
                        
                except Exception as e:
                    logger.warning(f"JS divergence calculation failed for feature {feature}: {e}")
        
        return results
    
    def _detect_concept_drift(
        self, 
        trace_data: Dict[str, Any],
        model_id: str
    ) -> List[DriftAnalysisResult]:
        """Detect concept drift using model performance degradation."""
        results = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        try:
            # Extract performance metrics from trace data
            performance_metrics = trace_data.get("performance_metrics", [])
            
            if len(performance_metrics) > 10:
                # Calculate rolling performance degradation
                recent_performance = performance_metrics[-10:]
                baseline_performance = performance_metrics[:-10] if len(performance_metrics) > 20 else performance_metrics[:10]
                
                recent_avg = np.mean([m.get("accuracy", 0) for m in recent_performance])
                baseline_avg = np.mean([m.get("accuracy", 0) for m in baseline_performance])
                
                performance_degradation = (baseline_avg - recent_avg) / baseline_avg if baseline_avg > 0 else 0
                
                if performance_degradation > self.drift_thresholds["concept_drift"]:
                    severity = self._determine_severity(performance_degradation, "concept_drift")
                    
                    results.append(DriftAnalysisResult(
                        model_id=model_id,
                        timestamp=timestamp,
                        drift_type="concept_drift",
                        drift_score=performance_degradation,
                        severity=severity,
                        statistical_method="performance_degradation",
                        p_value=None,
                        confidence_interval=None,
                        affected_features=["model_performance"],
                        root_cause_analysis={},
                        recommendation=f"Model performance degraded by {performance_degradation:.2%}, indicating concept drift"
                    ))
                    
        except Exception as e:
            logger.warning(f"Concept drift detection failed: {e}")
        
        return results
    
    def _detect_temporal_drift(
        self, 
        current_data: Dict[str, Any],
        model_id: str,
        timestamp: str
    ) -> List[DriftAnalysisResult]:
        """Detect temporal drift patterns."""
        results = []
        
        try:
            # Get historical drift data for this model
            historical_drifts = [
                d for d in self.drift_history 
                if d.model_id == model_id and d.timestamp >= (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            ]
            
            if len(historical_drifts) > 5:
                # Calculate drift acceleration
                drift_scores = [d.drift_score for d in historical_drifts[-10:]]
                
                if len(drift_scores) > 3:
                    # Simple trend analysis
                    x = np.arange(len(drift_scores))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, drift_scores)
                    
                    if slope > self.drift_thresholds["temporal_acceleration"]:
                        severity = self._determine_severity(slope, "temporal_acceleration")
                        
                        results.append(DriftAnalysisResult(
                            model_id=model_id,
                            timestamp=timestamp,
                            drift_type="temporal_drift",
                            drift_score=slope,
                            severity=severity,
                            statistical_method="linear_regression",
                            p_value=p_value,
                            confidence_interval=None,
                            affected_features=["temporal_pattern"],
                            root_cause_analysis={},
                            recommendation=f"Accelerating drift pattern detected (slope={slope:.4f}, R²={r_value**2:.4f})"
                        ))
                        
        except Exception as e:
            logger.warning(f"Temporal drift detection failed: {e}")
        
        return results
    
    def _detect_evidence_pattern_drift(
        self, 
        current_data: Dict[str, Any], 
        reference_data: Dict[str, Any],
        model_id: str
    ) -> List[DriftAnalysisResult]:
        """Detect drift in evidence patterns for Bayesian models."""
        results = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        try:
            # Extract evidence patterns
            current_evidence = current_data.get("evidence", {})
            reference_evidence = reference_data.get("evidence", {})
            
            if current_evidence and reference_evidence:
                # Compare evidence sufficiency patterns
                current_sufficiency = self._calculate_evidence_sufficiency_pattern(current_evidence)
                reference_sufficiency = self._calculate_evidence_sufficiency_pattern(reference_evidence)
                
                sufficiency_drift = abs(current_sufficiency - reference_sufficiency)
                
                if sufficiency_drift > self.drift_thresholds["evidence_pattern"]:
                    severity = self._determine_severity(sufficiency_drift, "evidence_pattern")
                    
                    results.append(DriftAnalysisResult(
                        model_id=model_id,
                        timestamp=timestamp,
                        drift_type="evidence_pattern_drift",
                        drift_score=sufficiency_drift,
                        severity=severity,
                        statistical_method="evidence_sufficiency_comparison",
                        p_value=None,
                        confidence_interval=None,
                        affected_features=["evidence_patterns"],
                        root_cause_analysis={},
                        recommendation=f"Evidence sufficiency pattern changed significantly (drift={sufficiency_drift:.4f})"
                    ))
                    
        except Exception as e:
            logger.warning(f"Evidence pattern drift detection failed: {e}")
        
        return results
    
    def analyze_drift_root_causes(
        self, 
        drift_results: List[DriftAnalysisResult],
        current_data: Dict[str, Any],
        reference_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Root cause analysis for detected drift.
        
        Args:
            drift_results: List of drift detection results
            current_data: Current data sample
            reference_data: Reference data sample
            
        Returns:
            Root cause analysis results
        """
        try:
            # Analyze market regime changes
            market_regime_change = self._detect_market_regime_change(current_data, reference_data)
            
            # Detect data quality issues
            data_quality_issues = self._detect_data_quality_issues(current_data, reference_data)
            
            # Identify seasonal patterns
            seasonal_patterns = self._identify_seasonal_patterns(drift_results)
            
            # Check for regulatory environment changes
            regulatory_changes = self._detect_regulatory_changes(current_data, reference_data)
            
            # Determine primary cause
            primary_cause = self._determine_primary_cause(
                market_regime_change, data_quality_issues, seasonal_patterns, regulatory_changes
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_root_cause_confidence(
                drift_results, market_regime_change, data_quality_issues
            )
            
            return {
                "primary_cause": primary_cause,
                "contributing_factors": [
                    {"factor": "market_regime_change", "detected": market_regime_change, "impact": 0.8 if market_regime_change else 0.0},
                    {"factor": "data_quality_issues", "detected": len(data_quality_issues) > 0, "impact": len(data_quality_issues) * 0.3},
                    {"factor": "seasonal_patterns", "detected": len(seasonal_patterns) > 0, "impact": len(seasonal_patterns) * 0.2},
                    {"factor": "regulatory_changes", "detected": len(regulatory_changes) > 0, "impact": len(regulatory_changes) * 0.4},
                ],
                "market_regime_change": market_regime_change,
                "data_quality_issues": data_quality_issues,
                "seasonal_patterns": seasonal_patterns,
                "regulatory_changes": regulatory_changes,
                "confidence_score": confidence_score
            }
            
        except Exception as e:
            logger.error(f"Root cause analysis failed: {e}")
            return {
                "primary_cause": "unknown",
                "confidence_score": 0.0,
                "error": str(e)
            }
    
    def predict_future_drift(
        self, 
        model_id: str,
        forecast_horizon_days: int = 7
    ) -> DriftForecast:
        """
        Predictive drift modeling with time series analysis.
        
        Args:
            model_id: Model identifier
            forecast_horizon_days: Number of days to forecast
            
        Returns:
            Drift forecast with confidence intervals
        """
        try:
            # Get historical drift data
            historical_drifts = [
                d for d in self.drift_history 
                if d.model_id == model_id
            ]
            
            if len(historical_drifts) < 10:
                # Not enough data for prediction
                return DriftForecast(
                    model_id=model_id,
                    forecast_horizon_days=forecast_horizon_days,
                    predicted_drift_score=0.0,
                    confidence_lower=0.0,
                    confidence_upper=0.0,
                    likelihood_high_drift=0.0,
                    contributing_factors=[],
                    recommended_actions=["Collect more historical data for accurate predictions"],
                    forecast_timestamp=datetime.now(timezone.utc).isoformat()
                )
            
            # Prepare time series data
            drift_scores = [d.drift_score for d in historical_drifts[-30:]]  # Last 30 observations
            
            # Simple ARIMA-like prediction (simplified for demo)
            predicted_score = self._predict_drift_score(drift_scores, forecast_horizon_days)
            
            # Calculate confidence intervals
            std_dev = np.std(drift_scores)
            confidence_lower = max(0.0, predicted_score - 1.96 * std_dev)
            confidence_upper = min(1.0, predicted_score + 1.96 * std_dev)
            
            # Calculate likelihood of high drift
            likelihood_high_drift = self._calculate_high_drift_likelihood(drift_scores, predicted_score)
            
            # Identify contributing factors
            contributing_factors = self._identify_drift_contributing_factors(historical_drifts)
            
            # Generate recommendations
            recommended_actions = self._generate_drift_recommendations(
                predicted_score, likelihood_high_drift, contributing_factors
            )
            
            return DriftForecast(
                model_id=model_id,
                forecast_horizon_days=forecast_horizon_days,
                predicted_drift_score=predicted_score,
                confidence_lower=confidence_lower,
                confidence_upper=confidence_upper,
                likelihood_high_drift=likelihood_high_drift,
                contributing_factors=contributing_factors,
                recommended_actions=recommended_actions,
                forecast_timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Drift prediction failed for model {model_id}: {e}")
            return DriftForecast(
                model_id=model_id,
                forecast_horizon_days=forecast_horizon_days,
                predicted_drift_score=0.0,
                confidence_lower=0.0,
                confidence_upper=0.0,
                likelihood_high_drift=0.0,
                contributing_factors=[],
                recommended_actions=[f"Prediction failed: {str(e)}"],
                forecast_timestamp=datetime.now(timezone.utc).isoformat()
            )
    
    def generate_drift_visualization_data(self, model_id: str, days: int = 30) -> DriftVisualizationData:
        """Generate data for drift visualization dashboards."""
        try:
            # Get recent drift history
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            recent_drifts = [
                d for d in self.drift_history 
                if d.model_id == model_id and d.timestamp >= cutoff_date
            ]
            
            # Prepare time series data
            time_series_data = [
                {
                    "timestamp": d.timestamp,
                    "drift_score": d.drift_score,
                    "drift_type": d.drift_type,
                    "severity": d.severity,
                    "statistical_method": d.statistical_method
                }
                for d in recent_drifts
            ]
            
            # Calculate feature importance
            feature_importance = self._calculate_feature_drift_importance(recent_drifts)
            
            # Generate distribution comparisons
            distribution_comparisons = self._generate_distribution_comparisons(recent_drifts)
            
            # Trend analysis
            trend_analysis = self._analyze_drift_trends(recent_drifts)
            
            # Alert timeline
            alert_timeline = [
                {
                    "timestamp": d.timestamp,
                    "severity": d.severity,
                    "message": d.recommendation,
                    "drift_type": d.drift_type
                }
                for d in recent_drifts if d.severity in ['medium', 'high']
            ]
            
            return DriftVisualizationData(
                model_id=model_id,
                time_series_data=time_series_data,
                feature_importance=feature_importance,
                distribution_comparisons=distribution_comparisons,
                trend_analysis=trend_analysis,
                alert_timeline=alert_timeline
            )
            
        except Exception as e:
            logger.error(f"Failed to generate visualization data: {e}")
            return DriftVisualizationData(
                model_id=model_id,
                time_series_data=[],
                feature_importance={},
                distribution_comparisons={},
                trend_analysis={},
                alert_timeline=[]
            )
    
    # Helper methods
    def _load_enhanced_thresholds(self) -> Dict[str, float]:
        """Load enhanced drift detection thresholds."""
        return {
            "ks_test": 0.1,
            "psi": 0.2,
            "js_divergence": 0.3,
            "concept_drift": 0.15,
            "temporal_acceleration": 0.05,
            "evidence_pattern": 0.25
        }
    
    def _extract_numeric_values(self, data: Any) -> List[float]:
        """Extract numeric values from various data formats."""
        if isinstance(data, (list, np.ndarray)):
            return [float(x) for x in data if isinstance(x, (int, float)) and not np.isnan(x)]
        elif isinstance(data, (int, float)) and not np.isnan(data):
            return [float(data)]
        elif isinstance(data, dict):
            # For nested dictionaries, extract all numeric values
            values = []
            for value in data.values():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    values.append(float(value))
            return values
        return []
    
    def _calculate_psi(self, current_vals: List[float], reference_vals: List[float]) -> float:
        """Calculate Population Stability Index."""
        try:
            # Create bins based on reference data
            bins = np.histogram_bin_edges(reference_vals, bins=10)
            
            # Calculate distributions
            current_hist, _ = np.histogram(current_vals, bins=bins)
            reference_hist, _ = np.histogram(reference_vals, bins=bins)
            
            # Normalize to probabilities
            current_dist = current_hist / np.sum(current_hist)
            reference_dist = reference_hist / np.sum(reference_hist)
            
            # Add small epsilon to avoid division by zero
            epsilon = 1e-10
            current_dist = current_dist + epsilon
            reference_dist = reference_dist + epsilon
            
            # Calculate PSI
            psi = np.sum((current_dist - reference_dist) * np.log(current_dist / reference_dist))
            
            return float(psi)
            
        except Exception as e:
            logger.warning(f"PSI calculation failed: {e}")
            return 0.0
    
    def _calculate_js_divergence(self, current_vals: List[float], reference_vals: List[float]) -> float:
        """Calculate Jensen-Shannon divergence."""
        try:
            # Create bins
            all_vals = current_vals + reference_vals
            bins = np.histogram_bin_edges(all_vals, bins=20)
            
            # Calculate distributions
            current_hist, _ = np.histogram(current_vals, bins=bins)
            reference_hist, _ = np.histogram(reference_vals, bins=bins)
            
            # Normalize to probabilities
            current_dist = current_hist / np.sum(current_hist)
            reference_dist = reference_hist / np.sum(reference_hist)
            
            # Add small epsilon
            epsilon = 1e-10
            current_dist = current_dist + epsilon
            reference_dist = reference_dist + epsilon
            
            # Calculate JS divergence
            m = 0.5 * (current_dist + reference_dist)
            js_div = 0.5 * stats.entropy(current_dist, m) + 0.5 * stats.entropy(reference_dist, m)
            
            return float(js_div)
            
        except Exception as e:
            logger.warning(f"JS divergence calculation failed: {e}")
            return 0.0
    
    def _calculate_evidence_sufficiency_pattern(self, evidence: Dict[str, Any]) -> float:
        """Calculate evidence sufficiency pattern for Bayesian models."""
        try:
            if not evidence:
                return 0.0
            
            # Simple sufficiency calculation based on evidence quality and quantity
            total_evidence = 0
            weighted_sum = 0
            
            for key, value in evidence.items():
                if isinstance(value, dict):
                    confidence = value.get('confidence', 'Low')
                    weight = {'High': 3, 'Medium': 2, 'Low': 1}.get(confidence, 1)
                    evidence_value = value.get('value', 0)
                    
                    total_evidence += weight
                    weighted_sum += evidence_value * weight
            
            return weighted_sum / total_evidence if total_evidence > 0 else 0.0
            
        except Exception as e:
            logger.warning(f"Evidence sufficiency calculation failed: {e}")
            return 0.0
    
    def _determine_severity(self, score: float, method: str) -> str:
        """Determine drift severity based on score and method."""
        thresholds = {
            "ks_test": {"high": 0.3, "medium": 0.15},
            "psi": {"high": 0.5, "medium": 0.25},
            "js_divergence": {"high": 0.6, "medium": 0.4},
            "concept_drift": {"high": 0.3, "medium": 0.2},
            "temporal_acceleration": {"high": 0.1, "medium": 0.07},
            "evidence_pattern": {"high": 0.5, "medium": 0.3}
        }
        
        method_thresholds = thresholds.get(method, {"high": 0.7, "medium": 0.4})
        
        if score >= method_thresholds["high"]:
            return "high"
        elif score >= method_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _detect_market_regime_change(self, current_data: Dict, reference_data: Dict) -> bool:
        """Detect market regime changes."""
        try:
            # Simple heuristic based on volatility changes
            current_volatility = current_data.get("market_volatility", 0)
            reference_volatility = reference_data.get("market_volatility", 0)
            
            if reference_volatility > 0:
                volatility_change = abs(current_volatility - reference_volatility) / reference_volatility
                return volatility_change > 0.5
            
            return False
        except:
            return False
    
    def _detect_data_quality_issues(self, current_data: Dict, reference_data: Dict) -> List[str]:
        """Detect data quality issues."""
        issues = []
        
        try:
            # Check for missing data
            current_size = len(current_data)
            reference_size = len(reference_data)
            
            if current_size < reference_size * 0.8:
                issues.append("Significant data volume reduction")
            
            # Check for data completeness
            current_nulls = sum(1 for v in current_data.values() if v is None or v == "")
            if current_nulls > len(current_data) * 0.1:
                issues.append("High percentage of missing values")
            
        except:
            issues.append("Data quality assessment failed")
        
        return issues
    
    def _identify_seasonal_patterns(self, drift_results: List[DriftAnalysisResult]) -> List[str]:
        """Identify seasonal patterns in drift."""
        patterns = []
        
        try:
            if len(drift_results) > 10:
                # Simple seasonal pattern detection
                timestamps = [datetime.fromisoformat(d.timestamp.replace('Z', '+00:00')) for d in drift_results]
                hours = [ts.hour for ts in timestamps]
                
                # Check for hourly patterns
                hour_counts = defaultdict(int)
                for hour in hours:
                    hour_counts[hour] += 1
                
                max_hour = max(hour_counts, key=hour_counts.get)
                if hour_counts[max_hour] > len(drift_results) * 0.3:
                    patterns.append(f"Peak drift activity at hour {max_hour}")
                    
        except:
            pass
        
        return patterns
    
    def _detect_regulatory_changes(self, current_data: Dict, reference_data: Dict) -> List[str]:
        """Detect regulatory environment changes."""
        changes = []
        
        try:
            # Check for regulatory indicators
            current_reg_score = current_data.get("regulatory_score", 0)
            reference_reg_score = reference_data.get("regulatory_score", 0)
            
            if abs(current_reg_score - reference_reg_score) > 0.2:
                changes.append("Regulatory environment score changed significantly")
                
        except:
            pass
        
        return changes
    
    def _determine_primary_cause(self, market_change: bool, data_issues: List, seasonal: List, regulatory: List) -> str:
        """Determine primary cause of drift."""
        if market_change:
            return "market_regime_change"
        elif len(data_issues) > 0:
            return "data_quality_degradation"
        elif len(regulatory) > 0:
            return "regulatory_environment_change"
        elif len(seasonal) > 0:
            return "seasonal_pattern"
        else:
            return "unknown"
    
    def _calculate_root_cause_confidence(self, drift_results: List, market_change: bool, data_issues: List) -> float:
        """Calculate confidence in root cause analysis."""
        base_confidence = 0.5
        
        # Increase confidence based on evidence
        if len(drift_results) > 5:
            base_confidence += 0.2
        if market_change:
            base_confidence += 0.2
        if len(data_issues) > 0:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _predict_drift_score(self, historical_scores: List[float], horizon: int) -> float:
        """Predict future drift score using simple time series methods."""
        if len(historical_scores) < 3:
            return np.mean(historical_scores) if historical_scores else 0.0
        
        # Simple exponential smoothing
        alpha = 0.3
        forecast = historical_scores[0]
        
        for score in historical_scores[1:]:
            forecast = alpha * score + (1 - alpha) * forecast
        
        # Apply trend adjustment for horizon
        if len(historical_scores) > 5:
            recent_trend = np.mean(historical_scores[-3:]) - np.mean(historical_scores[-6:-3])
            forecast += recent_trend * (horizon / 7)  # Scale by horizon
        
        return max(0.0, min(1.0, forecast))
    
    def _calculate_high_drift_likelihood(self, historical_scores: List[float], predicted_score: float) -> float:
        """Calculate likelihood of high drift."""
        if not historical_scores:
            return 0.0
        
        high_drift_threshold = 0.6
        historical_high_rate = sum(1 for score in historical_scores if score > high_drift_threshold) / len(historical_scores)
        
        # Combine historical rate with predicted score
        predicted_likelihood = 1.0 if predicted_score > high_drift_threshold else predicted_score / high_drift_threshold
        
        return (historical_high_rate + predicted_likelihood) / 2
    
    def _identify_drift_contributing_factors(self, historical_drifts: List[DriftAnalysisResult]) -> List[str]:
        """Identify contributing factors from historical drift data."""
        factors = []
        
        if not historical_drifts:
            return factors
        
        # Analyze drift types
        drift_types = defaultdict(int)
        for drift in historical_drifts:
            drift_types[drift.drift_type] += 1
        
        most_common_type = max(drift_types, key=drift_types.get)
        factors.append(f"Primary drift type: {most_common_type}")
        
        # Analyze affected features
        all_features = []
        for drift in historical_drifts:
            all_features.extend(drift.affected_features)
        
        if all_features:
            feature_counts = defaultdict(int)
            for feature in all_features:
                feature_counts[feature] += 1
            
            most_affected = max(feature_counts, key=feature_counts.get)
            factors.append(f"Most affected feature: {most_affected}")
        
        return factors
    
    def _generate_drift_recommendations(self, predicted_score: float, likelihood: float, factors: List[str]) -> List[str]:
        """Generate recommendations based on drift prediction."""
        recommendations = []
        
        if predicted_score > 0.6:
            recommendations.append("High drift predicted - prepare for model retraining")
            recommendations.append("Increase monitoring frequency")
        elif predicted_score > 0.4:
            recommendations.append("Moderate drift expected - monitor closely")
        else:
            recommendations.append("Low drift risk - maintain standard monitoring")
        
        if likelihood > 0.7:
            recommendations.append("Consider proactive model updates")
        
        if "feature_distribution_drift" in str(factors):
            recommendations.append("Focus on feature engineering improvements")
        
        return recommendations
    
    def _calculate_feature_drift_importance(self, drift_results: List[DriftAnalysisResult]) -> Dict[str, float]:
        """Calculate feature importance for drift visualization."""
        importance = defaultdict(float)
        
        for drift in drift_results:
            for feature in drift.affected_features:
                importance[feature] += drift.drift_score
        
        # Normalize
        max_importance = max(importance.values()) if importance else 1.0
        return {k: v / max_importance for k, v in importance.items()}
    
    def _generate_distribution_comparisons(self, drift_results: List[DriftAnalysisResult]) -> Dict[str, Dict[str, Any]]:
        """Generate distribution comparison data."""
        comparisons = {}
        
        for drift in drift_results:
            if drift.statistical_method in ["kolmogorov_smirnov", "jensen_shannon_divergence"]:
                for feature in drift.affected_features:
                    comparisons[feature] = {
                        "drift_score": drift.drift_score,
                        "method": drift.statistical_method,
                        "p_value": drift.p_value,
                        "severity": drift.severity
                    }
        
        return comparisons
    
    def _analyze_drift_trends(self, drift_results: List[DriftAnalysisResult]) -> Dict[str, Any]:
        """Analyze drift trends over time."""
        if not drift_results:
            return {}
        
        # Sort by timestamp
        sorted_drifts = sorted(drift_results, key=lambda x: x.timestamp)
        
        # Calculate trend
        scores = [d.drift_score for d in sorted_drifts]
        if len(scores) > 2:
            x = np.arange(len(scores))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, scores)
            
            return {
                "trend_slope": slope,
                "trend_r_squared": r_value ** 2,
                "trend_p_value": p_value,
                "trend_direction": "increasing" if slope > 0.01 else "decreasing" if slope < -0.01 else "stable"
            }
        
        return {"trend_direction": "insufficient_data"}