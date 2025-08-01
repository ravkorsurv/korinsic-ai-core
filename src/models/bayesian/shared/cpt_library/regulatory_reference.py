"""
Regulatory Reference System for CPT Library
This module provides regulatory compliance and enforcement case references
for all CPT definitions, ensuring traceability and regulatory justification
for probability table settings.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4


# Regulatory compliance threshold constants
class ComplianceThresholds:
    """Standard compliance thresholds for regulatory frameworks."""
    MAR_ARTICLE_8_THRESHOLD = 0.7  # Insider dealing detection threshold
    MAR_ARTICLE_12_THRESHOLD = 0.75  # Market manipulation detection threshold
    HIGH_RISK_THRESHOLD = 0.8  # High risk probability threshold
    MEDIUM_RISK_THRESHOLD = 0.6  # Medium risk probability threshold


class RegulatoryFramework(Enum):
    """Supported regulatory frameworks."""
    MAR_ARTICLE_8 = "MAR Article 8 - Insider Dealing"
    MAR_ARTICLE_12 = "MAR Article 12 - Market Manipulation"
    MIFID_II_ARTICLE_17 = "MiFID II Article 17 - Communication Recording"
    STOR_REQUIREMENTS = "STOR - Suspicious Transaction Reporting"
    FCA_MAR_GUIDANCE = "FCA MAR Guidance"
    ESMA_GUIDELINES = "ESMA Guidelines"
    CFTC_REGULATIONS = "CFTC Anti-Manipulation Rules"
    SEC_RULE_10B5 = "SEC Rule 10b-5"
    QFMA_CODE = "QFMA Code of Market Conduct"
    ARERA_RESOLUTION = "ARERA Market Monitoring"


class EnforcementLevel(Enum):
    """Level of enforcement action."""
    GUIDANCE = "regulatory_guidance"
    WARNING = "regulatory_warning"
    FINE = "monetary_penalty"
    SUSPENSION = "trading_suspension"
    CRIMINAL = "criminal_prosecution"


@dataclass
class EnforcementCase:
    """
    Enforcement case reference for CPT calibration.
    This provides the regulatory justification for specific
    probability settings based on real enforcement actions.
    """
    case_id: str
    case_name: str
    regulatory_authority: str
    framework: RegulatoryFramework
    enforcement_level: EnforcementLevel
    # Case details
    violation_type: str
    case_summary: str
    enforcement_date: datetime
    penalty_amount: Optional[float] = None
    # CPT relevance
    relevant_nodes: List[str] = field(default_factory=list)
    probability_justification: str = ""
    risk_threshold_impact: Dict[str, float] = field(default_factory=dict)
    # Metadata
    case_url: Optional[str] = None
    case_reference: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate enforcement case data."""
        if not self.case_id:
            self.case_id = f"ENF_{uuid4().hex[:8].upper()}"


@dataclass
class RegulatoryReference:
    """
    Regulatory reference for CPT definitions.
    Links CPT probability settings to regulatory requirements
    and enforcement precedents.
    """
    reference_id: str
    framework: RegulatoryFramework
    article_section: str
    # Regulatory details
    requirement_text: str
    interpretation_guidance: str
    compliance_threshold: Optional[float] = None
    # Enforcement precedents
    enforcement_cases: List[EnforcementCase] = field(default_factory=list)
    # CPT application
    applicable_typologies: List[str] = field(default_factory=list)
    node_mappings: Dict[str, str] = field(default_factory=dict)
    probability_rationale: str = ""
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    created_by: str = "system"

    def __post_init__(self):
        """Validate regulatory reference data."""
        if not self.reference_id:
            self.reference_id = f"REG_{uuid4().hex[:8].upper()}"

    def add_enforcement_case(self, case: EnforcementCase) -> None:
        """Add an enforcement case to this reference."""
        self.enforcement_cases.append(case)
        self.last_updated = datetime.now()

    def get_risk_threshold(self, typology: str) -> Optional[float]:
        """Get risk threshold for specific typology."""
        if typology not in self.applicable_typologies:
            return None
        return self.compliance_threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "reference_id": self.reference_id,
            "framework": self.framework.value,
            "article_section": self.article_section,
            "requirement_text": self.requirement_text,
            "interpretation_guidance": self.interpretation_guidance,
            "compliance_threshold": self.compliance_threshold,
            "enforcement_cases": [
                {
                    "case_id": case.case_id,
                    "case_name": case.case_name,
                    "regulatory_authority": case.regulatory_authority,
                    "framework": case.framework.value,
                    "enforcement_level": case.enforcement_level.value,
                    "violation_type": case.violation_type,
                    "case_summary": case.case_summary,
                    "enforcement_date": case.enforcement_date.isoformat(),
                    "penalty_amount": case.penalty_amount,
                    "relevant_nodes": case.relevant_nodes,
                    "probability_justification": case.probability_justification,
                    "risk_threshold_impact": case.risk_threshold_impact,
                    "case_url": case.case_url,
                    "case_reference": case.case_reference
                }
                for case in self.enforcement_cases
            ],
            "applicable_typologies": self.applicable_typologies,
            "node_mappings": self.node_mappings,
            "probability_rationale": self.probability_rationale,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "created_by": self.created_by
        }


