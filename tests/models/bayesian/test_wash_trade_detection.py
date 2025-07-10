"""
Tests for Wash Trade Detection Model.

This module provides comprehensive tests for the wash trade detection model
including unit tests, integration tests, and scenario testing.
"""

import unittest
from datetime import datetime
from typing import Dict, Any

from src.models.bayesian.wash_trade_detection import (
    WashTradeDetectionModel,
    WashTradeDetectionNodes,
    WashTradeDetectionConfig
)


class TestWashTradeDetectionModel(unittest.TestCase):
    """Test cases for WashTradeDetectionModel."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'wash_trade_probability_threshold': 0.7,
            'signal_distortion_threshold': 0.6,
            'algo_reaction_threshold': 0.65,
            'use_latent_intent': True
        }
        self.model = WashTradeDetectionModel(use_latent_intent=True, config=self.config)
    
    def test_model_initialization(self):
        """Test model initialization."""
        self.assertIsNotNone(self.model)
        self.assertEqual(self.model.model_version, '1.0.0')
        self.assertTrue(self.model.use_latent_intent)
        self.assertFalse(self.model.is_trained)
    
    def test_get_model_info(self):
        """Test model information retrieval."""
        info = self.model.get_model_info()
        
        self.assertEqual(info['model_name'], 'wash_trade_detection')
        self.assertEqual(info['model_version'], '1.0.0')
        self.assertTrue(info['use_latent_intent'])
        self.assertIn('core_nodes', info)
        self.assertIn('supporting_nodes', info)
    
    def test_validate_evidence_valid(self):
        """Test evidence validation with valid data."""
        evidence = {
            'trade_id': 'TEST_001',
            'timestamp': '2025-01-01T10:00:00Z',
            'counterparty_entity_match': 0.8,
            'signal_distortion_index': 0.6
        }
        
        self.assertTrue(self.model._validate_evidence(evidence))
    
    def test_validate_evidence_invalid(self):
        """Test evidence validation with invalid data."""
        evidence = {
            'counterparty_entity_match': 0.8,
            'signal_distortion_index': 0.6
        }
        
        self.assertFalse(self.model._validate_evidence(evidence))
    
    def test_wash_trade_likelihood_prediction_high(self):
        """Test wash trade likelihood prediction with high probability indicators."""
        evidence = {
            'lei_exact_match': True,
            'counterparty_entity_match': 0.9,
            'algo_framework_match': 0.8,
            'trade_time_delta': 0.5,
            'implied_strategy_execution': 0.7
        }
        
        result = self.model._predict_wash_trade_likelihood(evidence)
        
        self.assertEqual(result['state'], 'high_probability')
        self.assertGreater(result['probability'], 0.7)
        self.assertGreater(result['likelihood_score'], 0.7)
    
    def test_wash_trade_likelihood_prediction_low(self):
        """Test wash trade likelihood prediction with low probability indicators."""
        evidence = {
            'lei_exact_match': False,
            'counterparty_entity_match': 0.1,
            'algo_framework_match': 0.1,
            'trade_time_delta': 5000,
            'implied_strategy_execution': 0.1
        }
        
        result = self.model._predict_wash_trade_likelihood(evidence)
        
        self.assertEqual(result['state'], 'low_probability')
        self.assertLess(result['probability'], 0.4)
        self.assertLess(result['likelihood_score'], 0.4)
    
    def test_signal_distortion_prediction_high(self):
        """Test signal distortion prediction with high distortion indicators."""
        evidence = {
            'order_book_impact': 0.8,
            'quote_frequency_distortion': 0.9,
            'spread_manipulation': 0.7,
            'volume_at_best_change': 0.8,
            'order_book_imbalance_change': 0.6,
            'quote_frequency_ratio': 3.0
        }
        
        result = self.model._predict_signal_distortion_index(evidence)
        
        self.assertEqual(result['state'], 'high_distortion')
        self.assertGreater(result['probability'], 0.7)
        self.assertGreater(result['distortion_score'], 0.6)
    
    def test_algo_reaction_sensitivity_prediction(self):
        """Test algorithmic reaction sensitivity prediction."""
        evidence = {
            'order_flow_clustering': 0.8,
            'reaction_time_delta': 0.9,
            'passive_aggressive_ratio': 0.7,
            'algo_reaction_time_ms': 30,
            'order_clustering_ratio': 0.8,
            'passive_aggressive_change': 0.5
        }
        
        result = self.model._predict_algo_reaction_sensitivity(evidence)
        
        self.assertEqual(result['state'], 'high_sensitivity')
        self.assertGreater(result['probability'], 0.6)
        self.assertGreater(result['sensitivity_score'], 0.6)
    
    def test_strategy_leg_overlap_prediction(self):
        """Test strategy leg overlap prediction."""
        evidence = {
            'commodity_leg_matching': 0.8,
            'third_party_risk_validation': 0.7,
            'time_spread_detected': True,
            'cross_contract_matching': 0.6,
            'same_entity_legs': 0.9
        }
        
        result = self.model._predict_strategy_leg_overlap(evidence)
        
        self.assertEqual(result['state'], 'full_overlap')
        self.assertGreater(result['probability'], 0.7)
        self.assertGreater(result['overlap_score'], 0.7)
    
    def test_price_impact_anomaly_prediction(self):
        """Test price impact anomaly prediction."""
        evidence = {
            'mean_reversion_pattern': 0.8,
            'price_spike_fade': 0.7,
            'volatility_baseline_deviation': 0.6,
            'immediate_reversion': 5,
            'price_spike_magnitude': 0.03,
            'volatility_z_score': 4.0
        }
        
        result = self.model._predict_price_impact_anomaly(evidence)
        
        self.assertEqual(result['state'], 'anomalous_impact')
        self.assertGreater(result['probability'], 0.6)
        self.assertGreater(result['anomaly_score'], 0.6)
    
    def test_implied_liquidity_conflict_prediction(self):
        """Test implied liquidity conflict prediction."""
        evidence = {
            'venue_implied_matching': 0.8,
            'leg_execution_source': 0.7,
            'implied_matching_detected': True,
            'internal_execution_ratio': 0.8,
            'strategy_order_matching': 0.6
        }
        
        result = self.model._predict_implied_liquidity_conflict(evidence)
        
        self.assertEqual(result['state'], 'clear_conflict')
        self.assertGreater(result['probability'], 0.7)
        self.assertGreater(result['conflict_score'], 0.7)
    
    def test_full_prediction_wash_trade_detected(self):
        """Test full prediction with wash trade detection scenario."""
        evidence = {
            'trade_id': 'TEST_WASH_001',
            'timestamp': '2025-01-01T10:00:00Z',
            'lei_exact_match': True,
            'counterparty_entity_match': 0.9,
            'algo_framework_match': 0.8,
            'order_book_impact': 0.7,
            'quote_frequency_distortion': 0.8,
            'algo_reaction_time_ms': 25,
            'commodity_leg_matching': 0.8,
            'mean_reversion_pattern': 0.7,
            'venue_implied_matching': 0.7
        }
        
        result = self.model.predict(evidence)
        
        self.assertTrue(result['wash_trade_detected'])
        self.assertGreater(result['confidence_score'], 0.6)
        self.assertGreater(result['risk_score'], 0.6)
        self.assertIn('explanation', result)
        self.assertIn('core_requirements', result)
    
    def test_full_prediction_no_wash_trade(self):
        """Test full prediction with no wash trade detection scenario."""
        evidence = {
            'trade_id': 'TEST_NORMAL_001',
            'timestamp': '2025-01-01T10:00:00Z',
            'lei_exact_match': False,
            'counterparty_entity_match': 0.1,
            'algo_framework_match': 0.1,
            'order_book_impact': 0.2,
            'quote_frequency_distortion': 0.1,
            'algo_reaction_time_ms': 500,
            'commodity_leg_matching': 0.1,
            'mean_reversion_pattern': 0.2,
            'venue_implied_matching': 0.1
        }
        
        result = self.model.predict(evidence)
        
        self.assertFalse(result['wash_trade_detected'])
        self.assertLess(result['confidence_score'], 0.7)
        self.assertLess(result['risk_score'], 0.7)
        self.assertIn('explanation', result)


class TestWashTradeDetectionNodes(unittest.TestCase):
    """Test cases for WashTradeDetectionNodes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.nodes = WashTradeDetectionNodes()
    
    def test_nodes_initialization(self):
        """Test nodes initialization."""
        self.assertIsNotNone(self.nodes)
        self.assertIsNotNone(self.nodes.node_definitions)
        self.assertGreater(len(self.nodes.node_definitions), 0)
    
    def test_get_core_requirement_nodes(self):
        """Test getting core requirement nodes."""
        core_nodes = self.nodes.get_core_requirement_nodes()
        
        expected_core_nodes = [
            'wash_trade_likelihood',
            'signal_distortion_index',
            'algo_reaction_sensitivity',
            'strategy_leg_overlap',
            'price_impact_anomaly',
            'implied_liquidity_conflict'
        ]
        
        self.assertEqual(len(core_nodes), 6)
        for node in expected_core_nodes:
            self.assertIn(node, core_nodes)
    
    def test_create_node(self):
        """Test node creation."""
        node = self.nodes.create_node('wash_trade_likelihood')
        
        self.assertIsNotNone(node)
        self.assertEqual(node.name, 'wash_trade_likelihood')
    
    def test_get_node_statistics(self):
        """Test node statistics."""
        stats = self.nodes.get_node_statistics()
        
        self.assertIn('total_nodes', stats)
        self.assertIn('core_requirement_nodes', stats)
        self.assertIn('supporting_evidence_nodes', stats)
        self.assertEqual(stats['core_requirement_nodes'], 6)
        self.assertGreater(stats['total_nodes'], 20)
    
    def test_validate_node_compatibility(self):
        """Test node compatibility validation."""
        # Test valid node
        self.assertTrue(self.nodes.validate_node_compatibility('wash_trade_likelihood'))
        
        # Test invalid node
        self.assertFalse(self.nodes.validate_node_compatibility('nonexistent_node'))


