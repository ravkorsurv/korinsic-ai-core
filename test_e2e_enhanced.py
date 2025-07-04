#!/usr/bin/env python3
"""
Enhanced E2E Testing Framework for Kor AI Core
Features:
- Regression testing with baseline comparisons
- Comprehensive error reporting and logging
- CI/CD ready with exit codes and structured outputs
- Performance benchmarking
- Data validation and integrity checks
- Test result aggregation and reporting
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

# Import core modules
from src.core.data_processor import DataProcessor
from src.core.bayesian_engine import BayesianEngine
from src.core.alert_generator import AlertGenerator
from src.core.risk_aggregator import ComplexRiskAggregator
from src.core.evidence_mapper import map_evidence
from src.core.fallback_logic import apply_fallback_evidence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('e2e_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Structured test result data"""
    test_name: str
    status: str  # PASS, FAIL, ERROR, SKIP
    duration: float
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    performance_metrics: Optional[Dict[str, float]] = None
    data_validation: Optional[Dict[str, Any]] = None
    regression_score: Optional[float] = None
    baseline_deviation: Optional[float] = None

@dataclass
class TestSuite:
    """Test suite configuration and results"""
    name: str
    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    total_duration: float
    results: List[TestResult]
    performance_baseline: Optional[Dict[str, float]] = None

