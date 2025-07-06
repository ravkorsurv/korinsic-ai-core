#!/usr/bin/env python3
"""
Client Data Quality Gap Assessment Tool

This tool conducts a structured gap assessment for implementing DQSI 
at client sites and generates customized configurations.
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
    
    def assess_current_state(self, current_capabilities: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Assess current data quality capabilities
        
        Args:
            current_capabilities: Current DQ capabilities by dimension
            
        Returns:
            Dimension scores and overall maturity
        """
        dimension_scores = {}
        
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
        
        for dimension, capability_level in current_capabilities.items():
            level = capability_level.get('level', 'none')
            if dimension in scoring_criteria and level in scoring_criteria[dimension]:
                dimension_scores[dimension] = scoring_criteria[dimension][level]
            else:
                dimension_scores[dimension] = 0.0
        
        # Calculate overall maturity
        overall_maturity = sum(dimension_scores.values()) / len(dimension_scores)
        
        self.assessment_results = {
            'dimension_scores': dimension_scores,
            'overall_maturity': overall_maturity,
            'maturity_level': self._determine_maturity_level(overall_maturity),
            'assessment_date': datetime.now().isoformat()
        }
        
        return dimension_scores
    
    def determine_strategy(self) -> str:
        """Determine appropriate DQSI strategy based on client profile"""
        profile = self.client_profile
        
        # Strategy decision factors
        factors = {
            'size_score': self._score_firm_size(profile['basic_info']['employee_count']),
            'volume_score': self._score_trading_volume(profile['basic_info']['daily_volume']),
            'regulatory_score': self._score_regulatory_tier(profile['basic_info']['regulatory_tier']),
            'maturity_score': self._score_it_maturity(profile['technical_maturity']['it_sophistication']),
            'budget_score': self._score_budget(profile['business_priorities']['budget_range'])
        }
        
        # Calculate weighted strategy score
        weights = {'size_score': 0.2, 'volume_score': 0.2, 'regulatory_score': 0.3, 
                  'maturity_score': 0.2, 'budget_score': 0.1}
        
        weighted_score = sum(factors[factor] * weights[factor] for factor in factors)
        
        # Determine strategy
        if weighted_score >= 0.7:
            strategy = 'role_aware_producer'
        elif weighted_score >= 0.4:
            strategy = 'role_aware_consumer'
        else:
            strategy = 'fallback'
        
        return strategy
    
    def generate_kde_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Generate client-specific KDE mapping"""
        
        # Base KDE mappings
        base_kdes = {
            'trader_id': {'risk': 'high', 'weight': 3},
            'trade_time': {'risk': 'high', 'weight': 3},
            'order_timestamp': {'risk': 'high', 'weight': 3},
            'notional': {'risk': 'medium', 'weight': 2},
            'quantity': {'risk': 'medium', 'weight': 2},
            'price': {'risk': 'medium', 'weight': 2},
            'desk_id': {'risk': 'low', 'weight': 1},
            'instrument': {'risk': 'low', 'weight': 1},
            'client_id': {'risk': 'low', 'weight': 1}
        }
        
        # Client-specific adjustments
        profile = self.client_profile
        business_focus = profile['business_priorities']['primary_focus']
        regulatory_level = profile['basic_info']['regulatory_tier']
        
        # Adjust based on business focus
        if business_focus == 'client_services':
            base_kdes['client_id']['risk'] = 'high'
            base_kdes['client_id']['weight'] = 3
            
        elif business_focus == 'risk_management':
            base_kdes['notional']['risk'] = 'high'
            base_kdes['notional']['weight'] = 3
            base_kdes['price']['risk'] = 'high'
            base_kdes['price']['weight'] = 3
            
        elif business_focus == 'high_frequency':
            base_kdes['trade_time']['weight'] = 4  # Special weight for HFT
            base_kdes['order_timestamp']['weight'] = 4
            
        # Adjust based on regulatory requirements
        if regulatory_level in ['tier1_bank', 'regulatory_entity']:
            # Add regulatory-specific KDEs
            base_kdes['regulatory_flag'] = {'risk': 'high', 'weight': 3}
            base_kdes['counterparty'] = {'risk': 'medium', 'weight': 2}
            
        return base_kdes
    
    def generate_configuration(self) -> Dict[str, Any]:
        """Generate complete DQSI configuration for the client"""
        
        strategy = self.determine_strategy()
        kde_mapping = self.generate_kde_mapping()
        
        # Determine enabled sub-dimensions based on strategy
        if strategy == 'fallback':
            enabled_subdims = [
                'null_presence', 'data_type', 'format', 'freshness', 'volume_profile'
            ]
        elif strategy == 'role_aware_consumer':
            enabled_subdims = [
                'null_presence', 'field_population', 'data_type', 'length', 
                'format', 'range', 'freshness', 'volume_profile', 'coverage_baseline'
            ]
        else:  # role_aware_producer
            enabled_subdims = [
                'null_presence', 'field_population', 'data_type', 'length',
                'format', 'range', 'freshness', 'lag_detection', 
                'volume_reconciliation', 'coverage_baseline',
                'precision', 'value_accuracy', 'referential_accuracy',
                'duplicate_detection', 'cross_system_uniqueness',
                'internal_consistency', 'cross_system_consistency'
            ]
        
        # Generate calibrated thresholds
        thresholds = self._generate_thresholds()
        
        # Build complete configuration
        self.dqsi_config = {
            'client_info': self.client_profile['basic_info'],
            'strategy': strategy,
            'kde_mappings': kde_mapping,
            'enabled_subdimensions': enabled_subdims,
            'thresholds': thresholds,
            'assessment_results': self.assessment_results,
            'implementation_roadmap': self._generate_roadmap(strategy),
            'configuration_date': datetime.now().isoformat()
        }
        
        return self.dqsi_config
    
    def export_configuration(self, format: str = 'yaml', filepath: Optional[str] = None) -> str:
        """Export configuration to file"""
        
        if not self.dqsi_config:
            raise ValueError("No configuration generated. Run generate_configuration() first.")
        
        client_name = self.client_profile['basic_info']['name'].replace(' ', '_').lower()
        
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"dqsi_config_{client_name}_{timestamp}.{format}"
        
        if format.lower() == 'yaml':
            with open(filepath, 'w') as f:
                yaml.dump(self.dqsi_config, f, default_flow_style=False, indent=2)
        elif format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump(self.dqsi_config, f, indent=2)
        else:
            raise ValueError("Supported formats: 'yaml', 'json'")
        
        return filepath
    
    def generate_assessment_report(self) -> str:
        """Generate human-readable assessment report"""
        
        if not self.assessment_results:
            return "No assessment conducted yet."
        
        report = []
        report.append("=" * 60)
        report.append("DATA QUALITY GAP ASSESSMENT REPORT")
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
        
        # Current state assessment
        report.append("CURRENT STATE ASSESSMENT")
        report.append("-" * 30)
        
        for dimension, score in self.assessment_results['dimension_scores'].items():
            status = "CRITICAL" if score < 0.3 else "POOR" if score < 0.5 else "DEVELOPING" if score < 0.7 else "GOOD"
            report.append(f"  {dimension.capitalize()}: {score:.2f} ({score*100:.0f}%) - {status}")
        
        overall = self.assessment_results['overall_maturity']
        report.append("")
        report.append(f"OVERALL MATURITY: {overall:.2f} ({overall*100:.0f}%) - {self.assessment_results['maturity_level']}")
        report.append("")
        
        # Recommendations
        strategy = self.determine_strategy()
        report.append("RECOMMENDATIONS")
        report.append("-" * 15)
        report.append(f"Recommended Strategy: {strategy}")
        
        if overall < 0.3:
            report.append("Priority: IMMEDIATE ACTION REQUIRED")
            report.append("Focus: Implement basic foundational capabilities")
        elif overall < 0.5:
            report.append("Priority: Significant improvement needed")
            report.append("Focus: Systematic improvement program")
        else:
            report.append("Priority: Structured enhancement")
            report.append("Focus: Advanced capabilities and optimization")
        
        report.append("")
        
        # Implementation roadmap
        roadmap = self._generate_roadmap(strategy)
        report.append("IMPLEMENTATION ROADMAP")
        report.append("-" * 22)
        
        for phase, details in roadmap.items():
            report.append(f"{phase}:")
            report.append(f"  Timeline: {details['timeline']}")
            report.append(f"  Focus: {details['focus']}")
            for item in details['deliverables']:
                report.append(f"    • {item}")
            report.append("")
        
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
    """Example usage of the gap assessment tool"""
    
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
    
    # Current capabilities assessment
    current_capabilities = {
        'completeness': {'level': 'etl_validation'},
        'conformity': {'level': 'basic_format'},
        'timeliness': {'level': 'manual_monitoring'},
        'coverage': {'level': 'spreadsheet_monitoring'},
        'accuracy': {'level': 'manual_reconciliation'},
        'uniqueness': {'level': 'basic_duplicate_check'},
        'consistency': {'level': 'none'}
    }
    
    # Conduct assessment
    print("🔍 Conducting Client Gap Assessment...")
    print()
    
    assessment_tool.conduct_discovery_interview(client_responses)
    assessment_tool.assess_current_state(current_capabilities)
    config = assessment_tool.generate_configuration()
    
    # Generate report
    report = assessment_tool.generate_assessment_report()
    print(report)
    
    # Export configuration
    config_file = assessment_tool.export_configuration('yaml')
    print(f"✅ Configuration exported to: {config_file}")


if __name__ == "__main__":
    main()