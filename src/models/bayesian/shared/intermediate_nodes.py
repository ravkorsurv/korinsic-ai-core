"""
Intermediate Nodes Library for Fan-In Reduction

This module provides intermediate node classes that reduce fan-in complexity
by grouping related evidence nodes into coherent business logic units.
Each intermediate node caps parent nodes to 3-4 for manageable CPT complexity.
"""

from typing import Any, Dict, List, Optional
import numpy as np
from pgmpy.factors.discrete import TabularCPD

from .node_library import RiskFactorNode


class MarketImpactIntermediateNode(RiskFactorNode):
    """
    Intermediate node that aggregates market-level manipulation indicators.
    
    Typically combines:
    - order_clustering, price_impact_ratio, volume_participation
    - liquidity_context, benchmark_timing
    
    States: ["low_impact", "medium_impact", "high_impact"]
    """

    def __init__(
        self,
        name: str,
        parent_nodes: List[str],
        description: str = "Market impact aggregation node",
        fallback_prior: Optional[List[float]] = None,
    ):
        if len(parent_nodes) > 4:
            raise ValueError(f"MarketImpactIntermediateNode supports max 4 parents, got {len(parent_nodes)}")
            
        states = ["low_impact", "medium_impact", "high_impact"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.70, 0.25, 0.05]
        )
        self.parent_nodes = parent_nodes

    def create_noisy_or_cpt(self) -> TabularCPD:
        """
        Create a noisy-OR CPD for market impact aggregation.
        Assumes independence between parent failure modes.
        """
        num_parents = len(self.parent_nodes)
        parent_cards = [3] * num_parents  # All parents have 3 states
        
        # Noisy-OR parameters: probability of "failure" (high impact) for each parent
        leak_probability = 0.01  # Base rate without any evidence
        parent_probabilities = [0.8, 0.7, 0.6, 0.5][:num_parents]  # Decreasing influence
        
        # Calculate CPT values using noisy-OR logic
        total_combinations = 3 ** num_parents
        values = np.zeros((3, total_combinations))
        
        for i in range(total_combinations):
            # Convert combination index to parent state configuration
            parent_states = []
            temp = i
            for _ in range(num_parents):
                parent_states.append(temp % 3)
                temp //= 3
            
            # Calculate noisy-OR probability
            prob_no_impact = leak_probability
            for j, state in enumerate(parent_states):
                if state == 2:  # High state
                    prob_no_impact *= (1 - parent_probabilities[j])
                elif state == 1:  # Medium state  
                    prob_no_impact *= (1 - parent_probabilities[j] * 0.5)
            
            prob_high_impact = 1 - prob_no_impact
            prob_medium_impact = prob_high_impact * 0.3  # 30% of high becomes medium
            prob_low_impact = 1 - prob_high_impact - prob_medium_impact
            
            values[0, i] = max(0.01, prob_low_impact)
            values[1, i] = max(0.01, prob_medium_impact) 
            values[2, i] = max(0.01, prob_high_impact)
            
            # Normalize
            col_sum = values[:, i].sum()
            values[:, i] /= col_sum

        return TabularCPD(
            variable=self.name,
            variable_card=3,
            values=values,
            evidence=self.parent_nodes,
            evidence_card=parent_cards,
        )


class BehavioralIntentIntermediateNode(RiskFactorNode):
    """
    Intermediate node that aggregates behavioral intent indicators.
    
    Typically combines:
    - order_behavior, intent_to_execute, order_cancellation
    - comms_metadata, access_pattern
    
    States: ["benign_intent", "suspicious_intent", "malicious_intent"]
    """

    def __init__(
        self,
        name: str,
        parent_nodes: List[str],
        description: str = "Behavioral intent aggregation node",
        fallback_prior: Optional[List[float]] = None,
    ):
        if len(parent_nodes) > 4:
            raise ValueError(f"BehavioralIntentIntermediateNode supports max 4 parents, got {len(parent_nodes)}")
            
        states = ["benign_intent", "suspicious_intent", "malicious_intent"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.75, 0.20, 0.05]
        )
        self.parent_nodes = parent_nodes

    def create_noisy_or_cpt(self) -> TabularCPD:
        """Create noisy-OR CPT for behavioral intent aggregation."""
        num_parents = len(self.parent_nodes)
        parent_cards = [3] * num_parents
        
        leak_probability = 0.02  # Slightly higher base rate for behavioral indicators
        parent_probabilities = [0.85, 0.75, 0.65, 0.55][:num_parents]
        
        total_combinations = 3 ** num_parents
        values = np.zeros((3, total_combinations))
        
        for i in range(total_combinations):
            parent_states = []
            temp = i
            for _ in range(num_parents):
                parent_states.append(temp % 3)
                temp //= 3
            
            prob_benign = leak_probability
            for j, state in enumerate(parent_states):
                if state == 2:  # Malicious state
                    prob_benign *= (1 - parent_probabilities[j])
                elif state == 1:  # Suspicious state
                    prob_benign *= (1 - parent_probabilities[j] * 0.4)
            
            prob_malicious = 1 - prob_benign
            prob_suspicious = prob_malicious * 0.4  # 40% of malicious becomes suspicious
            prob_benign_final = 1 - prob_malicious - prob_suspicious
            
            values[0, i] = max(0.01, prob_benign_final)
            values[1, i] = max(0.01, prob_suspicious)
            values[2, i] = max(0.01, prob_malicious)
            
            # Normalize
            col_sum = values[:, i].sum()
            values[:, i] /= col_sum

        return TabularCPD(
            variable=self.name,
            variable_card=3,
            values=values,
            evidence=self.parent_nodes,
            evidence_card=parent_cards,
        )


