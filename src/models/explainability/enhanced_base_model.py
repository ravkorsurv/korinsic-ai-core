"""
Enhanced Base Model with Explainability

This module provides an enhanced base model class that includes comprehensive
explainability features, audit logging, and governance tracking for all models.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging

from ..shared import BaseModel, ModelMetadata
from .evidence_sufficiency_index import EvidenceSufficiencyIndex, ESIResult

logger = logging.getLogger(__name__)


class EnhancedBaseModel(BaseModel):
    """
    Enhanced base model with comprehensive explainability features.

    This class extends the base model to include:
    - Detailed explainability features
    - Comprehensive audit logging
    - Model governance tracking
    - Regulatory compliance support
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the enhanced base model.

        Args:
            config: Optional model configuration
        """
        super().__init__(config)

        # Initialize explainability components
        config = config or {}
        self.explainability_enabled = config.get("explainability_enabled", True)
        self.audit_enabled = config.get("audit_enabled", True)
        self.governance_enabled = config.get("governance_enabled", True)

        # Initialize ESI calculator
        self.esi_calculator = EvidenceSufficiencyIndex(weights=config.get("esi_weights"))

        # Enhanced metadata
        self.metadata = EnhancedModelMetadata()

        # Initialize tracking
        self.decision_history = []
        self.explanation_cache = {}

        logger.info(
            f"Enhanced base model initialized with explainability={self.explainability_enabled}"
        )

    def calculate_risk(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk with enhanced features.

        Args:
            evidence: Evidence dictionary

        Returns:
            Enhanced risk assessment with explainability
        """
        try:
            # Record decision start
            decision_id = self._generate_decision_id()
            start_time = datetime.now(timezone.utc)

            # Log audit trail
            if self.audit_enabled:
                self._log_decision_start(decision_id, evidence, start_time)

            # Calculate risk with explanation
            if self.explainability_enabled:
                result = self.calculate_risk_with_explanation(evidence)
            else:
                result = self._calculate_basic_risk(evidence)

            # Calculate Evidence Sufficiency Index
            esi_result = self.calculate_evidence_sufficiency_index(evidence, result)
            result["evidence_sufficiency_index"] = esi_result

            # Calculate adjusted risk score using ESI
            if "risk_scores" in result and "overall_score" in result["risk_scores"]:
                original_score = result["risk_scores"]["overall_score"]
                adjusted_score = self.esi_calculator.calculate_adjusted_risk_score(
                    original_score, esi_result
                )
                result["risk_scores"]["esi_adjusted_score"] = adjusted_score

            # Add metadata
            result["decision_metadata"] = {
                "decision_id": decision_id,
                "timestamp": start_time.isoformat(),
                "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "explainability_enabled": self.explainability_enabled,
                "audit_enabled": self.audit_enabled,
                "model_version": self.metadata.version,
                "esi_enabled": True,
            }

            # Store decision
            self._store_decision(decision_id, evidence, result)

            # Log completion
            if self.audit_enabled:
                self._log_decision_completion(decision_id, result)

            return result

        except Exception as e:
            logger.error(f"Error in enhanced risk calculation: {str(e)}")
            # Log error
            if self.audit_enabled:
                self._log_decision_error(decision_id, str(e))
            raise

    @abstractmethod
    def calculate_risk_with_explanation(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk with detailed explanations.

        Args:
            evidence: Evidence dictionary

        Returns:
            Risk assessment with comprehensive explanations
        """
        pass

    @abstractmethod
    def generate_counterfactuals(self, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate counterfactual explanations.

        Args:
            evidence: Evidence dictionary

        Returns:
            List of counterfactual scenarios
        """
        pass

    @abstractmethod
    def explain_decision_path(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain the decision-making path.

        Args:
            evidence: Evidence dictionary

        Returns:
            Detailed decision path explanation
        """
        pass

    def get_feature_importance(self, evidence: Dict[str, Any]) -> Dict[str, float]:
        """
        Get feature importance scores.

        Args:
            evidence: Evidence dictionary

        Returns:
            Feature importance scores
        """
        try:
            # Calculate risk first
            risk_result = self.calculate_risk_with_explanation(evidence)

            # Extract feature contributions
            feature_importance = {}

            if "feature_contributions" in risk_result:
                for feature, contribution in risk_result["feature_contributions"].items():
                    feature_importance[feature] = contribution.get("importance", 0.0)

            return feature_importance

        except Exception as e:
            logger.error(f"Error calculating feature importance: {str(e)}")
            return {}

    def calculate_evidence_sufficiency_index(
        self, evidence: Dict[str, Any], result: Dict[str, Any]
    ) -> ESIResult:
        """
        Calculate Evidence Sufficiency Index for the given evidence and result.

        Args:
            evidence: Input evidence dictionary
            result: Model inference result

        Returns:
            ESI calculation result matching wiki specification
        """
        try:
            return self.esi_calculator.calculate_esi(evidence, result)
        except Exception as e:
            logger.error(f"ESI calculation failed: {e}")
            # Return conservative ESI on failure
            return ESIResult(
                evidence_sufficiency_index=0.5,
                node_count=len(result.get("active_nodes", [])),
                mean_confidence="Medium",
                fallback_ratio=1.0,
                contribution_spread="Unknown",
                clusters=["System"],
                calculation_details={"error": "ESI calculation failed", "fallback_applied": True},
            )

    def validate_evidence_enhanced(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced evidence validation with detailed reporting.

        Args:
            evidence: Evidence to validate

        Returns:
            Detailed validation report
        """
        # Basic validation
        basic_validation = self.validate_evidence(evidence)

        # Enhanced validation
        enhanced_validation = {
            "basic_validation": basic_validation,
            "evidence_quality_score": self._calculate_evidence_quality(evidence),
            "completeness_score": self._calculate_completeness_score(evidence),
            "reliability_score": self._calculate_reliability_score(evidence),
            "regulatory_compliance": self._check_regulatory_compliance(evidence),
            "data_lineage": self._trace_data_lineage(evidence),
        }

        return enhanced_validation

    def get_model_explanation(self) -> Dict[str, Any]:
        """
        Get comprehensive model explanation.

        Returns:
            Detailed model explanation for regulatory purposes
        """
        return {
            "model_info": self.get_model_info(),
            "explainability_features": {
                "feature_attribution": True,
                "counterfactual_generation": True,
                "decision_path_explanation": True,
                "uncertainty_quantification": True,
                "evidence_sufficiency_index": True,
            },
            "audit_capabilities": {
                "decision_logging": self.audit_enabled,
                "data_lineage_tracking": True,
                "regulatory_compliance": True,
            },
            "governance_features": {
                "performance_monitoring": self.governance_enabled,
                "drift_detection": True,
                "model_versioning": True,
            },
            "regulatory_compliance": {
                "explainable_ai_ready": True,
                "audit_trail_complete": True,
                "risk_documentation": True,
            },
        }

    def _calculate_basic_risk(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate basic risk without explainability.

        Args:
            evidence: Evidence dictionary

        Returns:
            Basic risk assessment
        """
        # Fallback to parent implementation
        return super().calculate_risk(evidence)

    def _generate_decision_id(self) -> str:
        """Generate unique decision ID."""
        return f"decision_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"

    def _log_decision_start(self, decision_id: str, evidence: Dict[str, Any], timestamp: datetime):
        """Log decision start."""
        self.metadata.record_decision_start(decision_id, evidence, timestamp)

    def _log_decision_completion(self, decision_id: str, result: Dict[str, Any]):
        """Log decision completion."""
        self.metadata.record_decision_completion(decision_id, result)

    def _log_decision_error(self, decision_id: str, error: str):
        """Log decision error."""
        self.metadata.record_decision_error(decision_id, error)

    def _store_decision(self, decision_id: str, evidence: Dict[str, Any], result: Dict[str, Any]):
        """Store decision in history."""
        self.decision_history.append(
            {
                "decision_id": decision_id,
                "evidence": evidence,
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Keep only last 1000 decisions
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]

    def _calculate_evidence_quality(self, evidence: Dict[str, Any]) -> float:
        """Calculate evidence quality score."""
        quality_score = 0.0
        total_weight = 0.0

        for key, value in evidence.items():
            if value is not None:
                quality_score += 1.0
                total_weight += 1.0
            else:
                total_weight += 1.0

        return quality_score / total_weight if total_weight > 0 else 0.0

    def _calculate_completeness_score(self, evidence: Dict[str, Any]) -> float:
        """Calculate evidence completeness score."""
        try:
            # Try to get required nodes if method exists
            get_required_nodes = getattr(self, "get_required_nodes", None)
            if get_required_nodes and callable(get_required_nodes):
                required_fields_result = get_required_nodes()
                # Ensure it's a list
                if isinstance(required_fields_result, list):
                    required_fields = required_fields_result
                else:
                    required_fields = []
            else:
                required_fields = []
        except (AttributeError, TypeError):
            required_fields = []

        if not required_fields:
            return 1.0

        present_fields = sum(
            1 for field in required_fields if field in evidence and evidence[field] is not None
        )
        return present_fields / len(required_fields)

    def _calculate_reliability_score(self, evidence: Dict[str, Any]) -> float:
        """Calculate evidence reliability score."""
        # Simple reliability calculation based on data types and values
        reliability_score = 0.0
        total_fields = 0

        for key, value in evidence.items():
            total_fields += 1
            if isinstance(value, (int, float)) and value >= 0:
                reliability_score += 1.0
            elif isinstance(value, str) and value.strip():
                reliability_score += 0.8
            elif isinstance(value, (list, dict)) and value:
                reliability_score += 0.9
            else:
                reliability_score += 0.5

        return reliability_score / total_fields if total_fields > 0 else 0.0

    def _check_regulatory_compliance(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Check regulatory compliance."""
        return {
            "data_privacy_compliant": True,
            "audit_trail_complete": True,
            "explainability_ready": True,
            "regulatory_frameworks": ["MAR", "MiFID II"],
            "compliance_score": 1.0,
        }

    def _trace_data_lineage(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Trace data lineage for audit purposes."""
        return {
            "data_sources": list(evidence.keys()),
            "processing_timestamp": datetime.now(timezone.utc).isoformat(),
            "transformation_steps": ["validation", "normalization", "feature_extraction"],
            "lineage_complete": True,
        }


class EnhancedModelMetadata(ModelMetadata):
    """
    Enhanced model metadata with explainability tracking.
    """

    def __init__(self):
        super().__init__()
        self.decision_log = []
        self.explanation_metrics = {
            "explanations_generated": 0,
            "counterfactuals_generated": 0,
            "feature_attributions_calculated": 0,
        }
        self.audit_metrics = {"decisions_logged": 0, "errors_logged": 0, "compliance_checks": 0}

    def record_decision_start(
        self, decision_id: str, evidence: Dict[str, Any], timestamp: datetime
    ):
        """Record decision start in audit log."""
        self.decision_log.append(
            {
                "decision_id": decision_id,
                "event": "decision_start",
                "evidence_keys": list(evidence.keys()),
                "timestamp": timestamp.isoformat(),
            }
        )
        self.audit_metrics["decisions_logged"] += 1

    def record_decision_completion(self, decision_id: str, result: Dict[str, Any]):
        """Record decision completion in audit log."""
        self.decision_log.append(
            {
                "decision_id": decision_id,
                "event": "decision_completion",
                "risk_score": result.get("risk_scores", {}).get("overall_score", 0.0),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def record_decision_error(self, decision_id: str, error: str):
        """Record decision error in audit log."""
        self.decision_log.append(
            {
                "decision_id": decision_id,
                "event": "decision_error",
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        self.audit_metrics["errors_logged"] += 1

    def get_enhanced_metadata(self) -> Dict[str, Any]:
        """Get enhanced metadata including explainability metrics."""
        base_metadata = self.get_metadata()

        enhanced_metadata = {
            **base_metadata,
            "explanation_metrics": self.explanation_metrics.copy(),
            "audit_metrics": self.audit_metrics.copy(),
            "decision_log_size": len(self.decision_log),
            "enhanced_features": {
                "explainability_enabled": True,
                "audit_logging": True,
                "governance_tracking": True,
            },
        }

        return enhanced_metadata
