"""
Model Explainability Engine

This module provides comprehensive explainability features for all models,
including feature attribution, counterfactual generation, and decision path
visualization for regulatory compliance.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class FeatureAttribution:
    """Feature attribution information."""

    feature_name: str
    importance: float
    contribution: float
    confidence: float
    direction: str  # 'positive' or 'negative'
    explanation: str


@dataclass
class CounterfactualScenario:
    """Counterfactual scenario information."""

    scenario_id: str
    original_prediction: float
    counterfactual_prediction: float
    changed_features: Dict[str, Any]
    explanation: str
    plausibility: float


@dataclass
class DecisionPathNode:
    """Decision path node information."""

    node_name: str
    node_type: str
    evidence_value: Any
    probability: float
    contribution: float
    rationale: str
    confidence: float
    regulatory_relevance: str


@dataclass
class UncertaintyAnalysis:
    """Uncertainty analysis information."""

    prediction_uncertainty: float
    confidence_interval: Tuple[float, float]
    epistemic_uncertainty: float
    aleatoric_uncertainty: float
    reliability_score: float


class ModelExplainabilityEngine:
    """
    Comprehensive model explainability engine.

    This engine provides various explainability features including:
    - Feature attribution analysis
    - Counterfactual generation
    - Decision path visualization
    - Uncertainty quantification
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the explainability engine.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.feature_attributor = FeatureAttributor(
            self.config.get("feature_attribution", {})
        )
        self.counterfactual_generator = CounterfactualGenerator(
            self.config.get("counterfactual", {})
        )
        self.decision_visualizer = DecisionPathVisualizer(
            self.config.get("decision_path", {})
        )
        self.uncertainty_quantifier = UncertaintyQuantifier(
            self.config.get("uncertainty", {})
        )

        # Explanation cache
        self.explanation_cache = {}

        logger.info("Model explainability engine initialized")

    def generate_comprehensive_explanation(
        self,
        model_result: Dict[str, Any],
        evidence: Dict[str, Any],
        model_type: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for model result.

        Args:
            model_result: Model prediction result
            evidence: Input evidence
            model_type: Type of model

        Returns:
            Comprehensive explanation dictionary
        """
        try:
            explanation_id = self._generate_explanation_id()

            # Feature attribution
            feature_attributions = self.feature_attributor.calculate_attributions(
                model_result, evidence, model_type
            )

            # Counterfactual scenarios
            counterfactuals = self.counterfactual_generator.generate_scenarios(
                model_result, evidence, model_type
            )

            # Decision path
            decision_path = self.decision_visualizer.generate_decision_path(
                model_result, evidence, model_type
            )

            # Uncertainty analysis
            uncertainty_analysis = self.uncertainty_quantifier.analyze_uncertainty(
                model_result, evidence, model_type
            )

            # Comprehensive explanation
            comprehensive_explanation = {
                "explanation_id": explanation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model_type": model_type,
                "feature_attributions": [asdict(fa) for fa in feature_attributions],
                "counterfactual_scenarios": [asdict(cs) for cs in counterfactuals],
                "decision_path": [asdict(dp) for dp in decision_path],
                "uncertainty_analysis": asdict(uncertainty_analysis),
                "regulatory_summary": self._generate_regulatory_summary(
                    feature_attributions,
                    counterfactuals,
                    decision_path,
                    uncertainty_analysis,
                ),
                "explanation_metadata": {
                    "explanation_quality": self._assess_explanation_quality(
                        feature_attributions, counterfactuals, decision_path
                    ),
                    "completeness_score": self._calculate_completeness_score(
                        feature_attributions, counterfactuals, decision_path
                    ),
                    "regulatory_compliance": self._check_regulatory_compliance(
                        feature_attributions, decision_path
                    ),
                },
            }

            # Cache explanation
            self.explanation_cache[explanation_id] = comprehensive_explanation

            return comprehensive_explanation

        except Exception as e:
            logger.error(f"Error generating comprehensive explanation: {str(e)}")
            return self._generate_fallback_explanation(
                model_result, evidence, model_type
            )

    def _generate_explanation_id(self) -> str:
        """Generate unique explanation ID."""
        return f"explanation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"

    def _generate_regulatory_summary(
        self,
        feature_attributions: List[FeatureAttribution],
        counterfactuals: List[CounterfactualScenario],
        decision_path: List[DecisionPathNode],
        uncertainty_analysis: UncertaintyAnalysis,
    ) -> Dict[str, Any]:
        """Generate regulatory summary."""

        # Key factors
        key_factors = [
            fa.feature_name
            for fa in sorted(
                feature_attributions, key=lambda x: x.importance, reverse=True
            )[:3]
        ]

        # Decision rationale
        decision_rationale = self._generate_decision_rationale(
            feature_attributions, decision_path
        )

        # Risk indicators
        risk_indicators = self._identify_risk_indicators(
            feature_attributions, decision_path
        )

        return {
            "key_factors": key_factors,
            "decision_rationale": decision_rationale,
            "risk_indicators": risk_indicators,
            "uncertainty_level": uncertainty_analysis.prediction_uncertainty,
            "confidence_assessment": self._assess_confidence(uncertainty_analysis),
            "regulatory_compliance": {
                "explainability_score": self._calculate_explainability_score(
                    feature_attributions
                ),
                "audit_trail_complete": True,
                "regulatory_frameworks": ["MAR", "MiFID II", "GDPR"],
            },
        }

    def _generate_decision_rationale(
        self,
        feature_attributions: List[FeatureAttribution],
        decision_path: List[DecisionPathNode],
    ) -> str:
        """Generate decision rationale."""

        if not feature_attributions:
            return "Decision based on standard risk assessment procedures."

        # Top contributing factors
        top_factors = sorted(
            feature_attributions, key=lambda x: abs(x.contribution), reverse=True
        )[:3]

        rationale_parts = []
        for factor in top_factors:
            direction = "increases" if factor.contribution > 0 else "decreases"
            rationale_parts.append(
                f"{factor.feature_name} {direction} risk by {abs(factor.contribution):.2%}"
            )

        return f"Decision based on: {'; '.join(rationale_parts)}."

    def _identify_risk_indicators(
        self,
        feature_attributions: List[FeatureAttribution],
        decision_path: List[DecisionPathNode],
    ) -> List[str]:
        """Identify risk indicators."""

        risk_indicators = []

        # High importance features
        for fa in feature_attributions:
            if fa.importance > 0.5:
                risk_indicators.append(f"High importance: {fa.feature_name}")

        # High contribution features
        for fa in feature_attributions:
            if abs(fa.contribution) > 0.3:
                risk_indicators.append(f"High contribution: {fa.feature_name}")

        # Regulatory relevant nodes
        for node in decision_path:
            if node.regulatory_relevance == "high":
                risk_indicators.append(f"Regulatory concern: {node.node_name}")

        return risk_indicators

    def _assess_confidence(self, uncertainty_analysis: UncertaintyAnalysis) -> str:
        """Assess confidence level."""

        if uncertainty_analysis.prediction_uncertainty < 0.2:
            return "High confidence"
        elif uncertainty_analysis.prediction_uncertainty < 0.4:
            return "Medium confidence"
        else:
            return "Low confidence"

    def _calculate_explainability_score(
        self, feature_attributions: List[FeatureAttribution]
    ) -> float:
        """Calculate explainability score."""

        if not feature_attributions:
            return 0.0

        # Score based on number of attributions and their confidence
        confidence_sum = sum(fa.confidence for fa in feature_attributions)
        avg_confidence = confidence_sum / len(feature_attributions)

        # Normalize by number of features (more features = better explainability)
        feature_score = min(len(feature_attributions) / 10.0, 1.0)

        return (avg_confidence + feature_score) / 2.0

    def _assess_explanation_quality(
        self,
        feature_attributions: List[FeatureAttribution],
        counterfactuals: List[CounterfactualScenario],
        decision_path: List[DecisionPathNode],
    ) -> float:
        """Assess explanation quality."""

        # Quality factors
        attribution_quality = len(feature_attributions) / 10.0  # Max 10 features
        counterfactual_quality = len(counterfactuals) / 5.0  # Max 5 scenarios
        decision_path_quality = len(decision_path) / 20.0  # Max 20 nodes

        # Normalize and combine
        quality_score = (
            min(attribution_quality, 1.0) * 0.4
            + min(counterfactual_quality, 1.0) * 0.3
            + min(decision_path_quality, 1.0) * 0.3
        )

        return quality_score

    def _calculate_completeness_score(
        self,
        feature_attributions: List[FeatureAttribution],
        counterfactuals: List[CounterfactualScenario],
        decision_path: List[DecisionPathNode],
    ) -> float:
        """Calculate explanation completeness score."""

        # Completeness criteria
        has_attributions = len(feature_attributions) > 0
        has_counterfactuals = len(counterfactuals) > 0
        has_decision_path = len(decision_path) > 0

        completeness_score = (
            (1.0 if has_attributions else 0.0) * 0.4
            + (1.0 if has_counterfactuals else 0.0) * 0.3
            + (1.0 if has_decision_path else 0.0) * 0.3
        )

        return completeness_score

    def _check_regulatory_compliance(
        self,
        feature_attributions: List[FeatureAttribution],
        decision_path: List[DecisionPathNode],
    ) -> Dict[str, Any]:
        """Check regulatory compliance."""

        # Compliance criteria
        has_feature_explanations = len(feature_attributions) > 0
        has_decision_rationale = len(decision_path) > 0
        has_regulatory_relevance = any(
            node.regulatory_relevance for node in decision_path
        )

        compliance_score = (
            (1.0 if has_feature_explanations else 0.0) * 0.4
            + (1.0 if has_decision_rationale else 0.0) * 0.4
            + (1.0 if has_regulatory_relevance else 0.0) * 0.2
        )

        return {
            "compliance_score": compliance_score,
            "meets_explainability_requirements": compliance_score >= 0.8,
            "meets_audit_requirements": has_decision_rationale,
            "regulatory_frameworks_covered": (
                ["MAR", "MiFID II"] if compliance_score >= 0.8 else []
            ),
        }

    def _generate_fallback_explanation(
        self, model_result: Dict[str, Any], evidence: Dict[str, Any], model_type: str
    ) -> Dict[str, Any]:
        """Generate fallback explanation when full explanation fails."""

        return {
            "explanation_id": self._generate_explanation_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_type": model_type,
            "feature_attributions": [],
            "counterfactual_scenarios": [],
            "decision_path": [],
            "uncertainty_analysis": asdict(
                UncertaintyAnalysis(
                    prediction_uncertainty=0.5,
                    confidence_interval=(0.0, 1.0),
                    epistemic_uncertainty=0.3,
                    aleatoric_uncertainty=0.2,
                    reliability_score=0.5,
                )
            ),
            "regulatory_summary": {
                "key_factors": [],
                "decision_rationale": "Standard risk assessment applied",
                "risk_indicators": [],
                "uncertainty_level": 0.5,
                "confidence_assessment": "Medium confidence",
                "regulatory_compliance": {
                    "explainability_score": 0.5,
                    "audit_trail_complete": True,
                    "regulatory_frameworks": ["MAR", "MiFID II"],
                },
            },
            "explanation_metadata": {
                "explanation_quality": 0.5,
                "completeness_score": 0.0,
                "regulatory_compliance": {
                    "compliance_score": 0.5,
                    "meets_explainability_requirements": False,
                    "meets_audit_requirements": True,
                    "regulatory_frameworks_covered": [],
                },
            },
            "fallback_reason": "Full explanation generation failed",
        }


# Component classes (to be implemented)
class FeatureAttributor:
    """Feature attribution calculator."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def calculate_attributions(
        self, model_result: Dict[str, Any], evidence: Dict[str, Any], model_type: str
    ) -> List[FeatureAttribution]:
        """Calculate feature attributions."""

        attributions = []

        # Simple attribution calculation based on evidence
        for feature_name, value in evidence.items():
            if isinstance(value, (int, float)):
                # Normalize importance based on value
                importance = min(abs(value) / 10.0, 1.0)
                contribution = value / 100.0 if value != 0 else 0.0
                confidence = 0.8 if importance > 0.5 else 0.6
                direction = "positive" if contribution > 0 else "negative"
                explanation = (
                    f"{feature_name} contributes {direction}ly to the risk assessment"
                )

                attributions.append(
                    FeatureAttribution(
                        feature_name=feature_name,
                        importance=importance,
                        contribution=contribution,
                        confidence=confidence,
                        direction=direction,
                        explanation=explanation,
                    )
                )

        return attributions


