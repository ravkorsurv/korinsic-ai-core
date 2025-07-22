#!/usr/bin/env python3
"""
OpenInference Integration Demo for Korinsic Surveillance Platform

This script demonstrates the comprehensive OpenInference observability
integration with Bayesian inference models for market abuse detection.
"""

import sys
import os
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.utils.openinference_tracer import initialize_tracing, get_tracer
from src.core.engines.enhanced_bayesian_engine import EnhancedBayesianEngine
from src.utils.logger import setup_logger

logger = setup_logger()


class OpenInferenceDemo:
    """
    Demonstration of OpenInference integration with Korinsic surveillance platform.
    
    This demo shows:
    - Tracing setup and configuration
    - Enhanced Bayesian model inference with observability
    - Comprehensive trace data collection
    - Performance monitoring
    - Regulatory compliance features
    """
    
    def __init__(self):
        """Initialize the demo with tracing configuration."""
        self.demo_id = str(uuid.uuid4())
        self.results = []
        
        # Configure OpenInference tracing
        tracing_config = {
            'enabled': True,
            'console_exporter': True,  # Show traces in console for demo
            'otlp_endpoint': os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT'),
            'phoenix_endpoint': os.getenv('PHOENIX_ENDPOINT')
        }
        
        logger.info(f"Starting OpenInference Demo {self.demo_id}")
        
        # Initialize tracing
        initialize_tracing(tracing_config)
        self.tracer = get_tracer()
        
        # Initialize enhanced Bayesian engine
        self.engine = EnhancedBayesianEngine(tracing_config)
        
        logger.info("OpenInference integration initialized successfully")
    
    def generate_sample_trading_data(self, scenario: str) -> Dict[str, Any]:
        """
        Generate sample trading data for different risk scenarios.
        
        Args:
            scenario: Risk scenario ('low_risk', 'medium_risk', 'high_risk', 'insider_dealing', 'spoofing')
            
        Returns:
            Sample trading data
        """
        base_time = datetime.utcnow() - timedelta(hours=2)
        
        if scenario == 'high_risk_insider':
            return {
                "trades": [
                    {
                        "id": f"trade_{i}",
                        "timestamp": (base_time + timedelta(minutes=i*5)).isoformat(),
                        "volume": 5000 + i * 1000,
                        "value": (5000 + i * 1000) * 50,
                        "price": 50.0 + i * 0.5,
                        "symbol": "AAPL",
                        "trader_id": "trader_001"
                    }
                    for i in range(5)
                ],
                "orders": [
                    {
                        "id": f"order_{i}",
                        "timestamp": (base_time + timedelta(minutes=i*5-1)).isoformat(),
                        "quantity": 5000 + i * 1000,
                        "price": 50.0 + i * 0.5,
                        "side": "BUY",
                        "trader_id": "trader_001"
                    }
                    for i in range(5)
                ],
                "material_events": [
                    {
                        "event_type": "earnings_announcement",
                        "timestamp": (base_time - timedelta(minutes=30)).isoformat(),
                        "impact": "positive",
                        "symbol": "AAPL"
                    }
                ],
                "trader_info": {
                    "trader_id": "trader_001",
                    "access_level": "high",
                    "department": "corporate_finance",
                    "recent_meetings": ["earnings_preparation"]
                }
            }
        
        elif scenario == 'spoofing_pattern':
            return {
                "trades": [
                    {
                        "id": f"trade_{i}",
                        "timestamp": (base_time + timedelta(seconds=i*30)).isoformat(),
                        "volume": 100,
                        "value": 100 * 50,
                        "price": 50.0,
                        "symbol": "MSFT",
                        "trader_id": "trader_002"
                    }
                    for i in range(2)
                ],
                "orders": [
                    # Large orders that get cancelled
                    {
                        "id": f"large_order_{i}",
                        "timestamp": (base_time + timedelta(seconds=i*60)).isoformat(),
                        "quantity": 10000,
                        "price": 50.0 + 0.1,
                        "side": "BUY",
                        "status": "CANCELLED",
                        "trader_id": "trader_002"
                    }
                    for i in range(10)
                ] + [
                    # Small executed orders
                    {
                        "id": f"small_order_{i}",
                        "timestamp": (base_time + timedelta(seconds=i*30+15)).isoformat(),
                        "quantity": 100,
                        "price": 50.0,
                        "side": "BUY",
                        "status": "EXECUTED",
                        "trader_id": "trader_002"
                    }
                    for i in range(2)
                ],
                "material_events": [],
                "trader_info": {
                    "trader_id": "trader_002",
                    "access_level": "standard",
                    "department": "trading_desk"
                }
            }
        
        else:  # low_risk scenario
            return {
                "trades": [
                    {
                        "id": f"trade_{i}",
                        "timestamp": (base_time + timedelta(minutes=i*15)).isoformat(),
                        "volume": 100 + i * 10,
                        "value": (100 + i * 10) * 50,
                        "price": 50.0,
                        "symbol": "GOOGL",
                        "trader_id": "trader_003"
                    }
                    for i in range(3)
                ],
                "orders": [
                    {
                        "id": f"order_{i}",
                        "timestamp": (base_time + timedelta(minutes=i*15-1)).isoformat(),
                        "quantity": 100 + i * 10,
                        "price": 50.0,
                        "side": "BUY",
                        "trader_id": "trader_003"
                    }
                    for i in range(3)
                ],
                "material_events": [],
                "trader_info": {
                    "trader_id": "trader_003",
                    "access_level": "standard",
                    "department": "portfolio_management"
                }
            }
    
    def run_risk_analysis_demo(self, scenario: str) -> Dict[str, Any]:
        """
        Run a risk analysis demo with comprehensive tracing.
        
        Args:
            scenario: Risk scenario to analyze
            
        Returns:
            Analysis results with tracing metadata
        """
        logger.info(f"Running risk analysis demo for scenario: {scenario}")
        
        # Generate sample data
        trading_data = self.generate_sample_trading_data(scenario)
        
        # Perform risk analysis with tracing
        start_time = time.time()
        
        # Insider dealing analysis
        insider_result = self.engine.calculate_insider_dealing_risk(trading_data)
        
        # Spoofing analysis  
        spoofing_result = self.engine.calculate_spoofing_risk(trading_data)
        
        # Latent intent analysis (if high risk)
        if insider_result.get("overall_score", 0) > 0.6:
            latent_intent_result = self.engine.calculate_insider_dealing_risk_with_latent_intent(trading_data)
        else:
            latent_intent_result = None
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Compile results
        demo_result = {
            "scenario": scenario,
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_seconds": processing_time,
            "input_data_summary": {
                "trade_count": len(trading_data.get("trades", [])),
                "order_count": len(trading_data.get("orders", [])),
                "material_events_count": len(trading_data.get("material_events", []))
            },
            "risk_analysis": {
                "insider_dealing": insider_result,
                "spoofing": spoofing_result,
                "latent_intent": latent_intent_result
            },
            "overall_assessment": self._calculate_overall_assessment(
                insider_result, spoofing_result, latent_intent_result
            ),
            "tracing_session": self.engine.get_tracing_summary()
        }
        
        self.results.append(demo_result)
        
        logger.info(f"Analysis completed in {processing_time:.3f}s - Overall risk: {demo_result['overall_assessment']['risk_level']}")
        
        return demo_result
    
    def _calculate_overall_assessment(
        self, 
        insider_result: Dict[str, Any], 
        spoofing_result: Dict[str, Any],
        latent_intent_result: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate overall risk assessment."""
        insider_score = insider_result.get("overall_score", 0)
        spoofing_score = spoofing_result.get("overall_score", 0)
        
        # Use latent intent score if available and higher
        if latent_intent_result:
            latent_score = latent_intent_result.get("overall_score", 0)
            if latent_score > insider_score:
                insider_score = latent_score
        
        # Calculate weighted overall score
        overall_score = (insider_score * 0.6) + (spoofing_score * 0.4)
        
        # Determine risk level
        if overall_score >= 0.8:
            risk_level = "HIGH"
            action_required = "IMMEDIATE_INVESTIGATION"
        elif overall_score >= 0.5:
            risk_level = "MEDIUM"
            action_required = "ENHANCED_MONITORING"
        else:
            risk_level = "LOW"
            action_required = "STANDARD_MONITORING"
        
        return {
            "overall_score": overall_score,
            "risk_level": risk_level,
            "action_required": action_required,
            "contributing_factors": {
                "insider_dealing_score": insider_score,
                "spoofing_score": spoofing_score
            }
        }
    
    def run_comprehensive_demo(self):
        """Run a comprehensive demonstration of OpenInference integration."""
        logger.info("=" * 80)
        logger.info("KORINSIC OPENINFERENCE INTEGRATION DEMO")
        logger.info("=" * 80)
        
        scenarios = [
            ("low_risk", "Low Risk Trading Pattern"),
            ("spoofing_pattern", "Potential Spoofing Pattern"),
            ("high_risk_insider", "High Risk Insider Dealing Pattern")
        ]
        
        for scenario_id, scenario_name in scenarios:
            logger.info(f"\n--- {scenario_name} ---")
            
            try:
                result = self.run_risk_analysis_demo(scenario_id)
                self._print_analysis_summary(result)
                
                # Small delay between scenarios
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in scenario {scenario_id}: {e}")
        
        # Print overall demo summary
        self._print_demo_summary()
    
    def _print_analysis_summary(self, result: Dict[str, Any]):
        """Print a summary of analysis results."""
        assessment = result["overall_assessment"]
        tracing = result["tracing_session"]
        
        print(f"  📊 Overall Risk Score: {assessment['overall_score']:.2f}")
        print(f"  🚨 Risk Level: {assessment['risk_level']}")
        print(f"  ⚡ Processing Time: {result['processing_time_seconds']:.3f}s")
        print(f"  🔍 Tracing Session: {tracing['session_id'][:8]}...")
        print(f"  📈 Insider Dealing: {assessment['contributing_factors']['insider_dealing_score']:.2f}")
        print(f"  🎯 Spoofing: {assessment['contributing_factors']['spoofing_score']:.2f}")
        
        if assessment['risk_level'] == 'HIGH':
            print(f"  ⚠️  Action Required: {assessment['action_required']}")
    
    def _print_demo_summary(self):
        """Print overall demo summary."""
        logger.info("\n" + "=" * 80)
        logger.info("DEMO SUMMARY")
        logger.info("=" * 80)
        
        total_scenarios = len(self.results)
        total_processing_time = sum(r["processing_time_seconds"] for r in self.results)
        avg_processing_time = total_processing_time / total_scenarios if total_scenarios > 0 else 0
        
        high_risk_count = sum(1 for r in self.results if r["overall_assessment"]["risk_level"] == "HIGH")
        medium_risk_count = sum(1 for r in self.results if r["overall_assessment"]["risk_level"] == "MEDIUM")
        low_risk_count = sum(1 for r in self.results if r["overall_assessment"]["risk_level"] == "LOW")
        
        print(f"📊 Total Scenarios Analyzed: {total_scenarios}")
        print(f"⚡ Total Processing Time: {total_processing_time:.3f}s")
        print(f"�� Average Processing Time: {avg_processing_time:.3f}s")
        print(f"🔴 High Risk Scenarios: {high_risk_count}")
        print(f"🟡 Medium Risk Scenarios: {medium_risk_count}")
        print(f"🟢 Low Risk Scenarios: {low_risk_count}")
        
        print(f"\n🔍 OpenInference Tracing:")
        print(f"   - Tracer Enabled: {self.tracer.enabled}")
        print(f"   - Demo Session: {self.demo_id}")
        print(f"   - Engine Session: {self.engine.session_id}")
        
        print(f"\n📋 Key Features Demonstrated:")
        print(f"   ✅ Bayesian model tracing")
        print(f"   ✅ Performance monitoring")
        print(f"   ✅ Evidence sufficiency tracking")
        print(f"   ✅ Multi-model risk analysis")
        print(f"   ✅ Comprehensive audit trail")
        
        logger.info("Demo completed successfully!")
    
    def export_results(self, filename: str = None):
        """Export demo results to JSON file."""
        if filename is None:
            filename = f"openinference_demo_results_{self.demo_id[:8]}.json"
        
        export_data = {
            "demo_metadata": {
                "demo_id": self.demo_id,
                "timestamp": datetime.utcnow().isoformat(),
                "openinference_enabled": self.tracer.enabled,
                "engine_session": self.engine.session_id
            },
            "results": self.results,
            "summary": {
                "total_scenarios": len(self.results),
                "total_processing_time": sum(r["processing_time_seconds"] for r in self.results),
                "risk_level_distribution": {
                    "HIGH": sum(1 for r in self.results if r["overall_assessment"]["risk_level"] == "HIGH"),
                    "MEDIUM": sum(1 for r in self.results if r["overall_assessment"]["risk_level"] == "MEDIUM"),
                    "LOW": sum(1 for r in self.results if r["overall_assessment"]["risk_level"] == "LOW")
                }
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Demo results exported to {filename}")


def main():
    """Main demo execution."""
    try:
        # Create and run demo
        demo = OpenInferenceDemo()
        demo.run_comprehensive_demo()
        
        # Export results
        demo.export_results()
        
        print("\n" + "=" * 80)
        print("🎉 OpenInference Demo completed successfully!")
        print("Check the console output above for trace information.")
        print("If you have Phoenix or Jaeger running, check those UIs for detailed traces.")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