class E2ETestFramework:
    """Enhanced E2E testing framework with regression testing and CI/CD support"""
    
    def __init__(self, baseline_file: str = "test_baselines.json"):
        self.baseline_file = baseline_file
        self.test_results: List[TestResult] = []
        self.performance_baselines = self._load_baselines()
        self.start_time = time.time()
        
        # Initialize core components
        try:
            self.data_processor = DataProcessor()
            self.bayesian_engine = BayesianEngine()
            self.alert_generator = AlertGenerator()
            self.risk_aggregator = ComplexRiskAggregator()
            logger.info("Core components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize core components: {e}")
            raise
    
    def _load_baselines(self) -> Dict[str, Any]:
        """Load baseline data for regression testing"""
        try:
            if Path(self.baseline_file).exists():
                with open(self.baseline_file, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Baseline file {self.baseline_file} not found. Creating new baseline.")
                return {}
        except Exception as e:
            logger.error(f"Error loading baselines: {e}")
            return {}
    
    def _save_baselines(self):
        """Save current test results as new baselines"""
        try:
            baseline_data = {
                'timestamp': datetime.now().isoformat(),
                'performance_metrics': {},
                'regression_scores': {}
            }
            
            for result in self.test_results:
                if result.performance_metrics:
                    baseline_data['performance_metrics'][result.test_name] = result.performance_metrics
                if result.regression_score is not None:
                    baseline_data['regression_scores'][result.test_name] = result.regression_score
            
            with open(self.baseline_file, 'w') as f:
                json.dump(baseline_data, f, indent=2)
            logger.info(f"Baselines saved to {self.baseline_file}")
        except Exception as e:
            logger.error(f"Error saving baselines: {e}")
    
    def _validate_data_integrity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data integrity and structure"""
        validation_result = {
            'is_valid': True,
            'missing_fields': [],
            'type_errors': [],
            'range_errors': [],
            'warnings': []
        }
        
        required_fields = ['trades', 'market_data', 'hr_data', 'communications']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                validation_result['missing_fields'].append(field)
                validation_result['is_valid'] = False
        
        # Check data types and ranges
        if 'trades' in data:
            trades = data['trades']
            if not isinstance(trades, list):
                validation_result['type_errors'].append('trades should be a list')
                validation_result['is_valid'] = False
            
            for trade in trades[:10]:  # Sample first 10 trades
                if not isinstance(trade, dict):
                    validation_result['type_errors'].append('trade should be a dict')
                    break
                
                if 'amount' in trade and not isinstance(trade['amount'], (int, float)):
                    validation_result['type_errors'].append('trade amount should be numeric')
                
                if 'amount' in trade and trade['amount'] < 0:
                    validation_result['range_errors'].append('trade amount should be positive')
        
        return validation_result
    
    def _calculate_regression_score(self, test_name: str, current_metrics: Dict[str, float]) -> float:
        """Calculate regression score against baseline"""
        if test_name not in self.performance_baselines.get('performance_metrics', {}):
            return 0.0  # No baseline to compare against
        
        baseline = self.performance_baselines['performance_metrics'][test_name]
        total_deviation = 0.0
        metric_count = 0
        
        for metric, current_value in current_metrics.items():
            if metric in baseline:
                baseline_value = baseline[metric]
                if baseline_value > 0:
                    deviation = abs(current_value - baseline_value) / baseline_value
                    total_deviation += deviation
                    metric_count += 1
        
        return total_deviation / metric_count if metric_count > 0 else 0.0
    
    def run_test(self, test_func, test_name: str, *args, **kwargs) -> TestResult:
        """Run a single test with comprehensive error handling and metrics"""
        start_time = time.time()
        result = TestResult(
            test_name=test_name,
            status="PASS",
            duration=0.0
        )
        
        try:
            # Run the test
            test_output = test_func(*args, **kwargs)
            result.duration = time.time() - start_time
            
            # Collect performance metrics
            result.performance_metrics = {
                'execution_time': result.duration,
                'memory_usage': self._get_memory_usage(),
                'cpu_usage': self._get_cpu_usage()
            }
            
            # Calculate regression score
            result.regression_score = self._calculate_regression_score(test_name, result.performance_metrics)
            
            # Determine if regression is significant (>10% deviation)
            if result.regression_score > 0.1:
                result.status = "FAIL"
                result.error_message = f"Performance regression detected: {result.regression_score:.2%} deviation from baseline"
            
            logger.info(f"Test {test_name} completed successfully in {result.duration:.3f}s")
            
        except Exception as e:
            result.status = "ERROR"
            result.duration = time.time() - start_time
            result.error_message = str(e)
            result.error_traceback = traceback.format_exc()
            logger.error(f"Test {test_name} failed: {e}")
        
        self.test_results.append(result)
        return result
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage (simplified)"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage (simplified)"""
        try:
            import psutil
            return psutil.cpu_percent()
        except ImportError:
            return 0.0
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.status == "PASS")
        failed = sum(1 for r in self.test_results if r.status == "FAIL")
        errors = sum(1 for r in self.test_results if r.status == "ERROR")
        skipped = sum(1 for r in self.test_results if r.status == "SKIP")
        
        total_duration = sum(r.duration for r in self.test_results)
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'skipped': skipped,
                'success_rate': (passed / total_tests * 100) if total_tests > 0 else 0,
                'total_duration': total_duration,
                'timestamp': datetime.now().isoformat()
            },
            'performance_analysis': self._analyze_performance(),
            'regression_analysis': self._analyze_regressions(),
            'detailed_results': [asdict(r) for r in self.test_results],
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics across all tests"""
        if not self.test_results:
            return {}
        
        execution_times = [r.performance_metrics['execution_time'] for r in self.test_results if r.performance_metrics]
        
        return {
            'avg_execution_time': np.mean(execution_times) if execution_times else 0,
            'max_execution_time': max(execution_times) if execution_times else 0,
            'min_execution_time': min(execution_times) if execution_times else 0,
            'std_execution_time': np.std(execution_times) if execution_times else 0
        }
    
    def _analyze_regressions(self) -> Dict[str, Any]:
        """Analyze regression scores"""
        regression_scores = [r.regression_score for r in self.test_results if r.regression_score is not None]
        
        return {
            'avg_regression_score': np.mean(regression_scores) if regression_scores else 0,
            'max_regression_score': max(regression_scores) if regression_scores else 0,
            'tests_with_regression': sum(1 for r in self.test_results if r.regression_score and r.regression_score > 0.1)
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check success rate
        success_rate = sum(1 for r in self.test_results if r.status == "PASS") / len(self.test_results)
        if success_rate < 0.9:
            recommendations.append("Low test success rate detected. Review failing tests and fix issues.")
        
        # Check for performance regressions
        regressions = [r for r in self.test_results if r.regression_score and r.regression_score > 0.1]
        if regressions:
            recommendations.append(f"{len(regressions)} tests show performance regression. Investigate performance issues.")
        
        # Check execution time
        avg_time = np.mean([r.duration for r in self.test_results])
        if avg_time > 5.0:  # More than 5 seconds average
            recommendations.append("High average execution time detected. Consider performance optimization.")
        
        return recommendations
    
    def save_report(self, filename: str = "e2e_test_report.json"):
        """Save test report to file"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Test report saved to {filename}")
        return report
    
    def print_summary(self):
        """Print test summary to console"""
        report = self.generate_report()
        summary = report['summary']
        
        print("\n" + "="*60)
        print("E2E TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} (green)")
        print(f"Failed: {summary['failed']} (red)")
        print(f"Errors: {summary['errors']} (red)")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        print(f"Average Duration: {summary['total_duration']/summary['total_tests']:.2f}s per test")
        
        if report['recommendations']:
            print("\nRECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
        
        print("="*60)

# Test data generators
def generate_test_data(scenario: str = "normal") -> Dict[str, Any]:
    """Generate test data for different scenarios"""
    if scenario == "high_risk":
        return {
            "trades": [
                {"trader_id": "T001", "amount": 1000000, "timestamp": "2024-01-15T10:30:00Z", "direction": "buy"},
                {"trader_id": "T001", "amount": 500000, "timestamp": "2024-01-15T11:00:00Z", "direction": "sell"}
            ],
            "market_data": {
                "price_change": 0.15,
                "volume_spike": True,
                "volatility": 0.25
            },
            "hr_data": {
                "employee_id": "T001",
                "access_level": "high",
                "department": "trading"
            },
            "communications": [
                {"from": "T001", "to": "external", "content": "sensitive info", "timestamp": "2024-01-15T09:00:00Z"}
            ],
            "pnl_data": {
                "daily_loss": -500000,
                "unusual_pattern": True
            }
        }
    else:
        return {
            "trades": [
                {"trader_id": "T002", "amount": 50000, "timestamp": "2024-01-15T10:30:00Z", "direction": "buy"}
            ],
            "market_data": {
                "price_change": 0.02,
                "volume_spike": False,
                "volatility": 0.05
            },
            "hr_data": {
                "employee_id": "T002",
                "access_level": "low",
                "department": "operations"
            },
            "communications": [],
            "pnl_data": {
                "daily_loss": -5000,
                "unusual_pattern": False
            }
        }

# Test functions
def test_data_processing_pipeline(framework: E2ETestFramework) -> Dict[str, Any]:
    """Test the complete data processing pipeline"""
    test_data = generate_test_data("normal")
    
    # Validate input data
    validation = framework._validate_data_integrity(test_data)
    if not validation['is_valid']:
        raise ValueError(f"Data validation failed: {validation}")
    
    # Process data
    processed_data = framework.data_processor.process_data(test_data)
    
    # Validate processed data
    if not processed_data:
        raise ValueError("Data processing returned empty result")
    
    return {
        'input_validation': validation,
        'processed_data': processed_data,
        'processing_success': True
    }

def test_bayesian_inference(framework: E2ETestFramework) -> Dict[str, Any]:
    """Test Bayesian inference with different scenarios"""
    results = {}
    
    # Test normal scenario
    normal_data = generate_test_data("normal")
    processed_normal = framework.data_processor.process_data(normal_data)
    normal_risk = framework.bayesian_engine.calculate_insider_dealing_risk(processed_normal)
    results['normal_scenario'] = normal_risk
    
    # Test high-risk scenario
    high_risk_data = generate_test_data("high_risk")
    processed_high_risk = framework.data_processor.process_data(high_risk_data)
    high_risk_result = framework.bayesian_engine.calculate_insider_dealing_risk(processed_high_risk)
    results['high_risk_scenario'] = high_risk_result
    
    # Validate risk scores
    if high_risk_result['overall_score'] <= normal_risk['overall_score']:
        raise ValueError("High-risk scenario should have higher risk score than normal scenario")
    
    return results

def test_alert_generation(framework: E2ETestFramework) -> Dict[str, Any]:
    """Test alert generation with various risk levels"""
    test_data = generate_test_data("high_risk")
    processed_data = framework.data_processor.process_data(test_data)
    risk_result = framework.bayesian_engine.calculate_insider_dealing_risk(processed_data)
    
    # Generate alert
    alert = framework.alert_generator.generate_alert(
        risk_result, 
        processed_data, 
        "insider_dealing"
    )
    
    # Validate alert structure
    required_fields = ['alert_id', 'risk_level', 'timestamp', 'description']
    for field in required_fields:
        if field not in alert:
            raise ValueError(f"Alert missing required field: {field}")
    
    return alert

def test_risk_aggregation(framework: E2ETestFramework) -> Dict[str, Any]:
    """Test complex risk aggregation"""
    test_data = generate_test_data("high_risk")
    mapped_evidence = map_evidence(test_data)
    
    # Test risk aggregation
    aggregated_risk = framework.risk_aggregator.compute_overall_risk_score(
        mapped_evidence, 
        {'overall_score': 0.7}
    )
    
    # Validate aggregation result
    if 'overall_score' not in aggregated_risk:
        raise ValueError("Risk aggregation missing overall_score")
    
    return aggregated_risk

def test_end_to_end_workflow(framework: E2ETestFramework) -> Dict[str, Any]:
    """Test complete end-to-end workflow"""
    test_data = generate_test_data("high_risk")
    
    # Step 1: Data processing
    processed_data = framework.data_processor.process_data(test_data)
    
    # Step 2: Risk calculation
    risk_result = framework.bayesian_engine.calculate_insider_dealing_risk(processed_data)
    
    # Step 3: Alert generation
    alert = framework.alert_generator.generate_alert(risk_result, processed_data, "insider_dealing")
    
    # Step 4: Validate workflow output
    if risk_result['overall_score'] < 0.5:  # High-risk scenario should trigger high score
        raise ValueError("High-risk scenario should generate high risk score")
    
    if alert['risk_level'] not in ['medium', 'high', 'critical']:
        raise ValueError("High-risk scenario should generate medium or higher alert level")
    
    return {
        'processed_data': processed_data,
        'risk_result': risk_result,
        'alert': alert,
        'workflow_success': True
    }

def test_performance_benchmark(framework: E2ETestFramework) -> Dict[str, Any]:
    """Test performance with large dataset"""
    # Generate larger dataset
    large_data = {
        "trades": [{"trader_id": f"T{i:03d}", "amount": 10000, "timestamp": "2024-01-15T10:30:00Z", "direction": "buy"} 
                  for i in range(1000)],
        "market_data": {"price_change": 0.02, "volume_spike": False, "volatility": 0.05},
        "hr_data": {"employee_id": "T001", "access_level": "low", "department": "operations"},
        "communications": [],
        "pnl_data": {"daily_loss": -5000, "unusual_pattern": False}
    }
    
    start_time = time.time()
    processed_data = framework.data_processor.process_data(large_data)
    processing_time = time.time() - start_time
    
    start_time = time.time()
    risk_result = framework.bayesian_engine.calculate_insider_dealing_risk(processed_data)
    inference_time = time.time() - start_time
    
    return {
        'dataset_size': len(large_data['trades']),
        'processing_time': processing_time,
        'inference_time': inference_time,
        'total_time': processing_time + inference_time
    }

# Main test runner
def run_e2e_test_suite():
    """Run the complete E2E test suite"""
    framework = E2ETestFramework()
    
    try:
        # Run all tests
        framework.run_test(test_data_processing_pipeline, "Data Processing Pipeline", framework)
        framework.run_test(test_bayesian_inference, "Bayesian Inference", framework)
        framework.run_test(test_alert_generation, "Alert Generation", framework)
        framework.run_test(test_risk_aggregation, "Risk Aggregation", framework)
        framework.run_test(test_end_to_end_workflow, "End-to-End Workflow", framework)
        framework.run_test(test_performance_benchmark, "Performance Benchmark", framework)
        
        # Generate and save report
        report = framework.save_report()
        framework.print_summary()
        
        # Save baselines for future regression testing
        framework._save_baselines()
        
        # Return exit code for CI/CD
        success_rate = report['summary']['success_rate']
        if success_rate >= 90:  # 90% success rate threshold
            return 0  # Success
        else:
            return 1  # Failure
            
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        return 2  # Error

if __name__ == "__main__":
    exit_code = run_e2e_test_suite()
    sys.exit(exit_code) 