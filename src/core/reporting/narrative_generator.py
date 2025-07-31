"""
Narrative Generation Module for Regulatory Explainability System

This module provides modular, maintainable narrative generation for regulatory reports
by breaking down large templates into manageable sections.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ReportSection(Enum):
    """Report section types"""
    HEADER = "header"
    EXECUTIVE_SUMMARY = "executive_summary"
    EVIDENCE_ANALYSIS = "evidence_analysis"
    REGULATORY_CONCLUSIONS = "regulatory_conclusions"
    AUDIT_TRAIL = "audit_trail"

class NarrativeGenerator:
    """Generates regulatory narratives in modular sections"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[ReportSection, str]:
        """Load narrative templates for each section"""
        return {
            ReportSection.HEADER: """
REGULATORY EXPLAINABILITY REPORT
================================

Person Under Investigation: {person_name} (ID: {person_id})
Risk Typology: {risk_typology}
Alert Confidence: {detection_confidence:.1%}
STOR Eligible: {stor_eligible}
Generated: {generation_timestamp}
""".strip(),
            
            ReportSection.EXECUTIVE_SUMMARY: """
EXECUTIVE SUMMARY:
The surveillance system has detected a {detection_confidence:.1%} probability {risk_typology} pattern involving
{person_name}, a {employment} with {access_level} access. 
The evidence shows coordinated trading across {accounts_involved} linked accounts 
with total exposure of ${total_financial_exposure:,} initiated {timing_description}.
""".strip(),
            
            ReportSection.EVIDENCE_ANALYSIS: """
EVIDENCE CHAIN ANALYSIS:
========================

The following evidence items form a compelling chain of suspicious activity:
{evidence_items}
""".strip(),
            
            ReportSection.REGULATORY_CONCLUSIONS: """
REGULATORY CONCLUSIONS:
======================

{framework_name} Assessment:
{assessment_details}

Cross-Reference Analysis:
- Evidence items show strong interconnection ({cross_reference_count} cross-references)
- Temporal sequence supports deliberate planning hypothesis
- Multiple evidence types corroborate {risk_typology} theory
- Pattern sophistication suggests experienced trader with inside knowledge
""".strip(),
            
            ReportSection.AUDIT_TRAIL: """
AUDIT TRAIL:
============
- Total Evidence Items: {total_evidence_items}
- Evidence Time Span: {evidence_time_span_hours} hours
- Accounts Analyzed: {accounts_involved}
- Regulatory Frameworks: {regulatory_frameworks}
- Detection Algorithms: {detection_algorithms}
- Data Sources: {data_sources}

This evidence chain provides a comprehensive audit trail suitable for regulatory 
examination and demonstrates clear {risk_typology} patterns requiring immediate action.
""".strip()
        }
    
    def generate_regulatory_narrative(self, evidence_data: Dict[str, Any]) -> str:
        """
        Generate complete regulatory narrative from evidence data.
        
        Args:
            evidence_data: Complete evidence data structure
            
        Returns:
            Complete regulatory narrative
        """
        try:
            sections = [
                self.generate_report_header(evidence_data),
                self.generate_executive_summary(evidence_data),
                self.generate_evidence_analysis(evidence_data),
                self.generate_regulatory_conclusions(evidence_data),
                self.generate_audit_trail(evidence_data)
            ]
            
            return '\n\n'.join(filter(None, sections))
            
        except Exception as e:
            logger.error(f"Error generating regulatory narrative: {e}")
            return self._generate_error_narrative(evidence_data, str(e))
    
    def generate_report_header(self, evidence_data: Dict[str, Any]) -> str:
        """Generate report header section"""
        try:
            person = evidence_data.get("person_info", {})
            summary = evidence_data.get("scenario_summary", {})
            
            return self.templates[ReportSection.HEADER].format(
                person_name=person.get("person_name", "Unknown"),
                person_id=person.get("person_id", "Unknown"),
                risk_typology=summary.get("alert_type", "Unknown").replace("_", " ").title(),
                detection_confidence=summary.get("detection_confidence", 0.0),
                stor_eligible="Yes" if summary.get("stor_eligible", False) else "No",
                generation_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            )
        except Exception as e:
            logger.error(f"Error generating report header: {e}")
            return "REGULATORY EXPLAINABILITY REPORT\n================================\nError generating header"
    
    def generate_executive_summary(self, evidence_data: Dict[str, Any]) -> str:
        """Generate executive summary section"""
        try:
            person = evidence_data.get("person_info", {})
            summary = evidence_data.get("scenario_summary", {})
            
            # Generate timing description
            timing_description = self._generate_timing_description(evidence_data)
            
            return self.templates[ReportSection.EXECUTIVE_SUMMARY].format(
                detection_confidence=summary.get("detection_confidence", 0.0),
                risk_typology=summary.get("alert_type", "unknown").replace("_", " "),
                person_name=person.get("person_name", "Unknown"),
                employment=person.get("employment", "Unknown position"),
                access_level=person.get("access_level", "Unknown access"),
                accounts_involved=summary.get("accounts_involved", 0),
                total_financial_exposure=summary.get("total_financial_exposure", 0),
                timing_description=timing_description
            )
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return "EXECUTIVE SUMMARY: Error generating summary"
    
    def generate_evidence_analysis(self, evidence_data: Dict[str, Any]) -> str:
        """Generate evidence analysis section with optimized formatting"""
        try:
            chain = evidence_data.get("evidence_chain", [])
            
            # Use list comprehension for better performance
            evidence_items = [
                self._format_evidence_item(i + 1, evidence)
                for i, evidence in enumerate(chain)
            ]
            
            evidence_text = '\n\n'.join(evidence_items)
            
            return self.templates[ReportSection.EVIDENCE_ANALYSIS].format(
                evidence_items=evidence_text
            )
        except Exception as e:
            logger.error(f"Error generating evidence analysis: {e}")
            return "EVIDENCE CHAIN ANALYSIS: Error generating analysis"
    
    def generate_regulatory_conclusions(self, evidence_data: Dict[str, Any]) -> str:
        """Generate regulatory conclusions section"""
        try:
            summary = evidence_data.get("scenario_summary", {})
            chain = evidence_data.get("evidence_chain", [])
            
            # Count cross-references efficiently
            cross_reference_count = sum(
                len(item.get("cross_references", []))
                for item in chain
            )
            
            # Generate framework-specific assessment
            assessment_details = self._generate_framework_assessment(evidence_data)
            
            return self.templates[ReportSection.REGULATORY_CONCLUSIONS].format(
                framework_name=self._get_primary_framework(evidence_data),
                assessment_details=assessment_details,
                cross_reference_count=cross_reference_count,
                risk_typology=summary.get("alert_type", "unknown").replace("_", " ")
            )
        except Exception as e:
            logger.error(f"Error generating regulatory conclusions: {e}")
            return "REGULATORY CONCLUSIONS: Error generating conclusions"
    
    def generate_audit_trail(self, evidence_data: Dict[str, Any]) -> str:
        """Generate audit trail section"""
        try:
            summary = evidence_data.get("scenario_summary", {})
            
            return self.templates[ReportSection.AUDIT_TRAIL].format(
                total_evidence_items=summary.get("total_evidence_items", 0),
                evidence_time_span_hours=summary.get("evidence_time_span_hours", 0),
                accounts_involved=summary.get("accounts_involved", 0),
                regulatory_frameworks=", ".join(summary.get("regulatory_frameworks_triggered", [])),
                detection_algorithms="Bayesian Network, Temporal Analysis, Cross-Account Correlation",
                data_sources="Trading records, Communication logs, Market data, Corporate announcements",
                risk_typology=summary.get("alert_type", "unknown").replace("_", " ")
            )
        except Exception as e:
            logger.error(f"Error generating audit trail: {e}")
            return "AUDIT TRAIL: Error generating audit trail"
    
    def _format_evidence_item(self, sequence: int, evidence: Dict[str, Any]) -> str:
        """Format a single evidence item efficiently"""
        return f"""{sequence}. {evidence.get('evidence_type', 'UNKNOWN').replace('_', ' ').upper()} (Strength: {evidence.get('strength', 0.0):.2f})
   Time: {evidence.get('timestamp', 'Unknown')}
   Account: {evidence.get('account_id', 'Unknown')}
   Evidence: {evidence.get('description', 'No description')}
   Regulatory Significance: {self._get_regulatory_significance(evidence)}"""
    
    def _get_regulatory_significance(self, evidence: Dict[str, Any]) -> str:
        """Generate regulatory significance text for evidence item"""
        evidence_type = evidence.get('evidence_type', '')
        frameworks = evidence.get('regulatory_frameworks', [])
        
        significance_map = {
            'communication': 'Demonstrates potential access to material non-public information',
            'timing_anomaly': 'Highly suspicious timing suggests advance knowledge',
            'trading_pattern': 'Abnormal pattern indicates confidence in outcome',
            'cross_account_correlation': 'Coordination across accounts suggests deliberate strategy'
        }
        
        base_significance = significance_map.get(evidence_type, 'Requires regulatory attention')
        
        if 'mar_article_8' in frameworks:
            return f"{base_significance} (MAR Article 8 violation)"
        elif 'mar_article_12' in frameworks:
            return f"{base_significance} (MAR Article 12 violation)"
        else:
            return base_significance
    
    def _generate_timing_description(self, evidence_data: Dict[str, Any]) -> str:
        """Generate timing description for executive summary"""
        chain = evidence_data.get("evidence_chain", [])
        
        # Find timing-related evidence
        timing_evidence = [
            item for item in chain
            if item.get('evidence_type') == 'timing_anomaly'
        ]
        
        if timing_evidence:
            first_timing = timing_evidence[0]
            raw_data = first_timing.get('raw_data', {})
            hours_before = raw_data.get('hours_before_announcement', 0)
            
            if hours_before > 0:
                return f"exactly {hours_before} hours before a material announcement"
            else:
                return "with suspicious timing relative to market events"
        
        return "with coordinated timing across accounts"
    
    def _generate_framework_assessment(self, evidence_data: Dict[str, Any]) -> str:
        """Generate framework-specific assessment details"""
        summary = evidence_data.get("scenario_summary", {})
        
        # This would be expanded based on the specific regulatory framework
        assessment_lines = [
            f"- Information Access: CONFIRMED (employment position provides access)",
            f"- Trading Activity: HIGHLY SUSPICIOUS ({self._get_key_metric(evidence_data)})",
            f"- Timing Correlation: EXTREMELY SUSPICIOUS",
            f"- Financial Benefit: SIGNIFICANT (${summary.get('unrealized_gains', 0):,} unrealized gains)",
            f"- Recommendation: IMMEDIATE STOR FILING REQUIRED"
        ]
        
        return '\n'.join(assessment_lines)
    
    def _get_key_metric(self, evidence_data: Dict[str, Any]) -> str:
        """Extract key metric for assessment"""
        chain = evidence_data.get("evidence_chain", [])
        
        for item in chain:
            if item.get('evidence_type') == 'trading_pattern':
                raw_data = item.get('raw_data', {})
                increase = raw_data.get('position_increase_percentage', 0)
                if increase > 0:
                    return f"{increase}% position increase"
        
        return "abnormal trading patterns"
    
    def _get_primary_framework(self, evidence_data: Dict[str, Any]) -> str:
        """Get primary regulatory framework for the case"""
        summary = evidence_data.get("scenario_summary", {})
        frameworks = summary.get("regulatory_frameworks_triggered", [])
        
        if "MAR Article 8" in frameworks:
            return "MAR Article 8"
        elif "MAR Article 12" in frameworks:
            return "MAR Article 12"
        elif "STOR Requirements" in frameworks:
            return "STOR Requirements"
        else:
            return "Regulatory Framework"
    
    def _generate_error_narrative(self, evidence_data: Dict[str, Any], error_msg: str) -> str:
        """Generate error narrative when main generation fails"""
        return f"""
REGULATORY EXPLAINABILITY REPORT - ERROR
=======================================

An error occurred while generating the regulatory narrative.
Error: {error_msg}

Please contact the system administrator for assistance.
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
"""

