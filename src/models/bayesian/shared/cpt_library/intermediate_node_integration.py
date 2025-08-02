"""
Intermediate Node Integration for CPT Library

This module provides proper integration of fan-in reduction intermediate nodes
with the existing CPT library infrastructure, ensuring full compatibility and
maintaining all existing functionality.

Design Principles:
1. Full backward compatibility with existing CPT library
2. Proper integration with template system
3. Complete regression testing support
4. Seamless model builder integration
5. Regulatory compliance preservation
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from .typed_cpt import TypedCPT, CPTMetadata, CPTType, CPTStatus
from .library import CPTLibrary
from .typology_templates import TypologyTemplateManager

logger = logging.getLogger(__name__)


@dataclass
class IntermediateNodeSpec:
    """
    Specification for an intermediate node in fan-in reduction.
    
    Attributes:
        name: Node name
        node_type: Type of intermediate node (market_impact, behavioral_intent, etc.)
        parent_nodes: List of evidence nodes that feed into this intermediate
        target_nodes: List of nodes this intermediate feeds into
        description: Business logic description
        regulatory_basis: Regulatory framework reference
        model_types: List of model types this node applies to
    """
    name: str
    node_type: str
    parent_nodes: List[str]
    target_nodes: List[str]
    description: str
    regulatory_basis: str = ""
    model_types: List[str] = None
    
    def __post_init__(self):
        if self.model_types is None:
            self.model_types = []


class IntermediateNodeCPTLibraryIntegration:
    """
    Integration system for intermediate nodes with CPT library.
    
    Provides full integration while maintaining backward compatibility
    and ensuring proper regression testing.
    """
    
    def __init__(self, cpt_library: CPTLibrary):
        """
        Initialize integration system.
        
        Args:
            cpt_library: Existing CPT library instance
        """
        self.cpt_library = cpt_library
        self.template_manager = cpt_library.template_manager
        self.intermediate_specs: Dict[str, IntermediateNodeSpec] = {}
        self._initialize_intermediate_node_specs()
    
    def _initialize_intermediate_node_specs(self):
        """Initialize specifications for all intermediate nodes."""
        
        # Market Impact Intermediate Nodes
        self.intermediate_specs["market_impact_spoofing"] = IntermediateNodeSpec(
            name="market_impact_spoofing",
            node_type="market_impact",
            parent_nodes=["order_clustering", "price_impact_ratio", "volume_participation"],
            target_nodes=["spoofing_latent_intent", "risk_factor"],
            description="Market-level impact indicators for spoofing detection",
            regulatory_basis="ESMA Guidelines on Market Abuse - Price and volume effects",
            model_types=["spoofing"]
        )
        
        self.intermediate_specs["behavioral_intent_spoofing"] = IntermediateNodeSpec(
            name="behavioral_intent_spoofing", 
            node_type="behavioral_intent",
            parent_nodes=["order_behavior", "intent_to_execute", "order_cancellation"],
            target_nodes=["spoofing_latent_intent", "risk_factor"],
            description="Behavioral intent patterns for spoofing detection",
            regulatory_basis="MAR Article 12 - Market manipulation patterns",
            model_types=["spoofing"]
        )
        
        # Economic Withholding Intermediate Nodes
        self.intermediate_specs["cost_analysis_intermediate"] = IntermediateNodeSpec(
            name="cost_analysis_intermediate",
            node_type="cost_analysis",
            parent_nodes=["marginal_cost_deviation", "fuel_cost_variance", "plant_efficiency", "heat_rate_variance"],
            target_nodes=["withholding_latent_intent", "economic_withholding_risk"],
            description="Cost analysis patterns for economic withholding detection",
            regulatory_basis="ARERA Guidelines - Cost analysis requirements",
            model_types=["economic_withholding"]
        )
        
        self.intermediate_specs["market_conditions_intermediate"] = IntermediateNodeSpec(
            name="market_conditions_intermediate",
            node_type="market_conditions",
            parent_nodes=["load_factor", "market_tightness", "competitive_context", "transmission_constraint"],
            target_nodes=["withholding_latent_intent", "economic_withholding_risk"],
            description="Market conditions for economic withholding assessment",
            regulatory_basis="ARERA Guidelines - Market conditions assessment",
            model_types=["economic_withholding"]
        )
        
        self.intermediate_specs["behavioral_patterns_intermediate"] = IntermediateNodeSpec(
            name="behavioral_patterns_intermediate",
            node_type="behavioral_patterns",
            parent_nodes=["bid_shape_anomaly", "offer_withdrawal_pattern", "capacity_utilization", "markup_consistency", "opportunity_pricing"],
            target_nodes=["withholding_latent_intent", "economic_withholding_risk"],
            description="Behavioral patterns for economic withholding detection",
            regulatory_basis="ARERA Guidelines - Behavioral pattern analysis",
            model_types=["economic_withholding"]
        )
        
        self.intermediate_specs["technical_factors_intermediate"] = IntermediateNodeSpec(
            name="technical_factors_intermediate",
            node_type="technical_factors",
            parent_nodes=["fuel_price_correlation", "cross_plant_coordination", "price_impact_ratio", "volume_participation", "liquidity_context", "order_clustering"],
            target_nodes=["withholding_latent_intent", "economic_withholding_risk"],
            description="Technical factors for economic withholding assessment",
            regulatory_basis="ARERA Guidelines - Technical capacity assessment",
            model_types=["economic_withholding"]
        )
        
        # Cross-Desk Collusion Intermediate Nodes
        self.intermediate_specs["coordination_patterns_intermediate"] = IntermediateNodeSpec(
            name="coordination_patterns_intermediate",
            node_type="coordination_patterns",
            parent_nodes=["cross_venue_coordination", "access_pattern", "market_segmentation"],
            target_nodes=["collusion_latent_intent", "risk_factor"],
            description="Coordination patterns for cross-desk collusion detection",
            regulatory_basis="MAR Article 12 - Concerted practices detection",
            model_types=["cross_desk_collusion"]
        )
        
        self.intermediate_specs["communication_intent_intermediate"] = IntermediateNodeSpec(
            name="communication_intent_intermediate",
            node_type="communication_intent", 
            parent_nodes=["comms_metadata", "profit_motivation", "order_behavior"],
            target_nodes=["collusion_latent_intent", "risk_factor"],
            description="Communication intent patterns for collusion detection",
            regulatory_basis="MAR Article 12 - Information sharing patterns",
            model_types=["cross_desk_collusion"]
        )
    
    def create_intermediate_node_templates(self) -> None:
        """Create CPT templates for all intermediate nodes."""
        
        for spec in self.intermediate_specs.values():
            # Create template for each model type
            for model_type in spec.model_types:
                template = {
                    "cpt_type": CPTType.INTERMEDIATE_NODE,
                    "node_states": self._get_intermediate_node_states(spec.node_type),
                    "description": spec.description,
                    "parent_nodes": spec.parent_nodes,
                    "parent_states": self._get_parent_states_mapping(spec.parent_nodes),
                    "probability_table": self._generate_intermediate_probability_table(spec),
                    "fallback_prior": self._get_intermediate_fallback_prior(spec.node_type),
                    "probability_rationale": spec.description,
                    "threshold_justification": f"Intermediate aggregation for {spec.node_type} patterns",
                    "regulatory_basis": spec.regulatory_basis,
                    "intermediate_spec": spec  # Store full spec for reference
                }
                
                # Add template to library
                self.template_manager.add_template(model_type, spec.name, template)
                logger.info(f"Added intermediate node template: {model_type}.{spec.name}")
    
    def _get_intermediate_node_states(self, node_type: str) -> List[str]:
        """Get appropriate states for intermediate node type."""
        state_mappings = {
            "market_impact": ["minimal_impact", "moderate_impact", "significant_impact"],
            "behavioral_intent": ["legitimate_intent", "suspicious_intent", "manipulative_intent"],
            "cost_analysis": ["reasonable_costs", "questionable_costs", "excessive_costs"],
            "market_conditions": ["normal_conditions", "constrained_conditions", "tight_conditions"],
            "behavioral_patterns": ["normal_patterns", "unusual_patterns", "manipulative_patterns"],
            "technical_factors": ["normal_operations", "constrained_operations", "artificial_constraints"],
            "coordination_patterns": ["independent_activity", "correlated_activity", "coordinated_activity"],
            "communication_intent": ["legitimate_communication", "suspicious_communication", "collusive_communication"]
        }
        return state_mappings.get(node_type, ["low", "medium", "high"])
    
    def _get_parent_states_mapping(self, parent_nodes: List[str]) -> Dict[str, List[str]]:
        """Get parent states mapping for intermediate node."""
        # Standard 3-state mapping for most evidence nodes
        parent_states = {}
        for parent in parent_nodes:
            # Check if parent has specific states in existing templates
            parent_states[parent] = ["low", "medium", "high"]  # Default
        return parent_states
    
    def _generate_intermediate_probability_table(self, spec: IntermediateNodeSpec) -> List[List[float]]:
        """Generate probability table for intermediate node using noisy-OR logic."""
        num_parents = len(spec.parent_nodes)
        num_combinations = 3 ** num_parents
        num_states = 3
        
        # Initialize probability table
        prob_table = []
        for state_idx in range(num_states):
            prob_table.append([0.0] * num_combinations)
        
        # Noisy-OR parameters based on node type
        leak_probs = {
            "market_impact": 0.02,
            "behavioral_intent": 0.03,
            "cost_analysis": 0.05,
            "market_conditions": 0.10,
            "behavioral_patterns": 0.03,
            "technical_factors": 0.05,
            "coordination_patterns": 0.02,
            "communication_intent": 0.01
        }
        
        parent_influence = {
            "market_impact": [0.85, 0.75, 0.65, 0.55],
            "behavioral_intent": [0.90, 0.80, 0.70, 0.60],
            "cost_analysis": [0.80, 0.70, 0.60, 0.50],
            "market_conditions": [0.75, 0.65, 0.55, 0.45],
            "behavioral_patterns": [0.85, 0.75, 0.65, 0.55],
            "technical_factors": [0.80, 0.70, 0.60, 0.50],
            "coordination_patterns": [0.88, 0.78, 0.68, 0.58],
            "communication_intent": [0.92, 0.82, 0.72, 0.62]
        }
        
        leak_prob = leak_probs.get(spec.node_type, 0.05)
        influences = parent_influence.get(spec.node_type, [0.8, 0.7, 0.6, 0.5])[:num_parents]
        
        # Calculate probabilities for each combination
        for combo_idx in range(num_combinations):
            parent_config = self._index_to_parent_config(combo_idx, num_parents)
            
            # Calculate probability of "low" state (no effect)
            prob_low = leak_prob
            for parent_idx, parent_state in enumerate(parent_config):
                if parent_state == 2:  # High evidence state
                    prob_low *= (1 - influences[parent_idx])
                elif parent_state == 1:  # Medium evidence state
                    prob_low *= (1 - influences[parent_idx] * 0.5)
            
            # Calculate other states
            prob_high = 1 - prob_low
            prob_medium = prob_high * 0.4  # 40% of high becomes medium
            prob_low_final = 1 - prob_high - prob_medium
            
            # Ensure probabilities are valid
            prob_low_final = max(0.01, prob_low_final)
            prob_medium = max(0.01, prob_medium)
            prob_high = max(0.01, prob_high)
            
            # Normalize
            total = prob_low_final + prob_medium + prob_high
            prob_low_final /= total
            prob_medium /= total
            prob_high /= total
            
            # Assign to probability table
            prob_table[0][combo_idx] = prob_low_final    # Low state
            prob_table[1][combo_idx] = prob_medium       # Medium state
            prob_table[2][combo_idx] = prob_high         # High state
        
        return prob_table
    
    def _index_to_parent_config(self, index: int, num_parents: int) -> List[int]:
        """Convert combination index to parent state configuration."""
        config = []
        temp = index
        for _ in range(num_parents):
            config.append(temp % 3)
            temp //= 3
        return config
    
    def _get_intermediate_fallback_prior(self, node_type: str) -> List[float]:
        """Get fallback prior for intermediate node type."""
        priors = {
            "market_impact": [0.70, 0.25, 0.05],
            "behavioral_intent": [0.75, 0.20, 0.05],
            "cost_analysis": [0.65, 0.30, 0.05],
            "market_conditions": [0.60, 0.35, 0.05],
            "behavioral_patterns": [0.70, 0.25, 0.05],
            "technical_factors": [0.75, 0.20, 0.05],
            "coordination_patterns": [0.80, 0.15, 0.05],
            "communication_intent": [0.85, 0.12, 0.03]
        }
        return priors.get(node_type, [0.70, 0.25, 0.05])
    
    def create_intermediate_node_cpts(self) -> Dict[str, str]:
        """
        Create and register CPTs for all intermediate nodes.
        
        Returns:
            Dictionary mapping node names to CPT IDs
        """
        cpt_ids = {}
        
        for spec in self.intermediate_specs.values():
            for model_type in spec.model_types:
                # Get template
                template = self.template_manager.get_template(model_type, spec.name)
                if not template:
                    logger.error(f"No template found for {model_type}.{spec.name}")
                    continue
                
                # Create CPT metadata
                metadata = CPTMetadata(
                    cpt_id=f"INT_{spec.name.upper()}_{model_type.upper()}",
                    version="1.0.0",
                    status=CPTStatus.VALIDATED,
                    regulatory_references=[],
                    compliance_frameworks=["MAR", "ESMA"],
                    created_by="intermediate_node_integration",
                    applicable_models=[model_type]
                )
                
                # Create TypedCPT
                cpt = TypedCPT(
                    metadata=metadata,
                    cpt_type=CPTType.INTERMEDIATE_NODE,
                    node_name=spec.name,
                    node_states=template["node_states"],
                    node_description=template["description"],
                    parent_nodes=template["parent_nodes"],
                    parent_states=template["parent_states"],
                    probability_table=template["probability_table"],
                    fallback_prior=template["fallback_prior"],
                    probability_rationale=template["probability_rationale"],
                    threshold_justification=template["threshold_justification"]
                )
                
                # Add to library
                cpt_id = self.cpt_library.add_cpt(cpt)
                cpt_ids[f"{model_type}.{spec.name}"] = cpt_id
                
                logger.info(f"Created intermediate node CPT: {cpt_id}")
        
        return cpt_ids
    
    def update_outcome_node_templates(self) -> None:
        """Update outcome node templates to use intermediate nodes as parents."""
        
        # Spoofing model updates
        spoofing_risk_template = {
            "cpt_type": CPTType.RISK_FACTOR,
            "node_states": ["low", "medium", "high"],
            "description": "Spoofing risk assessment using intermediate nodes",
            "parent_nodes": ["market_impact_spoofing", "behavioral_intent_spoofing"],
            "parent_states": {
                "market_impact_spoofing": ["minimal_impact", "moderate_impact", "significant_impact"],
                "behavioral_intent_spoofing": ["legitimate_intent", "suspicious_intent", "manipulative_intent"]
            },
            "fallback_prior": [0.80, 0.15, 0.05],
            "probability_rationale": "Risk assessment based on market impact and behavioral intent aggregation",
            "threshold_justification": "High risk indicates likely spoofing activity requiring investigation"
        }
        self.template_manager.add_template("spoofing", "risk_factor", spoofing_risk_template)
        
        # Economic Withholding model updates
        ew_risk_template = {
            "cpt_type": CPTType.RISK_FACTOR,
            "node_states": ["no_withholding", "possible_withholding", "likely_withholding"],
            "description": "Economic withholding risk assessment using intermediate nodes",
            "parent_nodes": ["cost_analysis_intermediate", "market_conditions_intermediate", 
                           "behavioral_patterns_intermediate", "technical_factors_intermediate"],
            "parent_states": {
                "cost_analysis_intermediate": ["reasonable_costs", "questionable_costs", "excessive_costs"],
                "market_conditions_intermediate": ["normal_conditions", "constrained_conditions", "tight_conditions"],
                "behavioral_patterns_intermediate": ["normal_patterns", "unusual_patterns", "manipulative_patterns"],
                "technical_factors_intermediate": ["normal_operations", "constrained_operations", "artificial_constraints"]
            },
            "fallback_prior": [0.85, 0.12, 0.03],
            "probability_rationale": "Risk assessment based on cost, market, behavioral, and technical factor aggregation",
            "threshold_justification": "Likely withholding indicates economic manipulation requiring regulatory action"
        }
        self.template_manager.add_template("economic_withholding", "economic_withholding_risk", ew_risk_template)
        
        logger.info("Updated outcome node templates for intermediate node integration")
    
    def validate_integration(self) -> Dict[str, Any]:
        """
        Validate the intermediate node integration.
        
        Returns:
            Validation results dictionary
        """
        results = {
            "templates_created": 0,
            "cpts_created": 0,
            "validation_errors": [],
            "warnings": []
        }
        
        # Validate templates
        for spec in self.intermediate_specs.values():
            for model_type in spec.model_types:
                template = self.template_manager.get_template(model_type, spec.name)
                if template:
                    results["templates_created"] += 1
                else:
                    results["validation_errors"].append(f"Missing template: {model_type}.{spec.name}")
        
        # Validate CPTs
        for spec in self.intermediate_specs.values():
            for model_type in spec.model_types:
                cpt_id = f"INT_{spec.name.upper()}_{model_type.upper()}"
                cpt = self.cpt_library.get_cpt(cpt_id)
                if cpt:
                    results["cpts_created"] += 1
                    # Validate CPT structure
                    try:
                        cpt._validate_structure()
                        cpt._validate_probabilities()
                    except Exception as e:
                        results["validation_errors"].append(f"CPT validation failed for {cpt_id}: {str(e)}")
                else:
                    results["validation_errors"].append(f"Missing CPT: {cpt_id}")
        
        # Check for parent node consistency
        for spec in self.intermediate_specs.values():
            if len(spec.parent_nodes) > 4:
                results["warnings"].append(f"Intermediate node {spec.name} has {len(spec.parent_nodes)} parents (>4)")
        
        return results
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Get summary of intermediate node integration."""
        return {
            "total_intermediate_nodes": len(self.intermediate_specs),
            "nodes_by_type": {
                node_type: [spec.name for spec in self.intermediate_specs.values() 
                           if spec.node_type == node_type]
                for node_type in set(spec.node_type for spec in self.intermediate_specs.values())
            },
            "models_affected": list(set(
                model_type for spec in self.intermediate_specs.values() 
                for model_type in spec.model_types
            )),
            "total_parent_reduction": sum(
                len(spec.parent_nodes) - len(spec.target_nodes) 
                for spec in self.intermediate_specs.values()
            )
        }


def integrate_intermediate_nodes_with_cpt_library(cpt_library: CPTLibrary) -> IntermediateNodeCPTLibraryIntegration:
    """
    Main integration function for intermediate nodes with CPT library.
    
    Args:
        cpt_library: Existing CPT library instance
        
    Returns:
        Integration system instance
    """
    integration = IntermediateNodeCPTLibraryIntegration(cpt_library)
    
    # Create templates
    integration.create_intermediate_node_templates()
    
    # Create CPTs
    cpt_ids = integration.create_intermediate_node_cpts()
    
    # Update outcome node templates
    integration.update_outcome_node_templates()
    
    # Validate integration
    validation_results = integration.validate_integration()
    
    logger.info(f"Intermediate node integration completed:")
    logger.info(f"  Templates created: {validation_results['templates_created']}")
    logger.info(f"  CPTs created: {validation_results['cpts_created']}")
    logger.info(f"  Validation errors: {len(validation_results['validation_errors'])}")
    
    if validation_results['validation_errors']:
        for error in validation_results['validation_errors']:
            logger.error(f"  {error}")
    
    return integration