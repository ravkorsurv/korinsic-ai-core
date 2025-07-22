"""
Nodes helper for Market Cornering Detection Model.

This module contains the MarketCorneringNodes class which manages
the creation and configuration of nodes for the market cornering model.
"""

from typing import Dict, Any, Optional, List
from ..shared.node_library import BayesianNodeLibrary
from .config import MarketCorneringConfig


class MarketCorneringNodes:
    """
    Helper class for managing market cornering detection nodes.
    
    This class provides easy access to node creation and management
    for the market cornering detection model.
    """
    
    def __init__(self, config: Optional[MarketCorneringConfig] = None):
        """
        Initialize the market cornering nodes helper.
        
        Args:
            config: Optional configuration instance
        """
        self.config = config or MarketCorneringConfig()
        self.library = BayesianNodeLibrary()
        self.node_definitions = self._get_node_definitions()
    
    def _get_node_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get node definitions for the market cornering model.
        
        Returns:
            Dictionary of node definitions
        """
        return {
            # Evidence nodes
            'market_concentration': {
                'type': 'evidence',
                'class': 'market_concentration',
                'description': 'Market concentration analysis for cornering detection',
                'states': ['dispersed', 'concentrated', 'highly_concentrated'],
                'fallback_prior': [0.70, 0.25, 0.05]
            },
            'position_accumulation': {
                'type': 'evidence',
                'class': 'position_accumulation',
                'description': 'Position accumulation pattern analysis',
                'states': ['normal_accumulation', 'systematic_accumulation', 'aggressive_accumulation'],
                'fallback_prior': [0.75, 0.20, 0.05]
            },
            'supply_control': {
                'type': 'evidence',
                'class': 'supply_control',
                'description': 'Supply control analysis for cornering detection',
                'states': ['limited_control', 'significant_control', 'dominant_control'],
                'fallback_prior': [0.80, 0.15, 0.05]
            },
            'liquidity_manipulation': {
                'type': 'evidence',
                'class': 'liquidity_manipulation',
                'description': 'Liquidity manipulation detection',
                'states': ['normal_liquidity', 'constrained_liquidity', 'manipulated_liquidity'],
                'fallback_prior': [0.75, 0.20, 0.05]
            },
            'price_distortion': {
                'type': 'evidence',
                'class': 'price_distortion',
                'description': 'Price distortion analysis',
                'states': ['fair_pricing', 'moderate_distortion', 'extreme_distortion'],
                'fallback_prior': [0.70, 0.25, 0.05]
            },
            'delivery_constraint': {
                'type': 'evidence',
                'class': 'delivery_constraint',
                'description': 'Delivery constraint analysis',
                'states': ['normal_delivery', 'constrained_delivery', 'blocked_delivery'],
                'fallback_prior': [0.75, 0.20, 0.05]
            },
            
            # Latent intent node
            'cornering_latent_intent': {
                'type': 'latent_intent',
                'class': 'cornering_latent_intent',
                'description': 'Market cornering latent intent inference',
                'states': ['no_intent', 'potential_intent', 'clear_intent'],
                'fallback_prior': [0.90, 0.08, 0.02]
            },
            
            # Risk factor node
            'risk_factor': {
                'type': 'risk_factor',
                'class': 'risk_factor',
                'description': 'Market cornering risk factor',
                'states': ['low_risk', 'medium_risk', 'high_risk'],
                'fallback_prior': [0.70, 0.25, 0.05]
            },
            
            # Outcome node
            'market_cornering': {
                'type': 'outcome',
                'class': 'outcome',
                'description': 'Market cornering outcome assessment',
                'states': ['no_cornering', 'cornering'],
                'fallback_prior': [0.95, 0.05]
            }
        }
    
    def get_node(self, node_name: str) -> Optional[Any]:
        """
        Get a specific node by name.
        
        Args:
            node_name: Name of the node to retrieve
            
        Returns:
            Node instance or None if not found
        """
        if node_name not in self.node_definitions:
            return None
        
        node_def = self.node_definitions[node_name]
        
        try:
            # Create node using the library
            node = self.library.create_node(
                node_def['class'],
                node_name,
                description=node_def['description']
            )
            
            # Set fallback prior if available
            if hasattr(node, 'fallback_prior') and 'fallback_prior' in node_def:
                node.fallback_prior = node_def['fallback_prior']
            
            return node
            
        except Exception:
            return None
    
    def get_evidence_nodes(self) -> Dict[str, Any]:
        """
        Get all evidence nodes for the model.
        
        Returns:
            Dictionary of evidence nodes
        """
        evidence_nodes = {}
        
        for node_name, node_def in self.node_definitions.items():
            if node_def['type'] == 'evidence':
                node = self.get_node(node_name)
                if node:
                    evidence_nodes[node_name] = node
        
        return evidence_nodes
    
    def get_latent_intent_nodes(self) -> Dict[str, Any]:
        """
        Get all nodes for latent intent model structure.
        
        Returns:
            Dictionary of nodes for latent intent model
        """
        return {name: self.get_node(name) for name in self.node_definitions.keys()}
    
    def get_standard_nodes(self) -> Dict[str, Any]:
        """
        Get all nodes for standard model structure.
        
        Returns:
            Dictionary of nodes for standard model
        """
        # Standard model excludes latent intent node
        standard_nodes = {}
        
        for node_name, node_def in self.node_definitions.items():
            if node_def['type'] != 'latent_intent':
                node = self.get_node(node_name)
                if node:
                    standard_nodes[node_name] = node
        
        return standard_nodes
    
    def get_node_definition(self, node_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the definition for a specific node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Node definition or None if not found
        """
        return self.node_definitions.get(node_name)
    
    def get_all_node_names(self) -> List[str]:
        """
        Get names of all nodes in the model.
        
        Returns:
            List of node names
        """
        return list(self.node_definitions.keys())
    
    def get_evidence_node_names(self) -> List[str]:
        """
        Get names of all evidence nodes.
        
        Returns:
            List of evidence node names
        """
        return [
            name for name, node_def in self.node_definitions.items()
            if node_def['type'] == 'evidence'
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
        node_def = self.node_definitions.get(node_name)
        if not node_def:
            return False
        
        states = node_def['states']
        
        # Check if value is a valid state index
        if isinstance(value, int):
            return 0 <= value < len(states)
        
        # Check if value is a valid state name
        if isinstance(value, str):
            return value in states
        
        return False
    
    def get_node_states(self, node_name: str) -> Optional[List[str]]:
        """
        Get states for a specific node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            List of node states or None if not found
        """
        node_def = self.node_definitions.get(node_name)
        if node_def:
            return node_def['states']
        return None
    
    def get_state_index(self, node_name: str, state: str) -> int:
        """
        Get the index of a state for a specific node.
        
        Args:
            node_name: Name of the node
            state: State name
            
        Returns:
            State index or -1 if not found
        """
        states = self.get_node_states(node_name)
        if states and state in states:
            return states.index(state)
        return -1
    
    def get_state_name(self, node_name: str, index: int) -> Optional[str]:
        """
        Get the state name for a specific node and index.
        
        Args:
            node_name: Name of the node
            index: State index
            
        Returns:
            State name or None if not found
        """
        states = self.get_node_states(node_name)
        if states and 0 <= index < len(states):
            return states[index]
        return None
    
    def get_evidence_weights(self) -> Dict[str, float]:
        """
        Get evidence weights from configuration.
        
        Returns:
            Dictionary of evidence weights
        """
        return self.config.get_evidence_weights()
    
    def get_node_weight(self, node_name: str) -> float:
        """
        Get weight for a specific node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Node weight
        """
        weights = self.get_evidence_weights()
        return weights.get(node_name, 0.0)
    
    def get_state_weight(self, node_name: str, state: str) -> float:
        """
        Get weight for a specific state.
        
        Args:
            node_name: Name of the node
            state: State name
            
        Returns:
            State weight
        """
        return self.config.get_state_weight(node_name, state)
    
    def create_evidence_dict(self, **kwargs) -> Dict[str, Any]:
        """
        Create an evidence dictionary with validation.
        
        Args:
            **kwargs: Evidence values
            
        Returns:
            Validated evidence dictionary
        """
        evidence = {}
        
        for node_name, value in kwargs.items():
            if self.validate_node_value(node_name, value):
                evidence[node_name] = value
        
        return evidence
    
    def get_fallback_prior(self, node_name: str) -> Optional[List[float]]:
        """
        Get fallback prior for a specific node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Fallback prior or None if not found
        """
        node_def = self.node_definitions.get(node_name)
        if node_def:
            return node_def.get('fallback_prior')
        return None
    
    def get_nodes_info(self) -> Dict[str, Any]:
        """
        Get information about all nodes in the model.
        
        Returns:
            Dictionary containing node information
        """
        info = {
            'total_nodes': len(self.node_definitions),
            'evidence_nodes': len(self.get_evidence_node_names()),
            'node_types': {},
            'nodes': {}
        }
        
        # Count node types
        for node_name, node_def in self.node_definitions.items():
            node_type = node_def['type']
            if node_type not in info['node_types']:
                info['node_types'][node_type] = 0
            info['node_types'][node_type] += 1
            
            # Add node info
            info['nodes'][node_name] = {
                'type': node_type,
                'description': node_def['description'],
                'states': node_def['states'],
                'state_count': len(node_def['states'])
            }
        
        return info
    
    def __str__(self) -> str:
        """String representation of the nodes helper."""
        return f"MarketCorneringNodes(nodes={len(self.node_definitions)})"
    
    def __repr__(self) -> str:
        """Representation of the nodes helper."""
        return self.__str__()