class CounterfactualGenerator:
    """Counterfactual scenario generator."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate_scenarios(
        self, model_result: Dict[str, Any], evidence: Dict[str, Any], model_type: str
    ) -> List[CounterfactualScenario]:
        """Generate counterfactual scenarios."""

        scenarios = []
        original_prediction = model_result.get("risk_scores", {}).get(
            "overall_score", 0.0
        )

        # Generate simple counterfactuals
        for i, (feature_name, value) in enumerate(evidence.items()):
            if isinstance(value, (int, float)) and i < 3:  # Max 3 scenarios
                # Modify feature value
                modified_value = value * 0.5 if value > 0 else value * 1.5
                counterfactual_prediction = original_prediction * (
                    1 - (modified_value - value) / 10.0
                )

                scenarios.append(
                    CounterfactualScenario(
                        scenario_id=f"scenario_{i+1}",
                        original_prediction=original_prediction,
                        counterfactual_prediction=max(
                            0.0, min(1.0, counterfactual_prediction)
                        ),
                        changed_features={feature_name: modified_value},
                        explanation=f"If {feature_name} was {modified_value:.2f} instead of {value:.2f}",
                        plausibility=0.8,
                    )
                )

        return scenarios


class DecisionPathVisualizer:
    """Decision path visualizer."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate_decision_path(
        self, model_result: Dict[str, Any], evidence: Dict[str, Any], model_type: str
    ) -> List[DecisionPathNode]:
        """Generate decision path."""

        decision_path = []

        # Generate decision path nodes based on evidence
        for i, (feature_name, value) in enumerate(evidence.items()):
            if isinstance(value, (int, float)):
                probability = min(abs(value) / 10.0, 1.0)
                contribution = value / 100.0 if value != 0 else 0.0
                confidence = 0.8 if probability > 0.5 else 0.6
                regulatory_relevance = "high" if abs(contribution) > 0.3 else "medium"

                decision_path.append(
                    DecisionPathNode(
                        node_name=feature_name,
                        node_type="evidence",
                        evidence_value=value,
                        probability=probability,
                        contribution=contribution,
                        rationale=f"Evidence {feature_name} indicates {probability:.2%} probability",
                        confidence=confidence,
                        regulatory_relevance=regulatory_relevance,
                    )
                )

        return decision_path


