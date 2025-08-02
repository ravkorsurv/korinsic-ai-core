"""
Reusable Intermediate Nodes Library for Cross-Model Fan-In Reduction

This module provides intermediate node classes designed for reuse across multiple
Bayesian models. Each node represents a common business logic pattern that appears
across different market abuse typologies.

Design Principles:
1. Cross-typology reusability - nodes work across spoofing, collusion, manipulation, etc.
2. Business logic coherence - each node groups related evidence types
3. Regulatory alignment - nodes map to common regulatory investigation patterns
4. Fan-in optimization - cap parents to 3-4 for manageable CPT complexity
"""

from typing import Any, Dict, List, Optional, Set
import numpy as np
from pgmpy.factors.discrete import TabularCPD

from .node_library import RiskFactorNode


class MarketImpactNode(RiskFactorNode):
    """
    REUSABLE: Market-level manipulation impact indicators.
    
    Used across: Spoofing, Commodity Manipulation, Market Cornering, Economic Withholding
    
    Common parent patterns:
    - order_clustering + price_impact_ratio + volume_participation
    - liquidity_context + benchmark_timing + market_segmentation
    - cross_venue_coordination + price_movement + volume_impact
    
    States: ["minimal_impact", "moderate_impact", "significant_impact"]
    """

    def __init__(
        self,
        name: str = "market_impact_node",
        parent_nodes: Optional[List[str]] = None,
        description: str = "Market-level manipulation impact aggregation",
        fallback_prior: Optional[List[float]] = None,
    ):
        if parent_nodes and len(parent_nodes) > 4:
            raise ValueError(f"MarketImpactNode supports max 4 parents, got {len(parent_nodes)}")
            
        states = ["minimal_impact", "moderate_impact", "significant_impact"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.70, 0.25, 0.05]
        )
        self.parent_nodes = parent_nodes or []
        self.applicable_typologies = {
            "spoofing", "commodity_manipulation", "market_cornering", 
            "economic_withholding", "wash_trade_detection"
        }

    def create_noisy_or_cpt(self) -> TabularCPD:
        """Create noisy-OR CPT optimized for market impact patterns."""
        if not self.parent_nodes:
            raise ValueError("Parent nodes must be specified before creating CPT")
            
        num_parents = len(self.parent_nodes)
        parent_cards = [3] * num_parents
        
        # Market impact specific parameters
        leak_probability = 0.02  # Base market impact without evidence
        # Decreasing influence weights for additional parents
        parent_probabilities = [0.85, 0.75, 0.65, 0.55][:num_parents]
        
        total_combinations = 3 ** num_parents
        values = np.zeros((3, total_combinations))
        
        for i in range(total_combinations):
            parent_states = self._get_parent_states(i, num_parents)
            
            # Calculate probability of minimal impact (no market manipulation effect)
            prob_minimal = leak_probability
            for j, state in enumerate(parent_states):
                if state == 2:  # Significant evidence state
                    prob_minimal *= (1 - parent_probabilities[j])
                elif state == 1:  # Moderate evidence state
                    prob_minimal *= (1 - parent_probabilities[j] * 0.5)
            
            prob_significant = 1 - prob_minimal
            prob_moderate = prob_significant * 0.35  # 35% of significant becomes moderate
            prob_minimal_final = 1 - prob_significant - prob_moderate
            
            values[0, i] = max(0.01, prob_minimal_final)    # minimal_impact
            values[1, i] = max(0.01, prob_moderate)         # moderate_impact  
            values[2, i] = max(0.01, prob_significant)      # significant_impact
            
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


