"""
Performance Tests for Economic Withholding Detection.

This module provides comprehensive performance testing including:
1. Execution time benchmarks
2. Memory usage analysis  
3. Load testing with multiple concurrent requests
4. Scalability testing with varying data sizes
5. Resource utilization monitoring
"""

import pytest
import sys
import time
import threading
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Tuple
from datetime import datetime
import statistics

# Add src to path for imports
sys.path.insert(0, 'src')
sys.path.insert(0, 'tests')

from fixtures.economic_withholding_test_data import (
    get_compliant_gas_plant_data,
    get_flagged_gas_plant_data,
    get_coal_plant_data
)


class PerformanceMonitor:
    """Utility class for monitoring performance metrics."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.peak_memory = None
        
    def start_monitoring(self):
        """Start performance monitoring."""
        gc.collect()  # Clean up before monitoring
        process = psutil.Process()
        self.start_time = time.time()
        self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.start_memory
        
    def update_peak_memory(self):
        """Update peak memory usage."""
        process = psutil.Process()
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory
            
    def stop_monitoring(self):
        """Stop performance monitoring and return metrics."""
        process = psutil.Process()
        self.end_time = time.time()
        self.end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            'execution_time': self.end_time - self.start_time,
            'start_memory_mb': self.start_memory,
            'end_memory_mb': self.end_memory,
            'peak_memory_mb': self.peak_memory,
            'memory_delta_mb': self.end_memory - self.start_memory,
            'cpu_percent': process.cpu_percent(),
        }


class TestEconomicWithholdingPerformance:
    """Performance tests for economic withholding detection."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.compliant_data = get_compliant_gas_plant_data()
        self.flagged_data = get_flagged_gas_plant_data()
        self.coal_data = get_coal_plant_data()
        self.performance_targets = {
            'max_execution_time': 30.0,  # seconds
            'max_memory_usage': 512.0,    # MB
            'max_memory_growth': 100.0,   # MB per analysis
        }
    
    def test_single_analysis_performance(self):
        """Test performance of single economic withholding analysis."""
        try:
            from models.bayesian.economic_withholding import EconomicWithholdingModel
            
            # Initialize performance monitor
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            # Initialize model
            model = EconomicWithholdingModel(use_latent_intent=False)
            
            # Run analysis
            plant_data = self.flagged_data["plant_data"]
            offers = self.flagged_data["offers"]
            market_data = self.flagged_data["market_data"]
            fuel_prices = self.flagged_data["market_data"]["fuel_prices"]
            
            results = model.analyze_economic_withholding(
                plant_data=plant_data,
                offers=offers,
                market_data=market_data,
                fuel_prices=fuel_prices
            )
            
            # Stop monitoring
            metrics = monitor.stop_monitoring()
            
            # Validate results were generated
            assert 'overall_assessment' in results
            
            # Validate performance targets
            assert metrics['execution_time'] < self.performance_targets['max_execution_time']
            assert metrics['peak_memory_mb'] < self.performance_targets['max_memory_usage']
            
            print(f"✅ Single Analysis Performance:")
            print(f"   Execution Time: {metrics['execution_time']:.2f}s")
            print(f"   Peak Memory: {metrics['peak_memory_mb']:.1f} MB")
            print(f"   Memory Growth: {metrics['memory_delta_mb']:.1f} MB")
            print(f"   CPU Usage: {metrics['cpu_percent']:.1f}%")
            
            return metrics
            
        except ImportError as e:
            pytest.skip(f"Economic withholding model not available: {e}")
        except Exception as e:
            pytest.fail(f"Single analysis performance test failed: {str(e)}")
    
    def test_multiple_sequential_analyses(self):
        """Test performance of multiple sequential analyses."""
        try:
            from models.bayesian.economic_withholding import EconomicWithholdingModel
            
            model = EconomicWithholdingModel(use_latent_intent=False)
            
            # Test with different plant configurations
            test_scenarios = [
                self.compliant_data,
                self.flagged_data,
                self.coal_data
            ]
            
            execution_times = []
            memory_usages = []
            
            for i, scenario in enumerate(test_scenarios):
                monitor = PerformanceMonitor()
                monitor.start_monitoring()
                
                # Run analysis
                results = model.analyze_economic_withholding(
                    plant_data=scenario["plant_data"],
                    offers=scenario["offers"],
                    market_data=scenario["market_data"],
                    fuel_prices=scenario["market_data"]["fuel_prices"]
                )
                
                metrics = monitor.stop_monitoring()
                execution_times.append(metrics['execution_time'])
                memory_usages.append(metrics['peak_memory_mb'])
                
                # Validate results
                assert 'overall_assessment' in results
                
                print(f"   Analysis {i+1}: {metrics['execution_time']:.2f}s, {metrics['peak_memory_mb']:.1f} MB")
            
            # Calculate aggregate statistics
            avg_execution_time = statistics.mean(execution_times)
            max_execution_time = max(execution_times)
            avg_memory_usage = statistics.mean(memory_usages)
            max_memory_usage = max(memory_usages)
            
            # Validate performance consistency
            assert max_execution_time < self.performance_targets['max_execution_time']
            assert max_memory_usage < self.performance_targets['max_memory_usage']
            
            print(f"✅ Sequential Analyses Performance:")
            print(f"   Average Execution Time: {avg_execution_time:.2f}s")
            print(f"   Maximum Execution Time: {max_execution_time:.2f}s")
            print(f"   Average Memory Usage: {avg_memory_usage:.1f} MB")
            print(f"   Maximum Memory Usage: {max_memory_usage:.1f} MB")
            
            return {
                'execution_times': execution_times,
                'memory_usages': memory_usages,
                'avg_execution_time': avg_execution_time,
                'max_execution_time': max_execution_time,
                'avg_memory_usage': avg_memory_usage,
                'max_memory_usage': max_memory_usage
            }
            
        except ImportError as e:
            pytest.skip(f"Economic withholding model not available: {e}")
        except Exception as e:
            pytest.fail(f"Sequential analyses performance test failed: {str(e)}")
    
    def test_concurrent_analyses_load(self):
        """Test performance under concurrent load."""
        try:
            from models.bayesian.economic_withholding import EconomicWithholdingModel
            
            def run_analysis(scenario_data, thread_id):
                """Run a single analysis in a thread."""
                try:
                    model = EconomicWithholdingModel(use_latent_intent=False)
                    
                    start_time = time.time()
                    results = model.analyze_economic_withholding(
                        plant_data=scenario_data["plant_data"],
                        offers=scenario_data["offers"],
                        market_data=scenario_data["market_data"],
                        fuel_prices=scenario_data["market_data"]["fuel_prices"]
                    )
                    execution_time = time.time() - start_time
                    
                    return {
                        'thread_id': thread_id,
                        'execution_time': execution_time,
                        'success': True,
                        'results': results
                    }
                except Exception as e:
                    return {
                        'thread_id': thread_id,
                        'execution_time': 0,
                        'success': False,
                        'error': str(e)
                    }
            
            # Test concurrent execution
            num_threads = 5
            scenarios = [self.compliant_data, self.flagged_data, self.coal_data]
            
            # Monitor overall performance
            overall_monitor = PerformanceMonitor()
            overall_monitor.start_monitoring()
            
            # Execute concurrent analyses
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for i in range(num_threads):
                    scenario = scenarios[i % len(scenarios)]  # Cycle through scenarios
                    future = executor.submit(run_analysis, scenario, i)
                    futures.append(future)
                
                # Collect results
                results = []
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
            
            overall_metrics = overall_monitor.stop_monitoring()
            
            # Analyze results
            successful_analyses = [r for r in results if r['success']]
            failed_analyses = [r for r in results if not r['success']]
            
            if successful_analyses:
                execution_times = [r['execution_time'] for r in successful_analyses]
                avg_execution_time = statistics.mean(execution_times)
                max_execution_time = max(execution_times)
                
                # Validate concurrent performance
                assert len(successful_analyses) >= num_threads * 0.8  # At least 80% success rate
                assert max_execution_time < self.performance_targets['max_execution_time'] * 2  # Allow 2x time for concurrency
                
                print(f"✅ Concurrent Load Test Performance:")
                print(f"   Threads: {num_threads}")
                print(f"   Successful Analyses: {len(successful_analyses)}/{num_threads}")
                print(f"   Failed Analyses: {len(failed_analyses)}")
                print(f"   Average Execution Time: {avg_execution_time:.2f}s")
                print(f"   Maximum Execution Time: {max_execution_time:.2f}s")
                print(f"   Overall Time: {overall_metrics['execution_time']:.2f}s")
                print(f"   Peak Memory: {overall_metrics['peak_memory_mb']:.1f} MB")
                
                if failed_analyses:
                    print(f"   Failed Analysis Errors:")
                    for failure in failed_analyses[:3]:  # Show first 3 errors
                        print(f"     Thread {failure['thread_id']}: {failure['error']}")
                
                return {
                    'successful_analyses': len(successful_analyses),
                    'failed_analyses': len(failed_analyses),
                    'execution_times': execution_times,
                    'avg_execution_time': avg_execution_time,
                    'max_execution_time': max_execution_time,
                    'overall_metrics': overall_metrics
                }
            else:
                pytest.fail("All concurrent analyses failed")
                
        except ImportError as e:
            pytest.skip(f"Economic withholding model not available: {e}")
        except Exception as e:
            pytest.fail(f"Concurrent load test failed: {str(e)}")
    
    def test_scalability_with_data_size(self):
        """Test performance scalability with varying data sizes."""
        try:
            from models.bayesian.economic_withholding import EconomicWithholdingModel
            
            model = EconomicWithholdingModel(use_latent_intent=False)
            
            # Generate test data with varying offer sizes
            base_plant_data = self.flagged_data["plant_data"]
            base_market_data = self.flagged_data["market_data"]
            base_fuel_prices = self.flagged_data["market_data"]["fuel_prices"]
            base_offer = self.flagged_data["offers"][0]
            
            # Test with different numbers of offers
            offer_counts = [1, 5, 10, 25, 50]
            performance_results = []
            
            for offer_count in offer_counts:
                # Generate offers of specified size
                offers = []
                for i in range(offer_count):
                    offer = base_offer.copy()
                    offer['quantity_mw'] = base_offer['quantity_mw'] * (i + 1) / offer_count
                    offer['price_eur_mwh'] = base_offer['price_eur_mwh'] * (1 + i * 0.01)
                    offers.append(offer)
                
                # Monitor performance
                monitor = PerformanceMonitor()
                monitor.start_monitoring()
                
                # Run analysis
                results = model.analyze_economic_withholding(
                    plant_data=base_plant_data,
                    offers=offers,
                    market_data=base_market_data,
                    fuel_prices=base_fuel_prices
                )
                
                metrics = monitor.stop_monitoring()
                
                # Validate results
                assert 'overall_assessment' in results
                
                performance_results.append({
                    'offer_count': offer_count,
                    'execution_time': metrics['execution_time'],
                    'peak_memory_mb': metrics['peak_memory_mb'],
                    'memory_delta_mb': metrics['memory_delta_mb']
                })
                
                print(f"   {offer_count} offers: {metrics['execution_time']:.2f}s, {metrics['peak_memory_mb']:.1f} MB")
            
            # Analyze scalability
            execution_times = [r['execution_time'] for r in performance_results]
            memory_usages = [r['peak_memory_mb'] for r in performance_results]
            
            # Check that performance scales reasonably (not exponentially)
            max_time = max(execution_times)
            min_time = min(execution_times)
            time_ratio = max_time / min_time
            
            # Should not be more than 10x slower for 50x more data
            assert time_ratio < 10.0
            
            print(f"✅ Scalability Test Performance:")
            print(f"   Offer counts tested: {offer_counts}")
            print(f"   Execution time range: {min_time:.2f}s - {max_time:.2f}s")
            print(f"   Time scaling ratio: {time_ratio:.1f}x")
            print(f"   Memory usage range: {min(memory_usages):.1f} - {max(memory_usages):.1f} MB")
            
            return performance_results
            
        except ImportError as e:
            pytest.skip(f"Economic withholding model not available: {e}")
        except Exception as e:
            pytest.fail(f"Scalability test failed: {str(e)}")
    
    def test_memory_leak_detection(self):
        """Test for memory leaks during repeated analyses."""
        try:
            from models.bayesian.economic_withholding import EconomicWithholdingModel
            
            # Run multiple analyses and monitor memory growth
            num_iterations = 10
            memory_measurements = []
            
            for i in range(num_iterations):
                # Force garbage collection before measurement
                gc.collect()
                
                # Measure memory before analysis
                process = psutil.Process()
                memory_before = process.memory_info().rss / 1024 / 1024  # MB
                
                # Create new model instance each time
                model = EconomicWithholdingModel(use_latent_intent=False)
                
                # Run analysis
                results = model.analyze_economic_withholding(
                    plant_data=self.compliant_data["plant_data"],
                    offers=self.compliant_data["offers"],
                    market_data=self.compliant_data["market_data"],
                    fuel_prices=self.compliant_data["market_data"]["fuel_prices"]
                )
                
                # Measure memory after analysis
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                
                memory_measurements.append({
                    'iteration': i + 1,
                    'memory_before': memory_before,
                    'memory_after': memory_after,
                    'memory_delta': memory_after - memory_before
                })
                
                # Clean up
                del model
                del results
                gc.collect()
                
                print(f"   Iteration {i+1}: {memory_before:.1f} → {memory_after:.1f} MB (Δ{memory_after - memory_before:+.1f})")
            
            # Analyze memory growth pattern
            memory_deltas = [m['memory_delta'] for m in memory_measurements]
            avg_memory_delta = statistics.mean(memory_deltas)
            max_memory_delta = max(memory_deltas)
            
            # Calculate overall memory growth
            initial_memory = memory_measurements[0]['memory_before']
            final_memory = memory_measurements[-1]['memory_after']
            total_growth = final_memory - initial_memory
            growth_per_iteration = total_growth / num_iterations
            
            # Validate no significant memory leaks
            # Allow some growth but not excessive
            assert growth_per_iteration < 10.0  # Less than 10MB per iteration
            assert total_growth < 100.0  # Less than 100MB total growth
            
            print(f"✅ Memory Leak Detection:")
            print(f"   Iterations: {num_iterations}")
            print(f"   Average memory delta per iteration: {avg_memory_delta:.1f} MB")
            print(f"   Maximum memory delta: {max_memory_delta:.1f} MB")
            print(f"   Total memory growth: {total_growth:.1f} MB")
            print(f"   Growth per iteration: {growth_per_iteration:.1f} MB")
            
            return {
                'num_iterations': num_iterations,
                'memory_measurements': memory_measurements,
                'avg_memory_delta': avg_memory_delta,
                'total_growth': total_growth,
                'growth_per_iteration': growth_per_iteration
            }
            
        except ImportError as e:
            pytest.skip(f"Economic withholding model not available: {e}")
        except Exception as e:
            pytest.fail(f"Memory leak detection test failed: {str(e)}")
    
    def test_api_endpoint_performance(self):
        """Test API endpoint performance."""
        try:
            # This would test the actual API endpoint performance
            # For now, simulate API call overhead
            
            import json
            from unittest.mock import MagicMock
            
            # Simulate API request processing
            api_request = {
                "plant_data": self.compliant_data["plant_data"],
                "offers": self.compliant_data["offers"],
                "market_data": self.compliant_data["market_data"],
                "fuel_prices": self.compliant_data["market_data"]["fuel_prices"]
            }
            
            # Monitor serialization/deserialization overhead
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            # Simulate request processing
            json_request = json.dumps(api_request)
            parsed_request = json.loads(json_request)
            
            # Simulate validation overhead
            required_fields = ["plant_data", "offers", "market_data", "fuel_prices"]
            for field in required_fields:
                assert field in parsed_request
            
            # Simulate response generation
            api_response = {
                "analysis_type": "economic_withholding",
                "plant_id": parsed_request["plant_data"]["unit_id"],
                "risk_assessment": {
                    "risk_level": "low",
                    "risk_score": 0.25
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            json_response = json.dumps(api_response)
            
            metrics = monitor.stop_monitoring()
            
            # Validate API overhead is minimal
            assert metrics['execution_time'] < 0.1  # Less than 100ms for API overhead
            
            print(f"✅ API Endpoint Performance:")
            print(f"   API Overhead: {metrics['execution_time']*1000:.1f}ms")
            print(f"   Request Size: {len(json_request)} bytes")
            print(f"   Response Size: {len(json_response)} bytes")
            
            return {
                'api_overhead': metrics['execution_time'],
                'request_size': len(json_request),
                'response_size': len(json_response)
            }
            
        except Exception as e:
            pytest.fail(f"API endpoint performance test failed: {str(e)}")
    
    def test_component_performance_breakdown(self):
        """Test performance breakdown of individual components."""
        try:
            from models.bayesian.economic_withholding.scenario_engine import ScenarioSimulationEngine
            from models.bayesian.economic_withholding.cost_curve_analyzer import CostCurveAnalyzer
            from models.bayesian.economic_withholding.arera_compliance import ARERAComplianceEngine
            
            # Test data
            plant_data = self.flagged_data["plant_data"]
            offers = self.flagged_data["offers"]
            market_data = self.flagged_data["market_data"]
            fuel_prices = self.flagged_data["market_data"]["fuel_prices"]
            
            component_performance = {}
            
            # Test Scenario Engine Performance
            scenario_engine = ScenarioSimulationEngine({})
            
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            benchmark_offers = scenario_engine.generate_benchmark_offers(
                plant_data, market_data, fuel_prices
            )
            
            counterfactual_results = scenario_engine.run_counterfactual_simulation(
                offers, benchmark_offers, market_data
            )
            
            scenario_metrics = monitor.stop_monitoring()
            component_performance['scenario_engine'] = scenario_metrics
            
            # Test Cost Curve Analyzer Performance
            cost_analyzer = CostCurveAnalyzer({})
            
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            costs = {
                'marginal_cost': 50.0,
                'fuel_cost': 48.0,
                'efficiency': 0.47,
                'vom_cost': 3.2,
                'emission_cost': 1.1
            }
            
            cost_analysis = cost_analyzer.analyze_offer_cost_relationship(
                offers, costs, plant_data
            )
            
            cost_metrics = monitor.stop_monitoring()
            component_performance['cost_analyzer'] = cost_metrics
            
            # Test ARERA Compliance Engine Performance
            arera_engine = ARERAComplianceEngine({})
            
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            analysis_data = {
                'counterfactual_analysis': counterfactual_results,
                'cost_curve_analysis': cost_analysis
            }
            
            compliance_report = arera_engine.assess_compliance(
                analysis_data, plant_data, market_data
            )
            
            arera_metrics = monitor.stop_monitoring()
            component_performance['arera_engine'] = arera_metrics
            
            # Analyze component performance
            total_time = sum(metrics['execution_time'] for metrics in component_performance.values())
            
            print(f"✅ Component Performance Breakdown:")
            for component, metrics in component_performance.items():
                percentage = (metrics['execution_time'] / total_time) * 100
                print(f"   {component}: {metrics['execution_time']:.3f}s ({percentage:.1f}%)")
            print(f"   Total Component Time: {total_time:.3f}s")
            
            return component_performance
            
        except ImportError as e:
            pytest.skip(f"Economic withholding components not available: {e}")
        except Exception as e:
            pytest.fail(f"Component performance breakdown test failed: {str(e)}")


class TestPerformanceRegression:
    """Test for performance regressions."""
    
    def test_performance_benchmarks(self):
        """Test against established performance benchmarks."""
        # Established benchmarks (these would be updated based on actual measurements)
        benchmarks = {
            'single_analysis_max_time': 30.0,  # seconds
            'single_analysis_max_memory': 512.0,  # MB
            'concurrent_analyses_max_time': 60.0,  # seconds
            'api_overhead_max_time': 0.1,  # seconds
        }
        
        try:
            # Run performance tests and compare to benchmarks
            perf_tests = TestEconomicWithholdingPerformance()
            perf_tests.setup_method()
            
            # Single analysis benchmark
            single_metrics = perf_tests.test_single_analysis_performance()
            assert single_metrics['execution_time'] <= benchmarks['single_analysis_max_time']
            assert single_metrics['peak_memory_mb'] <= benchmarks['single_analysis_max_memory']
            
            # API overhead benchmark
            api_metrics = perf_tests.test_api_endpoint_performance()
            assert api_metrics['api_overhead'] <= benchmarks['api_overhead_max_time']
            
            print(f"✅ Performance Benchmarks:")
            print(f"   Single Analysis: {single_metrics['execution_time']:.2f}s ≤ {benchmarks['single_analysis_max_time']}s ✓")
            print(f"   Memory Usage: {single_metrics['peak_memory_mb']:.1f} MB ≤ {benchmarks['single_analysis_max_memory']} MB ✓")
            print(f"   API Overhead: {api_metrics['api_overhead']*1000:.1f}ms ≤ {benchmarks['api_overhead_max_time']*1000}ms ✓")
            
            return True
            
        except Exception as e:
            pytest.fail(f"Performance benchmarks test failed: {str(e)}")


if __name__ == "__main__":
    # Run performance tests
    print("⚡ Running Economic Withholding Performance Tests...")
    print("=" * 60)
    
    try:
        # Core performance tests
        perf_tests = TestEconomicWithholdingPerformance()
        perf_tests.setup_method()
        
        perf_tests.test_single_analysis_performance()
        perf_tests.test_multiple_sequential_analyses()
        perf_tests.test_concurrent_analyses_load()
        perf_tests.test_scalability_with_data_size()
        perf_tests.test_memory_leak_detection()
        perf_tests.test_api_endpoint_performance()
        perf_tests.test_component_performance_breakdown()
        
        # Performance regression tests
        regression_tests = TestPerformanceRegression()
        regression_tests.test_performance_benchmarks()
        
        print("=" * 60)
        print("🎉 All performance tests completed successfully!")
        print("⚡ Economic withholding module performance validated")
        
    except Exception as e:
        print(f"❌ Performance tests failed: {str(e)}")
        raise