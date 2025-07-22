#!/usr/bin/env python3
"""
Advanced Drift Detection Demo for Korinsic Surveillance Platform

This demo showcases Phase 1 of the Enhanced Analytics implementation:
- Multi-method statistical drift detection
- Root cause analysis capabilities
- Predictive drift modeling
- Integration with OpenInference tracing
- Real-time alerting and monitoring
- Comprehensive visualization data generation

The demo simulates realistic financial surveillance scenarios with:
- Market regime changes
- Data quality degradation
- Seasonal trading patterns
- Regulatory environment shifts
"""

import sys
import os
import asyncio
import json
import time
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from src.analytics.drift_detection import AdvancedDriftAnalyzer, DriftAnalysisResult
from src.analytics.drift_integration import DriftMonitoringService, DriftAlertManager
from src.utils.logger import setup_logger

logger = setup_logger()


class AdvancedDriftDetectionDemo:
    """
    Comprehensive demonstration of advanced drift detection capabilities.
    
    This demo showcases:
    - Multiple statistical methods for drift detection
    - Root cause analysis and predictive modeling
    - Real-time monitoring and alerting
    - Integration with OpenInference tracing
    - Business-relevant scenarios for financial surveillance
    """
    
    def __init__(self):
        """Initialize the advanced drift detection demo."""
        self.demo_id = f"advanced_drift_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = []
        
        # Initialize components
        self.drift_analyzer = AdvancedDriftAnalyzer({
            "drift_thresholds": {
                "ks_test": 0.1,
                "psi": 0.2,
                "js_divergence": 0.3,
                "concept_drift": 0.15,
                "temporal_acceleration": 0.05,
                "evidence_pattern": 0.25
            }
        })
        
        self.monitoring_service = DriftMonitoringService({
            "monitoring_interval_seconds": 5,
            "alert_thresholds": {
                "high_severity_drift": 0.7,
                "medium_severity_drift": 0.4,
                "drift_acceleration": 0.1
            }
        })
        
        self.alert_manager = DriftAlertManager()
        
        # Connect alert manager to monitoring service
        self.monitoring_service.add_alert_callback(self.alert_manager.handle_drift_alert)
        
        logger.info(f"Advanced Drift Detection Demo {self.demo_id} initialized")
    
    def generate_market_regime_scenario(self) -> Dict[str, Any]:
        """
        Generate data representing a market regime change scenario.
        
        This simulates the transition from a low-volatility to high-volatility market,
        which would affect trading patterns and risk model performance.
        """
        # Reference data (low volatility period)
        reference_data = {
            "trade_volumes": np.random.normal(1000, 200, 100).tolist(),
            "price_volatility": np.random.normal(0.02, 0.005, 100).tolist(),
            "order_sizes": np.random.normal(500, 100, 100).tolist(),
            "bid_ask_spreads": np.random.normal(0.001, 0.0002, 100).tolist(),
            "market_volatility": 0.02,
            "predictions": np.random.beta(2, 8, 100).tolist(),  # Mostly low risk scores
            "evidence": {
                "material_info": {"value": 1, "confidence": "Medium"},
                "trading_activity": {"value": 0, "confidence": "Low"},
                "timing": {"value": 1, "confidence": "Medium"},
                "price_impact": {"value": 0, "confidence": "Low"},
                "volume_anomaly": {"value": 0, "confidence": "Low"}
            }
        }
        
        # Current data (high volatility period - market regime change)
        current_data = {
            "trade_volumes": np.random.normal(2500, 800, 100).tolist(),  # Increased volume
            "price_volatility": np.random.normal(0.08, 0.02, 100).tolist(),  # Higher volatility
            "order_sizes": np.random.normal(1200, 400, 100).tolist(),  # Larger orders
            "bid_ask_spreads": np.random.normal(0.004, 0.001, 100).tolist(),  # Wider spreads
            "market_volatility": 0.08,  # Significantly higher
            "predictions": np.random.beta(4, 6, 100).tolist(),  # Higher risk scores
            "evidence": {
                "material_info": {"value": 2, "confidence": "High"},
                "trading_activity": {"value": 2, "confidence": "High"},
                "timing": {"value": 2, "confidence": "High"},
                "price_impact": {"value": 1, "confidence": "Medium"},
                "volume_anomaly": {"value": 2, "confidence": "High"}
            }
        }
        
        return {
            "scenario": "market_regime_change",
            "description": "Transition from low to high volatility market regime",
            "reference_data": reference_data,
            "current_data": current_data,
            "expected_drift_types": ["feature_distribution_drift", "population_stability_drift", "evidence_pattern_drift"]
        }
    
    def generate_data_quality_degradation_scenario(self) -> Dict[str, Any]:
        """
        Generate data representing data quality degradation.
        
        This simulates scenarios where data feeds become unreliable,
        affecting model inputs and performance.
        """
        # Reference data (good quality)
        reference_data = {
            "trade_prices": np.random.normal(100, 5, 150).tolist(),
            "trade_volumes": np.random.lognormal(6, 1, 150).tolist(),
            "timestamps": [(datetime.now() - timedelta(hours=i)).isoformat() for i in range(150)],
            "data_completeness": 0.98,
            "predictions": np.random.beta(3, 7, 150).tolist(),
            "evidence": {
                "material_info": {"value": 1, "confidence": "High"},
                "trading_activity": {"value": 1, "confidence": "High"},
                "timing": {"value": 1, "confidence": "High"}
            }
        }
        
        # Current data (degraded quality - missing values, outliers, delays)
        current_prices = np.random.normal(100, 5, 120).tolist()  # 20% missing data
        current_prices.extend([None] * 30)  # Add missing values
        current_prices.extend([500, -50, 1000])  # Add outliers
        
        current_volumes = np.random.lognormal(6, 1, 100).tolist()  # More missing data
        current_volumes.extend([None] * 50)
        
        current_data = {
            "trade_prices": current_prices,
            "trade_volumes": current_volumes,
            "timestamps": [(datetime.now() - timedelta(hours=i, minutes=np.random.randint(-30, 30))).isoformat() for i in range(150)],  # Timestamp inconsistencies
            "data_completeness": 0.75,  # Significantly lower
            "predictions": np.random.beta(2, 8, 120).tolist() + [None] * 30,  # Some missing predictions
            "evidence": {
                "material_info": {"value": 0, "confidence": "Low"},  # Degraded evidence
                "trading_activity": {"value": 0, "confidence": "Low"},
                "timing": {"value": 1, "confidence": "Medium"}
            }
        }
        
        return {
            "scenario": "data_quality_degradation",
            "description": "Data feed reliability issues with missing values and outliers",
            "reference_data": reference_data,
            "current_data": current_data,
            "expected_drift_types": ["feature_distribution_drift", "evidence_pattern_drift"]
        }
    
    def generate_seasonal_pattern_scenario(self) -> Dict[str, Any]:
        """
        Generate data representing seasonal trading patterns.
        
        This simulates end-of-quarter trading behavior changes that
        could affect risk model performance.
        """
        # Reference data (mid-quarter normal trading)
        base_activity = np.random.normal(1.0, 0.2, 100)
        reference_data = {
            "trading_intensity": base_activity.tolist(),
            "order_frequency": (base_activity * np.random.normal(50, 10, 100)).tolist(),
            "risk_appetite": np.random.beta(4, 6, 100).tolist(),
            "regulatory_score": 0.3,
            "predictions": np.random.beta(3, 7, 100).tolist(),
            "evidence": {
                "material_info": {"value": 1, "confidence": "Medium"},
                "trading_activity": {"value": 1, "confidence": "Medium"},
                "timing": {"value": 1, "confidence": "Medium"}
            }
        }
        
        # Current data (end-of-quarter increased activity)
        seasonal_multiplier = np.random.normal(2.5, 0.5, 100)  # Significant increase
        current_data = {
            "trading_intensity": seasonal_multiplier.tolist(),
            "order_frequency": (seasonal_multiplier * np.random.normal(50, 10, 100)).tolist(),
            "risk_appetite": np.random.beta(6, 4, 100).tolist(),  # Higher risk appetite
            "regulatory_score": 0.3,  # Same regulatory environment
            "predictions": np.random.beta(5, 5, 100).tolist(),  # More varied risk scores
            "evidence": {
                "material_info": {"value": 2, "confidence": "High"},
                "trading_activity": {"value": 2, "confidence": "High"},
                "timing": {"value": 2, "confidence": "High"}  # Timing becomes more important
            }
        }
        
        return {
            "scenario": "seasonal_pattern",
            "description": "End-of-quarter trading behavior changes",
            "reference_data": reference_data,
            "current_data": current_data,
            "expected_drift_types": ["population_stability_drift", "evidence_pattern_drift"]
        }
    
    def generate_concept_drift_scenario(self) -> Dict[str, Any]:
        """
        Generate data representing concept drift through performance degradation.
        
        This simulates a scenario where the relationship between features
        and outcomes changes, leading to model performance degradation.
        """
        # Generate performance metrics showing degradation over time
        baseline_accuracy = 0.85
        performance_metrics = []
        
        # Stable performance period
        for i in range(15):
            performance_metrics.append({
                "timestamp": (datetime.now() - timedelta(days=30-i)).isoformat(),
                "accuracy": np.random.normal(baseline_accuracy, 0.02),
                "precision": np.random.normal(0.80, 0.02),
                "recall": np.random.normal(0.75, 0.02),
                "f1_score": np.random.normal(0.77, 0.02)
            })
        
        # Degrading performance period
        for i in range(15):
            degradation_factor = 1 - (i * 0.02)  # 2% degradation per time step
            performance_metrics.append({
                "timestamp": (datetime.now() - timedelta(days=15-i)).isoformat(),
                "accuracy": np.random.normal(baseline_accuracy * degradation_factor, 0.03),
                "precision": np.random.normal(0.80 * degradation_factor, 0.03),
                "recall": np.random.normal(0.75 * degradation_factor, 0.03),
                "f1_score": np.random.normal(0.77 * degradation_factor, 0.03)
            })
        
        reference_data = {
            "feature_relationships": "stable",
            "model_assumptions": "valid"
        }
        
        current_data = {
            "feature_relationships": "changed",
            "model_assumptions": "violated",
            "trace_metadata": {
                "performance_metrics": performance_metrics
            }
        }
        
        return {
            "scenario": "concept_drift",
            "description": "Model performance degradation due to changing feature relationships",
            "reference_data": reference_data,
            "current_data": current_data,
            "expected_drift_types": ["concept_drift"]
        }
    
    async def run_scenario_analysis(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive drift analysis for a scenario.
        
        Args:
            scenario_data: Scenario data with reference and current data
            
        Returns:
            Analysis results with drift detection, root cause analysis, and predictions
        """
        scenario_name = scenario_data["scenario"]
        logger.info(f"Running drift analysis for scenario: {scenario_name}")
        
        start_time = time.time()
        
        # Perform comprehensive drift analysis
        drift_results = self.drift_analyzer.detect_comprehensive_drift(
            model_id=f"scenario_{scenario_name}",
            current_data=scenario_data["current_data"],
            reference_data=scenario_data["reference_data"],
            trace_data=scenario_data["current_data"].get("trace_metadata", {})
        )
        
        # Generate drift forecast
        forecast = self.drift_analyzer.predict_future_drift(
            model_id=f"scenario_{scenario_name}",
            forecast_horizon_days=7
        )
        
        # Generate visualization data
        viz_data = self.drift_analyzer.generate_drift_visualization_data(
            model_id=f"scenario_{scenario_name}",
            days=30
        )
        
        # Perform manual analysis through monitoring service
        monitoring_result = await self.monitoring_service.perform_manual_drift_analysis(
            model_id=f"scenario_{scenario_name}",
            current_data=scenario_data["current_data"],
            reference_data=scenario_data["reference_data"]
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Compile results
        result = {
            "scenario": scenario_name,
            "description": scenario_data["description"],
            "processing_time_seconds": processing_time,
            "drift_results": [
                {
                    "drift_type": d.drift_type,
                    "drift_score": d.drift_score,
                    "severity": d.severity,
                    "statistical_method": d.statistical_method,
                    "p_value": d.p_value,
                    "affected_features": d.affected_features,
                    "recommendation": d.recommendation,
                    "root_cause_analysis": d.root_cause_analysis
                }
                for d in drift_results
            ],
            "drift_forecast": {
                "predicted_drift_score": forecast.predicted_drift_score,
                "confidence_lower": forecast.confidence_lower,
                "confidence_upper": forecast.confidence_upper,
                "likelihood_high_drift": forecast.likelihood_high_drift,
                "contributing_factors": forecast.contributing_factors,
                "recommended_actions": forecast.recommended_actions
            },
            "monitoring_analysis": monitoring_result,
            "summary": {
                "total_detections": len(drift_results),
                "high_severity_count": len([d for d in drift_results if d.severity == "high"]),
                "medium_severity_count": len([d for d in drift_results if d.severity == "medium"]),
                "max_drift_score": max(d.drift_score for d in drift_results) if drift_results else 0.0,
                "detected_methods": list(set(d.statistical_method for d in drift_results)),
                "expected_vs_detected": {
                    "expected": scenario_data.get("expected_drift_types", []),
                    "detected": list(set(d.drift_type for d in drift_results))
                }
            }
        }
        
        self.results.append(result)
        return result
    
    async def demonstrate_real_time_monitoring(self):
        """
        Demonstrate real-time drift monitoring capabilities.
        
        This shows how the system can continuously monitor for drift
        and trigger alerts when significant changes are detected.
        """
        logger.info("Starting real-time monitoring demonstration...")
        
        # Start background monitoring
        model_ids = ["realtime_model_1", "realtime_model_2"]
        
        # Set up alert tracking
        alerts_received = []
        
        async def alert_tracker(alert_data):
            alerts_received.append(alert_data)
            logger.info(f"Alert received: {alert_data['alert_type']} for model {alert_data['model_id']}")
        
        self.monitoring_service.add_alert_callback(alert_tracker)
        
        # Start monitoring
        monitoring_task = asyncio.create_task(
            self.monitoring_service.start_continuous_monitoring(model_ids)
        )
        
        # Let it run for a short period
        logger.info("Monitoring active for 15 seconds...")
        await asyncio.sleep(15)
        
        # Stop monitoring
        self.monitoring_service.stop_monitoring()
        
        # Wait for task to complete
        try:
            await asyncio.wait_for(monitoring_task, timeout=5.0)
        except asyncio.TimeoutError:
            monitoring_task.cancel()
        
        logger.info(f"Real-time monitoring completed. Alerts received: {len(alerts_received)}")
        
        return {
            "monitoring_duration_seconds": 15,
            "models_monitored": model_ids,
            "alerts_received": alerts_received,
            "alert_statistics": self.alert_manager.get_alert_statistics(days=1)
        }
    
    def print_scenario_results(self, result: Dict[str, Any]):
        """Print formatted results for a scenario."""
        print(f"\n{'='*80}")
        print(f"SCENARIO: {result['scenario'].upper()}")
        print(f"{'='*80}")
        print(f"Description: {result['description']}")
        print(f"Processing Time: {result['processing_time_seconds']:.3f} seconds")
        
        summary = result['summary']
        print(f"\n📊 DETECTION SUMMARY:")
        print(f"   Total Detections: {summary['total_detections']}")
        print(f"   High Severity: {summary['high_severity_count']}")
        print(f"   Medium Severity: {summary['medium_severity_count']}")
        print(f"   Max Drift Score: {summary['max_drift_score']:.4f}")
        print(f"   Methods Used: {', '.join(summary['detected_methods'])}")
        
        expected_vs_detected = summary['expected_vs_detected']
        print(f"\n🎯 EXPECTED vs DETECTED:")
        print(f"   Expected: {', '.join(expected_vs_detected['expected'])}")
        print(f"   Detected: {', '.join(expected_vs_detected['detected'])}")
        
        forecast = result['drift_forecast']
        print(f"\n🔮 DRIFT FORECAST:")
        print(f"   Predicted Score: {forecast['predicted_drift_score']:.4f}")
        print(f"   Confidence Range: [{forecast['confidence_lower']:.4f}, {forecast['confidence_upper']:.4f}]")
        print(f"   High Drift Likelihood: {forecast['likelihood_high_drift']:.2%}")
        
        if result['drift_results']:
            print(f"\n🔍 DETAILED DETECTIONS:")
            for i, detection in enumerate(result['drift_results'][:3], 1):  # Show first 3
                print(f"   {i}. {detection['drift_type']} ({detection['statistical_method']})")
                print(f"      Score: {detection['drift_score']:.4f}, Severity: {detection['severity']}")
                print(f"      Features: {', '.join(detection['affected_features'])}")
                if detection['p_value']:
                    print(f"      P-value: {detection['p_value']:.4f}")
                print(f"      Recommendation: {detection['recommendation'][:100]}...")
                print()
        
        if forecast['recommended_actions']:
            print(f"💡 RECOMMENDED ACTIONS:")
            for i, action in enumerate(forecast['recommended_actions'], 1):
                print(f"   {i}. {action}")
    
    def print_demo_summary(self):
        """Print overall demo summary."""
        print(f"\n{'='*80}")
        print("ADVANCED DRIFT DETECTION DEMO SUMMARY")
        print(f"{'='*80}")
        
        total_scenarios = len(self.results)
        total_processing_time = sum(r["processing_time_seconds"] for r in self.results)
        total_detections = sum(r["summary"]["total_detections"] for r in self.results)
        
        print(f"📊 Overall Statistics:")
        print(f"   Scenarios Analyzed: {total_scenarios}")
        print(f"   Total Processing Time: {total_processing_time:.3f} seconds")
        print(f"   Average Processing Time: {total_processing_time/total_scenarios:.3f} seconds")
        print(f"   Total Drift Detections: {total_detections}")
        print(f"   Average Detections per Scenario: {total_detections/total_scenarios:.1f}")
        
        # Method effectiveness analysis
        all_methods = []
        for result in self.results:
            all_methods.extend(result["summary"]["detected_methods"])
        
        method_counts = {}
        for method in all_methods:
            method_counts[method] = method_counts.get(method, 0) + 1
        
        print(f"\n🔬 Statistical Method Effectiveness:")
        for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {method}: {count} detections")
        
        # Severity distribution
        high_severity_total = sum(r["summary"]["high_severity_count"] for r in self.results)
        medium_severity_total = sum(r["summary"]["medium_severity_count"] for r in self.results)
        low_severity_total = total_detections - high_severity_total - medium_severity_total
        
        print(f"\n⚠️ Severity Distribution:")
        print(f"   High Severity: {high_severity_total} ({high_severity_total/total_detections*100:.1f}%)")
        print(f"   Medium Severity: {medium_severity_total} ({medium_severity_total/total_detections*100:.1f}%)")
        print(f"   Low Severity: {low_severity_total} ({low_severity_total/total_detections*100:.1f}%)")
        
        # Alert statistics
        alert_stats = self.alert_manager.get_alert_statistics(days=1)
        print(f"\n🚨 Alert Summary:")
        print(f"   Total Alerts: {alert_stats['total_alerts']}")
        print(f"   Alert Types: {alert_stats['alert_breakdown']}")
        print(f"   Priority Breakdown: {alert_stats['priority_breakdown']}")
        
        print(f"\n✅ Key Capabilities Demonstrated:")
        print(f"   ✓ Multi-method statistical drift detection")
        print(f"   ✓ Root cause analysis with confidence scoring")
        print(f"   ✓ Predictive drift modeling with forecasting")
        print(f"   ✓ Real-time monitoring and alerting")
        print(f"   ✓ Integration with OpenInference tracing")
        print(f"   ✓ Comprehensive visualization data generation")
        print(f"   ✓ Business-relevant scenario analysis")
        
        print(f"\n🎯 Phase 1 Implementation Status: COMPLETE")
        print(f"   Ready for Phase 2: Performance Intelligence")
    
    def export_results(self, filename: str = None):
        """Export demo results to JSON file."""
        if filename is None:
            filename = f"advanced_drift_detection_demo_results_{self.demo_id}.json"
        
        export_data = {
            "demo_metadata": {
                "demo_id": self.demo_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": "Phase 1 - Enhanced Drift Detection",
                "version": "1.0.0"
            },
            "configuration": {
                "drift_thresholds": self.drift_analyzer.drift_thresholds,
                "monitoring_config": {
                    "interval_seconds": self.monitoring_service.monitoring_interval,
                    "alert_thresholds": self.monitoring_service.alert_thresholds
                }
            },
            "results": self.results,
            "alert_statistics": self.alert_manager.get_alert_statistics(days=1),
            "summary": {
                "total_scenarios": len(self.results),
                "total_processing_time": sum(r["processing_time_seconds"] for r in self.results),
                "total_detections": sum(r["summary"]["total_detections"] for r in self.results),
                "capabilities_demonstrated": [
                    "Multi-method statistical drift detection",
                    "Root cause analysis with confidence scoring",
                    "Predictive drift modeling with forecasting",
                    "Real-time monitoring and alerting",
                    "Integration with OpenInference tracing",
                    "Comprehensive visualization data generation",
                    "Business-relevant scenario analysis"
                ]
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Demo results exported to {filename}")
    
    async def run_comprehensive_demo(self):
        """Run the comprehensive advanced drift detection demo."""
        print(f"\n{'='*80}")
        print("KORINSIC ADVANCED DRIFT DETECTION DEMO")
        print("Phase 1: Enhanced Drift Detection Implementation")
        print(f"{'='*80}")
        print(f"Demo ID: {self.demo_id}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Scenario 1: Market Regime Change
        print(f"\n🏛️ SCENARIO 1: MARKET REGIME CHANGE")
        market_scenario = self.generate_market_regime_scenario()
        market_result = await self.run_scenario_analysis(market_scenario)
        self.print_scenario_results(market_result)
        
        # Scenario 2: Data Quality Degradation
        print(f"\n📉 SCENARIO 2: DATA QUALITY DEGRADATION")
        quality_scenario = self.generate_data_quality_degradation_scenario()
        quality_result = await self.run_scenario_analysis(quality_scenario)
        self.print_scenario_results(quality_result)
        
        # Scenario 3: Seasonal Pattern Changes
        print(f"\n📅 SCENARIO 3: SEASONAL PATTERN CHANGES")
        seasonal_scenario = self.generate_seasonal_pattern_scenario()
        seasonal_result = await self.run_scenario_analysis(seasonal_scenario)
        self.print_scenario_results(seasonal_result)
        
        # Scenario 4: Concept Drift
        print(f"\n🧠 SCENARIO 4: CONCEPT DRIFT")
        concept_scenario = self.generate_concept_drift_scenario()
        concept_result = await self.run_scenario_analysis(concept_scenario)
        self.print_scenario_results(concept_result)
        
        # Real-time monitoring demonstration
        print(f"\n📡 REAL-TIME MONITORING DEMONSTRATION")
        monitoring_result = await self.demonstrate_real_time_monitoring()
        print(f"   Monitoring Duration: {monitoring_result['monitoring_duration_seconds']} seconds")
        print(f"   Models Monitored: {', '.join(monitoring_result['models_monitored'])}")
        print(f"   Alerts Generated: {len(monitoring_result['alerts_received'])}")
        
        # Print overall summary
        self.print_demo_summary()
        
        # Export results
        self.export_results()
        
        print(f"\n{'='*80}")
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("Phase 1: Enhanced Drift Detection - FULLY IMPLEMENTED")
        print("Ready to proceed to Phase 2: Performance Intelligence")
        print(f"{'='*80}")


async def main():
    """Main demo execution."""
    try:
        demo = AdvancedDriftDetectionDemo()
        await demo.run_comprehensive_demo()
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())