class BehavioralIntentNode(RiskFactorNode):
    """
    REUSABLE: Trader/entity behavioral intent indicators.
    
    Used across: Spoofing, Cross-Desk Collusion, Insider Dealing, Circular Trading
    
    Common parent patterns:
    - order_behavior + intent_to_execute + order_cancellation
    - comms_metadata + profit_motivation + access_pattern
    - trade_pattern + timing_correlation + behavioral_consistency
    
    States: ["legitimate_intent", "suspicious_intent", "manipulative_intent"]
    """

    def __init__(
        self,
        name: str = "behavioral_intent_node",
        parent_nodes: Optional[List[str]] = None,
        description: str = "Behavioral intent pattern aggregation",
        fallback_prior: Optional[List[float]] = None,
    ):
        if parent_nodes and len(parent_nodes) > 4:
            raise ValueError(f"BehavioralIntentNode supports max 4 parents, got {len(parent_nodes)}")
            
        states = ["legitimate_intent", "suspicious_intent", "manipulative_intent"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.75, 0.20, 0.05]
        )
        self.parent_nodes = parent_nodes or []
        self.applicable_typologies = {
            "spoofing", "cross_desk_collusion", "insider_dealing", 
            "circular_trading", "wash_trade_detection"
        }

    def create_noisy_or_cpt(self) -> TabularCPD:
        """Create noisy-OR CPT optimized for behavioral intent patterns."""
        if not self.parent_nodes:
            raise ValueError("Parent nodes must be specified before creating CPT")
            
        num_parents = len(self.parent_nodes)
        parent_cards = [3] * num_parents
        
        # Behavioral intent specific parameters  
        leak_probability = 0.03  # Base rate of suspicious behavior
        parent_probabilities = [0.90, 0.80, 0.70, 0.60][:num_parents]
        
        total_combinations = 3 ** num_parents
        values = np.zeros((3, total_combinations))
        
        for i in range(total_combinations):
            parent_states = self._get_parent_states(i, num_parents)
            
            # Calculate probability of legitimate intent
            prob_legitimate = leak_probability
            for j, state in enumerate(parent_states):
                if state == 2:  # Manipulative evidence state
                    prob_legitimate *= (1 - parent_probabilities[j])
                elif state == 1:  # Suspicious evidence state
                    prob_legitimate *= (1 - parent_probabilities[j] * 0.4)
            
            prob_manipulative = 1 - prob_legitimate
            prob_suspicious = prob_manipulative * 0.45  # 45% of manipulative becomes suspicious
            prob_legitimate_final = 1 - prob_manipulative - prob_suspicious
            
            values[0, i] = max(0.01, prob_legitimate_final)  # legitimate_intent
            values[1, i] = max(0.01, prob_suspicious)        # suspicious_intent
            values[2, i] = max(0.01, prob_manipulative)      # manipulative_intent
            
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


class CoordinationPatternsNode(RiskFactorNode):
    """
    REUSABLE: Multi-party coordination and collusion indicators.
    
    Used across: Cross-Desk Collusion, Circular Trading, Wash Trading, Market Cornering
    
    Common parent patterns:
    - cross_venue_coordination + settlement_coordination + beneficial_ownership
    - information_sharing + coordinated_activity + timing_synchronization
    - counterparty_relationship + trade_sequence_analysis + risk_transfer
    
    States: ["independent_activity", "correlated_activity", "coordinated_activity"]
    """

    def __init__(
        self,
        name: str = "coordination_patterns_node",
        parent_nodes: Optional[List[str]] = None,
        description: str = "Multi-party coordination pattern aggregation",
        fallback_prior: Optional[List[float]] = None,
    ):
        if parent_nodes and len(parent_nodes) > 4:
            raise ValueError(f"CoordinationPatternsNode supports max 4 parents, got {len(parent_nodes)}")
            
        states = ["independent_activity", "correlated_activity", "coordinated_activity"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.80, 0.15, 0.05]
        )
        self.parent_nodes = parent_nodes or []
        self.applicable_typologies = {
            "cross_desk_collusion", "circular_trading", "wash_trade_detection", "market_cornering"
        }


class InformationAdvantageNode(RiskFactorNode):
    """
    REUSABLE: Information access and timing advantage indicators.
    
    Used across: Insider Dealing, Cross-Desk Collusion, Economic Withholding
    
    Common parent patterns:
    - mnpi_access + timing_correlation + trade_direction
    - news_timing + state_information_access + announcement_correlation
    - information_sharing + access_pattern + privileged_communication
    
    States: ["no_advantage", "potential_advantage", "clear_advantage"]
    """

    def __init__(
        self,
        name: str = "information_advantage_node",
        parent_nodes: Optional[List[str]] = None,
        description: str = "Information access and timing advantage aggregation",
        fallback_prior: Optional[List[float]] = None,
    ):
        if parent_nodes and len(parent_nodes) > 4:
            raise ValueError(f"InformationAdvantageNode supports max 4 parents, got {len(parent_nodes)}")
            
        states = ["no_advantage", "potential_advantage", "clear_advantage"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.70, 0.25, 0.05]
        )
        self.parent_nodes = parent_nodes or []
        self.applicable_typologies = {
            "insider_dealing", "cross_desk_collusion", "economic_withholding"
        }