# Performance-optimized output formatter
class OptimizedOutputFormatter:
    """Optimized formatter for evidence chain output"""
    
    @staticmethod
    def format_evidence_chain_output(evidence_data: Dict[str, Any]) -> str:
        """
        Format evidence chain output with optimized I/O operations.
        
        Args:
            evidence_data: Evidence data to format
            
        Returns:
            Formatted output string
        """
        try:
            # Build output in chunks for better performance
            output_chunks = []
            
            # Header section
            person = evidence_data.get("person_info", {})
            summary = evidence_data.get("scenario_summary", {})
            
            output_chunks.append("🔗 EVIDENCE CHAIN STRUCTURE:")
            output_chunks.append("-" * 35)
            
            # Evidence items - build all at once instead of multiple print calls
            chain = evidence_data.get("evidence_chain", [])
            evidence_lines = []
            
            for evidence in chain:
                sequence_id = evidence.get('sequence_id', 0)
                evidence_type = evidence.get('evidence_type', 'unknown').upper()
                timestamp = evidence.get('timestamp', 'Unknown')
                account_id = evidence.get('account_id', 'Unknown')
                strength = evidence.get('strength', 0.0)
                reliability = evidence.get('reliability', 0.0)
                description = evidence.get('description', 'No description')
                frameworks = evidence.get('regulatory_frameworks', [])
                cross_refs = evidence.get('cross_references', [])
                
                # Build evidence item as single string
                evidence_block = [
                    f"\n[{sequence_id}] {evidence_type}",
                    f"    Time: {timestamp}",
                    f"    Account: {account_id}",
                    f"    Strength: {strength:.2f} | Reliability: {reliability:.2f}",
                    f"    Description: {description}",
                    f"    Frameworks: {', '.join(frameworks)}"
                ]
                
                if cross_refs:
                    evidence_block.append(f"    Cross-refs: {', '.join(cross_refs)}")
                
                evidence_lines.append('\n'.join(evidence_block))
            
            # Join all evidence items
            output_chunks.append('\n'.join(evidence_lines))
            
            # Return complete output as single string
            return '\n'.join(output_chunks)
            
        except Exception as e:
            logger.error(f"Error formatting evidence chain output: {e}")
            return f"Error formatting output: {e}"