"""
Unit tests for Cross-Desk Collusion Detection Model.

This module contains tests for the CrossDeskCollusionModel class,
including model initialization, configuration, and risk calculation.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.models.bayesian.cross_desk_collusion import CrossDeskCollusionModel, CrossDeskCollusionNodes, CrossDeskCollusionConfig


class TestCrossDeskCollusionModel:
    """Test suite for CrossDeskCollusionModel."""
    
    def test_model_initialization(self):
        """Test basic model initialization."""
        model = CrossDeskCollusionModel()
        
        assert model.use_latent_intent is True
        assert isinstance(model.config, CrossDeskCollusionConfig)
        assert isinstance(model.nodes, CrossDeskCollusionNodes)
        assert model.model is not None
        assert model.inference_engine is not None
    
    def test_model_initialization_without_latent_intent(self):
        """Test model initialization without latent intent."""
        model = CrossDeskCollusionModel(use_latent_intent=False)
        
        assert model.use_latent_intent is False
        assert model.model is not None
    
    def test_model_initialization_with_config(self):
        """Test model initialization with custom configuration."""
        config = {
            'risk_thresholds': {
                'low_risk': 0.30,
                'medium_risk': 0.60,
                'high_risk': 0.80
            }
        }
        
        model = CrossDeskCollusionModel(config=config)
        
        assert model.config.get_risk_thresholds()['low_risk'] == 0.30
        assert model.config.get_risk_thresholds()['medium_risk'] == 0.60
        assert model.config.get_risk_thresholds()['high_risk'] == 0.80
    
    def test_get_required_nodes(self):
        """Test getting required nodes."""
        model = CrossDeskCollusionModel()
        required_nodes = model.get_required_nodes()
        
        expected_nodes = [
            'comms_metadata', 'profit_motivation', 'order_behavior',
            'cross_venue_coordination', 'access_pattern', 'market_segmentation'
        ]
        
        assert required_nodes == expected_nodes
    
    def test_get_model_info(self):
        """Test getting model information."""
        model = CrossDeskCollusionModel()
        info = model.get_model_info()
        
        assert info['model_type'] == 'cross_desk_collusion'
        assert info['use_latent_intent'] is True
        assert 'nodes_count' in info
        assert 'edges_count' in info
        assert 'required_nodes' in info
        assert 'variables' in info
        assert 'cpds_count' in info
        assert 'config' in info
    
    @patch('src.models.bayesian.cross_desk_collusion.model.VariableElimination')
    def test_calculate_risk_basic(self, mock_variable_elimination):
        """Test basic risk calculation."""
        # Mock the inference result
        mock_result = Mock()
        mock_result.values = [0.8, 0.2]  # [no_collusion, collusion_detected]
        
        mock_inference = Mock()
        mock_inference.query.return_value = mock_result
        mock_variable_elimination.return_value = mock_inference
        
        model = CrossDeskCollusionModel()
        
        # Mock the ESI calculator
        with patch.object(model.esi_calculator, 'calculate_esi') as mock_esi:
            mock_esi.return_value = {
                'evidence_sufficiency_index': 0.8,
                'esi_badge': 'Strong'
            }
            
            with patch.object(model.esi_calculator, 'adjust_risk_score') as mock_adjust:
                mock_adjust.return_value = 0.25
                
                evidence = {
                    'comms_metadata': 1,
                    'profit_motivation': 1,
                    'order_behavior': 1,
                    'cross_venue_coordination': 1,
                    'access_pattern': 1,
                    'market_segmentation': 1
                }
                
                result = model.calculate_risk(evidence)
                
                assert 'risk_scores' in result
                assert 'evidence_sufficiency' in result
                assert 'risk_assessment' in result
                assert 'fallback_report' in result
                assert 'model_metadata' in result
                
                assert result['risk_scores']['overall_score'] == 0.2
                assert result['model_metadata']['model_type'] == 'cross_desk_collusion'
                assert result['risk_assessment']['risk_level'] in ['LOW', 'MEDIUM', 'HIGH']
    
    def test_risk_level_determination(self):
        """Test risk level determination logic."""
        model = CrossDeskCollusionModel()
        
        # Test low risk
        assert model._determine_risk_level(0.30) == 'LOW'
        
        # Test medium risk
        assert model._determine_risk_level(0.70) == 'MEDIUM'
        
        # Test high risk
        assert model._determine_risk_level(0.90) == 'HIGH'
    
    def test_confidence_rating(self):
        """Test confidence rating logic."""
        model = CrossDeskCollusionModel()
        
        assert model._get_confidence_rating(0.9) == 'High'
        assert model._get_confidence_rating(0.7) == 'Medium'
        assert model._get_confidence_rating(0.5) == 'Low'
    
    def test_recommendations(self):
        """Test recommendation generation."""
        model = CrossDeskCollusionModel()
        
        # Test high risk with strong evidence
        assert 'Immediate investigation' in model._get_recommendation('HIGH', 'Strong')
        
        # Test high risk with weak evidence
        assert 'additional evidence collection' in model._get_recommendation('HIGH', 'Weak')
        
        # Test medium risk
        assert 'Enhanced monitoring' in model._get_recommendation('MEDIUM', 'Moderate')
        
        # Test low risk
        assert 'routine monitoring' in model._get_recommendation('LOW', 'Strong')


class TestCrossDeskCollusionNodes:
    """Test suite for CrossDeskCollusionNodes."""
    
    def test_nodes_initialization(self):
        """Test nodes initialization."""
        nodes = CrossDeskCollusionNodes()
        
        assert nodes.node_library is not None
        assert nodes.node_definitions is not None
        assert len(nodes.node_definitions) > 0
    
    def test_get_required_evidence_nodes(self):
        """Test getting required evidence nodes."""
        nodes = CrossDeskCollusionNodes()
        required_nodes = nodes.get_required_evidence_nodes()
        
        expected_nodes = [
            'comms_metadata', 'profit_motivation', 'order_behavior',
            'cross_venue_coordination', 'access_pattern', 'market_segmentation'
        ]
        
        assert required_nodes == expected_nodes
    
    def test_create_node(self):
        """Test node creation."""
        nodes = CrossDeskCollusionNodes()
        
        # Test creating a communication node
        node = nodes.create_node('comms_metadata')
        assert node is not None
        assert node.name == 'comms_metadata'
        assert hasattr(node, 'states')
        assert hasattr(node, 'fallback_prior')
    
    def test_get_node_definition(self):
        """Test getting node definition."""
        nodes = CrossDeskCollusionNodes()
        
        definition = nodes.get_node_definition('comms_metadata')
        
        assert definition['type'] == 'comms_metadata'
        assert 'states' in definition
        assert 'description' in definition
        assert 'fallback_prior' in definition
        assert 'evidence_type' in definition
    
    def test_get_evidence_nodes(self):
        """Test getting evidence nodes."""
        nodes = CrossDeskCollusionNodes()
        evidence_nodes = nodes.get_evidence_nodes()
        
        assert len(evidence_nodes) > 0
        assert 'comms_metadata' in evidence_nodes
        assert 'profit_motivation' in evidence_nodes
        assert 'order_behavior' in evidence_nodes
    
    def test_get_latent_nodes(self):
        """Test getting latent nodes."""
        nodes = CrossDeskCollusionNodes()
        latent_nodes = nodes.get_latent_nodes()
        
        assert len(latent_nodes) > 0
        assert 'collusion_latent_intent' in latent_nodes
    
    def test_get_outcome_nodes(self):
        """Test getting outcome nodes."""
        nodes = CrossDeskCollusionNodes()
        outcome_nodes = nodes.get_outcome_nodes()
        
        assert len(outcome_nodes) > 0
        assert 'cross_desk_collusion' in outcome_nodes
    
    def test_validate_node_compatibility(self):
        """Test node compatibility validation."""
        nodes = CrossDeskCollusionNodes()
        
        # Test valid node
        assert nodes.validate_node_compatibility('comms_metadata') is True
        
        # Test invalid node
        with pytest.raises(ValueError):
            nodes.validate_node_compatibility('invalid_node')
    
    def test_get_node_statistics(self):
        """Test getting node statistics."""
        nodes = CrossDeskCollusionNodes()
        stats = nodes.get_node_statistics()
        
        assert 'total_nodes' in stats
        assert 'evidence_nodes' in stats
        assert 'latent_nodes' in stats
        assert 'outcome_nodes' in stats
        assert 'intermediate_nodes' in stats
        assert stats['total_nodes'] > 0


class TestCrossDeskCollusionConfig:
    """Test suite for CrossDeskCollusionConfig."""
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        config = CrossDeskCollusionConfig()
        
        assert config.config == {}
        assert config.default_config is not None
        assert config.merged_config is not None
    
    def test_config_with_custom_values(self):
        """Test configuration with custom values."""
        custom_config = {
            'risk_thresholds': {
                'low_risk': 0.40,
                'medium_risk': 0.70,
                'high_risk': 0.90
            }
        }
        
        config = CrossDeskCollusionConfig(custom_config)
        
        thresholds = config.get_risk_thresholds()
        assert thresholds['low_risk'] == 0.40
        assert thresholds['medium_risk'] == 0.70
        assert thresholds['high_risk'] == 0.90
    
    def test_get_risk_thresholds(self):
        """Test getting risk thresholds."""
        config = CrossDeskCollusionConfig()
        thresholds = config.get_risk_thresholds()
        
        assert 'low_risk' in thresholds
        assert 'medium_risk' in thresholds
        assert 'high_risk' in thresholds
        assert thresholds['low_risk'] < thresholds['medium_risk'] < thresholds['high_risk']
    
    def test_get_evidence_weights(self):
        """Test getting evidence weights."""
        config = CrossDeskCollusionConfig()
        weights = config.get_evidence_weights()
        
        assert 'comms_metadata' in weights
        assert 'profit_motivation' in weights
        assert 'order_behavior' in weights
        assert 'cross_venue_coordination' in weights
        assert 'access_pattern' in weights
        assert 'market_segmentation' in weights
        
        # Weights should sum to approximately 1.0
        total_weight = sum(weights.values())
        assert 0.95 <= total_weight <= 1.05
    
    def test_get_model_parameters(self):
        """Test getting model parameters."""
        config = CrossDeskCollusionConfig()
        params = config.get_model_parameters()
        
        assert 'use_latent_intent' in params
        assert 'communication_sensitivity' in params
        assert 'profit_sharing_threshold' in params
        assert 'order_synchronization_window' in params
        assert 'market_division_threshold' in params
    
    def test_validate_config(self):
        """Test configuration validation."""
        config = CrossDeskCollusionConfig()
        
        # Valid configuration should pass
        assert config.validate_config() is True
        
        # Invalid configuration should fail
        invalid_config = {
            'risk_thresholds': {
                'low_risk': 0.8,
                'medium_risk': 0.5,  # Should be higher than low_risk
                'high_risk': 0.9
            }
        }
        
        invalid_config_obj = CrossDeskCollusionConfig(invalid_config)
        assert invalid_config_obj.validate_config() is False
    
    def test_get_node_fallback_prior(self):
        """Test getting node fallback prior."""
        config = CrossDeskCollusionConfig()
        
        # Test existing fallback prior
        prior = config.get_node_fallback_prior('communication')
        assert prior is not None
        assert isinstance(prior, list)
        
        # Test non-existent fallback prior
        prior = config.get_node_fallback_prior('nonexistent')
        assert prior is None
    
    def test_update_config(self):
        """Test updating configuration."""
        config = CrossDeskCollusionConfig()
        
        original_threshold = config.get_risk_thresholds()['low_risk']
        
        updates = {
            'risk_thresholds': {
                'low_risk': 0.50
            }
        }
        
        config.update_config(updates)
        
        new_threshold = config.get_risk_thresholds()['low_risk']
        assert new_threshold == 0.50
        assert new_threshold != original_threshold


if __name__ == '__main__':
    pytest.main([__file__])