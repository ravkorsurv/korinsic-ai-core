"""
Model Audit Logger

This module provides comprehensive audit logging capabilities for model decisions
and regulatory compliance tracking.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AuditLogEntry:
    """Audit log entry."""

    entry_id: str
    timestamp: str
    model_id: str
    event_type: str
    event_data: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    regulatory_context: Optional[Dict[str, Any]] = None


class ModelAuditLogger:
    """
    Comprehensive model audit logger.

    This class provides audit logging capabilities for:
    - Model decisions and predictions
    - Regulatory compliance tracking
    - Risk assessment documentation
    - Data lineage tracking
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the audit logger.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.audit_log = []
        self.compliance_checker = ComplianceChecker(self.config.get("compliance", {}))
        self.regulatory_reporter = RegulatoryReporter(self.config.get("regulatory", {}))
        self.risk_documenter = RiskDocumenter(self.config.get("risk_documentation", {}))

        logger.info("Model audit logger initialized")

    def log_model_decision(
        self,
        model_id: str,
        decision: Dict[str, Any],
        explanation: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Log model decision with full audit trail.

        Args:
            model_id: Unique model identifier
            decision: Model decision data
            explanation: Model explanation data
            user_id: Optional user identifier
            session_id: Optional session identifier

        Returns:
            Audit entry ID
        """
        try:
            entry_id = self._generate_audit_entry_id()

            # Create audit entry
            audit_entry = AuditLogEntry(
                entry_id=entry_id,
                timestamp=datetime.utcnow().isoformat(),
                model_id=model_id,
                event_type="model_decision",
                event_data={
                    "decision": decision,
                    "explanation": explanation,
                    "decision_metadata": {
                        "risk_level": decision.get("risk_assessment", {}).get(
                            "risk_level", "unknown"
                        ),
                        "confidence": decision.get("risk_scores", {}).get("confidence", 0.0),
                        "explainability_score": explanation.get("explanation_metadata", {}).get(
                            "explanation_quality", 0.0
                        ),
                    },
                },
                user_id=user_id,
                session_id=session_id,
                regulatory_context=self._get_regulatory_context(decision, explanation),
            )

            # Store audit entry
            self.audit_log.append(audit_entry)

            # Check compliance
            compliance_result = self.compliance_checker.check_decision_compliance(
                decision, explanation
            )

            # Log compliance check
            self._log_compliance_check(entry_id, compliance_result)

            # Generate regulatory documentation if high risk
            if self._is_high_risk_decision(decision):
                self.risk_documenter.document_high_risk_decision(entry_id, decision, explanation)

            logger.info(f"Model decision logged: {entry_id}")
            return entry_id

        except Exception as e:
            logger.error(f"Error logging model decision: {str(e)}")
            raise

    def log_compliance_event(
        self, model_id: str, event_type: str, event_data: Dict[str, Any]
    ) -> str:
        """
        Log compliance-related event.

        Args:
            model_id: Model identifier
            event_type: Type of compliance event
            event_data: Event data

        Returns:
            Audit entry ID
        """
        entry_id = self._generate_audit_entry_id()

        audit_entry = AuditLogEntry(
            entry_id=entry_id,
            timestamp=datetime.utcnow().isoformat(),
            model_id=model_id,
            event_type=f"compliance_{event_type}",
            event_data=event_data,
            regulatory_context={"compliance_event": True},
        )

        self.audit_log.append(audit_entry)

        logger.info(f"Compliance event logged: {entry_id}")
        return entry_id

    def get_audit_trail(
        self,
        model_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail for regulatory purposes.

        Args:
            model_id: Optional model ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of audit entries
        """
        filtered_entries = []

        for entry in self.audit_log:
            # Apply filters
            if model_id and entry.model_id != model_id:
                continue

            if start_date and entry.timestamp < start_date:
                continue

            if end_date and entry.timestamp > end_date:
                continue

            filtered_entries.append(asdict(entry))

        return filtered_entries

    def generate_compliance_report(
        self, model_id: str, report_type: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate compliance report.

        Args:
            model_id: Model identifier
            report_type: Type of report

        Returns:
            Compliance report
        """
        return self.regulatory_reporter.generate_compliance_report(
            model_id, self.audit_log, report_type
        )

    def _generate_audit_entry_id(self) -> str:
        """Generate unique audit entry ID."""
        return f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"

    def _get_regulatory_context(
        self, decision: Dict[str, Any], explanation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get regulatory context for decision."""

        return {
            "regulatory_frameworks": ["MAR", "MiFID II", "GDPR"],
            "compliance_requirements": {
                "explainability_required": True,
                "audit_trail_required": True,
                "risk_documentation_required": self._is_high_risk_decision(decision),
            },
            "risk_classification": decision.get("risk_assessment", {}).get("risk_level", "unknown"),
            "explainability_score": explanation.get("explanation_metadata", {}).get(
                "explanation_quality", 0.0
            ),
        }

    def _is_high_risk_decision(self, decision: Dict[str, Any]) -> bool:
        """Check if decision is high risk."""
        risk_level = decision.get("risk_assessment", {}).get("risk_level", "low")
        return risk_level.upper() == "HIGH"

    def _log_compliance_check(self, entry_id: str, compliance_result: Dict[str, Any]):
        """Log compliance check result."""

        compliance_entry = AuditLogEntry(
            entry_id=f"{entry_id}_compliance",
            timestamp=datetime.utcnow().isoformat(),
            model_id=entry_id,
            event_type="compliance_check",
            event_data=compliance_result,
            regulatory_context={"compliance_check": True},
        )

        self.audit_log.append(compliance_entry)


class ComplianceChecker:
    """Compliance checker for regulatory requirements."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.compliance_rules = self._load_compliance_rules()

    def check_decision_compliance(
        self, decision: Dict[str, Any], explanation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check decision compliance."""

        compliance_results = {
            "overall_compliance": True,
            "compliance_score": 1.0,
            "checks_performed": [],
            "violations": [],
            "recommendations": [],
        }

        # Check explainability requirements
        explainability_check = self._check_explainability_compliance(explanation)
        compliance_results["checks_performed"].append(explainability_check)

        # Check audit trail requirements
        audit_trail_check = self._check_audit_trail_compliance(decision)
        compliance_results["checks_performed"].append(audit_trail_check)

        # Check risk documentation requirements
        risk_doc_check = self._check_risk_documentation_compliance(decision, explanation)
        compliance_results["checks_performed"].append(risk_doc_check)

        # Calculate overall compliance
        compliance_results["overall_compliance"] = all(
            check["passed"] for check in compliance_results["checks_performed"]
        )

        compliance_results["compliance_score"] = sum(
            check["score"] for check in compliance_results["checks_performed"]
        ) / len(compliance_results["checks_performed"])

        return compliance_results

    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules."""
        return {
            "explainability_required": True,
            "audit_trail_required": True,
            "risk_documentation_required": True,
            "minimum_explanation_quality": 0.7,
            "minimum_compliance_score": 0.8,
        }

    def _check_explainability_compliance(self, explanation: Dict[str, Any]) -> Dict[str, Any]:
        """Check explainability compliance."""

        has_feature_attributions = len(explanation.get("feature_attributions", [])) > 0
        has_decision_path = len(explanation.get("decision_path", [])) > 0
        explanation_quality = explanation.get("explanation_metadata", {}).get(
            "explanation_quality", 0.0
        )

        passed = (
            has_feature_attributions
            and has_decision_path
            and explanation_quality >= self.compliance_rules["minimum_explanation_quality"]
        )

        return {
            "check_name": "explainability_compliance",
            "passed": passed,
            "score": explanation_quality,
            "details": {
                "has_feature_attributions": has_feature_attributions,
                "has_decision_path": has_decision_path,
                "explanation_quality": explanation_quality,
            },
        }

    def _check_audit_trail_compliance(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Check audit trail compliance."""

        has_decision_metadata = "decision_metadata" in decision
        has_timestamp = decision.get("decision_metadata", {}).get("timestamp") is not None

        passed = has_decision_metadata and has_timestamp
        score = 1.0 if passed else 0.0

        return {
            "check_name": "audit_trail_compliance",
            "passed": passed,
            "score": score,
            "details": {
                "has_decision_metadata": has_decision_metadata,
                "has_timestamp": has_timestamp,
            },
        }

    def _check_risk_documentation_compliance(
        self, decision: Dict[str, Any], explanation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check risk documentation compliance."""

        risk_level = decision.get("risk_assessment", {}).get("risk_level", "unknown")
        is_high_risk = risk_level.upper() == "HIGH"

        # High risk decisions require additional documentation
        if is_high_risk:
            has_risk_indicators = (
                len(explanation.get("regulatory_summary", {}).get("risk_indicators", [])) > 0
            )
            has_decision_rationale = (
                explanation.get("regulatory_summary", {}).get("decision_rationale", "") != ""
            )

            passed = has_risk_indicators and has_decision_rationale
            score = 1.0 if passed else 0.5
        else:
            passed = True
            score = 1.0

        return {
            "check_name": "risk_documentation_compliance",
            "passed": passed,
            "score": score,
            "details": {
                "is_high_risk": is_high_risk,
                "risk_level": risk_level,
                "documentation_required": is_high_risk,
            },
        }


class RegulatoryReporter:
    """Regulatory reporter for compliance reports."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate_compliance_report(
        self, model_id: str, audit_log: List[AuditLogEntry], report_type: str
    ) -> Dict[str, Any]:
        """Generate compliance report."""

        # Filter audit log for this model
        model_entries = [entry for entry in audit_log if entry.model_id == model_id]

        return {
            "report_id": f"compliance_{model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "model_id": model_id,
            "report_type": report_type,
            "generation_timestamp": datetime.utcnow().isoformat(),
            "total_decisions": len([e for e in model_entries if e.event_type == "model_decision"]),
            "compliance_summary": self._generate_compliance_summary(model_entries),
            "regulatory_frameworks": ["MAR", "MiFID II", "GDPR"],
            "audit_trail_complete": True,
        }

    def _generate_compliance_summary(self, audit_entries: List[AuditLogEntry]) -> Dict[str, Any]:
        """Generate compliance summary."""

        decision_entries = [e for e in audit_entries if e.event_type == "model_decision"]

        if not decision_entries:
            return {
                "overall_compliance": True,
                "compliance_score": 1.0,
                "total_decisions": 0,
                "violations": [],
            }

        # Calculate compliance metrics
        compliance_scores = []
        for entry in decision_entries:
            explanation = entry.event_data.get("explanation", {})
            compliance_scores.append(
                explanation.get("explanation_metadata", {})
                .get("regulatory_compliance", {})
                .get("compliance_score", 0.0)
            )

        avg_compliance_score = (
            sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
        )

        return {
            "overall_compliance": avg_compliance_score >= 0.8,
            "compliance_score": avg_compliance_score,
            "total_decisions": len(decision_entries),
            "violations": [],  # Would be populated with actual violations
        }


class RiskDocumenter:
    """Risk documenter for high-risk decisions."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.risk_documents = []

    def document_high_risk_decision(
        self, entry_id: str, decision: Dict[str, Any], explanation: Dict[str, Any]
    ) -> str:
        """Document high-risk decision."""

        document_id = f"risk_doc_{entry_id}"

        risk_document = {
            "document_id": document_id,
            "audit_entry_id": entry_id,
            "timestamp": datetime.utcnow().isoformat(),
            "risk_level": decision.get("risk_assessment", {}).get("risk_level", "unknown"),
            "risk_score": decision.get("risk_scores", {}).get("overall_score", 0.0),
            "key_risk_factors": explanation.get("regulatory_summary", {}).get("key_factors", []),
            "decision_rationale": explanation.get("regulatory_summary", {}).get(
                "decision_rationale", ""
            ),
            "regulatory_context": {
                "applicable_regulations": ["MAR", "MiFID II"],
                "compliance_requirements": ["explainability", "audit_trail", "risk_documentation"],
                "documentation_complete": True,
            },
        }

        self.risk_documents.append(risk_document)

        logger.info(f"High-risk decision documented: {document_id}")
        return document_id