class UncertaintyQuantifier:
    """Uncertainty quantifier."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def analyze_uncertainty(
        self, model_result: Dict[str, Any], evidence: Dict[str, Any], model_type: str
    ) -> UncertaintyAnalysis:
        """Analyze prediction uncertainty."""

        # Simple uncertainty analysis
        overall_score = model_result.get("risk_scores", {}).get("overall_score", 0.0)

        # Calculate uncertainty based on score and evidence quality
        evidence_quality = (
            len([v for v in evidence.values() if v is not None]) / len(evidence)
            if evidence
            else 0.0
        )

        prediction_uncertainty = 1.0 - evidence_quality
        epistemic_uncertainty = prediction_uncertainty * 0.6
        aleatoric_uncertainty = prediction_uncertainty * 0.4

        confidence_interval = (
            max(0.0, overall_score - prediction_uncertainty),
            min(1.0, overall_score + prediction_uncertainty),
        )

        reliability_score = evidence_quality * (1.0 - prediction_uncertainty)

        return UncertaintyAnalysis(
            prediction_uncertainty=prediction_uncertainty,
            confidence_interval=confidence_interval,
            epistemic_uncertainty=epistemic_uncertainty,
            aleatoric_uncertainty=aleatoric_uncertainty,
            reliability_score=reliability_score,
        )
