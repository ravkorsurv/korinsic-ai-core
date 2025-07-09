"""
Test suite for Enhanced Spoofing Detection Model.

This module contains comprehensive unit tests for the spoofing detection model,
including node validation, configuration testing, and inference validation.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import logging

# Import the models to test
from src.models.bayesian.spoofing import SpoofingModel, SpoofingConfig, SpoofingNodes

logger = logging.getLogger(__name__)


class TestSpoofingConfig(unittest.TestCase):
    """Test cases for SpoofingConfig class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SpoofingConfig()
        
    def test_default_config_initialization(self):
        """Test default configuration initialization."""
        config = SpoofingConfig()
        
        # Test that all required sections exist
        thresholds = config.get_risk_thresholds()
        self.assertIn('low_risk', thresholds)
        self.assertIn('medium_risk', thresholds)
        self.assertIn('high_risk', thresholds)
        
        # Test threshold ordering
        self.assertLess(thresholds['low_risk'], thresholds['medium_risk'])
        self.assertLess(thresholds['medium_risk'], thresholds['high_risk'])
        
    def test_evidence_weights_sum_to_one(self):
        """Test evidence weights sum to approximately 1.0."""
        weights = self.config.get_evidence_weights()
        total_weight = sum(weights.values())
        
        # Should sum to approximately 1.0 (within floating point tolerance)
        self.assertAlmostEqual(total_weight, 1.0, places=2)
        
    def test_custom_config_override(self):
        """Test custom configuration override."""
        custom_config = {
            'risk_thresholds': {
                'low_risk': 0.40,
                'medium_risk': 0.70,
                'high_risk': 0.90
            }
        }
        
        config = SpoofingConfig(custom_config)
        thresholds = config.get_risk_thresholds()
        
        self.assertEqual(thresholds['low_risk'], 0.40)
        self.assertEqual(thresholds['medium_risk'], 0.70)
        self.assertEqual(thresholds['high_risk'], 0.90)
        
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid configuration should pass
        self.assertTrue(self.config.validate_config())
        
        # Invalid threshold ordering should fail
        invalid_config = SpoofingConfig({
            'risk_thresholds': {
                'low_risk': 0.8,
                'medium_risk': 0.6,
                'high_risk': 0.4
            }
        })
        self.assertFalse(invalid_config.validate_config())
        
    def test_node_fallback_prior_retrieval(self):
        """Test node fallback prior retrieval."""
        prior = self.config.get_node_fallback_prior('order_clustering')
        self.assertIsNotNone(prior)
        self.assertIsInstance(prior, list)
        if prior is not None:
            self.assertEqual(len(prior), 3)  # Should have 3 states
        
    def test_config_update(self):
        """Test configuration updating."""
        original_threshold = self.config.get_risk_thresholds()['high_risk']
        
        self.config.update_config({
            'risk_thresholds': {
                'high_risk': 0.95
            }
        })
        
        updated_threshold = self.config.get_risk_thresholds()['high_risk']
        self.assertNotEqual(original_threshold, updated_threshold)
        self.assertEqual(updated_threshold, 0.95)


