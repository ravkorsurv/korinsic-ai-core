"""
Regulatory Service for generating regulatory rationales and compliance reporting.

This service handles the generation of regulatory explanations and rationales
for market abuse detection alerts to support compliance and regulatory reporting.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..regulatory_explainability import RegulatoryExplainability
from ...utils.logger import setup_logger

logger = setup_logger()


class RegulatoryService:
    """
    Service for generating regulatory rationales and compliance reporting.
    
    This service provides regulatory explainability features including:
    - Deterministic narrative generation
    - Inference path analysis
    - Value of Information (VoI) analysis
    - Sensitivity analysis
    - Regulatory framework mapping
    """
    
    def __init__(self):
        """Initialize the regulatory service."""
        self.supported_frameworks = [
            'MAR',  # Market Abuse Regulation
            'STOR', # Suspicious Transaction and Order Reporting
            'SMCR', # Senior Managers and Certification Regime
            'MiFID_II', # Markets in Financial Instruments Directive II
            'CFTC', # Commodity Futures Trading Commission
            'SEC'   # Securities and Exchange Commission
        ]
    
    def generate_rationales(self, alerts: List[Dict[str, Any]], 
                          risk_scores: Dict[str, Any],
                          processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate regulatory rationales for a list of alerts.
        
        Args:
            alerts: List of generated alerts
            risk_scores: Risk scores from analysis
            processed_data: Processed trading data
            
        Returns:
            List of regulatory rationales for each alert
        """
        rationales = []
        
        for alert in alerts:
            try:
                # Determine which risk scores to use based on alert type
                if alert['type'] == 'INSIDER_DEALING':
                    alert_risk_scores = risk_scores.get('insider_dealing', {})
                elif alert['type'] == 'SPOOFING':
                    alert_risk_scores = risk_scores.get('spoofing', {})
                else:
                    alert_risk_scores = {'overall_score': risk_scores.get('overall_risk', 0)}
                
                # Generate rationale for this alert
                rationale = self.generate_single_rationale(
                    alert, alert_risk_scores, processed_data
                )
                
                if rationale:
                    rationales.append(rationale)
                    
            except Exception as e:
                logger.error(f"Error generating regulatory rationale for alert {alert.get('id')}: {str(e)}")
                # Continue with other alerts even if one fails
                continue
        
        return rationales
    
    def generate_single_rationale(self, alert: Dict[str, Any], 
                                 risk_scores: Dict[str, Any],
                                 processed_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate a regulatory rationale for a single alert.
        
        Args:
            alert: Alert to generate rationale for
            risk_scores: Risk scores for the alert
            processed_data: Processed trading data
            
        Returns:
            Regulatory rationale dictionary or None if generation fails
        """
        try:
            # Use the existing regulatory explainability module
            rationale = generate_regulatory_rationale(alert, risk_scores, processed_data)
            
            # Format the rationale for API response
            formatted_rationale = {
                'alert_id': alert.get('id'),
                'timestamp': datetime.utcnow().isoformat(),
                'deterministic_narrative': rationale.deterministic_narrative,
                'inference_paths': [
                    {
                        'node_name': path.node_name,
                        'evidence_value': path.evidence_value,
                        'probability': path.probability,
                        'contribution': path.contribution,
                        'rationale': path.rationale,
                        'confidence': path.confidence,
                        'regulatory_relevance': path.regulatory_relevance
                    }
                    for path in rationale.inference_paths
                ],
                'voi_analysis': rationale.voi_analysis,
                'sensitivity_report': rationale.sensitivity_report,
                'regulatory_frameworks': rationale.regulatory_frameworks,
                'audit_trail': rationale.audit_trail,
                'compliance_notes': self._generate_compliance_notes(alert, risk_scores),
                'regulatory_risk_assessment': self._assess_regulatory_risk(alert, risk_scores)
            }
            
            return formatted_rationale
            
        except Exception as e:
            logger.error(f"Error in generate_single_rationale: {str(e)}")
            return None
    
    def _generate_compliance_notes(self, alert: Dict[str, Any], 
                                 risk_scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate compliance-specific notes for the alert.
        
        Args:
            alert: Alert information
            risk_scores: Risk scores
            
        Returns:
            Compliance notes dictionary
        """
        notes = {
            'alert_type': alert.get('type'),
            'risk_level': alert.get('severity'),
            'compliance_actions': [],
            'regulatory_thresholds': {},
            'reporting_requirements': []
        }
        
        # Add specific compliance actions based on alert type
        if alert.get('type') == 'INSIDER_DEALING':
            notes['compliance_actions'].extend([
                'Review trader access to material information',
                'Investigate trading timing relative to information events',
                'Document investigation findings',
                'Consider STOR reporting if threshold exceeded'
            ])
            notes['regulatory_thresholds']['stor_threshold'] = 0.7
            notes['reporting_requirements'].append('STOR (if applicable)')
            
        elif alert.get('type') == 'SPOOFING':
            notes['compliance_actions'].extend([
                'Analyze order placement and cancellation patterns',
                'Review trader intent and market impact',
                'Document market manipulation evidence',
                'Consider regulatory notification'
            ])
            notes['regulatory_thresholds']['manipulation_threshold'] = 0.6
            notes['reporting_requirements'].append('Market Surveillance Report')
        
        # Add general compliance considerations
        risk_score = risk_scores.get('overall_score', 0)
        if risk_score >= 0.8:
            notes['compliance_actions'].append('Escalate to senior compliance officer')
            notes['compliance_actions'].append('Consider immediate trading restrictions')
        
        return notes
    
    def _assess_regulatory_risk(self, alert: Dict[str, Any], 
                              risk_scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess regulatory risk level and implications.
        
        Args:
            alert: Alert information
            risk_scores: Risk scores
            
        Returns:
            Regulatory risk assessment
        """
        overall_score = risk_scores.get('overall_score', 0)
        alert_type = alert.get('type')
        
        # Determine regulatory risk level
        if overall_score >= 0.9:
            risk_level = 'CRITICAL'
            regulatory_priority = 'IMMEDIATE'
        elif overall_score >= 0.7:
            risk_level = 'HIGH'
            regulatory_priority = 'URGENT'
        elif overall_score >= 0.5:
            risk_level = 'MEDIUM'
            regulatory_priority = 'STANDARD'
        else:
            risk_level = 'LOW'
            regulatory_priority = 'MONITORING'
        
        # Determine potential regulatory consequences
        consequences = []
        if alert_type == 'INSIDER_DEALING':
            if overall_score >= 0.8:
                consequences.extend([
                    'Potential FCA investigation',
                    'Criminal prosecution risk',
                    'Significant financial penalties',
                    'Reputational damage'
                ])
            elif overall_score >= 0.6:
                consequences.extend([
                    'Regulatory scrutiny',
                    'Enhanced monitoring requirements',
                    'Potential administrative action'
                ])
                
        elif alert_type == 'SPOOFING':
            if overall_score >= 0.8:
                consequences.extend([
                    'Market manipulation charges',
                    'Trading ban possibility',
                    'Civil monetary penalties',
                    'Disgorgement of profits'
                ])
            elif overall_score >= 0.6:
                consequences.extend([
                    'Warning letter',
                    'Enhanced surveillance',
                    'Trading restrictions'
                ])
        
        return {
            'regulatory_risk_level': risk_level,
            'priority': regulatory_priority,
            'potential_consequences': consequences,
            'recommended_actions': self._get_recommended_actions(risk_level, alert_type),
            'timeline': self._get_response_timeline(risk_level)
        }
    
    def _get_recommended_actions(self, risk_level: str, alert_type: str) -> List[str]:
        """Get recommended actions based on risk level and alert type."""
        actions = []
        
        if risk_level == 'CRITICAL':
            actions.extend([
                'Immediate escalation to Chief Compliance Officer',
                'Consider trading suspension',
                'Prepare regulatory notification',
                'Engage external legal counsel',
                'Document all evidence'
            ])
        elif risk_level == 'HIGH':
            actions.extend([
                'Escalate to senior compliance team',
                'Enhanced monitoring of trader',
                'Detailed investigation',
                'Prepare preliminary report'
            ])
        elif risk_level == 'MEDIUM':
            actions.extend([
                'Standard investigation procedures',
                'Monitor for pattern development',
                'Document findings'
            ])
        else:  # LOW
            actions.extend([
                'Continue routine monitoring',
                'Log for trend analysis'
            ])
        
        return actions
    
    def _get_response_timeline(self, risk_level: str) -> str:
        """Get recommended response timeline based on risk level."""
        timelines = {
            'CRITICAL': 'Immediate (within 1 hour)',
            'HIGH': 'Urgent (within 4 hours)',
            'MEDIUM': 'Standard (within 24 hours)',
            'LOW': 'Routine (within 1 week)'
        }
        
        return timelines.get(risk_level, 'Standard (within 24 hours)')
    
    def generate_stor_report(self, alert: Dict[str, Any], 
                           risk_scores: Dict[str, Any],
                           processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a STOR (Suspicious Transaction and Order Reporting) report.
        
        Args:
            alert: Alert information
            risk_scores: Risk scores
            processed_data: Processed trading data
            
        Returns:
            STOR report data
        """
        # This would generate a full STOR report
        # For now, return a placeholder structure
        return {
            'report_id': f"STOR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'alert_id': alert.get('id'),
            'timestamp': datetime.utcnow().isoformat(),
            'report_type': 'STOR',
            'regulatory_framework': 'MAR',
            'status': 'DRAFT'
        }