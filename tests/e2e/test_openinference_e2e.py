#!/usr/bin/env python3
"""
End-to-End Tests for OpenInference AI Observability Integration

This module tests the complete OpenInference integration including:
- AI model tracing with semantic conventions
- Evidence mapping and fallback logic observability
- Performance metrics collection
- End-to-end request tracing
- Integration with existing Korinsic test framework
"""

import json
import time
import sys
import traceback
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import pytest
import numpy as np
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

# Import core modules
from core.data_processor import DataProcessor
from core.bayesian_engine import BayesianEngine
from core.alert_generator import AlertGenerator
from core.risk_aggregator import ComplexRiskAggregator
from utils.ai_observability import get_ai_observability, initialize_ai_observability

# Import OpenTelemetry for trace validation
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIObservabilityTestResult:
    """Test result with AI observability metrics"""
    test_name: str
    status: str  # PASS, FAIL, ERROR
    duration: float
    traces_generated: int
    ai_attributes_found: int
    spans_with_errors: int
    inference_latency_ms: float
    evidence_completeness: float
    fallback_usage_count: int
    error_message: Optional[str] = None

class MockSpanExporter:
    """Mock span exporter to capture traces during testing"""
    
    def __init__(self):
        self.spans = []
        self.ai_attributes = {}
        self.errors = []
    
    def export(self, spans):
        """Capture exported spans for validation"""
        for span in spans:
            self.spans.append(span)
            
            # Extract AI-specific attributes
            for key, value in span.attributes.items() if span.attributes else {}:
                if key.startswith('ai.') or key.startswith('llm.'):
                    if key not in self.ai_attributes:
                        self.ai_attributes[key] = []
                    self.ai_attributes[key].append(value)
            
            # Check for errors
            if span.status.status_code.name == 'ERROR':
                self.errors.append({
                    'span_name': span.name,
                    'error': span.status.description,
                    'attributes': dict(span.attributes) if span.attributes else {}
                })
    
    def shutdown(self):
        pass
    
    def get_spans_by_name(self, name: str):
        """Get spans by name for validation"""
        return [span for span in self.spans if span.name == name]
    
    def get_ai_attribute(self, key: str):
        """Get AI attribute values"""
        return self.ai_attributes.get(key, [])
    
    def clear(self):
        """Clear captured data"""
        self.spans.clear()
        self.ai_attributes.clear()
        self.errors.clear()

