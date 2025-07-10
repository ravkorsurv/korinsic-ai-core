"""
Wash Trade Detection Model Nodes.

This module provides node definitions and management for the wash trade detection model,
including evidence nodes and latent intent nodes for wash trade and signal distortion detection.
"""

from typing import Dict, Any, Optional
import logging
from ..shared.node_library import BayesianNodeLibrary

logger = logging.getLogger(__name__)


class WashTradeDetectionNodes:
    """
    Node management class for wash trade detection model.
    
    This class manages all node definitions and provides methods for creating
    and configuring nodes used in the wash trade detection Bayesian network.
    """
    
    def __init__(self):
        """Initialize the node manager."""
        self.node_library = BayesianNodeLibrary()
        self.node_definitions = self._get_node_definitions()
        
        logger.info("Wash trade detection nodes initialized")
    
    def _get_node_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get node definitions for wash trade detection model.
        
        Returns:
            Dictionary of node definitions
        """
        return {
            'wash_trade_likelihood': {
                'type': 'wash_trade_likelihood',
                'states': ['low_probability', 'medium_probability', 'high_probability'],
                'description': 'Probability that a transaction is a wash trade (no change in economic interest)',
                'fallback_prior': [0.85, 0.12, 0.03],
                'evidence_type': 'trade_pattern'
            },
            'signal_distortion_index': {
                'type': 'signal_distortion_index',
                'states': ['minimal_distortion', 'moderate_distortion', 'high_distortion'],
                'description': 'Measures distortion introduced into order book signals by the trade',
                'fallback_prior': [0.75, 0.20, 0.05],
                'evidence_type': 'market_signal'
            },
            'algo_reaction_sensitivity': {
                'type': 'algo_reaction_sensitivity',
                'states': ['low_sensitivity', 'medium_sensitivity', 'high_sensitivity'],
                'description': 'Likelihood that trading algorithms respond to false signals from wash trades',
                'fallback_prior': [0.70, 0.25, 0.05],
                'evidence_type': 'algo_response'
            },
            'strategy_leg_overlap': {
                'type': 'strategy_leg_overlap',
                'states': ['no_overlap', 'partial_overlap', 'full_overlap'],
                'description': 'Detects whether same-entity orders in a strategy matched against each other',
                'fallback_prior': [0.80, 0.15, 0.05],
                'evidence_type': 'strategy_pattern'
            },
            'price_impact_anomaly': {
                'type': 'price_impact_anomaly',
                'states': ['normal_impact', 'unusual_impact', 'anomalous_impact'],
                'description': 'Quantifies short-term abnormal price behavior after trade occurs',
                'fallback_prior': [0.78, 0.18, 0.04],
                'evidence_type': 'price_pattern'
            },
            'implied_liquidity_conflict': {
                'type': 'implied_liquidity_conflict',
                'states': ['no_conflict', 'potential_conflict', 'clear_conflict'],
                'description': 'Detects cases where venue-level implied matching creates artificial interactions',
                'fallback_prior': [0.85, 0.12, 0.03],
                'evidence_type': 'liquidity_pattern'
            },
            'counterparty_entity_match': {
                'type': 'counterparty_entity_match',
                'states': ['different_entities', 'affiliated_entities', 'same_entity'],
                'description': 'Matches buyer and seller entities through LEI or affiliate relationships',
                'fallback_prior': [0.88, 0.10, 0.02],
                'evidence_type': 'entity_analysis'
            },
            'algo_framework_match': {
                'type': 'algo_framework_match',
                'states': ['different_frameworks', 'similar_frameworks', 'same_framework'],
                'description': 'Detects trades executed within same algorithmic or PTF framework',
                'fallback_prior': [0.82, 0.15, 0.03],
                'evidence_type': 'execution_pattern'
            },
            'implied_strategy_execution': {
                'type': 'implied_strategy_execution',
                'states': ['direct_execution', 'implied_execution', 'strategy_leg_execution'],
                'description': 'Identifies trades executed via implied strategy legs (e.g., time spreads)',
                'fallback_prior': [0.75, 0.20, 0.05],
                'evidence_type': 'execution_method'
            },
            'order_book_impact': {
                'type': 'order_book_impact',
                'states': ['minimal_impact', 'moderate_impact', 'significant_impact'],
                'description': 'Measures impact on volume at best bid/ask and order book imbalance',
                'fallback_prior': [0.70, 0.25, 0.05],
                'evidence_type': 'orderbook_signal'
            },
            'quote_frequency_distortion': {
                'type': 'quote_frequency_distortion',
                'states': ['normal_frequency', 'increased_frequency', 'flickering_quotes'],
                'description': 'Detects artificial quote frequency changes (flickering) after trade',
                'fallback_prior': [0.78, 0.18, 0.04],
                'evidence_type': 'quote_pattern'
            },
            'spread_manipulation': {
                'type': 'spread_manipulation',
                'states': ['natural_spread', 'artificial_widening', 'artificial_tightening'],
                'description': 'Detects artificial widening or tightening of spreads',
                'fallback_prior': [0.80, 0.12, 0.08],
                'evidence_type': 'spread_pattern'
            },
            'order_flow_clustering': {
                'type': 'order_flow_clustering',
                'states': ['normal_distribution', 'moderate_clustering', 'high_clustering'],
                'description': 'Detects order flow clustering following the trade',
                'fallback_prior': [0.72, 0.23, 0.05],
                'evidence_type': 'flow_pattern'
            },
            'reaction_time_delta': {
                'type': 'reaction_time_delta',
                'states': ['normal_timing', 'fast_reaction', 'ultra_fast_reaction'],
                'description': 'Measures reaction time delta for algorithmic responses (<100ms)',
                'fallback_prior': [0.75, 0.20, 0.05],
                'evidence_type': 'timing_pattern'
            },
            'passive_aggressive_ratio': {
                'type': 'passive_aggressive_ratio',
                'states': ['normal_ratio', 'increased_passive', 'increased_aggressive'],
                'description': 'Measures increase in passive/aggressive quoting after distorted signals',
                'fallback_prior': [0.80, 0.15, 0.05],
                'evidence_type': 'quoting_pattern'
            },
            'commodity_leg_matching': {
                'type': 'commodity_leg_matching',
                'states': ['no_matching', 'partial_matching', 'full_matching'],
                'description': 'Detects leg-level matches across time-separated commodity contracts',
                'fallback_prior': [0.85, 0.12, 0.03],
                'evidence_type': 'commodity_pattern'
            },
            'third_party_risk_validation': {
                'type': 'third_party_risk_validation',
                'states': ['risk_transferred', 'risk_partially_transferred', 'no_risk_transfer'],
                'description': 'Validates whether third-party risk change occurred despite price differences',
                'fallback_prior': [0.78, 0.18, 0.04],
                'evidence_type': 'risk_analysis'
            },
            'mean_reversion_pattern': {
                'type': 'mean_reversion_pattern',
                'states': ['normal_movement', 'quick_reversion', 'immediate_reversion'],
                'description': 'Detects immediate mean reversion after trade',
                'fallback_prior': [0.75, 0.20, 0.05],
                'evidence_type': 'reversion_pattern'
            },
            'price_spike_fade': {
                'type': 'price_spike_fade',
                'states': ['normal_price_action', 'price_spike', 'price_fade'],
                'description': 'Detects price spike or fade within 10-60 seconds',
                'fallback_prior': [0.80, 0.12, 0.08],
                'evidence_type': 'price_movement'
            },
            'volatility_baseline_deviation': {
                'type': 'volatility_baseline_deviation',
                'states': ['within_baseline', 'moderate_deviation', 'extreme_deviation'],
                'description': 'Cross-references with historical volatility baseline',
                'fallback_prior': [0.75, 0.20, 0.05],
                'evidence_type': 'volatility_pattern'
            },
            'venue_implied_matching': {
                'type': 'venue_implied_matching',
                'states': ['direct_matching', 'implied_matching', 'artificial_matching'],
                'description': 'Detects venue-level implied matching facility usage',
                'fallback_prior': [0.80, 0.15, 0.05],
                'evidence_type': 'venue_pattern'
            },
            'leg_execution_source': {
                'type': 'leg_execution_source',
                'states': ['external_source', 'internal_book', 'strategy_order'],
                'description': 'Compares leg execution source with participant book and strategy orders',
                'fallback_prior': [0.70, 0.25, 0.05],
                'evidence_type': 'execution_source'
            },
            'wash_trade_latent_intent': {
                'type': 'wash_trade_latent_intent',
                'states': ['legitimate_trading', 'potential_wash_trade', 'clear_wash_trade'],
                'description': 'Hidden wash trade intent inference',
                'fallback_prior': [0.90, 0.08, 0.02],
                'evidence_type': 'latent'
            },
            'signal_distortion_latent_intent': {
                'type': 'signal_distortion_latent_intent',
                'states': ['normal_signaling', 'potential_distortion', 'clear_distortion'],
                'description': 'Hidden signal distortion intent inference',
                'fallback_prior': [0.88, 0.10, 0.02],
                'evidence_type': 'latent'
            },
            'risk_factor': {
                'type': 'risk_factor',
                'states': ['low_risk', 'medium_risk', 'high_risk'],
                'description': 'Intermediate risk assessment factor',
                'fallback_prior': [0.80, 0.15, 0.05],
                'evidence_type': 'intermediate'
            },
            'wash_trade_detection': {
                'type': 'outcome',
                'states': ['no_wash_trade', 'wash_trade_detected'],
                'description': 'Wash trade detection outcome',
                'fallback_prior': [0.97, 0.03],
                'evidence_type': 'outcome'
            }
        }
    
    def create_node(self, node_name: str, description: str = "", 
                   fallback_prior: Optional[list] = None) -> Any:
        """
        Create a node instance.
        
        Args:
            node_name: Name of the node to create
            description: Optional description override
            fallback_prior: Optional fallback prior override
            
        Returns:
            Node instance
        """
        if node_name not in self.node_definitions:
            raise ValueError(f"Unknown node: {node_name}")
        
        node_def = self.node_definitions[node_name]
        
        # Use provided parameters or defaults
        final_description = description or node_def['description']
        final_fallback_prior = fallback_prior or node_def['fallback_prior']
        
        # Create node using the library
        node = self.node_library.create_node(
            node_type=node_def['type'],
            name=node_name,
            description=final_description,
            fallback_prior=final_fallback_prior
        )
        
        logger.debug(f"Created node: {node_name}")
        return node
    
    def get_node(self, node_name: str) -> Any:
        """
        Get a node instance (creates if not exists).
        
        Args:
            node_name: Name of the node
            
        Returns:
            Node instance
        """
        return self.create_node(node_name)
    
    def get_evidence_nodes(self) -> Dict[str, Any]:
        """
        Get all evidence nodes for the model.
        
        Returns:
            Dictionary of evidence nodes
        """
        evidence_nodes = {}
        
        for node_name, node_def in self.node_definitions.items():
            if node_def['evidence_type'] in ['trade_pattern', 'market_signal', 'algo_response', 
                                             'strategy_pattern', 'price_pattern', 'liquidity_pattern',
                                             'entity_analysis', 'execution_pattern', 'execution_method',
                                             'orderbook_signal', 'quote_pattern', 'spread_pattern',
                                             'flow_pattern', 'timing_pattern', 'quoting_pattern',
                                             'commodity_pattern', 'risk_analysis', 'reversion_pattern',
                                             'price_movement', 'volatility_pattern', 'venue_pattern',
                                             'execution_source']:
                evidence_nodes[node_name] = self.create_node(node_name)
        
        return evidence_nodes
    
    def get_latent_nodes(self) -> Dict[str, Any]:
        """
        Get all latent nodes for the model.
        
        Returns:
            Dictionary of latent nodes
        """
        latent_nodes = {}
        
        for node_name, node_def in self.node_definitions.items():
            if node_def['evidence_type'] == 'latent':
                latent_nodes[node_name] = self.create_node(node_name)
        
        return latent_nodes
    
    def get_outcome_nodes(self) -> Dict[str, Any]:
        """
        Get all outcome nodes for the model.
        
        Returns:
            Dictionary of outcome nodes
        """
        outcome_nodes = {}
        
        for node_name, node_def in self.node_definitions.items():
            if node_def['evidence_type'] == 'outcome':
                outcome_nodes[node_name] = self.create_node(node_name)
        
        return outcome_nodes
    
    def get_core_requirement_nodes(self) -> list:
        """
        Get the core requirement nodes from KOR.AI Model Enhancement.
        
        Returns:
            List of core requirement node names
        """
        return [
            'wash_trade_likelihood',
            'signal_distortion_index',
            'algo_reaction_sensitivity',
            'strategy_leg_overlap',
            'price_impact_anomaly',
            'implied_liquidity_conflict'
        ]
    
    def get_supporting_evidence_nodes(self) -> list:
        """
        Get the supporting evidence nodes.
        
        Returns:
            List of supporting evidence node names
        """
        return [
            'counterparty_entity_match',
            'algo_framework_match',
            'implied_strategy_execution',
            'order_book_impact',
            'quote_frequency_distortion',
            'spread_manipulation',
            'order_flow_clustering',
            'reaction_time_delta',
            'passive_aggressive_ratio',
            'commodity_leg_matching',
            'third_party_risk_validation',
            'mean_reversion_pattern',
            'price_spike_fade',
            'volatility_baseline_deviation',
            'venue_implied_matching',
            'leg_execution_source'
        ]
    
    def get_node_definition(self, node_name: str) -> Dict[str, Any]:
        """
        Get definition for a specific node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Node definition dictionary
        """
        if node_name not in self.node_definitions:
            raise ValueError(f"Unknown node: {node_name}")
        
        return self.node_definitions[node_name].copy()
    
    def get_all_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all node definitions.
        
        Returns:
            Dictionary of all node definitions
        """
        return self.node_definitions.copy()
    
    def validate_node_compatibility(self, node_name: str) -> bool:
        """
        Validate if a node is compatible with the model.
        
        Args:
            node_name: Name of the node to validate
            
        Returns:
            True if compatible, False otherwise
        """
        try:
            node_def = self.get_node_definition(node_name)
            
            # Check if node type is available in library
            if node_def['type'] not in self.node_library.get_node_classes():
                logger.error(f"Node type {node_def['type']} not available in library")
                return False
            
            # Check if states are properly defined
            if not node_def.get('states') or not isinstance(node_def['states'], list):
                logger.error(f"Invalid states definition for node {node_name}")
                return False
            
            # Check if fallback prior matches states
            if len(node_def['fallback_prior']) != len(node_def['states']):
                logger.error(f"Fallback prior length doesn't match states for node {node_name}")
                return False
            
            logger.debug(f"Node {node_name} is compatible")
            return True
            
        except Exception as e:
            logger.error(f"Error validating node {node_name}: {str(e)}")
            return False
    
    def get_node_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the nodes.
        
        Returns:
            Dictionary of node statistics
        """
        stats = {
            'total_nodes': len(self.node_definitions),
            'core_requirement_nodes': len(self.get_core_requirement_nodes()),
            'supporting_evidence_nodes': len(self.get_supporting_evidence_nodes()),
            'latent_nodes': 0,
            'outcome_nodes': 0,
            'intermediate_nodes': 0
        }
        
        for node_def in self.node_definitions.values():
            evidence_type = node_def['evidence_type']
            if evidence_type == 'latent':
                stats['latent_nodes'] += 1
            elif evidence_type == 'outcome':
                stats['outcome_nodes'] += 1
            elif evidence_type == 'intermediate':
                stats['intermediate_nodes'] += 1
        
        return stats
    
    def __repr__(self) -> str:
        """String representation of the nodes manager."""
        stats = self.get_node_statistics()
        return f"WashTradeDetectionNodes(total_nodes={stats['total_nodes']}, core_nodes={stats['core_requirement_nodes']})"