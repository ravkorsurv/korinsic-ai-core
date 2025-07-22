"""
Regulatory Explainability Module

Converts soft probabilities into deterministic narratives suitable for regulatory compliance.
Provides structured inference paths, rationale attachment, STOR-ready exports, and VOI/sensitivity reporting.
"""

import csv
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class InferencePath:
    """Represents a structured inference path from evidence to conclusion"""

    evidence_node: str
    evidence_state: str
    evidence_weight: float
    inference_rule: str
    conclusion_impact: str
    confidence_level: str


@dataclass
class RegulatoryRationale:
    """Structured rationale for regulatory compliance"""

    alert_id: str
    timestamp: str
    risk_level: str
    overall_score: float
    deterministic_narrative: str
    inference_paths: List[InferencePath]
    key_evidence: Dict[str, Any]
    regulatory_basis: str
    audit_trail: List[str]


@dataclass
class STORRecord:
    """STOR (Suspicious Transaction Order Report) record format"""

    record_id: str
    timestamp: str
    entity_id: str
    transaction_type: str
    risk_score: float
    risk_level: str
    narrative: str
    evidence_summary: str
    regulatory_basis: str


class RegulatoryExplainability:
    """
    Converts probabilistic Bayesian outputs into deterministic regulatory narratives
    """

    def __init__(self):
        self.risk_thresholds = {"low": 0.3, "medium": 0.6, "high": 0.8}

        self.regulatory_basis_map = {
            "insider_dealing": "Market Abuse Regulation (MAR) Article 14",
            "spoofing": "MiFID II Article 48 - Market manipulation",
            "market_manipulation": "MAR Article 12 - Market manipulation",
        }

    def generate_regulatory_rationale(
        self,
        alert_id: str,
        risk_result: Dict[str, Any],
        evidence_factors: Dict[str, Any],
        model_type: str = "insider_dealing",
    ) -> RegulatoryRationale:
        """
        Generate structured regulatory rationale from Bayesian risk assessment
        """
        try:
            # Extract key information
            overall_score = risk_result.get("risk_score", 0.0)
            risk_level = self._determine_risk_level(overall_score)

            # Generate deterministic narrative
            narrative = self._generate_deterministic_narrative(
                risk_result, evidence_factors, model_type
            )

            # Build inference paths
            inference_paths = self._build_inference_paths(evidence_factors, risk_result)

            # Identify key evidence
            key_evidence = self._identify_key_evidence(evidence_factors, risk_result)

            # Get regulatory basis
            regulatory_basis = self.regulatory_basis_map.get(
                model_type, "General market abuse regulations"
            )

            # Create audit trail
            audit_trail = self._create_audit_trail(risk_result, evidence_factors)

            return RegulatoryRationale(
                alert_id=alert_id,
                timestamp=datetime.now().isoformat(),
                risk_level=risk_level,
                overall_score=overall_score,
                deterministic_narrative=narrative,
                inference_paths=inference_paths,
                key_evidence=key_evidence,
                regulatory_basis=regulatory_basis,
                audit_trail=audit_trail,
            )

        except Exception as e:
            logger.error(f"Error generating regulatory rationale: {str(e)}")
            # Return fallback rationale
            return self._create_fallback_rationale(alert_id, risk_result, model_type)

    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on score"""
        if score >= self.risk_thresholds["high"]:
            return "high"
        elif score >= self.risk_thresholds["medium"]:
            return "medium"
        else:
            return "low"

    def _generate_deterministic_narrative(
        self,
        risk_result: Dict[str, Any],
        evidence_factors: Dict[str, Any],
        model_type: str,
    ) -> str:
        """Convert probabilistic assessment into deterministic narrative"""

        if model_type == "insider_dealing":
            return self._generate_insider_dealing_narrative(
                risk_result, evidence_factors
            )
        elif model_type == "spoofing":
            return self._generate_spoofing_narrative(risk_result, evidence_factors)
        else:
            return self._generate_general_narrative(risk_result, evidence_factors)

    def _generate_insider_dealing_narrative(
        self, risk_result: Dict[str, Any], evidence_factors: Dict[str, Any]
    ) -> str:
        """Generate insider dealing specific narrative"""

        material_info = evidence_factors.get("MaterialInfo", 0)
        trading_activity = evidence_factors.get("TradingActivity", 0)
        timing = evidence_factors.get("Timing", 0)
        price_impact = evidence_factors.get("PriceImpact", 0)

        narrative_parts = []

        # Material information access
        if material_info == 2:
            narrative_parts.append("Clear access to material non-public information")
        elif material_info == 1:
            narrative_parts.append("Potential access to material information")

        # Trading activity
        if trading_activity == 2:
            narrative_parts.append("highly unusual trading patterns")
        elif trading_activity == 1:
            narrative_parts.append("unusual trading activity")

        # Timing
        if timing == 2:
            narrative_parts.append("suspicious timing relative to material events")
        elif timing == 1:
            narrative_parts.append("questionable timing")

        # Price impact
        if price_impact == 2:
            narrative_parts.append("significant price impact")
        elif price_impact == 1:
            narrative_parts.append("moderate price impact")

        if narrative_parts:
            return f"Detected potential insider dealing based on {' and '.join(narrative_parts)}."
        else:
            return "No significant insider dealing indicators detected."

    def _generate_spoofing_narrative(
        self, risk_result: Dict[str, Any], evidence_factors: Dict[str, Any]
    ) -> str:
        """Generate spoofing specific narrative"""

        order_pattern = evidence_factors.get("OrderPattern", 0)
        cancellation_rate = evidence_factors.get("CancellationRate", 0)
        price_movement = evidence_factors.get("PriceMovement", 0)
        volume_ratio = evidence_factors.get("VolumeRatio", 0)

        narrative_parts = []

        if order_pattern == 2:
            narrative_parts.append("manipulative order patterns")
        elif order_pattern == 1:
            narrative_parts.append("suspicious order behavior")

        if cancellation_rate == 2:
            narrative_parts.append("excessive order cancellations")
        elif cancellation_rate == 1:
            narrative_parts.append("unusual cancellation patterns")

        if price_movement == 2:
            narrative_parts.append("artificial price movements")
        elif price_movement == 1:
            narrative_parts.append("suspicious price activity")

        if volume_ratio == 2:
            narrative_parts.append("manipulative volume patterns")
        elif volume_ratio == 1:
            narrative_parts.append("unusual volume activity")

        if narrative_parts:
            return (
                f"Detected potential spoofing based on {' and '.join(narrative_parts)}."
            )
        else:
            return "No significant spoofing indicators detected."

    def _generate_general_narrative(
        self, risk_result: Dict[str, Any], evidence_factors: Dict[str, Any]
    ) -> str:
        """Generate general market abuse narrative"""

        risk_score = risk_result.get("risk_score", 0.0)

        if risk_score >= 0.8:
            return "High risk of market abuse detected based on multiple suspicious indicators."
        elif risk_score >= 0.6:
            return "Medium risk of market abuse detected based on several concerning factors."
        elif risk_score >= 0.3:
            return "Low risk of market abuse detected with some unusual patterns."
        else:
            return "No significant market abuse indicators detected."

    def _build_inference_paths(
        self, evidence_factors: Dict[str, Any], risk_result: Dict[str, Any]
    ) -> List[InferencePath]:
        """Build structured inference paths from evidence to conclusion"""

        paths = []

        for factor, state in evidence_factors.items():
            if isinstance(state, (int, float)) and state > 0:
                weight = self._calculate_evidence_weight(factor, state)
                rule = self._get_inference_rule(factor, state)
                impact = self._get_conclusion_impact(factor, state)
                confidence = self._get_confidence_level(state)

                paths.append(
                    InferencePath(
                        evidence_node=factor,
                        evidence_state=str(state),
                        evidence_weight=weight,
                        inference_rule=rule,
                        conclusion_impact=impact,
                        confidence_level=confidence,
                    )
                )

        return paths

    def _calculate_evidence_weight(self, factor: str, state: int) -> float:
        """Calculate evidence weight based on factor and state"""
        base_weights = {
            "MaterialInfo": 0.4,
            "TradingActivity": 0.3,
            "Timing": 0.2,
            "PriceImpact": 0.1,
            "OrderPattern": 0.35,
            "CancellationRate": 0.25,
            "PriceMovement": 0.2,
            "VolumeRatio": 0.2,
        }

        base_weight = base_weights.get(factor, 0.1)
        state_multiplier = state / 2.0  # Normalize to 0-1 range

        return base_weight * state_multiplier

    def _get_inference_rule(self, factor: str, state: int) -> str:
        """Get inference rule description"""
        rules = {
            "MaterialInfo": "Material information access assessment",
            "TradingActivity": "Trading pattern analysis",
            "Timing": "Temporal correlation analysis",
            "PriceImpact": "Price impact evaluation",
            "OrderPattern": "Order pattern analysis",
            "CancellationRate": "Cancellation behavior assessment",
            "PriceMovement": "Price movement analysis",
            "VolumeRatio": "Volume pattern evaluation",
        }

        return rules.get(factor, "General factor analysis")

    def _get_conclusion_impact(self, factor: str, state: int) -> str:
        """Get conclusion impact description"""
        if state == 2:
            return "High impact on risk assessment"
        elif state == 1:
            return "Moderate impact on risk assessment"
        else:
            return "Low impact on risk assessment"

    def _get_confidence_level(self, state: int) -> str:
        """Get confidence level based on state"""
        if state == 2:
            return "High"
        elif state == 1:
            return "Medium"
        else:
            return "Low"

    def _identify_key_evidence(
        self, evidence_factors: Dict[str, Any], risk_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify key evidence factors"""

        key_evidence = {}

        for factor, state in evidence_factors.items():
            if isinstance(state, (int, float)) and state > 0:
                weight = self._calculate_evidence_weight(factor, state)
                if weight > 0.1:  # Only include significant evidence
                    key_evidence[factor] = {
                        "state": state,
                        "weight": weight,
                        "significance": (
                            "High"
                            if weight > 0.2
                            else "Medium" if weight > 0.1 else "Low"
                        ),
                    }

        return key_evidence

    def _create_audit_trail(
        self, risk_result: Dict[str, Any], evidence_factors: Dict[str, Any]
    ) -> List[str]:
        """Create audit trail for regulatory compliance"""

        audit_trail = [
            f"Analysis timestamp: {datetime.now().isoformat()}",
            f"Risk score: {risk_result.get('risk_score', 0.0):.3f}",
            f"Evidence factors analyzed: {len(evidence_factors)}",
            f"Model type: {risk_result.get('model_type', 'unknown')}",
        ]

        for factor, state in evidence_factors.items():
            if isinstance(state, (int, float)):
                audit_trail.append(f"Factor {factor}: state {state}")

        return audit_trail

    def _create_fallback_rationale(
        self, alert_id: str, risk_result: Dict[str, Any], model_type: str
    ) -> RegulatoryRationale:
        """Create fallback rationale when analysis fails"""

        return RegulatoryRationale(
            alert_id=alert_id,
            timestamp=datetime.now().isoformat(),
            risk_level="unknown",
            overall_score=0.0,
            deterministic_narrative="Analysis failed - insufficient data for regulatory assessment",
            inference_paths=[],
            key_evidence={},
            regulatory_basis=self.regulatory_basis_map.get(
                model_type, "General market abuse regulations"
            ),
            audit_trail=["Analysis failed due to insufficient data"],
        )

    def generate_voi_analysis(self, evidence_factors: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Value of Information (VOI) analysis"""

        voi_results = {}

        for factor in evidence_factors.keys():
            # Calculate potential information value
            base_uncertainty = 0.5  # Assume base uncertainty
            potential_reduction = 0.3  # Assume 30% uncertainty reduction

            voi_results[factor] = {
                "current_value": evidence_factors.get(factor, 0),
                "potential_uncertainty_reduction": potential_reduction,
                "information_value": base_uncertainty * potential_reduction,
                "recommendation": (
                    "Collect additional data"
                    if evidence_factors.get(factor, 0) == 0
                    else "Sufficient data available"
                ),
            }

        return voi_results

    def generate_sensitivity_report(
        self, risk_result: Dict[str, Any], evidence_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate sensitivity analysis report"""

        base_score = risk_result.get("risk_score", 0.0)
        sensitivity_results = {}

        for factor, state in evidence_factors.items():
            if isinstance(state, (int, float)):
                # Simulate impact of changing evidence state
                if state > 0:
                    # Impact of reducing evidence
                    reduced_score = max(0.0, base_score - 0.1)
                    # Impact of increasing evidence
                    increased_score = min(1.0, base_score + 0.1)

                    sensitivity_results[factor] = {
                        "current_state": state,
                        "current_impact": base_score,
                        "reduced_impact": reduced_score,
                        "increased_impact": increased_score,
                        "sensitivity": (
                            "High"
                            if abs(increased_score - reduced_score) > 0.15
                            else "Medium"
                        ),
                    }

        return sensitivity_results

    def export_stor_format(self, rationale: RegulatoryRationale) -> STORRecord:
        """Export rationale to STOR format"""

        return STORRecord(
            record_id=rationale.alert_id,
            timestamp=rationale.timestamp,
            entity_id="ENTITY_ID",  # Would be populated from actual data
            transaction_type="SUSPICIOUS_TRANSACTION",
            risk_score=rationale.overall_score,
            risk_level=rationale.risk_level,
            narrative=rationale.deterministic_narrative,
            evidence_summary=json.dumps(rationale.key_evidence),
            regulatory_basis=rationale.regulatory_basis,
        )

    def export_csv_format(self, rationale: RegulatoryRationale) -> str:
        """Export rationale to CSV format"""

        output = []
        output.append("Alert ID,Timestamp,Risk Level,Score,Narrative,Regulatory Basis")
        output.append(
            f'{rationale.alert_id},{rationale.timestamp},{rationale.risk_level},{rationale.overall_score:.3f},"{rationale.deterministic_narrative}",{rationale.regulatory_basis}'
        )

        return "\n".join(output)
