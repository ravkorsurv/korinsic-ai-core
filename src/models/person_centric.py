"""
Person-Centric Data Models for Individual Surveillance

This module contains data models for aggregating trading, communication,
and risk data at the individual level to support person-centric surveillance.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .trading_data import RawTradeData, TradeDirection


class RiskTypology(Enum):
    """Risk typology enumeration for person-centric analysis"""
    
    INSIDER_DEALING = "insider_dealing"
    SPOOFING = "spoofing"
    WASH_TRADING = "wash_trading"
    FRONT_RUNNING = "front_running"
    MARKET_MANIPULATION = "market_manipulation"
    CROSS_DESK_COLLUSION = "cross_desk_collusion"


class AlertSeverity(Enum):
    """Alert severity levels for person-centric alerts"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PersonRiskProfile:
    """
    Comprehensive risk profile for an individual across all linked accounts
    """
    
    person_id: str
    primary_name: Optional[str] = None
    primary_role: Optional[str] = None
    
    # Identity resolution metadata
    linked_accounts: Set[str] = field(default_factory=set)
    linked_desks: Set[str] = field(default_factory=set)
    linked_emails: Set[str] = field(default_factory=set)
    identity_confidence: float = 0.0
    
    # Risk scores by typology
    risk_scores: Dict[RiskTypology, float] = field(default_factory=dict)
    risk_confidence: Dict[RiskTypology, float] = field(default_factory=dict)
    
    # Cross-typology influence scores
    typology_priors: Dict[RiskTypology, float] = field(default_factory=dict)
    cross_risk_correlations: Dict[str, float] = field(default_factory=dict)
    
    # Temporal risk evolution
    risk_history: List[Dict[str, Any]] = field(default_factory=list)
    risk_trend: Optional[str] = None  # "increasing", "decreasing", "stable"
    
    # Evidence aggregation
    aggregated_evidence: Dict[str, Any] = field(default_factory=dict)
    evidence_sources: Dict[str, List[str]] = field(default_factory=dict)
    
    # Metadata
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PersonActivitySummary:
    """
    Activity summary for a person across all linked accounts
    """
    
    person_id: str
    time_period_start: datetime
    time_period_end: datetime
    
    # Trading activity aggregation
    total_trades: int = 0
    total_volume: float = 0.0
    total_notional: float = 0.0
    unique_instruments: Set[str] = field(default_factory=set)
    unique_exchanges: Set[str] = field(default_factory=set)
    
    # Cross-account patterns
    cross_account_trades: int = 0
    cross_desk_trades: int = 0
    simultaneous_account_activity: int = 0
    
    # Communication patterns
    communication_volume: int = 0
    sensitive_communications: int = 0
    external_communications: int = 0
    
    # Risk indicators
    suspicious_timing_events: int = 0
    price_movement_correlations: int = 0
    volume_anomalies: int = 0
    
    # Performance metrics
    pnl_total: Optional[float] = None
    pnl_by_account: Dict[str, float] = field(default_factory=dict)
    hit_rate: Optional[float] = None


