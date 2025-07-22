"""
Core Bayesian inference engine for detecting market abuse patterns
using probabilistic graphical models
"""

import json
import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from typing import Dict, List, Any
import logging
from .fallback_logic import apply_fallback_evidence
from .risk_aggregator import ComplexRiskAggregator
from .evidence_sufficiency_index import EvidenceSufficiencyIndex
from .regulatory_explainability import RegulatoryExplainability
import os

logger = logging.getLogger(__name__)

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
        """Create Bayesian network for insider dealing detection"""
        # Define the network structure
        model = BayesianNetwork([
            ('MaterialInfo', 'Risk'),
            ('TradingActivity', 'Risk'),
            ('Timing', 'Risk'),
            ('PriceImpact', 'Risk'),
            ('MaterialInfo', 'Timing'),
            ('TradingActivity', 'PriceImpact')
        ])
        
        # Define Conditional Probability Distributions
        cpd_material = TabularCPD(
            variable='MaterialInfo',
            variable_card=3,
            values=[[0.7], [0.25], [0.05]]
        )
        
        cpd_trading = TabularCPD(
            variable='TradingActivity',
            variable_card=3,
            values=[[0.8], [0.15], [0.05]]
        )
        
        cpd_timing = TabularCPD(
            variable='Timing',
            variable_card=3,
            values=[
                [0.9, 0.7, 0.3],
                [0.08, 0.2, 0.4],
                [0.02, 0.1, 0.3]
            ],
            evidence=['MaterialInfo'],
            evidence_card=[3]
        )
        
        cpd_price = TabularCPD(
            variable='PriceImpact',
            variable_card=3,
            values=[
                [0.8, 0.5, 0.2],
                [0.15, 0.3, 0.3],
                [0.05, 0.2, 0.5]
            ],
            evidence=['TradingActivity'],
            evidence_card=[3]
        )
        
        cpd_risk = TabularCPD(
            variable='Risk',
            variable_card=3,
            values=[
                [0.95, 0.9, 0.8, 0.85, 0.7, 0.5, 0.7, 0.5, 0.2,
                 0.9, 0.85, 0.75, 0.8, 0.65, 0.45, 0.65, 0.45, 0.15,
                 0.85, 0.8, 0.7, 0.75, 0.6, 0.4, 0.6, 0.4, 0.1,
                 0.8, 0.7, 0.5, 0.6, 0.4, 0.2, 0.4, 0.2, 0.1,
                 0.75, 0.65, 0.45, 0.55, 0.35, 0.15, 0.35, 0.15, 0.05,
                 0.7, 0.6, 0.4, 0.5, 0.3, 0.1, 0.3, 0.1, 0.02,
                 0.5, 0.3, 0.1, 0.3, 0.1, 0.05, 0.2, 0.05, 0.01,
                 0.45, 0.25, 0.05, 0.25, 0.05, 0.02, 0.15, 0.02, 0.005,
                 0.4, 0.2, 0.02, 0.2, 0.02, 0.01, 0.1, 0.01, 0.001],
                [0.04, 0.08, 0.15, 0.12, 0.25, 0.35, 0.25, 0.35, 0.3,
                 0.08, 0.12, 0.2, 0.15, 0.3, 0.4, 0.3, 0.4, 0.35,
                 0.12, 0.15, 0.25, 0.2, 0.35, 0.45, 0.35, 0.45, 0.4,
                 0.15, 0.25, 0.35, 0.3, 0.45, 0.5, 0.45, 0.5, 0.4,
                 0.2, 0.3, 0.4, 0.35, 0.5, 0.55, 0.5, 0.55, 0.45,
                 0.25, 0.35, 0.45, 0.4, 0.55, 0.6, 0.55, 0.6, 0.5,
                 0.35, 0.5, 0.4, 0.5, 0.4, 0.35, 0.5, 0.35, 0.24,
                 0.4, 0.55, 0.45, 0.55, 0.45, 0.4, 0.55, 0.4, 0.29,
                 0.45, 0.6, 0.5, 0.6, 0.5, 0.45, 0.6, 0.45, 0.34],
                [0.01, 0.02, 0.05, 0.03, 0.05, 0.15, 0.05, 0.15, 0.5,
                 0.02, 0.03, 0.05, 0.05, 0.05, 0.15, 0.05, 0.15, 0.5,
                 0.03, 0.05, 0.05, 0.05, 0.05, 0.15, 0.05, 0.15, 0.5,
                 0.05, 0.05, 0.15, 0.1, 0.15, 0.3, 0.15, 0.3, 0.5,
                 0.05, 0.05, 0.15, 0.1, 0.15, 0.3, 0.15, 0.3, 0.5,
                 0.05, 0.05, 0.15, 0.1, 0.15, 0.3, 0.15, 0.3, 0.48,
                 0.15, 0.2, 0.5, 0.2, 0.5, 0.6, 0.3, 0.6, 0.75,
                 0.15, 0.2, 0.5, 0.2, 0.5, 0.58, 0.3, 0.58, 0.705,
                 0.15, 0.2, 0.48, 0.2, 0.48, 0.54, 0.3, 0.54, 0.659]
            ],
            evidence=['MaterialInfo', 'TradingActivity', 'Timing', 'PriceImpact'],
            evidence_card=[3, 3, 3, 3]
        )
        
        model.add_cpds(cpd_material, cpd_trading, cpd_timing, cpd_price, cpd_risk)
        assert model.check_model()
        self.insider_dealing_model = model
        self.insider_dealing_inference = VariableElimination(model)
    
    def _create_spoofing_model(self):
        """Create Bayesian network for spoofing detection"""
        model = BayesianNetwork([
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
    
    def analyze_insider_dealing(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze insider dealing patterns using Bayesian inference"""
        try:
            # Apply fallback evidence if needed
            evidence = apply_fallback_evidence(evidence, 'insider_dealing')
            
            # Perform inference
            query = self.insider_dealing_inference.query(variables=['Risk'], evidence=evidence)
            risk_probabilities = query.values
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(risk_probabilities)
            
            # Calculate ESI
            esi_score = self.esi_calculator.calculate_esi(evidence, 'insider_dealing')
            
            return {
                'risk_score': risk_score,
                'risk_probabilities': risk_probabilities.tolist(),
                'esi_score': esi_score,
                'evidence_used': evidence,
                'model_type': 'insider_dealing'
            }
        except Exception as e:
            logger.error(f"Error in insider dealing analysis: {str(e)}")
            return {
                'risk_score': 0.5,
                'risk_probabilities': [0.5, 0.3, 0.2],
                'esi_score': 0.5,
                'evidence_used': evidence,
                'model_type': 'insider_dealing',
                'error': str(e)
            }
    
    def analyze_spoofing(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spoofing patterns using Bayesian inference"""
        try:
            # Apply fallback evidence if needed
            evidence = apply_fallback_evidence(evidence, 'spoofing')
            
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