"""
Integration Tests for Alert Scoring with DQSI Trust Bucket

Tests that dqsi_trust_bucket appears in alert scoring output and
integrates properly with the existing scoring pipeline.
"""

import unittest
import sys
import os
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.dq_sufficiency_index import DQSufficiencyIndex
from core.role_aware_dq_strategy import RoleAwareDQStrategy
from core.fallback_dq_strategy import FallbackDQStrategy

class TestAlertScoringDQSI(unittest.TestCase):
    """Integration tests for DQSI trust bucket in alert scoring."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dqsi = DQSufficiencyIndex()
        self.role_strategy = RoleAwareDQStrategy()
        self.fallback_strategy = FallbackDQStrategy()
    
    def test_alert_scoring_output_includes_trust_bucket(self):
        """Test that alert scoring output includes dqsi_trust_bucket field."""
        print("\n🧪 Testing Alert Scoring Output Includes Trust Bucket")
        
        # Mock alert data with various data quality scenarios
        alert_scenarios = [
            {
                'alert_id': 'ALERT_001',
                'type': 'insider_dealing',
                'evidence': {
                    'trade_volume': 1000000,
                    'price_impact': 0.05,
                    'material_info_timing': 'before_announcement',
                    'employee_access': 'high_level'
                },
                'data_quality_metrics': {
                    'trade_source': 0.95,
                    'timing_source': 0.90,
                    'access_source': 0.85
                },
                'kde_presence': {
                    'material_info': True,
                    'timing_data': True,
                    'trade_data': True,
                    'access_data': True
                },
                'expected_trust_bucket': 'High'
            },
            {
                'alert_id': 'ALERT_002',
                'type': 'market_manipulation',
                'evidence': {
                    'trade_volume': 50000,
                    'price_pattern': 'suspicious'
                },
                'data_quality_metrics': {
                    'trade_source': 0.70,
                    'pattern_source': 0.65
                },
                'kde_presence': {
                    'trade_data': True,
                    'pattern_data': True,
                    'timing_data': False
                },
                'imputation_usage': {
                    'missing_timing': True
                },
                'expected_trust_bucket': 'Moderate'
            },
            {
                'alert_id': 'ALERT_003',
                'type': 'spoofing',
                'evidence': {
                    'order_pattern': 'layering'
                },
                'data_quality_metrics': {
                    'order_source': 0.40
                },
                'kde_presence': {
                    'order_data': True,
                    'execution_data': False,
                    'cancellation_data': False
                },
                'imputation_usage': {
                    'missing_execution': True,
                    'missing_cancellation': True
                },
                'expected_trust_bucket': 'Low'
            }
        ]
        
        for scenario in alert_scenarios:
            alert_id = scenario['alert_id']
            evidence = scenario['evidence']
            data_quality_metrics = scenario.get('data_quality_metrics', {})
            kde_presence = scenario.get('kde_presence', {})
            imputation_usage = scenario.get('imputation_usage', {})
            
            # Calculate DQSI for this alert
            dqsi_result = self.dqsi.calculate_dqsi(
                evidence, data_quality_metrics, imputation_usage, kde_presence
            )
            
            # Verify required fields are present
            self.assertIn('dqsi_confidence_index', dqsi_result)
            self.assertIn('dqsi_trust_bucket', dqsi_result)
            
            trust_bucket = dqsi_result['dqsi_trust_bucket']
            confidence_index = dqsi_result['dqsi_confidence_index']
            
            # Verify trust bucket is valid
            self.assertTrue(self.dqsi.validate_trust_bucket(trust_bucket))
            
            print(f"   ✅ {alert_id}: confidence={confidence_index:.3f}, "
                  f"trust_bucket={trust_bucket}")
            
            # Create full alert scoring output
            alert_output = self._create_alert_output(scenario, dqsi_result)
            
            # Verify the full alert output includes DQSI fields
            self.assertIn('dqsi_trust_bucket', alert_output)
            self.assertEqual(alert_output['dqsi_trust_bucket'], trust_bucket)
            
            print(f"      📊 Full alert output includes trust bucket: {trust_bucket}")
    
    def test_role_aware_alert_scoring(self):
        """Test role-aware alert scoring includes trust bucket."""
        print("\n🧪 Testing Role-Aware Alert Scoring")
        
        alert_evidence = {
            'trade_volume': 500000,
            'suspicious_pattern': 'detected',
            'timing_correlation': 0.7
        }
        
        roles_to_test = ['analyst', 'compliance', 'auditor', 'trader']
        
        for role in roles_to_test:
            # Calculate role-aware DQ score
            role_result = self.role_strategy.calculate_dq_score(alert_evidence, user_role=role)
            
            # Verify role-specific fields
            self.assertIn('dqsi_trust_bucket', role_result)
            self.assertIn('user_role', role_result)
            self.assertIn('dq_strategy', role_result)
            self.assertEqual(role_result['user_role'], role)
            self.assertEqual(role_result['dq_strategy'], 'role_aware')
            
            trust_bucket = role_result['dqsi_trust_bucket']
            confidence = role_result['dqsi_confidence_index']
            
            print(f"   ✅ {role}: confidence={confidence:.3f}, bucket={trust_bucket}")
            
            # Create alert output with role-aware scoring
            alert_output = {
                'alert_id': f'ROLE_ALERT_{role.upper()}',
                'type': 'insider_dealing',
                'risk_score': 0.75,
                'dqsi_confidence_index': confidence,
                'dqsi_trust_bucket': trust_bucket,
                'user_role': role,
                'scoring_strategy': 'role_aware',
                'evidence': alert_evidence
            }
            
            # Verify alert output schema
            self._validate_alert_output_schema(alert_output)
            print(f"      📋 Alert output schema valid for {role}")
    
    def test_fallback_alert_scoring(self):
        """Test fallback alert scoring includes trust bucket."""
        print("\n🧪 Testing Fallback Alert Scoring")
        
        fallback_scenarios = [
            {
                'reason': 'insufficient_data',
                'evidence': {},
                'description': 'No evidence available'
            },
            {
                'reason': 'data_corruption',
                'evidence': {'corrupted_field': None},
                'description': 'Corrupted data detected'
            },
            {
                'reason': 'system_degraded',
                'evidence': {'minimal_data': 'partial'},
                'description': 'System running in degraded mode'
            }
        ]
        
        for scenario in fallback_scenarios:
            reason = scenario['reason']
            evidence = scenario['evidence']
            description = scenario['description']
            
            # Calculate fallback DQ score
            fallback_result = self.fallback_strategy.calculate_dq_score(
                evidence, fallback_reason=reason
            )
            
            # Verify fallback fields
            self.assertIn('dqsi_trust_bucket', fallback_result)
            self.assertIn('fallback_reason', fallback_result)
            self.assertIn('is_degraded_mode', fallback_result)
            self.assertEqual(fallback_result['dq_strategy'], 'fallback')
            self.assertEqual(fallback_result['fallback_reason'], reason)
            self.assertTrue(fallback_result['is_degraded_mode'])
            
            trust_bucket = fallback_result['dqsi_trust_bucket']
            confidence = fallback_result['dqsi_confidence_index']
            
            # Fallback should result in Low trust bucket
            self.assertEqual(trust_bucket, 'Low', f"Fallback should result in Low trust bucket for {reason}")
            
            print(f"   ✅ {reason}: confidence={confidence:.3f}, bucket={trust_bucket}")
            print(f"      📝 {description}")
    
    def test_kafka_output_format(self):
        """Test that DQSI fields are properly formatted for Kafka output."""
        print("\n🧪 Testing Kafka Output Format")
        
        # Mock alert for Kafka output
        alert_data = {
            'trade_volume': 750000,
            'price_movement': 0.03,
            'communication_flag': True
        }
        
        dqsi_result = self.dqsi.calculate_dqsi(alert_data)
        
        # Create Kafka message format
        kafka_message = {
            'timestamp': '2024-01-15T10:30:00Z',
            'alert_id': 'KAFKA_ALERT_001',
            'alert_type': 'insider_dealing',
            'risk_score': 0.82,
            'dqsi_confidence_index': dqsi_result['dqsi_confidence_index'],
            'dqsi_trust_bucket': dqsi_result['dqsi_trust_bucket'],
            'data_quality_summary': dqsi_result['quality_summary'],
            'evidence': alert_data
        }
        
        # Verify Kafka message can be serialized to JSON
        try:
            kafka_json = json.dumps(kafka_message)
            self.assertIsInstance(kafka_json, str)
            print(f"   ✅ Kafka message serializable to JSON")
        except Exception as e:
            self.fail(f"Kafka message not serializable: {e}")
        
        # Verify required fields are present
        self.assertIn('dqsi_trust_bucket', kafka_message)
        self.assertIn('dqsi_confidence_index', kafka_message)
        
        print(f"   📨 Kafka message includes: trust_bucket={kafka_message['dqsi_trust_bucket']}")
        print(f"   📊 Confidence index: {kafka_message['dqsi_confidence_index']}")
    
    def test_rest_api_output_format(self):
        """Test that DQSI fields are properly formatted for REST API output."""
        print("\n🧪 Testing REST API Output Format")
        
        alert_evidence = {
            'transaction_amount': 2000000,
            'unusual_timing': True,
            'insider_connection': 'confirmed'
        }
        
        dqsi_result = self.dqsi.calculate_dqsi(alert_evidence)
        
        # Create REST API response format
        api_response = {
            'status': 'success',
            'data': {
                'alert': {
                    'id': 'API_ALERT_001',
                    'type': 'insider_dealing',
                    'created_at': '2024-01-15T10:30:00Z',
                    'risk_assessment': {
                        'risk_score': 0.88,
                        'confidence_level': 'high'
                    },
                    'data_quality': {
                        'dqsi_confidence_index': dqsi_result['dqsi_confidence_index'],
                        'dqsi_trust_bucket': dqsi_result['dqsi_trust_bucket'],
                        'components': dqsi_result['data_quality_components']
                    },
                    'evidence': alert_evidence
                }
            }
        }
        
        # Verify API response structure
        self.assertIn('data', api_response)
        self.assertIn('alert', api_response['data'])
        self.assertIn('data_quality', api_response['data']['alert'])
        
        data_quality = api_response['data']['alert']['data_quality']
        self.assertIn('dqsi_trust_bucket', data_quality)
        self.assertIn('dqsi_confidence_index', data_quality)
        
        print(f"   ✅ REST API response includes DQSI fields")
        print(f"   🏷️  Trust bucket: {data_quality['dqsi_trust_bucket']}")
        print(f"   📊 Confidence: {data_quality['dqsi_confidence_index']}")
    
    def test_elasticsearch_output_format(self):
        """Test that DQSI fields are properly formatted for Elasticsearch indexing."""
        print("\n🧪 Testing Elasticsearch Output Format")
        
        alert_evidence = {
            'order_size': 1500000,
            'market_impact': 0.04,
            'execution_timing': 'pre_announcement'
        }
        
        dqsi_result = self.dqsi.calculate_dqsi(alert_evidence)
        
        # Create Elasticsearch document format
        es_document = {
            '_index': 'surveillance-alerts',
            '_type': '_doc',
            '_id': 'ES_ALERT_001',
            '_source': {
                '@timestamp': '2024-01-15T10:30:00Z',
                'alert_id': 'ES_ALERT_001',
                'alert_type': 'insider_dealing',
                'risk_score': 0.79,
                'dqsi_confidence_index': dqsi_result['dqsi_confidence_index'],
                'dqsi_trust_bucket': dqsi_result['dqsi_trust_bucket'],
                'data_quality_breakdown': dqsi_result['data_quality_components'],
                'evidence': alert_evidence,
                'tags': ['surveillance', 'high_risk', dqsi_result['dqsi_trust_bucket'].lower() + '_trust']
            }
        }
        
        # Verify Elasticsearch document structure
        self.assertIn('_source', es_document)
        source = es_document['_source']
        
        self.assertIn('dqsi_trust_bucket', source)
        self.assertIn('dqsi_confidence_index', source)
        
        # Verify trust bucket is included in tags
        trust_tag = dqsi_result['dqsi_trust_bucket'].lower() + '_trust'
        self.assertIn(trust_tag, source['tags'])
        
        print(f"   ✅ Elasticsearch document includes DQSI fields")
        print(f"   🏷️  Trust bucket: {source['dqsi_trust_bucket']}")
        print(f"   🏷️  Trust tag: {trust_tag}")
        print(f"   📊 Confidence: {source['dqsi_confidence_index']}")
    
    def _create_alert_output(self, scenario: dict, dqsi_result: dict) -> dict:
        """Create full alert output including DQSI results."""
        return {
            'alert_id': scenario['alert_id'],
            'alert_type': scenario['type'],
            'timestamp': '2024-01-15T10:30:00Z',
            'risk_score': 0.75,  # Mock risk score
            'dqsi_confidence_index': dqsi_result['dqsi_confidence_index'],
            'dqsi_trust_bucket': dqsi_result['dqsi_trust_bucket'],
            'data_quality_components': dqsi_result['data_quality_components'],
            'quality_summary': dqsi_result['quality_summary'],
            'evidence': scenario['evidence']
        }
    
    def _validate_alert_output_schema(self, alert_output: dict):
        """Validate that alert output contains required DQSI fields."""
        required_fields = [
            'alert_id',
            'dqsi_confidence_index',
            'dqsi_trust_bucket'
        ]
        
        for field in required_fields:
            self.assertIn(field, alert_output, f"Alert output missing required field: {field}")
        
        # Validate data types
        self.assertIsInstance(alert_output['dqsi_confidence_index'], float)
        self.assertIsInstance(alert_output['dqsi_trust_bucket'], str)
        
        # Validate trust bucket value
        self.assertTrue(self.dqsi.validate_trust_bucket(alert_output['dqsi_trust_bucket']))

def run_alert_scoring_integration_tests():
    """Run all alert scoring integration tests."""
    print("🚨 STARTING ALERT SCORING INTEGRATION TESTS")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAlertScoringDQSI)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("🏁 ALERT SCORING INTEGRATION TESTS COMPLETED")
    
    if result.wasSuccessful():
        print("✅ ALL INTEGRATION TESTS PASSED!")
    else:
        print(f"❌ {len(result.failures)} FAILURES, {len(result.errors)} ERRORS")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_alert_scoring_integration_tests()