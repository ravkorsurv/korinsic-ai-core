"""
Economic Withholding Detection Model.

This module contains the main EconomicWithholdingModel class that encapsulates
the Bayesian network for detecting economic withholding in power markets using
ARERA-style counterfactual analysis.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from pgmpy.inference import VariableElimination
    from pgmpy.models import DiscreteBayesianNetwork
    from pgmpy.factors.discrete import TabularCPD
    PGMPY_AVAILABLE = True
except ImportError:
    PGMPY_AVAILABLE = False
    DiscreteBayesianNetwork = None
    VariableElimination = None
    TabularCPD = None

from ..shared.esi import EvidenceSufficiencyIndex
from ..shared.fallback_logic import FallbackLogic

# Add intermediate nodes import
from ..shared.intermediate_nodes import (
    CostAnalysisIntermediateNode,
    MarketConditionsIntermediateNode, 
    BehavioralPatternsIntermediateNode,
    TechnicalFactorsIntermediateNode,
    create_intermediate_cpt
)

# Add regulatory explainability import
from core.regulatory_explainability import (
    RegulatoryExplainabilityEngine,
    EvidenceItem,
    EvidenceType,
    RegulatoryFramework
)
from .config import EconomicWithholdingConfig
from .nodes import EconomicWithholdingNodes
from .scenario_engine import ScenarioSimulationEngine
from .cost_curve_analyzer import CostCurveAnalyzer
from .arera_compliance import ARERAComplianceEngine

logger = logging.getLogger(__name__)


class EconomicWithholdingModel:
    """
    Economic withholding detection model using ARERA methodology.

    This class provides a complete interface for economic withholding risk assessment,
    including counterfactual simulation, cost curve analysis, Bayesian inference,
    and ARERA compliance reporting.
    
    REFACTORED: Now uses intermediate nodes to reduce fan-in complexity from 19→4 parents.
    """

    def __init__(
        self, 
        use_latent_intent: bool = False, 
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the economic withholding model.

        Args:
            use_latent_intent: Whether to use latent intent modeling
            config: Optional model configuration
        """
        self.use_latent_intent = use_latent_intent
        self.config = EconomicWithholdingConfig(config or {})
        self.nodes = EconomicWithholdingNodes()
        self.fallback_logic = FallbackLogic()
        self.esi_calculator = EvidenceSufficiencyIndex()

        # Initialize regulatory explainability engine
        self.explainability_engine = RegulatoryExplainabilityEngine(config or {})
        
        # Initialize specialized engines
        self.scenario_engine = ScenarioSimulationEngine(
            self.config.get_simulation_config()
        )
        self.cost_analyzer = CostCurveAnalyzer(
            self.config.get_simulation_config()
        )
        self.arera_engine = ARERAComplianceEngine(
            self.config.get_arera_config()
        )

        # Initialize intermediate nodes for fan-in reduction
        self.intermediate_nodes = self._initialize_intermediate_nodes()

        # Build the Bayesian network if pgmpy is available
        if PGMPY_AVAILABLE:
            self.model = self._build_model()
            self.inference_engine = VariableElimination(self.model)
        else:
            logger.warning("pgmpy not available, using fallback logic only")
            self.model = None
            self.inference_engine = None

        logger.info(
            f"Economic withholding model initialized (latent_intent={use_latent_intent}, "
            f"intermediate_nodes={len(self.intermediate_nodes)})"
        )

    def _initialize_intermediate_nodes(self) -> Dict[str, Any]:
        """Initialize intermediate nodes for fan-in reduction."""
        return {
            "cost_analysis": CostAnalysisIntermediateNode(),
            "market_conditions": MarketConditionsIntermediateNode(),
            "behavioral_patterns": BehavioralPatternsIntermediateNode(),
            "technical_factors": TechnicalFactorsIntermediateNode(),
        }

    def _build_model(self) -> Optional[DiscreteBayesianNetwork]:
        """
        Build the Bayesian network model for economic withholding detection.
        REFACTORED: Uses intermediate nodes to reduce complexity.

        Returns:
            Configured Bayesian network or None if pgmpy unavailable
        """
        if not PGMPY_AVAILABLE:
            return None

        try:
            # Create the network structure with intermediate nodes
            model = DiscreteBayesianNetwork()
            
            # Add all nodes (evidence + intermediate + outcome)
            nodes = self._get_all_node_names()
            model.add_nodes_from(nodes)
            
            # Add edges with new hierarchical structure
            edges = self._get_network_edges_with_intermediates()
            model.add_edges_from(edges)
            
            # Add CPDs (Conditional Probability Distributions)
            cpds = self._get_conditional_probability_distributions()
            model.add_cpds(*cpds)
            
            # Validate the model
            if not model.check_model():
                raise ValueError("Bayesian Network structure or CPDs are invalid")
                
            logger.info(
                f"Economic withholding model built successfully with "
                f"{len(nodes)} nodes and {len(edges)} edges (intermediate structure)"
            )
            return model
            
        except Exception as e:
            logger.error(f"Error building economic withholding model: {str(e)}")
            raise

    def _get_network_edges_with_intermediates(self) -> List[tuple]:
        """
        Get network edges using intermediate node structure.
        REFACTORED: 19 direct connections → 4 intermediate → 1 final
        
        Returns:
            List of edges (parent, child) for the hierarchical Bayesian network
        """
        edges = []
        
        # Evidence nodes to intermediate nodes (grouped by business logic)
        
        # Cost analysis group (4 evidence → 1 intermediate)
        cost_evidence = [
            'marginal_cost_deviation', 'fuel_cost_variance', 
            'plant_efficiency', 'heat_rate_variance'
        ]
        for evidence in cost_evidence:
            edges.append((evidence, 'cost_analysis_intermediate'))
        
        # Market conditions group (4 evidence → 1 intermediate)  
        market_evidence = [
            'load_factor', 'market_tightness', 
            'competitive_context', 'transmission_constraint'
        ]
        for evidence in market_evidence:
            edges.append((evidence, 'market_conditions_intermediate'))
        
        # Behavioral patterns group (5 evidence → 1 intermediate)
        behavioral_evidence = [
            'bid_shape_anomaly', 'offer_withdrawal_pattern', 'capacity_utilization',
            'markup_consistency', 'opportunity_pricing'
        ]
        for evidence in behavioral_evidence:
            edges.append((evidence, 'behavioral_patterns_intermediate'))
        
        # Technical factors group (6 evidence → 1 intermediate)
        technical_evidence = [
            'fuel_price_correlation', 'cross_plant_coordination', 'price_impact_ratio',
            'volume_participation', 'liquidity_context', 'order_clustering'
        ]
        for evidence in technical_evidence:
            edges.append((evidence, 'technical_factors_intermediate'))
        
        # Intermediate nodes to final risk assessment (4 intermediate → 1 final)
        intermediate_nodes = [
            'cost_analysis_intermediate',
            'market_conditions_intermediate', 
            'behavioral_patterns_intermediate',
            'technical_factors_intermediate'
        ]
        
        if self.use_latent_intent:
            # Intermediate nodes influence latent intent
            for intermediate in intermediate_nodes:
                edges.append((intermediate, 'withholding_latent_intent'))
            # Latent intent influences final risk
            edges.append(('withholding_latent_intent', 'economic_withholding_risk'))
        else:
            # Direct intermediate to risk connections
            for intermediate in intermediate_nodes:
                edges.append((intermediate, 'economic_withholding_risk'))
        
        return edges

    def _get_all_node_names(self) -> List[str]:
        """Get all node names including intermediate nodes."""
        # Evidence nodes (19 total)
        evidence_nodes = [
            # Cost analysis evidence
            'marginal_cost_deviation', 'fuel_cost_variance', 'plant_efficiency', 'heat_rate_variance',
            # Market conditions evidence  
            'load_factor', 'market_tightness', 'competitive_context', 'transmission_constraint',
            # Behavioral patterns evidence
            'bid_shape_anomaly', 'offer_withdrawal_pattern', 'capacity_utilization', 
            'markup_consistency', 'opportunity_pricing',
            # Technical factors evidence
            'fuel_price_correlation', 'cross_plant_coordination', 'price_impact_ratio',
            'volume_participation', 'liquidity_context', 'order_clustering'
        ]
        
        # Intermediate nodes (4 total)
        intermediate_nodes = [
            'cost_analysis_intermediate',
            'market_conditions_intermediate',
            'behavioral_patterns_intermediate', 
            'technical_factors_intermediate'
        ]
        
        # Outcome nodes
        outcome_nodes = ['economic_withholding_risk']
        
        # Optional latent intent node
        if self.use_latent_intent:
            outcome_nodes.append('withholding_latent_intent')
        
        return evidence_nodes + intermediate_nodes + outcome_nodes

    def _get_conditional_probability_distributions(self) -> List[Any]:
        """
        Create conditional probability distributions for the network.
        REFACTORED: Uses intermediate nodes with manageable CPT sizes.
        
        Returns:
            List of TabularCPD objects for all nodes
        """
        if not PGMPY_AVAILABLE:
            return []
            
        cpds = []
        
        # Evidence node CPDs (prior probabilities - no parents)
        evidence_priors = self._get_evidence_node_priors()
        cpds.extend(evidence_priors)
        
        # Intermediate node CPDs (evidence → intermediate)
        intermediate_cpds = self._get_intermediate_node_cpds()
        cpds.extend(intermediate_cpds)
        
        # Final outcome CPDs (intermediate → outcome)
        outcome_cpds = self._get_outcome_node_cpds()
        cpds.extend(outcome_cpds)
        
        logger.info(f"Created {len(cpds)} CPDs for economic withholding model")
        return cpds

    def _get_evidence_node_priors(self) -> List[TabularCPD]:
        """Create CPDs for evidence nodes (prior probabilities)."""
        cpds = []
        
        # Marginal cost deviation (0 or 1)
        marginal_cost_deviation_cpd = TabularCPD(
            variable='marginal_cost_deviation',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'marginal_cost_deviation': ['no_deviation', 'deviation']}
        )
        cpds.append(marginal_cost_deviation_cpd)

        # Fuel cost variance (0 or 1)
        fuel_cost_variance_cpd = TabularCPD(
            variable='fuel_cost_variance',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'fuel_cost_variance': ['no_variance', 'variance']}
        )
        cpds.append(fuel_cost_variance_cpd)

        # Plant efficiency (0 or 1)
        plant_efficiency_cpd = TabularCPD(
            variable='plant_efficiency',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'plant_efficiency': ['efficient', 'inefficient']}
        )
        cpds.append(plant_efficiency_cpd)

        # Heat rate variance (0 or 1)
        heat_rate_variance_cpd = TabularCPD(
            variable='heat_rate_variance',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'heat_rate_variance': ['no_variance', 'variance']}
        )
        cpds.append(heat_rate_variance_cpd)

        # Load factor (0 or 1)
        load_factor_cpd = TabularCPD(
            variable='load_factor',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'load_factor': ['low', 'high']}
        )
        cpds.append(load_factor_cpd)

        # Market tightness (0 or 1)
        market_tightness_cpd = TabularCPD(
            variable='market_tightness',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'market_tightness': ['tight', 'loose']}
        )
        cpds.append(market_tightness_cpd)

        # Competitive context (0 or 1)
        competitive_context_cpd = TabularCPD(
            variable='competitive_context',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'competitive_context': ['competitive', 'non_competitive']}
        )
        cpds.append(competitive_context_cpd)

        # Transmission constraint (0 or 1)
        transmission_constraint_cpd = TabularCPD(
            variable='transmission_constraint',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'transmission_constraint': ['no_constraint', 'constraint']}
        )
        cpds.append(transmission_constraint_cpd)

        # Bid shape anomaly (0 or 1)
        bid_shape_anomaly_cpd = TabularCPD(
            variable='bid_shape_anomaly',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'bid_shape_anomaly': ['normal', 'anomaly']}
        )
        cpds.append(bid_shape_anomaly_cpd)

        # Offer withdrawal pattern (0 or 1)
        offer_withdrawal_pattern_cpd = TabularCPD(
            variable='offer_withdrawal_pattern',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'offer_withdrawal_pattern': ['no_withdrawal', 'withdrawal']}
        )
        cpds.append(offer_withdrawal_pattern_cpd)

        # Capacity utilization (0 or 1)
        capacity_utilization_cpd = TabularCPD(
            variable='capacity_utilization',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'capacity_utilization': ['low', 'high']}
        )
        cpds.append(capacity_utilization_cpd)

        # Markup consistency (0 or 1)
        markup_consistency_cpd = TabularCPD(
            variable='markup_consistency',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'markup_consistency': ['consistent', 'inconsistent']}
        )
        cpds.append(markup_consistency_cpd)

        # Opportunity pricing (0 or 1)
        opportunity_pricing_cpd = TabularCPD(
            variable='opportunity_pricing',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'opportunity_pricing': ['no_opportunity', 'opportunity']}
        )
        cpds.append(opportunity_pricing_cpd)

        # Fuel price correlation (0 or 1)
        fuel_price_correlation_cpd = TabularCPD(
            variable='fuel_price_correlation',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'fuel_price_correlation': ['no_correlation', 'correlation']}
        )
        cpds.append(fuel_price_correlation_cpd)

        # Cross plant coordination (0 or 1)
        cross_plant_coordination_cpd = TabularCPD(
            variable='cross_plant_coordination',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'cross_plant_coordination': ['no_coordination', 'coordination']}
        )
        cpds.append(cross_plant_coordination_cpd)

        # Price impact ratio (0 or 1)
        price_impact_ratio_cpd = TabularCPD(
            variable='price_impact_ratio',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'price_impact_ratio': ['no_impact', 'impact']}
        )
        cpds.append(price_impact_ratio_cpd)

        # Volume participation (0 or 1)
        volume_participation_cpd = TabularCPD(
            variable='volume_participation',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'volume_participation': ['low', 'high']}
        )
        cpds.append(volume_participation_cpd)

        # Liquidity context (0 or 1)
        liquidity_context_cpd = TabularCPD(
            variable='liquidity_context',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'liquidity_context': ['low', 'high']}
        )
        cpds.append(liquidity_context_cpd)

        # Order clustering (0 or 1)
        order_clustering_cpd = TabularCPD(
            variable='order_clustering',
            variable_card=2,
            values=[[0.9], [0.1]],
            state_names={'order_clustering': ['no_clustering', 'clustering']}
        )
        cpds.append(order_clustering_cpd)

        return cpds

    def _get_intermediate_node_cpds(self) -> List[TabularCPD]:
        """Create CPDs for intermediate nodes using noisy-OR logic."""
        cpds = []
        
        # Cost analysis intermediate (4 parents → 81 combinations vs 1.16B)
        cost_cpd = create_intermediate_cpt(
            self.intermediate_nodes["cost_analysis"],
            ['marginal_cost_deviation', 'fuel_cost_variance', 'plant_efficiency', 'heat_rate_variance'],
            cpt_type="noisy_or"
        )
        cpds.append(cost_cpd)
        
        # Market conditions intermediate (4 parents → 81 combinations)
        market_cpd = create_intermediate_cpt(
            self.intermediate_nodes["market_conditions"],
            ['load_factor', 'market_tightness', 'competitive_context', 'transmission_constraint'],
            cpt_type="noisy_or"
        )
        cpds.append(market_cpd)
        
        # Behavioral patterns intermediate (5 parents → 243 combinations)
        behavioral_cpd = create_intermediate_cpt(
            self.intermediate_nodes["behavioral_patterns"],
            ['bid_shape_anomaly', 'offer_withdrawal_pattern', 'capacity_utilization', 
             'markup_consistency', 'opportunity_pricing'],
            cpt_type="noisy_or"
        )
        cpds.append(behavioral_cpd)
        
        # Technical factors intermediate (6 parents → 729 combinations)
        technical_cpd = create_intermediate_cpt(
            self.intermediate_nodes["technical_factors"],
            ['fuel_price_correlation', 'cross_plant_coordination', 'price_impact_ratio',
             'volume_participation', 'liquidity_context', 'order_clustering'],
            cpt_type="noisy_or"
        )
        cpds.append(technical_cpd)
        
        return cpds

    def _get_outcome_node_cpds(self) -> List[TabularCPD]:
        """Create CPDs for final outcome nodes (4 intermediate parents → manageable)."""
        cpds = []
        
        intermediate_parents = [
            'cost_analysis_intermediate',
            'market_conditions_intermediate', 
            'behavioral_patterns_intermediate',
            'technical_factors_intermediate'
        ]
        
        if self.use_latent_intent:
            # Latent intent CPD (4 intermediate parents → 81 combinations)
            latent_intent_values = self._create_expert_latent_intent_cpt()
            latent_cpd = TabularCPD(
                variable='withholding_latent_intent',
                variable_card=3,
                values=latent_intent_values,
                evidence=intermediate_parents,
                evidence_card=[3, 3, 3, 3]
            )
            cpds.append(latent_cpd)
            
            # Final risk CPD (1 latent intent parent → 3 combinations)
            risk_values = self._create_final_risk_cpt_with_latent()
            risk_cpd = TabularCPD(
                variable='economic_withholding_risk',
                variable_card=3,
                values=risk_values,
                evidence=['withholding_latent_intent'],
                evidence_card=[3]
            )
            cpds.append(risk_cpd)
        else:
            # Direct final risk CPD (4 intermediate parents → 81 combinations)
            risk_values = self._create_final_risk_cpt_direct()
            risk_cpd = TabularCPD(
                variable='economic_withholding_risk',
                variable_card=3,
                values=risk_values,
                evidence=intermediate_parents,
                evidence_card=[3, 3, 3, 3]
            )
            cpds.append(risk_cpd)
        
        return cpds

    def _create_expert_latent_intent_cpt(self) -> List[List[float]]:
        """Create a CPD for the latent intent node."""
        # This is a simplified example. In a real model, this would be learned
        # from expert knowledge or data. For now, a fixed mapping.
        return [
            [0.1, 0.2, 0.7], # No withholding
            [0.3, 0.5, 0.2], # Potential withholding
            [0.6, 0.2, 0.1]  # Clear withholding
        ]

    def _create_final_risk_cpt_with_latent(self) -> List[List[float]]:
        """Create a CPD for the final risk node, considering latent intent."""
        # This is a simplified example. In a real model, this would be learned
        # from expert knowledge or data. For now, a fixed mapping.
        return [
            [0.1, 0.2, 0.7], # No withholding
            [0.3, 0.5, 0.2], # Potential withholding
            [0.6, 0.2, 0.1]  # Clear withholding
        ]

    def _create_final_risk_cpt_direct(self) -> List[List[float]]:
        """Create a CPD for the final risk node, considering direct intermediate parents."""
        # This is a simplified example. In a real model, this would be learned
        # from expert knowledge or data. For now, a fixed mapping.
        return [
            [0.1, 0.2, 0.7], # No withholding
            [0.3, 0.5, 0.2], # Potential withholding
            [0.6, 0.2, 0.1]  # Clear withholding
        ]

    def _get_state_index(self, node_name: str, state_value: str) -> int:
        """
        Convert string state value to numeric index for a given node.
        
        Args:
            node_name: Name of the node
            state_value: String value of the state
            
        Returns:
            Numeric index of the state
        """
        node_states = self.nodes.get_node_states(node_name)
        if node_states and state_value in node_states:
            return node_states.index(state_value)
        # Return default index 0 if state not found
        return 0
    
    def _convert_numeric_to_string_evidence(self, numeric_evidence: Dict[str, int]) -> Dict[str, str]:
        """
        Convert numeric evidence indices back to string states for compatibility.
        
        Args:
            numeric_evidence: Evidence with numeric state indices
            
        Returns:
            Evidence with string state values
        """
        string_evidence = {}
        for node_name, state_index in numeric_evidence.items():
            node_states = self.nodes.get_node_states(node_name)
            if node_states and 0 <= state_index < len(node_states):
                string_evidence[node_name] = node_states[state_index]
            else:
                # Use first state as default
                string_evidence[node_name] = node_states[0] if node_states else ""
        return string_evidence

    def analyze_economic_withholding(
        self, 
        plant_data: Dict[str, Any],
        offers: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        fuel_prices: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive economic withholding analysis.

        Args:
            plant_data: Plant characteristics and technical data
            offers: List of submitted offers (price-quantity pairs)
            market_data: Market conditions and context
            fuel_prices: Current fuel price data

        Returns:
            Complete analysis results including risk assessment and compliance report
        """
        try:
            analysis_start = datetime.utcnow()
            
            # Step 1: Generate benchmark offers using counterfactual simulation
            logger.info("Generating benchmark offers...")
            benchmark_offers = self.scenario_engine.generate_benchmark_offers(
                plant_data, market_data, fuel_prices
            )
            
            # Step 2: Run counterfactual simulation
            logger.info("Running counterfactual simulation...")
            counterfactual_results = self.scenario_engine.run_counterfactual_simulation(
                offers, benchmark_offers, market_data
            )
            
            # Step 3: Analyze cost-offer relationships
            logger.info("Analyzing cost curves...")
            cost_analysis = self._analyze_cost_relationships(
                offers, plant_data, fuel_prices
            )
            
            # Step 4: Detect bid shape anomalies
            logger.info("Detecting bid shape anomalies...")
            bid_shape_analysis = self.cost_analyzer.detect_bid_shape_anomalies(offers)
            
            # Step 5: Calculate Bayesian risk scores
            logger.info("Calculating Bayesian risk scores...")
            bayesian_results = self._calculate_bayesian_risk(
                counterfactual_results, cost_analysis, market_data
            )
            
            # Step 6: Generate ARERA compliance report
            logger.info("Generating ARERA compliance report...")
            compliance_report = self.arera_engine.assess_compliance(
                {
                    'counterfactual_analysis': counterfactual_results,
                    'cost_curve_analysis': cost_analysis,
                    'bid_shape_analysis': bid_shape_analysis,
                    'bayesian_analysis': bayesian_results
                },
                plant_data,
                market_data
            )
            
            # Step 7: Compile final results
            analysis_end = datetime.utcnow()
            processing_time = (analysis_end - analysis_start).total_seconds()
            
            final_results = {
                'analysis_metadata': {
                    'analysis_id': f"ew_{analysis_start.strftime('%Y%m%d_%H%M%S')}",
                    'plant_id': plant_data.get('unit_id', 'unknown'),
                    'analysis_timestamp': analysis_start.isoformat(),
                    'processing_time_seconds': processing_time,
                    'model_version': '1.0.0',
                    'methodology': 'arera_counterfactual_bayesian'
                },
                'input_summary': {
                    'plant_data': {
                        'unit_id': plant_data.get('unit_id'),
                        'fuel_type': plant_data.get('fuel_type'),
                        'capacity_mw': plant_data.get('capacity_mw'),
                        'efficiency': plant_data.get('efficiency')
                    },
                    'offers_count': len(offers),
                    'market_conditions': market_data,
                    'fuel_prices': fuel_prices
                },
                'counterfactual_analysis': counterfactual_results,
                'cost_curve_analysis': cost_analysis,
                'bid_shape_analysis': bid_shape_analysis,
                'bayesian_analysis': bayesian_results,
                'arera_compliance_report': compliance_report,
                'overall_assessment': self._generate_overall_assessment(
                    counterfactual_results, bayesian_results, compliance_report
                )
            }
            
            logger.info(f"Economic withholding analysis completed in {processing_time:.2f}s")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in economic withholding analysis: {str(e)}")
            return {
                'error': str(e),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'plant_id': plant_data.get('unit_id', 'unknown')
            }

    def _analyze_cost_relationships(
        self, 
        offers: List[Dict[str, Any]], 
        plant_data: Dict[str, Any],
        fuel_prices: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Analyze cost-offer relationships using the cost curve analyzer.
        
        Args:
            offers: List of offers
            plant_data: Plant characteristics
            fuel_prices: Fuel price data
            
        Returns:
            Cost relationship analysis results
        """
        try:
            # Calculate marginal costs
            fuel_type = plant_data.get('fuel_type', 'gas')
            fuel_cost = fuel_prices.get(fuel_type, 50.0)
            heat_rate = plant_data.get('heat_rate', 7500)
            efficiency = plant_data.get('efficiency', 0.45)
            
            variable_costs = plant_data.get('variable_costs', {})
            vom_cost = variable_costs.get('vom_cost', 3.5)
            emission_cost = variable_costs.get('emission_cost', 1.2)
            
            # Calculate marginal cost using scenario engine method
            marginal_cost = self.scenario_engine._calculate_marginal_cost(
                fuel_cost, heat_rate, efficiency, vom_cost, emission_cost
            )
            
            costs = {
                'marginal_cost': marginal_cost,
                'fuel_cost': fuel_cost,
                'efficiency': efficiency,
                'vom_cost': vom_cost,
                'emission_cost': emission_cost
            }
            
            # Analyze offer-cost relationships
            return self.cost_analyzer.analyze_offer_cost_relationship(
                offers, costs, plant_data
            )
            
        except Exception as e:
            logger.error(f"Error in cost relationship analysis: {str(e)}")
            return {'error': str(e)}

    def _calculate_bayesian_risk(
        self, 
        counterfactual_results: Dict[str, Any],
        cost_analysis: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate Bayesian risk scores based on analysis results.
        
        Args:
            counterfactual_results: Counterfactual simulation results
            cost_analysis: Cost curve analysis results
            market_data: Market conditions
            
        Returns:
            Bayesian risk assessment results
        """
        try:
            # Extract evidence from analysis results
            evidence = self._extract_evidence_from_analysis(
                counterfactual_results, cost_analysis, market_data
            )
            
            # Perform Bayesian inference if model available
            if self.model and self.inference_engine:
                risk_scores = self._perform_bayesian_inference(evidence)
            else:
                # Use fallback logic
                risk_scores = self._calculate_fallback_risk(evidence)
            
            # Calculate evidence sufficiency index
            esi_result = self._calculate_esi(evidence)
            
            return {
                'evidence': evidence,
                'risk_scores': risk_scores,
                'evidence_sufficiency': esi_result,
                'inference_method': 'bayesian' if self.model else 'fallback',
                'model_metadata': {
                    'use_latent_intent': self.use_latent_intent,
                    'pgmpy_available': PGMPY_AVAILABLE
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Bayesian risk calculation: {str(e)}")
            return {'error': str(e)}

    def _extract_evidence_from_analysis(
        self,
        counterfactual_results: Dict[str, Any],
        cost_analysis: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract evidence variables from analysis results for Bayesian inference.
        
        Args:
            counterfactual_results: Counterfactual analysis results
            cost_analysis: Cost curve analysis results
            market_data: Market conditions
            
        Returns:
            Evidence dictionary for Bayesian network (numeric indices)
        """
        # Import the standard evidence mapper
        from core.evidence_mapper import map_economic_withholding_evidence
        
        # Prepare data in the standard format
        ew_data = {
            'plant_data': {},  # Will be populated from context
            'market_data': market_data,
            'cost_analysis': cost_analysis,
            'counterfactual_results': counterfactual_results,
            'operational_data': {},  # Could be extracted from analysis
            'bid_analysis': {},  # Could be extracted from analysis
            'withdrawal_data': {},  # Could be extracted from analysis
            'coordination_data': {},  # Could be extracted from analysis
            'pricing_data': {},  # Could be extracted from analysis
            'fuel_prices': {},  # Could be extracted from context
        }
        
        # Use standard evidence mapper
        evidence = map_economic_withholding_evidence(ew_data)
        
        # For backward compatibility, ensure all evidence nodes have values
        all_nodes = self.nodes.get_evidence_nodes()
        for node_name in all_nodes:
            if node_name not in evidence:
                evidence[node_name] = 0  # Default to first state (index 0)
        
        return evidence

    def _perform_bayesian_inference(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform Bayesian inference using pgmpy.
        
        Args:
            evidence: Evidence dictionary
            
        Returns:
            Risk scores from Bayesian inference
        """
        try:
            # Convert numeric evidence back to string states for pgmpy
            string_evidence = self._convert_numeric_to_string_evidence(evidence)

            # Query the outcome node
            query_result = self.inference_engine.query(
                variables=['economic_withholding_risk'],
                evidence=string_evidence
            )
            
            # Extract probabilities
            risk_probs = query_result['economic_withholding_risk'].values
            risk_states = ['no_withholding', 'potential_withholding', 'clear_withholding']
            
            risk_scores = {}
            for i, state in enumerate(risk_states):
                risk_scores[state] = float(risk_probs[i])
            
            return {
                'risk_probabilities': risk_scores,
                'max_risk_state': max(risk_scores.items(), key=lambda x: x[1])[0],
                'confidence': max(risk_scores.values())
            }
            
        except Exception as e:
            logger.error(f"Error in Bayesian inference: {str(e)}")
            return self._calculate_fallback_risk(evidence)

    def _calculate_fallback_risk(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk using fallback logic when Bayesian inference unavailable.
        
        Args:
            evidence: Evidence dictionary
            
        Returns:
            Risk scores from fallback logic
        """
        try:
            # Use evidence weights from configuration
            weights = self.config.get_evidence_weights()
            
            # Calculate weighted risk score
            total_score = 0.0
            total_weight = 0.0
            
            for node_name, value in evidence.items():
                if node_name in weights:
                    weight = weights[node_name]
                    
                    # Convert evidence value to numeric score
                    node_states = self.nodes.get_node_states(node_name)
                    if node_states and value in node_states:
                        state_index = node_states.index(value)
                        # Higher state index = higher risk (generally)
                        node_score = state_index / (len(node_states) - 1)
                        
                        total_score += weight * node_score
                        total_weight += weight
            
            # Normalize score
            if total_weight > 0:
                normalized_score = total_score / total_weight
            else:
                normalized_score = 0.0
            
            # Convert to risk probabilities
            if normalized_score > 0.7:
                risk_probs = {'no_withholding': 0.1, 'potential_withholding': 0.3, 'clear_withholding': 0.6}
            elif normalized_score > 0.4:
                risk_probs = {'no_withholding': 0.3, 'potential_withholding': 0.5, 'clear_withholding': 0.2}
            else:
                risk_probs = {'no_withholding': 0.7, 'potential_withholding': 0.2, 'clear_withholding': 0.1}
            
            return {
                'risk_probabilities': risk_probs,
                'max_risk_state': max(risk_probs.items(), key=lambda x: x[1])[0],
                'confidence': max(risk_probs.values()),
                'fallback_score': normalized_score
            }
            
        except Exception as e:
            logger.error(f"Error in fallback risk calculation: {str(e)}")
            return {
                'risk_probabilities': {'no_withholding': 0.8, 'potential_withholding': 0.15, 'clear_withholding': 0.05},
                'max_risk_state': 'no_withholding',
                'confidence': 0.8,
                'error': str(e)
            }

    def analyze_with_standard_evidence(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze economic withholding using standard evidence mapping pattern.
        This method integrates with the unified evidence mapper.
        
        Args:
            processed_data: Processed data in standard format from DataProcessor
            
        Returns:
            Analysis results including risk assessment
        """
        try:
            # Import the standard evidence mapper
            from core.evidence_mapper import map_economic_withholding_evidence
            
            # Extract specific data for economic withholding analysis
            ew_data = processed_data.get('economic_withholding', {})
            
            # If no economic withholding specific data, extract from general data
            if not ew_data:
                ew_data = {
                    'plant_data': processed_data.get('plant_data', {}),
                    'market_data': processed_data.get('market_data', {}),
                    'cost_analysis': processed_data.get('cost_analysis', {}),
                    'counterfactual_results': processed_data.get('counterfactual_results', {}),
                    'operational_data': processed_data.get('operational_data', {}),
                    'bid_analysis': processed_data.get('bid_analysis', {}),
                    'withdrawal_data': processed_data.get('withdrawal_data', {}),
                    'coordination_data': processed_data.get('coordination_data', {}),
                    'pricing_data': processed_data.get('pricing_data', {}),
                    'fuel_prices': processed_data.get('fuel_prices', {}),
                }
            
            # Use standard evidence mapper to get numeric evidence
            numeric_evidence = map_economic_withholding_evidence(ew_data)
            
            # Convert numeric evidence to string states for internal use
            string_evidence = self._convert_numeric_to_string_evidence(numeric_evidence)
            
            # Perform Bayesian inference with string evidence
            if self.model and self.inference_engine:
                # Query the outcome node
                query_result = self.inference_engine.query(
                    variables=['economic_withholding_risk'],
                    evidence=string_evidence
                )
                
                # Extract probabilities
                risk_probs = query_result['economic_withholding_risk'].values
                risk_states = ['no_withholding', 'potential_withholding', 'clear_withholding']
                
                risk_scores = {}
                for i, state in enumerate(risk_states):
                    risk_scores[state] = float(risk_probs[i])
            else:
                # Fallback calculation based on numeric evidence
                high_risk_count = sum(1 for v in numeric_evidence.values() if v == 2)
                medium_risk_count = sum(1 for v in numeric_evidence.values() if v == 1)
                
                if high_risk_count >= 3:
                    risk_scores = {
                        'no_withholding': 0.1,
                        'potential_withholding': 0.2,
                        'clear_withholding': 0.7,
                    }
                elif high_risk_count >= 1 or medium_risk_count >= 3:
                    risk_scores = {
                        'no_withholding': 0.5,
                        'potential_withholding': 0.4,
                        'clear_withholding': 0.1,
                    }
                else:
                    risk_scores = {
                        'no_withholding': 0.9,
                        'potential_withholding': 0.08,
                        'clear_withholding': 0.02,
                    }
            
            # Return results in standard format
            return {
                'risk_score': risk_scores.get('clear_withholding', 0.0),
                'overall_score': risk_scores.get('clear_withholding', 0.0),
                'risk_probabilities': [
                    risk_scores.get('no_withholding', 0.95),
                    risk_scores.get('potential_withholding', 0.04),
                    risk_scores.get('clear_withholding', 0.01)
                ],
                'esi_score': 0.8,  # Could calculate actual ESI
                'evidence_used': numeric_evidence,
                'model_type': 'economic_withholding',
                'confidence': max(risk_scores.values())
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_with_standard_evidence: {str(e)}")
            return {
                'risk_score': 0.0,
                'overall_score': 0.0,
                'risk_probabilities': [0.95, 0.04, 0.01],
                'esi_score': 0.0,
                'evidence_used': {},
                'model_type': 'economic_withholding',
                'error': str(e)
            }

    def _calculate_esi(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Evidence Sufficiency Index.
        
        Args:
            evidence: Evidence dictionary
            
        Returns:
            ESI calculation results
        """
        try:
            # Get required evidence nodes
            all_evidence_nodes = set(self.nodes.get_evidence_nodes().keys())
            provided_evidence = set(evidence.keys())
            
            # Calculate sufficiency metrics
            coverage = len(provided_evidence & all_evidence_nodes) / len(all_evidence_nodes)
            
            # Calculate quality based on evidence weights
            weights = self.config.get_evidence_weights()
            weighted_coverage = 0.0
            total_weight = 0.0
            
            for node_name in all_evidence_nodes:
                weight = weights.get(node_name, 0.5)
                total_weight += weight
                if node_name in provided_evidence:
                    weighted_coverage += weight
            
            quality = weighted_coverage / total_weight if total_weight > 0 else 0.0
            
            # Overall ESI score
            esi_score = (coverage + quality) / 2
            
            return {
                'esi_score': esi_score,
                'coverage': coverage,
                'quality': quality,
                'evidence_provided': len(provided_evidence),
                'evidence_required': len(all_evidence_nodes),
                'missing_evidence': list(all_evidence_nodes - provided_evidence)
            }
            
        except Exception as e:
            logger.error(f"Error calculating ESI: {str(e)}")
            return {'esi_score': 0.5, 'error': str(e)}

    def _generate_overall_assessment(
        self,
        counterfactual_results: Dict[str, Any],
        bayesian_results: Dict[str, Any],
        compliance_report: Any
    ) -> Dict[str, Any]:
        """
        Generate overall risk assessment combining all analysis results.
        
        Args:
            counterfactual_results: Counterfactual analysis
            bayesian_results: Bayesian risk scores
            compliance_report: ARERA compliance report
            
        Returns:
            Overall assessment summary
        """
        try:
            # Extract key metrics
            risk_indicators = counterfactual_results.get('risk_indicators', {})
            overall_risk_score = risk_indicators.get('overall_risk_score', 0.0)
            
            bayesian_confidence = bayesian_results.get('risk_scores', {}).get('confidence', 0.0)
            
            compliance_status = compliance_report.compliance_status if hasattr(compliance_report, 'compliance_status') else 'unknown'
            violation_count = len(compliance_report.violations) if hasattr(compliance_report, 'violations') else 0
            
            # Determine overall risk level
            if overall_risk_score > 0.8 or violation_count > 2:
                overall_risk_level = 'high'
                recommendation = 'Immediate investigation required - strong evidence of economic withholding'
            elif overall_risk_score > 0.6 or violation_count > 0:
                overall_risk_level = 'medium'
                recommendation = 'Further analysis recommended - potential withholding patterns detected'
            else:
                overall_risk_level = 'low'
                recommendation = 'No significant withholding indicators - continue monitoring'
            
            return {
                'overall_risk_level': overall_risk_level,
                'overall_risk_score': overall_risk_score,
                'bayesian_confidence': bayesian_confidence,
                'compliance_status': compliance_status,
                'violation_count': violation_count,
                'recommendation': recommendation,
                'key_findings': self._extract_key_findings(
                    counterfactual_results, bayesian_results, compliance_report
                ),
                'next_steps': self._generate_next_steps(overall_risk_level, compliance_status)
            }
            
        except Exception as e:
            logger.error(f"Error generating overall assessment: {str(e)}")
            return {
                'overall_risk_level': 'unknown',
                'error': str(e)
            }

    def _extract_key_findings(
        self,
        counterfactual_results: Dict[str, Any],
        bayesian_results: Dict[str, Any],
        compliance_report: Any
    ) -> List[str]:
        """Extract key findings from analysis results."""
        findings = []
        
        try:
            # Counterfactual findings
            risk_indicators = counterfactual_results.get('risk_indicators', {})
            if 'EXCESSIVE_MARKUP' in risk_indicators.get('arera_compliance_flags', []):
                findings.append("Offers exceed ARERA markup thresholds")
            
            # Statistical findings
            stat_analysis = counterfactual_results.get('statistical_analysis', {})
            hypothesis_tests = stat_analysis.get('hypothesis_test_results', {})
            if hypothesis_tests.get('t_test_vs_zero', {}).get('significant_at_05', False):
                findings.append("Statistically significant markup detected")
            
            # Compliance findings
            if hasattr(compliance_report, 'violations') and compliance_report.violations:
                high_severity = len([v for v in compliance_report.violations if v.severity == 'high'])
                if high_severity > 0:
                    findings.append(f"{high_severity} high-severity ARERA violations identified")
            
        except Exception as e:
            logger.warning(f"Error extracting key findings: {str(e)}")
        
        return findings

    def _generate_next_steps(self, risk_level: str, compliance_status: str) -> List[str]:
        """Generate recommended next steps based on assessment."""
        next_steps = []
        
        if risk_level == 'high':
            next_steps.extend([
                "Conduct detailed forensic analysis of bidding patterns",
                "Review plant cost declarations and supporting documentation",
                "Consider regulatory enforcement action",
                "Implement enhanced monitoring for this plant"
            ])
        elif risk_level == 'medium':
            next_steps.extend([
                "Expand analysis to longer time period",
                "Compare with peer plants in same market",
                "Request additional cost justification from operator",
                "Continue enhanced surveillance"
            ])
        else:
            next_steps.extend([
                "Continue routine monitoring",
                "Include in periodic compliance review"
            ])
        
        if compliance_status == 'non_compliant':
            next_steps.append("Prepare regulatory compliance report")
        
        return next_steps

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model configuration and capabilities.
        
        Returns:
            Model information dictionary
        """
        return {
            'model_type': 'economic_withholding',
            'version': '1.0.0',
            'methodology': 'arera_counterfactual_bayesian',
            'use_latent_intent': self.use_latent_intent,
            'pgmpy_available': PGMPY_AVAILABLE,
            'capabilities': {
                'counterfactual_simulation': True,
                'cost_curve_analysis': True,
                'bayesian_inference': PGMPY_AVAILABLE,
                'arera_compliance_reporting': True,
                'monte_carlo_simulation': True,
                'sensitivity_analysis': True
            },
            'supported_fuel_types': ['gas', 'coal', 'oil', 'nuclear'],
            'regulatory_frameworks': ['arera', 'ferc', 'ofgem'],
            'confidence_thresholds': self.config.get_arera_config().get('confidence_threshold', 0.90),
            'markup_thresholds': self.config.get_arera_config().get('markup_threshold', 0.15)
        }


# Utility function for backward compatibility
def create_economic_withholding_model(
    use_latent_intent: bool = False,
    config: Optional[Dict[str, Any]] = None
) -> EconomicWithholdingModel:
    """
    Create an economic withholding detection model.
    
    Args:
        use_latent_intent: Whether to use latent intent modeling
        config: Optional model configuration
        
    Returns:
        Configured EconomicWithholdingModel instance
    """
    return EconomicWithholdingModel(use_latent_intent, config)

    def generate_regulatory_explanation(
        self, 
        evidence: Dict[str, Any], 
        inference_result: Dict[str, float],
        account_id: str,
        timestamp: str
    ) -> List[EvidenceItem]:
        """
        Generate regulatory explainability evidence for economic withholding detection.
        
        Args:
            evidence: Input evidence dictionary
            inference_result: Model inference results
            account_id: Account identifier
            timestamp: Evidence timestamp
            
        Returns:
            List of evidence items for regulatory explanation
        """
        evidence_items = []
        
        # Generate evidence items based on model-specific patterns
        for evidence_key, evidence_value in evidence.items():
            if isinstance(evidence_value, (int, float)) and evidence_value > 0.1:
                # Determine evidence type based on key
                evidence_type = EvidenceType.TRADING_PATTERN
                if 'communication' in evidence_key.lower():
                    evidence_type = EvidenceType.COMMUNICATION
                elif 'timing' in evidence_key.lower() or 'temporal' in evidence_key.lower():
                    evidence_type = EvidenceType.TIMING_ANOMALY
                elif 'cross' in evidence_key.lower() or 'correlation' in evidence_key.lower():
                    evidence_type = EvidenceType.CROSS_ACCOUNT_CORRELATION
                
                evidence_items.append(EvidenceItem(
                    evidence_type=evidence_type,
                    account_id=account_id,
                    timestamp=datetime.fromisoformat(timestamp),
                    description=f"Economic Withholding indicator: {evidence_key} = {evidence_value:.2f}",
                    strength=min(float(evidence_value), 1.0),
                    reliability=0.85,
                    regulatory_relevance={
                        RegulatoryFramework.STOR_REQUIREMENTS: 0.9,
                        RegulatoryFramework.STOR_REQUIREMENTS: 0.8
                    },
                    raw_data={
                        'model_type': 'economic_withholding',
                        'evidence_node': evidence_key,
                        'score': evidence_value,
                        'inference_result': inference_result
                    }
                ))
        
        return evidence_items
    
    def get_regulatory_framework_mapping(self) -> Dict[RegulatoryFramework, Dict[str, Any]]:
        """
        Get regulatory framework mapping for economic withholding detection.
        
        Returns:
            Dictionary mapping regulatory frameworks to their requirements
        """
        return {
            RegulatoryFramework.STOR_REQUIREMENTS: {
                "description": "Economic Withholding detection and analysis",
                "key_indicators": ['Capacity withholding patterns', 'Economic withholding strategies', 'Market power abuse'],
                "evidence_threshold": 0.7,
                "reporting_requirements": "Detailed pattern analysis required"
            },
            RegulatoryFramework.STOR_REQUIREMENTS: {
                "description": "Suspicious transaction reporting for economic withholding behavior",
                "key_indicators": ['Capacity withholding patterns', 'Economic withholding strategies'],
                "evidence_threshold": 0.6,
                "reporting_requirements": "Transaction-level details required"
            }
        }