class RegulatoryReferenceManager:
    """
    Manager for regulatory references and enforcement cases.
    Provides centralized access to regulatory justifications
    for CPT probability settings.
    """

    def __init__(self):
        """Initialize the regulatory reference manager."""
        self.references: Dict[str, RegulatoryReference] = {}
        self.enforcement_cases: Dict[str, EnforcementCase] = {}
        self._default_references_loaded = False

    def _ensure_default_references_loaded(self) -> None:
        """Ensure default references are loaded (lazy loading)."""
        if not self._default_references_loaded:
            self._load_default_references()
            self._default_references_loaded = True

    def _load_default_references(self) -> None:
        """Load default regulatory references."""
        # MAR Article 8 - Insider Dealing
        mar_8_ref = RegulatoryReference(
            reference_id="REG_MAR8_001",
            framework=RegulatoryFramework.MAR_ARTICLE_8,
            article_section="Article 8(1)",
            requirement_text="A person possesses inside information where they have access to information of a precise nature...",
            interpretation_guidance="Information access patterns and timing correlation are key indicators",
            compliance_threshold=ComplianceThresholds.MAR_ARTICLE_8_THRESHOLD,
            applicable_typologies=["insider_dealing"],
            node_mappings={
                "MaterialInfo": "Information access patterns",
                "Timing": "Temporal correlation with material events"
            },
            probability_rationale="Probability thresholds based on FCA enforcement patterns and ESMA guidance"
        )
        # Add sample enforcement case
        fca_case = EnforcementCase(
            case_id="ENF_FCA_2023_001",
            case_name="FCA v. Investment Manager - Insider Dealing",
            regulatory_authority="Financial Conduct Authority",
            framework=RegulatoryFramework.MAR_ARTICLE_8,
            enforcement_level=EnforcementLevel.FINE,
            violation_type="Insider Dealing",
            case_summary="Investment manager traded on material non-public information regarding acquisition",
            enforcement_date=datetime(2023, 6, 15),
            penalty_amount=2500000.0,
            relevant_nodes=["MaterialInfo", "Timing", "TradingActivity"],
            probability_justification=f"High probability threshold ({ComplianceThresholds.HIGH_RISK_THRESHOLD}) justified by clear information access and timing patterns",
            risk_threshold_impact={"high_risk": ComplianceThresholds.HIGH_RISK_THRESHOLD, "medium_risk": ComplianceThresholds.MEDIUM_RISK_THRESHOLD},
            case_reference="FCA/2023/INS/001"
        )
        mar_8_ref.add_enforcement_case(fca_case)
        self.add_reference(mar_8_ref)
        # MAR Article 12 - Market Manipulation
        mar_12_ref = RegulatoryReference(
            reference_id="REG_MAR12_001",
            framework=RegulatoryFramework.MAR_ARTICLE_12,
            article_section="Article 12(1)(a)",
            requirement_text="Entering into a transaction which gives false or misleading signals...",
            interpretation_guidance="Focus on order patterns, cancellation rates, and price impact",
            compliance_threshold=ComplianceThresholds.MAR_ARTICLE_12_THRESHOLD,
            applicable_typologies=["spoofing", "wash_trade_detection", "market_manipulation"],
            node_mappings={
                "OrderPattern": "Order placement patterns",
                "CancellationRate": "Order cancellation behavior",
                "PriceMovement": "Price impact assessment"
            },
            probability_rationale="Thresholds calibrated based on ESMA spoofing cases and market manipulation precedents"
        )
        self.add_reference(mar_12_ref)

    def add_reference(self, reference: RegulatoryReference) -> None:
        """Add a regulatory reference."""
        self.references[reference.reference_id] = reference
        # Index enforcement cases
        for case in reference.enforcement_cases:
            self.enforcement_cases[case.case_id] = case

    def get_reference(self, reference_id: str) -> Optional[RegulatoryReference]:
        """Get regulatory reference by ID."""
        return self.references.get(reference_id)

    def get_references_for_typology(self, typology: str) -> List[RegulatoryReference]:
        """Get all regulatory references applicable to a typology."""
        self._ensure_default_references_loaded()
        return [
            ref for ref in self.references.values()
            if typology in ref.applicable_typologies
        ]

    def get_enforcement_case(self, case_id: str) -> Optional[EnforcementCase]:
        """Get enforcement case by ID."""
        self._ensure_default_references_loaded()
        return self.enforcement_cases.get(case_id)

    def get_compliance_threshold(self, typology: str, framework: RegulatoryFramework) -> Optional[float]:
        """Get compliance threshold for typology and framework."""
        refs = self.get_references_for_typology(typology)
        for ref in refs:
            if ref.framework == framework:
                return ref.compliance_threshold
        return None

    def export_references(self) -> Dict[str, Any]:
        """Export all references for serialization."""
        self._ensure_default_references_loaded()
        return {
            "references": {
                ref_id: ref.to_dict()
                for ref_id, ref in self.references.items()
            },
            "metadata": {
                "total_references": len(self.references),
                "total_enforcement_cases": len(self.enforcement_cases),
                "export_timestamp": datetime.now().isoformat()
            }
        }
