"""
Test suite for Phase 1 enhancements to insider dealing model.

This module tests the new enhanced evidence nodes and their integration
with the existing insider dealing model.
"""

import pytest
import sys
import numpy as np
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, 'src')

from core.node_library import (
    NewsTimingNode, StateInformationNode, AnnouncementCorrelationNode
)
from models.bayesian.shared.node_library import (
    BayesianNodeLibrary, NewsTimingNode as SharedNewsTimingNode,
    StateInformationNode as SharedStateInformationNode,
    AnnouncementCorrelationNode as SharedAnnouncementCorrelationNode
)
from models.bayesian.insider_dealing.nodes import InsiderDealingNodes
from models.bayesian.insider_dealing.model import InsiderDealingModel
from core.model_construction import build_insider_dealing_bn, build_insider_dealing_bn_with_latent_intent


class TestEnhancedNodes:
    """Test the new enhanced evidence nodes."""
    
    def test_news_timing_node_creation(self):
        """Test NewsTimingNode creation and properties."""
        node = NewsTimingNode("test_news_timing", "Test news timing node")
        
        assert node.name == "test_news_timing"
        assert node.description == "Test news timing node"
        assert node.states == ["normal_timing", "suspicious_timing", "highly_suspicious_timing"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_state_information_node_creation(self):
        """Test StateInformationNode creation and properties."""
        node = StateInformationNode("test_state_info", "Test state information node")
        
        assert node.name == "test_state_info"
        assert node.description == "Test state information node"
        assert node.states == ["no_access", "potential_access", "clear_access"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_announcement_correlation_node_creation(self):
        """Test AnnouncementCorrelationNode creation and properties."""
        node = AnnouncementCorrelationNode("test_announcement", "Test announcement node")
        
        assert node.name == "test_announcement"
        assert node.description == "Test announcement node"
        assert node.states == ["no_correlation", "weak_correlation", "strong_correlation"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_news_timing_node_with_custom_prior(self):
        """Test NewsTimingNode with custom fallback prior."""
        custom_prior = [0.7, 0.2, 0.1]
        node = NewsTimingNode("test_news_timing", "Test node", custom_prior)
        
        assert node.fallback_prior == custom_prior
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)


class TestBayesianNodeLibrary:
    """Test the integration of enhanced nodes into the node library."""
    
    def test_node_library_includes_enhanced_nodes(self):
        """Test that the node library includes enhanced node classes."""
        library = BayesianNodeLibrary()
        
        assert 'news_timing' in library.node_classes
        assert 'state_information' in library.node_classes
        assert 'announcement_correlation' in library.node_classes
        
        assert library.node_classes['news_timing'] == SharedNewsTimingNode
        assert library.node_classes['state_information'] == SharedStateInformationNode
        assert library.node_classes['announcement_correlation'] == SharedAnnouncementCorrelationNode
    
    def test_create_enhanced_nodes_via_library(self):
        """Test creating enhanced nodes via the library."""
        library = BayesianNodeLibrary()
        
        # Test creating news timing node
        news_node = library.create_node(
            'news_timing', 
            'test_news_timing',
            description="Test news timing node"
        )
        assert news_node.name == 'test_news_timing'
        assert news_node.states == ["normal_timing", "suspicious_timing", "highly_suspicious_timing"]
        
        # Test creating state information node
        state_node = library.create_node(
            'state_information',
            'test_state_info',
            description="Test state information node"
        )
        assert state_node.name == 'test_state_info'
        assert state_node.states == ["no_access", "potential_access", "clear_access"]
        
        # Test creating announcement correlation node
        announcement_node = library.create_node(
            'announcement_correlation',
            'test_announcement',
            description="Test announcement node"
        )
        assert announcement_node.name == 'test_announcement'
        assert announcement_node.states == ["no_correlation", "weak_correlation", "strong_correlation"]


class TestInsiderDealingNodesEnhancement:
    """Test the enhanced insider dealing nodes with enhanced additions."""
    
    def test_insider_dealing_nodes_include_enhanced_nodes(self):
        """Test that InsiderDealingNodes includes enhanced nodes."""
        nodes = InsiderDealingNodes()
        
        # Check that enhanced nodes are in the definitions
        assert 'news_timing' in nodes.node_definitions
        assert 'state_information_access' in nodes.node_definitions
        assert 'announcement_correlation' in nodes.node_definitions
        
        # Check node definitions
        news_timing_def = nodes.node_definitions['news_timing']
        assert news_timing_def['type'] == 'news_timing'
        assert news_timing_def['states'] == ['normal_timing', 'suspicious_timing', 'highly_suspicious_timing']
        
        state_info_def = nodes.node_definitions['state_information_access']
        assert state_info_def['type'] == 'state_information'
        assert state_info_def['states'] == ['no_access', 'potential_access', 'clear_access']
        
        announcement_def = nodes.node_definitions['announcement_correlation']
        assert announcement_def['type'] == 'announcement_correlation'
        assert announcement_def['states'] == ['no_correlation', 'weak_correlation', 'strong_correlation']
    
    def test_get_node_creates_enhanced_nodes(self):
        """Test that get_node creates enhanced nodes correctly."""
        nodes = InsiderDealingNodes()
        
        # Test getting enhanced nodes
        news_node = nodes.get_node('news_timing')
        assert news_node is not None
        assert news_node.name == 'news_timing'
        assert news_node.states == ['normal_timing', 'suspicious_timing', 'highly_suspicious_timing']
        
        state_node = nodes.get_node('state_information_access')
        assert state_node is not None
        assert state_node.name == 'state_information_access'
        assert state_node.states == ['no_access', 'potential_access', 'clear_access']
        
        announcement_node = nodes.get_node('announcement_correlation')
        assert announcement_node is not None
        assert announcement_node.name == 'announcement_correlation'
        assert announcement_node.states == ['no_correlation', 'weak_correlation', 'strong_correlation']
    
    def test_get_evidence_nodes_includes_enhanced_nodes(self):
        """Test that get_evidence_nodes includes enhanced nodes."""
        nodes = InsiderDealingNodes()
        evidence_nodes = nodes.get_evidence_nodes()
        
        assert 'news_timing' in evidence_nodes
        assert 'state_information_access' in evidence_nodes
        assert 'announcement_correlation' in evidence_nodes
        
        # Verify they are actual node instances
        assert evidence_nodes['news_timing'] is not None
        assert evidence_nodes['state_information_access'] is not None
        assert evidence_nodes['announcement_correlation'] is not None
    
    def test_get_latent_intent_nodes_includes_enhanced_nodes(self):
        """Test that get_latent_intent_nodes includes enhanced nodes."""
        nodes = InsiderDealingNodes()
        latent_intent_nodes = nodes.get_latent_intent_nodes()
        
        assert 'news_timing' in latent_intent_nodes
        assert 'state_information_access' in latent_intent_nodes
        assert 'announcement_correlation' in latent_intent_nodes
        
        # Verify all expected nodes are present
        expected_nodes = [
            'trade_pattern', 'comms_intent', 'pnl_drift',
            'profit_motivation', 'access_pattern', 'order_behavior', 'comms_metadata',
            'news_timing', 'state_information_access', 'announcement_correlation',
            'latent_intent', 'risk_factor', 'insider_dealing'
        ]
        
        for node_name in expected_nodes:
            assert node_name in latent_intent_nodes
    
    def test_validate_node_value_for_enhanced_nodes(self):
        """Test node value validation for enhanced nodes."""
        nodes = InsiderDealingNodes()
        
        # Test news timing node validation
        assert nodes.validate_node_value('news_timing', 0) == True
        assert nodes.validate_node_value('news_timing', 1) == True
        assert nodes.validate_node_value('news_timing', 2) == True
        assert nodes.validate_node_value('news_timing', 3) == False
        assert nodes.validate_node_value('news_timing', 'normal_timing') == True
        assert nodes.validate_node_value('news_timing', 'suspicious_timing') == True
        assert nodes.validate_node_value('news_timing', 'highly_suspicious_timing') == True
        assert nodes.validate_node_value('news_timing', 'invalid_state') == False
        
        # Test state information node validation
        assert nodes.validate_node_value('state_information_access', 'no_access') == True
        assert nodes.validate_node_value('state_information_access', 'potential_access') == True
        assert nodes.validate_node_value('state_information_access', 'clear_access') == True
        assert nodes.validate_node_value('state_information_access', 'invalid_state') == False


class TestInsiderDealingModelEnhancement:
    """Test the enhanced insider dealing model with enhanced nodes."""
    
    def test_required_nodes_without_latent_intent(self):
        """Test required nodes for basic insider dealing model includes enhanced nodes."""
        model = InsiderDealingModel(use_latent_intent=False)
        required_nodes = model.get_required_nodes()
        
        # Check that enhanced nodes are included
        assert 'news_timing' in required_nodes
        assert 'state_information_access' in required_nodes
        
        # Check that all expected nodes are present
        expected_nodes = [
            'trade_pattern', 'comms_intent', 'pnl_drift',
            'news_timing', 'state_information_access'
        ]
        
        for node_name in expected_nodes:
            assert node_name in required_nodes
    
    def test_required_nodes_with_latent_intent(self):
        """Test required nodes for latent intent model includes enhanced nodes."""
        model = InsiderDealingModel(use_latent_intent=True)
        required_nodes = model.get_required_nodes()
        
        # Check that enhanced nodes are included
        assert 'news_timing' in required_nodes
        assert 'state_information_access' in required_nodes
        assert 'announcement_correlation' in required_nodes
        
        # Check that all expected nodes are present
        expected_nodes = [
            'trade_pattern', 'comms_intent', 'pnl_drift',
            'profit_motivation', 'access_pattern', 'order_behavior', 'comms_metadata',
            'news_timing', 'state_information_access', 'announcement_correlation'
        ]
        
        for node_name in expected_nodes:
            assert node_name in required_nodes
    
    def test_model_info_includes_enhanced_nodes(self):
        """Test that model info includes enhanced nodes."""
        model = InsiderDealingModel(use_latent_intent=True)
        model_info = model.get_model_info()
        
        required_nodes = model_info['required_nodes']
        assert 'news_timing' in required_nodes
        assert 'state_information_access' in required_nodes
        assert 'announcement_correlation' in required_nodes
    
    @pytest.mark.skip(reason="Complex network mocking - functionality tested in integration tests")
    @patch('models.bayesian.insider_dealing.model.build_insider_dealing_bn_with_latent_intent')
    def test_calculate_risk_with_enhanced_evidence(self, mock_build_model):
        """Test risk calculation with enhanced evidence."""
        # Mock the Bayesian network
        mock_network = MagicMock()
        mock_network.nodes.return_value = [
            'trade_pattern', 'comms_intent', 'pnl_drift', 'news_timing', 
            'state_information_access', 'announcement_correlation', 'latent_intent',
            'risk_factor', 'insider_dealing'
        ]
        mock_network.check_model.return_value = True
        mock_build_model.return_value = mock_network
        
        # Mock the inference engine
        mock_inference = MagicMock()
        mock_inference.query.return_value = MagicMock(values=[0.3, 0.7])
        
        with patch('pgmpy.inference.VariableElimination', return_value=mock_inference):
            model = InsiderDealingModel(use_latent_intent=True)
            
            # Test with enhanced evidence
            evidence = {
                'trade_pattern': 1,
                'comms_intent': 1,
                'pnl_drift': 1,
                'news_timing': 2,  # enhanced
                'state_information_access': 1,  # enhanced
                'announcement_correlation': 1  # enhanced
            }
            
            result = model.calculate_risk(evidence)
            
            # Verify result structure
            assert 'risk_scores' in result
            assert 'evidence_sufficiency' in result
            assert 'risk_assessment' in result
            assert 'model_metadata' in result
            
            # Verify enhanced evidence is processed
            assert result['model_metadata']['use_latent_intent'] == True


class TestBayesianNetworkConstruction:
    """Test the Bayesian network construction with enhanced nodes."""
    
    def test_build_basic_insider_dealing_bn_includes_enhanced_nodes(self):
        """Test that the basic Bayesian network includes enhanced nodes."""
        network = build_insider_dealing_bn()
        
        # Check that enhanced nodes are in the network
        assert 'news_timing' in network.nodes()
        assert 'state_information_access' in network.nodes()
        
        # Check that edges exist for enhanced nodes
        assert ('news_timing', 'risk_factor') in network.edges()
        assert ('state_information_access', 'risk_factor') in network.edges()
        
        # Verify network structure
        assert network.check_model() == True
        
        # Check CPDs exist for enhanced nodes
        cpds = network.get_cpds()
        cpd_names = [cpd.variable for cpd in cpds]
        assert 'news_timing' in cpd_names
        assert 'state_information_access' in cpd_names
    
    def test_build_latent_intent_bn_includes_enhanced_nodes(self):
        """Test that the latent intent Bayesian network includes enhanced nodes."""
        network = build_insider_dealing_bn_with_latent_intent()
        
        # Check that enhanced nodes are in the network
        assert 'news_timing' in network.nodes()
        assert 'state_information_access' in network.nodes()
        assert 'announcement_correlation' in network.nodes()
        
        # Check that edges exist for enhanced nodes to latent intent
        assert ('news_timing', 'latent_intent') in network.edges()
        assert ('state_information_access', 'latent_intent') in network.edges()
        assert ('announcement_correlation', 'latent_intent') in network.edges()
        
        # Verify network structure
        assert network.check_model() == True
        
        # Check CPDs exist for enhanced nodes
        cpds = network.get_cpds()
        cpd_names = [cpd.variable for cpd in cpds]
        assert 'news_timing' in cpd_names
        assert 'state_information_access' in cpd_names
        assert 'announcement_correlation' in cpd_names
    
    def test_latent_intent_cpd_updated_for_enhanced_nodes(self):
        """Test that latent intent CPD is updated to include enhanced nodes."""
        network = build_insider_dealing_bn_with_latent_intent()
        
        # Find the latent intent CPD
        latent_intent_cpd = None
        for cpd in network.get_cpds():
            if cpd.variable == 'latent_intent':
                latent_intent_cpd = cpd
                break
        
        assert latent_intent_cpd is not None
        
        # Check that enhanced nodes are in the evidence
        expected_evidence = [
            "profit_motivation", "access_pattern", "order_behavior", "comms_metadata",
            "news_timing", "state_information_access", "announcement_correlation"
        ]
        
        for evidence_var in expected_evidence:
            assert evidence_var in latent_intent_cpd.variables
        
        # Check that the CPD has the right number of values (3^7 = 2187 combinations)
        # For a multi-dimensional array, we need to check the total number of combinations
        total_combinations = np.prod(latent_intent_cpd.values.shape[1:])  # Skip first dimension (variable states)
        assert total_combinations == 2187


class TestIntegrationWithExistingSystem:
    """Test integration with existing system components."""
    
    def test_fallback_logic_compatibility(self):
        """Test that fallback logic works with enhanced nodes."""
        model = InsiderDealingModel(use_latent_intent=True)
        
        # Test with partial evidence (missing enhanced nodes)
        evidence = {
            'trade_pattern': 1,
            'comms_intent': 1,
            'pnl_drift': 1
            # Missing enhanced nodes
        }
        
        # This should not raise an error due to fallback logic
        result = model.calculate_risk(evidence)
        assert result is not None
        assert 'risk_scores' in result
    
    def test_evidence_sufficiency_with_enhanced_nodes(self):
        """Test evidence sufficiency calculation with enhanced nodes."""
        model = InsiderDealingModel(use_latent_intent=True)
        
        # Test with complete enhanced evidence
        evidence = {
            'trade_pattern': 1,
            'comms_intent': 1,
            'pnl_drift': 1,
            'news_timing': 2,
            'state_information_access': 1,
            'announcement_correlation': 1
        }
        
        result = model.calculate_risk(evidence)
        
        # Verify evidence sufficiency is calculated
        assert 'evidence_sufficiency' in result
        assert 'evidence_sufficiency_index' in result['evidence_sufficiency']
        
        # enhanced evidence should improve sufficiency
        assert result['evidence_sufficiency']['evidence_sufficiency_index'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])