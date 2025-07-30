"""
Person-Centric Alert Generator

This module generates person-centric alerts that aggregate evidence across all
linked accounts and incorporate cross-typology signals for comprehensive
individual surveillance.

Features:
- PersonID-based alert generation
- Cross-account evidence aggregation
- Cross-typology signal integration
- Probabilistic risk scoring
- Enhanced regulatory explainability
- STOR-eligible alert identification
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from src.models.person_centric import (
    PersonCentricAlert,
    PersonRiskProfile,
    RiskTypology,
    AlertSeverity,
    CrossTypologySignal
)
from src.models.trading_data import RawTradeData
from .entity_resolution import EntityResolutionService
from .person_evidence_aggregator import PersonEvidenceAggregator
from .person_centric_nodes import PersonRiskNode
from .cross_typology_engine import CrossTypologyEngine
from .regulatory_explainability import RegulatoryExplainabilityEngine

logger = logging.getLogger(__name__)


class PersonCentricAlertGenerator:
    """
    Generates person-centric alerts with cross-account evidence and probabilistic scoring
    """
    
    def __init__(
        self,
        entity_resolution_service: EntityResolutionService,
        evidence_aggregator: PersonEvidenceAggregator,
        cross_typology_engine: CrossTypologyEngine,
        config: Optional[Dict[str, Any]] = None
    ):
        self.entity_resolution = entity_resolution_service
        self.evidence_aggregator = evidence_aggregator
        self.cross_typology_engine = cross_typology_engine
        self.config = config or {}
        
        # Initialize enhanced explainability engine
        self.explainability_engine = RegulatoryExplainabilityEngine(self.config)
        
        # Alert configuration
        self.alert_thresholds = {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.7,
            "critical": 0.85
        }
        
        self.probability_thresholds = {
            "minimum_alert": 0.4,
            "stor_eligible": 0.75,
            "immediate_escalation": 0.9
        }
        
        # Cross-typology escalation weights
        self.cross_typology_weights = {
            "multiple_typologies": 0.15,
            "high_correlation": 0.2,
            "systematic_pattern": 0.25
        }
        
        # Alert history for tracking
        self.alert_history: List[PersonCentricAlert] = []
        self.person_alert_counts: Dict[str, int] = {}
    
    def generate_person_alert(
        self,
        person_id: str,
        risk_typology: RiskTypology,
        person_profile: PersonRiskProfile,
        trade_data: List[RawTradeData],
        communication_data: Optional[List[Dict[str, Any]]] = None,
        news_events: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[PersonCentricAlert]:
        """
        Generate a person-centric alert for a specific risk typology
        
        Args:
            person_id: The person identifier
            risk_typology: The risk typology being assessed
            person_profile: The person's risk profile
            trade_data: Trading data across all linked accounts
            communication_data: Communication data across all channels
            news_events: Relevant news events for timing analysis
            
        Returns:
            PersonCentricAlert if alert criteria are met, None otherwise
        """
        logger.info(f"Generating person alert for {person_id}, typology {risk_typology.value}")
        
        try:
            # Calculate base risk probability
            base_risk_prob = self._calculate_base_risk_probability(
                person_id, risk_typology, person_profile, trade_data, communication_data, news_events
            )
            
            if base_risk_prob < self.probability_thresholds["minimum_alert"]:
                logger.debug(f"Risk probability {base_risk_prob:.3f} below minimum alert threshold")
                return None
            
            # Get cross-typology signals and adjustments
            cross_typology_summary = self.cross_typology_engine.get_person_cross_typology_summary(person_id)
            cross_typology_adjustment = self._calculate_cross_typology_adjustment(
                cross_typology_summary, risk_typology
            )
            
            # Calculate final probability with cross-typology influence
            final_probability = min(base_risk_prob + cross_typology_adjustment, 1.0)
            
            # Determine alert severity
            severity = self._determine_alert_severity(final_probability, cross_typology_summary)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                person_profile, cross_typology_summary, trade_data
            )
            
            # Aggregate evidence across accounts
            primary_evidence, supporting_evidence = self._aggregate_alert_evidence(
                person_id, risk_typology, person_profile, trade_data, communication_data
            )
            
            # Identify cross-account patterns
            cross_account_patterns = self._identify_cross_account_patterns(
                person_id, trade_data, communication_data
            )
            
            # Generate escalation factors
            escalation_factors = self._generate_escalation_factors(
                person_id, risk_typology, cross_typology_summary, final_probability
            )
            
            # Create regulatory rationale
            regulatory_rationale = self._create_regulatory_rationale(
                person_id, risk_typology, primary_evidence, cross_account_patterns
            )
            
            # Determine STOR eligibility
            stor_eligible = self._assess_stor_eligibility(
                final_probability, severity, risk_typology, escalation_factors
            )
            
            # Generate explanation summary
            explanation_summary = self._generate_explanation_summary(
                person_id, risk_typology, final_probability, primary_evidence, 
                cross_account_patterns, escalation_factors
            )
            
            # Create the alert
            alert = PersonCentricAlert(
                alert_id=f"person_alert_{uuid4().hex[:8]}",
                person_id=person_id,
                person_name=person_profile.primary_name,
                risk_typology=risk_typology,
                severity=severity,
                probability_score=final_probability,
                confidence_score=confidence_score,
                involved_accounts=list(person_profile.linked_accounts),
                involved_desks=list(person_profile.linked_desks),
                account_count=len(person_profile.linked_accounts),
                desk_count=len(person_profile.linked_desks),
                primary_evidence=primary_evidence,
                supporting_evidence=supporting_evidence,
                cross_account_patterns=cross_account_patterns,
                related_typologies=self._extract_related_typologies(cross_typology_summary),
                escalation_factors=escalation_factors,
                regulatory_rationale=regulatory_rationale,
                stor_eligible=stor_eligible,
                explanation_summary=explanation_summary,
                key_driver_nodes=self._identify_key_driver_nodes(primary_evidence),
                evidence_trail=self._create_evidence_trail(person_id, primary_evidence, supporting_evidence)
            )
            
            # Store alert in history
            self.alert_history.append(alert)
            self.person_alert_counts[person_id] = self.person_alert_counts.get(person_id, 0) + 1
            
            logger.info(f"Generated person alert {alert.alert_id} for {person_id}: {severity.value} severity, {final_probability:.3f} probability")
            return alert
            
        except Exception as e:
            logger.error(f"Error generating person alert for {person_id}: {str(e)}")
            return None
    
    def generate_enhanced_explanation(
        self,
        alert: PersonCentricAlert,
        person_profile: PersonRiskProfile,
        evidence_data: Dict[str, Any],
        cross_typology_signals: List[CrossTypologySignal]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive regulatory explanation for the alert
        """
        try:
            logger.info(f"Generating enhanced explanation for alert {alert.alert_id}")
            
            # Generate comprehensive regulatory explanation
            regulatory_explanation = self.explainability_engine.generate_comprehensive_explanation(
                alert=alert,
                person_profile=person_profile,
                evidence_data=evidence_data,
                cross_typology_signals=cross_typology_signals
            )
            
            # Convert to audit-ready format
            audit_report = regulatory_explanation.to_audit_report()
            
            # Add additional metadata
            enhanced_explanation = {
                "alert_id": alert.alert_id,
                "person_id": alert.person_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "explanation_version": "2.0",
                "regulatory_explanation": regulatory_explanation,
                "audit_report": audit_report,
                "explainability_metadata": {
                    "total_evidence_items": sum(
                        len(account_evidence.evidence_items) 
                        for account_evidence in regulatory_explanation.account_evidence.values()
                    ),
                    "cross_account_patterns": len(regulatory_explanation.cross_account_patterns),
                    "applicable_frameworks": list(regulatory_explanation.applicable_frameworks.keys()),
                    "stor_eligible": regulatory_explanation.stor_assessment.get("eligible", False),
                    "confidence_score": alert.confidence_score,
                    "explanation_completeness": self._assess_explanation_completeness(regulatory_explanation)
                }
            }
            
            logger.info(f"Enhanced explanation generated successfully for alert {alert.alert_id}")
            return enhanced_explanation
            
        except Exception as e:
            logger.error(f"Error generating enhanced explanation for alert {alert.alert_id}: {str(e)}")
            return {
                "alert_id": alert.alert_id,
                "error": f"Failed to generate enhanced explanation: {str(e)}",
                "fallback_explanation": self._generate_fallback_explanation(alert, evidence_data)
            }
    
    def _assess_explanation_completeness(self, regulatory_explanation) -> float:
        """Assess the completeness of the regulatory explanation"""
        completeness_factors = []
        
        # Evidence coverage
        if regulatory_explanation.account_evidence:
            completeness_factors.append(0.3)
        
        # Cross-account patterns identified
        if regulatory_explanation.cross_account_patterns:
            completeness_factors.append(0.2)
        
        # Temporal analysis available
        if regulatory_explanation.temporal_analysis and not regulatory_explanation.temporal_analysis.get("error"):
            completeness_factors.append(0.2)
        
        # Regulatory frameworks mapped
        if regulatory_explanation.applicable_frameworks:
            completeness_factors.append(0.15)
        
        # STOR assessment completed
        if regulatory_explanation.stor_assessment:
            completeness_factors.append(0.1)
        
        # Model interpretability provided
        if regulatory_explanation.model_interpretability:
            completeness_factors.append(0.05)
        
        return sum(completeness_factors)
    
    def _generate_fallback_explanation(self, alert: PersonCentricAlert, evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a basic fallback explanation when comprehensive explanation fails"""
        return {
            "type": "fallback_explanation",
            "alert_summary": {
                "person_id": alert.person_id,
                "person_name": alert.person_name,
                "risk_typology": alert.risk_typology.value,
                "probability_score": alert.probability_score,
                "severity": alert.severity.value,
                "involved_accounts": alert.involved_accounts
            },
            "basic_rationale": f"Person {alert.person_name} flagged for {alert.risk_typology.value} with {alert.probability_score:.1%} probability based on cross-account analysis.",
            "evidence_summary": {
                "accounts_analyzed": len(alert.involved_accounts),
                "evidence_sources": list(evidence_data.keys()) if evidence_data else [],
                "recommendation": "Manual review required due to explanation generation failure"
            }
        }
    
    def _calculate_base_risk_probability(
        self,
        person_id: str,
        risk_typology: RiskTypology,
        person_profile: PersonRiskProfile,
        trade_data: List[RawTradeData],
        communication_data: Optional[List[Dict[str, Any]]],
        news_events: Optional[List[Dict[str, Any]]]
    ) -> float:
        """Calculate base risk probability without cross-typology influence"""
        
        # Get or create risk nodes for this person and typology
        from .person_centric_nodes import create_person_risk_nodes
        
        risk_node, evidence_nodes = create_person_risk_nodes(
            person_id, risk_typology, person_profile.identity_confidence
        )
        
        # Analyze trading patterns
        trades_by_account = self._group_trades_by_account(person_id, trade_data)
        if trades_by_account:
            evidence_nodes["trading_pattern"].analyze_trading_patterns(trades_by_account)
        
        # Analyze communications
        if communication_data:
            comms_by_channel = self._group_communications_by_channel(person_id, communication_data)
            if comms_by_channel:
                evidence_nodes["communication"].analyze_communications(comms_by_channel)
        
        # Analyze timing patterns
        evidence_nodes["timing"].analyze_timing_patterns(
            trades_by_account, 
            self._group_communications_by_channel(person_id, communication_data or []),
            news_events
        )
        
        # Analyze access patterns
        evidence_nodes["access"].analyze_access_patterns(person_profile)
        
        # Register with cross-typology engine
        self.cross_typology_engine.register_person_risk_node(person_id, risk_typology, risk_node)
        
        # Calculate risk probability
        risk_prob, _ = risk_node.calculate_risk_probability()
        return risk_prob
    
    def _group_trades_by_account(self, person_id: str, trade_data: List[RawTradeData]) -> Dict[str, List[RawTradeData]]:
        """Group trades by account for the person"""
        person_accounts = self.entity_resolution.identity_graph.get_person_accounts(person_id)
        
        trades_by_account = {}
        for trade in trade_data:
            if trade.trader_id in person_accounts:
                if trade.trader_id not in trades_by_account:
                    trades_by_account[trade.trader_id] = []
                trades_by_account[trade.trader_id].append(trade)
        
        return trades_by_account
    
    def _group_communications_by_channel(
        self, 
        person_id: str, 
        communication_data: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group communications by channel for the person"""
        person_identity = self.entity_resolution.get_all_persons().get(person_id)
        if not person_identity:
            return {}
        
        comms_by_channel = {}
        for comm in communication_data:
            # Check if communication involves this person
            if (comm.get("sender_email") in person_identity.linked_emails or
                comm.get("sender_handle") in person_identity.linked_comm_handles or
                comm.get("sender_id") in person_identity.linked_accounts):
                
                channel = comm.get("channel", "default")
                if channel not in comms_by_channel:
                    comms_by_channel[channel] = []
                comms_by_channel[channel].append(comm)
        
        return comms_by_channel
    
    def _calculate_cross_typology_adjustment(
        self, 
        cross_typology_summary: Dict[str, Any], 
        target_typology: RiskTypology
    ) -> float:
        """Calculate adjustment based on cross-typology signals"""
        
        if "error" in cross_typology_summary or not cross_typology_summary.get("active_signals"):
            return 0.0
        
        adjustment = 0.0
        active_signals = cross_typology_summary["active_signals"]
        
        # Find signals targeting this typology
        for signal_dict in active_signals:
            if signal_dict["target_typology"] == target_typology.value:
                adjustment += signal_dict["impact_on_prior"]
        
        # Add escalation factor adjustments
        escalation_factors = cross_typology_summary.get("escalation_factors", [])
        if len(escalation_factors) >= 2:
            adjustment += self.cross_typology_weights["multiple_typologies"]
        
        if any("strong" in factor.lower() for factor in escalation_factors):
            adjustment += self.cross_typology_weights["high_correlation"]
        
        if any("systematic" in factor.lower() for factor in escalation_factors):
            adjustment += self.cross_typology_weights["systematic_pattern"]
        
        return min(adjustment, 0.3)  # Cap at 30% adjustment
    
    def _determine_alert_severity(
        self, 
        probability: float, 
        cross_typology_summary: Dict[str, Any]
    ) -> AlertSeverity:
        """Determine alert severity based on probability and cross-typology factors"""
        
        base_severity = AlertSeverity.LOW
        
        if probability >= self.alert_thresholds["critical"]:
            base_severity = AlertSeverity.CRITICAL
        elif probability >= self.alert_thresholds["high"]:
            base_severity = AlertSeverity.HIGH
        elif probability >= self.alert_thresholds["medium"]:
            base_severity = AlertSeverity.MEDIUM
        
        # Escalate based on cross-typology factors
        escalation_factors = cross_typology_summary.get("escalation_factors", [])
        if len(escalation_factors) >= 3 and base_severity != AlertSeverity.CRITICAL:
            # Escalate by one level for multiple escalation factors
            if base_severity == AlertSeverity.HIGH:
                return AlertSeverity.CRITICAL
            elif base_severity == AlertSeverity.MEDIUM:
                return AlertSeverity.HIGH
            elif base_severity == AlertSeverity.LOW:
                return AlertSeverity.MEDIUM
        
        return base_severity
    
    def _calculate_confidence_score(
        self,
        person_profile: PersonRiskProfile,
        cross_typology_summary: Dict[str, Any],
        trade_data: List[RawTradeData]
    ) -> float:
        """Calculate confidence score for the alert"""
        
        # Base confidence from identity resolution
        base_confidence = person_profile.identity_confidence
        
        # Data volume factor
        data_volume_factor = min(len(trade_data) / 50, 1.0)  # Normalize to 50 trades
        
        # Cross-account factor
        cross_account_factor = min(len(person_profile.linked_accounts) / 5, 1.0)  # Normalize to 5 accounts
        
        # Cross-typology factor
        cross_typology_factor = 0.0
        if not cross_typology_summary.get("error"):
            active_signals = cross_typology_summary.get("active_signals", [])
            if active_signals:
                avg_signal_strength = sum(s["signal_strength"] for s in active_signals) / len(active_signals)
                cross_typology_factor = avg_signal_strength * 0.3
        
        # Combine factors
        confidence = (
            base_confidence * 0.4 +
            data_volume_factor * 0.3 +
            cross_account_factor * 0.2 +
            cross_typology_factor * 0.1
        )
        
        return min(confidence, 1.0)
    
    def _aggregate_alert_evidence(
        self,
        person_id: str,
        risk_typology: RiskTypology,
        person_profile: PersonRiskProfile,
        trade_data: List[RawTradeData],
        communication_data: Optional[List[Dict[str, Any]]]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Aggregate primary and supporting evidence for the alert"""
        
        # Get evidence aggregation
        aggregated_profile = self.evidence_aggregator.aggregate_person_evidence(
            person_id, trade_data, communication_data
        )
        
        primary_evidence = {
            "person_identity": {
                "person_id": person_id,
                "primary_name": person_profile.primary_name,
                "identity_confidence": person_profile.identity_confidence,
                "linked_accounts": list(person_profile.linked_accounts),
                "linked_desks": list(person_profile.linked_desks)
            },
            "risk_typology": risk_typology.value,
            "aggregated_patterns": aggregated_profile.aggregated_evidence
        }
        
        supporting_evidence = {
            "evidence_sources": aggregated_profile.evidence_sources,
            "cross_account_correlations": aggregated_profile.cross_risk_correlations,
            "data_quality": {
                "trade_count": len(trade_data),
                "communication_count": len(communication_data) if communication_data else 0,
                "time_span_hours": self._calculate_time_span(trade_data)
            }
        }
        
        return primary_evidence, supporting_evidence
    
    def _identify_cross_account_patterns(
        self,
        person_id: str,
        trade_data: List[RawTradeData],
        communication_data: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Identify patterns across multiple accounts"""
        
        patterns = []
        
        # Group data by account
        trades_by_account = self._group_trades_by_account(person_id, trade_data)
        
        if len(trades_by_account) > 1:
            # Timing synchronization pattern
            sync_pattern = self._analyze_timing_synchronization(trades_by_account)
            if sync_pattern["detected"]:
                patterns.append({
                    "type": "timing_synchronization",
                    "description": "Synchronized trading activity across multiple accounts",
                    "evidence": sync_pattern,
                    "risk_factor": 0.7
                })
            
            # Volume distribution pattern
            volume_pattern = self._analyze_volume_distribution(trades_by_account)
            if volume_pattern["suspicious"]:
                patterns.append({
                    "type": "volume_distribution",
                    "description": "Suspicious volume distribution across accounts",
                    "evidence": volume_pattern,
                    "risk_factor": 0.6
                })
            
            # Instrument correlation pattern
            instrument_pattern = self._analyze_instrument_correlation(trades_by_account)
            if instrument_pattern["high_correlation"]:
                patterns.append({
                    "type": "instrument_correlation",
                    "description": "High correlation in instrument selection across accounts",
                    "evidence": instrument_pattern,
                    "risk_factor": 0.5
                })
        
        return patterns
    
    def _analyze_timing_synchronization(self, trades_by_account: Dict[str, List[RawTradeData]]) -> Dict[str, Any]:
        """Analyze timing synchronization across accounts"""
        
        if len(trades_by_account) <= 1:
            return {"detected": False}
        
        # Simple synchronization detection
        all_trades = []
        for account_id, trades in trades_by_account.items():
            for trade in trades:
                all_trades.append((trade, account_id))
        
        # Sort by timestamp
        all_trades.sort(key=lambda x: x[0].execution_timestamp)
        
        sync_events = 0
        for i in range(len(all_trades) - 1):
            trade1, account1 = all_trades[i]
            trade2, account2 = all_trades[i + 1]
            
            if account1 != account2:  # Different accounts
                try:
                    time1 = datetime.fromisoformat(trade1.execution_timestamp.replace('Z', '+00:00'))
                    time2 = datetime.fromisoformat(trade2.execution_timestamp.replace('Z', '+00:00'))
                    
                    time_diff = abs((time2 - time1).total_seconds())
                    if time_diff <= 300:  # Within 5 minutes
                        sync_events += 1
                except:
                    continue
        
        return {
            "detected": sync_events >= 3,
            "sync_events": sync_events,
            "total_comparisons": len(all_trades) - 1,
            "sync_ratio": sync_events / (len(all_trades) - 1) if len(all_trades) > 1 else 0
        }
    
    def _analyze_volume_distribution(self, trades_by_account: Dict[str, List[RawTradeData]]) -> Dict[str, Any]:
        """Analyze volume distribution across accounts"""
        
        account_volumes = {}
        total_volume = 0
        
        for account_id, trades in trades_by_account.items():
            volume = sum(trade.quantity for trade in trades)
            account_volumes[account_id] = volume
            total_volume += volume
        
        if total_volume == 0:
            return {"suspicious": False}
        
        # Calculate volume distribution statistics
        volume_ratios = [v / total_volume for v in account_volumes.values()]
        max_ratio = max(volume_ratios)
        min_ratio = min(volume_ratios)
        
        # Suspicious if very uneven distribution or very even distribution (potential wash trading)
        suspicious = (max_ratio > 0.8) or (max_ratio - min_ratio < 0.1 and len(account_volumes) > 2)
        
        return {
            "suspicious": suspicious,
            "account_volumes": account_volumes,
            "volume_ratios": dict(zip(account_volumes.keys(), volume_ratios)),
            "max_ratio": max_ratio,
            "min_ratio": min_ratio,
            "distribution_evenness": max_ratio - min_ratio
        }
    
    def _analyze_instrument_correlation(self, trades_by_account: Dict[str, List[RawTradeData]]) -> Dict[str, Any]:
        """Analyze instrument correlation across accounts"""
        
        account_instruments = {}
        all_instruments = set()
        
        for account_id, trades in trades_by_account.items():
            instruments = set(trade.symbol for trade in trades)
            account_instruments[account_id] = instruments
            all_instruments.update(instruments)
        
        if len(all_instruments) == 0:
            return {"high_correlation": False}
        
        # Calculate pairwise correlations
        correlations = []
        accounts = list(account_instruments.keys())
        
        for i, account1 in enumerate(accounts):
            for account2 in accounts[i+1:]:
                instruments1 = account_instruments[account1]
                instruments2 = account_instruments[account2]
                
                if not instruments1 or not instruments2:
                    continue
                
                intersection = instruments1.intersection(instruments2)
                union = instruments1.union(instruments2)
                correlation = len(intersection) / len(union) if union else 0
                correlations.append(correlation)
        
        avg_correlation = sum(correlations) / len(correlations) if correlations else 0
        
        return {
            "high_correlation": avg_correlation > 0.7,
            "average_correlation": avg_correlation,
            "account_instruments": {k: list(v) for k, v in account_instruments.items()},
            "total_unique_instruments": len(all_instruments)
        }
    
    def _generate_escalation_factors(
        self,
        person_id: str,
        risk_typology: RiskTypology,
        cross_typology_summary: Dict[str, Any],
        probability: float
    ) -> List[str]:
        """Generate escalation factors for the alert"""
        
        escalation_factors = []
        
        # High probability
        if probability > self.probability_thresholds["immediate_escalation"]:
            escalation_factors.append("Extremely high risk probability (>90%)")
        
        # Cross-typology factors
        if not cross_typology_summary.get("error"):
            cross_factors = cross_typology_summary.get("escalation_factors", [])
            escalation_factors.extend(cross_factors)
        
        # Historical factors
        if self.person_alert_counts.get(person_id, 0) > 2:
            escalation_factors.append(f"Repeat offender ({self.person_alert_counts[person_id]} prior alerts)")
        
        # STOR eligibility
        if probability > self.probability_thresholds["stor_eligible"]:
            escalation_factors.append("STOR filing eligible")
        
        return escalation_factors
    
    def _create_regulatory_rationale(
        self,
        person_id: str,
        risk_typology: RiskTypology,
        primary_evidence: Dict[str, Any],
        cross_account_patterns: List[Dict[str, Any]]
    ) -> str:
        """Create regulatory rationale for the alert"""
        
        rationale_parts = []
        
        # Person identification
        person_name = primary_evidence["person_identity"]["primary_name"] or "Unknown"
        account_count = len(primary_evidence["person_identity"]["linked_accounts"])
        desk_count = len(primary_evidence["person_identity"]["linked_desks"])
        
        rationale_parts.append(
            f"Individual {person_name} (PersonID: {person_id}) exhibits suspicious {risk_typology.value} "
            f"patterns across {account_count} linked accounts and {desk_count} desks."
        )
        
        # Evidence summary
        aggregated_patterns = primary_evidence.get("aggregated_patterns", {})
        if aggregated_patterns:
            evidence_strengths = []
            for pattern_type, pattern_data in aggregated_patterns.items():
                if isinstance(pattern_data, dict) and pattern_data.get("strength", 0) > 0.5:
                    evidence_strengths.append(pattern_type.replace("_", " "))
            
            if evidence_strengths:
                rationale_parts.append(f"Strong evidence observed in: {', '.join(evidence_strengths)}.")
        
        # Cross-account patterns
        if cross_account_patterns:
            pattern_descriptions = [p["description"] for p in cross_account_patterns]
            rationale_parts.append(f"Cross-account patterns detected: {'; '.join(pattern_descriptions)}.")
        
        # Regulatory context
        if risk_typology == RiskTypology.INSIDER_DEALING:
            rationale_parts.append("Potential violation of insider dealing regulations (MAR Article 8).")
        elif risk_typology == RiskTypology.SPOOFING:
            rationale_parts.append("Potential market manipulation through spoofing (MAR Article 12).")
        elif risk_typology == RiskTypology.MARKET_MANIPULATION:
            rationale_parts.append("Potential market manipulation (MAR Article 12).")
        
        return " ".join(rationale_parts)
    
    def _assess_stor_eligibility(
        self,
        probability: float,
        severity: AlertSeverity,
        risk_typology: RiskTypology,
        escalation_factors: List[str]
    ) -> bool:
        """Assess if alert is eligible for STOR filing"""
        
        # High probability threshold
        if probability > self.probability_thresholds["stor_eligible"]:
            return True
        
        # Critical severity
        if severity == AlertSeverity.CRITICAL:
            return True
        
        # Multiple escalation factors
        if len(escalation_factors) >= 3:
            return True
        
        # Specific typologies with lower thresholds
        if risk_typology in [RiskTypology.INSIDER_DEALING, RiskTypology.MARKET_MANIPULATION]:
            if probability > 0.6 and severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                return True
        
        return False
    
    def _generate_explanation_summary(
        self,
        person_id: str,
        risk_typology: RiskTypology,
        probability: float,
        primary_evidence: Dict[str, Any],
        cross_account_patterns: List[Dict[str, Any]],
        escalation_factors: List[str]
    ) -> str:
        """Generate human-readable explanation summary"""
        
        person_name = primary_evidence["person_identity"]["primary_name"] or f"Person {person_id}"
        account_count = len(primary_evidence["person_identity"]["linked_accounts"])
        
        explanation = f"{person_name} shows {probability:.1%} likelihood of {risk_typology.value} "
        explanation += f"across {account_count} linked accounts. "
        
        # Key evidence
        key_evidence = []
        aggregated_patterns = primary_evidence.get("aggregated_patterns", {})
        for pattern_type, pattern_data in aggregated_patterns.items():
            if isinstance(pattern_data, dict) and pattern_data.get("strength", 0) > 0.6:
                key_evidence.append(pattern_type.replace("_", " "))
        
        if key_evidence:
            explanation += f"Key evidence: {', '.join(key_evidence)}. "
        
        # Cross-account activity
        if len(cross_account_patterns) > 0:
            explanation += f"Cross-account coordination detected in {len(cross_account_patterns)} patterns. "
        
        # Escalation factors
        if escalation_factors:
            explanation += f"Escalation factors: {len(escalation_factors)} identified."
        
        return explanation
    
    def _extract_related_typologies(self, cross_typology_summary: Dict[str, Any]) -> Dict[RiskTypology, float]:
        """Extract related typologies and their influence scores"""
        
        related = {}
        
        if cross_typology_summary.get("error"):
            return related
        
        risk_levels = cross_typology_summary.get("risk_levels", {})
        for typology_name, risk_data in risk_levels.items():
            try:
                typology = RiskTypology(typology_name)
                probability = risk_data.get("probability", 0.0)
                if probability > 0.3:  # Only include significant risks
                    related[typology] = probability
            except ValueError:
                continue
        
        return related
    
    def _identify_key_driver_nodes(self, primary_evidence: Dict[str, Any]) -> List[str]:
        """Identify key driver nodes for explainability"""
        
        key_drivers = []
        aggregated_patterns = primary_evidence.get("aggregated_patterns", {})
        
        for pattern_type, pattern_data in aggregated_patterns.items():
            if isinstance(pattern_data, dict) and pattern_data.get("strength", 0) > 0.5:
                key_drivers.append(f"{pattern_type}_node")
        
        return key_drivers
    
    def _create_evidence_trail(
        self,
        person_id: str,
        primary_evidence: Dict[str, Any],
        supporting_evidence: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create evidence trail for audit purposes"""
        
        trail = []
        
        # Identity resolution evidence
        trail.append({
            "step": "identity_resolution",
            "description": "Person identity resolved across multiple accounts",
            "evidence": primary_evidence["person_identity"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Pattern analysis evidence
        aggregated_patterns = primary_evidence.get("aggregated_patterns", {})
        for pattern_type, pattern_data in aggregated_patterns.items():
            if isinstance(pattern_data, dict) and pattern_data.get("strength", 0) > 0.3:
                trail.append({
                    "step": f"{pattern_type}_analysis",
                    "description": f"Analysis of {pattern_type.replace('_', ' ')} patterns",
                    "evidence": pattern_data,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        # Data sources evidence
        evidence_sources = supporting_evidence.get("evidence_sources", {})
        if evidence_sources:
            trail.append({
                "step": "data_aggregation",
                "description": "Data aggregated from multiple sources",
                "evidence": evidence_sources,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return trail
    
    def _calculate_time_span(self, trade_data: List[RawTradeData]) -> float:
        """Calculate time span of trade data in hours"""
        
        if not trade_data:
            return 0.0
        
        timestamps = []
        for trade in trade_data:
            try:
                dt = datetime.fromisoformat(trade.execution_timestamp.replace('Z', '+00:00'))
                timestamps.append(dt)
            except:
                continue
        
        if len(timestamps) < 2:
            return 0.0
        
        timestamps.sort()
        time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600  # Convert to hours
        return time_span
    
    def get_person_alert_history(self, person_id: str) -> List[PersonCentricAlert]:
        """Get alert history for a specific person"""
        return [alert for alert in self.alert_history if alert.person_id == person_id]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get overall alert statistics"""
        
        if not self.alert_history:
            return {"total_alerts": 0}
        
        # Count by severity
        severity_counts = {}
        for alert in self.alert_history:
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by typology
        typology_counts = {}
        for alert in self.alert_history:
            typology = alert.risk_typology.value
            typology_counts[typology] = typology_counts.get(typology, 0) + 1
        
        # STOR eligible count
        stor_count = sum(1 for alert in self.alert_history if alert.stor_eligible)
        
        return {
            "total_alerts": len(self.alert_history),
            "severity_distribution": severity_counts,
            "typology_distribution": typology_counts,
            "stor_eligible_count": stor_count,
            "unique_persons": len(set(alert.person_id for alert in self.alert_history)),
            "average_probability": sum(alert.probability_score for alert in self.alert_history) / len(self.alert_history),
            "average_confidence": sum(alert.confidence_score for alert in self.alert_history) / len(self.alert_history)
        }