@dataclass
class PersonCentricAlert:
    """
    Person-centric alert with cross-account evidence and probabilistic scoring
    """
    
    alert_id: str
    person_id: str
    person_name: Optional[str] = None
    
    # Risk classification
    risk_typology: RiskTypology
    severity: AlertSeverity
    probability_score: float  # 0.0 to 1.0
    confidence_score: float  # 0.0 to 1.0
    
    # Cross-account context
    involved_accounts: List[str] = field(default_factory=list)
    involved_desks: List[str] = field(default_factory=list)
    account_count: int = 0
    desk_count: int = 0
    
    # Evidence aggregation
    primary_evidence: Dict[str, Any] = field(default_factory=dict)
    supporting_evidence: Dict[str, Any] = field(default_factory=dict)
    cross_account_patterns: List[Dict[str, Any]] = field(default_factory=list)
    
    # Temporal context
    detection_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    activity_period_start: Optional[datetime] = None
    activity_period_end: Optional[datetime] = None
    
    # Cross-typology context
    related_typologies: Dict[RiskTypology, float] = field(default_factory=dict)
    escalation_factors: List[str] = field(default_factory=list)
    
    # Regulatory context
    regulatory_rationale: str = ""
    stor_eligible: bool = False
    compliance_notes: List[str] = field(default_factory=list)
    
    # Explainability
    explanation_summary: str = ""
    key_driver_nodes: List[str] = field(default_factory=list)
    evidence_trail: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary for JSON serialization"""
        return {
            "alert_id": self.alert_id,
            "person_id": self.person_id,
            "person_name": self.person_name,
            "risk_typology": self.risk_typology.value,
            "severity": self.severity.value,
            "probability_score": self.probability_score,
            "confidence_score": self.confidence_score,
            "involved_accounts": self.involved_accounts,
            "involved_desks": self.involved_desks,
            "account_count": self.account_count,
            "desk_count": self.desk_count,
            "primary_evidence": self.primary_evidence,
            "supporting_evidence": self.supporting_evidence,
            "cross_account_patterns": self.cross_account_patterns,
            "detection_timestamp": self.detection_timestamp.isoformat(),
            "activity_period_start": self.activity_period_start.isoformat() if self.activity_period_start else None,
            "activity_period_end": self.activity_period_end.isoformat() if self.activity_period_end else None,
            "related_typologies": {k.value: v for k, v in self.related_typologies.items()},
            "escalation_factors": self.escalation_factors,
            "regulatory_rationale": self.regulatory_rationale,
            "stor_eligible": self.stor_eligible,
            "compliance_notes": self.compliance_notes,
            "explanation_summary": self.explanation_summary,
            "key_driver_nodes": self.key_driver_nodes,
            "evidence_trail": self.evidence_trail
        }


@dataclass
class PersonCentricEvidence:
    """
    Aggregated evidence for a person across all linked accounts and data sources
    """
    
    person_id: str
    evidence_type: str  # "trading_pattern", "communication", "timing", "access"
    
    # Source aggregation
    source_accounts: List[str] = field(default_factory=list)
    source_data_types: List[str] = field(default_factory=list)
    evidence_count: int = 0
    
    # Evidence strength
    strength_score: float = 0.0  # 0.0 to 1.0
    reliability_score: float = 0.0  # 0.0 to 1.0
    consistency_score: float = 0.0  # 0.0 to 1.0
    
    # Temporal patterns
    first_occurrence: Optional[datetime] = None
    last_occurrence: Optional[datetime] = None
    frequency_pattern: Optional[str] = None  # "increasing", "decreasing", "sporadic", "consistent"
    
    # Cross-account patterns
    cross_account_consistency: float = 0.0
    account_correlation_strength: float = 0.0
    
    # Evidence details
    evidence_data: Dict[str, Any] = field(default_factory=dict)
    supporting_data: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CrossTypologySignal:
    """
    Signal sharing between risk typologies at the person level
    """
    
    person_id: str
    source_typology: RiskTypology
    target_typology: RiskTypology
    
    # Signal strength and direction
    signal_strength: float  # 0.0 to 1.0
    signal_direction: str  # "positive", "negative", "neutral"
    
    # Evidence for signal
    shared_evidence: List[str] = field(default_factory=list)
    correlation_factors: Dict[str, float] = field(default_factory=dict)
    
    # Temporal aspects
    signal_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signal_duration: Optional[float] = None  # Duration in hours
    
    # Impact assessment
    impact_on_prior: float = 0.0  # How much this affects the target typology's prior
    confidence_adjustment: float = 0.0  # Confidence adjustment for target typology
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "person_id": self.person_id,
            "source_typology": self.source_typology.value,
            "target_typology": self.target_typology.value,
            "signal_strength": self.signal_strength,
            "signal_direction": self.signal_direction,
            "shared_evidence": self.shared_evidence,
            "correlation_factors": self.correlation_factors,
            "signal_timestamp": self.signal_timestamp.isoformat(),
            "signal_duration": self.signal_duration,
            "impact_on_prior": self.impact_on_prior,
            "confidence_adjustment": self.confidence_adjustment
        }