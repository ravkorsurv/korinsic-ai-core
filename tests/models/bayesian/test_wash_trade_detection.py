"""
Tests for wash trade detection system
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.models.bayesian.wash_trade_detection.model import WashTradeDetectionModel
from src.models.bayesian.wash_trade_detection.config import WashTradeDetectionConfig
from src.models.bayesian.wash_trade_detection.nodes import *
from src.models.bayesian.registry import ModelRegistry
from src.models.bayesian.shared.node_library import NodeLibrary
from src.core.evidence_mapper import EvidenceMapper
from src.core.regulatory_explainability import RegulatoryExplainability

class TestWashTradeDetectionModel:
    """Test cases for wash trade detection model"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = WashTradeDetectionConfig()
        self.model = WashTradeDetectionModel(self.config)
        self.evidence_mapper = EvidenceMapper()
        self.reg_explainability = RegulatoryExplainability()
        
    def test_model_initialization(self):
        """Test model initialization"""
        assert self.model.config == self.config
        assert self.model.network is not None
        assert len(self.model.network.nodes) > 0
        
    def test_registry_integration(self):
        """Test model registry integration"""
        registry = ModelRegistry()
        assert 'wash_trade_detection' in registry.models
        assert callable(registry.models['wash_trade_detection'])
        
    def test_node_library_integration(self):
        """Test node library integration"""
        library = NodeLibrary()
        
        # Test wash trade specific nodes
        wash_trade_nodes = [
            'WashTradeLikelihood',
            'SignalDistortionIndex',
            'AlgoReactionSensitivity',
            'StrategyLegOverlap',
            'PriceImpactAnomaly',
            'ImpliedLiquidityConflict'
        ]
        
        for node_name in wash_trade_nodes:
            assert node_name in library.nodes
            assert callable(library.nodes[node_name])
            
    def test_high_risk_wash_trade_prediction(self):
        """Test high risk wash trade prediction"""
        
        # Mock high risk wash trade data
        market_data = {
            'entity_a_lei': 'LEI123456789',
            'entity_b_lei': 'LEI123456789',  # Same LEI
            'entity_relationship': 'same_entity',
            'algo_framework_match': True,
            'timing_correlation': 0.95,
            'volume_imbalance': 0.8,
            'quote_flicker_frequency': 50,
            'order_book_depth_distortion': 0.7,
            'algo_reaction_time': 0.05,  # 50ms
            'post_trade_reaction_count': 15,
            'commodity_venue_overlap': 0.9,
            'strategy_leg_correlation': 0.85,
            'price_impact_magnitude': 0.6,
            'mean_reversion_speed': 0.8,
            'venue_liquidity_conflict': 0.7,
            'implied_matching_rate': 0.75
        }
        
        result = self.model.predict(market_data)
        
        assert result['risk_level'] == 'high'
        assert result['overall_score'] > 0.7
        assert 'WashTradeLikelihood' in result['node_states']
        assert 'SignalDistortionIndex' in result['node_states']
        
    def test_medium_risk_wash_trade_prediction(self):
        """Test medium risk wash trade prediction"""
        
        market_data = {
            'entity_a_lei': 'LEI123456789',
            'entity_b_lei': 'LEI987654321',  # Different LEI
            'entity_relationship': 'affiliate',
            'algo_framework_match': True,
            'timing_correlation': 0.7,
            'volume_imbalance': 0.5,
            'quote_flicker_frequency': 20,
            'order_book_depth_distortion': 0.4,
            'algo_reaction_time': 0.08,  # 80ms
            'post_trade_reaction_count': 8,
            'commodity_venue_overlap': 0.6,
            'strategy_leg_correlation': 0.6,
            'price_impact_magnitude': 0.4,
            'mean_reversion_speed': 0.6,
            'venue_liquidity_conflict': 0.4,
            'implied_matching_rate': 0.45
        }
        
        result = self.model.predict(market_data)
        
        assert result['risk_level'] == 'medium'
        assert 0.4 < result['overall_score'] < 0.8
        
    def test_low_risk_wash_trade_prediction(self):
        """Test low risk wash trade prediction"""
        
        market_data = {
            'entity_a_lei': 'LEI123456789',
            'entity_b_lei': 'LEI987654321',  # Different LEI
            'entity_relationship': 'unrelated',
            'algo_framework_match': False,
            'timing_correlation': 0.3,
            'volume_imbalance': 0.2,
            'quote_flicker_frequency': 5,
            'order_book_depth_distortion': 0.1,
            'algo_reaction_time': 0.2,  # 200ms
            'post_trade_reaction_count': 2,
            'commodity_venue_overlap': 0.2,
            'strategy_leg_correlation': 0.3,
            'price_impact_magnitude': 0.1,
            'mean_reversion_speed': 0.3,
            'venue_liquidity_conflict': 0.1,
            'implied_matching_rate': 0.2
        }
        
        result = self.model.predict(market_data)
        
        assert result['risk_level'] == 'low'
        assert result['overall_score'] < 0.4
        
    def test_evidence_mapping_integration(self):
        """Test evidence mapping integration"""
        
        # Test wash trade likelihood evidence mapping
        evidence = self.evidence_mapper.map_wash_trade_likelihood({
            'entity_a_lei': 'LEI123456789',
            'entity_b_lei': 'LEI123456789',
            'entity_relationship': 'same_entity',
            'algo_framework_match': True,
            'timing_correlation': 0.9
        })
        
        assert evidence['wash_trade_likelihood'] > 0.7
        assert evidence['entity_match_score'] > 0.8
        
        # Test signal distortion evidence mapping
        evidence = self.evidence_mapper.map_signal_distortion_index({
            'volume_imbalance': 0.8,
            'quote_flicker_frequency': 50,
            'order_book_depth_distortion': 0.7
        })
        
        assert evidence['signal_distortion_index'] > 0.6
        assert evidence['order_book_impact'] > 0.7
        
    def test_regulatory_explainability_integration(self):
        """Test regulatory explainability integration"""
        
        # Mock high risk result
        risk_result = {
            'overall_score': 0.85,
            'risk_level': 'high',
            'confidence': 0.92
        }
        
        evidence_factors = {
            'WashTradeLikelihood': 2,
            'SignalDistortionIndex': 2,
            'AlgoReactionSensitivity': 1,
            'StrategyLegOverlap': 2,
            'PriceImpactAnomaly': 1,
            'ImpliedLiquidityConflict': 1
        }
        
        rationale = self.reg_explainability.generate_regulatory_rationale(
            alert_id='WASH_TRADE_001',
            risk_result=risk_result,
            evidence_factors=evidence_factors,
            model_type='wash_trade_detection'
        )
        
        assert rationale.alert_id == 'WASH_TRADE_001'
        assert rationale.risk_level == 'high'
        assert rationale.overall_score == 0.85
        assert 'wash trade activity' in rationale.deterministic_narrative.lower()
        assert rationale.regulatory_basis == 'MiFID II Article 48 - Wash trades and matched orders'
        assert len(rationale.inference_paths) > 0
        assert len(rationale.key_evidence) > 0
        
    def test_wash_trade_narrative_generation(self):
        """Test wash trade specific narrative generation"""
        
        evidence_factors = {
            'WashTradeLikelihood': 2,
            'SignalDistortionIndex': 2,
            'AlgoReactionSensitivity': 2,
            'StrategyLegOverlap': 1,
            'PriceImpactAnomaly': 2,
            'ImpliedLiquidityConflict': 1
        }
        
        narrative = self.reg_explainability._generate_wash_trade_narrative(
            {'overall_score': 0.85, 'risk_level': 'high'},
            evidence_factors
        )
        
        # Check that narrative includes all key indicators
        assert 'wash trade' in narrative.lower()
        assert 'related entities' in narrative.lower()
        assert 'signal distortion' in narrative.lower()
        assert 'algorithmic systems' in narrative.lower()
        assert 'price impact' in narrative.lower()
        
    def test_stor_export_format(self):
        """Test STOR export format"""
        
        # Create test rationale
        risk_result = {
            'overall_score': 0.8,
            'risk_level': 'high'
        }
        
        evidence_factors = {
            'WashTradeLikelihood': 2,
            'SignalDistortionIndex': 1
        }
        
        rationale = self.reg_explainability.generate_regulatory_rationale(
            alert_id='WASH_TRADE_STOR_001',
            risk_result=risk_result,
            evidence_factors=evidence_factors,
            model_type='wash_trade_detection'
        )
        
        stor_record = self.reg_explainability.export_stor_format(rationale)
        
        assert stor_record.record_id == 'WASH_TRADE_STOR_001'
        assert stor_record.risk_score == 0.8
        assert stor_record.risk_level == 'high'
        assert stor_record.transaction_type == 'SUSPICIOUS_ACTIVITY'
        assert stor_record.regulatory_basis == 'MiFID II Article 48 - Wash trades and matched orders'
        
    def test_full_pipeline_integration(self):
        """Test full pipeline integration from prediction to regulatory output"""
        
        # High risk wash trade scenario
        market_data = {
            'entity_a_lei': 'LEI123456789',
            'entity_b_lei': 'LEI123456789',
            'entity_relationship': 'same_entity',
            'algo_framework_match': True,
            'timing_correlation': 0.95,
            'volume_imbalance': 0.8,
            'quote_flicker_frequency': 50,
            'order_book_depth_distortion': 0.7,
            'algo_reaction_time': 0.05,
            'post_trade_reaction_count': 15,
            'commodity_venue_overlap': 0.9,
            'strategy_leg_correlation': 0.85,
            'price_impact_magnitude': 0.6,
            'mean_reversion_speed': 0.8,
            'venue_liquidity_conflict': 0.7,
            'implied_matching_rate': 0.75
        }
        
        # Step 1: Model prediction
        prediction_result = self.model.predict(market_data)
        assert prediction_result['risk_level'] == 'high'
        
        # Step 2: Evidence mapping
        evidence_factors = {}
        for node_name, state in prediction_result['node_states'].items():
            if node_name in ['WashTradeLikelihood', 'SignalDistortionIndex', 
                           'AlgoReactionSensitivity', 'StrategyLegOverlap',
                           'PriceImpactAnomaly', 'ImpliedLiquidityConflict']:
                evidence_factors[node_name] = state
        
        # Step 3: Regulatory explainability
        rationale = self.reg_explainability.generate_regulatory_rationale(
            alert_id='WASH_TRADE_FULL_001',
            risk_result=prediction_result,
            evidence_factors=evidence_factors,
            model_type='wash_trade_detection'
        )
        
        # Step 4: STOR export
        stor_record = self.reg_explainability.export_stor_format(rationale)
        
        # Verify full pipeline
        assert stor_record.risk_level == 'high'
        assert 'wash trade' in stor_record.narrative.lower()
        assert stor_record.regulatory_basis == 'MiFID II Article 48 - Wash trades and matched orders'
        assert len(rationale.inference_paths) > 0
        assert len(rationale.audit_trail) > 0
        
    def test_node_state_transitions(self):
        """Test node state transitions for wash trade detection"""
        
        # Test WashTradeLikelihood node
        wash_node = WashTradeLikelihood()
        
        # High risk scenario
        high_risk_evidence = {
            'entity_a_lei': 'LEI123456789',
            'entity_b_lei': 'LEI123456789',
            'entity_relationship': 'same_entity',
            'algo_framework_match': True,
            'timing_correlation': 0.95
        }
        
        high_risk_state = wash_node.calculate_state(high_risk_evidence)
        assert high_risk_state == 2  # High state
        
        # Low risk scenario
        low_risk_evidence = {
            'entity_a_lei': 'LEI123456789',
            'entity_b_lei': 'LEI987654321',
            'entity_relationship': 'unrelated',
            'algo_framework_match': False,
            'timing_correlation': 0.2
        }
        
        low_risk_state = wash_node.calculate_state(low_risk_evidence)
        assert low_risk_state == 0  # Low state
        
    def test_error_handling(self):
        """Test error handling in wash trade detection"""
        
        # Test with missing data
        incomplete_data = {
            'entity_a_lei': 'LEI123456789'
            # Missing most required fields
        }
        
        result = self.model.predict(incomplete_data)
        assert result is not None
        assert 'overall_score' in result
        assert result['overall_score'] >= 0.0
        
        # Test regulatory explainability error handling
        invalid_evidence = {'invalid_node': 'invalid_value'}
        
        rationale = self.reg_explainability.generate_regulatory_rationale(
            alert_id='ERROR_TEST',
            risk_result={'overall_score': 0.5, 'risk_level': 'medium'},
            evidence_factors=invalid_evidence,
            model_type='wash_trade_detection'
        )
        
        assert rationale is not None
        assert rationale.alert_id == 'ERROR_TEST'
        
    def test_performance_benchmarks(self):
        """Test performance benchmarks for wash trade detection"""
        
        import time
        
        # Create large dataset
        test_data = []
        for i in range(100):
            test_data.append({
                'entity_a_lei': f'LEI{i:09d}',
                'entity_b_lei': f'LEI{(i+1):09d}',
                'entity_relationship': 'unrelated',
                'algo_framework_match': i % 2 == 0,
                'timing_correlation': np.random.uniform(0.1, 0.9),
                'volume_imbalance': np.random.uniform(0.1, 0.8),
                'quote_flicker_frequency': np.random.randint(1, 100),
                'order_book_depth_distortion': np.random.uniform(0.1, 0.8),
                'algo_reaction_time': np.random.uniform(0.05, 0.5),
                'post_trade_reaction_count': np.random.randint(1, 20),
                'commodity_venue_overlap': np.random.uniform(0.1, 0.9),
                'strategy_leg_correlation': np.random.uniform(0.1, 0.9),
                'price_impact_magnitude': np.random.uniform(0.1, 0.8),
                'mean_reversion_speed': np.random.uniform(0.1, 0.9),
                'venue_liquidity_conflict': np.random.uniform(0.1, 0.8),
                'implied_matching_rate': np.random.uniform(0.1, 0.8)
            })
        
        # Time the predictions
        start_time = time.time()
        results = []
        
        for data in test_data:
            result = self.model.predict(data)
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert len(results) == 100
        assert total_time < 10.0  # Should complete in under 10 seconds
        assert all('overall_score' in result for result in results)
        
        # Check distribution of results
        high_risk_count = sum(1 for r in results if r['risk_level'] == 'high')
        medium_risk_count = sum(1 for r in results if r['risk_level'] == 'medium')
        low_risk_count = sum(1 for r in results if r['risk_level'] == 'low')
        
        assert high_risk_count + medium_risk_count + low_risk_count == 100
        
        print(f"Performance test completed in {total_time:.2f} seconds")
        print(f"Risk distribution: High={high_risk_count}, Medium={medium_risk_count}, Low={low_risk_count}")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])