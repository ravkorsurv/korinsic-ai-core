"""
ARERA Compliance Engine for Economic Withholding Detection.

This module implements ARERA (Italian Energy Regulatory Authority) specific
compliance logic and reporting for economic withholding detection in power markets.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class ARERAViolation:
    """Represents an ARERA compliance violation."""
    violation_type: str
    severity: str  # 'low', 'medium', 'high'
    description: str
    evidence: Dict[str, Any]
    statistical_significance: float
    economic_significance: float
    regulatory_reference: str
    timestamp: str


@dataclass
class ARERAComplianceReport:
    """ARERA compliance analysis report."""
    analysis_id: str
    plant_id: str
    analysis_period: Dict[str, str]
    methodology: str
    violations: List[ARERAViolation]
    statistical_summary: Dict[str, Any]
    regulatory_assessment: Dict[str, Any]
    recommendations: List[str]
    compliance_status: str  # 'compliant', 'non_compliant', 'requires_investigation'
    confidence_level: float
    generated_timestamp: str


class ARERAComplianceEngine:
    """
    ARERA compliance engine for economic withholding detection.
    
    Implements Italian regulatory methodology for detecting and reporting
    economic withholding violations in electricity markets.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ARERA compliance engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.confidence_threshold = self.config.get('confidence_threshold', 0.90)
        self.markup_threshold = self.config.get('markup_threshold', 0.15)
        self.statistical_significance = self.config.get('statistical_significance', 0.05)
        self.economic_significance = self.config.get('economic_significance', 0.10)
        
        # ARERA regulatory references
        self.regulatory_references = {
            'economic_withholding': 'ARERA Resolution 111/06 and subsequent amendments',
            'market_power_abuse': 'Legislative Decree 79/99, Article 6ter',
            'price_manipulation': 'REMIT Regulation (EU) No 1227/2011',
            'transparency_obligations': 'ARERA Resolution 351/12'
        }
        
        logger.info("ARERA compliance engine initialized")

    def assess_compliance(
        self,
        analysis_results: Dict[str, Any],
        plant_data: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> ARERAComplianceReport:
        """
        Assess ARERA compliance based on analysis results.
        
        Args:
            analysis_results: Economic withholding analysis results
            plant_data: Plant characteristics and data
            market_context: Market conditions and context
            
        Returns:
            ARERA compliance report
        """
        try:
            analysis_id = f"arera_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize compliance report
            report = ARERAComplianceReport(
                analysis_id=analysis_id,
                plant_id=plant_data.get('unit_id', 'unknown'),
                analysis_period={
                    'start': analysis_results.get('analysis_period', {}).get('start', ''),
                    'end': analysis_results.get('analysis_period', {}).get('end', '')
                },
                methodology='arera_counterfactual_simulation',
                violations=[],
                statistical_summary={},
                regulatory_assessment={},
                recommendations=[],
                compliance_status='compliant',
                confidence_level=0.0,
                generated_timestamp=datetime.utcnow().isoformat()
            )
            
            # Assess different violation types
            violations = []
            
            # 1. Economic withholding assessment
            economic_violations = self._assess_economic_withholding(
                analysis_results, plant_data, market_context
            )
            violations.extend(economic_violations)
            
            # 2. Market power abuse assessment
            market_power_violations = self._assess_market_power_abuse(
                analysis_results, plant_data, market_context
            )
            violations.extend(market_power_violations)
            
            # 3. Price manipulation assessment
            price_manipulation_violations = self._assess_price_manipulation(
                analysis_results, plant_data, market_context
            )
            violations.extend(price_manipulation_violations)
            
            # 4. Transparency violations assessment
            transparency_violations = self._assess_transparency_violations(
                analysis_results, plant_data, market_context
            )
            violations.extend(transparency_violations)
            
            report.violations = violations
            
            # Generate statistical summary
            report.statistical_summary = self._generate_statistical_summary(
                analysis_results, violations
            )
            
            # Generate regulatory assessment
            report.regulatory_assessment = self._generate_regulatory_assessment(
                violations, analysis_results
            )
            
            # Generate recommendations
            report.recommendations = self._generate_recommendations(violations)
            
            # Determine overall compliance status
            report.compliance_status = self._determine_compliance_status(violations)
            
            # Calculate confidence level
            report.confidence_level = self._calculate_confidence_level(
                analysis_results, violations
            )
            
            logger.info(f"ARERA compliance assessment completed: {report.compliance_status}")
            return report
            
        except Exception as e:
            logger.error(f"Error in ARERA compliance assessment: {str(e)}")
            # Return error report
            return ARERAComplianceReport(
                analysis_id=f"error_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                plant_id=plant_data.get('unit_id', 'unknown'),
                analysis_period={'start': '', 'end': ''},
                methodology='arera_counterfactual_simulation',
                violations=[],
                statistical_summary={'error': str(e)},
                regulatory_assessment={},
                recommendations=[],
                compliance_status='analysis_error',
                confidence_level=0.0,
                generated_timestamp=datetime.utcnow().isoformat()
            )

    def _assess_economic_withholding(
        self,
        analysis_results: Dict[str, Any],
        plant_data: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> List[ARERAViolation]:
        """
        Assess economic withholding violations using ARERA criteria.
        
        Args:
            analysis_results: Analysis results
            plant_data: Plant data
            market_context: Market context
            
        Returns:
            List of economic withholding violations
        """
        violations = []
        
        try:
            # Extract relevant data
            counterfactual_results = analysis_results.get('counterfactual_analysis', {})
            statistical_analysis = analysis_results.get('statistical_analysis', {})
            risk_indicators = analysis_results.get('risk_indicators', {})
            
            # Check for excessive markup (ARERA criterion)
            markup_violations = self._check_markup_violations(
                counterfactual_results, statistical_analysis
            )
            violations.extend(markup_violations)
            
            # Check for systematic withholding patterns
            pattern_violations = self._check_systematic_patterns(
                analysis_results, plant_data
            )
            violations.extend(pattern_violations)
            
            # Check for capacity withholding
            capacity_violations = self._check_capacity_withholding(
                analysis_results, plant_data, market_context
            )
            violations.extend(capacity_violations)
            
        except Exception as e:
            logger.warning(f"Error assessing economic withholding: {str(e)}")
        
        return violations

    def _check_markup_violations(
        self,
        counterfactual_results: Dict[str, Any],
        statistical_analysis: Dict[str, Any]
    ) -> List[ARERAViolation]:
        """Check for excessive markup violations."""
        violations = []
        
        try:
            comparisons = counterfactual_results.get('comparisons', [])
            
            for comparison in comparisons:
                avg_markup = comparison.get('average_markup', 0.0)
                max_markup = comparison.get('max_markup', 0.0)
                scenario = comparison.get('benchmark_scenario', 'unknown')
                
                # ARERA threshold: 15% average markup
                if avg_markup > self.markup_threshold:
                    # Check statistical significance
                    hypothesis_tests = statistical_analysis.get('hypothesis_test_results', {})
                    t_test = hypothesis_tests.get('t_test_vs_zero', {})
                    p_value = t_test.get('p_value', 1.0)
                    
                    if p_value < self.statistical_significance:
                        severity = 'high' if avg_markup > 0.25 else 'medium'
                        
                        violation = ARERAViolation(
                            violation_type='ECONOMIC_WITHHOLDING_EXCESSIVE_MARKUP',
                            severity=severity,
                            description=f"Average markup of {avg_markup:.1%} exceeds ARERA threshold of {self.markup_threshold:.1%} for scenario {scenario}",
                            evidence={
                                'average_markup': avg_markup,
                                'max_markup': max_markup,
                                'benchmark_scenario': scenario,
                                'statistical_significance': p_value,
                                'threshold_exceeded': avg_markup - self.markup_threshold
                            },
                            statistical_significance=1.0 - p_value,
                            economic_significance=avg_markup,
                            regulatory_reference=self.regulatory_references['economic_withholding'],
                            timestamp=datetime.utcnow().isoformat()
                        )
                        violations.append(violation)
                
                # Check for extreme markup cases
                if max_markup > 0.30:  # 30% maximum markup threshold
                    violation = ARERAViolation(
                        violation_type='ECONOMIC_WITHHOLDING_EXTREME_MARKUP',
                        severity='high',
                        description=f"Maximum markup of {max_markup:.1%} indicates severe economic withholding",
                        evidence={
                            'max_markup': max_markup,
                            'benchmark_scenario': scenario,
                            'extreme_threshold': 0.30
                        },
                        statistical_significance=0.99,  # High confidence for extreme cases
                        economic_significance=max_markup,
                        regulatory_reference=self.regulatory_references['economic_withholding'],
                        timestamp=datetime.utcnow().isoformat()
                    )
                    violations.append(violation)
                    
        except Exception as e:
            logger.warning(f"Error checking markup violations: {str(e)}")
        
        return violations

    def _check_systematic_patterns(
        self,
        analysis_results: Dict[str, Any],
        plant_data: Dict[str, Any]
    ) -> List[ARERAViolation]:
        """Check for systematic withholding patterns."""
        violations = []
        
        try:
            cost_curve_analysis = analysis_results.get('cost_curve_analysis', {})
            relationships = cost_curve_analysis.get('relationships', {})
            
            # Check for quantity-dependent markup (systematic pattern)
            linear_rel = relationships.get('linear', {})
            if linear_rel.get('significant_at_05', False):
                slope = linear_rel.get('slope', 0.0)
                r_squared = linear_rel.get('r_squared', 0.0)
                
                if slope > 0.001 and r_squared > 0.3:  # Positive relationship with quantity
                    violation = ARERAViolation(
                        violation_type='ECONOMIC_WITHHOLDING_SYSTEMATIC_PATTERN',
                        severity='medium',
                        description=f"Systematic increase in markup with quantity (slope: {slope:.4f}, R²: {r_squared:.3f})",
                        evidence={
                            'slope': slope,
                            'r_squared': r_squared,
                            'p_value': linear_rel.get('p_value', 1.0),
                            'relationship_type': 'quantity_dependent_markup'
                        },
                        statistical_significance=1.0 - linear_rel.get('p_value', 1.0),
                        economic_significance=slope * plant_data.get('capacity_mw', 100),
                        regulatory_reference=self.regulatory_references['economic_withholding'],
                        timestamp=datetime.utcnow().isoformat()
                    )
                    violations.append(violation)
            
            # Check for bid shape anomalies
            bid_shape_analysis = analysis_results.get('bid_shape_analysis', {})
            anomaly_flags = bid_shape_analysis.get('anomaly_flags', [])
            anomaly_score = bid_shape_analysis.get('anomaly_score', 0.0)
            
            if anomaly_score > 0.6:  # High anomaly score
                violation = ARERAViolation(
                    violation_type='ECONOMIC_WITHHOLDING_BID_SHAPE_ANOMALY',
                    severity='medium' if anomaly_score < 0.8 else 'high',
                    description=f"Anomalous bid shape patterns detected (score: {anomaly_score:.2f})",
                    evidence={
                        'anomaly_score': anomaly_score,
                        'anomaly_flags': anomaly_flags,
                        'curve_characteristics': bid_shape_analysis.get('shape_characteristics', {})
                    },
                    statistical_significance=anomaly_score,
                    economic_significance=anomaly_score * 0.1,  # Estimated impact
                    regulatory_reference=self.regulatory_references['price_manipulation'],
                    timestamp=datetime.utcnow().isoformat()
                )
                violations.append(violation)
                
        except Exception as e:
            logger.warning(f"Error checking systematic patterns: {str(e)}")
        
        return violations

    def _check_capacity_withholding(
        self,
        analysis_results: Dict[str, Any],
        plant_data: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> List[ARERAViolation]:
        """Check for physical capacity withholding."""
        violations = []
        
        try:
            capacity_analysis = analysis_results.get('capacity_analysis', {})
            declared_capacity = plant_data.get('capacity_mw', 0)
            
            # Check capacity utilization patterns
            utilization_data = capacity_analysis.get('utilization_patterns', {})
            avg_utilization = utilization_data.get('average_utilization', 1.0)
            
            # Check for systematic under-utilization during high-price periods
            high_price_utilization = utilization_data.get('high_price_periods', {}).get('avg_utilization', 1.0)
            normal_price_utilization = utilization_data.get('normal_price_periods', {}).get('avg_utilization', 1.0)
            
            if high_price_utilization < normal_price_utilization * 0.8:  # 20% lower utilization during high prices
                utilization_difference = normal_price_utilization - high_price_utilization
                
                violation = ARERAViolation(
                    violation_type='ECONOMIC_WITHHOLDING_CAPACITY_WITHHOLDING',
                    severity='high',
                    description=f"Systematic capacity withholding during high-price periods (utilization difference: {utilization_difference:.1%})",
                    evidence={
                        'high_price_utilization': high_price_utilization,
                        'normal_price_utilization': normal_price_utilization,
                        'utilization_difference': utilization_difference,
                        'declared_capacity_mw': declared_capacity
                    },
                    statistical_significance=0.95,  # High confidence for clear patterns
                    economic_significance=utilization_difference * declared_capacity,
                    regulatory_reference=self.regulatory_references['economic_withholding'],
                    timestamp=datetime.utcnow().isoformat()
                )
                violations.append(violation)
            
            # Check for unreported capacity constraints
            technical_availability = plant_data.get('technical_availability', 1.0)
            if avg_utilization < technical_availability * 0.7:  # Significant under-utilization
                violation = ARERAViolation(
                    violation_type='ECONOMIC_WITHHOLDING_UNREPORTED_CONSTRAINTS',
                    severity='medium',
                    description=f"Capacity utilization ({avg_utilization:.1%}) significantly below technical availability ({technical_availability:.1%})",
                    evidence={
                        'average_utilization': avg_utilization,
                        'technical_availability': technical_availability,
                        'utilization_gap': technical_availability - avg_utilization
                    },
                    statistical_significance=0.80,
                    economic_significance=(technical_availability - avg_utilization) * declared_capacity,
                    regulatory_reference=self.regulatory_references['transparency_obligations'],
                    timestamp=datetime.utcnow().isoformat()
                )
                violations.append(violation)
                
        except Exception as e:
            logger.warning(f"Error checking capacity withholding: {str(e)}")
        
        return violations

    def _assess_market_power_abuse(
        self,
        analysis_results: Dict[str, Any],
        plant_data: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> List[ARERAViolation]:
        """Assess market power abuse violations."""
        violations = []
        
        try:
            market_share = market_context.get('market_share', 0.0)
            market_concentration = market_context.get('hhi_index', 0.0)
            
            # Check for dominant position abuse
            if market_share > 0.30 and market_concentration > 2500:  # High concentration market
                price_impact = analysis_results.get('price_impact_analysis', {}).get('estimated_impact', 0.0)
                
                if price_impact > self.economic_significance:
                    violation = ARERAViolation(
                        violation_type='MARKET_POWER_ABUSE_DOMINANT_POSITION',
                        severity='high',
                        description=f"Abuse of dominant market position (market share: {market_share:.1%}, price impact: {price_impact:.1%})",
                        evidence={
                            'market_share': market_share,
                            'hhi_index': market_concentration,
                            'price_impact': price_impact,
                            'economic_significance_threshold': self.economic_significance
                        },
                        statistical_significance=0.90,
                        economic_significance=price_impact,
                        regulatory_reference=self.regulatory_references['market_power_abuse'],
                        timestamp=datetime.utcnow().isoformat()
                    )
                    violations.append(violation)
                    
        except Exception as e:
            logger.warning(f"Error assessing market power abuse: {str(e)}")
        
        return violations

    def _assess_price_manipulation(
        self,
        analysis_results: Dict[str, Any],
        plant_data: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> List[ARERAViolation]:
        """Assess price manipulation violations."""
        violations = []
        
        try:
            # Check for coordinated behavior across plants
            coordination_analysis = analysis_results.get('coordination_analysis', {})
            coordination_score = coordination_analysis.get('coordination_score', 0.0)
            
            if coordination_score > 0.7:  # High coordination score
                violation = ARERAViolation(
                    violation_type='PRICE_MANIPULATION_COORDINATED_BEHAVIOR',
                    severity='high',
                    description=f"Evidence of coordinated pricing behavior (coordination score: {coordination_score:.2f})",
                    evidence={
                        'coordination_score': coordination_score,
                        'coordination_indicators': coordination_analysis.get('indicators', []),
                        'related_plants': coordination_analysis.get('related_plants', [])
                    },
                    statistical_significance=coordination_score,
                    economic_significance=coordination_score * 0.05,  # Estimated price impact
                    regulatory_reference=self.regulatory_references['price_manipulation'],
                    timestamp=datetime.utcnow().isoformat()
                )
                violations.append(violation)
                
        except Exception as e:
            logger.warning(f"Error assessing price manipulation: {str(e)}")
        
        return violations

    def _assess_transparency_violations(
        self,
        analysis_results: Dict[str, Any],
        plant_data: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> List[ARERAViolation]:
        """Assess transparency and reporting violations."""
        violations = []
        
        try:
            # Check for cost declaration inconsistencies
            cost_analysis = analysis_results.get('cost_analysis', {})
            anomalies = cost_analysis.get('anomaly_detection', {})
            anomaly_score = anomalies.get('overall_anomaly_score', 0.0)
            
            if anomaly_score > 0.5:  # Significant cost declaration anomalies
                violation = ARERAViolation(
                    violation_type='TRANSPARENCY_VIOLATION_COST_DECLARATION',
                    severity='medium',
                    description=f"Inconsistencies in cost declarations (anomaly score: {anomaly_score:.2f})",
                    evidence={
                        'anomaly_score': anomaly_score,
                        'fuel_cost_anomalies': anomalies.get('fuel_cost_anomalies', []),
                        'efficiency_anomalies': anomalies.get('efficiency_anomalies', []),
                        'vom_cost_anomalies': anomalies.get('vom_cost_anomalies', [])
                    },
                    statistical_significance=anomaly_score,
                    economic_significance=anomaly_score * 0.02,  # Estimated impact
                    regulatory_reference=self.regulatory_references['transparency_obligations'],
                    timestamp=datetime.utcnow().isoformat()
                )
                violations.append(violation)
                
        except Exception as e:
            logger.warning(f"Error assessing transparency violations: {str(e)}")
        
        return violations

    def _generate_statistical_summary(
        self,
        analysis_results: Dict[str, Any],
        violations: List[ARERAViolation]
    ) -> Dict[str, Any]:
        """Generate statistical summary for the compliance report."""
        try:
            summary = {
                'total_violations': len(violations),
                'violation_breakdown': {
                    'high_severity': len([v for v in violations if v.severity == 'high']),
                    'medium_severity': len([v for v in violations if v.severity == 'medium']),
                    'low_severity': len([v for v in violations if v.severity == 'low'])
                },
                'violation_types': {},
                'statistical_confidence': {
                    'high_confidence': len([v for v in violations if v.statistical_significance > 0.95]),
                    'medium_confidence': len([v for v in violations if 0.80 <= v.statistical_significance <= 0.95]),
                    'low_confidence': len([v for v in violations if v.statistical_significance < 0.80])
                },
                'economic_impact': {
                    'total_estimated_impact': sum(v.economic_significance for v in violations),
                    'max_single_impact': max([v.economic_significance for v in violations], default=0.0),
                    'avg_impact': np.mean([v.economic_significance for v in violations]) if violations else 0.0
                }
            }
            
            # Count violation types
            for violation in violations:
                violation_type = violation.violation_type
                if violation_type not in summary['violation_types']:
                    summary['violation_types'][violation_type] = 0
                summary['violation_types'][violation_type] += 1
            
            # Add analysis quality metrics
            statistical_analysis = analysis_results.get('statistical_analysis', {})
            summary['analysis_quality'] = {
                'confidence_intervals_available': bool(statistical_analysis.get('confidence_intervals')),
                'hypothesis_tests_performed': len(statistical_analysis.get('tests_performed', [])),
                'sample_size': analysis_results.get('sample_size', 0)
            }
            
            return summary
            
        except Exception as e:
            logger.warning(f"Error generating statistical summary: {str(e)}")
            return {'error': str(e)}

    def _generate_regulatory_assessment(
        self,
        violations: List[ARERAViolation],
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate regulatory assessment."""
        try:
            assessment = {
                'overall_risk_level': 'low',
                'regulatory_concerns': [],
                'enforcement_likelihood': 'low',
                'precedent_cases': [],
                'legal_implications': [],
                'mitigation_urgency': 'low'
            }
            
            # Determine overall risk level
            high_severity_count = len([v for v in violations if v.severity == 'high'])
            medium_severity_count = len([v for v in violations if v.severity == 'medium'])
            
            if high_severity_count > 0:
                assessment['overall_risk_level'] = 'high'
                assessment['enforcement_likelihood'] = 'high'
                assessment['mitigation_urgency'] = 'immediate'
            elif medium_severity_count > 2:
                assessment['overall_risk_level'] = 'medium'
                assessment['enforcement_likelihood'] = 'medium'
                assessment['mitigation_urgency'] = 'short_term'
            elif len(violations) > 0:
                assessment['overall_risk_level'] = 'low'
                assessment['enforcement_likelihood'] = 'low'
                assessment['mitigation_urgency'] = 'long_term'
            
            # Generate regulatory concerns
            violation_types = set(v.violation_type for v in violations)
            for violation_type in violation_types:
                if 'ECONOMIC_WITHHOLDING' in violation_type:
                    assessment['regulatory_concerns'].append(
                        'Economic withholding violations may result in administrative sanctions and financial penalties'
                    )
                elif 'MARKET_POWER_ABUSE' in violation_type:
                    assessment['regulatory_concerns'].append(
                        'Market power abuse may trigger structural remedies and ongoing monitoring'
                    )
                elif 'PRICE_MANIPULATION' in violation_type:
                    assessment['regulatory_concerns'].append(
                        'Price manipulation may result in criminal prosecution under REMIT regulations'
                    )
            
            # Add legal implications
            if high_severity_count > 0:
                assessment['legal_implications'].extend([
                    'Potential administrative sanctions under ARERA Resolution 111/06',
                    'Financial penalties up to 3% of annual turnover',
                    'Mandatory compliance monitoring for 24 months'
                ])
            
            return assessment
            
        except Exception as e:
            logger.warning(f"Error generating regulatory assessment: {str(e)}")
            return {'error': str(e)}

    def _generate_recommendations(self, violations: List[ARERAViolation]) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        try:
            if not violations:
                recommendations.append("Continue current compliance practices and regular monitoring")
                return recommendations
            
            violation_types = set(v.violation_type for v in violations)
            
            # Economic withholding recommendations
            if any('ECONOMIC_WITHHOLDING' in vt for vt in violation_types):
                recommendations.extend([
                    "Review and adjust bidding strategies to ensure cost-reflective offers",
                    "Implement enhanced cost calculation and validation procedures",
                    "Establish regular benchmarking against market conditions",
                    "Consider voluntary compliance program with ARERA"
                ])
            
            # Market power recommendations
            if any('MARKET_POWER_ABUSE' in vt for vt in violation_types):
                recommendations.extend([
                    "Assess market position and consider voluntary capacity divestiture",
                    "Implement market power mitigation measures",
                    "Enhance transparency in capacity availability reporting"
                ])
            
            # Price manipulation recommendations
            if any('PRICE_MANIPULATION' in vt for vt in violation_types):
                recommendations.extend([
                    "Review internal trading procedures and controls",
                    "Implement enhanced surveillance and monitoring systems",
                    "Provide additional training on REMIT compliance requirements"
                ])
            
            # Transparency recommendations
            if any('TRANSPARENCY_VIOLATION' in vt for vt in violation_types):
                recommendations.extend([
                    "Enhance cost data collection and validation procedures",
                    "Implement regular audits of cost declarations",
                    "Improve documentation and record-keeping practices"
                ])
            
            # General recommendations for high-risk cases
            high_severity_violations = [v for v in violations if v.severity == 'high']
            if high_severity_violations:
                recommendations.extend([
                    "Engage external legal counsel for regulatory compliance review",
                    "Consider proactive engagement with ARERA to discuss findings",
                    "Implement immediate corrective measures to address identified violations"
                ])
            
        except Exception as e:
            logger.warning(f"Error generating recommendations: {str(e)}")
            recommendations.append("Consult with regulatory compliance experts for detailed guidance")
        
        return recommendations

    def _determine_compliance_status(self, violations: List[ARERAViolation]) -> str:
        """Determine overall compliance status."""
        if not violations:
            return 'compliant'
        
        high_severity_count = len([v for v in violations if v.severity == 'high'])
        medium_severity_count = len([v for v in violations if v.severity == 'medium'])
        
        if high_severity_count > 0:
            return 'non_compliant'
        elif medium_severity_count > 2:
            return 'requires_investigation'
        else:
            return 'requires_monitoring'

    def _calculate_confidence_level(
        self,
        analysis_results: Dict[str, Any],
        violations: List[ARERAViolation]
    ) -> float:
        """Calculate overall confidence level of the assessment."""
        try:
            if not violations:
                return 0.95  # High confidence in compliant assessment
            
            # Calculate weighted average of statistical significance
            total_weight = sum(v.economic_significance for v in violations)
            if total_weight == 0:
                return np.mean([v.statistical_significance for v in violations])
            
            weighted_confidence = sum(
                v.statistical_significance * v.economic_significance 
                for v in violations
            ) / total_weight
            
            return min(weighted_confidence, 0.99)  # Cap at 99%
            
        except Exception as e:
            logger.warning(f"Error calculating confidence level: {str(e)}")
            return 0.50  # Default moderate confidence

    def generate_arera_report_json(self, compliance_report: ARERAComplianceReport) -> str:
        """
        Generate ARERA compliance report in JSON format.
        
        Args:
            compliance_report: Compliance report object
            
        Returns:
            JSON string of the report
        """
        try:
            # Convert dataclass to dictionary
            report_dict = {
                'analysis_id': compliance_report.analysis_id,
                'plant_id': compliance_report.plant_id,
                'analysis_period': compliance_report.analysis_period,
                'methodology': compliance_report.methodology,
                'violations': [
                    {
                        'violation_type': v.violation_type,
                        'severity': v.severity,
                        'description': v.description,
                        'evidence': v.evidence,
                        'statistical_significance': v.statistical_significance,
                        'economic_significance': v.economic_significance,
                        'regulatory_reference': v.regulatory_reference,
                        'timestamp': v.timestamp
                    }
                    for v in compliance_report.violations
                ],
                'statistical_summary': compliance_report.statistical_summary,
                'regulatory_assessment': compliance_report.regulatory_assessment,
                'recommendations': compliance_report.recommendations,
                'compliance_status': compliance_report.compliance_status,
                'confidence_level': compliance_report.confidence_level,
                'generated_timestamp': compliance_report.generated_timestamp
            }
            
            return json.dumps(report_dict, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error generating ARERA report JSON: {str(e)}")
            return json.dumps({'error': str(e)}, indent=2)

    def export_arera_xml_report(self, compliance_report: ARERAComplianceReport) -> str:
        """
        Export ARERA compliance report in XML format for regulatory submission.
        
        Args:
            compliance_report: Compliance report object
            
        Returns:
            XML string of the report
        """
        try:
            # This would generate XML in ARERA's required format
            # For now, return a simplified XML structure
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<ARERAComplianceReport>
    <Header>
        <AnalysisId>{compliance_report.analysis_id}</AnalysisId>
        <PlantId>{compliance_report.plant_id}</PlantId>
        <Methodology>{compliance_report.methodology}</Methodology>
        <GeneratedTimestamp>{compliance_report.generated_timestamp}</GeneratedTimestamp>
        <ComplianceStatus>{compliance_report.compliance_status}</ComplianceStatus>
        <ConfidenceLevel>{compliance_report.confidence_level:.3f}</ConfidenceLevel>
    </Header>
    <AnalysisPeriod>
        <Start>{compliance_report.analysis_period['start']}</Start>
        <End>{compliance_report.analysis_period['end']}</End>
    </AnalysisPeriod>
    <Violations>
"""
            
            for violation in compliance_report.violations:
                xml_content += f"""        <Violation>
            <Type>{violation.violation_type}</Type>
            <Severity>{violation.severity}</Severity>
            <Description>{violation.description}</Description>
            <StatisticalSignificance>{violation.statistical_significance:.3f}</StatisticalSignificance>
            <EconomicSignificance>{violation.economic_significance:.3f}</EconomicSignificance>
            <RegulatoryReference>{violation.regulatory_reference}</RegulatoryReference>
            <Timestamp>{violation.timestamp}</Timestamp>
        </Violation>
"""
            
            xml_content += """    </Violations>
    <StatisticalSummary>
        <TotalViolations>{}</TotalViolations>
        <HighSeverityCount>{}</HighSeverityCount>
        <MediumSeverityCount>{}</MediumSeverityCount>
        <LowSeverityCount>{}</LowSeverityCount>
    </StatisticalSummary>
    <Recommendations>
""".format(
                compliance_report.statistical_summary.get('total_violations', 0),
                compliance_report.statistical_summary.get('violation_breakdown', {}).get('high_severity', 0),
                compliance_report.statistical_summary.get('violation_breakdown', {}).get('medium_severity', 0),
                compliance_report.statistical_summary.get('violation_breakdown', {}).get('low_severity', 0)
            )
            
            for recommendation in compliance_report.recommendations:
                xml_content += f"        <Recommendation>{recommendation}</Recommendation>\n"
            
            xml_content += """    </Recommendations>
</ARERAComplianceReport>"""
            
            return xml_content
            
        except Exception as e:
            logger.error(f"Error generating ARERA XML report: {str(e)}")
            return f"<Error>{str(e)}</Error>"