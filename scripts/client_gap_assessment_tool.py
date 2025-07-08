#!/usr/bin/env python3
"""
Client Data Quality Gap Assessment Tool

This tool conducts a structured gap assessment for implementing DQSI 
at client sites and generates customized configurations with mixed-role support.
"""

import json
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional


class ClientGapAssessmentTool:
    """Tool for conducting DQ gap assessments and generating client configurations"""
    
    def __init__(self):
        self.assessment_results = {}
        self.client_profile = {}
        self.data_flows = {}
        self.dqsi_config = {}
        
    def conduct_discovery_interview(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process discovery interview responses
        
        Args:
            responses: Client responses to discovery questions
            
        Returns:
            Structured client profile
        """
        self.client_profile = {
            'basic_info': {
                'name': responses.get('company_name', 'Unknown'),
                'industry': responses.get('industry', 'financial_services'),
                'employee_count': responses.get('employee_count', 0),
                'daily_volume': responses.get('daily_trading_volume', 0),
                'regulatory_tier': responses.get('regulatory_level', 'basic')
            },
            'technical_maturity': {
                'it_sophistication': responses.get('it_maturity', 'basic'),
                'current_dq_tools': responses.get('dq_tools', []),
                'automation_level': responses.get('automation_level', 'manual'),
                'integration_capabilities': responses.get('integration_apis', False)
            },
            'business_priorities': {
                'primary_focus': responses.get('primary_business_focus', 'trading'),
                'regulatory_pressure': responses.get('regulatory_pressure', 'medium'),
                'risk_tolerance': responses.get('risk_tolerance', 'medium'),
                'budget_range': responses.get('dq_budget', 'medium')
            }
        }
        
        return self.client_profile
    
    def map_data_flows(self, data_flow_config: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Map client data flows with role assignments
        
        Args:
            data_flow_config: Configuration of data flows with roles
            
        Returns:
            Structured data flow mapping
        """
        self.data_flows = {}
        
        for flow_name, flow_config in data_flow_config.items():
            self.data_flows[flow_name] = {
                'role': flow_config.get('role', 'consumer'),
                'type': flow_config.get('type', 'trading_data'),
                'source_destination': flow_config.get('source_destination', 'unknown'),
                'criticality': flow_config.get('criticality', 'medium'),
                'current_capability': flow_config.get('current_capability', 'basic'),
                'volume': flow_config.get('volume', 'medium'),
                'frequency': flow_config.get('frequency', 'daily')
            }
        
        return self.data_flows
    
    def assess_current_state_by_flow(self, current_capabilities: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """
        Assess current data quality capabilities by data flow
        
        Args:
            current_capabilities: Current DQ capabilities by data flow and dimension
            
        Returns:
            Flow-specific dimension scores and maturity levels
        """
        flow_scores = {}
        
        # Scoring criteria for each dimension
        scoring_criteria = {
            'completeness': {
                'none': 0.0,
                'basic_null_check': 0.3,
                'etl_validation': 0.6,
                'business_rules': 0.8,
                'automated_monitoring': 1.0
            },
            'conformity': {
                'none': 0.0,
                'basic_format': 0.2,
                'type_validation': 0.4,
                'reference_tables': 0.7,
                'comprehensive_rules': 1.0
            },
            'timeliness': {
                'none': 0.0,
                'manual_monitoring': 0.2,
                'batch_reporting': 0.4,
                'near_realtime': 0.7,
                'realtime_sla': 1.0
            },
            'coverage': {
                'none': 0.0,
                'manual_tracking': 0.1,
                'spreadsheet_monitoring': 0.3,
                'automated_profiling': 0.6,
                'baseline_comparison': 1.0
            },
            'accuracy': {
                'none': 0.0,
                'manual_reconciliation': 0.2,
                'periodic_validation': 0.4,
                'reference_checking': 0.7,
                'golden_source_validation': 1.0
            },
            'uniqueness': {
                'none': 0.0,
                'basic_duplicate_check': 0.3,
                'system_level_dedup': 0.6,
                'cross_system_checking': 1.0
            },
            'consistency': {
                'none': 0.0,
                'manual_reconciliation': 0.3,
                'automated_reconciliation': 0.6,
                'cross_system_validation': 1.0
            }
        }
        
        for flow_name, flow_capabilities in current_capabilities.items():
            flow_scores[flow_name] = {'dimension_scores': {}}
            
            for dimension, capability_level in flow_capabilities.items():
                if dimension == 'role':
                    continue
                    
                level = capability_level.get('level', 'none')
                if dimension in scoring_criteria and level in scoring_criteria[dimension]:
                    flow_scores[flow_name]['dimension_scores'][dimension] = scoring_criteria[dimension][level]
                else:
                    flow_scores[flow_name]['dimension_scores'][dimension] = 0.0
            
            # Calculate flow-specific maturity
            dimension_scores = flow_scores[flow_name]['dimension_scores']
            if dimension_scores:
                flow_maturity = sum(dimension_scores.values()) / len(dimension_scores)
                flow_scores[flow_name]['flow_maturity'] = flow_maturity
                flow_scores[flow_name]['maturity_level'] = self._determine_maturity_level(flow_maturity)
        
        self.assessment_results = {
            'flow_scores': flow_scores,
            'assessment_date': datetime.now().isoformat()
        }
        
        return flow_scores
    
    def determine_mixed_role_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Determine appropriate DQSI strategies for each data flow"""
        
        if not self.data_flows:
            raise ValueError("Data flows not mapped. Call map_data_flows() first.")
        
        strategies = {}
        
        for flow_name, flow_config in self.data_flows.items():
            role = flow_config['role']
            criticality = flow_config['criticality']
            
            if role == 'consumer':
                # Consumer strategy - foundational dimensions focus
                strategies[flow_name] = {
                    'strategy': 'role_aware_consumer',
                    'dimensions': ['completeness', 'conformity', 'timeliness', 'coverage'],
                    'subdimensions': self._get_consumer_subdimensions(),
                    'validation_depth': 'input_validation',
                    'kde_count': 6,
                    'comparison_types': ['None', 'Reference Table']
                }
            elif role == 'producer':
                # Producer strategy - full validation
                strategies[flow_name] = {
                    'strategy': 'role_aware_producer',
                    'dimensions': ['completeness', 'conformity', 'timeliness', 'coverage', 
                                  'accuracy', 'uniqueness', 'consistency'],
                    'subdimensions': self._get_producer_subdimensions(),
                    'validation_depth': 'full_validation',
                    'kde_count': 12,
                    'comparison_types': ['None', 'Reference Table', 'Golden Source', 'Cross-System', 'Trend']
                }
            
            # Adjust based on criticality
            if criticality == 'high':
                strategies[flow_name]['kde_count'] += 3
                strategies[flow_name]['enhanced_validation'] = True
            elif criticality == 'low':
                strategies[flow_name]['kde_count'] -= 2
                strategies[flow_name]['basic_validation'] = True
        
        return strategies
    
    def generate_mixed_role_kde_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Generate data flow-specific KDE mappings"""
        
        kde_mappings = {}
        
        for flow_name, flow_config in self.data_flows.items():
            role = flow_config['role']
            flow_type = flow_config['type']
            
            if role == 'consumer':
                # Consumer KDEs - input validation focused
                if flow_type == 'market_data':
                    kde_mappings[flow_name] = {
                        'price': {'risk': 'high', 'weight': 3, 'validation': 'input_only'},
                        'volume': {'risk': 'medium', 'weight': 2, 'validation': 'input_only'},
                        'timestamp': {'risk': 'high', 'weight': 3, 'validation': 'input_only'},
                        'symbol': {'risk': 'medium', 'weight': 2, 'validation': 'input_only'},
                        'exchange': {'risk': 'low', 'weight': 1, 'validation': 'input_only'}
                    }
                elif flow_type == 'trading_data':
                    kde_mappings[flow_name] = {
                        'trader_id': {'risk': 'high', 'weight': 3, 'validation': 'input_only'},
                        'trade_time': {'risk': 'high', 'weight': 3, 'validation': 'input_only'},
                        'notional': {'risk': 'high', 'weight': 3, 'validation': 'input_only'},
                        'quantity': {'risk': 'medium', 'weight': 2, 'validation': 'input_only'},
                        'price': {'risk': 'medium', 'weight': 2, 'validation': 'input_only'},
                        'instrument': {'risk': 'low', 'weight': 1, 'validation': 'input_only'}
                    }
                elif flow_type == 'reference_data':
                    kde_mappings[flow_name] = {
                        'symbol': {'risk': 'high', 'weight': 3, 'validation': 'input_only'},
                        'isin': {'risk': 'high', 'weight': 3, 'validation': 'input_only'},
                        'currency': {'risk': 'medium', 'weight': 2, 'validation': 'input_only'},
                        'sector': {'risk': 'low', 'weight': 1, 'validation': 'input_only'}
                    }
            
            elif role == 'producer':
                # Producer KDEs - full validation
                if flow_type == 'alert_data':
                    kde_mappings[flow_name] = {
                        'alert_id': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'alert_type': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'confidence_score': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'trader_id': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'trade_ids': {'risk': 'medium', 'weight': 2, 'validation': 'full_validation'},
                        'alert_timestamp': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'risk_score': {'risk': 'medium', 'weight': 2, 'validation': 'full_validation'}
                    }
                elif flow_type == 'case_data':
                    kde_mappings[flow_name] = {
                        'case_id': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'case_status': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'evidence_score': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'related_alerts': {'risk': 'medium', 'weight': 2, 'validation': 'full_validation'},
                        'assigned_analyst': {'risk': 'medium', 'weight': 2, 'validation': 'full_validation'},
                        'case_priority': {'risk': 'medium', 'weight': 2, 'validation': 'full_validation'},
                        'resolution_date': {'risk': 'low', 'weight': 1, 'validation': 'full_validation'}
                    }
                elif flow_type == 'regulatory_reports':
                    kde_mappings[flow_name] = {
                        'report_id': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'report_type': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'submission_date': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'data_completeness': {'risk': 'high', 'weight': 3, 'validation': 'full_validation'},
                        'validation_status': {'risk': 'medium', 'weight': 2, 'validation': 'full_validation'}
                    }
        
        return kde_mappings
    
    def generate_mixed_role_configuration(self) -> Dict[str, Any]:
        """Generate complete mixed-role DQSI configuration for the client"""
        
        strategies = self.determine_mixed_role_strategies()
        kde_mappings = self.generate_mixed_role_kde_mapping()
        
        # Generate flow-specific thresholds
        flow_thresholds = self._generate_flow_thresholds()
        
        # Build complete configuration
        self.dqsi_config = {
            'client_info': self.client_profile['basic_info'],
            'mixed_role_configuration': True,
            'data_flows': self.data_flows,
            'flow_strategies': strategies,
            'kde_mappings': kde_mappings,
            'flow_thresholds': flow_thresholds,
            'assessment_results': self.assessment_results,
            'implementation_roadmap': self._generate_mixed_role_roadmap(),
            'configuration_date': datetime.now().isoformat()
        }
        
        return self.dqsi_config
    
    def export_configuration(self, format: str = 'yaml', filepath: Optional[str] = None) -> str:
        """Export configuration to file"""
        
        if not self.dqsi_config:
            raise ValueError("No configuration generated. Run generate_mixed_role_configuration() first.")
        
        client_name = self.client_profile['basic_info']['name'].replace(' ', '_').lower()
        
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"mixed_role_dqsi_config_{client_name}_{timestamp}.{format}"
        
        if format.lower() == 'yaml':
            with open(filepath, 'w') as f:
                yaml.dump(self.dqsi_config, f, default_flow_style=False, indent=2)
        elif format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump(self.dqsi_config, f, indent=2)
        else:
            raise ValueError("Supported formats: 'yaml', 'json'")
        
        return filepath
    
    def _get_consumer_subdimensions(self) -> List[str]:
        """Get sub-dimensions for consumer flows"""
        return [
            'null_presence',
            'field_population', 
            'data_type',
            'length',
            'format',
            'range',
            'freshness',
            'volume_profile',
            'coverage_baseline'
        ]
    
    def _get_producer_subdimensions(self) -> List[str]:
        """Get sub-dimensions for producer flows"""
        return [
            'null_presence',
            'field_population',
            'data_type',
            'length',
            'format',
            'range',
            'freshness',
            'lag_detection',
            'volume_reconciliation',
            'coverage_baseline',
            'precision',
            'value_accuracy',
            'referential_accuracy',
            'duplicate_detection',
            'cross_system_uniqueness',
            'internal_consistency',
            'cross_system_consistency'
        ]
    
    def _generate_flow_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Generate flow-specific thresholds"""
        
        flow_thresholds = {}
        
        for flow_name, flow_config in self.data_flows.items():
            role = flow_config['role']
            flow_type = flow_config['type']
            
            if role == 'consumer':
                # Lighter thresholds for consumer flows
                flow_thresholds[flow_name] = {
                    'acceptable_null_rate': 0.15,
                    'critical_null_rate': 0.25,
                    'acceptable_delay_minutes': 30,
                    'critical_delay_minutes': 120,
                    'volume_drop_alert': 0.40,
                    'format_error_threshold': 0.10
                }
            elif role == 'producer':
                # Strict thresholds for producer flows
                flow_thresholds[flow_name] = {
                    'acceptable_null_rate': 0.05,
                    'critical_null_rate': 0.10,
                    'acceptable_delay_minutes': 10,
                    'critical_delay_minutes': 30,
                    'volume_drop_alert': 0.20,
                    'format_error_threshold': 0.02,
                    'accuracy_threshold': 0.95,
                    'uniqueness_threshold': 0.98,
                    'consistency_threshold': 0.90
                }
            
            # Adjust based on flow type
            if flow_type == 'alert_data':
                flow_thresholds[flow_name]['critical_null_rate'] = 0.01
                flow_thresholds[flow_name]['accuracy_threshold'] = 0.98
            elif flow_type == 'market_data':
                flow_thresholds[flow_name]['acceptable_delay_minutes'] = 5
                flow_thresholds[flow_name]['critical_delay_minutes'] = 15
        
        return flow_thresholds
    
    def _generate_mixed_role_roadmap(self) -> Dict[str, Dict[str, Any]]:
        """Generate mixed-role implementation roadmap"""
        
        consumer_flows = [name for name, config in self.data_flows.items() if config['role'] == 'consumer']
        producer_flows = [name for name, config in self.data_flows.items() if config['role'] == 'producer']
        
        return {
            'Phase 1': {
                'timeline': '1-3 months',
                'focus': 'Consumer Data Flows',
                'deliverables': [
                    f'Implement consumer strategy for: {", ".join(consumer_flows)}',
                    'Basic KDE scoring for input validation',
                    'Completeness and conformity validation',
                    'Feed monitoring and alerting'
                ]
            },
            'Phase 2': {
                'timeline': '4-6 months',
                'focus': 'Producer Data Flows Foundation',
                'deliverables': [
                    f'Implement producer strategy for: {", ".join(producer_flows)}',
                    'Enhanced KDE scoring',
                    'Foundational dimensions (completeness, conformity, timeliness, coverage)',
                    'Basic output quality monitoring'
                ]
            },
            'Phase 3': {
                'timeline': '7-12 months',
                'focus': 'Producer Data Flows Enhanced',
                'deliverables': [
                    'Full 7-dimension validation for produced data',
                    'Accuracy validation against golden sources',
                    'Cross-system consistency checking',
                    'Full regulatory compliance for outputs'
                ]
            },
            'Phase 4': {
                'timeline': '13-18 months',
                'focus': 'Optimization and Integration',
                'deliverables': [
                    'Cross-flow consistency validation',
                    'Performance optimization',
                    'Advanced analytics and trending',
                    'Continuous improvement framework'
                ]
            }
        }
    
    def generate_mixed_role_assessment_report(self) -> str:
        """Generate human-readable mixed-role assessment report"""
        
        if not self.assessment_results:
            return "No assessment conducted yet."
        
        report = []
        report.append("=" * 60)
        report.append("MIXED-ROLE DATA QUALITY GAP ASSESSMENT REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Client overview
        client = self.client_profile['basic_info']
        report.append(f"CLIENT: {client['name']}")
        report.append(f"Industry: {client['industry']}")
        report.append(f"Size: {client['employee_count']} employees")
        report.append(f"Trading Volume: ${client['daily_volume']:,.0f}/day")
        report.append(f"Regulatory Tier: {client['regulatory_tier']}")
        report.append("")
        
        # Data flow overview
        report.append("DATA FLOW ARCHITECTURE")
        report.append("-" * 25)
        consumer_flows = [name for name, config in self.data_flows.items() if config['role'] == 'consumer']
        producer_flows = [name for name, config in self.data_flows.items() if config['role'] == 'producer']
        
        report.append(f"Consumer Flows: {', '.join(consumer_flows)}")
        report.append(f"Producer Flows: {', '.join(producer_flows)}")
        report.append("")
        
        # Flow-specific assessment
        report.append("CURRENT STATE ASSESSMENT BY DATA FLOW")
        report.append("-" * 40)
        
        for flow_name, flow_results in self.assessment_results['flow_scores'].items():
            flow_config = self.data_flows[flow_name]
            role = flow_config['role'].upper()
            
            report.append(f"{flow_name} ({role}):")
            
            for dimension, score in flow_results['dimension_scores'].items():
                status = "CRITICAL" if score < 0.3 else "POOR" if score < 0.5 else "DEVELOPING" if score < 0.7 else "GOOD"
                report.append(f"  {dimension.capitalize()}: {score:.2f} ({score*100:.0f}%) - {status}")
            
            maturity = flow_results['flow_maturity']
            report.append(f"  Flow Maturity: {maturity:.2f} ({maturity*100:.0f}%) - {flow_results['maturity_level']}")
            report.append("")
        
        # Overall recommendations
        report.append("MIXED-ROLE RECOMMENDATIONS")
        report.append("-" * 27)
        
        consumer_avg = sum([results['flow_maturity'] for name, results in self.assessment_results['flow_scores'].items() 
                           if self.data_flows[name]['role'] == 'consumer']) / len(consumer_flows) if consumer_flows else 0
        producer_avg = sum([results['flow_maturity'] for name, results in self.assessment_results['flow_scores'].items() 
                           if self.data_flows[name]['role'] == 'producer']) / len(producer_flows) if producer_flows else 0
        
        report.append(f"Consumer Flow Average Maturity: {consumer_avg:.2f} ({consumer_avg*100:.0f}%)")
        report.append(f"Producer Flow Average Maturity: {producer_avg:.2f} ({producer_avg*100:.0f}%)")
        report.append("")
        
        if producer_avg < 0.3:
            report.append("CRITICAL: Producer flows require immediate attention")
            report.append("Focus: Implement basic validation for output data")
        elif consumer_avg < 0.3:
            report.append("CRITICAL: Consumer flows require immediate attention") 
            report.append("Focus: Implement basic validation for input data")
        else:
            report.append("Focus: Balanced improvement across both roles")
        
        return "\n".join(report)
    
    # Helper methods
    def _determine_maturity_level(self, score: float) -> str:
        if score < 0.3:
            return "CRITICAL"
        elif score < 0.5:
            return "POOR"
        elif score < 0.7:
            return "DEVELOPING"
        else:
            return "GOOD"
    
    def _score_firm_size(self, employee_count: int) -> float:
        if employee_count < 100:
            return 0.1
        elif employee_count < 500:
            return 0.3
        elif employee_count < 2000:
            return 0.6
        else:
            return 1.0
    
    def _score_trading_volume(self, daily_volume: float) -> float:
        if daily_volume < 1e6:  # < $1M
            return 0.1
        elif daily_volume < 1e8:  # < $100M
            return 0.3
        elif daily_volume < 1e9:  # < $1B
            return 0.6
        else:
            return 1.0
    
    def _score_regulatory_tier(self, tier: str) -> float:
        mapping = {
            'none': 0.0,
            'basic': 0.2,
            'moderate': 0.5,
            'tier2_bank': 0.7,
            'tier1_bank': 1.0,
            'regulatory_entity': 1.0
        }
        return mapping.get(tier, 0.0)
    
    def _score_it_maturity(self, maturity: str) -> float:
        mapping = {
            'basic': 0.2,
            'developing': 0.4,
            'medium': 0.6,
            'advanced': 0.8,
            'leading': 1.0
        }
        return mapping.get(maturity, 0.2)
    
    def _score_budget(self, budget: str) -> float:
        mapping = {
            'minimal': 0.1,
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'unlimited': 1.0
        }
        return mapping.get(budget, 0.3)
    
    def _generate_thresholds(self) -> Dict[str, float]:
        """Generate calibrated scoring thresholds based on client profile"""
        
        # Base thresholds
        base_thresholds = {
            'critical_null_rate': 0.05,
            'acceptable_null_rate': 0.10,
            'critical_delay_minutes': 60,
            'acceptable_delay_minutes': 15,
            'volume_drop_alert': 0.30,
            'format_error_threshold': 0.05
        }
        
        # Adjust based on client requirements
        business_focus = self.client_profile['business_priorities']['primary_focus']
        regulatory_level = self.client_profile['basic_info']['regulatory_tier']
        
        if business_focus == 'high_frequency':
            base_thresholds['critical_delay_minutes'] = 1
            base_thresholds['acceptable_delay_minutes'] = 0.1
            
        if regulatory_level in ['tier1_bank', 'regulatory_entity']:
            base_thresholds['critical_null_rate'] = 0.01
            base_thresholds['acceptable_null_rate'] = 0.05
            base_thresholds['format_error_threshold'] = 0.01
        
        return base_thresholds
    
    def _generate_roadmap(self, strategy: str) -> Dict[str, Dict[str, Any]]:
        """Generate implementation roadmap based on strategy"""
        
        if strategy == 'fallback':
            return {
                'Phase 1': {
                    'timeline': '1-2 months',
                    'focus': 'Basic DQSI implementation',
                    'deliverables': [
                        'Fallback strategy deployment',
                        'Basic KDE scoring',
                        'Completeness monitoring',
                        'Simple alerting'
                    ]
                },
                'Phase 2': {
                    'timeline': '3-4 months',
                    'focus': 'Enhancement and optimization',
                    'deliverables': [
                        'Conformity validation',
                        'Timeliness monitoring',
                        'Reporting dashboards',
                        'Process automation'
                    ]
                }
            }
        
        elif strategy == 'role_aware_consumer':
            return {
                'Phase 1': {
                    'timeline': '2-3 months',
                    'focus': 'Foundational capabilities',
                    'deliverables': [
                        'Role-aware strategy (consumer mode)',
                        'Enhanced KDE scoring',
                        'Reference table integration',
                        'Coverage monitoring'
                    ]
                },
                'Phase 2': {
                    'timeline': '4-6 months',
                    'focus': 'Advanced monitoring',
                    'deliverables': [
                        'Baseline establishment',
                        'Trend analysis',
                        'Advanced alerting',
                        'Integration with existing tools'
                    ]
                }
            }
        
        else:  # role_aware_producer
            return {
                'Phase 1': {
                    'timeline': '3-4 months',
                    'focus': 'Foundational + Enhanced',
                    'deliverables': [
                        'Role-aware strategy (producer mode)',
                        'All 7 dimensions implementation',
                        'Golden source integration',
                        'Cross-system validation'
                    ]
                },
                'Phase 2': {
                    'timeline': '5-8 months',
                    'focus': 'Advanced capabilities',
                    'deliverables': [
                        'Accuracy validation',
                        'Uniqueness checking',
                        'Consistency validation',
                        'Full regulatory compliance'
                    ]
                },
                'Phase 3': {
                    'timeline': '9-12 months',
                    'focus': 'Optimization and governance',
                    'deliverables': [
                        'Performance optimization',
                        'Advanced analytics',
                        'Governance framework',
                        'Continuous improvement'
                    ]
                }
            }


def main():
    """Example usage of the mixed-role gap assessment tool"""
    
    # Initialize tool
    assessment_tool = ClientGapAssessmentTool()
    
    # Example client responses
    client_responses = {
        'company_name': 'MidTier Investment Bank',
        'industry': 'investment_banking',
        'employee_count': 2500,
        'daily_trading_volume': 5e9,  # $5B
        'regulatory_level': 'tier2_bank',
        'it_maturity': 'medium',
        'dq_tools': ['informatica', 'manual_processes'],
        'automation_level': 'partial',
        'integration_apis': True,
        'primary_business_focus': 'trading',
        'regulatory_pressure': 'high',
        'risk_tolerance': 'medium',
        'dq_budget': 'medium'
    }
    
    # Mixed-role data flow configuration
    data_flows = {
        'market_data_feed': {
            'role': 'consumer',
            'type': 'market_data',
            'source_destination': 'Bloomberg/Reuters',
            'criticality': 'high',
            'volume': 'high',
            'frequency': 'realtime'
        },
        'trading_data_feed': {
            'role': 'consumer',
            'type': 'trading_data',
            'source_destination': 'OMS/Settlement',
            'criticality': 'high',
            'volume': 'high',
            'frequency': 'realtime'
        },
        'reference_data_feed': {
            'role': 'consumer',
            'type': 'reference_data',
            'source_destination': 'Vendor feeds',
            'criticality': 'medium',
            'volume': 'medium',
            'frequency': 'daily'
        },
        'surveillance_alerts': {
            'role': 'producer',
            'type': 'alert_data',
            'source_destination': 'Case Management System',
            'criticality': 'high',
            'volume': 'medium',
            'frequency': 'realtime'
        },
        'compliance_cases': {
            'role': 'producer',
            'type': 'case_data',
            'source_destination': 'Regulatory Reporting',
            'criticality': 'high',
            'volume': 'low',
            'frequency': 'daily'
        }
    }
    
    # Current capabilities by flow
    current_capabilities = {
        'market_data_feed': {
            'completeness': {'level': 'basic_null_check'},
            'conformity': {'level': 'type_validation'},
            'timeliness': {'level': 'near_realtime'},
            'coverage': {'level': 'automated_profiling'}
        },
        'trading_data_feed': {
            'completeness': {'level': 'etl_validation'},
            'conformity': {'level': 'basic_format'},
            'timeliness': {'level': 'manual_monitoring'},
            'coverage': {'level': 'spreadsheet_monitoring'}
        },
        'reference_data_feed': {
            'completeness': {'level': 'basic_null_check'},
            'conformity': {'level': 'reference_tables'},
            'timeliness': {'level': 'batch_reporting'},
            'coverage': {'level': 'manual_tracking'}
        },
        'surveillance_alerts': {
            'completeness': {'level': 'business_rules'},
            'conformity': {'level': 'basic_format'},
            'timeliness': {'level': 'manual_monitoring'},
            'coverage': {'level': 'manual_tracking'},
            'accuracy': {'level': 'manual_reconciliation'},
            'uniqueness': {'level': 'basic_duplicate_check'},
            'consistency': {'level': 'none'}
        },
        'compliance_cases': {
            'completeness': {'level': 'automated_monitoring'},
            'conformity': {'level': 'comprehensive_rules'},
            'timeliness': {'level': 'batch_reporting'},
            'coverage': {'level': 'spreadsheet_monitoring'},
            'accuracy': {'level': 'periodic_validation'},
            'uniqueness': {'level': 'system_level_dedup'},
            'consistency': {'level': 'manual_reconciliation'}
        }
    }
    
    # Conduct mixed-role assessment
    print("🔍 Conducting Mixed-Role Client Gap Assessment...")
    print()
    
    assessment_tool.conduct_discovery_interview(client_responses)
    assessment_tool.map_data_flows(data_flows)
    assessment_tool.assess_current_state_by_flow(current_capabilities)
    config = assessment_tool.generate_mixed_role_configuration()
    
    # Generate report
    report = assessment_tool.generate_mixed_role_assessment_report()
    print(report)
    
    # Export configuration
    config_file = assessment_tool.export_configuration('yaml')
    print(f"✅ Mixed-role configuration exported to: {config_file}")


if __name__ == "__main__":
    main()