class EconomicRationalityNode(RiskFactorNode):
    """
    REUSABLE: Economic purpose and rationality indicators.
    
    Used across: Wash Trading, Circular Trading, Economic Withholding, Commodity Manipulation
    
    Common parent patterns:
    - economic_purpose + risk_transfer_analysis + profit_motivation
    - cost_analysis + pricing_rationality + efficiency_metrics
    - market_conditions + competitive_context + opportunity_assessment
    
    States: ["economically_rational", "questionable_rationale", "no_economic_purpose"]
    """

    def __init__(
        self,
        name: str = "economic_rationality_node",
        parent_nodes: Optional[List[str]] = None,
        description: str = "Economic purpose and rationality aggregation",
        fallback_prior: Optional[List[float]] = None,
    ):
        if parent_nodes and len(parent_nodes) > 4:
            raise ValueError(f"EconomicRationalityNode supports max 4 parents, got {len(parent_nodes)}")
            
        states = ["economically_rational", "questionable_rationale", "no_economic_purpose"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.85, 0.12, 0.03]
        )
        self.parent_nodes = parent_nodes or []
        self.applicable_typologies = {
            "wash_trade_detection", "circular_trading", "economic_withholding", "commodity_manipulation"
        }


class TechnicalManipulationNode(RiskFactorNode):
    """
    REUSABLE: Technical manipulation and artificial constraint indicators.
    
    Used across: Economic Withholding, Commodity Manipulation, Market Cornering
    
    Common parent patterns:
    - capacity_utilization + plant_efficiency + technical_constraints
    - physical_position + delivery_manipulation + storage_capacity
    - supply_control + artificial_scarcity + technical_barriers
    
    States: ["normal_operations", "constrained_operations", "artificial_constraints"]
    """

    def __init__(
        self,
        name: str = "technical_manipulation_node",
        parent_nodes: Optional[List[str]] = None,
        description: str = "Technical manipulation and constraint aggregation",
        fallback_prior: Optional[List[float]] = None,
    ):
        if parent_nodes and len(parent_nodes) > 4:
            raise ValueError(f"TechnicalManipulationNode supports max 4 parents, got {len(parent_nodes)}")
            
        states = ["normal_operations", "constrained_operations", "artificial_constraints"]
        super().__init__(
            name, 
            states, 
            description=description, 
            fallback_prior=fallback_prior or [0.75, 0.20, 0.05]
        )
        self.parent_nodes = parent_nodes or []
        self.applicable_typologies = {
            "economic_withholding", "commodity_manipulation", "market_cornering"
        }


# Shared utility methods for all intermediate nodes
class IntermediateNodeMixin:
    """Mixin providing common functionality for intermediate nodes."""
    
    def _get_parent_states(self, combination_index: int, num_parents: int) -> List[int]:
        """Convert combination index to parent state configuration."""
        parent_states = []
        temp = combination_index
        for _ in range(num_parents):
            parent_states.append(temp % 3)
            temp //= 3
        return parent_states
    
    def get_applicable_models(self) -> Set[str]:
        """Get set of models this node can be used in."""
        return getattr(self, 'applicable_typologies', set())
    
    def is_compatible_with_model(self, model_type: str) -> bool:
        """Check if this node is compatible with a specific model type."""
        return model_type in self.get_applicable_models()


# Add mixin to all intermediate node classes
for cls in [MarketImpactNode, BehavioralIntentNode, CoordinationPatternsNode, 
           InformationAdvantageNode, EconomicRationalityNode, TechnicalManipulationNode]:
    # Add mixin methods to each class
    for method_name in dir(IntermediateNodeMixin):
        if not method_name.startswith('_') or method_name in ['_get_parent_states']:
            setattr(cls, method_name, getattr(IntermediateNodeMixin, method_name))


