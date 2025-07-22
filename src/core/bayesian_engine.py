"""
Core Bayesian inference engine for detecting market abuse patterns
using probabilistic graphical models
"""

import json
import numpy as np
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from typing import Dict, List, Any
import logging
from .fallback_logic import apply_fallback_evidence
from .risk_aggregator import ComplexRiskAggregator
from .evidence_sufficiency_index import EvidenceSufficiencyIndex
from .regulatory_explainability import RegulatoryExplainability
import os
from .node_library import BayesianNode
from datetime import datetime
from src.models.bayesian.shared.model_builder import build_insider_dealing_bn

logger = logging.getLogger(__name__)

def map_insider_dealing_evidence(processed_data: Dict[str, Any]) -> Dict[str, int]:
    """Map processed data to Bayesian node names and state indices for insider dealing."""
    from logging import getLogger
    logger = getLogger(__name__)
    logger.info(f"[EVIDENCE MAPPING] processed_data={processed_data}")
    evidence = {}
    trader_info = processed_data.get('trader_info', {})
    market_data = processed_data.get('market_data', {})
    comms = processed_data.get('communications', [])
    pnl = processed_data.get('pnl_data', {})
    # trade_pattern: 0=normal, 1=suspicious (use volatility or price_movement as proxy)
    evidence['trade_pattern'] = 1 if market_data.get('volatility', 0) > 0.2 or market_data.get('price_movement', 0) > 0.1 else 0
    # comms_intent: 0=benign, 1=suspicious, 2=malicious
    evidence['comms_intent'] = 2 if any('sensitive' in c.get('content', '').lower() for c in comms) else 0
    # pnl_drift: 0=normal, 1=anomalous
    evidence['pnl_drift'] = 1 if pnl.get('daily_loss', 0) <= -100000 else 0
    # news_timing: 0=normal, 1=delayed, 2=unexplained (use price_movement as proxy)
    evidence['news_timing'] = 2 if market_data.get('price_movement', 0) > 0.1 else 0
    # state_information_access: 0=none, 1=potential, 2=clear
    evidence['state_information_access'] = 2 if trader_info.get('access_level', '').lower() == 'high' else 0
    logger.info(f"[EVIDENCE MAPPING] mapped_evidence={evidence}")
    return evidence

def apply_fallback_evidence_with_usage(evidence: Dict[str, Any], node_defs: Dict[str, BayesianNode]):
    completed_evidence = evidence.copy()
    fallback_usage = {}
    for node_name, node in node_defs.items():
        if node_name not in completed_evidence or completed_evidence[node_name] is None:
            fallback = node.get_fallback_prior()
            max_idx = fallback.index(max(fallback))
            completed_evidence[node_name] = max_idx
            fallback_usage[node_name] = True
        else:
            fallback_usage[node_name] = False
    return completed_evidence, fallback_usage

