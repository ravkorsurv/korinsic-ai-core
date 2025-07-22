"""
Unit tests for Evidence Sufficiency Index (ESI) component.

This module tests the ESI implementation against wiki specification 12.2
to ensure accurate calculation and proper integration.
"""

import unittest
import math
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.models.explainability.evidence_sufficiency_index import (
    EvidenceSufficiencyIndex,
    ESIResult
)


class TestEvidenceSufficiencyIndex(unittest.TestCase):
    """Test suite for Evidence Sufficiency Index component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.esi_calculator = EvidenceSufficiencyIndex()
        
        # Sample evidence for testing
        self.sample_evidence = {
            'MaterialInfo': {'value': 2, 'confidence': 'High'},
            'TradingActivity': {'value': 1, 'confidence': 'Medium'},
            'Timing': {'value': 2, 'confidence': 'High'},
            'PriceImpact': {'value': 1, 'confidence': 'Medium'}
        }
        
        # Sample result for testing
        self.sample_result = {
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
    
    def test_esi_calculation_formula(self):
        """Test ESI calculation matches wiki specification formula."""
        # Calculate ESI
        esi_result = self.esi_calculator.calculate_esi(self.sample_evidence, self.sample_result)
        
        # Verify result structure matches wiki specification
        self.assertIsInstance(esi_result, ESIResult)
        self.assertIsInstance(esi_result.evidence_sufficiency_index, float)
        self.assertIsInstance(esi_result.node_count, int)
        self.assertIsInstance(esi_result.mean_confidence, str)
        self.assertIsInstance(esi_result.fallback_ratio, float)
        self.assertIsInstance(esi_result.contribution_spread, str)
        self.assertIsInstance(esi_result.clusters, list)
        
        # Verify ESI is between 0 and 1
        self.assertGreaterEqual(esi_result.evidence_sufficiency_index, 0.0)
        self.assertLessEqual(esi_result.evidence_sufficiency_index, 1.0)
        
        # Verify calculation details are present
        self.assertIn('calculation_details', esi_result.calculation_details)
    
    def test_node_activation_ratio_calculation(self):
        """Test node activation ratio calculation."""
        ratio = self.esi_calculator._calculate_node_activation_ratio(self.sample_result)
        
        # Should be 4 active out of 5 total = 0.8
        expected_ratio = 4 / 5
        self.assertAlmostEqual(ratio, expected_ratio, places=2)
    
    def test_mean_confidence_calculation(self):
        """Test mean confidence score calculation."""
        confidence_score = self.esi_calculator._calculate_mean_confidence(self.sample_evidence)
        
        # Verify confidence is between 0 and 1
        self.assertGreaterEqual(confidence_score, 0.0)
        self.assertLessEqual(confidence_score, 1.0)
        
        # Test with known confidence values
        test_evidence = {
            'field1': {'confidence': 'High'},    # 1.0
            'field2': {'confidence': 'Medium'},  # 0.7
            'field3': {'confidence': 'Low'}      # 0.4
        }
        
        expected_mean = (1.0 + 0.7 + 0.4) / 3
        actual_mean = self.esi_calculator._calculate_mean_confidence(test_evidence)
        self.assertAlmostEqual(actual_mean, expected_mean, places=2)
    
    def test_fallback_ratio_calculation(self):
        """Test fallback ratio calculation."""
        # Test with no fallbacks
        ratio = self.esi_calculator._calculate_fallback_ratio(self.sample_result)
        self.assertEqual(ratio, 0.0)
        
        # Test with fallbacks
        result_with_fallbacks = self.sample_result.copy()
        result_with_fallbacks['fallback_count'] = 2
        
        ratio = self.esi_calculator._calculate_fallback_ratio(result_with_fallbacks)
        expected_ratio = 2 / 4  # 2 fallbacks out of 4 active nodes
        self.assertAlmostEqual(ratio, expected_ratio, places=2)
    
    def test_contribution_entropy_calculation(self):
        """Test contribution entropy calculation."""
        entropy = self.esi_calculator._calculate_contribution_entropy(self.sample_result)
        
        # Verify entropy is between 0 and 1
        self.assertGreaterEqual(entropy, 0.0)
        self.assertLessEqual(entropy, 1.0)
        
        # Test with uniform distribution (should have high entropy)
        uniform_result = {
            'posteriors': {'A': 0.25, 'B': 0.25, 'C': 0.25, 'D': 0.25}
        }
        uniform_entropy = self.esi_calculator._calculate_contribution_entropy(uniform_result)
        
        # Test with concentrated distribution (should have low entropy)
        concentrated_result = {
            'posteriors': {'A': 0.97, 'B': 0.01, 'C': 0.01, 'D': 0.01}
        }
        concentrated_entropy = self.esi_calculator._calculate_contribution_entropy(concentrated_result)
        
        # Uniform should have higher entropy than concentrated
        self.assertGreater(uniform_entropy, concentrated_entropy)
    
    def test_cross_cluster_diversity_calculation(self):
        """Test cross-cluster diversity calculation."""
        diversity = self.esi_calculator._calculate_cross_cluster_diversity(self.sample_result)
        
        # Verify diversity is between 0 and 1
        self.assertGreaterEqual(diversity, 0.0)
        self.assertLessEqual(diversity, 1.0)
        
        # Test with nodes from different clusters
        multi_cluster_result = {
            'active_nodes': ['Q20_PnLDeviation', 'Q75_CommsIntentInfluence', 'Q35_TradeClustering']
        }
        multi_diversity = self.esi_calculator._calculate_cross_cluster_diversity(multi_cluster_result)
        
        # Should have diversity > 0 since nodes span multiple clusters
        self.assertGreater(multi_diversity, 0.0)
    
    def test_confidence_to_numeric_conversion(self):
        """Test confidence label to numeric conversion."""
        # Test known mappings
        self.assertEqual(self.esi_calculator._confidence_to_numeric('High'), 1.0)
        self.assertEqual(self.esi_calculator._confidence_to_numeric('Medium'), 0.7)
        self.assertEqual(self.esi_calculator._confidence_to_numeric('Low'), 0.4)
        self.assertEqual(self.esi_calculator._confidence_to_numeric('Very Low'), 0.2)
        self.assertEqual(self.esi_calculator._confidence_to_numeric('Unknown'), 0.5)
        
        # Test numeric passthrough
        self.assertEqual(self.esi_calculator._confidence_to_numeric(0.8), 0.8)
        
        # Test unknown confidence
        self.assertEqual(self.esi_calculator._confidence_to_numeric('Invalid'), 0.5)
    
    def test_confidence_to_label_conversion(self):
        """Test numeric confidence to label conversion."""
        self.assertEqual(self.esi_calculator._confidence_to_label(0.9), "High")
        self.assertEqual(self.esi_calculator._confidence_to_label(0.7), "Medium")
        self.assertEqual(self.esi_calculator._confidence_to_label(0.5), "Low")
        self.assertEqual(self.esi_calculator._confidence_to_label(0.2), "Very Low")
    
    def test_evidence_clusters_identification(self):
        """Test evidence clusters identification."""
        clusters = self.esi_calculator._get_evidence_clusters(self.sample_result)
        
        # Should return a list of cluster names
        self.assertIsInstance(clusters, list)
        
        # Test with specific cluster nodes
        cluster_result = {
            'active_nodes': ['Q20_PnLDeviation', 'Q75_CommsIntentInfluence']
        }
        clusters = self.esi_calculator._get_evidence_clusters(cluster_result)
        
        # Should identify PnL and MNPI clusters
        self.assertIn('PnL', clusters)
        self.assertIn('MNPI', clusters)
    
    def test_adjusted_risk_score_calculation(self):
        """Test ESI-adjusted risk score calculation."""
        # Create sample ESI result
        esi_result = ESIResult(
            evidence_sufficiency_index=0.8,
            node_count=4,
            mean_confidence="High",
            fallback_ratio=0.0,
            contribution_spread="Balanced",
            clusters=["PnL", "MNPI"],
            calculation_details={}
        )
        
        original_score = 0.7
        adjusted_score = self.esi_calculator.calculate_adjusted_risk_score(
            original_score, esi_result
        )
        
        # Should be original_score * ESI
        expected_adjusted = 0.7 * 0.8
        self.assertAlmostEqual(adjusted_score, expected_adjusted, places=2)
    
    def test_esi_explanation_generation(self):
        """Test ESI explanation text generation."""
        esi_result = ESIResult(
            evidence_sufficiency_index=0.85,
            node_count=5,
            mean_confidence="High",
            fallback_ratio=0.1,
            contribution_spread="Balanced",
            clusters=["PnL", "MNPI", "TradePattern"],
            calculation_details={}
        )
        
        explanation = self.esi_calculator.generate_esi_explanation(esi_result)
        
        # Should contain key information
        self.assertIn("Strong Evidence", explanation)
        self.assertIn("0.85", explanation)
        self.assertIn("3 evidence clusters", explanation)
        self.assertIn("high confidence", explanation)
    
    def test_esi_badge_generation(self):
        """Test ESI badge generation for UI."""
        # Test strong evidence
        strong_badge = self.esi_calculator.get_esi_badge(0.85)
        self.assertEqual(strong_badge["label"], "Strong Evidence")
        self.assertEqual(strong_badge["color"], "green")
        
        # Test moderate evidence
        moderate_badge = self.esi_calculator.get_esi_badge(0.65)
        self.assertEqual(moderate_badge["label"], "Moderate Evidence")
        self.assertEqual(moderate_badge["color"], "orange")
        
        # Test weak evidence
        weak_badge = self.esi_calculator.get_esi_badge(0.45)
        self.assertEqual(weak_badge["label"], "Weak Evidence")
        self.assertEqual(weak_badge["color"], "yellow")
        
        # Test sparse evidence
        sparse_badge = self.esi_calculator.get_esi_badge(0.25)
        self.assertEqual(sparse_badge["label"], "Sparse Evidence")
        self.assertEqual(sparse_badge["color"], "red")
    
    def test_fallback_esi_result(self):
        """Test fallback ESI result on calculation failure."""
        # Create ESI calculator that will fail
        with patch.object(self.esi_calculator, '_calculate_node_activation_ratio', side_effect=Exception("Test error")):
            esi_result = self.esi_calculator.calculate_esi(self.sample_evidence, self.sample_result)
            
            # Should return conservative fallback values
            self.assertEqual(esi_result.evidence_sufficiency_index, 0.5)
            self.assertEqual(esi_result.fallback_ratio, 1.0)
            self.assertEqual(esi_result.contribution_spread, "Unknown")
            self.assertIn("error", esi_result.calculation_details)
    
    def test_custom_weights_configuration(self):
        """Test ESI calculation with custom weights."""
        custom_weights = {
            'W1': 0.3,  # node_activation_ratio
            'W2': 0.3,  # mean_confidence_score
            'W3': 0.2,  # (1 - fallback_ratio)
            'W4': 0.1,  # contribution_entropy
            'W5': 0.1   # cross_cluster_diversity
        }
        
        custom_esi = EvidenceSufficiencyIndex(weights=custom_weights)
        result = custom_esi.calculate_esi(self.sample_evidence, self.sample_result)
        
        # Should use custom weights
        self.assertEqual(custom_esi.weights, custom_weights)
        self.assertIsInstance(result, ESIResult)
    
    def test_empty_evidence_handling(self):
        """Test ESI calculation with empty evidence."""
        empty_evidence = {}
        empty_result = {
            'active_nodes': [],
            'all_nodes': ['A', 'B', 'C'],
            'fallback_count': 0,
            'posteriors': {}
        }
        
        esi_result = self.esi_calculator.calculate_esi(empty_evidence, empty_result)
        
        # Should handle empty evidence gracefully
        self.assertIsInstance(esi_result, ESIResult)
        self.assertEqual(esi_result.node_count, 0)
        self.assertGreaterEqual(esi_result.evidence_sufficiency_index, 0.0)
    
    def test_wiki_specification_compliance(self):
        """Test compliance with wiki 12.2 specification."""
        # Use example from wiki
        wiki_evidence = {
            'field1': {'confidence': 'High'},
            'field2': {'confidence': 'High'},
            'field3': {'confidence': 'Medium'},
            'field4': {'confidence': 'High'},
            'field5': {'confidence': 'Medium'},
            'field6': {'confidence': 'High'}
        }
        
        wiki_result = {
            'active_nodes': ['Q20_PnLDeviation', 'Q75_CommsIntentInfluence', 'Q35_TradeClustering',
                           'Q21_PriceSensitivityAbuse', 'Q51_NewsSentimentImpact', 'Q19_HRIncentiveAlignment'],
            'all_nodes': ['Q20_PnLDeviation', 'Q75_CommsIntentInfluence', 'Q35_TradeClustering',
                         'Q21_PriceSensitivityAbuse', 'Q51_NewsSentimentImpact', 'Q19_HRIncentiveAlignment'],
            'fallback_count': 0,
            'posteriors': {
                'Q20_PnLDeviation': 0.7,
                'Q75_CommsIntentInfluence': 0.8,
                'Q35_TradeClustering': 0.6,
                'Q21_PriceSensitivityAbuse': 0.5,
                'Q51_NewsSentimentImpact': 0.4,
                'Q19_HRIncentiveAlignment': 0.3
            }
        }
        
        esi_result = self.esi_calculator.calculate_esi(wiki_evidence, wiki_result)
        
        # Verify output format matches wiki specification
        expected_fields = [
            'evidence_sufficiency_index',
            'node_count',
            'mean_confidence',
            'fallback_ratio',
            'contribution_spread',
            'clusters'
        ]
        
        for field in expected_fields:
            self.assertTrue(hasattr(esi_result, field), f"Missing field: {field}")
        
        # Verify values are reasonable for this high-quality evidence
        self.assertGreater(esi_result.evidence_sufficiency_index, 0.7)
        self.assertEqual(esi_result.node_count, 6)
        self.assertEqual(esi_result.fallback_ratio, 0.0)
        self.assertGreater(len(esi_result.clusters), 1)


if __name__ == '__main__':
    unittest.main()