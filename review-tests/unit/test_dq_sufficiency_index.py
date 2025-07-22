"""
Unit Tests for Data Quality Sufficiency Index (DQSI)

Tests the DQSI trust bucket mapping logic, boundary thresholds,
and edge value handling as specified in the feature requirements.
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.dq_sufficiency_index import DQSufficiencyIndex
from core.role_aware_dq_strategy import RoleAwareDQStrategy
from core.fallback_dq_strategy import FallbackDQStrategy

class TestDQSufficiencyIndex(unittest.TestCase):
    """Test cases for DQ Sufficiency Index calculations and trust bucket mapping."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dqsi = DQSufficiencyIndex()
        self.role_strategy = RoleAwareDQStrategy()
        self.fallback_strategy = FallbackDQStrategy()
    
    def test_trust_bucket_boundary_thresholds(self):
        """Test exact boundary thresholds for trust bucket assignment."""
        print("\n🧪 Testing Trust Bucket Boundary Thresholds")
        
        # Test High boundary (0.85)
        high_boundary = self.dqsi._get_trust_bucket(0.85)
        self.assertEqual(high_boundary, "High", "0.85 should map to High bucket")
        print(f"   ✅ 0.85 -> {high_boundary}")
        
        # Test just above High boundary
        high_above = self.dqsi._get_trust_bucket(0.86)
        self.assertEqual(high_above, "High", "0.86 should map to High bucket")
        print(f"   ✅ 0.86 -> {high_above}")
        
        # Test just below High boundary
        moderate_high = self.dqsi._get_trust_bucket(0.84)
        self.assertEqual(moderate_high, "Moderate", "0.84 should map to Moderate bucket")
        print(f"   ✅ 0.84 -> {moderate_high}")
        
        # Test Moderate boundary (0.65)
        moderate_boundary = self.dqsi._get_trust_bucket(0.65)
        self.assertEqual(moderate_boundary, "Moderate", "0.65 should map to Moderate bucket")
        print(f"   ✅ 0.65 -> {moderate_boundary}")
        
        # Test just above Moderate boundary
        moderate_above = self.dqsi._get_trust_bucket(0.66)
        self.assertEqual(moderate_above, "Moderate", "0.66 should map to Moderate bucket")
        print(f"   ✅ 0.66 -> {moderate_above}")
        
        # Test just below Moderate boundary
        low_high = self.dqsi._get_trust_bucket(0.64)
        self.assertEqual(low_high, "Low", "0.64 should map to Low bucket")
        print(f"   ✅ 0.64 -> {low_high}")
    
    def test_edge_values(self):
        """Test edge values (0.0, 1.0) for trust bucket assignment."""
        print("\n🧪 Testing Edge Values")
        
        # Test minimum value
        min_bucket = self.dqsi._get_trust_bucket(0.0)
        self.assertEqual(min_bucket, "Low", "0.0 should map to Low bucket")
        print(f"   ✅ 0.0 -> {min_bucket}")
        
        # Test maximum value
        max_bucket = self.dqsi._get_trust_bucket(1.0)
        self.assertEqual(max_bucket, "High", "1.0 should map to High bucket")
        print(f"   ✅ 1.0 -> {max_bucket}")
        
        # Test very small positive value
        small_bucket = self.dqsi._get_trust_bucket(0.001)
        self.assertEqual(small_bucket, "Low", "0.001 should map to Low bucket")
        print(f"   ✅ 0.001 -> {small_bucket}")
        
        # Test value very close to 1.0
        near_max_bucket = self.dqsi._get_trust_bucket(0.999)
        self.assertEqual(near_max_bucket, "High", "0.999 should map to High bucket")
        print(f"   ✅ 0.999 -> {near_max_bucket}")
    
    def test_boundary_test_cases(self):
        """Test predefined boundary test cases from DQSI calculator."""
        print("\n🧪 Testing Predefined Boundary Cases")
        
        test_cases = self.dqsi.get_boundary_test_cases()
        
        for case_name, case_data in test_cases.items():
            confidence_index = case_data['confidence_index']
            expected_bucket = case_data['expected_bucket']
            description = case_data['description']
            
            actual_bucket = self.dqsi._get_trust_bucket(confidence_index)
            self.assertEqual(actual_bucket, expected_bucket, 
                           f"Test case '{case_name}' failed: {description}")
            print(f"   ✅ {case_name}: {confidence_index} -> {actual_bucket} ({description})")
    
    def test_trust_bucket_validation(self):
        """Test trust bucket validation function."""
        print("\n🧪 Testing Trust Bucket Validation")
        
        # Valid buckets
        valid_buckets = ["High", "Moderate", "Low"]
        for bucket in valid_buckets:
            self.assertTrue(self.dqsi.validate_trust_bucket(bucket), 
                          f"{bucket} should be valid")
            print(f"   ✅ '{bucket}' is valid")
        
        # Invalid buckets
        invalid_buckets = ["high", "MODERATE", "low", "Medium", "Very High", "", None]
        for bucket in invalid_buckets:
            self.assertFalse(self.dqsi.validate_trust_bucket(bucket), 
                           f"{bucket} should be invalid")
            print(f"   ✅ '{bucket}' is correctly invalid")
    
    def test_dqsi_calculation_with_trust_bucket(self):
        """Test full DQSI calculation includes trust bucket in output."""
        print("\n🧪 Testing Full DQSI Calculation")
        
        # Test with high quality data
        evidence = {
            'trade_volume': 1000000,
            'price_impact': 0.02,
            'timing_score': 0.8,
            'communication_data': 'insider_meeting_detected'
        }
        
        data_quality_metrics = {
            'trade_source': 0.95,
            'price_source': 0.90,
            'timing_source': 0.85
        }
        
        kde_presence = {
            'material_info': True,
            'timing_data': True,
            'trade_data': True
        }
        
        result = self.dqsi.calculate_dqsi(evidence, data_quality_metrics, 
                                         imputation_usage={}, kde_presence=kde_presence)
        
        # Verify required fields are present
        self.assertIn('dqsi_confidence_index', result)
        self.assertIn('dqsi_trust_bucket', result)
        
        # Verify trust bucket is valid
        trust_bucket = result['dqsi_trust_bucket']
        self.assertTrue(self.dqsi.validate_trust_bucket(trust_bucket))
        
        # Verify consistency between confidence index and trust bucket
        confidence_index = result['dqsi_confidence_index']
        expected_bucket = self.dqsi._get_trust_bucket(confidence_index)
        self.assertEqual(trust_bucket, expected_bucket, 
                        "Trust bucket should match confidence index mapping")
        
        print(f"   ✅ DQSI calculation successful")
        print(f"   📊 Confidence Index: {confidence_index}")
        print(f"   🏷️  Trust Bucket: {trust_bucket}")
        print(f"   📈 Data Quality Components: {result['data_quality_components']}")
    
    def test_role_aware_strategy_trust_bucket(self):
        """Test role-aware strategy includes trust bucket in output."""
        print("\n🧪 Testing Role-Aware Strategy Trust Bucket")
        
        evidence = {'trade_data': 50000, 'timing_info': 'suspicious'}
        
        # Test different roles
        roles = ['analyst', 'compliance', 'auditor', 'trader']
        
        for role in roles:
            result = self.role_strategy.calculate_dq_score(evidence, user_role=role)
            
            # Verify required fields
            self.assertIn('dqsi_confidence_index', result)
            self.assertIn('dqsi_trust_bucket', result)
            self.assertIn('user_role', result)
            self.assertEqual(result['user_role'], role)
            
            # Verify trust bucket is valid
            trust_bucket = result['dqsi_trust_bucket']
            self.assertTrue(self.dqsi.validate_trust_bucket(trust_bucket))
            
            print(f"   ✅ {role}: confidence={result['dqsi_confidence_index']:.3f}, "
                  f"bucket={trust_bucket}")
    
    def test_fallback_strategy_trust_bucket(self):
        """Test fallback strategy includes trust bucket in output."""
        print("\n🧪 Testing Fallback Strategy Trust Bucket")
        
        # Test fallback with minimal data
        result = self.fallback_strategy.calculate_dq_score(
            evidence={}, fallback_reason="insufficient_data"
        )
        
        # Verify required fields
        self.assertIn('dqsi_confidence_index', result)
        self.assertIn('dqsi_trust_bucket', result)
        self.assertIn('fallback_reason', result)
        self.assertIn('is_degraded_mode', result)
        
        # Verify trust bucket is valid
        trust_bucket = result['dqsi_trust_bucket']
        self.assertTrue(self.dqsi.validate_trust_bucket(trust_bucket))
        
        # Fallback should always result in Low trust bucket
        self.assertEqual(trust_bucket, "Low", "Fallback should result in Low trust bucket")
        
        print(f"   ✅ Fallback: confidence={result['dqsi_confidence_index']:.3f}, "
              f"bucket={trust_bucket}")
        print(f"   ⚠️  Degraded mode: {result['is_degraded_mode']}")
    
    def test_dqsi_output_schema(self):
        """Test that DQSI output matches expected schema."""
        print("\n🧪 Testing DQSI Output Schema")
        
        evidence = {'sample_data': 'test'}
        result = self.dqsi.calculate_dqsi(evidence)
        
        # Required top-level fields
        required_fields = [
            'dqsi_confidence_index',
            'dqsi_trust_bucket',
            'data_quality_components',
            'quality_summary'
        ]
        
        for field in required_fields:
            self.assertIn(field, result, f"Missing required field: {field}")
            print(f"   ✅ Field present: {field}")
        
        # Check data types
        self.assertIsInstance(result['dqsi_confidence_index'], float)
        self.assertIsInstance(result['dqsi_trust_bucket'], str)
        self.assertIsInstance(result['data_quality_components'], dict)
        self.assertIsInstance(result['quality_summary'], dict)
        
        # Check confidence index range
        confidence = result['dqsi_confidence_index']
        self.assertGreaterEqual(confidence, 0.0, "Confidence index should be >= 0.0")
        self.assertLessEqual(confidence, 1.0, "Confidence index should be <= 1.0")
        
        print(f"   ✅ Schema validation passed")
    
    def test_precision_and_rounding(self):
        """Test that confidence index values are properly rounded to 3 decimal places."""
        print("\n🧪 Testing Precision and Rounding")
        
        # Test with data that would produce precise values
        evidence = {'precise_data': 123.456789}
        result = self.dqsi.calculate_dqsi(evidence)
        
        confidence = result['dqsi_confidence_index']
        
        # Check that value is rounded to 3 decimal places
        str_confidence = str(confidence)
        decimal_places = len(str_confidence.split('.')[-1]) if '.' in str_confidence else 0
        self.assertLessEqual(decimal_places, 3, 
                           f"Confidence index should have max 3 decimal places, got {decimal_places}")
        
        print(f"   ✅ Confidence index properly rounded: {confidence}")
        
        # Test components are also properly rounded
        components = result['data_quality_components']
        for component_name, component_value in components.items():
            str_value = str(component_value)
            decimal_places = len(str_value.split('.')[-1]) if '.' in str_value else 0
            self.assertLessEqual(decimal_places, 3, 
                               f"Component {component_name} should have max 3 decimal places")
            print(f"   ✅ Component {component_name}: {component_value}")

def run_dqsi_tests():
    """Run all DQSI unit tests."""
    print("🧮 STARTING DQ SUFFICIENCY INDEX TESTS")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDQSufficiencyIndex)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("🏁 DQ SUFFICIENCY INDEX TESTS COMPLETED")
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {len(result.failures)} FAILURES, {len(result.errors)} ERRORS")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_dqsi_tests()