"""
Node Library for Kor.ai Bayesian Risk Engine
Reusable node classes, templates, and CPT logic for Bayesian Network construction.
"""

from typing import Any, Dict, List, Optional

import numpy as np


class BayesianNode:
    """
    Base class for a Bayesian Network node.
    """

    def __init__(
        self,
        name: str,
        states: List[str],
        cpt: Optional[Dict] = None,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        self.name = name
        self.states = states
        self.cpt = cpt or {}
        self.description = description
        self.fallback_prior = fallback_prior or [1.0 / len(states)] * len(states)

    def set_cpt(self, cpt: Dict):
        self.cpt = cpt

    def get_cpt(self) -> Dict:
        return self.cpt

    def get_fallback_prior(self) -> List[float]:
        return self.fallback_prior

    def explain(self) -> str:
        return f"Node: {self.name}\nDescription: {self.description}\nStates: {self.states}\nFallback Prior: {self.fallback_prior}"


class EvidenceNode(BayesianNode):
    """
    Node representing an evidence variable (input from data/events).
    """

    def __init__(
        self,
        name: str,
        states: List[str],
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        super().__init__(
            name,
            states,
            cpt=None,
            description=description,
            fallback_prior=fallback_prior,
        )


class RiskFactorNode(BayesianNode):
    """
    Node representing a risk factor (intermediate or latent variable).
    """

    def __init__(
        self,
        name: str,
        states: List[str],
        cpt: Optional[Dict] = None,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        super().__init__(
            name,
            states,
            cpt=cpt,
            description=description,
            fallback_prior=fallback_prior,
        )


class OutcomeNode(BayesianNode):
    """
    Node representing the outcome (e.g., Insider Dealing, Spoofing, etc.).
    """

    def __init__(
        self,
        name: str,
        states: List[str],
        cpt: Optional[Dict] = None,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        super().__init__(
            name,
            states,
            cpt=cpt,
            description=description,
            fallback_prior=fallback_prior,
        )


# Example: Template for a comms intent node (specialized evidence node)
class CommsIntentNode(EvidenceNode):
    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["benign", "suspicious", "malicious"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


# Example: Variance-tuned indicator node (for EM-based learning)
class VarianceTunedIndicatorNode(EvidenceNode):
    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal", "anomalous"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


# NEW: Latent Intent Nodes for Hidden Causality Modeling
class LatentIntentNode(BayesianNode):
    """
    Node representing latent intent (unobservable core abusive intent).
    This is the key innovation for modeling hidden causality.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["no_intent", "potential_intent", "clear_intent"]
        super().__init__(
            name,
            states,
            cpt=None,
            description=description,
            fallback_prior=fallback_prior,
        )

    def get_intent_strength(self, evidence_values: Dict[str, Any]) -> float:
        """
        Calculate intent strength based on converging evidence paths.
        This implements the Kor.ai approach of inferring latent intent.
        """
        # Default implementation - should be overridden with domain-specific logic
        return 0.5


class ProfitMotivationNode(EvidenceNode):
    """
    Node representing profit motivation evidence (PnL drift, profit patterns).
    One of the converging evidence paths for latent intent inference.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_profit", "unusual_profit", "suspicious_profit"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class AccessPatternNode(EvidenceNode):
    """
    Node representing access pattern evidence (information access, timing).
    One of the converging evidence paths for latent intent inference.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_access", "unusual_access", "suspicious_access"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class OrderBehaviorNode(EvidenceNode):
    """
    Node representing order behavior evidence (order patterns, timing).
    One of the converging evidence paths for latent intent inference.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_behavior", "unusual_behavior", "suspicious_behavior"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class CommsMetadataNode(EvidenceNode):
    """
    Node representing communications metadata evidence.
    One of the converging evidence paths for latent intent inference.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_comms", "unusual_comms", "suspicious_comms"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


# NEW: Enhanced nodes for insider dealing model
class NewsTimingNode(EvidenceNode):
    """
    Node representing news-trade timing analysis evidence.
    Detects suspicious timing patterns between trades and market-moving announcements.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_timing", "suspicious_timing", "highly_suspicious_timing"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class StateInformationNode(EvidenceNode):
    """
    Node representing state-level information access evidence.
    Detects access to material non-public information from government or state sources.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["no_access", "potential_access", "clear_access"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class AnnouncementCorrelationNode(EvidenceNode):
    """
    Node representing trading correlation with government/regulatory announcements.
    Analyzes statistical correlation between trading patterns and public announcements.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["no_correlation", "weak_correlation", "strong_correlation"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


# Utility for CPT normalization


def normalize_cpt(cpt: Dict[str, List[float]]) -> Dict[str, List[float]]:
    norm_cpt = {}
    for k, v in cpt.items():
        total = sum(v)
        norm_cpt[k] = [x / total if total > 0 else 1.0 / len(v) for x in v]
    return norm_cpt


# NEW: Commodity Manipulation Model nodes
class LiquidityContextNode(EvidenceNode):
    """
    Node representing market liquidity conditions evidence.
    Analyzes market depth, spread, and trading activity to assess liquidity.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["liquid", "moderate", "illiquid"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class BenchmarkTimingNode(EvidenceNode):
    """
    Node representing benchmark window timing evidence.
    Detects suspicious trading activity around benchmark fixing windows.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["outside_window", "near_window", "during_window"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class OrderClusteringNode(EvidenceNode):
    """
    Node representing order clustering analysis evidence.
    Detects unusual concentration of orders in time or price.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_distribution", "moderate_clustering", "high_clustering"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class PriceImpactRatioNode(EvidenceNode):
    """
    Node representing price impact ratio evidence.
    Analyzes the relationship between order size and price movement.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_impact", "elevated_impact", "excessive_impact"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class VolumeParticipationNode(EvidenceNode):
    """
    Node representing volume participation evidence.
    Analyzes the proportion of trading volume during specific periods.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = [
            "normal_participation",
            "high_participation",
            "dominant_participation",
        ]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class CrossVenueCoordinationNode(EvidenceNode):
    """
    Node representing cross-venue coordination evidence.
    Detects coordinated trading patterns across multiple venues.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["no_coordination", "weak_coordination", "strong_coordination"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class ManipulationLatentIntentNode(LatentIntentNode):
    """
    Node representing latent manipulation intent for commodity markets.
    Infers hidden intent to manipulate commodity prices from converging evidence.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        super().__init__(name, description=description, fallback_prior=fallback_prior)

    def get_intent_strength(self, evidence_values: Dict[str, Any]) -> float:
        """
        Calculate manipulation intent strength based on commodity-specific evidence.
        """
        # Commodity-specific logic for intent inference
        strength = 0.0

        # Weight evidence from different sources
        weights = {
            "liquidity_context": 0.15,
            "benchmark_timing": 0.25,
            "order_clustering": 0.20,
            "price_impact_ratio": 0.20,
            "volume_participation": 0.15,
            "cross_venue_coordination": 0.05,
        }

        for evidence_name, weight in weights.items():
            if evidence_name in evidence_values:
                evidence_value = evidence_values[evidence_name]
                if isinstance(evidence_value, (int, float)):
                    strength += weight * evidence_value

        return min(strength, 1.0)


# NEW: Circular Trading Detection Model nodes
class CounterpartyRelationshipNode(EvidenceNode):
    """
    Node representing counterparty relationship evidence.
    Analyzes relationships between trading counterparties to detect coordinated activities.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["unrelated", "connected", "closely_related"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class RiskTransferAnalysisNode(EvidenceNode):
    """
    Node representing risk transfer analysis evidence.
    Detects whether trades actually transfer economic risk between counterparties.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["genuine_transfer", "limited_transfer", "no_transfer"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class PriceNegotiationPatternNode(EvidenceNode):
    """
    Node representing price negotiation pattern evidence.
    Analyzes pricing patterns to detect artificial or coordinated pricing.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["market_driven", "coordinated", "artificial"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class SettlementCoordinationNode(EvidenceNode):
    """
    Node representing settlement coordination evidence.
    Detects coordination in settlement timing and methods between counterparties.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["independent", "synchronized", "coordinated"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class BeneficialOwnershipNode(EvidenceNode):
    """
    Node representing beneficial ownership evidence.
    Analyzes ultimate beneficial ownership to detect hidden relationships.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["separate_ownership", "shared_interests", "common_ownership"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class TradeSequenceAnalysisNode(EvidenceNode):
    """
    Node representing trade sequence analysis evidence.
    Detects patterns in trade sequences that indicate circular or wash trading.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["random_sequence", "structured_sequence", "circular_sequence"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class CoordinationLatentIntentNode(LatentIntentNode):
    """
    Node representing latent coordination intent for circular trading.
    Infers hidden intent to engage in circular or wash trading from converging evidence.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        super().__init__(name, description=description, fallback_prior=fallback_prior)

    def get_intent_strength(self, evidence_values: Dict[str, Any]) -> float:
        """
        Calculate coordination intent strength based on circular trading evidence.
        """
        # Circular trading specific logic for intent inference
        strength = 0.0

        # Weight evidence from different sources
        weights = {
            "counterparty_relationship": 0.20,
            "risk_transfer_analysis": 0.25,
            "price_negotiation_pattern": 0.15,
            "settlement_coordination": 0.15,
            "beneficial_ownership": 0.15,
            "trade_sequence_analysis": 0.10,
        }

        for evidence_name, weight in weights.items():
            if evidence_name in evidence_values:
                evidence_value = evidence_values[evidence_name]
                if isinstance(evidence_value, (int, float)):
                    strength += weight * evidence_value

        return min(strength, 1.0)


# NEW: Phase 4 Market Cornering Detection Model nodes
class MarketConcentrationNode(EvidenceNode):
    """
    Node representing market concentration evidence.
    Analyzes the concentration of market share to detect potential cornering activities.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["dispersed", "concentrated", "highly_concentrated"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class PositionAccumulationNode(EvidenceNode):
    """
    Node representing position accumulation pattern evidence.
    Detects systematic accumulation of positions that may indicate cornering strategies.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = [
            "normal_accumulation",
            "systematic_accumulation",
            "aggressive_accumulation",
        ]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class SupplyControlNode(EvidenceNode):
    """
    Node representing supply control evidence.
    Analyzes the degree of control over available supply which is key to market cornering.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["limited_control", "significant_control", "dominant_control"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class LiquidityManipulationNode(EvidenceNode):
    """
    Node representing liquidity manipulation evidence.
    Detects manipulation of market liquidity as part of cornering strategies.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_liquidity", "constrained_liquidity", "manipulated_liquidity"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class PriceDistortionNode(EvidenceNode):
    """
    Node representing price distortion evidence.
    Measures the extent of price distortion from fair value indicating market cornering.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["fair_pricing", "moderate_distortion", "extreme_distortion"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class DeliveryConstraintNode(EvidenceNode):
    """
    Node representing delivery constraint evidence.
    Analyzes delivery and settlement constraints that may be exploited in cornering.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_delivery", "constrained_delivery", "blocked_delivery"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class CorneringLatentIntentNode(LatentIntentNode):
    """
    Node representing latent cornering intent.
    Infers hidden intent to corner a market from converging evidence patterns.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        super().__init__(name, description=description, fallback_prior=fallback_prior)

    def get_intent_strength(self, evidence_values: Dict[str, Any]) -> float:
        """
        Calculate cornering intent strength based on market cornering evidence.
        """
        # Market cornering specific logic for intent inference
        strength = 0.0

        # Weight evidence from different sources
        weights = {
            "market_concentration": 0.18,
            "position_accumulation": 0.18,
            "supply_control": 0.25,  # Highest weight - key to cornering
            "liquidity_manipulation": 0.16,
            "price_distortion": 0.16,
            "delivery_constraint": 0.07,
        }

        for evidence_name, weight in weights.items():
            if evidence_name in evidence_values:
                evidence_value = evidence_values[evidence_name]
                if isinstance(evidence_value, (int, float)):
                    strength += weight * evidence_value

        return min(strength, 1.0)


# NEW: Qatar Energy & Commodity Market Abuse Detection Nodes


class MarketSegmentationNode(EvidenceNode):
    """
    Node representing market division patterns between trading desks.
    Detects coordinated market segmentation that may indicate collusive behavior.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["competitive", "segmented", "coordinated_division"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class CollusionLatentIntentNode(LatentIntentNode):
    """
    Node representing latent collusion intent across trading desks.
    Infers hidden intent to engage in collusive behavior from converging evidence.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["independent_trading", "coordinated_trading", "collusive_trading"]
        super().__init__(name, description=description, fallback_prior=fallback_prior)

    def get_intent_strength(self, evidence_values: Dict[str, Any]) -> float:
        """
        Calculate collusion intent strength based on cross-desk evidence.
        """
        # Cross-desk collusion specific logic for intent inference
        strength = 0.0

        # Weight evidence from different sources
        weights = {
            "comms_metadata": 0.20,  # Communication patterns
            "profit_motivation": 0.18,  # Unusual profit sharing
            "order_behavior": 0.18,  # Order synchronization
            "cross_venue_coordination": 0.15,  # Trading correlation
            "access_pattern": 0.15,  # Information sharing
            "market_segmentation": 0.14,  # Market division
        }

        for evidence_name, weight in weights.items():
            if evidence_name in evidence_values:
                evidence_value = evidence_values[evidence_name]
                if isinstance(evidence_value, (int, float)):
                    strength += weight * evidence_value

        return min(strength, 1.0)


class IntentToExecuteNode(EvidenceNode):
    """
    Node representing analysis of genuine intent to execute orders.
    Detects whether orders are placed with genuine intent to execute or to manipulate.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["genuine_intent", "uncertain_intent", "no_intent"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class OrderCancellationNode(EvidenceNode):
    """
    Node representing order cancellation pattern analysis.
    Detects suspicious order cancellation patterns that may indicate spoofing.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = [
            "normal_cancellation",
            "suspicious_cancellation",
            "manipulative_cancellation",
        ]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class SpoofingLatentIntentNode(LatentIntentNode):
    """
    Node representing latent spoofing intent.
    Infers hidden intent to engage in spoofing behavior from converging evidence.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["legitimate_trading", "potential_spoofing", "clear_spoofing"]
        super().__init__(name, description=description, fallback_prior=fallback_prior)

    def get_intent_strength(self, evidence_values: Dict[str, Any]) -> float:
        """
        Calculate spoofing intent strength based on order behavior evidence.
        """
        # Spoofing specific logic for intent inference
        strength = 0.0

        # Weight evidence from different sources
        weights = {
            "order_clustering": 0.22,  # Layering patterns
            "price_impact_ratio": 0.20,  # Market impact
            "volume_participation": 0.18,  # Volume effects
            "order_behavior": 0.18,  # Order behavior
            "intent_to_execute": 0.12,  # Execution intent
            "order_cancellation": 0.10,  # Cancellation patterns
        }

        for evidence_name, weight in weights.items():
            if evidence_name in evidence_values:
                evidence_value = evidence_values[evidence_name]
                if isinstance(evidence_value, (int, float)):
                    strength += weight * evidence_value

        return min(strength, 1.0)
