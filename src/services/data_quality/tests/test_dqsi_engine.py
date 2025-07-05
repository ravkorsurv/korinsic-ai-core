"""
Tests for DQSI Engine - Strategy Mode Selection and Output Schema
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from ..dq_sufficiency_index import DataQualitySufficiencyIndex
from ..dq_strategy_base import DQConfig, DQSIOutput, KDEResult
from ..fallback_dq_strategy import FallbackDQScoringStrategy
from ..role_aware_dq_strategy import RoleAwareDQScoringStrategy


class TestDQSIEngine(unittest.TestCase):
    """Test suite for DQSI Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_data = {
            'trader_id': 'TRD001',
            'trade_time': '2024-01-15T10:30:00Z',
            'notional': 1000000.0,
            'quantity': 1000,
            'price': 100.50,
            'desk_id': 'DESK001',
            'instrument': 'AAPL',
            'client_id': 'CLT001'
        }
        
        self.sample_metadata = {
            'role': 'producer',
            'reference_data': {
                'trader_id': 'TRD001',
                'notional': 1000000.0
            },
            'reconciliation_data': {
                'trade_time': '2024-01-15T10:30:00Z',
                'price': 100.50
            }
        }
    
    def test_fallback_strategy_selection(self):
        """Test fallback strategy is selected correctly"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        self.assertIsInstance(dqsi.strategy, FallbackDQScoringStrategy)
        self.assertEqual(dqsi.strategy.get_strategy_name(), 'fallback')
    
    def test_role_aware_strategy_selection(self):
        """Test role-aware strategy is selected correctly"""
        config = DQConfig(dq_strategy='role_aware')
        dqsi = DataQualitySufficiencyIndex(config)
        
        self.assertIsInstance(dqsi.strategy, RoleAwareDQScoringStrategy)
        self.assertEqual(dqsi.strategy.get_strategy_name(), 'role_aware')
    
    def test_unknown_strategy_fallback(self):
        """Test unknown strategy falls back to fallback"""
        config = DQConfig(dq_strategy='unknown_strategy')
        dqsi = DataQualitySufficiencyIndex(config)
        
        self.assertIsInstance(dqsi.strategy, FallbackDQScoringStrategy)
        self.assertEqual(dqsi.strategy.get_strategy_name(), 'fallback')
    
    def test_dqsi_output_schema(self):
        """Test DQSI output contains all required fields"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        output = dqsi.calculate_dqsi(self.sample_data)
        
        # Check all required fields are present
        self.assertIsInstance(output, DQSIOutput)
        self.assertIn('dqsi_score', output.__dict__)
        self.assertIn('dqsi_confidence_index', output.__dict__)
        self.assertIn('dqsi_mode', output.__dict__)
        self.assertIn('dqsi_critical_kdes_missing', output.__dict__)
        self.assertIn('dqsi_sub_scores', output.__dict__)
        self.assertIn('dqsi_kde_weights', output.__dict__)
        self.assertIn('dqsi_confidence_note', output.__dict__)
        self.assertIn('kde_results', output.__dict__)
        self.assertIn('timestamp', output.__dict__)
    
    def test_dqsi_score_range(self):
        """Test DQSI score is in valid range [0.0, 1.0]"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        output = dqsi.calculate_dqsi(self.sample_data)
        
        self.assertGreaterEqual(output.dqsi_score, 0.0)
        self.assertLessEqual(output.dqsi_score, 1.0)
    
    def test_confidence_index_range(self):
        """Test confidence index is in valid range [0.0, 1.0]"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        output = dqsi.calculate_dqsi(self.sample_data)
        
        self.assertGreaterEqual(output.dqsi_confidence_index, 0.0)
        self.assertLessEqual(output.dqsi_confidence_index, 1.0)
    
    def test_critical_kde_cap_enforcement(self):
        """Test critical KDE cap is enforced"""
        config = DQConfig(
            dq_strategy='fallback',
            critical_kdes=['trader_id'],
            dqsi_critical_cap=0.75
        )
        dqsi = DataQualitySufficiencyIndex(config)
        
        # Missing critical KDE
        data_missing_critical = self.sample_data.copy()
        del data_missing_critical['trader_id']
        
        output = dqsi.calculate_dqsi(data_missing_critical)
        
        self.assertLessEqual(output.dqsi_score, 0.75)
        self.assertIn('trader_id', output.dqsi_critical_kdes_missing)
    
    def test_synthetic_kde_injection(self):
        """Test synthetic KDEs are injected into results"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        output = dqsi.calculate_dqsi(self.sample_data)
        
        # Check for synthetic KDEs
        synthetic_kdes = [kde for kde in output.kde_results if kde.is_synthetic]
        self.assertGreater(len(synthetic_kdes), 0)
        
        # Check synthetic KDE names
        synthetic_names = [kde.kde_name for kde in synthetic_kdes]
        self.assertIn('synthetic_timeliness', synthetic_names)
        self.assertIn('synthetic_coverage', synthetic_names)
    
    def test_dimension_sub_scores(self):
        """Test dimension sub-scores are calculated"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        output = dqsi.calculate_dqsi(self.sample_data)
        
        # Check sub-scores exist
        self.assertIsInstance(output.dqsi_sub_scores, dict)
        self.assertGreater(len(output.dqsi_sub_scores), 0)
        
        # Check all scores are in valid range
        for dimension, score in output.dqsi_sub_scores.items():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_kde_weights_mapping(self):
        """Test KDE weights are correctly mapped"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        output = dqsi.calculate_dqsi(self.sample_data)
        
        # Check kde_weights dictionary
        self.assertIsInstance(output.dqsi_kde_weights, dict)
        
        # Check weights are valid
        for kde_name, weight in output.dqsi_kde_weights.items():
            self.assertIn(weight, [1, 2, 3])  # Valid risk weights
    
    def test_role_aware_vs_fallback_differences(self):
        """Test role-aware and fallback strategies produce different results"""
        fallback_config = DQConfig(dq_strategy='fallback')
        role_aware_config = DQConfig(dq_strategy='role_aware')
        
        fallback_dqsi = DataQualitySufficiencyIndex(fallback_config)
        role_aware_dqsi = DataQualitySufficiencyIndex(role_aware_config)
        
        fallback_output = fallback_dqsi.calculate_dqsi(self.sample_data, self.sample_metadata)
        role_aware_output = role_aware_dqsi.calculate_dqsi(self.sample_data, self.sample_metadata)
        
        # Should have different modes
        self.assertEqual(fallback_output.dqsi_mode, 'fallback')
        self.assertEqual(role_aware_output.dqsi_mode, 'role_aware')
        
        # Should have different confidence indices (fallback has modifier)
        self.assertNotEqual(fallback_output.dqsi_confidence_index, role_aware_output.dqsi_confidence_index)
    
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        output = dqsi.calculate_dqsi({})
        
        self.assertEqual(output.dqsi_score, 0.0)
        self.assertEqual(output.dqsi_confidence_index, 0.0)
        self.assertIsInstance(output.dqsi_sub_scores, dict)
    
    def test_alert_injection_format(self):
        """Test alert injection format"""
        config = DQConfig(dq_strategy='role_aware')
        dqsi = DataQualitySufficiencyIndex(config)
        
        alert_data = {
            'producer_role': 'producer',
            'typology': 'market_manipulation',
            **self.sample_data
        }
        
        alert_output = dqsi.calculate_dqsi_for_alert(alert_data)
        
        # Check required fields for alert injection
        required_fields = [
            'dqsi_score', 'dqsi_confidence_index', 'dqsi_mode',
            'dqsi_critical_kdes_missing', 'dqsi_sub_scores',
            'dqsi_kde_weights', 'dqsi_confidence_note'
        ]
        
        for field in required_fields:
            self.assertIn(field, alert_output)
    
    def test_case_aggregation(self):
        """Test case-level aggregation across multiple alerts"""
        config = DQConfig(dq_strategy='role_aware')
        dqsi = DataQualitySufficiencyIndex(config)
        
        case_data = {
            'alerts': [
                {'producer_role': 'producer', **self.sample_data},
                {'producer_role': 'producer', 'trader_id': 'TRD002', **self.sample_data}
            ]
        }
        
        case_output = dqsi.calculate_dqsi_for_case(case_data)
        
        # Check case-specific fields
        self.assertIn('case_alert_count', case_output)
        self.assertEqual(case_output['case_alert_count'], 2)
        
        # Check aggregated scores
        self.assertGreaterEqual(case_output['dqsi_score'], 0.0)
        self.assertLessEqual(case_output['dqsi_score'], 1.0)
    
    def test_strategy_info(self):
        """Test strategy info retrieval"""
        config = DQConfig(dq_strategy='role_aware')
        dqsi = DataQualitySufficiencyIndex(config)
        
        info = dqsi.get_strategy_info()
        
        expected_fields = [
            'strategy_name', 'strategy_mode', 'dimensions',
            'kde_risk_tiers', 'critical_kdes', 'critical_cap',
            'synthetic_kdes'
        ]
        
        for field in expected_fields:
            self.assertIn(field, info)
    
    def test_kde_coverage_validation(self):
        """Test KDE coverage validation"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        coverage = dqsi.validate_kde_coverage(self.sample_data)
        
        expected_fields = [
            'coverage_ratio', 'expected_kdes', 'present_kdes',
            'missing_kdes', 'missing_by_tier', 'unexpected_kdes',
            'critical_missing'
        ]
        
        for field in expected_fields:
            self.assertIn(field, coverage)
        
        self.assertGreaterEqual(coverage['coverage_ratio'], 0.0)
        self.assertLessEqual(coverage['coverage_ratio'], 1.0)
    
    def test_dqsi_impact_simulation(self):
        """Test DQSI impact simulation"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        modifications = {'trader_id': 'TRD002'}
        
        impact = dqsi.simulate_dqsi_impact(self.sample_data, modifications)
        
        expected_fields = [
            'original_score', 'modified_score', 'score_delta',
            'original_confidence', 'modified_confidence', 'confidence_delta',
            'modifications_applied', 'impact_analysis'
        ]
        
        for field in expected_fields:
            self.assertIn(field, impact)
    
    def test_improvement_recommendations(self):
        """Test improvement recommendations generation"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        # Create data with poor quality
        poor_data = {
            'trader_id': None,  # Missing critical KDE
            'notional': 'invalid',  # Invalid format
            'price': -100  # Invalid value
        }
        
        output = dqsi.calculate_dqsi(poor_data)
        recommendations = dqsi.get_improvement_recommendations(output)
        
        self.assertIsInstance(recommendations, list)
        
        if recommendations:
            # Check recommendation structure
            rec = recommendations[0]
            expected_fields = [
                'kde_name', 'current_score', 'risk_tier', 'dimension',
                'priority', 'suggestions', 'expected_impact'
            ]
            
            for field in expected_fields:
                self.assertIn(field, rec)
    
    def test_error_handling(self):
        """Test error handling in DQSI calculation"""
        config = DQConfig(dq_strategy='fallback')
        dqsi = DataQualitySufficiencyIndex(config)
        
        # Mock strategy to raise exception
        with patch.object(dqsi.strategy, 'score_kdes', side_effect=Exception("Test error")):
            output = dqsi.calculate_dqsi(self.sample_data)
            
            self.assertEqual(output.dqsi_score, 0.0)
            self.assertEqual(output.dqsi_confidence_index, 0.0)
            self.assertIn("Error calculating DQSI", output.dqsi_confidence_note)
    
    def test_7_dimensions_coverage(self):
        """Test that all 7 dimensions are covered"""
        config = DQConfig()
        
        # Check we have exactly 7 dimensions
        all_dimensions = []
        for tier_dimensions in config.dimensions.values():
            all_dimensions.extend(tier_dimensions)
        
        self.assertEqual(len(all_dimensions), 7)
        
        # Check specific dimensions
        expected_foundational = {'completeness', 'conformity', 'timeliness', 'coverage'}
        expected_enhanced = {'accuracy', 'uniqueness', 'consistency'}
        
        actual_foundational = set(config.dimensions['foundational'])
        actual_enhanced = set(config.dimensions['enhanced'])
        
        self.assertEqual(actual_foundational, expected_foundational)
        self.assertEqual(actual_enhanced, expected_enhanced)


if __name__ == '__main__':
    unittest.main()