"""
Centralized Probability Configuration for Bayesian Models

This module provides centralized configuration of all probability values used across
the Bayesian network models, replacing hardcoded magic numbers with well-documented,
maintainable configuration.

Design Principles:
1. Single source of truth for all probability values
2. Business logic documentation for each probability
3. Regulatory compliance context
4. Easy maintenance and updates
5. Type safety and validation
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class EvidenceType(Enum):
    """Types of evidence nodes with different probability characteristics."""
    BEHAVIORAL = "behavioral"  # Order behavior, intent patterns
    MARKET_IMPACT = "market_impact"  # Price, volume, clustering effects  
    INFORMATION = "information"  # MNPI access, timing, communications
    COORDINATION = "coordination"  # Cross-venue, settlement patterns
    TECHNICAL = "technical"  # Capacity, efficiency, constraints
    ECONOMIC = "economic"  # Cost analysis, rationality, purpose


@dataclass
class ProbabilityProfile:
    """
    Probability profile for different evidence types.
    
    Attributes:
        low_state: Probability for low/minimal/legitimate state
        medium_state: Probability for medium/moderate/suspicious state  
        high_state: Probability for high/significant/manipulative state
        description: Business logic explanation
        regulatory_basis: Regulatory framework reference
    """
    low_state: float
    medium_state: float
    high_state: float
    description: str
    regulatory_basis: str = ""
    
    def __post_init__(self):
        """Validate probabilities sum to 1.0"""
        total = self.low_state + self.medium_state + self.high_state
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValueError(f"Probabilities must sum to 1.0, got {total}")
    
    def as_list(self) -> List[List[float]]:
        """Return as TabularCPD format."""
        return [[self.low_state], [self.medium_state], [self.high_state]]


class ProbabilityConfig:
    """
    Centralized probability configuration for all Bayesian models.
    
    Provides evidence node priors, intermediate node parameters, and outcome
    probabilities with full business logic documentation and regulatory context.
    """
    
    # Evidence Node Prior Probabilities by Type
    EVIDENCE_PROFILES = {
        EvidenceType.BEHAVIORAL: ProbabilityProfile(
            low_state=0.70,
            medium_state=0.25,
            high_state=0.05,
            description="Most trading behavior is legitimate; suspicious patterns are moderate; manipulative behavior is rare",
            regulatory_basis="MAR Article 12 - Market manipulation patterns"
        ),
        
        EvidenceType.MARKET_IMPACT: ProbabilityProfile(
            low_state=0.75,
            medium_state=0.20,
            high_state=0.05,
            description="Most market movements are natural; moderate impacts from legitimate large orders; significant artificial impact is rare",
            regulatory_basis="ESMA Guidelines on Market Abuse - Price and volume effects"
        ),
        
        EvidenceType.INFORMATION: ProbabilityProfile(
            low_state=0.80,
            medium_state=0.15,
            high_state=0.05,
            description="Most information access is legitimate; potential advantages are uncommon; clear insider advantages are rare",
            regulatory_basis="MAR Article 7 - Inside information definition"
        ),
        
        EvidenceType.COORDINATION: ProbabilityProfile(
            low_state=0.80,
            medium_state=0.15,
            high_state=0.05,
            description="Most activity is independent; correlated patterns may be coincidental; coordinated manipulation is rare",
            regulatory_basis="MAR Article 12 - Concerted practices"
        ),
        
        EvidenceType.TECHNICAL: ProbabilityProfile(
            low_state=0.75,
            medium_state=0.20,
            high_state=0.05,
            description="Most operations are normal; constraints are often legitimate; artificial constraints are rare",
            regulatory_basis="ARERA Guidelines - Technical capacity assessment"
        ),
        
        EvidenceType.ECONOMIC: ProbabilityProfile(
            low_state=0.85,
            medium_state=0.12,
            high_state=0.03,
            description="Most trading has economic rationale; questionable rationale needs investigation; clear lack of purpose is rare",
            regulatory_basis="Economic substance requirements under MAR"
        )
    }
    
    # Hierarchical Evidence Node Structure by Model
    class EvidenceNodeGroups:
        """Hierarchical organization of evidence nodes by model type."""
        
        @classmethod
        def get_nodes_for_model(cls, model_type: str) -> Dict[str, ProbabilityProfile]:
            """Get evidence nodes for a specific model type with lazy loading."""
            if model_type == 'spoofing':
                return {
                    "order_clustering": EVIDENCE_PROFILES[EvidenceType.MARKET_IMPACT],
                    "price_impact_ratio": EVIDENCE_PROFILES[EvidenceType.MARKET_IMPACT], 
                    "volume_participation": EVIDENCE_PROFILES[EvidenceType.MARKET_IMPACT],
                    "order_behavior": EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL],
                    "intent_to_execute": EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL],
                    "order_cancellation": EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL],
                }
            elif model_type == 'cross_desk_collusion':
                return {
                    "comms_metadata": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
                    "profit_motivation": EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL],
                    "cross_venue_coordination": EVIDENCE_PROFILES[EvidenceType.COORDINATION],
                    "access_pattern": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
                    "market_segmentation": EVIDENCE_PROFILES[EvidenceType.COORDINATION],
                }
            else:
                return {}

        @classmethod
        def validate_model_completeness(cls, model_type: str, required_nodes: List[str]) -> bool:
            """Validate that all required nodes exist for a model."""
            available_nodes = cls.get_nodes_for_model(model_type)
            return all(node in available_nodes for node in required_nodes)

        @classmethod
        def get_model_types(cls) -> List[str]:
            """Get list of supported model types."""
            return ['spoofing', 'cross_desk_collusion', 'insider_dealing', 
                   'economic_withholding', 'wash_trading']

    # Specific Evidence Node Configurations (Flat structure for backward compatibility)
    EVIDENCE_NODE_PROBABILITIES = {
        # Spoofing Evidence Nodes
        "order_clustering": EVIDENCE_PROFILES[EvidenceType.MARKET_IMPACT],
        "price_impact_ratio": EVIDENCE_PROFILES[EvidenceType.MARKET_IMPACT], 
        "volume_participation": EVIDENCE_PROFILES[EvidenceType.MARKET_IMPACT],
        "order_behavior": EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL],
        "intent_to_execute": EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL],
        "order_cancellation": EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL],
        
        # Cross-Desk Collusion Evidence Nodes
        "comms_metadata": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
        "profit_motivation": EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL],
        "cross_venue_coordination": EVIDENCE_PROFILES[EvidenceType.COORDINATION],
        "access_pattern": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
        "market_segmentation": EVIDENCE_PROFILES[EvidenceType.COORDINATION],
        
        # Insider Dealing Evidence Nodes
        "trade_pattern": ProbabilityProfile(0.95, 0.04, 0.01, "Most trades follow normal patterns"),
        "comms_intent": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
        "pnl_drift": ProbabilityProfile(0.90, 0.08, 0.02, "Most P&L changes are market-driven"),
        "mnpi_access": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
        "timing_correlation": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
        "trade_direction": EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL],
        "news_timing": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
        "algo_reaction_sensitivity": EVIDENCE_PROFILES[EvidenceType.TECHNICAL],
        "price_impact_anomaly": EVIDENCE_PROFILES[EvidenceType.MARKET_IMPACT],
        
        # Economic Withholding Evidence Nodes (binary)
        "capacity_utilization": ProbabilityProfile(0.90, 0.00, 0.10, "Most capacity use is optimal", "ARERA capacity rules"),
        "plant_efficiency": ProbabilityProfile(0.90, 0.00, 0.10, "Most plants operate efficiently"),
        "fuel_cost_analysis": ProbabilityProfile(0.90, 0.00, 0.10, "Most fuel costs are legitimate"),
        "bid_price_analysis": ProbabilityProfile(0.90, 0.00, 0.10, "Most bids are competitively priced"),
        "technical_constraints": ProbabilityProfile(0.90, 0.00, 0.10, "Most constraints are genuine"),
        "market_conditions": ProbabilityProfile(0.90, 0.00, 0.10, "Most market conditions are normal"),
        "regulatory_compliance": ProbabilityProfile(0.90, 0.00, 0.10, "Most operations are compliant"),
        "competitive_context": ProbabilityProfile(0.90, 0.00, 0.10, "Most competition is fair"),
        "historical_performance": ProbabilityProfile(0.90, 0.00, 0.10, "Most performance is consistent"),
        "dispatch_instructions": ProbabilityProfile(0.90, 0.00, 0.10, "Most dispatch follows merit order"),
        "maintenance_scheduling": ProbabilityProfile(0.90, 0.00, 0.10, "Most maintenance is scheduled appropriately"),
        "fuel_availability": ProbabilityProfile(0.90, 0.00, 0.10, "Most fuel supply is adequate"),
        "transmission_constraints": ProbabilityProfile(0.90, 0.00, 0.10, "Most transmission is unconstrained"),
        "environmental_limits": ProbabilityProfile(0.90, 0.00, 0.10, "Most operations meet environmental limits"),
        "startup_costs": ProbabilityProfile(0.90, 0.00, 0.10, "Most startup costs are reasonable"),
        "ramping_capabilities": ProbabilityProfile(0.90, 0.00, 0.10, "Most ramping is within technical limits"),
        "demand_forecasting": ProbabilityProfile(0.90, 0.00, 0.10, "Most demand forecasts are accurate"),
        "price_forecasting": ProbabilityProfile(0.90, 0.00, 0.10, "Most price forecasts are reasonable"),
        "risk_management": ProbabilityProfile(0.90, 0.00, 0.10, "Most risk management is appropriate"),
        
        # Wash Trading Evidence Nodes
        "economic_purpose": EVIDENCE_PROFILES[EvidenceType.ECONOMIC],
        "risk_transfer_analysis": EVIDENCE_PROFILES[EvidenceType.ECONOMIC],
        "counterparty_relationship": EVIDENCE_PROFILES[EvidenceType.COORDINATION],
        "settlement_coordination": EVIDENCE_PROFILES[EvidenceType.COORDINATION],
        "beneficial_ownership": EVIDENCE_PROFILES[EvidenceType.COORDINATION],
        "trade_sequence_analysis": EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL],
        "timing_synchronization": EVIDENCE_PROFILES[EvidenceType.COORDINATION],
        
        # Common evidence nodes across models
        "liquidity_context": EVIDENCE_PROFILES[EvidenceType.MARKET_IMPACT],
        "benchmark_timing": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
        "information_sharing": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
        "coordinated_activity": EVIDENCE_PROFILES[EvidenceType.COORDINATION],
        "privileged_communication": EVIDENCE_PROFILES[EvidenceType.INFORMATION],
        "pricing_rationality": EVIDENCE_PROFILES[EvidenceType.ECONOMIC],
        "efficiency_metrics": EVIDENCE_PROFILES[EvidenceType.TECHNICAL],
        "opportunity_assessment": EVIDENCE_PROFILES[EvidenceType.ECONOMIC],
        "physical_position": EVIDENCE_PROFILES[EvidenceType.TECHNICAL],
        "delivery_manipulation": EVIDENCE_PROFILES[EvidenceType.TECHNICAL],
        "storage_capacity": EVIDENCE_PROFILES[EvidenceType.TECHNICAL],
        "supply_control": EVIDENCE_PROFILES[EvidenceType.TECHNICAL],
        "artificial_scarcity": EVIDENCE_PROFILES[EvidenceType.TECHNICAL],
        "technical_barriers": EVIDENCE_PROFILES[EvidenceType.TECHNICAL]
    }
    
    # Intermediate Node Parameters for Noisy-OR CPTs
    INTERMEDIATE_NODE_PARAMETERS = {
        "market_impact": {
            "leak_probability": 0.02,  # Base market impact without evidence
            "parent_probabilities": [0.85, 0.75, 0.65, 0.55],  # Decreasing influence
            "description": "Market manipulation impact parameters",
            "regulatory_basis": "ESMA market impact thresholds"
        },
        
        "behavioral_intent": {
            "leak_probability": 0.03,  # Base rate of suspicious behavior  
            "parent_probabilities": [0.90, 0.80, 0.70, 0.60],  # Strong behavioral signals
            "description": "Behavioral intent assessment parameters",
            "regulatory_basis": "MAR behavioral pattern recognition"
        },
        
        "coordination_patterns": {
            "leak_probability": 0.02,  # Base coordination without evidence
            "parent_probabilities": [0.88, 0.78, 0.68, 0.58],  # Coordination detection
            "description": "Multi-party coordination parameters",
            "regulatory_basis": "MAR concerted practices detection"
        },
        
        "information_advantage": {
            "leak_probability": 0.01,  # Information advantages are rare
            "parent_probabilities": [0.92, 0.82, 0.72, 0.62],  # Strong information signals
            "description": "Information advantage assessment parameters", 
            "regulatory_basis": "MAR inside information definition"
        },
        
        "economic_rationality": {
            "leak_probability": 0.05,  # Some trades lack clear rationale
            "parent_probabilities": [0.80, 0.70, 0.60, 0.50],  # Economic purpose assessment
            "description": "Economic rationale evaluation parameters",
            "regulatory_basis": "Economic substance requirements"
        },
        
        "technical_manipulation": {
            "leak_probability": 0.03,  # Some technical issues are artificial
            "parent_probabilities": [0.85, 0.75, 0.65, 0.55],  # Technical constraint assessment
            "description": "Technical manipulation detection parameters",
            "regulatory_basis": "ARERA technical capacity rules"
        }
    }
    
    # Outcome Node Probabilities (Risk Factor → Final Outcome)
    OUTCOME_PROBABILITIES = {
        "spoofing": {
            "low_risk": [0.95, 0.04, 0.01],    # [No spoofing, Possible, Likely]
            "medium_risk": [0.60, 0.30, 0.10],
            "high_risk": [0.10, 0.40, 0.50],
            "description": "Spoofing outcome given risk level"
        },
        
        "insider_dealing": {
            "low_risk": [0.98, 0.015, 0.005],   # [No insider dealing, Possible, Likely]
            "medium_risk": [0.70, 0.25, 0.05],
            "high_risk": [0.15, 0.35, 0.50],
            "description": "Insider dealing outcome given risk level"
        },
        
        "cross_desk_collusion": {
            "low_risk": [0.96, 0.03, 0.01],     # [No collusion, Possible, Likely]
            "medium_risk": [0.65, 0.28, 0.07],
            "high_risk": [0.12, 0.38, 0.50],
            "description": "Cross-desk collusion outcome given risk level"
        },
        
        "economic_withholding": {
            "no_withholding": [0.95, 0.05],      # [No withholding, Withholding] (binary)
            "possible_withholding": [0.70, 0.30],
            "likely_withholding": [0.20, 0.80],
            "description": "Economic withholding outcome given assessment"
        }
    }
    
    @classmethod
    def get_evidence_prior(cls, node_name: str) -> ProbabilityProfile:
        """
        Get probability profile for an evidence node.
        
        Args:
            node_name: Name of the evidence node
            
        Returns:
            ProbabilityProfile with probabilities and documentation
            
        Raises:
            KeyError: If node_name not found in configuration
        """
        if node_name not in cls.EVIDENCE_NODE_PROBABILITIES:
            raise KeyError(f"No probability configuration found for evidence node: {node_name}")
        
        return cls.EVIDENCE_NODE_PROBABILITIES[node_name]
    
    @classmethod
    def get_intermediate_params(cls, node_type: str) -> Dict:
        """
        Get parameters for intermediate node CPT creation.
        
        Args:
            node_type: Type of intermediate node (e.g., 'market_impact')
            
        Returns:
            Dictionary with noisy-OR parameters
            
        Raises:
            KeyError: If node_type not found in configuration
        """
        if node_type not in cls.INTERMEDIATE_NODE_PARAMETERS:
            raise KeyError(f"No parameters found for intermediate node type: {node_type}")
        
        return cls.INTERMEDIATE_NODE_PARAMETERS[node_type]
    
    @classmethod
    def get_outcome_probabilities(cls, outcome_type: str) -> Dict:
        """
        Get probability distributions for outcome nodes.
        
        Args:
            outcome_type: Type of outcome (e.g., 'spoofing')
            
        Returns:
            Dictionary with outcome probability distributions
            
        Raises:
            KeyError: If outcome_type not found in configuration
        """
        if outcome_type not in cls.OUTCOME_PROBABILITIES:
            raise KeyError(f"No outcome probabilities found for: {outcome_type}")
        
        return cls.OUTCOME_PROBABILITIES[outcome_type]
    
    @classmethod
    def create_evidence_cpd(cls, node_name: str, variable_card: int = 3):
        """
        Create a TabularCPD for an evidence node using configured probabilities.
        
        Args:
            node_name: Name of the evidence node
            variable_card: Number of states (default 3)
            
        Returns:
            TabularCPD configured with appropriate probabilities
        """
        from pgmpy.factors.discrete import TabularCPD
        
        profile = cls.get_evidence_prior(node_name)
        
        if variable_card == 2:
            # Binary node - use low_state and high_state only
            values = [[profile.low_state], [profile.high_state]]
        elif variable_card == 3:
            # Ternary node - use all three states
            values = profile.as_list()
        else:
            raise ValueError(f"Unsupported variable_card: {variable_card}. Only 2 and 3 are supported.")
        
        return TabularCPD(
            variable=node_name,
            variable_card=variable_card,
            values=values
        )
    
    @classmethod
    def validate_all_probabilities(cls) -> bool:
        """
        Validate all configured probabilities sum to 1.0.
        
        Returns:
            True if all probabilities are valid
            
        Raises:
            ValueError: If any probability configuration is invalid
        """
        # Validate evidence profiles
        for evidence_type, profile in cls.EVIDENCE_PROFILES.items():
            try:
                profile.__post_init__()  # Trigger validation
            except ValueError as e:
                raise ValueError(f"Invalid probability profile for {evidence_type}: {e}")
        
        # Validate specific evidence nodes
        for node_name, profile in cls.EVIDENCE_NODE_PROBABILITIES.items():
            try:
                profile.__post_init__()  # Trigger validation
            except ValueError as e:
                raise ValueError(f"Invalid probability configuration for {node_name}: {e}")
        
        # Validate outcome probabilities
        for outcome, probs in cls.OUTCOME_PROBABILITIES.items():
            for risk_level, prob_list in probs.items():
                if risk_level == "description":
                    continue
                if not (0.99 <= sum(prob_list) <= 1.01):
                    raise ValueError(f"Invalid outcome probabilities for {outcome}.{risk_level}: {prob_list}")
        
        return True


# Configuration validation moved to explicit method call
# Call ProbabilityConfig.validate_all_probabilities() during testing or deployment
# to avoid import-time performance overhead