"""
Test suite for Phase 2 commodity manipulation model.

This module tests the new commodity manipulation model including nodes,
configuration, and the main model class.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, 'src')

from core.node_library import (
    LiquidityContextNode, BenchmarkTimingNode, OrderClusteringNode,
    PriceImpactRatioNode, VolumeParticipationNode, CrossVenueCoordinationNode,
    ManipulationLatentIntentNode
)
from models.bayesian.shared.node_library import (
    BayesianNodeLibrary, LiquidityContextNode as SharedLiquidityContextNode,
    BenchmarkTimingNode as SharedBenchmarkTimingNode,
    OrderClusteringNode as SharedOrderClusteringNode,
    PriceImpactRatioNode as SharedPriceImpactRatioNode,
    VolumeParticipationNode as SharedVolumeParticipationNode,
    CrossVenueCoordinationNode as SharedCrossVenueCoordinationNode,
    ManipulationLatentIntentNode as SharedManipulationLatentIntentNode
)
from models.bayesian.commodity_manipulation.nodes import CommodityManipulationNodes
from models.bayesian.commodity_manipulation.model import CommodityManipulationModel
from models.bayesian.commodity_manipulation.config import CommodityManipulationConfig
from models.bayesian.registry import BayesianModelRegistry


class TestCommodityManipulationNodes:
    """Test the new commodity manipulation evidence nodes."""
    
    def test_liquidity_context_node_creation(self):
        """Test LiquidityContextNode creation and properties."""
        node = LiquidityContextNode("test_liquidity", "Test liquidity context node")
        
        assert node.name == "test_liquidity"
        assert node.description == "Test liquidity context node"
        assert node.states == ["liquid", "moderate", "illiquid"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_benchmark_timing_node_creation(self):
        """Test BenchmarkTimingNode creation and properties."""
        node = BenchmarkTimingNode("test_benchmark", "Test benchmark timing node")
        
        assert node.name == "test_benchmark"
        assert node.description == "Test benchmark timing node"
        assert node.states == ["outside_window", "near_window", "during_window"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_order_clustering_node_creation(self):
        """Test OrderClusteringNode creation and properties."""
        node = OrderClusteringNode("test_clustering", "Test order clustering node")
        
        assert node.name == "test_clustering"
        assert node.description == "Test order clustering node"
        assert node.states == ["normal_distribution", "moderate_clustering", "high_clustering"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_price_impact_ratio_node_creation(self):
        """Test PriceImpactRatioNode creation and properties."""
        node = PriceImpactRatioNode("test_price_impact", "Test price impact node")
        
        assert node.name == "test_price_impact"
        assert node.description == "Test price impact node"
        assert node.states == ["normal_impact", "elevated_impact", "excessive_impact"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_volume_participation_node_creation(self):
        """Test VolumeParticipationNode creation and properties."""
        node = VolumeParticipationNode("test_volume", "Test volume participation node")
        
        assert node.name == "test_volume"
        assert node.description == "Test volume participation node"
        assert node.states == ["normal_participation", "high_participation", "dominant_participation"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_cross_venue_coordination_node_creation(self):
        """Test CrossVenueCoordinationNode creation and properties."""
        node = CrossVenueCoordinationNode("test_coordination", "Test cross venue coordination node")
        
        assert node.name == "test_coordination"
        assert node.description == "Test cross venue coordination node"
        assert node.states == ["no_coordination", "weak_coordination", "strong_coordination"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_manipulation_latent_intent_node_creation(self):
        """Test ManipulationLatentIntentNode creation and properties."""
        node = ManipulationLatentIntentNode("test_intent", "Test manipulation latent intent node")
        
        assert node.name == "test_intent"
        assert node.description == "Test manipulation latent intent node"
        assert node.states == ["no_intent", "potential_intent", "clear_intent"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_manipulation_latent_intent_get_intent_strength(self):
        """Test ManipulationLatentIntentNode get_intent_strength method."""
        node = ManipulationLatentIntentNode("test_intent", "Test manipulation latent intent node")
        
        # Test with some evidence
        evidence = {
            'liquidity_context': 0.8,
            'benchmark_timing': 0.6,
            'order_clustering': 0.4,
            'price_impact_ratio': 0.7,
            'volume_participation': 0.5,
            'cross_venue_coordination': 0.3
        }
        
        strength = node.get_intent_strength(evidence)
        assert 0.0 <= strength <= 1.0
        
        # Test with empty evidence
        empty_strength = node.get_intent_strength({})
        assert empty_strength == 0.0


class TestBayesianNodeLibrary:
    """Test the integration of commodity manipulation nodes into the node library."""
    
    def test_node_library_includes_commodity_manipulation_nodes(self):
        """Test that the node library includes commodity manipulation node classes."""
        library = BayesianNodeLibrary()
        
        assert 'liquidity_context' in library.node_classes
        assert 'benchmark_timing' in library.node_classes
        assert 'order_clustering' in library.node_classes
        assert 'price_impact_ratio' in library.node_classes
        assert 'volume_participation' in library.node_classes
        assert 'cross_venue_coordination' in library.node_classes
        assert 'manipulation_latent_intent' in library.node_classes
        
        assert library.node_classes['liquidity_context'] == SharedLiquidityContextNode
        assert library.node_classes['benchmark_timing'] == SharedBenchmarkTimingNode
        assert library.node_classes['order_clustering'] == SharedOrderClusteringNode
        assert library.node_classes['price_impact_ratio'] == SharedPriceImpactRatioNode
        assert library.node_classes['volume_participation'] == SharedVolumeParticipationNode
        assert library.node_classes['cross_venue_coordination'] == SharedCrossVenueCoordinationNode
        assert library.node_classes['manipulation_latent_intent'] == SharedManipulationLatentIntentNode
    
    def test_create_commodity_manipulation_nodes_via_library(self):
        """Test creating commodity manipulation nodes via the library."""
        library = BayesianNodeLibrary()
        
        # Test creating liquidity context node
        liquidity_node = library.create_node(
            'liquidity_context', 
            'test_liquidity_context',
            description="Test liquidity context node"
        )
        assert liquidity_node.name == 'test_liquidity_context'
        assert liquidity_node.states == ["liquid", "moderate", "illiquid"]
        
        # Test creating benchmark timing node
        benchmark_node = library.create_node(
            'benchmark_timing',
            'test_benchmark_timing',
            description="Test benchmark timing node"
        )
        assert benchmark_node.name == 'test_benchmark_timing'
        assert benchmark_node.states == ["outside_window", "near_window", "during_window"]
        
        # Test creating manipulation latent intent node
        intent_node = library.create_node(
            'manipulation_latent_intent',
            'test_manipulation_intent',
            description="Test manipulation intent node"
        )
        assert intent_node.name == 'test_manipulation_intent'
        assert intent_node.states == ["no_intent", "potential_intent", "clear_intent"]


class TestCommodityManipulationNodesHelper:
    """Test the CommodityManipulationNodes helper class."""
    
    def test_commodity_manipulation_nodes_initialization(self):
        """Test CommodityManipulationNodes initialization."""
        nodes = CommodityManipulationNodes()
        
        # Check that all expected nodes are defined
        expected_nodes = [
            'liquidity_context', 'benchmark_timing', 'order_clustering',
            'price_impact_ratio', 'volume_participation', 'cross_venue_coordination',
            'manipulation_latent_intent', 'risk_factor', 'commodity_manipulation'
        ]
        
        for node_name in expected_nodes:
            assert node_name in nodes.node_definitions
    
    def test_get_node_creates_commodity_manipulation_nodes(self):
        """Test that get_node creates commodity manipulation nodes correctly."""
        nodes = CommodityManipulationNodes()
        
        # Test getting commodity manipulation nodes
        liquidity_node = nodes.get_node('liquidity_context')
        assert liquidity_node is not None
        assert liquidity_node.name == 'liquidity_context'
        assert liquidity_node.states == ['liquid', 'moderate', 'illiquid']
        
        benchmark_node = nodes.get_node('benchmark_timing')
        assert benchmark_node is not None
        assert benchmark_node.name == 'benchmark_timing'
        assert benchmark_node.states == ['outside_window', 'near_window', 'during_window']
        
        intent_node = nodes.get_node('manipulation_latent_intent')
        assert intent_node is not None
        assert intent_node.name == 'manipulation_latent_intent'
        assert intent_node.states == ['no_intent', 'potential_intent', 'clear_intent']
    
    def test_get_evidence_nodes_includes_commodity_manipulation_nodes(self):
        """Test that get_evidence_nodes includes commodity manipulation nodes."""
        nodes = CommodityManipulationNodes()
        evidence_nodes = nodes.get_evidence_nodes()
        
        expected_evidence_nodes = [
            'liquidity_context', 'benchmark_timing', 'order_clustering',
            'price_impact_ratio', 'volume_participation', 'cross_venue_coordination'
        ]
        
        for node_name in expected_evidence_nodes:
            assert node_name in evidence_nodes
            assert evidence_nodes[node_name] is not None
    
    def test_get_latent_intent_nodes_includes_commodity_manipulation_nodes(self):
        """Test that get_latent_intent_nodes includes commodity manipulation nodes."""
        nodes = CommodityManipulationNodes()
        latent_intent_nodes = nodes.get_latent_intent_nodes()
        
        expected_nodes = [
            'liquidity_context', 'benchmark_timing', 'order_clustering',
            'price_impact_ratio', 'volume_participation', 'cross_venue_coordination',
            'manipulation_latent_intent', 'risk_factor', 'commodity_manipulation'
        ]
        
        for node_name in expected_nodes:
            assert node_name in latent_intent_nodes
    
    def test_validate_node_value_for_commodity_manipulation_nodes(self):
        """Test node value validation for commodity manipulation nodes."""
        nodes = CommodityManipulationNodes()
        
        # Test liquidity context node validation
        assert nodes.validate_node_value('liquidity_context', 0) == True
        assert nodes.validate_node_value('liquidity_context', 1) == True
        assert nodes.validate_node_value('liquidity_context', 2) == True
        assert nodes.validate_node_value('liquidity_context', 3) == False
        assert nodes.validate_node_value('liquidity_context', 'liquid') == True
        assert nodes.validate_node_value('liquidity_context', 'moderate') == True
        assert nodes.validate_node_value('liquidity_context', 'illiquid') == True
        assert nodes.validate_node_value('liquidity_context', 'invalid_state') == False
        
        # Test benchmark timing node validation
        assert nodes.validate_node_value('benchmark_timing', 'outside_window') == True
        assert nodes.validate_node_value('benchmark_timing', 'near_window') == True
        assert nodes.validate_node_value('benchmark_timing', 'during_window') == True
        assert nodes.validate_node_value('benchmark_timing', 'invalid_state') == False


class TestCommodityManipulationConfig:
    """Test the CommodityManipulationConfig class."""
    
    def test_commodity_manipulation_config_initialization(self):
        """Test CommodityManipulationConfig initialization."""
        config = CommodityManipulationConfig()
        
        # Check default risk thresholds
        thresholds = config.get_risk_thresholds()
        assert thresholds['low_risk'] == 0.25
        assert thresholds['medium_risk'] == 0.55
        assert thresholds['high_risk'] == 0.75
        
        # Check model parameters
        params = config.get_model_parameters()
        assert params['use_latent_intent'] == True
        assert params['benchmark_window_sensitivity'] == 0.8
        
        # Check evidence weights
        weights = config.get_evidence_weights()
        assert abs(sum(weights.values()) - 1.0) < 1e-6
    
    def test_commodity_manipulation_config_custom_config(self):
        """Test CommodityManipulationConfig with custom configuration."""
        custom_config = {
            'risk_thresholds': {
                'low_risk': 0.3,
                'medium_risk': 0.6,
                'high_risk': 0.8
            }
        }
        
        config = CommodityManipulationConfig(custom_config)
        thresholds = config.get_risk_thresholds()
        assert thresholds['low_risk'] == 0.3
        assert thresholds['medium_risk'] == 0.6
        assert thresholds['high_risk'] == 0.8
    
    def test_commodity_manipulation_config_validation(self):
        """Test CommodityManipulationConfig validation."""
        config = CommodityManipulationConfig()
        assert config.validate_config() == True
        
        # Test invalid config
        invalid_config = CommodityManipulationConfig({
            'risk_thresholds': {
                'low_risk': 0.8,
                'medium_risk': 0.6,
                'high_risk': 0.4
            }
        })
        assert invalid_config.validate_config() == False


class TestCommodityManipulationModel:
    """Test the CommodityManipulationModel class."""
    
    def test_commodity_manipulation_model_initialization(self):
        """Test CommodityManipulationModel initialization."""
        model = CommodityManipulationModel(use_latent_intent=True)
        
        assert model.use_latent_intent == True
        assert model.config is not None
        assert model.nodes is not None
        assert model.fallback_logic is not None
        assert model.esi_calculator is not None
        assert model.model is not None
        assert model.inference_engine is not None
    
    def test_commodity_manipulation_model_required_nodes(self):
        """Test required nodes for commodity manipulation model."""
        model = CommodityManipulationModel(use_latent_intent=True)
        required_nodes = model.get_required_nodes()
        
        expected_nodes = [
            'liquidity_context', 'benchmark_timing', 'order_clustering',
            'price_impact_ratio', 'volume_participation', 'cross_venue_coordination'
        ]
        
        for node_name in expected_nodes:
            assert node_name in required_nodes
    
    def test_commodity_manipulation_model_info(self):
        """Test that model info includes commodity manipulation nodes."""
        model = CommodityManipulationModel(use_latent_intent=True)
        model_info = model.get_model_info()
        
        assert model_info['model_type'] == 'commodity_manipulation'
        assert model_info['use_latent_intent'] == True
        assert 'nodes_count' in model_info
        assert 'edges_count' in model_info
        assert 'required_nodes' in model_info
        assert 'config' in model_info
    
    @pytest.mark.skip(reason="Complex network mocking - functionality tested in integration tests")
    def test_commodity_manipulation_model_risk_calculation(self):
        """Test risk calculation with commodity manipulation evidence."""
        model = CommodityManipulationModel(use_latent_intent=True)
        
        # Test with commodity manipulation evidence
        evidence = {
            'liquidity_context': 2,  # illiquid
            'benchmark_timing': 2,   # during_window
            'order_clustering': 2,   # high_clustering
            'price_impact_ratio': 2, # excessive_impact
            'volume_participation': 2, # dominant_participation
            'cross_venue_coordination': 2  # strong_coordination
        }
        
        result = model.calculate_risk(evidence)
        
        # Verify result structure
        assert 'risk_scores' in result
        assert 'evidence_sufficiency' in result
        assert 'risk_assessment' in result
        assert 'model_metadata' in result
        
        # Verify model metadata
        assert result['model_metadata']['model_type'] == 'commodity_manipulation'
        assert result['model_metadata']['use_latent_intent'] == True


class TestModelRegistryIntegration:
    """Test integration of commodity manipulation model with the registry."""
    
    def test_registry_includes_commodity_manipulation_model(self):
        """Test that the registry includes the commodity manipulation model."""
        registry = BayesianModelRegistry()
        
        available_models = registry.get_available_models()
        assert 'commodity_manipulation' in available_models
    
    def test_registry_can_create_commodity_manipulation_model(self):
        """Test that the registry can create commodity manipulation model instances."""
        registry = BayesianModelRegistry()
        
        # Create model instance
        model = registry.create_model('commodity_manipulation', {'use_latent_intent': True})
        
        assert model is not None
        assert isinstance(model, CommodityManipulationModel)
        assert model.use_latent_intent == True
    
    def test_registry_commodity_manipulation_model_info(self):
        """Test that the registry can provide info about the commodity manipulation model."""
        registry = BayesianModelRegistry()
        
        model_info = registry.get_model_info('commodity_manipulation')
        
        assert model_info['model_type'] == 'commodity_manipulation'
        assert model_info['available'] == True
        assert 'class_name' in model_info


class TestIntegrationWithExistingSystem:
    """Test integration with existing system components."""
    
    def test_fallback_logic_compatibility(self):
        """Test that fallback logic works with commodity manipulation nodes."""
        model = CommodityManipulationModel(use_latent_intent=True)
        
        # Test with partial evidence (missing some nodes)
        evidence = {
            'liquidity_context': 1,
            'benchmark_timing': 1
            # Missing other nodes
        }
        
        # This should not raise an error due to fallback logic
        result = model.calculate_risk(evidence)
        assert result is not None
        assert 'risk_scores' in result
    
    def test_evidence_sufficiency_with_commodity_manipulation_nodes(self):
        """Test evidence sufficiency calculation with commodity manipulation nodes."""
        model = CommodityManipulationModel(use_latent_intent=True)
        
        # Test with complete commodity manipulation evidence
        evidence = {
            'liquidity_context': 2,
            'benchmark_timing': 2,
            'order_clustering': 2,
            'price_impact_ratio': 2,
            'volume_participation': 2,
            'cross_venue_coordination': 2
        }
        
        result = model.calculate_risk(evidence)
        
        # Verify evidence sufficiency is calculated
        assert 'evidence_sufficiency' in result
        assert 'evidence_sufficiency_index' in result['evidence_sufficiency']
        
        # Complete evidence should have good sufficiency
        assert result['evidence_sufficiency']['evidence_sufficiency_index'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])