class CostAnalysisIntermediateNode(RiskFactorNode):
    """
    Intermediate node for Economic Withholding cost analysis indicators.
    
    Combines: marginal_cost_deviation, fuel_cost_variance, plant_efficiency, heat_rate_variance
    States: ["cost_reflective", "moderate_deviation", "excessive_deviation"]
    """

    def __init__(
        self,
        name: str = "cost_analysis_intermediate",
        description: str = "Cost analysis aggregation for economic withholding",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["cost_reflective", "moderate_deviation", "excessive_deviation"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.60, 0.30, 0.10]
        )
        self.parent_nodes = [
            "marginal_cost_deviation", 
            "fuel_cost_variance", 
            "plant_efficiency", 
            "heat_rate_variance"
        ]


class MarketConditionsIntermediateNode(RiskFactorNode):
    """
    Intermediate node for Economic Withholding market condition indicators.
    
    Combines: load_factor, market_tightness, competitive_context, transmission_constraint
    States: ["normal_conditions", "stressed_conditions", "critical_conditions"]
    """

    def __init__(
        self,
        name: str = "market_conditions_intermediate",
        description: str = "Market conditions aggregation for economic withholding",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_conditions", "stressed_conditions", "critical_conditions"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.50, 0.35, 0.15]
        )
        self.parent_nodes = [
            "load_factor", 
            "market_tightness", 
            "competitive_context", 
            "transmission_constraint"
        ]


class BehavioralPatternsIntermediateNode(RiskFactorNode):
    """
    Intermediate node for Economic Withholding behavioral pattern indicators.
    
    Combines: bid_shape_anomaly, offer_withdrawal_pattern, capacity_utilization, 
              markup_consistency, opportunity_pricing
    States: ["normal_behavior", "suspicious_behavior", "manipulative_behavior"]
    """

    def __init__(
        self,
        name: str = "behavioral_patterns_intermediate",
        description: str = "Behavioral patterns aggregation for economic withholding",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_behavior", "suspicious_behavior", "manipulative_behavior"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.65, 0.25, 0.10]
        )
        self.parent_nodes = [
            "bid_shape_anomaly", 
            "offer_withdrawal_pattern", 
            "capacity_utilization", 
            "markup_consistency", 
            "opportunity_pricing"
        ]


class TechnicalFactorsIntermediateNode(RiskFactorNode):
    """
    Intermediate node for Economic Withholding technical analysis indicators.
    
    Combines: fuel_price_correlation, cross_plant_coordination, price_impact_ratio,
              volume_participation, liquidity_context, order_clustering
    States: ["normal_technical", "unusual_technical", "anomalous_technical"]
    """

    def __init__(
        self,
        name: str = "technical_factors_intermediate",
        description: str = "Technical factors aggregation for economic withholding",
        fallback_prior: Optional[List[float]] = None,
    ):
        states = ["normal_technical", "unusual_technical", "anomalous_technical"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.70, 0.25, 0.05]
        )
        self.parent_nodes = [
            "fuel_price_correlation", 
            "cross_plant_coordination", 
            "price_impact_ratio",
            "volume_participation", 
            "liquidity_context", 
            "order_clustering"
        ]


def create_intermediate_cpt(
    intermediate_node: RiskFactorNode,
    parent_nodes: List[str],
    cpt_type: str = "noisy_or"
) -> TabularCPD:
    """
    Factory function to create CPTs for intermediate nodes.
    
    Args:
        intermediate_node: The intermediate node instance
        parent_nodes: List of parent node names
        cpt_type: Type of CPT to create ("noisy_or", "weighted_average", "expert_prior")
    
    Returns:
        TabularCPD for the intermediate node
    """
    if hasattr(intermediate_node, 'create_noisy_or_cpt'):
        return intermediate_node.create_noisy_or_cpt()
    
    # Default implementation for other intermediate nodes
    num_parents = len(parent_nodes)
    parent_cards = [3] * num_parents
    total_combinations = 3 ** num_parents
    
    # Simple weighted average approach
    values = np.full((3, total_combinations), 1/3)  # Uniform prior
    
    return TabularCPD(
        variable=intermediate_node.name,
        variable_card=3,
        values=values,
        evidence=parent_nodes,
        evidence_card=parent_cards,
    )