"""
Enhanced Insider Dealing Detection Model

This module demonstrates the enhanced insider dealing model with comprehensive
explainability, audit logging, and governance features for regulatory compliance.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...explainability import (
    EnhancedBaseModel,
    ModelAuditLogger,
    ModelExplainabilityEngine,
    ModelGovernanceTracker,
)
from .config import InsiderDealingConfig
from .model import InsiderDealingModel  # Original model
from .nodes import InsiderDealingNodes

logger = logging.getLogger(__name__)


class EnhancedInsiderDealingModel(EnhancedBaseModel):
    """
    Enhanced insider dealing detection model with comprehensive explainability.

    This model extends the base insider dealing model to include:
    - Comprehensive explainability features
    - Full audit trail logging
    - Regulatory compliance verification
    - Model governance tracking
    """

    def __init__(
        self, use_latent_intent: bool = False, config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the enhanced insider dealing model.

        Args:
            use_latent_intent: Whether to use latent intent modeling
            config: Optional model configuration
        """
        # Initialize enhanced base model
        super().__init__(config)

        # Model-specific configuration
        self.use_latent_intent = use_latent_intent
        self.model_config = InsiderDealingConfig(config or {})
        self.nodes = InsiderDealingNodes()

        # Initialize original model for core functionality
        self.core_model = InsiderDealingModel(use_latent_intent, config or {})

        # Initialize explainability components
        if self.explainability_enabled:
            self.explainability_engine = ModelExplainabilityEngine(
                self.config.get("explainability", {})
            )

        # Initialize audit logger
        if self.audit_enabled:
            self.audit_logger = ModelAuditLogger(self.config.get("audit", {}))

        # Initialize governance tracker
        if self.governance_enabled:
            self.governance_tracker = ModelGovernanceTracker(
                self.config.get("governance", {})
            )

        logger.info(
            f"Enhanced insider dealing model initialized (latent_intent={use_latent_intent})"
        )

    def calculate_risk_with_explanation(
        self, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate insider dealing risk with comprehensive explanations.

        Args:
            evidence: Evidence dictionary

        Returns:
            Risk assessment with detailed explanations
        """
        try:
            # Validate evidence
            validation_result = self.validate_evidence_enhanced(evidence)

            # Calculate core risk using original model
            core_risk_result = self.core_model.calculate_risk(evidence)

            # Generate comprehensive explanation
            if self.explainability_enabled:
                explanation = (
                    self.explainability_engine.generate_comprehensive_explanation(
                        core_risk_result, evidence, "insider_dealing"
                    )
                )
            else:
                explanation = {"explanation_available": False}

            # Enhanced risk assessment
            enhanced_result = {
                "risk_scores": core_risk_result.get("risk_scores", {}),
                "evidence_sufficiency": core_risk_result.get(
                    "evidence_sufficiency", {}
                ),
                "risk_assessment": core_risk_result.get("risk_assessment", {}),
                "fallback_report": core_risk_result.get("fallback_report", {}),
                "model_metadata": {
                    **core_risk_result.get("model_metadata", {}),
                    "enhanced_features": True,
                    "explainability_enabled": self.explainability_enabled,
                    "model_version": "2.0_enhanced",
                },
                "explainability": explanation,
                "evidence_validation": validation_result,
                "insider_dealing_specifics": self._generate_insider_dealing_specifics(
                    core_risk_result, evidence, explanation
                ),
            }

            # Log decision for audit
            if self.audit_enabled:
                audit_entry_id = self.audit_logger.log_model_decision(
                    model_id=f"enhanced_insider_dealing_{self.use_latent_intent}",
                    decision=enhanced_result,
                    explanation=explanation,
                )
                enhanced_result["audit_entry_id"] = audit_entry_id

            # Track governance
            if self.governance_enabled:
                self.governance_tracker.track_model_lifecycle(
                    model_id=f"enhanced_insider_dealing_{self.use_latent_intent}",
                    event="risk_calculation",
                    metadata={
                        "risk_level": enhanced_result.get("risk_assessment", {}).get(
                            "risk_level", "unknown"
                        ),
                        "evidence_quality": validation_result.get(
                            "evidence_quality_score", 0.0
                        ),
                        "explainability_score": (
                            0.0
                            if not isinstance(explanation, dict)
                            else explanation.get("explanation_metadata", {}).get(
                                "explanation_quality", 0.0
                            )
                        ),
                    },
                )

            return enhanced_result

        except Exception as e:
            logger.error(
                f"Error in enhanced insider dealing risk calculation: {str(e)}"
            )
            raise

    def generate_counterfactuals(
        self, evidence: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate counterfactual explanations for insider dealing scenarios.

        Args:
            evidence: Evidence dictionary

        Returns:
            List of counterfactual scenarios
        """
        try:
            # Calculate baseline risk
            baseline_result = self.calculate_risk_with_explanation(evidence)
            baseline_score = baseline_result.get("risk_scores", {}).get(
                "overall_score", 0.0
            )

            counterfactuals = []

            # Scenario 1: No material information access
            if evidence.get("MaterialInfo", 0) > 0:
                modified_evidence = evidence.copy()
                modified_evidence["MaterialInfo"] = 0

                modified_result = self.core_model.calculate_risk(modified_evidence)
                modified_score = modified_result.get("risk_scores", {}).get(
                    "overall_score", 0.0
                )

                counterfactuals.append(
                    {
                        "scenario_id": "no_material_info",
                        "description": "What if there was no access to material information?",
                        "original_score": baseline_score,
                        "counterfactual_score": modified_score,
                        "score_change": modified_score - baseline_score,
                        "changed_factors": {"MaterialInfo": 0},
                        "explanation": f"Risk would {'decrease' if modified_score < baseline_score else 'remain similar'} to {modified_score:.2%}",
                        "regulatory_relevance": "High - Material information access is key regulatory indicator",
                        "plausibility": 0.8,
                    }
                )

            # Scenario 2: Normal trading patterns
            if evidence.get("TradingActivity", 0) > 1:
                modified_evidence = evidence.copy()
                modified_evidence["TradingActivity"] = 0  # Normal trading

                modified_result = self.core_model.calculate_risk(modified_evidence)
                modified_score = modified_result.get("risk_scores", {}).get(
                    "overall_score", 0.0
                )

                counterfactuals.append(
                    {
                        "scenario_id": "normal_trading",
                        "description": "What if trading patterns were normal?",
                        "original_score": baseline_score,
                        "counterfactual_score": modified_score,
                        "score_change": modified_score - baseline_score,
                        "changed_factors": {"TradingActivity": 0},
                        "explanation": f"Risk would change to {modified_score:.2%} with normal trading patterns",
                        "regulatory_relevance": "Medium - Trading patterns are supportive evidence",
                        "plausibility": 0.7,
                    }
                )

            # Scenario 3: Poor timing correlation
            if evidence.get("Timing", 0) > 1:
                modified_evidence = evidence.copy()
                modified_evidence["Timing"] = 0  # Poor timing

                modified_result = self.core_model.calculate_risk(modified_evidence)
                modified_score = modified_result.get("risk_scores", {}).get(
                    "overall_score", 0.0
                )

                counterfactuals.append(
                    {
                        "scenario_id": "poor_timing",
                        "description": "What if timing correlation was poor?",
                        "original_score": baseline_score,
                        "counterfactual_score": modified_score,
                        "score_change": modified_score - baseline_score,
                        "changed_factors": {"Timing": 0},
                        "explanation": f"Risk would change to {modified_score:.2%} with poor timing correlation",
                        "regulatory_relevance": "High - Timing is crucial for insider dealing detection",
                        "plausibility": 0.6,
                    }
                )

            return counterfactuals

        except Exception as e:
            logger.error(f"Error generating counterfactuals: {str(e)}")
            return []

    def explain_decision_path(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain the decision-making path for insider dealing detection.

        Args:
            evidence: Evidence dictionary

        Returns:
            Detailed decision path explanation
        """
        try:
            # Calculate risk to get inference details
            risk_result = self.calculate_risk_with_explanation(evidence)

            # Build decision path
            decision_path = {
                "model_type": "insider_dealing",
                "use_latent_intent": self.use_latent_intent,
                "decision_steps": [],
                "regulatory_framework": "MAR Article 14 - Insider Dealing",
                "evidence_analysis": {},
                "final_assessment": {},
            }

            # Step 1: Evidence evaluation
            decision_path["decision_steps"].append(
                {
                    "step": 1,
                    "name": "Evidence Evaluation",
                    "description": "Assess quality and completeness of evidence",
                    "input": evidence,
                    "output": risk_result.get("evidence_validation", {}),
                    "rationale": "Evidence must meet quality thresholds for reliable assessment",
                }
            )

            # Step 2: Material information analysis
            material_info = evidence.get("MaterialInfo", 0)
            decision_path["decision_steps"].append(
                {
                    "step": 2,
                    "name": "Material Information Access",
                    "description": "Evaluate access to material non-public information",
                    "input": {"MaterialInfo": material_info},
                    "output": {
                        "level": ["No access", "Potential access", "Clear access"][
                            min(material_info, 2)
                        ],
                        "weight": 0.4,  # High weight for regulatory compliance
                        "regulatory_significance": "Primary indicator for MAR Article 14",
                    },
                    "rationale": "Material information access is the primary legal requirement for insider dealing",
                }
            )

            # Step 3: Trading pattern analysis
            trading_activity = evidence.get("TradingActivity", 0)
            decision_path["decision_steps"].append(
                {
                    "step": 3,
                    "name": "Trading Pattern Analysis",
                    "description": "Analyze unusual trading patterns",
                    "input": {"TradingActivity": trading_activity},
                    "output": {
                        "level": ["Normal", "Unusual", "Highly unusual"][
                            min(trading_activity, 2)
                        ],
                        "weight": 0.3,
                        "regulatory_significance": "Supporting evidence for suspicious activity",
                    },
                    "rationale": "Unusual trading patterns support insider dealing allegations",
                }
            )

            # Step 4: Timing analysis
            timing = evidence.get("Timing", 0)
            decision_path["decision_steps"].append(
                {
                    "step": 4,
                    "name": "Timing Correlation",
                    "description": "Assess timing relative to material events",
                    "input": {"Timing": timing},
                    "output": {
                        "level": ["Poor", "Moderate", "Strong"][min(timing, 2)],
                        "weight": 0.3,
                        "regulatory_significance": "Critical for establishing causal relationship",
                    },
                    "rationale": "Timing correlation establishes the link between information access and trading",
                }
            )

            # Step 5: Final risk calculation
            overall_score = risk_result.get("risk_scores", {}).get("overall_score", 0.0)
            decision_path["decision_steps"].append(
                {
                    "step": 5,
                    "name": "Risk Aggregation",
                    "description": "Combine evidence into overall risk score",
                    "input": {
                        "material_info_weight": 0.4,
                        "trading_pattern_weight": 0.3,
                        "timing_weight": 0.3,
                    },
                    "output": {
                        "overall_score": overall_score,
                        "risk_level": risk_result.get("risk_assessment", {}).get(
                            "risk_level", "unknown"
                        ),
                        "confidence": risk_result.get("risk_scores", {}).get(
                            "confidence", "medium"
                        ),
                    },
                    "rationale": "Weighted combination of evidence factors produces final risk assessment",
                }
            )

            # Evidence analysis summary
            decision_path["evidence_analysis"] = {
                "primary_factors": {
                    "material_information": material_info,
                    "trading_activity": trading_activity,
                    "timing_correlation": timing,
                },
                "regulatory_compliance": {
                    "mar_article_14_elements": {
                        "material_information": material_info >= 1,
                        "trading_activity": trading_activity >= 1,
                        "causal_relationship": timing >= 1,
                    },
                    "compliance_score": self._calculate_regulatory_compliance_score(
                        evidence
                    ),
                },
            }

            # Final assessment
            decision_path["final_assessment"] = {
                "overall_risk_score": overall_score,
                "risk_level": risk_result.get("risk_assessment", {}).get(
                    "risk_level", "unknown"
                ),
                "regulatory_action_required": overall_score >= 0.7,
                "key_evidence": self._identify_key_evidence(evidence),
                "regulatory_rationale": self._generate_regulatory_rationale(
                    evidence, overall_score
                ),
            }

            return decision_path

        except Exception as e:
            logger.error(f"Error explaining decision path: {str(e)}")
            return {"error": str(e)}

    def get_required_nodes(self) -> List[str]:
        """
        Get list of required nodes for this enhanced model.

        Returns:
            List of required node names
        """
        return self.core_model.get_required_nodes()

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive model information.

        Returns:
            Enhanced model information dictionary
        """
        base_info = self.core_model.get_model_info()

        enhanced_info = {
            **base_info,
            "model_version": "2.0_enhanced",
            "enhanced_features": {
                "explainability_enabled": self.explainability_enabled,
                "audit_logging": self.audit_enabled,
                "governance_tracking": self.governance_enabled,
                "counterfactual_generation": True,
                "decision_path_explanation": True,
                "regulatory_compliance_checking": True,
            },
            "regulatory_frameworks": ["MAR Article 14", "MiFID II Article 48"],
            "compliance_capabilities": {
                "audit_trail_complete": True,
                "explainability_ready": True,
                "regulatory_reporting": True,
                "risk_documentation": True,
            },
            "governance_features": {
                "performance_monitoring": self.governance_enabled,
                "drift_detection": self.governance_enabled,
                "approval_workflow": self.governance_enabled,
            },
        }

        return enhanced_info

    def _generate_insider_dealing_specifics(
        self,
        risk_result: Dict[str, Any],
        evidence: Dict[str, Any],
        explanation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate insider dealing specific analysis."""

        return {
            "regulatory_elements": {
                "material_information_present": evidence.get("MaterialInfo", 0) >= 1,
                "trading_activity_suspicious": evidence.get("TradingActivity", 0) >= 1,
                "timing_correlation_strong": evidence.get("Timing", 0) >= 1,
                "mar_article_14_compliance": self._check_mar_compliance(evidence),
            },
            "risk_factors": {
                "primary_risk_factors": self._identify_primary_risk_factors(evidence),
                "supporting_evidence": self._identify_supporting_evidence(evidence),
                "mitigating_factors": self._identify_mitigating_factors(evidence),
            },
            "regulatory_assessment": {
                "prosecution_likelihood": self._assess_prosecution_likelihood(
                    risk_result, evidence
                ),
                "regulatory_action_probability": self._assess_regulatory_action_probability(
                    risk_result
                ),
                "compliance_recommendation": self._generate_compliance_recommendation(
                    risk_result, evidence
                ),
            },
        }

    def _calculate_regulatory_compliance_score(self, evidence: Dict[str, Any]) -> float:
        """Calculate regulatory compliance score."""

        material_info = evidence.get("MaterialInfo", 0) >= 1
        trading_activity = evidence.get("TradingActivity", 0) >= 1
        timing = evidence.get("Timing", 0) >= 1

        compliance_elements = [material_info, trading_activity, timing]
        return sum(compliance_elements) / len(compliance_elements)

    def _identify_key_evidence(self, evidence: Dict[str, Any]) -> List[str]:
        """Identify key evidence factors."""

        key_evidence = []

        if evidence.get("MaterialInfo", 0) >= 2:
            key_evidence.append("Clear access to material information")
        elif evidence.get("MaterialInfo", 0) >= 1:
            key_evidence.append("Potential access to material information")

        if evidence.get("TradingActivity", 0) >= 2:
            key_evidence.append("Highly unusual trading patterns")
        elif evidence.get("TradingActivity", 0) >= 1:
            key_evidence.append("Unusual trading activity")

        if evidence.get("Timing", 0) >= 2:
            key_evidence.append("Strong timing correlation with material events")
        elif evidence.get("Timing", 0) >= 1:
            key_evidence.append("Moderate timing correlation")

        return key_evidence

    def _generate_regulatory_rationale(
        self, evidence: Dict[str, Any], risk_score: float
    ) -> str:
        """Generate regulatory rationale for the decision."""

        if risk_score >= 0.8:
            return (
                "High probability of insider dealing based on strong evidence of material information "
                "access, suspicious trading patterns, and timing correlation with material events. "
                "Immediate regulatory investigation recommended."
            )
        elif risk_score >= 0.6:
            return (
                "Moderate probability of insider dealing with some concerning indicators. "
                "Enhanced monitoring and further investigation recommended."
            )
        elif risk_score >= 0.3:
            return (
                "Low to moderate probability of insider dealing with limited indicators. "
                "Continued monitoring recommended."
            )
        else:
            return (
                "No significant indicators of insider dealing detected. "
                "Continue routine surveillance."
            )

    def _check_mar_compliance(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Check MAR Article 14 compliance elements."""

        return {
            "article_14_elements": {
                "inside_information": evidence.get("MaterialInfo", 0) >= 1,
                "precise_nature": True,  # Assumed for demonstration
                "not_public": True,  # Assumed for demonstration
                "price_sensitive": (
                    evidence.get("PriceImpact", 0) >= 1
                    if "PriceImpact" in evidence
                    else True
                ),
            },
            "compliance_met": all(
                [
                    evidence.get("MaterialInfo", 0) >= 1,
                    evidence.get("TradingActivity", 0) >= 1,
                    evidence.get("Timing", 0) >= 1,
                ]
            ),
        }

    def _identify_primary_risk_factors(self, evidence: Dict[str, Any]) -> List[str]:
        """Identify primary risk factors."""

        primary_factors = []

        if evidence.get("MaterialInfo", 0) >= 2:
            primary_factors.append("Clear access to material non-public information")

        if evidence.get("TradingActivity", 0) >= 2:
            primary_factors.append("Highly unusual trading patterns")

        if evidence.get("Timing", 0) >= 2:
            primary_factors.append("Strong timing correlation with material events")

        return primary_factors

    def _identify_supporting_evidence(self, evidence: Dict[str, Any]) -> List[str]:
        """Identify supporting evidence."""

        supporting = []

        if evidence.get("PriceImpact", 0) >= 1:
            supporting.append("Significant price impact from trading")

        if evidence.get("VolumeAnomaly", 0) >= 1:
            supporting.append("Unusual trading volume")

        return supporting

    def _identify_mitigating_factors(self, evidence: Dict[str, Any]) -> List[str]:
        """Identify mitigating factors."""

        mitigating = []

        if evidence.get("MaterialInfo", 0) == 0:
            mitigating.append("No clear access to material information")

        if evidence.get("TradingActivity", 0) == 0:
            mitigating.append("Normal trading patterns")

        if evidence.get("Timing", 0) == 0:
            mitigating.append("Poor timing correlation")

        return mitigating

    def _assess_prosecution_likelihood(
        self, risk_result: Dict[str, Any], evidence: Dict[str, Any]
    ) -> str:
        """Assess likelihood of successful prosecution."""

        risk_score = risk_result.get("risk_scores", {}).get("overall_score", 0.0)
        compliance_score = self._calculate_regulatory_compliance_score(evidence)

        if risk_score >= 0.8 and compliance_score >= 0.8:
            return "High - Strong evidence supporting prosecution"
        elif risk_score >= 0.6 and compliance_score >= 0.6:
            return "Medium - Moderate evidence, additional investigation recommended"
        else:
            return "Low - Insufficient evidence for prosecution"

    def _assess_regulatory_action_probability(self, risk_result: Dict[str, Any]) -> str:
        """Assess probability of regulatory action."""

        risk_score = risk_result.get("risk_scores", {}).get("overall_score", 0.0)

        if risk_score >= 0.7:
            return "High - Regulatory action likely"
        elif risk_score >= 0.5:
            return "Medium - Regulatory scrutiny expected"
        else:
            return "Low - Routine monitoring sufficient"

    def _generate_compliance_recommendation(
        self, risk_result: Dict[str, Any], evidence: Dict[str, Any]
    ) -> str:
        """Generate compliance recommendation."""

        risk_score = risk_result.get("risk_scores", {}).get("overall_score", 0.0)

        if risk_score >= 0.8:
            return (
                "Immediate action required: File suspicious transaction report (STR), "
                "conduct internal investigation, preserve evidence, consider trade restrictions."
            )
        elif risk_score >= 0.6:
            return (
                "Enhanced monitoring required: Increase surveillance frequency, "
                "gather additional evidence, prepare preliminary documentation."
            )
        elif risk_score >= 0.3:
            return (
                "Continued monitoring: Maintain current surveillance level, "
                "document rationale for no immediate action."
            )
        else:
            return "Routine monitoring: Continue standard surveillance procedures."


# Convenience function for creating enhanced insider dealing model
def create_enhanced_insider_dealing_model(
    use_latent_intent: bool = False, config: Optional[Dict[str, Any]] = None
) -> EnhancedInsiderDealingModel:
    """
    Create an enhanced insider dealing model with full explainability features.

    Args:
        use_latent_intent: Whether to use latent intent modeling
        config: Optional model configuration

    Returns:
        Enhanced insider dealing model instance
    """
    return EnhancedInsiderDealingModel(use_latent_intent, config)
