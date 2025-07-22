import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from .regulatory_explainability import RegulatoryExplainability, RegulatoryRationale, STORRecord

logger = logging.getLogger(__name__)

class AlertService:
    """
    Alert generation system for market abuse detection
    """
    
    def __init__(self):
        self.alert_thresholds = {
            'insider_dealing': {
                'high_risk': 0.7,
                'medium_risk': 0.4
            },
            'spoofing': {
                'high_risk': 0.8,
                'medium_risk': 0.5
            },
            'overall_risk': {
                'critical': 0.8,
                'high': 0.6,
                'medium': 0.4
            }
        }
        
        self.alert_history = []
        self.regulatory_explainability = RegulatoryExplainability()
    
    def generate_alerts(self, processed_data: Dict, insider_score: Dict, 
                       spoofing_score: Dict, overall_risk: float) -> List[Dict]:
        """Generate alerts based on risk scores and thresholds, with news context and dynamic fields"""
        alerts = []
        try:
            # News context suppression logic
            news_context = insider_score.get('news_context', 2)
            # 0 = explained, 1 = partial, 2 = unexplained
            if news_context == 0:
                logger.info("Suppressing alerts due to explained move (news context)")
                return []
            # Check insider dealing alerts
            insider_alerts = self._check_insider_dealing_alerts(
                processed_data, insider_score
            )
            alerts.extend(insider_alerts)
            # Check spoofing alerts
            spoofing_alerts = self._check_spoofing_alerts(
                processed_data, spoofing_score
            )
            alerts.extend(spoofing_alerts)
            # Check overall risk alerts
            overall_alerts = self._check_overall_risk_alerts(
                processed_data, overall_risk
            )
            alerts.extend(overall_alerts)
            # Store alerts in history
            for alert in alerts:
                self.alert_history.append(alert)
                logger.warning(f"ALERT GENERATED: {alert['type']} - {alert['severity']}")
            return alerts
        except Exception as e:
            logger.error(f"Error generating alerts: {str(e)}")
            return []
    
    def _check_insider_dealing_alerts(self, data: Dict, scores: Dict) -> List[Dict]:
        """Check for insider dealing alerts, include dynamic fields"""
        alerts = []
        if 'error' in scores:
            return alerts
        overall_score = scores.get('overall_score', 0)
        thresholds = self.alert_thresholds['insider_dealing']
        if overall_score >= thresholds['high_risk']:
            severity = 'HIGH'
        elif overall_score >= thresholds['medium_risk']:
            severity = 'MEDIUM'
        else:
            return alerts
        alert = {
            'id': f"insider_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'type': 'INSIDER_DEALING',
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'risk_score': overall_score,
            'trader_id': data.get('trader_info', {}).get('id'),
            'description': self._generate_insider_description(data, scores),
            'evidence': self._compile_insider_evidence(data, scores),
            'recommended_actions': self._get_insider_actions(severity),
            'instruments': data.get('instruments', []),
            'timeframe': data.get('timeframe'),
            # New dynamic fields
            'news_context': scores.get('news_context', None),
            'high_nodes': scores.get('high_nodes', []),
            'critical_nodes': scores.get('critical_nodes', []),
            'explanation': scores.get('explanation', None),
            'esi': scores.get('esi', {})
        }
        alerts.append(alert)
        return alerts
    
    def _check_spoofing_alerts(self, data: Dict, scores: Dict) -> List[Dict]:
        """Check for spoofing alerts, include dynamic fields"""
        alerts = []
        if 'error' in scores:
            return alerts
        overall_score = scores.get('overall_score', 0)
        thresholds = self.alert_thresholds['spoofing']
        if overall_score >= thresholds['high_risk']:
            severity = 'HIGH'
        elif overall_score >= thresholds['medium_risk']:
            severity = 'MEDIUM'
        else:
            return alerts
        alert = {
            'id': f"spoofing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'type': 'SPOOFING',
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'risk_score': overall_score,
            'trader_id': data.get('trader_info', {}).get('id'),
            'description': self._generate_spoofing_description(data, scores),
            'evidence': self._compile_spoofing_evidence(data, scores),
            'recommended_actions': self._get_spoofing_actions(severity),
            'instruments': data.get('instruments', []),
            'timeframe': data.get('timeframe'),
            # New dynamic fields
            'news_context': scores.get('news_context', None),
            'high_nodes': scores.get('high_nodes', []),
            'critical_nodes': scores.get('critical_nodes', []),
            'explanation': scores.get('explanation', None),
            'esi': scores.get('esi', {})
        }
        alerts.append(alert)
        return alerts
    
    def _check_overall_risk_alerts(self, data: Dict, overall_risk: float) -> List[Dict]:
        """Check for overall risk alerts"""
        alerts = []
        thresholds = self.alert_thresholds['overall_risk']
        
        if overall_risk >= thresholds['critical']:
            severity = 'CRITICAL'
        elif overall_risk >= thresholds['high']:
            severity = 'HIGH'
        elif overall_risk >= thresholds['medium']:
            severity = 'MEDIUM'
        else:
            return alerts
        
        alert = {
            'id': f"overall_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'type': 'OVERALL_RISK',
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'risk_score': overall_risk,
            'trader_id': data.get('trader_info', {}).get('id', 'unknown'),
            'description': f"Overall market abuse risk score of {overall_risk:.2f} exceeds threshold",
            'evidence': {
                'risk_score': overall_risk,
                'trades_count': len(data.get('trades', [])),
                'orders_count': len(data.get('orders', [])),
                'timeframe': data.get('timeframe', 'unknown')
            },
            'recommended_actions': self._get_overall_actions(severity),
            'instruments': data.get('instruments', []),
            'timeframe': data.get('timeframe', 'unknown')
        }
        
        alerts.append(alert)
        return alerts
    
    def _generate_insider_description(self, data: Dict, scores: Dict) -> str:
        """Generate description for insider dealing alert, include news context and nodes"""
        evidence_factors = scores.get('evidence_factors', {})
        trader_role = data.get('trader_info', {}).get('role', 'unknown')
        trades_count = len(data.get('trades', []))
        news_context = scores.get('news_context', None)
        high_nodes = scores.get('high_nodes', [])
        critical_nodes = scores.get('critical_nodes', [])
        description = f"Potential insider dealing detected for {trader_role} with {trades_count} trades. "
        if news_context == 0:
            description += "(Move explained by public news/event.) "
        elif news_context == 1:
            description += "(Partially explained by news/event.) "
        elif news_context == 2:
            description += "(Unexplained move.) "
        if high_nodes:
            description += f"High-risk nodes: {', '.join(high_nodes)}. "
        if critical_nodes:
            description += f"Critical nodes: {', '.join(critical_nodes)}. "
        if evidence_factors.get('MaterialInfo', 0) >= 1:
            description += "Trader has potential access to material information. "
        if evidence_factors.get('Timing', 0) >= 1:
            description += "Suspicious timing relative to material events. "
        if evidence_factors.get('TradingActivity', 0) >= 1:
            description += "Unusual trading activity detected. "
        return description
    
    def _generate_spoofing_description(self, data: Dict, scores: Dict) -> str:
        """Generate description for spoofing alert, include news context and nodes"""
        evidence_factors = scores.get('evidence_factors', {})
        orders_count = len(data.get('orders', []))
        news_context = scores.get('news_context', None)
        high_nodes = scores.get('high_nodes', [])
        critical_nodes = scores.get('critical_nodes', [])
        description = f"Potential spoofing activity detected with {orders_count} orders. "
        if news_context == 0:
            description += "(Move explained by public news/event.) "
        elif news_context == 1:
            description += "(Partially explained by news/event.) "
        elif news_context == 2:
            description += "(Unexplained move.) "
        if high_nodes:
            description += f"High-risk nodes: {', '.join(high_nodes)}. "
        if critical_nodes:
            description += f"Critical nodes: {', '.join(critical_nodes)}. "
        if evidence_factors.get('OrderPattern', 0) >= 1:
            description += "Layered ordering patterns identified. "
        if evidence_factors.get('CancellationRate', 0) >= 1:
            description += "High order cancellation rate observed. "
        if evidence_factors.get('VolumeRatio', 0) >= 1:
            description += "Volume imbalance detected. "
        return description
    
    def _compile_insider_evidence(self, data: Dict, scores: Dict) -> Dict:
        """Compile evidence for insider dealing alert, include dynamic fields"""
        return {
            'risk_scores': scores,
            'trader_info': data.get('trader_info', {}),
            'insider_indicators': data.get('insider_indicators', []),
            'material_events_count': len(data.get('material_events', [])),
            'pre_event_trading': data.get('metrics', {}).get('pre_event_trading', 0),
            'unusual_volume': data.get('metrics', {}).get('avg_volume', 0),
            'price_impact': data.get('metrics', {}).get('price_impact', 0),
            'news_context': scores.get('news_context', None),
            'high_nodes': scores.get('high_nodes', []),
            'critical_nodes': scores.get('critical_nodes', []),
            'explanation': scores.get('explanation', None)
        }
    
    def _compile_spoofing_evidence(self, data: Dict, scores: Dict) -> Dict:
        """Compile evidence for spoofing alert, include dynamic fields"""
        return {
            'risk_scores': scores,
            'cancellation_ratio': data.get('metrics', {}).get('cancellation_ratio', 0),
            'order_frequency': data.get('metrics', {}).get('order_frequency', 0),
            'volume_imbalance': data.get('metrics', {}).get('volume_imbalance', 0),
            'large_orders_count': len([o for o in data.get('orders', []) if o.get('size', 0) > 10000]),
            'cancelled_orders_count': len([o for o in data.get('orders', []) if o.get('status') == 'cancelled']),
            'news_context': scores.get('news_context', None),
            'high_nodes': scores.get('high_nodes', []),
            'critical_nodes': scores.get('critical_nodes', []),
            'explanation': scores.get('explanation', None)
        }
    
    def _get_insider_actions(self, severity: str) -> List[str]:
        """Get recommended actions for insider dealing alerts"""
        if severity == 'HIGH':
            return [
                "Immediate investigation required",
                "Freeze trader account pending review",
                "Review all recent trades and communications",
                "Notify compliance department",
                "Consider regulatory reporting"
            ]
        else:
            return [
                "Monitor trader activity closely",
                "Review trading patterns",
                "Check access to material information",
                "Document findings for compliance review"
            ]
    
    def _get_spoofing_actions(self, severity: str) -> List[str]:
        """Get recommended actions for spoofing alerts"""
        if severity == 'HIGH':
            return [
                "Immediate investigation of order patterns",
                "Review order book manipulation",
                "Analyze market impact",
                "Consider trade cancellation if ongoing",
                "Notify market surveillance team"
            ]
        else:
            return [
                "Monitor order patterns",
                "Review cancellation ratios",
                "Analyze trading behavior",
                "Document suspicious activity"
            ]
    
    def _get_overall_actions(self, severity: str) -> List[str]:
        """Get recommended actions for overall risk alerts"""
        if severity == 'CRITICAL':
            return [
                "Immediate escalation to senior management",
                "Comprehensive investigation across all activities",
                "Consider temporary trading restrictions",
                "Prepare regulatory notifications",
                "Engage external counsel if necessary"
            ]
        elif severity == 'HIGH':
            return [
                "Escalate to compliance team",
                "Detailed review of all trading activities",
                "Enhanced monitoring protocols",
                "Document all findings"
            ]
        else:
            return [
                "Continue monitoring",
                "Regular compliance review",
                "Document patterns for trend analysis"
            ]
    
    def get_historical_alerts(self, limit: int = 100, alert_type: Optional[str] = None) -> List[Dict]:
        """Get historical alerts with optional filtering"""
        filtered_alerts = self.alert_history
        
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a['type'] == alert_type.upper()]
        
        # Sort by timestamp (most recent first)
        filtered_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return filtered_alerts[:limit]
    
    def get_alert_summary(self, days: int = 30) -> Dict:
        """Get summary of alerts over specified period"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_alerts = [
            a for a in self.alert_history 
            if datetime.fromisoformat(a['timestamp']) > cutoff_date
        ]
        
        summary = {
            'total_alerts': len(recent_alerts),
            'by_type': {},
            'by_severity': {},
            'unique_traders': set(),
            'instruments_affected': set()
        }
        
        for alert in recent_alerts:
            # Count by type
            alert_type = alert['type']
            summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1
            
            # Count by severity
            severity = alert['severity']
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Track unique traders
            if alert.get('trader_id'):
                summary['unique_traders'].add(alert['trader_id'])
            
            # Track instruments
            for instrument in alert.get('instruments', []):
                summary['instruments_affected'].add(instrument)
        
        # Convert sets to lists for JSON serialization
        summary['unique_traders'] = list(summary['unique_traders'])
        summary['instruments_affected'] = list(summary['instruments_affected'])
        
        return summary
    
    def generate_regulatory_rationale(self, alert: Dict, risk_scores: Dict, 
                                    processed_data: Dict) -> RegulatoryRationale:
        """Generate regulatory rationale for an alert"""
        try:
            return self.regulatory_explainability.generate_regulatory_rationale(
                alert, risk_scores, processed_data
            )
        except Exception as e:
            logger.error(f"Error generating regulatory rationale: {str(e)}")
            raise
    
    def export_stor_report(self, alert: Dict, risk_scores: Dict, 
                          processed_data: Dict) -> STORRecord:
        """Export alert in STOR format"""
        try:
            rationale = self.generate_regulatory_rationale(alert, risk_scores, processed_data)
            return self.regulatory_explainability.export_stor_format(rationale, processed_data)
        except Exception as e:
            logger.error(f"Error exporting STOR report: {str(e)}")
            raise
    
    def export_regulatory_csv(self, alert: Dict, risk_scores: Dict, 
                             processed_data: Dict, filename: Optional[str] = None) -> str:
        """Export regulatory rationale as CSV report"""
        try:
            rationale = self.generate_regulatory_rationale(alert, risk_scores, processed_data)
            return self.regulatory_explainability.export_csv_report(rationale, filename)
        except Exception as e:
            logger.error(f"Error exporting regulatory CSV: {str(e)}")
            raise