class TestWashTradeDetectionConfig(unittest.TestCase):
    """Test cases for WashTradeDetectionConfig."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = WashTradeDetectionConfig()
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        self.assertIsNotNone(self.config)
        self.assertEqual(self.config.get('model_name'), 'wash_trade_detection')
        self.assertEqual(self.config.get('model_version'), '1.0.0')
    
    def test_get_detection_thresholds(self):
        """Test getting detection thresholds."""
        thresholds = self.config.get_detection_thresholds()
        
        self.assertIn('wash_trade_probability_threshold', thresholds)
        self.assertIn('signal_distortion_threshold', thresholds)
        self.assertIn('algo_reaction_threshold', thresholds)
        
        # Validate threshold ranges
        for threshold_name, threshold_value in thresholds.items():
            self.assertGreaterEqual(threshold_value, 0.0)
            self.assertLessEqual(threshold_value, 1.0)
    
    def test_get_time_parameters(self):
        """Test getting time parameters."""
        time_params = self.config.get_time_parameters()
        
        self.assertIn('algo_reaction_window_ms', time_params)
        self.assertIn('price_impact_window_seconds', time_params)
        self.assertIn('mean_reversion_window_seconds', time_params)
        
        # Validate time parameters are positive
        for param_name, param_value in time_params.items():
            self.assertGreater(param_value, 0)
    
    def test_get_risk_factor_weights(self):
        """Test getting risk factor weights."""
        weights = self.config.get_risk_factor_weights()
        
        expected_weights = [
            'wash_trade_likelihood',
            'signal_distortion_index',
            'algo_reaction_sensitivity',
            'strategy_leg_overlap',
            'price_impact_anomaly',
            'implied_liquidity_conflict'
        ]
        
        for weight_name in expected_weights:
            self.assertIn(weight_name, weights)
            self.assertGreater(weights[weight_name], 0.0)
        
        # Weights should sum to approximately 1.0
        total_weight = sum(weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=1)
    
    def test_validate_configuration(self):
        """Test configuration validation."""
        self.assertTrue(self.config.validate_configuration())
    
    def test_custom_configuration(self):
        """Test custom configuration override."""
        custom_config = {
            'wash_trade_probability_threshold': 0.8,
            'model_version': '1.1.0'
        }
        
        config = WashTradeDetectionConfig(custom_config)
        
        self.assertEqual(config.get('wash_trade_probability_threshold'), 0.8)
        self.assertEqual(config.get('model_version'), '1.1.0')
        self.assertEqual(config.get('model_name'), 'wash_trade_detection')  # Default value
    
    def test_is_feature_enabled(self):
        """Test feature enablement checking."""
        self.assertTrue(self.config.is_feature_enabled('use_latent_intent'))
        self.assertTrue(self.config.is_feature_enabled('enable_signal_distortion'))
        self.assertFalse(self.config.is_feature_enabled('nonexistent_feature'))


class TestWashTradeDetectionScenarios(unittest.TestCase):
    """Test cases for specific wash trade detection scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.model = WashTradeDetectionModel(use_latent_intent=True)
    
    def test_lei_exact_match_scenario(self):
        """Test scenario with exact LEI match (high wash trade probability)."""
        evidence = {
            'trade_id': 'LEI_EXACT_001',
            'timestamp': '2025-01-01T10:00:00Z',
            'lei_exact_match': True,
            'trade_time_delta': 0,
            'counterparty_entity_match': 1.0,
            'algo_framework_match': 0.9
        }
        
        result = self.model.predict(evidence)
        
        self.assertTrue(result['wash_trade_detected'])
        self.assertGreater(result['confidence_score'], 0.7)
    
    def test_commodity_time_spread_scenario(self):
        """Test scenario with commodity derivatives time spreads."""
        evidence = {
            'trade_id': 'COMMODITY_SPREAD_001',
            'timestamp': '2025-01-01T10:00:00Z',
            'time_spread_detected': True,
            'commodity_leg_matching': 0.9,
            'same_entity_legs': 0.8,
            'third_party_risk_validation': 0.1,  # No real risk transfer
            'cross_contract_matching': 0.7
        }
        
        result = self.model.predict(evidence)
        
        # Should detect strategy leg overlap
        strategy_overlap = result['core_requirements']['strategy_leg_overlap']
        self.assertEqual(strategy_overlap['state'], 'full_overlap')
    
    def test_algo_reaction_fast_response_scenario(self):
        """Test scenario with fast algorithmic reaction (<100ms)."""
        evidence = {
            'trade_id': 'ALGO_REACTION_001',
            'timestamp': '2025-01-01T10:00:00Z',
            'algo_reaction_time_ms': 25,
            'order_clustering_ratio': 0.8,
            'passive_aggressive_change': 0.6,
            'order_flow_clustering': 0.9
        }
        
        result = self.model.predict(evidence)
        
        # Should detect high algo reaction sensitivity
        algo_reaction = result['core_requirements']['algo_reaction_sensitivity']
        self.assertEqual(algo_reaction['state'], 'high_sensitivity')
    
    def test_signal_distortion_orderbook_scenario(self):
        """Test scenario with order book signal distortion."""
        evidence = {
            'trade_id': 'SIGNAL_DISTORTION_001',
            'timestamp': '2025-01-01T10:00:00Z',
            'volume_at_best_change': 0.8,
            'order_book_imbalance_change': 0.7,
            'quote_frequency_ratio': 4.0,
            'spread_manipulation': 0.6
        }
        
        result = self.model.predict(evidence)
        
        # Should detect high signal distortion
        signal_distortion = result['core_requirements']['signal_distortion_index']
        self.assertEqual(signal_distortion['state'], 'high_distortion')
    
    def test_price_impact_anomaly_scenario(self):
        """Test scenario with price impact anomalies."""
        evidence = {
            'trade_id': 'PRICE_ANOMALY_001',
            'timestamp': '2025-01-01T10:00:00Z',
            'immediate_reversion': 3,  # 3 seconds for reversion
            'price_spike_magnitude': 0.04,  # 4% spike
            'volatility_z_score': 5.0,  # Extreme deviation
            'mean_reversion_pattern': 0.9
        }
        
        result = self.model.predict(evidence)
        
        # Should detect anomalous price impact
        price_impact = result['core_requirements']['price_impact_anomaly']
        self.assertEqual(price_impact['state'], 'anomalous_impact')
    
    def test_implied_liquidity_venue_scenario(self):
        """Test scenario with venue-level implied liquidity conflicts."""
        evidence = {
            'trade_id': 'IMPLIED_LIQUIDITY_001',
            'timestamp': '2025-01-01T10:00:00Z',
            'implied_matching_detected': True,
            'internal_execution_ratio': 0.9,
            'strategy_order_matching': 0.8,
            'venue_implied_matching': 0.8
        }
        
        result = self.model.predict(evidence)
        
        # Should detect clear liquidity conflict
        liquidity_conflict = result['core_requirements']['implied_liquidity_conflict']
        self.assertEqual(liquidity_conflict['state'], 'clear_conflict')


if __name__ == '__main__':
    unittest.main()