class BayesianEngine:
    """
    Core Bayesian inference engine for detecting market abuse patterns
    using probabilistic graphical models
    """
    
    def __init__(self):
        self.insider_dealing_model = None
        self.spoofing_model = None
        self.models_loaded = False
        self.risk_aggregator = ComplexRiskAggregator()
        self.esi_calculator = EvidenceSufficiencyIndex()
        self._load_models()
    
    def _load_models(self):
        """Load and initialize Bayesian models"""
        try:
            self._create_insider_dealing_model()
            self._create_spoofing_model()
            self.models_loaded = True
            logger.info("Bayesian models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Bayesian models: {str(e)}")
            raise
    
    def _create_insider_dealing_model(self):
        """Create Bayesian network for insider dealing detection (standardized MVP model)"""
        model = build_insider_dealing_bn()
        self.insider_dealing_model = model
        self.insider_dealing_inference = VariableElimination(model)
        # Node definitions for fallback logic
        self.insider_dealing_node_defs = {
            'trade_pattern': BayesianNode('trade_pattern', ['normal', 'suspicious'], fallback_prior=[0.95, 0.05]),
            'comms_intent': BayesianNode('comms_intent', ['benign', 'suspicious', 'malicious'], fallback_prior=[0.8, 0.15, 0.05]),
            'pnl_drift': BayesianNode('pnl_drift', ['normal', 'anomalous'], fallback_prior=[0.9, 0.1]),
            'news_timing': BayesianNode('news_timing', ['normal', 'delayed', 'unexplained'], fallback_prior=[0.85, 0.12, 0.03]),
            'state_information_access': BayesianNode('state_information_access', ['none', 'potential', 'clear'], fallback_prior=[0.88, 0.10, 0.02])
        }
    
    def _create_spoofing_model(self):
        """Create Bayesian network for spoofing detection"""
        model = DiscreteBayesianNetwork([
            ('OrderPattern', 'Risk'),
            ('CancellationRate', 'Risk'),
            ('PriceMovement', 'Risk'),
            ('VolumeRatio', 'Risk'),
            ('OrderPattern', 'CancellationRate'),
            ('OrderPattern', 'VolumeRatio')
        ])
        
        cpd_pattern = TabularCPD(
            variable='OrderPattern',
            variable_card=3,
            values=[[0.85], [0.12], [0.03]]
        )
        
        cpd_cancellation = TabularCPD(
            variable='CancellationRate',
            variable_card=3,
            values=[
                [0.8, 0.4, 0.1],
                [0.15, 0.4, 0.3],
                [0.05, 0.2, 0.6]
            ],
            evidence=['OrderPattern'],
            evidence_card=[3]
        )
        
        cpd_price_movement = TabularCPD(
            variable='PriceMovement',
            variable_card=3,
            values=[[0.7], [0.25], [0.05]]
        )
        
        cpd_volume = TabularCPD(
            variable='VolumeRatio',
            variable_card=3,
            values=[
                [0.8, 0.5, 0.2],
                [0.15, 0.3, 0.3],
                [0.05, 0.2, 0.5]
            ],
            evidence=['OrderPattern'],
            evidence_card=[3]
        )
        
        base_low = [0.95, 0.9, 0.8, 0.85, 0.7, 0.5, 0.7, 0.5, 0.2,
                    0.8, 0.7, 0.5, 0.6, 0.4, 0.2, 0.4, 0.2, 0.1,
                    0.5, 0.3, 0.1, 0.3, 0.1, 0.05, 0.2, 0.05, 0.01]
        base_med = [0.04, 0.08, 0.15, 0.12, 0.25, 0.35, 0.25, 0.35, 0.3,
                    0.15, 0.25, 0.35, 0.3, 0.45, 0.5, 0.45, 0.5, 0.4,
                    0.35, 0.5, 0.4, 0.5, 0.4, 0.35, 0.5, 0.35, 0.24]
        base_high = [0.01, 0.02, 0.05, 0.03, 0.05, 0.15, 0.05, 0.15, 0.5,
                     0.05, 0.05, 0.15, 0.1, 0.15, 0.3, 0.15, 0.3, 0.5,
                     0.15, 0.2, 0.5, 0.2, 0.5, 0.6, 0.3, 0.6, 0.75]
        
        cpd_risk = TabularCPD(
            variable='Risk',
            variable_card=3,
            values=[
                base_low * 3,
                base_med * 3,
                base_high * 3
            ],
            evidence=['OrderPattern', 'CancellationRate', 'PriceMovement', 'VolumeRatio'],
            evidence_card=[3, 3, 3, 3]
        )
        
        model.add_cpds(cpd_pattern, cpd_cancellation, cpd_price_movement, cpd_volume, cpd_risk)
        assert model.check_model()
        self.spoofing_model = model
        self.spoofing_inference = VariableElimination(model)
        self.spoofing_node_defs = {
            'OrderPattern': BayesianNode('OrderPattern', ['benign', 'suspicious', 'malicious'], fallback_prior=[0.85, 0.12, 0.03]),
            'CancellationRate': BayesianNode('CancellationRate', ['low', 'medium', 'high'], fallback_prior=[0.8, 0.15, 0.05]),
            'PriceMovement': BayesianNode('PriceMovement', ['stable', 'volatile', 'extreme'], fallback_prior=[0.7, 0.25, 0.05]),
            'VolumeRatio': BayesianNode('VolumeRatio', ['low', 'medium', 'high'], fallback_prior=[0.8, 0.15, 0.05])
        }
    
    def analyze_insider_dealing(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze insider dealing patterns using Bayesian inference"""
        try:
            # Map evidence to Bayesian node names and state indices
            mapped_evidence = map_insider_dealing_evidence(evidence)
            logger.info(f"Mapped evidence for insider dealing: {mapped_evidence}")
            # Apply fallback evidence if needed, and track fallback usage
            evidence, fallback_usage = apply_fallback_evidence_with_usage(mapped_evidence, self.insider_dealing_node_defs)
            # Perform inference
            query = self.insider_dealing_inference.query(variables=['insider_dealing'], evidence=evidence)
            risk_probabilities = query.values
            # Calculate risk score as probability of 'yes' (index 1)
            risk_score = float(risk_probabilities[1]) if hasattr(risk_probabilities, '__getitem__') else 0.0
            logger.info(f"[BAYESIAN] risk_probabilities={risk_probabilities}, risk_score={risk_score}")
            # Calculate ESI
            esi_score = self.esi_calculator.calculate_esi(evidence, evidence, fallback_usage)
            return {
                'risk_score': risk_score,
                'overall_score': risk_score,
                'risk_probabilities': risk_probabilities.tolist() if hasattr(risk_probabilities, 'tolist') else list(risk_probabilities),
                'esi_score': esi_score,
                'evidence_used': evidence,
                'model_type': 'insider_dealing'
            }
        except Exception as e:
            logger.error(f"Error in insider dealing analysis: {str(e)}")
            return {
                'risk_score': 0.0,
                'overall_score': 0.0,
                'risk_probabilities': [0.0, 0.0, 0.0],
                'esi_score': 0.0,
                'evidence_used': {},
                'model_type': 'insider_dealing',
                'error': str(e)
            }
    
    def analyze_spoofing(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spoofing patterns using Bayesian inference"""
        try:
            # Apply fallback evidence if needed
            evidence = apply_fallback_evidence(evidence, self.spoofing_node_defs)
            
            # Perform inference
            query = self.spoofing_inference.query(variables=['Risk'], evidence=evidence)
            risk_probabilities = query.values
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(risk_probabilities)
            
            # Calculate ESI
            esi_score = self.esi_calculator.calculate_esi(evidence, 'spoofing')
            
            return {
                'risk_score': risk_score,
                'risk_probabilities': risk_probabilities.tolist(),
                'esi_score': esi_score,
                'evidence_used': evidence,
                'model_type': 'spoofing'
            }
        except Exception as e:
            logger.error(f"Error in spoofing analysis: {str(e)}")
            return {
                'risk_score': 0.5,
                'risk_probabilities': [0.5, 0.3, 0.2],
                'esi_score': 0.5,
                'evidence_used': evidence,
                'model_type': 'spoofing',
                'error': str(e)
            }
    
    def _calculate_risk_score(self, probabilities: np.ndarray) -> float:
        """Calculate risk score from probability distribution"""
        # Weighted average: Low=0, Medium=0.5, High=1
        weights = np.array([0.0, 0.5, 1.0])
        return float(np.sum(probabilities * weights))
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'models_loaded': self.models_loaded,
            'insider_dealing_model': self.insider_dealing_model is not None,
            'spoofing_model': self.spoofing_model is not None,
            'available_models': ['insider_dealing', 'spoofing']
        } 

    def get_models_info(self):
        return self.get_model_info() 