class TestSpoofingNodes(unittest.TestCase):
    """Test cases for SpoofingNodes class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.nodes = SpoofingNodes()
        
    def test_node_definitions_completeness(self):
        """Test that all required nodes are defined."""
        definitions = self.nodes.get_all_definitions()
        
        required_nodes = [
            'order_clustering', 'price_impact_ratio', 'volume_participation',
            'order_behavior', 'intent_to_execute', 'order_cancellation',
            'spoofing_latent_intent', 'spoofing'
        ]
        
        for node_name in required_nodes:
            self.assertIn(node_name, definitions)
            
    def test_node_creation(self):
        """Test node creation."""
        node = self.nodes.create_node('order_clustering')
        self.assertIsNotNone(node)
        
        # Test invalid node creation
        with self.assertRaises(ValueError):
            self.nodes.create_node('invalid_node')
            
    def test_evidence_nodes_retrieval(self):
        """Test evidence nodes retrieval."""
        evidence_nodes = self.nodes.get_evidence_nodes()
        self.assertIsInstance(evidence_nodes, dict)
        self.assertGreater(len(evidence_nodes), 0)
        
    def test_latent_nodes_retrieval(self):
        """Test latent nodes retrieval."""
        latent_nodes = self.nodes.get_latent_nodes()
        self.assertIsInstance(latent_nodes, dict)
        self.assertIn('spoofing_latent_intent', latent_nodes)
        
    def test_outcome_nodes_retrieval(self):
        """Test outcome nodes retrieval."""
        outcome_nodes = self.nodes.get_outcome_nodes()
        self.assertIsInstance(outcome_nodes, dict)
        self.assertIn('spoofing', outcome_nodes)
        
    def test_required_evidence_nodes(self):
        """Test required evidence nodes list."""
        required = self.nodes.get_required_evidence_nodes()
        self.assertIsInstance(required, list)
        self.assertGreater(len(required), 0)
        
        # All required nodes should be createable
        for node_name in required:
            node = self.nodes.create_node(node_name)
            self.assertIsNotNone(node)
            
    def test_node_statistics(self):
        """Test node statistics calculation."""
        stats = self.nodes.get_node_statistics()
        
        self.assertIn('total_nodes', stats)
        self.assertIn('evidence_nodes', stats)
        self.assertIn('latent_nodes', stats)
        self.assertIn('outcome_nodes', stats)
        
        # Total should equal sum of categories
        total = stats['evidence_nodes'] + stats['latent_nodes'] + stats['outcome_nodes'] + stats['intermediate_nodes']
        self.assertEqual(total, stats['total_nodes'])
        
    def test_node_compatibility_validation(self):
        """Test node compatibility validation."""
        # Valid nodes should pass
        self.assertTrue(self.nodes.validate_node_compatibility('order_clustering'))
        
        # Invalid nodes should fail
        self.assertFalse(self.nodes.validate_node_compatibility('invalid_node'))


class TestSpoofingModel(unittest.TestCase):
    """Test cases for SpoofingModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the external dependencies
        self.mock_pgmpy_patcher = patch('src.models.bayesian.spoofing.model.DiscreteBayesianNetwork')
        self.mock_inference_patcher = patch('src.models.bayesian.spoofing.model.VariableElimination')
        
        self.mock_pgmpy = self.mock_pgmpy_patcher.start()
        self.mock_inference = self.mock_inference_patcher.start()
        
        # Create mock instances
        self.mock_network = Mock()
        self.mock_pgmpy.return_value = self.mock_network
        
        self.mock_inference_engine = Mock()
        self.mock_inference.return_value = self.mock_inference_engine
        
        # Create model instance
        self.model = SpoofingModel()
        
    def tearDown(self):
        """Clean up after tests."""
        self.mock_pgmpy_patcher.stop()
        self.mock_inference_patcher.stop()
        
    def test_model_initialization(self):
        """Test model initialization."""
        # Test with default parameters
        model = SpoofingModel()
        self.assertTrue(model.use_latent_intent)
        self.assertIsNotNone(model.config)
        self.assertIsNotNone(model.nodes)
        
        # Test with custom parameters
        model = SpoofingModel(use_latent_intent=False)
        self.assertFalse(model.use_latent_intent)
        
    def test_required_nodes(self):
        """Test required nodes retrieval."""
        # Test with latent intent
        model = SpoofingModel(use_latent_intent=True)
        required = model.get_required_nodes()
        
        self.assertIsInstance(required, list)
        self.assertGreater(len(required), 0)
        
        expected_nodes = [
            'order_clustering', 'price_impact_ratio', 'volume_participation',
            'order_behavior', 'intent_to_execute', 'order_cancellation'
        ]
        
        for node in expected_nodes:
            self.assertIn(node, required)
            
    def test_model_info(self):
        """Test model information retrieval."""
        info = self.model.get_model_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('model_type', info)
        self.assertIn('use_latent_intent', info)
        self.assertIn('required_nodes', info)
        self.assertEqual(info['model_type'], 'spoofing')
        
    def test_evidence_validation(self):
        """Test evidence validation."""
        # Valid evidence
        valid_evidence = {
            'order_clustering': 1,
            'price_impact_ratio': 0,
            'volume_participation': 1
        }
        
        validation_result = self.model.validate_evidence(valid_evidence)
        self.assertIsInstance(validation_result, dict)
        
    @patch('src.models.bayesian.spoofing.model.SpoofingModel._perform_inference')
    @patch('src.models.bayesian.spoofing.model.SpoofingModel._calculate_esi')
    def test_risk_calculation(self, mock_esi, mock_inference):
        """Test risk calculation."""
        # Mock return values
        mock_inference.return_value = {
            'overall_score': 0.75,
            'confidence': 0.85,
            'evidence_nodes': ['order_clustering', 'price_impact_ratio']
        }
        
        mock_esi.return_value = {
            'evidence_sufficiency_index': 0.8,
            'esi_badge': 'Strong'
        }
        
        # Test evidence
        evidence = {
            'order_clustering': 2,
            'price_impact_ratio': 1,
            'volume_participation': 1
        }
        
        result = self.model.calculate_risk(evidence)
        
        self.assertIsInstance(result, dict)
        self.assertIn('risk_scores', result)
        self.assertIn('evidence_sufficiency', result)
        self.assertIn('risk_assessment', result)
        self.assertIn('model_metadata', result)
        
    def test_risk_level_determination(self):
        """Test risk level determination."""
        # Test low risk
        low_risk_level = self.model._determine_risk_level(0.2)
        self.assertEqual(low_risk_level, 'LOW')
        
        # Test medium risk
        medium_risk_level = self.model._determine_risk_level(0.5)
        self.assertEqual(medium_risk_level, 'MEDIUM')
        
        # Test high risk
        high_risk_level = self.model._determine_risk_level(0.9)
        self.assertEqual(high_risk_level, 'HIGH')
        
    def test_confidence_rating(self):
        """Test confidence rating calculation."""
        # Test high confidence
        high_confidence = self.model._get_confidence_rating(0.9)
        self.assertEqual(high_confidence, 'High')
        
        # Test medium confidence
        medium_confidence = self.model._get_confidence_rating(0.7)
        self.assertEqual(medium_confidence, 'Medium')
        
        # Test low confidence
        low_confidence = self.model._get_confidence_rating(0.4)
        self.assertEqual(low_confidence, 'Low')
        
    def test_recommendation_generation(self):
        """Test recommendation generation."""
        # Test high risk with strong evidence
        high_risk_rec = self.model._get_recommendation('HIGH', 'Strong')
        self.assertIn('Immediate investigation', high_risk_rec)
        
        # Test medium risk
        medium_risk_rec = self.model._get_recommendation('MEDIUM', 'Moderate')
        self.assertIn('Enhanced monitoring', medium_risk_rec)
        
        # Test low risk
        low_risk_rec = self.model._get_recommendation('LOW', 'Weak')
        self.assertIn('Continue routine', low_risk_rec)