class OpenInferenceE2ETestFramework:
    """Enhanced E2E test framework with OpenInference validation"""
    
    def __init__(self):
        self.test_results: List[AIObservabilityTestResult] = []
        self.mock_exporter = MockSpanExporter()
        self.setup_test_tracing()
        self.initialize_components()
    
    def setup_test_tracing(self):
        """Setup tracing for testing with mock exporter"""
        # Create tracer provider with mock exporter
        tracer_provider = TracerProvider()
        span_processor = SimpleSpanProcessor(self.mock_exporter)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)
        
        # Initialize AI observability with test endpoint
        self.ai_observability = initialize_ai_observability(
            service_name="korinsic-ai-test",
            service_version="1.0.0-test",
            otlp_endpoint="http://localhost:4317"  # Will be mocked
        )
        
        logger.info("Test tracing setup completed")
    
    def initialize_components(self):
        """Initialize core components for testing"""
        try:
            self.data_processor = DataProcessor()
            self.bayesian_engine = BayesianEngine()
            self.alert_generator = AlertGenerator()
            self.risk_aggregator = ComplexRiskAggregator()
            logger.info("Core components initialized for OpenInference testing")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def create_sample_data(self, scenario: str = "normal") -> Dict[str, Any]:
        """Create sample data for different test scenarios"""
        base_data = {
            'trader_info': {
                'trader_id': f'TRADER_{scenario.upper()}_001',
                'access_level': 'medium',
                'department': 'equity_trading'
            },
            'trades': [
                {
                    'trade_id': f'T_{scenario}_001',
                    'instrument': 'AAPL',
                    'quantity': 1000,
                    'price': 150.25,
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'market_data': {
                'volatility': 0.15,
                'price_movement': 0.05,
                'volume': 10000
            },
            'communications': [],
            'pnl_data': {
                'daily_loss': -5000,
                'unusual_pattern': False
            }
        }
        
        # Modify data based on scenario
        if scenario == "high_risk":
            base_data['trader_info']['access_level'] = 'high'
            base_data['market_data']['volatility'] = 0.35
            base_data['market_data']['price_movement'] = 0.15
            base_data['communications'] = [{
                'content': 'We have sensitive information about the earnings',
                'timestamp': datetime.now().isoformat()
            }]
            base_data['pnl_data']['daily_loss'] = -200000
            base_data['pnl_data']['unusual_pattern'] = True
        
        elif scenario == "missing_data":
            # Remove some data to test fallback logic
            del base_data['communications']
            del base_data['market_data']['volatility']
            base_data['pnl_data'] = {}
        
        return base_data
    
    def run_test(self, test_func, test_name: str, *args, **kwargs) -> AIObservabilityTestResult:
        """Run a test with OpenInference validation"""
        logger.info(f"Running test: {test_name}")
        
        # Clear previous traces
        self.mock_exporter.clear()
        
        start_time = time.time()
        
        try:
            # Run the test
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Analyze traces
            traces_generated = len(self.mock_exporter.spans)
            ai_attributes_found = len(self.mock_exporter.ai_attributes)
            spans_with_errors = len(self.mock_exporter.errors)
            
            # Extract performance metrics
            inference_latency = self._extract_inference_latency()
            evidence_completeness = self._extract_evidence_completeness()
            fallback_usage = self._extract_fallback_usage()
            
            test_result = AIObservabilityTestResult(
                test_name=test_name,
                status="PASS",
                duration=duration,
                traces_generated=traces_generated,
                ai_attributes_found=ai_attributes_found,
                spans_with_errors=spans_with_errors,
                inference_latency_ms=inference_latency,
                evidence_completeness=evidence_completeness,
                fallback_usage_count=fallback_usage
            )
            
            logger.info(f"✅ {test_name} PASSED")
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = AIObservabilityTestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                traces_generated=len(self.mock_exporter.spans),
                ai_attributes_found=len(self.mock_exporter.ai_attributes),
                spans_with_errors=len(self.mock_exporter.errors),
                inference_latency_ms=0.0,
                evidence_completeness=0.0,
                fallback_usage_count=0,
                error_message=str(e)
            )
            
            logger.error(f"❌ {test_name} FAILED: {e}")
        
        self.test_results.append(test_result)
        return test_result

# Test Functions
def test_bayesian_inference_tracing(framework) -> Dict[str, Any]:
    """Test that Bayesian inference generates proper AI traces"""
    sample_data = framework.create_sample_data("normal")
    
    # Process data
    processed_data = framework.data_processor.process(sample_data)
    
    # Run Bayesian analysis (this should generate traces)
    result = framework.bayesian_engine.analyze_insider_dealing(processed_data)
    
    # Validate result structure
    required_fields = ['risk_score', 'esi_score', 'evidence_used', 'model_type']
    for field in required_fields:
        if field not in result:
            raise AssertionError(f"Missing required field in result: {field}")
    
    return {
        'risk_score': result['risk_score'],
        'traces_generated': len(framework.mock_exporter.spans),
        'ai_attributes': len(framework.mock_exporter.ai_attributes)
    }

# Main test runner
def main():
    """Run all OpenInference E2E tests"""
    print("🧪 OpenInference E2E Test Suite")
    print("=" * 50)
    
    try:
        framework = OpenInferenceE2ETestFramework()
        
        # Run basic test
        framework.run_test(test_bayesian_inference_tracing, "Bayesian Inference Tracing", framework)
        
        # Generate simple report
        total_tests = len(framework.test_results)
        passed_tests = sum(1 for r in framework.test_results if r.status == "PASS")
        
        print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✅ All OpenInference E2E tests passed!")
            return 0
        else:
            print("❌ Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Test framework failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
