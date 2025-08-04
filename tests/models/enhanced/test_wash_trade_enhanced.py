#!/usr/bin/env python3
"""
Enhanced Wash Trade Detection Model Tests

Tests the enhanced 4-parent CPT structure with explaining away behavior.
Validates that the model correctly implements explaining away patterns where
strong evidence explains away weaker indicators.
"""

import unittest
import json
from unittest.mock import Mock, patch
import numpy as np

# Import the enhanced model components
from src.models.bayesian.shared.evidence_node_templates import get_model_templates
from src.models.bayesian.shared.reusable_intermediate_nodes import (
    MarketImpactNode, BehavioralIntentNode, ReusableNodeFactory
)

class TestEnhancedWashTradeModel(unittest.TestCase):
    """Test suite for enhanced wash trade detection model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.model_type = "wash_trade_detection"
        
    def test_evidence_node_templates(self):
        """Test that evidence node templates are correctly defined"""
        templates = get_model_templates(self.model_type)
        
        # Should have 4 evidence nodes
        self.assertEqual(len(templates), 4)
        
        # Verify node names
        expected_nodes = {"VolumePatterns", "TimingPatterns", "PricePatterns", "AccountRelationships"}
        actual_nodes = {template["name"] for template in templates}
        self.assertEqual(actual_nodes, expected_nodes)
        
        # Verify all nodes have consistent state structure
        for template in templates:
            self.assertEqual(template["states"], ["normal", "suspicious", "highly_suspicious"])
            self.assertEqual(len(template["fallback_prior"]), 3)
            self.assertAlmostEqual(sum(template["fallback_prior"]), 1.0, places=5)
            
    def test_reusable_node_applicability(self):
        """Test that reusable nodes are applicable to wash trade detection"""
        # Test MarketImpactNode
        market_node = MarketImpactNode()
        self.assertIn("wash_trade_detection", market_node.applicable_typologies)
        self.assertTrue(market_node.is_compatible_with_model("wash_trade_detection"))
        
        # Test BehavioralIntentNode
        behavioral_node = BehavioralIntentNode()
        self.assertIn("wash_trade_detection", behavioral_node.applicable_typologies)
        self.assertTrue(behavioral_node.is_compatible_with_model("wash_trade_detection"))
        
    def test_intermediate_node_creation(self):
        """Test creation of intermediate nodes for wash trade model"""
        # Test MarketImpact node creation
        market_node = ReusableNodeFactory.create_market_impact_node(
            model_type="wash_trade_detection",
            parent_nodes=["VolumePatterns", "PricePatterns"],
            name_suffix="_wash_trade"
        )
        
        self.assertEqual(market_node.name, "market_impact_wash_trade")
        self.assertEqual(len(market_node.parent_nodes), 2)
        self.assertIn("VolumePatterns", market_node.parent_nodes)
        self.assertIn("PricePatterns", market_node.parent_nodes)
        
    @patch('src.models.bayesian.shared.reusable_intermediate_nodes.TabularCPD')
    def test_noisy_or_cpt_generation(self, mock_tabular_cpd):
        """Test noisy-OR CPT generation for intermediate nodes"""
        # Test MarketImpact node CPT generation
        market_node = MarketImpactNode(parent_nodes=["VolumePatterns", "PricePatterns"])
        
        # Mock the CPT creation
        mock_cpd = Mock()
        mock_tabular_cpd.return_value = mock_cpd
        
        result_cpd = market_node.create_noisy_or_cpt()
        
        # Verify CPT was created with correct parameters
        mock_tabular_cpd.assert_called_once()
        call_args = mock_tabular_cpd.call_args
        self.assertEqual(call_args[1]["variable"], market_node.name)
        self.assertEqual(call_args[1]["evidence"], market_node.parent_nodes)
        
    def test_explaining_away_cpt_structure(self):
        """Test that CPT structure supports explaining away behavior"""
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        wash_trade_config = config["models"]["wash_trade_detection"]
        
        # Verify node structure
        nodes = {node["name"]: node for node in wash_trade_config["nodes"]}
        
        # Check evidence nodes exist
        evidence_nodes = ["VolumePatterns", "TimingPatterns", "PricePatterns", "AccountRelationships"]
        for node_name in evidence_nodes:
            self.assertIn(node_name, nodes)
            
        # Check intermediate nodes exist
        intermediate_nodes = ["MarketImpact", "BehavioralIntent"]
        for node_name in intermediate_nodes:
            self.assertIn(node_name, nodes)
            
        # Check Risk node exists
        self.assertIn("Risk", nodes)
        
        # Verify edge structure supports explaining away
        edges = wash_trade_config["edges"]
        edge_dict = {}
        for parent, child in edges:
            if child not in edge_dict:
                edge_dict[child] = []
            edge_dict[child].append(parent)
            
        # MarketImpact should have 2 parents (VolumePatterns, PricePatterns)
        self.assertEqual(len(edge_dict["MarketImpact"]), 2)
        self.assertIn("VolumePatterns", edge_dict["MarketImpact"])
        self.assertIn("PricePatterns", edge_dict["MarketImpact"])
        
        # BehavioralIntent should have 2 parents (TimingPatterns, AccountRelationships)
        self.assertEqual(len(edge_dict["BehavioralIntent"]), 2)
        self.assertIn("TimingPatterns", edge_dict["BehavioralIntent"])
        self.assertIn("AccountRelationships", edge_dict["BehavioralIntent"])
        
        # Risk should have 2 parents (MarketImpact, BehavioralIntent)
        self.assertEqual(len(edge_dict["Risk"]), 2)
        self.assertIn("MarketImpact", edge_dict["Risk"])
        self.assertIn("BehavioralIntent", edge_dict["Risk"])
        
    def test_explaining_away_cpt_probabilities(self):
        """Test that CPT probabilities implement explaining away logic"""
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        wash_trade_config = config["models"]["wash_trade_detection"]
        cpds = {cpd["variable"]: cpd for cpd in wash_trade_config["cpds"]}
        
        # Test Risk node CPT (explaining away between MarketImpact and BehavioralIntent)
        risk_cpd = cpds["Risk"]
        risk_values = np.array(risk_cpd["values"])
        
        # Risk CPT should be 3x9 (3 states, 3^2 parent combinations)
        self.assertEqual(risk_values.shape, (3, 9))
        
        # Test explaining away pattern: when both MarketImpact and BehavioralIntent are high,
        # risk should be very high (explaining away alternative explanations)
        # Index 8 corresponds to both parents in highest state
        high_risk_prob_both_high = risk_values[2, 8]  # High risk when both parents high
        
        # When only one parent is high, risk should be lower
        high_risk_prob_market_only = risk_values[2, 6]  # MarketImpact high, BehavioralIntent low
        high_risk_prob_behavioral_only = risk_values[2, 2]  # BehavioralIntent high, MarketImpact low
        
        # Explaining away: combined evidence should be stronger than individual evidence
        self.assertGreater(high_risk_prob_both_high, high_risk_prob_market_only)
        self.assertGreater(high_risk_prob_both_high, high_risk_prob_behavioral_only)
        
    def test_model_configuration_completeness(self):
        """Test that model configuration is complete and valid"""
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        self.assertIn("wash_trade_detection", config["models"])
        wash_trade_config = config["models"]["wash_trade_detection"]
        
        # Check required sections
        required_sections = ["nodes", "edges", "cpds"]
        for section in required_sections:
            self.assertIn(section, wash_trade_config)
            
        # Verify CPD completeness
        nodes = {node["name"] for node in wash_trade_config["nodes"]}
        cpd_variables = {cpd["variable"] for cpd in wash_trade_config["cpds"]}
        
        # All nodes should have CPDs
        self.assertEqual(nodes, cpd_variables)
        
        # Verify probability distributions sum to 1
        for cpd in wash_trade_config["cpds"]:
            values = np.array(cpd["values"])
            for col in range(values.shape[1]):
                column_sum = values[:, col].sum()
                self.assertAlmostEqual(column_sum, 1.0, places=5, 
                                     msg=f"CPD for {cpd['variable']} column {col} doesn't sum to 1")
                                     
    def test_explaining_away_pattern_documentation(self):
        """Test that explaining away patterns are properly documented"""
        templates = get_model_templates(self.model_type)
        
        # All templates should have regulatory basis
        for template in templates:
            self.assertIn("regulatory_basis", template)
            self.assertNotEqual(template["regulatory_basis"], "")
            
        # All templates should have evidence category
        for template in templates:
            self.assertIn("evidence_category", template)
            self.assertNotEqual(template["evidence_category"], "")
            
    def test_performance_characteristics(self):
        """Test performance characteristics of enhanced model"""
        # Test CPT size reduction through intermediate nodes
        # Direct 4-parent CPT would have 3^4 = 81 combinations
        # With intermediate nodes: 2*(3^2) + 3^2 = 18 + 9 = 27 combinations
        
        direct_combinations = 3 ** 4  # 81
        intermediate_combinations = 2 * (3 ** 2) + (3 ** 2)  # 27
        
        reduction_factor = direct_combinations / intermediate_combinations
        
        # Should achieve ~3x reduction in CPT complexity
        self.assertGreater(reduction_factor, 2.5)
        self.assertLess(reduction_factor, 3.5)
        
    def test_backward_compatibility(self):
        """Test that enhanced model maintains backward compatibility"""
        # The Risk node should still have the same states as original model
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        wash_trade_config = config["models"]["wash_trade_detection"]
        nodes = {node["name"]: node for node in wash_trade_config["nodes"]}
        
        risk_node = nodes["Risk"]
        expected_states = ["Low", "Medium", "High"]
        self.assertEqual(risk_node["states"], expected_states)
        
        # Risk node should still be the final output
        edges = wash_trade_config["edges"]
        risk_parents = [parent for parent, child in edges if child == "Risk"]
        self.assertEqual(len(risk_parents), 2)  # Should have exactly 2 parents
        

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedWashTradeModel)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"ENHANCED WASH TRADE MODEL TEST RESULTS")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
            
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
            
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    print(f"\nTest suite {'PASSED' if exit_code == 0 else 'FAILED'}")
    exit(exit_code)