class TestSpoofingModelIntegration(unittest.TestCase):
    """Integration tests for spoofing model components."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.config = SpoofingConfig()
        self.nodes = SpoofingNodes()
        
    def test_config_nodes_integration(self):
        """Test configuration and nodes integration."""
        # Test that config fallback priors match node definitions
        node_definitions = self.nodes.get_all_definitions()
        
        for node_name, definition in node_definitions.items():
            if definition['evidence_type'] in ['order_pattern', 'market_impact', 'volume_pattern', 
                                             'behavior_pattern', 'execution_intent', 'cancellation_pattern']:
                fallback_prior = self.config.get_node_fallback_prior(node_name)
                self.assertIsNotNone(fallback_prior)
                if fallback_prior is not None:
                    self.assertEqual(len(fallback_prior), len(definition['states']))
                
    def test_evidence_weights_node_coverage(self):
        """Test evidence weights cover all evidence nodes."""
        evidence_weights = self.config.get_evidence_weights()
        evidence_nodes = self.nodes.get_evidence_nodes()
        
        # All evidence nodes should have weights
        for node_name in evidence_nodes.keys():
            self.assertIn(node_name, evidence_weights)
            
    def test_model_configuration_consistency(self):
        """Test model configuration consistency."""
        # Test with different configurations
        configs = [
            None,  # Default
            {'risk_thresholds': {'low_risk': 0.25, 'medium_risk': 0.55, 'high_risk': 0.85}},
            {'model_parameters': {'use_latent_intent': False}}
        ]
        
        for config in configs:
            with patch('src.models.bayesian.spoofing.model.DiscreteBayesianNetwork'):
                with patch('src.models.bayesian.spoofing.model.VariableElimination'):
                    model = SpoofingModel(config=config)
                    self.assertIsNotNone(model.config)
                    self.assertIsNotNone(model.nodes)


class TestSpoofingModelErrorHandling(unittest.TestCase):
    """Test error handling in spoofing model."""
    
    def setUp(self):
        """Set up error handling test fixtures."""
        with patch('src.models.bayesian.spoofing.model.DiscreteBayesianNetwork'):
            with patch('src.models.bayesian.spoofing.model.VariableElimination'):
                self.model = SpoofingModel()
                
    def test_invalid_evidence_handling(self):
        """Test handling of invalid evidence."""
        # Test with invalid evidence types
        invalid_evidence = {
            'invalid_node': 'invalid_value',
            'order_clustering': 'not_a_number'
        }
        
        # Should not raise an exception, but handle gracefully
        try:
            validation_result = self.model.validate_evidence(invalid_evidence)
            self.assertIsInstance(validation_result, dict)
        except Exception as e:
            self.fail(f"Model should handle invalid evidence gracefully: {e}")
            
    def test_empty_evidence_handling(self):
        """Test handling of empty evidence."""
        empty_evidence = {}
        
        try:
            validation_result = self.model.validate_evidence(empty_evidence)
            self.assertIsInstance(validation_result, dict)
        except Exception as e:
            self.fail(f"Model should handle empty evidence gracefully: {e}")
            
    def test_configuration_error_recovery(self):
        """Test configuration error recovery."""
        # Test with invalid configuration
        invalid_config = {
            'risk_thresholds': 'invalid_format'
        }
        
        with patch('src.models.bayesian.spoofing.model.DiscreteBayesianNetwork'):
            with patch('src.models.bayesian.spoofing.model.VariableElimination'):
                try:
                    model = SpoofingModel(config=invalid_config)
                    self.assertIsNotNone(model)
                except Exception as e:
                    # Should either handle gracefully or raise a clear error
                    self.assertIsInstance(e, (ValueError, TypeError))


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.INFO)
    
    # Run the tests
    unittest.main(verbosity=2)