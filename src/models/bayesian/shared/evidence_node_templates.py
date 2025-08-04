"""
Evidence Node Templates for Enhanced Bayesian Models

This module provides templates for common evidence node patterns across models,
promoting consistency and reusability in 4-parent CPT structures.

Design Principles:
1. Model-specific customization with common base patterns
2. Regulatory alignment for evidence types
3. Consistent state definitions across similar evidence types
4. Optimized fallback priors based on surveillance data
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class EvidenceNodeTemplate:
    """Template for evidence node configuration"""
    name: str
    states: List[str]
    description: str
    fallback_prior: List[float]
    regulatory_basis: str = ""
    evidence_category: str = ""
    
    def __post_init__(self):
        """Validate probability distributions and state consistency"""
        if len(self.fallback_prior) != len(self.states):
            raise ValueError(
                f"Length of fallback_prior ({len(self.fallback_prior)}) must match "
                f"length of states ({len(self.states)}) for node '{self.name}'"
            )
        
        prior_sum = sum(self.fallback_prior)
        if abs(prior_sum - 1.0) > 1e-10:  # Using epsilon for float comparison
            raise ValueError(
                f"Fallback prior probabilities must sum to 1.0, got {prior_sum:.10f} "
                f"for node '{self.name}'"
            )
        
        # Validate that all probabilities are non-negative
        for i, prob in enumerate(self.fallback_prior):
            if prob < 0:
                raise ValueError(
                    f"Probability values must be non-negative, got {prob} at index {i} "
                    f"for node '{self.name}'"
                )
        
        # Validate that states list is not empty
        if not self.states:
            raise ValueError(f"States list cannot be empty for node '{self.name}'")
        
        # Validate that all state names are non-empty strings
        for i, state in enumerate(self.states):
            if not isinstance(state, str) or not state.strip():
                raise ValueError(
                    f"State names must be non-empty strings, got '{state}' at index {i} "
                    f"for node '{self.name}'"
                )


class EvidenceNodeTemplates:
    """Templates for common evidence node patterns across models"""
    
    @staticmethod
    def create_volume_patterns_node(model_type: str) -> Dict[str, Any]:
        """Volume-based evidence patterns"""
        descriptions = {
            "wash_trade_detection": "Volume clustering and artificial inflation patterns",
            "circular_trading": "Volume circulation and conservation analysis",
            "market_cornering": "Position accumulation and volume concentration patterns",
            "commodity_manipulation": "Physical volume control and artificial scarcity patterns"
        }
        
        return {
            "name": "VolumePatterns",
            "states": ["normal", "suspicious", "highly_suspicious"],
            "description": descriptions.get(model_type, "Volume-based manipulation patterns"),
            "fallback_prior": [0.70, 0.25, 0.05],
            "regulatory_basis": "MAR Article 12 - Volume manipulation indicators",
            "evidence_category": "market_structure"
        }
        
    @staticmethod  
    def create_timing_patterns_node(model_type: str) -> Dict[str, Any]:
        """Timing-based evidence patterns"""
        descriptions = {
            "wash_trade_detection": "Execution timing and coordination patterns",
            "circular_trading": "Circular timing patterns and sequence analysis",
            "cross_desk_collusion": "Cross-desk communication and execution timing",
            "market_cornering": "Strategic timing for position accumulation"
        }
        
        return {
            "name": "TimingPatterns", 
            "states": ["normal", "suspicious", "highly_suspicious"],
            "description": descriptions.get(model_type, "Timing-based coordination patterns"),
            "fallback_prior": [0.75, 0.20, 0.05],
            "regulatory_basis": "MAR Article 8 - Timing coordination indicators",
            "evidence_category": "behavioral_patterns"
        }
    
    @staticmethod
    def create_price_patterns_node(model_type: str) -> Dict[str, Any]:
        """Price impact and manipulation patterns"""
        descriptions = {
            "wash_trade_detection": "Price impact and spread behavior analysis",
            "commodity_manipulation": "Artificial pricing and benchmark manipulation",
            "market_cornering": "Price inflation and artificial scarcity pricing",
            "economic_withholding": "Price targeting and strategic pricing behavior"
        }
        
        return {
            "name": "PricePatterns",
            "states": ["normal", "suspicious", "highly_suspicious"], 
            "description": descriptions.get(model_type, "Price manipulation and impact patterns"),
            "fallback_prior": [0.80, 0.15, 0.05],
            "regulatory_basis": "MAR Article 12 - Price manipulation definition",
            "evidence_category": "market_impact"
        }
    
    @staticmethod
    def create_account_relationships_node(model_type: str) -> Dict[str, Any]:
        """Account linkage and control patterns"""
        descriptions = {
            "wash_trade_detection": "Account linkage and control indicators", 
            "circular_trading": "Entity relationships and beneficial ownership",
            "cross_desk_collusion": "Cross-entity relationships and coordination"
        }
        
        return {
            "name": "AccountRelationships",
            "states": ["normal", "suspicious", "highly_suspicious"],
            "description": descriptions.get(model_type, "Account relationships and control patterns"),
            "fallback_prior": [0.60, 0.30, 0.10],
            "regulatory_basis": "MiFID II - Beneficial ownership requirements",
            "evidence_category": "entity_relationships"
        }
    
    @staticmethod
    def create_communication_patterns_node(model_type: str) -> Dict[str, Any]:
        """Communication and coordination evidence"""
        descriptions = {
            "cross_desk_collusion": "Cross-desk communications and information sharing",
            "insider_dealing": "Material non-public information communication",
            "market_cornering": "Coordination communications for market control"
        }
        
        return {
            "name": "CommunicationPatterns",
            "states": ["normal", "suspicious", "highly_suspicious"],
            "description": descriptions.get(model_type, "Communication and coordination patterns"),
            "fallback_prior": [0.85, 0.12, 0.03],
            "regulatory_basis": "MAR Article 8 - Information sharing restrictions",
            "evidence_category": "communication_analysis"
        }
    
    @staticmethod
    def create_capacity_analysis_node(model_type: str) -> Dict[str, Any]:
        """Capacity and resource control patterns"""
        descriptions = {
            "economic_withholding": "Available capacity and utilization analysis",
            "commodity_manipulation": "Physical market control and storage capacity",
            "market_cornering": "Supply control and inventory management"
        }
        
        return {
            "name": "CapacityAnalysis",
            "states": ["normal", "suspicious", "highly_suspicious"],
            "description": descriptions.get(model_type, "Capacity control and manipulation patterns"),
            "fallback_prior": [0.65, 0.25, 0.10],
            "regulatory_basis": "STOR - Physical withholding regulations",
            "evidence_category": "resource_control"
        }
    
    @staticmethod
    def create_cost_structure_node(model_type: str) -> Dict[str, Any]:
        """Economic cost and benefit analysis"""
        descriptions = {
            "economic_withholding": "Marginal costs and withholding economics",
            "commodity_manipulation": "Cost-benefit analysis of manipulation schemes",
            "cross_desk_collusion": "Economic benefits and profit sharing analysis"
        }
        
        return {
            "name": "CostStructure",
            "states": ["normal", "suspicious", "highly_suspicious"],
            "description": descriptions.get(model_type, "Economic cost-benefit analysis patterns"),
            "fallback_prior": [0.70, 0.22, 0.08],
            "regulatory_basis": "Economic manipulation cost analysis",
            "evidence_category": "economic_analysis"
        }
    
    @staticmethod
    def create_market_conditions_node(model_type: str) -> Dict[str, Any]:
        """Market environment and conditions analysis"""
        descriptions = {
            "economic_withholding": "Demand-supply imbalance and market power analysis",
            "commodity_manipulation": "Market structure and competitive dynamics",
            "market_cornering": "Market liquidity and concentration analysis"
        }
        
        return {
            "name": "MarketConditions",
            "states": ["normal", "suspicious", "highly_suspicious"],
            "description": descriptions.get(model_type, "Market conditions and environment analysis"),
            "fallback_prior": [0.75, 0.20, 0.05],
            "regulatory_basis": "Market structure analysis requirements",
            "evidence_category": "market_environment"
        }
    
    @staticmethod
    def create_information_advantage_node(model_type: str) -> Dict[str, Any]:
        """Information asymmetry and advantage patterns"""
        descriptions = {
            "cross_desk_collusion": "Non-public information access and timing advantage",
            "insider_dealing": "Material non-public information access and usage",
            "commodity_manipulation": "Information manipulation and false reporting"
        }
        
        return {
            "name": "InformationAdvantage",
            "states": ["normal", "suspicious", "highly_suspicious"],
            "description": descriptions.get(model_type, "Information advantage and asymmetry patterns"),
            "fallback_prior": [0.80, 0.15, 0.05],
            "regulatory_basis": "MAR Article 7 - Inside information definition",
            "evidence_category": "information_analysis"
        }


class ModelSpecificTemplates:
    """Model-specific evidence node template collections"""
    
    @staticmethod
    def get_wash_trade_templates() -> List[Dict[str, Any]]:
        """Get all evidence node templates for wash trade detection"""
        return [
            EvidenceNodeTemplates.create_volume_patterns_node("wash_trade_detection"),
            EvidenceNodeTemplates.create_timing_patterns_node("wash_trade_detection"),
            EvidenceNodeTemplates.create_price_patterns_node("wash_trade_detection"),
            EvidenceNodeTemplates.create_account_relationships_node("wash_trade_detection")
        ]
    
    @staticmethod
    def get_circular_trading_templates() -> List[Dict[str, Any]]:
        """Get all evidence node templates for circular trading"""
        return [
            {
                "name": "CircularityPatterns",
                "states": ["normal", "suspicious", "highly_suspicious"],
                "description": "Trade chain analysis and return path detection",
                "fallback_prior": [0.75, 0.20, 0.05],
                "regulatory_basis": "Circular trading pattern identification",
                "evidence_category": "pattern_analysis"
            },
            {
                "name": "ParticipantAnalysis", 
                "states": ["normal", "suspicious", "highly_suspicious"],
                "description": "Entity relationships and role rotation analysis",
                "fallback_prior": [0.70, 0.25, 0.05],
                "regulatory_basis": "Entity relationship analysis",
                "evidence_category": "entity_relationships"
            },
            EvidenceNodeTemplates.create_volume_patterns_node("circular_trading"),
            {
                "name": "MarketImpactAnalysis",
                "states": ["normal", "suspicious", "highly_suspicious"], 
                "description": "Price effect and liquidity impact analysis",
                "fallback_prior": [0.80, 0.15, 0.05],
                "regulatory_basis": "Market impact assessment",
                "evidence_category": "market_impact"
            }
        ]
    
    @staticmethod
    def get_cross_desk_collusion_templates() -> List[Dict[str, Any]]:
        """Get all evidence node templates for cross desk collusion"""
        return [
            EvidenceNodeTemplates.create_communication_patterns_node("cross_desk_collusion"),
            {
                "name": "TradingCoordination",
                "states": ["normal", "suspicious", "highly_suspicious"],
                "description": "Synchronized execution and position coordination",
                "fallback_prior": [0.75, 0.20, 0.05],
                "regulatory_basis": "Trading coordination analysis",
                "evidence_category": "coordination_patterns"
            },
            EvidenceNodeTemplates.create_information_advantage_node("cross_desk_collusion"),
            {
                "name": "EconomicBenefit",
                "states": ["normal", "suspicious", "highly_suspicious"],
                "description": "Profit sharing and risk mitigation analysis",
                "fallback_prior": [0.70, 0.25, 0.05],
                "regulatory_basis": "Economic benefit analysis",
                "evidence_category": "economic_analysis"
            }
        ]
    
    @staticmethod
    def get_economic_withholding_templates() -> List[Dict[str, Any]]:
        """Get all evidence node templates for economic withholding"""
        return [
            EvidenceNodeTemplates.create_capacity_analysis_node("economic_withholding"),
            EvidenceNodeTemplates.create_cost_structure_node("economic_withholding"),
            EvidenceNodeTemplates.create_market_conditions_node("economic_withholding"),
            {
                "name": "StrategicBehavior",
                "states": ["normal", "suspicious", "highly_suspicious"],
                "description": "Withholding timing and capacity manipulation patterns",
                "fallback_prior": [0.75, 0.20, 0.05],
                "regulatory_basis": "Strategic withholding behavior analysis",
                "evidence_category": "behavioral_patterns"
            }
        ]
    
    @staticmethod
    def get_market_cornering_templates() -> List[Dict[str, Any]]:
        """Get all evidence node templates for market cornering"""
        return [
            {
                "name": "PositionAccumulation",
                "states": ["normal", "suspicious", "highly_suspicious"],
                "description": "Position concentration and accumulation analysis",
                "fallback_prior": [0.70, 0.25, 0.05],
                "regulatory_basis": "Position concentration limits",
                "evidence_category": "position_analysis"
            },
            {
                "name": "SupplyControl",
                "states": ["normal", "suspicious", "highly_suspicious"], 
                "description": "Supply restriction and inventory control patterns",
                "fallback_prior": [0.75, 0.20, 0.05],
                "regulatory_basis": "Supply manipulation analysis",
                "evidence_category": "resource_control"
            },
            EvidenceNodeTemplates.create_price_patterns_node("market_cornering"),
            {
                "name": "MarketDomination",
                "states": ["normal", "suspicious", "highly_suspicious"],
                "description": "Market power abuse and competitive exclusion",
                "fallback_prior": [0.80, 0.15, 0.05],
                "regulatory_basis": "Market dominance analysis",
                "evidence_category": "market_structure"
            }
        ]
    
    @staticmethod
    def get_commodity_manipulation_templates() -> List[Dict[str, Any]]:
        """Get all evidence node templates for commodity manipulation"""
        return [
            {
                "name": "PhysicalMarketControl",
                "states": ["normal", "suspicious", "highly_suspicious"],
                "description": "Storage and transportation control analysis",
                "fallback_prior": [0.75, 0.20, 0.05],
                "regulatory_basis": "Physical market control analysis",
                "evidence_category": "resource_control"
            },
            {
                "name": "FinancialPositions",
                "states": ["normal", "suspicious", "highly_suspicious"],
                "description": "Futures positions and derivatives exposure analysis", 
                "fallback_prior": [0.70, 0.25, 0.05],
                "regulatory_basis": "Financial position reporting requirements",
                "evidence_category": "position_analysis"
            },
            {
                "name": "InformationManipulation",
                "states": ["normal", "suspicious", "highly_suspicious"],
                "description": "False reporting and rumor spreading analysis",
                "fallback_prior": [0.85, 0.12, 0.03],
                "regulatory_basis": "Information manipulation prohibitions",
                "evidence_category": "information_analysis"
            },
            EvidenceNodeTemplates.create_price_patterns_node("commodity_manipulation")
        ]


def get_model_templates(model_type: str) -> List[Dict[str, Any]]:
    """Get evidence node templates for a specific model type"""
    template_map = {
        "wash_trade_detection": ModelSpecificTemplates.get_wash_trade_templates,
        "circular_trading": ModelSpecificTemplates.get_circular_trading_templates,
        "cross_desk_collusion": ModelSpecificTemplates.get_cross_desk_collusion_templates,
        "economic_withholding": ModelSpecificTemplates.get_economic_withholding_templates,
        "market_cornering": ModelSpecificTemplates.get_market_cornering_templates,
        "commodity_manipulation": ModelSpecificTemplates.get_commodity_manipulation_templates
    }
    
    if model_type not in template_map:
        raise ValueError(f"No templates available for model type: {model_type}")
    
    return template_map[model_type]()