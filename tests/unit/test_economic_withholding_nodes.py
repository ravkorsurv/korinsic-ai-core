"""
Test suite for Economic Withholding Detection model nodes.

This module tests the new economic withholding model including nodes,
configuration, and specialized evidence nodes for power markets.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, 'src')

from models.bayesian.economic_withholding.nodes import (
    EconomicWithholdingNodes,
    FuelCostVarianceNode,
    PlantEfficiencyNode,
    MarginalCostDeviationNode,
    HeatRateVarianceNode,
    LoadFactorNode,
    MarketTightnessNode,
    CompetitiveContextNode,
    TransmissionConstraintNode,
    BidShapeAnomalyNode,
    OfferWithdrawalPatternNode,
    CrossPlantCoordinationNode,
    CapacityUtilizationNode,
    MarkupConsistencyNode,
    OpportunityPricingNode,
    FuelPriceCorrelationNode,
    WithholdingLatentIntentNode,
    EconomicWithholdingRiskNode
)


class TestEconomicWithholdingNodes:
    """Test the new economic withholding evidence nodes."""
    
    def test_fuel_cost_variance_node_creation(self):
        """Test FuelCostVarianceNode creation and properties."""
        node = FuelCostVarianceNode("test_fuel_cost", "Test fuel cost variance node")
        
        assert node.name == "test_fuel_cost"
        assert node.description == "Test fuel cost variance node"
        assert node.states == ["aligned", "moderate_variance", "high_variance"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_plant_efficiency_node_creation(self):
        """Test PlantEfficiencyNode creation and properties."""
        node = PlantEfficiencyNode("test_efficiency", "Test plant efficiency node")
        
        assert node.name == "test_efficiency"
        assert node.description == "Test plant efficiency node"
        assert node.states == ["optimal", "suboptimal", "significantly_impaired"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_marginal_cost_deviation_node_creation(self):
        """Test MarginalCostDeviationNode creation and properties."""
        node = MarginalCostDeviationNode("test_marginal_cost", "Test marginal cost deviation node")
        
        assert node.name == "test_marginal_cost"
        assert node.description == "Test marginal cost deviation node"
        assert node.states == ["cost_reflective", "moderate_markup", "excessive_markup"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_heat_rate_variance_node_creation(self):
        """Test HeatRateVarianceNode creation and properties."""
        node = HeatRateVarianceNode("test_heat_rate", "Test heat rate variance node")
        
        assert node.name == "test_heat_rate"
        assert node.description == "Test heat rate variance node"
        assert node.states == ["consistent", "moderate_variance", "significant_variance"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_load_factor_node_creation(self):
        """Test LoadFactorNode creation and properties."""
        node = LoadFactorNode("test_load_factor", "Test load factor node")
        
        assert node.name == "test_load_factor"
        assert node.description == "Test load factor node"
        assert node.states == ["low_demand", "normal_demand", "peak_demand"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_market_tightness_node_creation(self):
        """Test MarketTightnessNode creation and properties."""
        node = MarketTightnessNode("test_market_tightness", "Test market tightness node")
        
        assert node.name == "test_market_tightness"
        assert node.description == "Test market tightness node"
        assert node.states == ["surplus", "balanced", "tight"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_competitive_context_node_creation(self):
        """Test CompetitiveContextNode creation and properties."""
        node = CompetitiveContextNode("test_competitive", "Test competitive context node")
        
        assert node.name == "test_competitive"
        assert node.description == "Test competitive context node"
        assert node.states == ["competitive", "concentrated", "monopolistic"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_transmission_constraint_node_creation(self):
        """Test TransmissionConstraintNode creation and properties."""
        node = TransmissionConstraintNode("test_transmission", "Test transmission constraint node")
        
        assert node.name == "test_transmission"
        assert node.description == "Test transmission constraint node"
        assert node.states == ["unconstrained", "moderate_constraints", "severe_constraints"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_bid_shape_anomaly_node_creation(self):
        """Test BidShapeAnomalyNode creation and properties."""
        node = BidShapeAnomalyNode("test_bid_shape", "Test bid shape anomaly node")
        
        assert node.name == "test_bid_shape"
        assert node.description == "Test bid shape anomaly node"
        assert node.states == ["normal_curve", "stepped_curve", "manipulative_curve"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_offer_withdrawal_pattern_node_creation(self):
        """Test OfferWithdrawalPatternNode creation and properties."""
        node = OfferWithdrawalPatternNode("test_withdrawal", "Test offer withdrawal pattern node")
        
        assert node.name == "test_withdrawal"
        assert node.description == "Test offer withdrawal pattern node"
        assert node.states == ["normal_availability", "selective_withdrawal", "systematic_withholding"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_cross_plant_coordination_node_creation(self):
        """Test CrossPlantCoordinationNode creation and properties."""
        node = CrossPlantCoordinationNode("test_coordination", "Test cross plant coordination node")
        
        assert node.name == "test_coordination"
        assert node.description == "Test cross plant coordination node"
        assert node.states == ["independent_operation", "coordinated_operation", "systematic_coordination"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_capacity_utilization_node_creation(self):
        """Test CapacityUtilizationNode creation and properties."""
        node = CapacityUtilizationNode("test_capacity", "Test capacity utilization node")
        
        assert node.name == "test_capacity"
        assert node.description == "Test capacity utilization node"
        assert node.states == ["full_utilization", "partial_utilization", "artificial_limitation"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_markup_consistency_node_creation(self):
        """Test MarkupConsistencyNode creation and properties."""
        node = MarkupConsistencyNode("test_markup", "Test markup consistency node")
        
        assert node.name == "test_markup"
        assert node.description == "Test markup consistency node"
        assert node.states == ["consistent_markup", "variable_markup", "strategic_markup"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_opportunity_pricing_node_creation(self):
        """Test OpportunityPricingNode creation and properties."""
        node = OpportunityPricingNode("test_opportunity", "Test opportunity pricing node")
        
        assert node.name == "test_opportunity"
        assert node.description == "Test opportunity pricing node"
        assert node.states == ["cost_based", "opportunistic", "exploitative"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_fuel_price_correlation_node_creation(self):
        """Test FuelPriceCorrelationNode creation and properties."""
        node = FuelPriceCorrelationNode("test_correlation", "Test fuel price correlation node")
        
        assert node.name == "test_correlation"
        assert node.description == "Test fuel price correlation node"
        assert node.states == ["strong_correlation", "weak_correlation", "no_correlation"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_withholding_latent_intent_node_creation(self):
        """Test WithholdingLatentIntentNode creation and properties."""
        node = WithholdingLatentIntentNode("test_intent", "Test withholding latent intent node")
        
        assert node.name == "test_intent"
        assert node.description == "Test withholding latent intent node"
        assert node.states == ["no_withholding_intent", "potential_withholding", "clear_withholding_intent"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)
    
    def test_withholding_latent_intent_node_intent_strength(self):
        """Test WithholdingLatentIntentNode intent strength calculation."""
        node = WithholdingLatentIntentNode("test_intent", "Test withholding latent intent node")
        
        # Test with empty evidence
        evidence = {}
        strength = node.get_intent_strength(evidence)
        assert strength == 0.0
        
        # Test with partial evidence
        evidence = {
            "marginal_cost_deviation": 0.8,
            "fuel_cost_variance": 0.6,
            "market_tightness": 0.7
        }
        strength = node.get_intent_strength(evidence)
        expected = 0.25 * 0.8 + 0.15 * 0.6 + 0.15 * 0.7  # Based on weights in implementation
        assert strength == pytest.approx(expected, abs=1e-10)
        
        # Test with complete evidence
        evidence = {
            "marginal_cost_deviation": 1.0,
            "fuel_cost_variance": 0.9,
            "plant_efficiency": 0.8,
            "market_tightness": 0.9,
            "load_factor": 0.8,
            "bid_shape_anomaly": 0.8,
            "capacity_utilization": 0.8,
            "profit_motivation": 0.6
        }
        strength = node.get_intent_strength(evidence)
        expected = (0.25 * 1.0 + 0.15 * 0.9 + 0.10 * 0.8 + 0.15 * 0.9 + 
                   0.10 * 0.8 + 0.10 * 0.8 + 0.10 * 0.8 + 0.05 * 0.6)
        assert strength == pytest.approx(expected, abs=1e-10)
        assert strength <= 1.0  # Should be capped at 1.0
    
    def test_economic_withholding_risk_node_creation(self):
        """Test EconomicWithholdingRiskNode creation and properties."""
        node = EconomicWithholdingRiskNode("test_risk", "Test economic withholding risk node")
        
        assert node.name == "test_risk"
        assert node.description == "Test economic withholding risk node"
        assert node.states == ["no_withholding", "potential_withholding", "clear_withholding"]
        assert len(node.fallback_prior) == 3
        assert sum(node.fallback_prior) == pytest.approx(1.0, abs=1e-10)


class TestEconomicWithholdingNodesManager:
    """Test the EconomicWithholdingNodes manager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.nodes_manager = EconomicWithholdingNodes()
    
    def test_nodes_manager_initialization(self):
        """Test EconomicWithholdingNodes initialization."""
        assert hasattr(self.nodes_manager, 'FUEL_COST_VARIANCE')
        assert hasattr(self.nodes_manager, 'PLANT_EFFICIENCY')
        assert hasattr(self.nodes_manager, 'MARGINAL_COST_DEVIATION')
        assert hasattr(self.nodes_manager, 'ECONOMIC_WITHHOLDING_RISK')
        assert hasattr(self.nodes_manager, 'node_definitions')
        
        # Check that all expected nodes are defined
        expected_nodes = [
            'fuel_cost_variance', 'plant_efficiency', 'marginal_cost_deviation',
            'heat_rate_variance', 'load_factor', 'market_tightness',
            'competitive_context', 'transmission_constraint', 'bid_shape_anomaly',
            'offer_withdrawal_pattern', 'cross_plant_coordination', 'capacity_utilization',
            'markup_consistency', 'opportunity_pricing', 'fuel_price_correlation',
            'withholding_latent_intent', 'economic_withholding_risk'
        ]
        
        for node_name in expected_nodes:
            assert node_name in self.nodes_manager.node_definitions
    
    def test_get_node_valid(self):
        """Test getting a valid node."""
        node = self.nodes_manager.get_node('fuel_cost_variance')
        assert node is not None
        assert node.name == 'fuel_cost_variance'
        assert isinstance(node, FuelCostVarianceNode)
    
    def test_get_node_invalid(self):
        """Test getting an invalid node."""
        node = self.nodes_manager.get_node('nonexistent_node')
        assert node is None
    
    def test_get_all_nodes(self):
        """Test getting all nodes."""
        all_nodes = self.nodes_manager.get_all_nodes()
        assert isinstance(all_nodes, dict)
        assert len(all_nodes) > 0
        
        # Check that all nodes are properly instantiated
        for node_name, node in all_nodes.items():
            assert node is not None
            assert hasattr(node, 'name')
            assert hasattr(node, 'states')
            assert hasattr(node, 'fallback_prior')
    
    def test_get_evidence_nodes(self):
        """Test getting evidence nodes only."""
        evidence_nodes = self.nodes_manager.get_evidence_nodes()
        assert isinstance(evidence_nodes, dict)
        assert len(evidence_nodes) > 0
        
        # Should not include outcome nodes
        assert 'economic_withholding_risk' not in evidence_nodes
        # Should include evidence nodes
        assert 'fuel_cost_variance' in evidence_nodes
        assert 'marginal_cost_deviation' in evidence_nodes
    
    def test_get_node_states(self):
        """Test getting node states."""
        states = self.nodes_manager.get_node_states('fuel_cost_variance')
        assert states == ["aligned", "moderate_variance", "high_variance"]
        
        # Test invalid node
        states = self.nodes_manager.get_node_states('nonexistent_node')
        assert states is None
    
    def test_get_standard_nodes(self):
        """Test getting standard (non-latent intent) nodes."""
        standard_nodes = self.nodes_manager.get_standard_nodes()
        assert isinstance(standard_nodes, list)
        assert len(standard_nodes) > 0
        assert 'fuel_cost_variance' in standard_nodes
        assert 'economic_withholding_risk' in standard_nodes
        # Should not include latent intent node
        assert 'withholding_latent_intent' not in standard_nodes
    
    def test_get_latent_intent_nodes(self):
        """Test getting latent intent model nodes."""
        latent_nodes = self.nodes_manager.get_latent_intent_nodes()
        assert isinstance(latent_nodes, list)
        assert len(latent_nodes) > 0
        assert 'fuel_cost_variance' in latent_nodes
        assert 'withholding_latent_intent' in latent_nodes
        assert 'economic_withholding_risk' in latent_nodes
    
    def test_validate_node_value_valid_state_name(self):
        """Test validating node value with valid state name."""
        is_valid = self.nodes_manager.validate_node_value('fuel_cost_variance', 'aligned')
        assert is_valid is True
        
        is_valid = self.nodes_manager.validate_node_value('load_factor', 'peak_demand')
        assert is_valid is True
    
    def test_validate_node_value_valid_state_index(self):
        """Test validating node value with valid state index."""
        is_valid = self.nodes_manager.validate_node_value('fuel_cost_variance', 0)
        assert is_valid is True
        
        is_valid = self.nodes_manager.validate_node_value('fuel_cost_variance', 2)
        assert is_valid is True
    
    def test_validate_node_value_invalid_state_name(self):
        """Test validating node value with invalid state name."""
        is_valid = self.nodes_manager.validate_node_value('fuel_cost_variance', 'invalid_state')
        assert is_valid is False
    
    def test_validate_node_value_invalid_state_index(self):
        """Test validating node value with invalid state index."""
        is_valid = self.nodes_manager.validate_node_value('fuel_cost_variance', 5)
        assert is_valid is False
        
        is_valid = self.nodes_manager.validate_node_value('fuel_cost_variance', -1)
        assert is_valid is False
    
    def test_validate_node_value_invalid_node(self):
        """Test validating node value for invalid node."""
        is_valid = self.nodes_manager.validate_node_value('nonexistent_node', 'any_value')
        assert is_valid is False
    
    def test_node_definitions_structure(self):
        """Test that node definitions have the correct structure."""
        for node_name, node_def in self.nodes_manager.node_definitions.items():
            assert 'type' in node_def
            assert 'class' in node_def
            assert 'states' in node_def
            assert 'description' in node_def
            assert 'fallback_prior' in node_def
            
            # Check that fallback_prior sums to 1.0
            assert sum(node_def['fallback_prior']) == pytest.approx(1.0, abs=1e-10)
            
            # Check that states match fallback_prior length
            assert len(node_def['states']) == len(node_def['fallback_prior'])
    
    def test_reused_nodes_included(self):
        """Test that reused nodes from existing library are properly included."""
        reused_nodes = [
            'price_impact_ratio', 'volume_participation', 'liquidity_context',
            'order_clustering', 'benchmark_timing', 'profit_motivation'
        ]
        
        for node_name in reused_nodes:
            assert node_name in self.nodes_manager.node_definitions
            node = self.nodes_manager.get_node(node_name)
            assert node is not None
    
    def test_energy_specific_nodes_included(self):
        """Test that all energy-specific nodes are properly included."""
        energy_nodes = [
            'fuel_cost_variance', 'plant_efficiency', 'marginal_cost_deviation',
            'heat_rate_variance', 'load_factor', 'market_tightness',
            'competitive_context', 'transmission_constraint', 'bid_shape_anomaly',
            'offer_withdrawal_pattern', 'cross_plant_coordination', 'capacity_utilization',
            'markup_consistency', 'opportunity_pricing', 'fuel_price_correlation'
        ]
        
        for node_name in energy_nodes:
            assert node_name in self.nodes_manager.node_definitions
            node = self.nodes_manager.get_node(node_name)
            assert node is not None


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])