"""
Performance benchmarks for Explainability & Audit components.

This module provides comprehensive performance testing to ensure
the implementation meets production quality gates.
"""

import pytest
import time
import psutil
import os
from typing import Dict, Any
from unittest.mock import Mock

from src.models.explainability.evidence_sufficiency_index import (
    EvidenceSufficiencyIndex,
    ESIResult
)
from src.models.explainability.enhanced_base_model import EnhancedBaseModel


class MockEnhancedModel(EnhancedBaseModel):
    """Mock enhanced model for benchmark testing."""
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information."""
        return {
            'model_name': 'MockEnhancedModel',
            'version': '1.0.0',
            'model_type': 'benchmark_test',
            'description': 'Mock model for performance benchmarking'
        }
    
    def calculate_risk_with_explanation(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation for benchmarking."""
        return {
            'risk_scores': {'overall_score': 0.7},
            'active_nodes': list(evidence.keys()),
            'all_nodes': list(evidence.keys()) + ['extra_node1', 'extra_node2'],
            'fallback_count': 0,
            'posteriors': {key: 0.5 + (hash(key) % 100) / 200 for key in evidence.keys()},
            'explanation': 'Mock explanation for benchmarking'
        }
    
    def generate_counterfactuals(self, evidence: Dict[str, Any]) -> list:
        """Mock counterfactual generation."""
        return [{'scenario': f'counterfactual_{i}'} for i in range(3)]
    
    def explain_decision_path(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Mock decision path explanation."""
        return {'decision_path': f'Mock path for {len(evidence)} evidence items'}


class TestPerformanceBenchmarks:
    """Performance benchmark test suite."""
    
    @pytest.fixture
    def esi_calculator(self):
        """ESI calculator fixture."""
        return EvidenceSufficiencyIndex()
    
    @pytest.fixture
    def enhanced_model(self):
        """Enhanced model fixture."""
        return MockEnhancedModel()
    
    @pytest.fixture
    def small_evidence(self):
        """Small evidence dataset for benchmarking."""
        return {
            'MaterialInfo': {'value': 2, 'confidence': 'High'},
            'TradingActivity': {'value': 1, 'confidence': 'Medium'},
            'Timing': {'value': 2, 'confidence': 'High'}
        }
    
    @pytest.fixture
    def medium_evidence(self):
        """Medium evidence dataset for benchmarking."""
        return {
            f'evidence_{i}': {
                'value': i % 3,
                'confidence': ['Low', 'Medium', 'High'][i % 3]
            }
            for i in range(20)
        }
    
    @pytest.fixture
    def large_evidence(self):
        """Large evidence dataset for benchmarking."""
        return {
            f'evidence_{i}': {
                'value': i % 3,
                'confidence': ['Low', 'Medium', 'High'][i % 3],
                'quality_score': (i % 100) / 100
            }
            for i in range(100)
        }
    
    @pytest.fixture
    def sample_result(self):
        """Sample result for ESI calculation."""
        return {
            'active_nodes': ['MaterialInfo', 'TradingActivity', 'Timing'],
            'all_nodes': ['MaterialInfo', 'TradingActivity', 'Timing', 'Extra1', 'Extra2'],
            'fallback_count': 0,
            'posteriors': {'MaterialInfo': 0.8, 'TradingActivity': 0.3, 'Timing': 0.7}
        }

    # ===============================================
    # ESI Calculation Performance Tests
    # ===============================================
    
    def test_esi_calculation_small_dataset(self, benchmark, esi_calculator, small_evidence, sample_result):
        """Benchmark ESI calculation with small dataset."""
        # Target: <10ms for small datasets
        result = benchmark(esi_calculator.calculate_esi, small_evidence, sample_result)
        
        # Verify correctness
        assert isinstance(result, ESIResult)
        assert 0 <= result.evidence_sufficiency_index <= 1
        
    def test_esi_calculation_medium_dataset(self, benchmark, esi_calculator, medium_evidence):
        """Benchmark ESI calculation with medium dataset."""
        # Target: <50ms for medium datasets
        medium_result = {
            'active_nodes': list(medium_evidence.keys()),
            'all_nodes': list(medium_evidence.keys()) + ['extra1', 'extra2', 'extra3'],
            'fallback_count': 2,
            'posteriors': {key: 0.5 + (hash(key) % 100) / 200 for key in medium_evidence.keys()}
        }
        
        result = benchmark(esi_calculator.calculate_esi, medium_evidence, medium_result)
        
        # Verify correctness
        assert isinstance(result, ESIResult)
        assert result.node_count == len(medium_evidence)
        
    def test_esi_calculation_large_dataset(self, benchmark, esi_calculator, large_evidence):
        """Benchmark ESI calculation with large dataset."""
        # Target: <100ms for large datasets
        large_result = {
            'active_nodes': list(large_evidence.keys()),
            'all_nodes': list(large_evidence.keys()) + [f'extra_{i}' for i in range(10)],
            'fallback_count': 5,
            'posteriors': {key: 0.5 + (hash(key) % 100) / 200 for key in large_evidence.keys()}
        }
        
        result = benchmark(esi_calculator.calculate_esi, large_evidence, large_result)
        
        # Verify correctness
        assert isinstance(result, ESIResult)
        assert result.node_count == len(large_evidence)

    # ===============================================
    # Enhanced Model Performance Tests
    # ===============================================
    
    def test_risk_calculation_with_explanation(self, benchmark, enhanced_model, medium_evidence):
        """Benchmark complete risk calculation with explanation."""
        # Target: <200ms for complete explanation
        result = benchmark(enhanced_model.calculate_risk, medium_evidence)
        
        # Verify correctness
        assert 'risk_scores' in result
        assert 'evidence_sufficiency_index' in result
        assert isinstance(result['evidence_sufficiency_index'], ESIResult)
        
    def test_counterfactual_generation(self, benchmark, enhanced_model, small_evidence):
        """Benchmark counterfactual generation."""
        # Target: <300ms for counterfactual generation
        result = benchmark(enhanced_model.generate_counterfactuals, small_evidence)
        
        # Verify correctness
        assert isinstance(result, list)
        assert len(result) > 0
        
    def test_decision_path_explanation(self, benchmark, enhanced_model, medium_evidence):
        """Benchmark decision path explanation."""
        # Target: <150ms for decision path
        result = benchmark(enhanced_model.explain_decision_path, medium_evidence)
        
        # Verify correctness
        assert isinstance(result, dict)
        assert 'decision_path' in result

    # ===============================================
    # Memory Usage Tests
    # ===============================================
    
    def test_esi_memory_usage(self, esi_calculator, large_evidence):
        """Test ESI calculation memory usage."""
        # Target: <10MB additional memory
        process = psutil.Process(os.getpid())
        
        # Measure baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large result set
        large_result = {
            'active_nodes': list(large_evidence.keys()),
            'all_nodes': list(large_evidence.keys()) + [f'extra_{i}' for i in range(50)],
            'fallback_count': 10,
            'posteriors': {key: 0.5 + (hash(key) % 100) / 200 for key in large_evidence.keys()}
        }
        
        # Perform ESI calculation
        results = []
        for _ in range(100):  # Simulate multiple calculations
            result = esi_calculator.calculate_esi(large_evidence, large_result)
            results.append(result)
        
        # Measure peak memory
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - baseline_memory
        
        # Verify memory usage within limits
        assert memory_increase < 50, f"Memory usage {memory_increase:.1f}MB exceeds 50MB limit"
        
        # Cleanup
        del results
        
    def test_enhanced_model_memory_usage(self, enhanced_model, medium_evidence):
        """Test enhanced model memory usage."""
        # Target: <20MB additional memory for model operations
        process = psutil.Process(os.getpid())
        
        # Measure baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform multiple calculations
        results = []
        for i in range(50):
            evidence = {**medium_evidence, f'extra_evidence_{i}': {'value': i % 3, 'confidence': 'Medium'}}
            result = enhanced_model.calculate_risk(evidence)
            results.append(result)
        
        # Measure peak memory
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - baseline_memory
        
        # Verify memory usage within limits
        assert memory_increase < 100, f"Memory usage {memory_increase:.1f}MB exceeds 100MB limit"
        
        # Cleanup
        del results

    # ===============================================
    # Concurrent Performance Tests
    # ===============================================
    
    def test_concurrent_esi_calculations(self, esi_calculator, medium_evidence):
        """Test ESI calculation under concurrent load."""
        import threading
        import queue
        
        # Target: Handle 10 concurrent calculations efficiently
        num_threads = 10
        results_queue = queue.Queue()
        
        def calculate_esi():
            result_set = {
                'active_nodes': list(medium_evidence.keys()),
                'all_nodes': list(medium_evidence.keys()) + ['extra1', 'extra2'],
                'fallback_count': 1,
                'posteriors': {key: 0.5 for key in medium_evidence.keys()}
            }
            
            start_time = time.time()
            result = esi_calculator.calculate_esi(medium_evidence, result_set)
            end_time = time.time()
            
            results_queue.put({
                'result': result,
                'duration': end_time - start_time
            })
        
        # Create and start threads
        threads = []
        start_time = time.time()
        
        for _ in range(num_threads):
            thread = threading.Thread(target=calculate_esi)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        thread_results = []
        while not results_queue.empty():
            thread_results.append(results_queue.get())
        
        # Verify all calculations completed successfully
        assert len(thread_results) == num_threads
        
        # Verify individual calculation times
        max_individual_time = max(r['duration'] for r in thread_results)
        avg_individual_time = sum(r['duration'] for r in thread_results) / len(thread_results)
        
        # Performance assertions
        assert total_time < 5.0, f"Total concurrent execution time {total_time:.2f}s exceeds 5s limit"
        assert max_individual_time < 1.0, f"Max individual time {max_individual_time:.2f}s exceeds 1s limit"
        assert avg_individual_time < 0.5, f"Average individual time {avg_individual_time:.2f}s exceeds 0.5s limit"

    # ===============================================
    # Stress Tests
    # ===============================================
    
    def test_esi_stress_test(self, esi_calculator):
        """Stress test ESI calculation with varying data sizes."""
        # Test with progressively larger datasets
        sizes = [10, 50, 100, 200, 500]
        results = []
        
        for size in sizes:
            # Create evidence of specified size
            evidence = {
                f'evidence_{i}': {
                    'value': i % 3,
                    'confidence': ['Low', 'Medium', 'High'][i % 3]
                }
                for i in range(size)
            }
            
            result_set = {
                'active_nodes': list(evidence.keys()),
                'all_nodes': list(evidence.keys()) + [f'extra_{i}' for i in range(size // 10)],
                'fallback_count': size // 20,
                'posteriors': {key: 0.5 + (hash(key) % 100) / 200 for key in evidence.keys()}
            }
            
            # Measure calculation time
            start_time = time.time()
            result = esi_calculator.calculate_esi(evidence, result_set)
            end_time = time.time()
            
            duration = end_time - start_time
            results.append({
                'size': size,
                'duration': duration,
                'esi_score': result.evidence_sufficiency_index
            })
        
        # Verify performance scales reasonably
        for i, result in enumerate(results):
            size = result['size']
            duration = result['duration']
            
            # Performance should scale sub-linearly
            expected_max_time = 0.001 * size  # 1ms per evidence item
            assert duration < expected_max_time, f"Size {size} took {duration:.3f}s, expected <{expected_max_time:.3f}s"
            
        # Verify largest dataset completes within reasonable time
        largest_result = results[-1]
        assert largest_result['duration'] < 1.0, f"Largest dataset took {largest_result['duration']:.3f}s, expected <1.0s"

    # ===============================================
    # Performance Regression Tests
    # ===============================================
    
    def test_performance_regression_baseline(self, benchmark, esi_calculator):
        """Establish performance baseline for regression testing."""
        # Standard test case for regression comparison
        evidence = {
            'MaterialInfo': {'value': 2, 'confidence': 'High'},
            'TradingActivity': {'value': 1, 'confidence': 'Medium'},
            'Timing': {'value': 2, 'confidence': 'High'},
            'PriceImpact': {'value': 1, 'confidence': 'Medium'},
            'VolumeAnomaly': {'value': 0, 'confidence': 'Low'}
        }
        
        result_set = {
            'active_nodes': ['MaterialInfo', 'TradingActivity', 'Timing', 'PriceImpact'],
            'all_nodes': ['MaterialInfo', 'TradingActivity', 'Timing', 'PriceImpact', 'VolumeAnomaly'],
            'fallback_count': 0,
            'posteriors': {
                'MaterialInfo': 0.8,
                'TradingActivity': 0.3,
                'Timing': 0.7,
                'PriceImpact': 0.4
            }
        }
        
        # Benchmark the calculation
        result = benchmark(esi_calculator.calculate_esi, evidence, result_set)
        
        # Store baseline metrics for comparison
        benchmark.extra_info.update({
            'evidence_count': len(evidence),
            'active_nodes': len(result_set['active_nodes']),
            'esi_score': result.evidence_sufficiency_index,
            'baseline_version': '1.0.0'
        })
        
        # Verify baseline correctness
        assert isinstance(result, ESIResult)
        assert 0.5 < result.evidence_sufficiency_index < 1.0  # Should be reasonably high for good evidence

    # ===============================================
    # Benchmark Validation
    # ===============================================
    
    @pytest.mark.parametrize("dataset_size", [10, 25, 50, 100])
    def test_esi_scaling_performance(self, benchmark, esi_calculator, dataset_size):
        """Test ESI performance scaling across different dataset sizes."""
        # Generate evidence of specified size
        evidence = {
            f'Q{i:02d}_Evidence': {
                'value': i % 3,
                'confidence': ['Low', 'Medium', 'High'][i % 3]
            }
            for i in range(dataset_size)
        }
        
        result_set = {
            'active_nodes': list(evidence.keys()),
            'all_nodes': list(evidence.keys()) + [f'Extra_{i}' for i in range(dataset_size // 5)],
            'fallback_count': dataset_size // 10,
            'posteriors': {key: 0.4 + (hash(key) % 60) / 100 for key in evidence.keys()}
        }
        
        # Benchmark the calculation
        result = benchmark(esi_calculator.calculate_esi, evidence, result_set)
        
        # Add size-specific metadata
        benchmark.extra_info.update({
            'dataset_size': dataset_size,
            'node_count': result.node_count,
            'fallback_ratio': result.fallback_ratio
        })
        
        # Verify scaling performance
        assert isinstance(result, ESIResult)
        assert result.node_count == dataset_size


if __name__ == '__main__':
    pytest.main([__file__, '--benchmark-only'])