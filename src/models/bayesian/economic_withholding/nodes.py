"""
Economic withholding model nodes definitions.

This module contains node definitions and helpers specific to the
economic withholding detection model for power markets.
"""

from typing import Any, Dict, List, Optional, Union

from core.node_library import (
    BayesianNode,
    EvidenceNode,
    LatentIntentNode,
    OutcomeNode,
    RiskFactorNode,
    # Reuse existing nodes
    PriceImpactRatioNode,
    VolumeParticipationNode,
    LiquidityContextNode,
    OrderClusteringNode,
    BenchmarkTimingNode,
    ProfitMotivationNode,
)


# NEW: Energy-specific evidence nodes
class FuelCostVarianceNode(EvidenceNode):
    """
    Node representing variance between declared fuel costs and market benchmarks.
    Detects inconsistencies in fuel cost declarations that may enable withholding.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["aligned", "moderate_variance", "high_variance"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class PlantEfficiencyNode(EvidenceNode):
    """
    Node representing plant operational efficiency compared to design specifications.
    Analyzes declared efficiency vs engineering benchmarks to detect artificial constraints.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["optimal", "suboptimal", "significantly_impaired"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class MarginalCostDeviationNode(EvidenceNode):
    """
    Node representing deviation of offers from calculated marginal costs.
    Core indicator for economic withholding - excessive markup over marginal cost.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["cost_reflective", "moderate_markup", "excessive_markup"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class HeatRateVarianceNode(EvidenceNode):
    """
    Node representing variance in declared heat rate vs engineering benchmarks.
    Detects artificial efficiency degradation used to justify higher offers.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["consistent", "moderate_variance", "significant_variance"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class LoadFactorNode(EvidenceNode):
    """
    Node representing system load factor during offer periods.
    Higher load periods provide more opportunity for profitable withholding.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["low_demand", "normal_demand", "peak_demand"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class MarketTightnessNode(EvidenceNode):
    """
    Node representing supply-demand balance in the market.
    Tight markets provide more opportunity for withholding to affect prices.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["surplus", "balanced", "tight"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class CompetitiveContextNode(EvidenceNode):
    """
    Node representing level of competition in the market segment.
    Less competitive markets enable more effective withholding strategies.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["competitive", "concentrated", "monopolistic"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class TransmissionConstraintNode(EvidenceNode):
    """
    Node representing transmission system constraints affecting competition.
    Transmission constraints can create local market power enabling withholding.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["unconstrained", "moderate_constraints", "severe_constraints"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class BidShapeAnomalyNode(EvidenceNode):
    """
    Node representing analysis of bid curve shape for anomalies.
    Detects unusual bid curve shapes that suggest strategic withholding.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_curve", "stepped_curve", "manipulative_curve"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class OfferWithdrawalPatternNode(EvidenceNode):
    """
    Node representing pattern of offer withdrawals or capacity withholding.
    Detects systematic patterns of capacity withdrawal during high-value periods.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_availability", "selective_withdrawal", "systematic_withholding"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class CrossPlantCoordinationNode(EvidenceNode):
    """
    Node representing coordination patterns across multiple generation units.
    Detects coordinated withholding strategies across multiple plants.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["independent_operation", "coordinated_operation", "systematic_coordination"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class CapacityUtilizationNode(EvidenceNode):
    """
    Node representing plant capacity utilization compared to availability declarations.
    Detects artificial capacity limitations used to support higher offers.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["full_utilization", "partial_utilization", "artificial_limitation"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class MarkupConsistencyNode(EvidenceNode):
    """
    Node representing consistency of markup patterns across time periods.
    Analyzes whether markup patterns are consistent or strategically variable.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["consistent_markup", "variable_markup", "strategic_markup"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class OpportunityPricingNode(EvidenceNode):
    """
    Node representing pricing behavior during high-value opportunities.
    Detects opportunistic pricing during peak demand or tight supply conditions.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["cost_based", "opportunistic", "exploitative"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


class FuelPriceCorrelationNode(EvidenceNode):
    """
    Node representing correlation between fuel price changes and offer adjustments.
    Analyzes whether offers adjust appropriately with fuel price movements.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["strong_correlation", "weak_correlation", "no_correlation"]
        super().__init__(
            name, states, description=description, fallback_prior=fallback_prior
        )


# NEW: Specialized latent intent node for economic withholding
class WithholdingLatentIntentNode(LatentIntentNode):
    """
    Node representing latent intent to engage in economic withholding.
    Infers hidden intent to withhold capacity from converging evidence patterns.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["no_withholding_intent", "potential_withholding", "clear_withholding_intent"]
        super().__init__(name, description=description, fallback_prior=fallback_prior)

    @staticmethod
    def _normalize_evidence_value(value: Union[int, float], evidence_name: str) -> float:
        """
        Normalize evidence values to 0-1 scale for consistent intent strength calculation.
        
        Normalization ensures different evidence types with varying scales (percentages, ratios, scores)
        can be fairly weighted in the final withholding intent calculation. This is critical for
        accurate economic withholding detection as it prevents high-magnitude values from
        dominating the risk assessment.
        
        Args:
            value: Raw evidence value to normalize
            evidence_name: Name of the evidence type for scale determination
            
        Returns:
            Normalized value between 0.0 and 1.0
        """
        # Define normalization ranges for different evidence types
        normalization_ranges = {
            "marginal_cost_deviation": 100.0,  # Percentage deviation
            "fuel_cost_variance": 50.0,        # Price variance percentage
            "plant_efficiency": 1.0,           # Already normalized 0-1
            "market_tightness": 1.0,           # Already normalized 0-1
            "load_factor": 1.0,                # Already normalized 0-1
            "bid_shape_anomaly": 10.0,         # Anomaly score
            "capacity_utilization": 1.0,       # Already normalized 0-1
            "profit_motivation": 1.0,          # Already normalized 0-1
        }
        
        max_range = normalization_ranges.get(evidence_name, 100.0)
        return min(max(value / max_range, 0.0), 1.0)

    def get_intent_strength(self, evidence_values: Dict[str, Any]) -> float:
        """
        Calculate withholding intent strength based on energy market evidence.
        
        Args:
            evidence_values: Dictionary of evidence node values
            
        Returns:
            Intent strength score between 0.0 and 1.0
        """
        strength = 0.0

        # Energy market specific weights based on ARERA methodology
        weights = {
            "marginal_cost_deviation": 0.25,      # Highest weight - core indicator
            "fuel_cost_variance": 0.15,           # Cost basis manipulation
            "plant_efficiency": 0.10,             # Artificial constraints
            "market_tightness": 0.15,             # Market opportunity
            "load_factor": 0.10,                  # Demand conditions
            "bid_shape_anomaly": 0.10,            # Offer curve manipulation
            "capacity_utilization": 0.10,         # Physical withholding
            "profit_motivation": 0.05,            # Reused existing node
        }

        for evidence_name, weight in weights.items():
            if evidence_name in evidence_values:
                evidence_value = evidence_values[evidence_name]
                if isinstance(evidence_value, (int, float)):
                    normalized_value = self._normalize_evidence_value(evidence_value, evidence_name)
                    strength += weight * normalized_value

        return min(strength, 1.0)


# NEW: Outcome node for economic withholding risk
class EconomicWithholdingRiskNode(OutcomeNode):
    """
    Node representing the final economic withholding risk assessment.
    Combines all evidence through Bayesian inference to produce risk score.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["no_withholding", "potential_withholding", "clear_withholding"]
        super().__init__(name, description=description, fallback_prior=fallback_prior)


class EconomicWithholdingNodes:
    """
    Helper class for managing economic withholding detection nodes.
    
    This class provides easy access to node definitions and templates
    specific to economic withholding detection in power markets.
    """

    def __init__(self):
        """Initialize the economic withholding nodes helper."""
        
        # REUSED NODES (imported as-is from existing library)
        self.PRICE_IMPACT_RATIO = "price_impact_ratio"
        self.VOLUME_PARTICIPATION = "volume_participation"
        self.LIQUIDITY_CONTEXT = "liquidity_context"
        self.ORDER_CLUSTERING = "order_clustering"
        self.BENCHMARK_TIMING = "benchmark_timing"
        self.PROFIT_MOTIVATION = "profit_motivation"
        
        # NEW ENERGY-SPECIFIC NODES
        self.FUEL_COST_VARIANCE = "fuel_cost_variance"
        self.PLANT_EFFICIENCY = "plant_efficiency"
        self.MARGINAL_COST_DEVIATION = "marginal_cost_deviation"
        self.HEAT_RATE_VARIANCE = "heat_rate_variance"
        self.LOAD_FACTOR = "load_factor"
        self.MARKET_TIGHTNESS = "market_tightness"
        self.COMPETITIVE_CONTEXT = "competitive_context"
        self.TRANSMISSION_CONSTRAINT = "transmission_constraint"
        self.BID_SHAPE_ANOMALY = "bid_shape_anomaly"
        self.OFFER_WITHDRAWAL_PATTERN = "offer_withdrawal_pattern"
        self.CROSS_PLANT_COORDINATION = "cross_plant_coordination"
        self.CAPACITY_UTILIZATION = "capacity_utilization"
        self.MARKUP_CONSISTENCY = "markup_consistency"
        self.OPPORTUNITY_PRICING = "opportunity_pricing"
        self.FUEL_PRICE_CORRELATION = "fuel_price_correlation"
        
        # INTENT AND OUTCOME NODES
        self.WITHHOLDING_LATENT_INTENT = "withholding_latent_intent"
        self.ECONOMIC_WITHHOLDING_RISK = "economic_withholding_risk"

        # Define node configurations
        self.node_definitions = {
            # Reused nodes (reference existing implementations)
            self.PRICE_IMPACT_RATIO: {
                "type": "price_impact_ratio",
                "class": PriceImpactRatioNode,
                "states": ["normal_impact", "elevated_impact", "excessive_impact"],
                "description": "Price impact ratio analysis",
                "fallback_prior": [0.75, 0.2, 0.05],
            },
            self.VOLUME_PARTICIPATION: {
                "type": "volume_participation", 
                "class": VolumeParticipationNode,
                "states": ["normal_participation", "high_participation", "dominant_participation"],
                "description": "Volume participation analysis",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            self.LIQUIDITY_CONTEXT: {
                "type": "liquidity_context",
                "class": LiquidityContextNode,
                "states": ["liquid", "moderate", "illiquid"],
                "description": "Market liquidity conditions",
                "fallback_prior": [0.6, 0.3, 0.1],
            },
            self.ORDER_CLUSTERING: {
                "type": "order_clustering",
                "class": OrderClusteringNode,
                "states": ["normal_distribution", "moderate_clustering", "high_clustering"],
                "description": "Order clustering analysis",
                "fallback_prior": [0.7, 0.25, 0.05],
            },
            self.BENCHMARK_TIMING: {
                "type": "benchmark_timing",
                "class": BenchmarkTimingNode,
                "states": ["outside_window", "near_window", "during_window"],
                "description": "Peak period timing analysis",
                "fallback_prior": [0.7, 0.2, 0.1],
            },
            self.PROFIT_MOTIVATION: {
                "type": "profit_motivation",
                "class": ProfitMotivationNode,
                "states": ["normal_profit", "unusual_profit", "suspicious_profit"],
                "description": "Profit motivation analysis",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            
            # New energy-specific nodes
            self.FUEL_COST_VARIANCE: {
                "type": "fuel_cost_variance",
                "class": FuelCostVarianceNode,
                "states": ["aligned", "moderate_variance", "high_variance"],
                "description": "Fuel cost variance analysis",
                "fallback_prior": [0.7, 0.25, 0.05],
            },
            self.PLANT_EFFICIENCY: {
                "type": "plant_efficiency",
                "class": PlantEfficiencyNode,
                "states": ["optimal", "suboptimal", "significantly_impaired"],
                "description": "Plant efficiency analysis",
                "fallback_prior": [0.6, 0.3, 0.1],
            },
            self.MARGINAL_COST_DEVIATION: {
                "type": "marginal_cost_deviation",
                "class": MarginalCostDeviationNode,
                "states": ["cost_reflective", "moderate_markup", "excessive_markup"],
                "description": "Marginal cost deviation analysis",
                "fallback_prior": [0.7, 0.25, 0.05],
            },
            self.HEAT_RATE_VARIANCE: {
                "type": "heat_rate_variance",
                "class": HeatRateVarianceNode,
                "states": ["consistent", "moderate_variance", "significant_variance"],
                "description": "Heat rate variance analysis",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            self.LOAD_FACTOR: {
                "type": "load_factor",
                "class": LoadFactorNode,
                "states": ["low_demand", "normal_demand", "peak_demand"],
                "description": "System load factor analysis",
                "fallback_prior": [0.3, 0.5, 0.2],
            },
            self.MARKET_TIGHTNESS: {
                "type": "market_tightness",
                "class": MarketTightnessNode,
                "states": ["surplus", "balanced", "tight"],
                "description": "Market supply-demand balance",
                "fallback_prior": [0.4, 0.4, 0.2],
            },
            self.COMPETITIVE_CONTEXT: {
                "type": "competitive_context",
                "class": CompetitiveContextNode,
                "states": ["competitive", "concentrated", "monopolistic"],
                "description": "Market competition level",
                "fallback_prior": [0.6, 0.3, 0.1],
            },
            self.TRANSMISSION_CONSTRAINT: {
                "type": "transmission_constraint",
                "class": TransmissionConstraintNode,
                "states": ["unconstrained", "moderate_constraints", "severe_constraints"],
                "description": "Transmission system constraints",
                "fallback_prior": [0.7, 0.25, 0.05],
            },
            self.BID_SHAPE_ANOMALY: {
                "type": "bid_shape_anomaly",
                "class": BidShapeAnomalyNode,
                "states": ["normal_curve", "stepped_curve", "manipulative_curve"],
                "description": "Bid curve shape analysis",
                "fallback_prior": [0.8, 0.15, 0.05],
            },
            self.OFFER_WITHDRAWAL_PATTERN: {
                "type": "offer_withdrawal_pattern",
                "class": OfferWithdrawalPatternNode,
                "states": ["normal_availability", "selective_withdrawal", "systematic_withholding"],
                "description": "Offer withdrawal pattern analysis",
                "fallback_prior": [0.85, 0.12, 0.03],
            },
            self.CROSS_PLANT_COORDINATION: {
                "type": "cross_plant_coordination",
                "class": CrossPlantCoordinationNode,
                "states": ["independent_operation", "coordinated_operation", "systematic_coordination"],
                "description": "Cross-plant coordination analysis",
                "fallback_prior": [0.9, 0.08, 0.02],
            },
            self.CAPACITY_UTILIZATION: {
                "type": "capacity_utilization",
                "class": CapacityUtilizationNode,
                "states": ["full_utilization", "partial_utilization", "artificial_limitation"],
                "description": "Capacity utilization analysis",
                "fallback_prior": [0.7, 0.25, 0.05],
            },
            self.MARKUP_CONSISTENCY: {
                "type": "markup_consistency",
                "class": MarkupConsistencyNode,
                "states": ["consistent_markup", "variable_markup", "strategic_markup"],
                "description": "Markup consistency analysis",
                "fallback_prior": [0.6, 0.3, 0.1],
            },
            self.OPPORTUNITY_PRICING: {
                "type": "opportunity_pricing",
                "class": OpportunityPricingNode,
                "states": ["cost_based", "opportunistic", "exploitative"],
                "description": "Opportunity pricing analysis",
                "fallback_prior": [0.7, 0.25, 0.05],
            },
            self.FUEL_PRICE_CORRELATION: {
                "type": "fuel_price_correlation",
                "class": FuelPriceCorrelationNode,
                "states": ["strong_correlation", "weak_correlation", "no_correlation"],
                "description": "Fuel price correlation analysis",
                "fallback_prior": [0.6, 0.3, 0.1],
            },
            self.WITHHOLDING_LATENT_INTENT: {
                "type": "withholding_latent_intent",
                "class": WithholdingLatentIntentNode,
                "states": ["no_withholding_intent", "potential_withholding", "clear_withholding_intent"],
                "description": "Latent withholding intent",
                "fallback_prior": [0.95, 0.04, 0.01],
            },
            self.ECONOMIC_WITHHOLDING_RISK: {
                "type": "economic_withholding_risk",
                "class": EconomicWithholdingRiskNode,
                "states": ["no_withholding", "potential_withholding", "clear_withholding"],
                "description": "Economic withholding risk outcome",
                "fallback_prior": [0.95, 0.04, 0.01],
            },
        }

    def get_node(self, node_name: str) -> Optional[BayesianNode]:
        """
        Get a node by name.

        Args:
            node_name: Name of the node

        Returns:
            BayesianNode instance or None
        """
        if node_name not in self.node_definitions:
            return None

        node_def = self.node_definitions[node_name]
        node_class = node_def["class"]
        
        # Create the node instance
        node = node_class(
            name=node_name,
            description=node_def["description"],
            fallback_prior=node_def["fallback_prior"],
        )

        return node

    def get_all_nodes(self) -> Dict[str, BayesianNode]:
        """
        Get all nodes for the economic withholding model.

        Returns:
            Dictionary of all nodes
        """
        nodes = {}
        for node_name in self.node_definitions.keys():
            nodes[node_name] = self.get_node(node_name)

        return nodes

    def get_evidence_nodes(self) -> Dict[str, BayesianNode]:
        """
        Get only the evidence nodes.

        Returns:
            Dictionary of evidence nodes
        """
        evidence_nodes = {}

        evidence_types = [
            "price_impact_ratio", "volume_participation", "liquidity_context",
            "order_clustering", "benchmark_timing", "profit_motivation",
            "fuel_cost_variance", "plant_efficiency", "marginal_cost_deviation",
            "heat_rate_variance", "load_factor", "market_tightness",
            "competitive_context", "transmission_constraint", "bid_shape_anomaly",
            "offer_withdrawal_pattern", "cross_plant_coordination", "capacity_utilization",
            "markup_consistency", "opportunity_pricing", "fuel_price_correlation"
        ]

        for node_name, node_def in self.node_definitions.items():
            if node_def["type"] in evidence_types:
                evidence_nodes[node_name] = self.get_node(node_name)

        return evidence_nodes

    def get_node_states(self, node_name: str) -> Optional[List[str]]:
        """
        Get the states for a specific node.

        Args:
            node_name: Name of the node

        Returns:
            List of node states or None
        """
        if node_name in self.node_definitions:
            return self.node_definitions[node_name]["states"]
        return None

    def get_standard_nodes(self) -> List[str]:
        """Get the standard (non-latent intent) node names."""
        return [
            self.PRICE_IMPACT_RATIO, self.VOLUME_PARTICIPATION, self.LIQUIDITY_CONTEXT,
            self.ORDER_CLUSTERING, self.BENCHMARK_TIMING, self.PROFIT_MOTIVATION,
            self.FUEL_COST_VARIANCE, self.PLANT_EFFICIENCY, self.MARGINAL_COST_DEVIATION,
            self.HEAT_RATE_VARIANCE, self.LOAD_FACTOR, self.MARKET_TIGHTNESS,
            self.COMPETITIVE_CONTEXT, self.TRANSMISSION_CONSTRAINT, self.BID_SHAPE_ANOMALY,
            self.OFFER_WITHDRAWAL_PATTERN, self.CROSS_PLANT_COORDINATION, self.CAPACITY_UTILIZATION,
            self.MARKUP_CONSISTENCY, self.OPPORTUNITY_PRICING, self.FUEL_PRICE_CORRELATION,
            self.ECONOMIC_WITHHOLDING_RISK,
        ]

    def get_latent_intent_nodes(self) -> List[str]:
        """Get the latent intent model node names."""
        return [
            self.PRICE_IMPACT_RATIO, self.VOLUME_PARTICIPATION, self.LIQUIDITY_CONTEXT,
            self.ORDER_CLUSTERING, self.BENCHMARK_TIMING, self.PROFIT_MOTIVATION,
            self.FUEL_COST_VARIANCE, self.PLANT_EFFICIENCY, self.MARGINAL_COST_DEVIATION,
            self.HEAT_RATE_VARIANCE, self.LOAD_FACTOR, self.MARKET_TIGHTNESS,
            self.COMPETITIVE_CONTEXT, self.TRANSMISSION_CONSTRAINT, self.BID_SHAPE_ANOMALY,
            self.OFFER_WITHDRAWAL_PATTERN, self.CROSS_PLANT_COORDINATION, self.CAPACITY_UTILIZATION,
            self.MARKUP_CONSISTENCY, self.OPPORTUNITY_PRICING, self.FUEL_PRICE_CORRELATION,
            self.WITHHOLDING_LATENT_INTENT,
            self.ECONOMIC_WITHHOLDING_RISK,
        ]

    def validate_node_value(self, node_name: str, value: Any) -> bool:
        """
        Validate a value for a specific node.

        Args:
            node_name: Name of the node
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        if node_name not in self.node_definitions:
            return False

        states = self.node_definitions[node_name]["states"]

        # Check if value is a valid state index
        if isinstance(value, int):
            return 0 <= value < len(states)

        # Check if value is a valid state name
        if isinstance(value, str):
            return value in states

        return False