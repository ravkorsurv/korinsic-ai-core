"""
Performance tests for OpenInference integration.
"""

import pytest
import time
import statistics
from unittest.mock import Mock, patch
from typing import List, Dict, Any

import sys
sys.path.insert(0, 'src')

from src.utils.openinference_tracer import get_tracer, initialize_tracing
from src.core.engines.enhanced_bayesian_engine import EnhancedBayesianEngine


@pytest.mark.performance
class TestOpenInferencePerformance:
    """Performance tests for OpenInference tracing."""
    
    def measure_execution_time(self, func, iterations: int = 10) -> Dict[str, float]:
        """Measure execution time statistics."""
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            func()
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def test_tracer_initialization_performance(self):
        """Test tracer initialization performance."""
        def init_tracer():
            tracer = get_tracer()
            return tracer
        
        stats = self.measure_execution_time(init_tracer, iterations=5)
        
        # Tracer initialization should be fast (< 100ms)
        assert stats["mean"] < 0.1, f"Tracer initialization too slow: {stats['mean']:.3f}s"
    
    def test_bayesian_inference_tracing_overhead(self):
        """Test overhead of Bayesian inference tracing."""
        engine = EnhancedBayesianEngine()
        
        sample_data = {
            "trades": [{"id": f"trade_{i}", "volume": 100, "value": 5000} for i in range(10)],
            "orders": [{"id": f"order_{i}", "quantity": 100, "price": 50.0} for i in range(5)],
            "material_events": []
        }
        
        with patch.object(engine, 'calculate_insider_dealing_risk') as mock_calc:
            mock_calc.return_value = {"overall_score": 0.5, "confidence": "Medium"}
            
            def traced_calculation():
                return engine.calculate_insider_dealing_risk(sample_data)
            
            stats = self.measure_execution_time(traced_calculation, iterations=20)
            
            # Performance should be reasonable
            assert stats["mean"] < 0.1, f"Tracing too slow: {stats['mean']:.3f}s"
            assert stats["stdev"] < stats["mean"], f"High variability in performance"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
