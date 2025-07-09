"""
Test suite for Phase 3 circular trading model.

This module tests the new circular trading model including nodes,
configuration, and the main model class.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, 'src')

from core.node_library import (
    CounterpartyRelationshipNode, RiskTransferAnalysisNode, PriceNegotiationPatternNode,
    SettlementCoordinationNode, BeneficialOwnershipNode, TradeSequenceAnalysisNode,
    CoordinationLatentIntentNode
)
from models.bayesian.shared.node_library import (
    BayesianNodeLibrary, CounterpartyRelationshipNode as SharedCounterpartyRelationshipNode,
    RiskTransferAnalysisNode as SharedRiskTransferAnalysisNode,
    PriceNegotiationPatternNode as SharedPriceNegotiationPatternNode,
    SettlementCoordinationNode as SharedSettlementCoordinationNode,
    BeneficialOwnershipNode as SharedBeneficialOwnershipNode,
    TradeSequenceAnalysisNode as SharedTradeSequenceAnalysisNode,
    CoordinationLatentIntentNode as SharedCoordinationLatentIntentNode
)
from models.bayesian.circular_trading.nodes import CircularTradingNodes
from models.bayesian.circular_trading.model import CircularTradingModel
from models.bayesian.circular_trading.config import CircularTradingConfig
from models.bayesian.registry import BayesianModelRegistry


class TestCircularTradingNodes:
    """Test the new circular trading evidence nodes."""
    
    def test_counterparty_relationship_node_creation(self):
        """Test CounterpartyRelationshipNode creation and properties."""
        node = CounterpartyRelationshipNode("test_counterparty", "Test counterparty relationship node")
        
        assert node.name == "test_counterparty"
        assert node.description == "Test counterparty relationship node"
        assert node.states == ["unrelated", "connected", "closely_related"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_risk_transfer_analysis_node_creation(self):
        """Test RiskTransferAnalysisNode creation and properties."""
        node = RiskTransferAnalysisNode("test_risk_transfer", "Test risk transfer analysis node")
        
        assert node.name == "test_risk_transfer"
        assert node.description == "Test risk transfer analysis node"
        assert node.states == ["genuine_transfer", "limited_transfer", "no_transfer"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_price_negotiation_pattern_node_creation(self):
        """Test PriceNegotiationPatternNode creation and properties."""
        node = PriceNegotiationPatternNode("test_price_negotiation", "Test price negotiation node")
        
        assert node.name == "test_price_negotiation"
        assert node.description == "Test price negotiation node"
        assert node.states == ["market_driven", "coordinated", "artificial"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_settlement_coordination_node_creation(self):
        """Test SettlementCoordinationNode creation and properties."""
        node = SettlementCoordinationNode("test_settlement", "Test settlement coordination node")
        
        assert node.name == "test_settlement"
        assert node.description == "Test settlement coordination node"
        assert node.states == ["independent", "synchronized", "coordinated"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_beneficial_ownership_node_creation(self):
        """Test BeneficialOwnershipNode creation and properties."""
        node = BeneficialOwnershipNode("test_ownership", "Test beneficial ownership node")
        
        assert node.name == "test_ownership"
        assert node.description == "Test beneficial ownership node"
        assert node.states == ["separate_ownership", "shared_interests", "common_ownership"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_trade_sequence_analysis_node_creation(self):
        """Test TradeSequenceAnalysisNode creation and properties."""
        node = TradeSequenceAnalysisNode("test_sequence", "Test trade sequence analysis node")
        
        assert node.name == "test_sequence"
        assert node.description == "Test trade sequence analysis node"
        assert node.states == ["random_sequence", "structured_sequence", "circular_sequence"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_coordination_latent_intent_node_creation(self):
        """Test CoordinationLatentIntentNode creation and properties."""
        node = CoordinationLatentIntentNode("test_coordination", "Test coordination latent intent node")
        
        assert node.name == "test_coordination"
        assert node.description == "Test coordination latent intent node"
        assert node.states == ["no_intent", "potential_intent", "clear_intent"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_coordination_latent_intent_get_intent_strength(self):
        """Test CoordinationLatentIntentNode get_intent_strength method."""
        node = CoordinationLatentIntentNode("test_coordination", "Test coordination latent intent node")
        
        # Test with some evidence
        evidence = {
            'counterparty_relationship': 0.8,
            'risk_transfer_analysis': 0.9,
            'price_negotiation_pattern': 0.6,
            'settlement_coordination': 0.7,
            'beneficial_ownership': 0.5,
            'trade_sequence_analysis': 0.4
        }
        
        strength = node.get_intent_strength(evidence)
        assert 0.0 <= strength <= 1.0
        
        # Test with empty evidence
        empty_strength = node.get_intent_strength({})
        assert empty_strength == 0.0


class TestBayesianNodeLibrary:
    """Test the integration of circular trading nodes into the node library."""
    
    def test_node_library_includes_circular_trading_nodes(self):
        """Test that the node library includes circular trading node classes."""
        library = BayesianNodeLibrary()
        
        assert 'counterparty_relationship' in library.node_classes
        assert 'risk_transfer_analysis' in library.node_classes
        assert 'price_negotiation_pattern' in library.node_classes
        assert 'settlement_coordination' in library.node_classes
        assert 'beneficial_ownership' in library.node_classes
        assert 'trade_sequence_analysis' in library.node_classes
        assert 'coordination_latent_intent' in library.node_classes
        
        assert library.node_classes['counterparty_relationship'] == SharedCounterpartyRelationshipNode
        assert library.node_classes['risk_transfer_analysis'] == SharedRiskTransferAnalysisNode
        assert library.node_classes['price_negotiation_pattern'] == SharedPriceNegotiationPatternNode
        assert library.node_classes['settlement_coordination'] == SharedSettlementCoordinationNode
        assert library.node_classes['beneficial_ownership'] == SharedBeneficialOwnershipNode
        assert library.node_classes['trade_sequence_analysis'] == SharedTradeSequenceAnalysisNode
        assert library.node_classes['coordination_latent_intent'] == SharedCoordinationLatentIntentNode
    
    def test_create_circular_trading_nodes_via_library(self):
        """Test creating circular trading nodes via the library."""
        library = BayesianNodeLibrary()
        
        # Test creating counterparty relationship node
        counterparty_node = library.create_node(
            'counterparty_relationship', 
            'test_counterparty_relationship',
            description="Test counterparty relationship node"
        )
        assert counterparty_node.name == 'test_counterparty_relationship'
        assert counterparty_node.states == ["unrelated", "connected", "closely_related"]
        
        # Test creating risk transfer analysis node
        risk_transfer_node = library.create_node(
            'risk_transfer_analysis',
            'test_risk_transfer_analysis',
            description="Test risk transfer analysis node"
        )
        assert risk_transfer_node.name == 'test_risk_transfer_analysis'
        assert risk_transfer_node.states == ["genuine_transfer", "limited_transfer", "no_transfer"]
        
        # Test creating coordination latent intent node
        coordination_node = library.create_node(
            'coordination_latent_intent',
            'test_coordination_intent',
            description="Test coordination intent node"
        )
        assert coordination_node.name == 'test_coordination_intent'
        assert coordination_node.states == ["no_intent", "potential_intent", "clear_intent"]


class TestCircularTradingNodesHelper:
    """Test the CircularTradingNodes helper class."""
    
    def test_circular_trading_nodes_initialization(self):
        """Test CircularTradingNodes initialization."""
        nodes = CircularTradingNodes()
        
        # Check that all expected nodes are defined
        expected_nodes = [
            'counterparty_relationship', 'risk_transfer_analysis', 'price_negotiation_pattern',
            'settlement_coordination', 'beneficial_ownership', 'trade_sequence_analysis',
            'coordination_latent_intent', 'risk_factor', 'circular_trading'
        ]
        
        for node_name in expected_nodes:
            assert node_name in nodes.node_definitions
    
    def test_get_node_creates_circular_trading_nodes(self):
        """Test that get_node creates circular trading nodes correctly."""
        nodes = CircularTradingNodes()
        
        # Test getting circular trading nodes
        counterparty_node = nodes.get_node('counterparty_relationship')
        assert counterparty_node is not None
        assert counterparty_node.name == 'counterparty_relationship'
        assert counterparty_node.states == ['unrelated', 'connected', 'closely_related']
        
        risk_transfer_node = nodes.get_node('risk_transfer_analysis')
        assert risk_transfer_node is not None
        assert risk_transfer_node.name == 'risk_transfer_analysis'
        assert risk_transfer_node.states == ['genuine_transfer', 'limited_transfer', 'no_transfer']
        
        coordination_node = nodes.get_node('coordination_latent_intent')
        assert coordination_node is not None
        assert coordination_node.name == 'coordination_latent_intent'
        assert coordination_node.states == ['no_intent', 'potential_intent', 'clear_intent']
    
    def test_get_evidence_nodes_includes_circular_trading_nodes(self):
        """Test that get_evidence_nodes includes circular trading nodes."""
        nodes = CircularTradingNodes()
        evidence_nodes = nodes.get_evidence_nodes()
        
        expected_evidence_nodes = [
            'counterparty_relationship', 'risk_transfer_analysis', 'price_negotiation_pattern',
            'settlement_coordination', 'beneficial_ownership', 'trade_sequence_analysis'
        ]
        
        for node_name in expected_evidence_nodes:
            assert node_name in evidence_nodes
            assert evidence_nodes[node_name] is not None
    
    def test_get_latent_intent_nodes_includes_circular_trading_nodes(self):
        """Test that get_latent_intent_nodes includes circular trading nodes."""
        nodes = CircularTradingNodes()
        latent_intent_nodes = nodes.get_latent_intent_nodes()
        
        expected_nodes = [
            'counterparty_relationship', 'risk_transfer_analysis', 'price_negotiation_pattern',
            'settlement_coordination', 'beneficial_ownership', 'trade_sequence_analysis',
            'coordination_latent_intent', 'risk_factor', 'circular_trading'
        ]
        
        for node_name in expected_nodes:
            assert node_name in latent_intent_nodes
    
    def test_validate_node_value_for_circular_trading_nodes(self):
        """Test node value validation for circular trading nodes."""
        nodes = CircularTradingNodes()
        
        # Test counterparty relationship node validation
        assert nodes.validate_node_value('counterparty_relationship', 0) == True
        assert nodes.validate_node_value('counterparty_relationship', 1) == True
        assert nodes.validate_node_value('counterparty_relationship', 2) == True
        assert nodes.validate_node_value('counterparty_relationship', 3) == False
        assert nodes.validate_node_value('counterparty_relationship', 'unrelated') == True
        assert nodes.validate_node_value('counterparty_relationship', 'connected') == True
        assert nodes.validate_node_value('counterparty_relationship', 'closely_related') == True
        assert nodes.validate_node_value('counterparty_relationship', 'invalid_state') == False
        
        # Test risk transfer analysis node validation
        assert nodes.validate_node_value('risk_transfer_analysis', 'genuine_transfer') == True
        assert nodes.validate_node_value('risk_transfer_analysis', 'limited_transfer') == True
        assert nodes.validate_node_value('risk_transfer_analysis', 'no_transfer') == True
        assert nodes.validate_node_value('risk_transfer_analysis', 'invalid_state') == False


class TestCircularTradingConfig:
    """Test the CircularTradingConfig class."""
    
    def test_circular_trading_config_initialization(self):
        """Test CircularTradingConfig initialization."""
        config = CircularTradingConfig()
        
        # Check default risk thresholds
        thresholds = config.get_risk_thresholds()
        assert thresholds['low_risk'] == 0.30
        assert thresholds['medium_risk'] == 0.60
        assert thresholds['high_risk'] == 0.80
        
        # Check model parameters
        params = config.get_model_parameters()
        assert params['use_latent_intent'] == True
        assert params['counterparty_relationship_weight'] == 0.20
        
        # Check evidence weights
        weights = config.get_evidence_weights()
        assert abs(sum(weights.values()) - 1.0) < 1e-6
    
    def test_circular_trading_config_custom_config(self):
        """Test CircularTradingConfig with custom configuration."""
        custom_config = {
            'risk_thresholds': {
                'low_risk': 0.25,
                'medium_risk': 0.55,
                'high_risk': 0.75
            }
        }
        
        config = CircularTradingConfig(custom_config)
        thresholds = config.get_risk_thresholds()
        assert thresholds['low_risk'] == 0.25
        assert thresholds['medium_risk'] == 0.55
        assert thresholds['high_risk'] == 0.75
    
    def test_circular_trading_config_validation(self):
        """Test CircularTradingConfig validation."""
        config = CircularTradingConfig()
        assert config.validate_config() == True
        
        # Test invalid config
        invalid_config = CircularTradingConfig({
            'risk_thresholds': {
                'low_risk': 0.8,
                'medium_risk': 0.6,
                'high_risk': 0.4
            }
        })
        assert invalid_config.validate_config() == False


class TestCircularTradingModel:
    """Test the CircularTradingModel class."""
    
    def test_circular_trading_model_initialization(self):
        """Test CircularTradingModel initialization."""
        model = CircularTradingModel(use_latent_intent=True)
        
        assert model.use_latent_intent == True
        assert model.config is not None
        assert model.nodes is not None
        assert model.fallback_logic is not None
        assert model.esi_calculator is not None
        assert model.model is not None
        assert model.inference_engine is not None
    
    def test_circular_trading_model_required_nodes(self):
        """Test required nodes for circular trading model."""
        model = CircularTradingModel(use_latent_intent=True)
        required_nodes = model.get_required_nodes()
        
        expected_nodes = [
            'counterparty_relationship', 'risk_transfer_analysis', 'price_negotiation_pattern',
            'settlement_coordination', 'beneficial_ownership', 'trade_sequence_analysis'
        ]
        
        for node_name in expected_nodes:
            assert node_name in required_nodes
    
    def test_circular_trading_model_info(self):
        """Test that model info includes circular trading nodes."""
        model = CircularTradingModel(use_latent_intent=True)
        model_info = model.get_model_info()
        
        assert model_info['model_type'] == 'circular_trading'
        assert model_info['use_latent_intent'] == True
        assert 'nodes_count' in model_info
        assert 'edges_count' in model_info
        assert 'required_nodes' in model_info
        assert 'config' in model_info
    
    @pytest.mark.skip(reason="Complex network mocking - functionality tested in integration tests")
    def test_circular_trading_model_risk_calculation(self):
        """Test risk calculation with circular trading evidence."""
        model = CircularTradingModel(use_latent_intent=True)
        
        # Test with circular trading evidence
        evidence = {
            'counterparty_relationship': 2,     # closely_related
            'risk_transfer_analysis': 2,        # no_transfer
            'price_negotiation_pattern': 2,     # artificial
            'settlement_coordination': 2,       # coordinated
            'beneficial_ownership': 2,          # common_ownership
            'trade_sequence_analysis': 2        # circular_sequence
        }
        
        result = model.calculate_risk(evidence)
        
        # Verify result structure
        assert 'risk_scores' in result
        assert 'evidence_sufficiency' in result
        assert 'risk_assessment' in result
        assert 'model_metadata' in result
        
        # Verify model metadata
        assert result['model_metadata']['model_type'] == 'circular_trading'
        assert result['model_metadata']['use_latent_intent'] == True


class TestModelRegistryIntegration:
    """Test integration of circular trading model with the registry."""
    
    def test_registry_includes_circular_trading_model(self):
        """Test that the registry includes the circular trading model."""
        registry = BayesianModelRegistry()
        
        available_models = registry.get_available_models()
        assert 'circular_trading' in available_models
    
    def test_registry_can_create_circular_trading_model(self):
        """Test that the registry can create circular trading model instances."""
        registry = BayesianModelRegistry()
        
        # Create model instance
        model = registry.create_model('circular_trading', {'use_latent_intent': True})
        
        assert model is not None
        assert isinstance(model, CircularTradingModel)
        assert model.use_latent_intent == True
    
    def test_registry_circular_trading_model_info(self):
        """Test that the registry can provide info about the circular trading model."""
        registry = BayesianModelRegistry()
        
        model_info = registry.get_model_info('circular_trading')
        
        assert model_info['model_type'] == 'circular_trading'
        assert model_info['available'] == True
        assert 'class_name' in model_info


class TestIntegrationWithExistingSystem:
    """Test integration with existing system components."""
    
    def test_fallback_logic_compatibility(self):
        """Test that fallback logic works with circular trading nodes."""
        model = CircularTradingModel(use_latent_intent=True)
        
        # Test with partial evidence (missing some nodes)
        evidence = {
            'counterparty_relationship': 1,
            'risk_transfer_analysis': 1
            # Missing other nodes
        }
        
        # This should not raise an error due to fallback logic
        result = model.calculate_risk(evidence)
        assert result is not None
        assert 'risk_scores' in result
    
    def test_evidence_sufficiency_with_circular_trading_nodes(self):
        """Test evidence sufficiency calculation with circular trading nodes."""
        model = CircularTradingModel(use_latent_intent=True)
        
        # Test with complete circular trading evidence
        evidence = {
            'counterparty_relationship': 2,
            'risk_transfer_analysis': 2,
            'price_negotiation_pattern': 2,
            'settlement_coordination': 2,
            'beneficial_ownership': 2,
            'trade_sequence_analysis': 2
        }
        
        result = model.calculate_risk(evidence)
        
        # Verify evidence sufficiency is calculated
        assert 'evidence_sufficiency' in result
        assert 'evidence_sufficiency_index' in result['evidence_sufficiency']
        
        # Complete evidence should have good sufficiency
        assert result['evidence_sufficiency']['evidence_sufficiency_index'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])