class ReusableNodeFactory:
    """
    Factory for creating reusable intermediate nodes with appropriate configurations.
    Provides standardized node creation patterns across different models.
    """
    
    @staticmethod
    def create_market_impact_node(
        model_type: str,
        parent_nodes: List[str],
        name_suffix: str = ""
    ) -> MarketImpactNode:
        """Create a market impact node configured for specific model type."""
        name = f"market_impact{name_suffix}" if name_suffix else "market_impact"
        
        # Model-specific descriptions
        descriptions = {
            "spoofing": "Market impact from spoofing and layering activities",
            "commodity_manipulation": "Market impact from commodity manipulation schemes", 
            "market_cornering": "Market impact from cornering and squeezing activities",
            "economic_withholding": "Market impact from economic withholding behavior",
            "wash_trade_detection": "Market impact from wash trading activities"
        }
        
        description = descriptions.get(model_type, "Market-level manipulation impact indicators")
        
        node = MarketImpactNode(
            name=name,
            parent_nodes=parent_nodes,
            description=description
        )
        
        if not node.is_compatible_with_model(model_type):
            raise ValueError(f"MarketImpactNode not compatible with model type: {model_type}")
        
        return node
    
    @staticmethod
    def create_behavioral_intent_node(
        model_type: str,
        parent_nodes: List[str],
        name_suffix: str = ""
    ) -> BehavioralIntentNode:
        """Create a behavioral intent node configured for specific model type."""
        name = f"behavioral_intent{name_suffix}" if name_suffix else "behavioral_intent"
        
        descriptions = {
            "spoofing": "Behavioral intent behind spoofing activities",
            "cross_desk_collusion": "Behavioral intent in cross-desk coordination",
            "insider_dealing": "Behavioral intent in insider trading activities",
            "circular_trading": "Behavioral intent in circular trading schemes",
            "wash_trade_detection": "Behavioral intent in wash trading activities"
        }
        
        description = descriptions.get(model_type, "Behavioral intent pattern indicators")
        
        node = BehavioralIntentNode(
            name=name,
            parent_nodes=parent_nodes,
            description=description
        )
        
        if not node.is_compatible_with_model(model_type):
            raise ValueError(f"BehavioralIntentNode not compatible with model type: {model_type}")
        
        return node
    
    @staticmethod
    def get_recommended_nodes_for_model(model_type: str) -> Dict[str, type]:
        """Get recommended intermediate node types for a specific model."""
        recommendations = {
            "spoofing": {
                "market_impact": MarketImpactNode,
                "behavioral_intent": BehavioralIntentNode
            },
            "cross_desk_collusion": {
                "coordination_patterns": CoordinationPatternsNode,
                "behavioral_intent": BehavioralIntentNode,
                "information_advantage": InformationAdvantageNode
            },
            "insider_dealing": {
                "information_advantage": InformationAdvantageNode,
                "behavioral_intent": BehavioralIntentNode
            },
            "circular_trading": {
                "coordination_patterns": CoordinationPatternsNode,
                "economic_rationality": EconomicRationalityNode,
                "behavioral_intent": BehavioralIntentNode
            },
            "wash_trade_detection": {
                "economic_rationality": EconomicRationalityNode,
                "coordination_patterns": CoordinationPatternsNode,
                "market_impact": MarketImpactNode
            },
            "economic_withholding": {
                "technical_manipulation": TechnicalManipulationNode,
                "economic_rationality": EconomicRationalityNode,
                "market_impact": MarketImpactNode,
                "information_advantage": InformationAdvantageNode
            },
            "commodity_manipulation": {
                "technical_manipulation": TechnicalManipulationNode,
                "market_impact": MarketImpactNode,
                "economic_rationality": EconomicRationalityNode
            },
            "market_cornering": {
                "technical_manipulation": TechnicalManipulationNode,
                "coordination_patterns": CoordinationPatternsNode,
                "market_impact": MarketImpactNode
            }
        }
        
        return recommendations.get(model_type, {})