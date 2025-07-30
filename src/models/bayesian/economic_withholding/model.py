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
    PGMPY_AVAILABLE = True
except ImportError:
    PGMPY_AVAILABLE = False
    DiscreteBayesianNetwork = None
    VariableElimination = None

from ..shared.esi import EvidenceSufficiencyIndex
from ..shared.fallback_logic import FallbackLogic
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

        # Build the Bayesian network if pgmpy is available
        if PGMPY_AVAILABLE:
            self.model = self._build_model()
            self.inference_engine = VariableElimination(self.model)
        else:
            logger.warning("pgmpy not available, using fallback logic only")
            self.model = None
            self.inference_engine = None

        logger.info(
            f"Economic withholding model initialized (latent_intent={use_latent_intent})"
        )

    def _build_model(self) -> Optional[DiscreteBayesianNetwork]:
        """
        Build the Bayesian network model for economic withholding detection.

        Returns:
            Configured Bayesian network or None if pgmpy unavailable
        """
        if not PGMPY_AVAILABLE:
            return None
            
        try:
            # Create Bayesian Network
            model = DiscreteBayesianNetwork()
            
            # Get node names based on model type
            if self.use_latent_intent:
                node_names = self.nodes.get_latent_intent_nodes()
            else:
                node_names = self.nodes.get_standard_nodes()
            
            # Add nodes to the network
            model.add_nodes_from(node_names)
            
            # Define network structure for economic withholding
            edges = self._get_network_edges()
            model.add_edges_from(edges)
            
            # Add CPDs (Conditional Probability Distributions)
            cpds = self._get_conditional_probability_distributions()
            model.add_cpds(*cpds)
            
            # Validate the model
            if model.check_model():
                logger.info("Economic withholding Bayesian network built successfully")
                return model
            else:
                logger.error("Bayesian network validation failed")
                return None
                
        except Exception as e:
            logger.error(f"Error building Bayesian network: {str(e)}")
            return None

    def _get_network_edges(self) -> List[tuple]:
        """
        Define the network structure for economic withholding detection.
        
        Returns:
            List of edges (parent, child) for the Bayesian network
        """
        edges = []
        
        # Core cost analysis influences risk
        edges.extend([
            ('marginal_cost_deviation', 'economic_withholding_risk'),
            ('fuel_cost_variance', 'economic_withholding_risk'),
            ('plant_efficiency', 'economic_withholding_risk'),
            ('heat_rate_variance', 'economic_withholding_risk'),
        ])
        
        # Market conditions influence behavior
        edges.extend([
            ('load_factor', 'economic_withholding_risk'),
            ('market_tightness', 'economic_withholding_risk'),
            ('competitive_context', 'economic_withholding_risk'),
            ('transmission_constraint', 'economic_withholding_risk'),
        ])
        
        # Behavioral indicators
        edges.extend([
            ('bid_shape_anomaly', 'economic_withholding_risk'),
            ('offer_withdrawal_pattern', 'economic_withholding_risk'),
            ('capacity_utilization', 'economic_withholding_risk'),
            ('markup_consistency', 'economic_withholding_risk'),
            ('opportunity_pricing', 'economic_withholding_risk'),
        ])
        
        # Technical analysis
        edges.extend([
            ('fuel_price_correlation', 'economic_withholding_risk'),
            ('cross_plant_coordination', 'economic_withholding_risk'),
        ])
        
        # Reused nodes from existing library
        edges.extend([
            ('price_impact_ratio', 'economic_withholding_risk'),
            ('volume_participation', 'economic_withholding_risk'),
            ('liquidity_context', 'economic_withholding_risk'),
            ('order_clustering', 'economic_withholding_risk'),
            ('benchmark_timing', 'economic_withholding_risk'),
            ('profit_motivation', 'economic_withholding_risk'),
        ])
        
        # Add latent intent connections if enabled
        if self.use_latent_intent:
            # Evidence influences latent intent
            edges.extend([
                ('marginal_cost_deviation', 'withholding_latent_intent'),
                ('fuel_cost_variance', 'withholding_latent_intent'),
                ('plant_efficiency', 'withholding_latent_intent'),
                ('market_tightness', 'withholding_latent_intent'),
                ('bid_shape_anomaly', 'withholding_latent_intent'),
                ('capacity_utilization', 'withholding_latent_intent'),
            ])
            # Latent intent influences risk
            edges.append(('withholding_latent_intent', 'economic_withholding_risk'))
        
        return edges

    def _get_conditional_probability_distributions(self) -> List[Any]:
        """
        Create conditional probability distributions for the network.
        
        Returns:
            List of CPDs for the Bayesian network
        """
        # This would create actual CPDs - for now return empty list
        # In production, this would use the node definitions and expert knowledge
        # to create proper probability distributions
        return []

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
            Evidence dictionary for Bayesian network
        """
        evidence = {}
        
        try:
            # Extract evidence from counterfactual results
            if 'comparisons' in counterfactual_results:
                comparisons = counterfactual_results['comparisons']
                if comparisons:
                    avg_markup = max(comp.get('average_markup', 0) for comp in comparisons)
                    
                    # Marginal cost deviation evidence
                    if avg_markup > 0.20:
                        evidence['marginal_cost_deviation'] = 'excessive_markup'
                    elif avg_markup > 0.10:
                        evidence['marginal_cost_deviation'] = 'moderate_markup'
                    else:
                        evidence['marginal_cost_deviation'] = 'cost_reflective'
            
            # Extract evidence from cost analysis
            if 'anomaly_detection' in cost_analysis:
                anomalies = cost_analysis['anomaly_detection']
                
                # Fuel cost variance evidence
                fuel_anomalies = anomalies.get('fuel_cost_anomalies', [])
                if any(a.get('severity') == 'high' for a in fuel_anomalies):
                    evidence['fuel_cost_variance'] = 'high_variance'
                elif fuel_anomalies:
                    evidence['fuel_cost_variance'] = 'moderate_variance'
                else:
                    evidence['fuel_cost_variance'] = 'aligned'
                
                # Plant efficiency evidence
                efficiency_anomalies = anomalies.get('efficiency_anomalies', [])
                if any(a.get('severity') == 'high' for a in efficiency_anomalies):
                    evidence['plant_efficiency'] = 'significantly_impaired'
                elif efficiency_anomalies:
                    evidence['plant_efficiency'] = 'suboptimal'
                else:
                    evidence['plant_efficiency'] = 'optimal'
            
            # Extract market condition evidence
            load_factor = market_data.get('load_factor', 'normal_demand')
            evidence['load_factor'] = load_factor
            
            market_tightness = market_data.get('market_tightness', 'balanced')
            evidence['market_tightness'] = market_tightness
            
            transmission_constraints = market_data.get('transmission_constraints', 'unconstrained')
            evidence['transmission_constraint'] = transmission_constraints
            
            # Set default values for missing evidence
            all_nodes = self.nodes.get_evidence_nodes()
            for node_name in all_nodes:
                if node_name not in evidence:
                    node_states = self.nodes.get_node_states(node_name)
                    if node_states:
                        evidence[node_name] = node_states[0]  # Use first state as default
            
        except Exception as e:
            logger.warning(f"Error extracting evidence: {str(e)}")
        
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
            # Query the outcome node
            query_result = self.inference_engine.query(
                variables=['economic_withholding_risk'],
                evidence=evidence
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