"""
Typology Template Manager for CPT Library
This module provides template management for different risk typologies,
enabling consistent CPT creation across models.
"""
from typing import Dict, List, Optional, Any
from .typed_cpt import CPTType


class TypologyTemplateManager:
    """
    Manager for CPT templates by typology.
    Provides standardized templates for creating CPTs
    across different risk typologies.
    """

    def __init__(self):
        """Initialize template manager."""
        self.templates: Dict[str, Dict[str, Any]] = {}
        self._load_default_templates()

    def _load_default_templates(self) -> None:
        """Load default typology templates."""
        # Insider Dealing Templates
        self.templates["insider_dealing"] = {
            "MaterialInfo": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["None", "Limited", "Substantial"],
                "description": "Access to material non-public information",
                "fallback_prior": [0.7, 0.2, 0.1],
                "probability_rationale": "Based on MAR Article 8 interpretation and FCA enforcement patterns",
                "threshold_justification": "Substantial information access indicates high insider dealing risk"
            },
            "Timing": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["Random", "Correlated", "Highly_Correlated"],
                "description": "Timing correlation with material events",
                "fallback_prior": [0.6, 0.3, 0.1],
                "probability_rationale": "Temporal correlation is key indicator per ESMA guidelines",
                "threshold_justification": "High correlation suggests non-random trading behavior"
            },
            "TradingActivity": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["Normal", "Elevated", "Extreme"],
                "description": "Trading activity patterns",
                "fallback_prior": [0.8, 0.15, 0.05],
                "probability_rationale": "Activity spikes around material events indicate potential insider trading",
                "threshold_justification": "Extreme activity requires investigation per STOR requirements"
            }
        }
        # Spoofing Templates
        self.templates["spoofing"] = {
            "OrderPattern": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["Normal", "Suspicious", "Highly_Suspicious"],
                "description": "Order placement and cancellation patterns",
                "fallback_prior": [0.85, 0.12, 0.03],
                "probability_rationale": "Based on MAR Article 12(1)(a) and ESMA spoofing guidance",
                "threshold_justification": "Highly suspicious patterns require immediate investigation"
            },
            "CancellationRate": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["Low", "Medium", "High"],
                "description": "Order cancellation rate analysis",
                "fallback_prior": [0.6, 0.3, 0.1],
                "probability_rationale": "High cancellation rates are primary spoofing indicator",
                "threshold_justification": "High cancellation rates suggest deceptive trading intent"
            },
            "PriceMovement": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["No_Impact", "Minor_Impact", "Significant_Impact"],
                "description": "Price movement correlation with order activity",
                "fallback_prior": [0.7, 0.2, 0.1],
                "probability_rationale": "Price impact demonstrates market manipulation effect",
                "threshold_justification": "Significant impact indicates successful market manipulation"
            }
        }
        # Wash Trade Detection Templates
        self.templates["wash_trade_detection"] = {
            "SelfTrading": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["None", "Limited", "Extensive"],
                "description": "Self-trading patterns detection",
                "fallback_prior": [0.9, 0.08, 0.02],
                "probability_rationale": "Self-trading is primary wash trade indicator per MAR Article 12",
                "threshold_justification": "Extensive self-trading patterns indicate wash trading activity"
            },
            "EconomicPurpose": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["Clear", "Unclear", "Absent"],
                "description": "Economic purpose of trading activity",
                "fallback_prior": [0.8, 0.15, 0.05],
                "probability_rationale": "Lack of economic purpose is key wash trade characteristic",
                "threshold_justification": "Absent economic purpose strongly suggests wash trading"
            },
            "VolumePattern": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["Normal", "Elevated", "Artificial"],
                "description": "Trading volume pattern analysis",
                "fallback_prior": [0.75, 0.2, 0.05],
                "probability_rationale": "Artificial volume inflation is wash trading objective",
                "threshold_justification": "Artificial volume patterns indicate market manipulation"
            }
        }
        # Cross-Typology Shared Templates
        self.templates["cross_typology"] = {
            "RegulatoryRisk": {
                "cpt_type": CPTType.CROSS_TYPOLOGY,
                "node_states": ["Low", "Medium", "High", "Critical"],
                "description": "Overall regulatory risk assessment",
                "fallback_prior": [0.6, 0.25, 0.12, 0.03],
                "probability_rationale": "Cross-typology risk aggregation for regulatory reporting",
                "threshold_justification": "Critical risk requires immediate regulatory notification"
            },
            "MarketImpact": {
                "cpt_type": CPTType.CROSS_TYPOLOGY,
                "node_states": ["Minimal", "Moderate", "Significant", "Severe"],
                "description": "Market impact assessment",
                "fallback_prior": [0.7, 0.2, 0.08, 0.02],
                "probability_rationale": "Market impact common across manipulation typologies",
                "threshold_justification": "Severe impact indicates systemic market abuse"
            }
        }
        # Economic Withholding Templates
        self.templates["economic_withholding"] = {
            "CapacityWithheld": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["None", "Partial", "Substantial"],
                "description": "Economic capacity withholding patterns",
                "fallback_prior": [0.8, 0.15, 0.05],
                "probability_rationale": "Capacity withholding is primary indicator of economic manipulation",
                "threshold_justification": "Substantial withholding suggests market manipulation intent"
            },
            "PriceInflation": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["Normal", "Elevated", "Extreme"],
                "description": "Price inflation due to artificial scarcity",
                "fallback_prior": [0.7, 0.25, 0.05],
                "probability_rationale": "Price inflation indicates successful economic manipulation",
                "threshold_justification": "Extreme inflation requires immediate intervention"
            }
        }
        # Circular Trading Templates
        self.templates["circular_trading"] = {
            "CircularPattern": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["None", "Potential", "Confirmed"],
                "description": "Circular trading pattern detection",
                "fallback_prior": [0.85, 0.12, 0.03],
                "probability_rationale": "Circular patterns indicate coordinated market manipulation",
                "threshold_justification": "Confirmed patterns require regulatory investigation"
            },
            "CoordinationEvidence": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["None", "Circumstantial", "Direct"],
                "description": "Evidence of coordination between parties",
                "fallback_prior": [0.8, 0.15, 0.05],
                "probability_rationale": "Coordination evidence supports circular trading allegations",
                "threshold_justification": "Direct evidence confirms market manipulation scheme"
            }
        }
        # Commodity Manipulation Templates
        self.templates["commodity_manipulation"] = {
            "PhysicalPosition": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["Normal", "Dominant", "Monopolistic"],
                "description": "Physical commodity position analysis",
                "fallback_prior": [0.75, 0.2, 0.05],
                "probability_rationale": "Dominant positions enable commodity manipulation",
                "threshold_justification": "Monopolistic positions indicate manipulation capability"
            },
            "DeliveryManipulation": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["None", "Suspected", "Confirmed"],
                "description": "Delivery manipulation patterns",
                "fallback_prior": [0.9, 0.08, 0.02],
                "probability_rationale": "Delivery manipulation is key commodity abuse technique",
                "threshold_justification": "Confirmed manipulation requires enforcement action"
            }
        }
        # Cross-Desk Collusion Templates
        self.templates["cross_desk_collusion"] = {
            "InformationSharing": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["None", "Limited", "Extensive"],
                "description": "Cross-desk information sharing patterns",
                "fallback_prior": [0.8, 0.15, 0.05],
                "probability_rationale": "Information sharing enables coordinated manipulation",
                "threshold_justification": "Extensive sharing indicates collusion scheme"
            },
            "CoordinatedActivity": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["Independent", "Correlated", "Synchronized"],
                "description": "Coordinated trading activity across desks",
                "fallback_prior": [0.7, 0.25, 0.05],
                "probability_rationale": "Synchronized activity suggests collusion",
                "threshold_justification": "Synchronization indicates deliberate coordination"
            }
        }
        # Market Cornering Templates
        self.templates["market_cornering"] = {
            "MarketControl": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["None", "Partial", "Dominant"],
                "description": "Market control and cornering patterns",
                "fallback_prior": [0.85, 0.12, 0.03],
                "probability_rationale": "Market control is prerequisite for cornering",
                "threshold_justification": "Dominant control indicates cornering attempt"
            },
            "SupplyRestriction": {
                "cpt_type": CPTType.EVIDENCE_NODE,
                "node_states": ["Normal", "Restricted", "Artificially_Scarce"],
                "description": "Supply restriction and artificial scarcity",
                "fallback_prior": [0.8, 0.15, 0.05],
                "probability_rationale": "Supply restriction enables market cornering",
                "threshold_justification": "Artificial scarcity confirms cornering strategy"
            }
        }

    def get_template(self, typology: str, node_name: str) -> Optional[Dict[str, Any]]:
        """
        Get template for specific typology and node.
        Args:
            typology: Risk typology
            node_name: Node name
        Returns:
            Template dictionary or None if not found
        """
        if typology in self.templates:
            return self.templates[typology].get(node_name)
        return None

    def get_typology_templates(self, typology: str) -> Dict[str, Any]:
        """Get all templates for a typology."""
        return self.templates.get(typology, {})

    def get_available_typologies(self) -> List[str]:
        """Get list of available typologies."""
        return list(self.templates.keys())

    def get_available_nodes(self, typology: str) -> List[str]:
        """Get available nodes for a typology."""
        if typology in self.templates:
            return list(self.templates[typology].keys())
        return []

    def add_template(self, typology: str, node_name: str, template: Dict[str, Any]) -> None:
        """
        Add a new template.
        Args:
            typology: Risk typology
            node_name: Node name
            template: Template definition
        """
        if typology not in self.templates:
            self.templates[typology] = {}
        self.templates[typology][node_name] = template

    def get_cross_typology_templates(self) -> Dict[str, Any]:
        """Get templates that can be shared across typologies."""
        return self.templates.get("cross_typology", {})
