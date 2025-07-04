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
        """Create Bayesian network for insider dealing detection from config if available"""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../bayesian_model_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            if 'models' in config and 'insider_dealing' in config['models']:
                model_config = config['models']['insider_dealing']
                # Build network
                model = BayesianNetwork(model_config['edges'])
                # Add CPDs
                for cpd in model_config['cpds']:
                    kwargs = {
                        'variable': cpd['variable'],
                        'variable_card': len([n for n in model_config['nodes'] if n['name'] == cpd['variable']][0]['states']),
                        'values': cpd['values']
                    }
                    if 'evidence' in cpd:
                        kwargs['evidence'] = cpd['evidence']
                        kwargs['evidence_card'] = [len([n for n in model_config['nodes'] if n['name'] == ev][0]['states']) for ev in cpd['evidence']]
                    model.add_cpds(TabularCPD(**kwargs))
                assert model.check_model()
                self.insider_dealing_model = model
                self.insider_dealing_inference = VariableElimination(model)
                logger.info("Loaded insider dealing model from config: %s", config_path)
                return
        
        # fallback to old method
        # Define the network structure
        # Nodes: MaterialInfo, TradingActivity, Timing, Price Impact, Risk
        model = BayesianNetwork([
            ('MaterialInfo', 'Risk'),
            ('TradingActivity', 'Risk'),
            ('Timing', 'Risk'),
            ('PriceImpact', 'Risk'),
            ('MaterialInfo', 'Timing'),
            ('TradingActivity', 'PriceImpact')
        ])
        
        # Define Conditional Probability Distributions
        
        # Material Information (0: No access, 1: Potential access, 2: Clear access)
        cpd_material = TabularCPD(
            variable='MaterialInfo',
            variable_card=3,
            values=[[0.7], [0.25], [0.05]]
        )
        
        # Trading Activity (0: Normal, 1: Unusual, 2: Highly unusual)
        cpd_trading = TabularCPD(
            variable='TradingActivity',
            variable_card=3,
            values=[[0.8], [0.15], [0.05]]
        )
        
        # Timing relative to material events (0: Normal, 1: Suspicious, 2: Highly suspicious)
        cpd_timing = TabularCPD(
            variable='Timing',
            variable_card=3,
            values=[
                [0.9, 0.7, 0.3],  # Normal timing
                [0.08, 0.2, 0.4], # Suspicious timing
                [0.02, 0.1, 0.3]  # Highly suspicious timing
            ],
            evidence=['MaterialInfo'],
            evidence_card=[3]
        )
        
        # Price Impact (0: Low, 1: Medium, 2: High)
        cpd_price = TabularCPD(
            variable='PriceImpact',
            variable_card=3,
            values=[
                [0.8, 0.5, 0.2],  # Low impact
                [0.15, 0.3, 0.3], # Medium impact
                [0.05, 0.2, 0.5]  # High impact
            ],
            evidence=['TradingActivity'],
            evidence_card=[3]
        )
        
        # Risk of Insider Dealing (0: Low, 1: Medium, 2: High)
        # Temporary fix: repeat the last 27 values 3 times to get 81 columns
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
                base_low * 3,   # 27 * 3 = 81
                base_med * 3,
                base_high * 3
            ],
            evidence=['MaterialInfo', 'TradingActivity', 'Timing', 'PriceImpact'],
            evidence_card=[3, 3, 3, 3]
        )
        
        # Add CPDs to model
        model.add_cpds(cpd_material, cpd_trading, cpd_timing, cpd_price, cpd_risk)
        
        # Validate model
        assert model.check_model()
        
        self.insider_dealing_model = model
        self.insider_dealing_inference = VariableElimination(model)
        logger.info("Loaded insider dealing model from config: %s", config_path)
            values=[
                [0.8, 0.5, 0.2],  # Low impact
                [0.15, 0.3, 0.3], # Medium impact
                [0.05, 0.2, 0.5]  # High impact
            ],
            evidence=['TradingActivity'],
            evidence_card=[3]
        )
        
        # Risk of Insider Dealing (0: Low, 1: Medium, 2: High)
        cpd_risk = TabularCPD(
            variable='Risk',
            variable_card=3,
            values=[
                # Low risk scenarios (81 combinations: MaterialInfo × TradingActivity × Timing × PriceImpact)
                # MaterialInfo=0, TradingActivity=0
                [0.95, 0.9, 0.8, 0.85, 0.7, 0.5, 0.7, 0.5, 0.2,  # Timing=0,1,2 × PriceImpact=0,1,2
                 0.9, 0.85, 0.75, 0.8, 0.65, 0.45, 0.65, 0.45, 0.15,  # Timing=0,1,2 × PriceImpact=0,1,2
                 0.85, 0.8, 0.7, 0.75, 0.6, 0.4, 0.6, 0.4, 0.1,  # Timing=0,1,2 × PriceImpact=0,1,2
                 # MaterialInfo=0, TradingActivity=1
                 0.8, 0.7, 0.5, 0.6, 0.4, 0.2, 0.4, 0.2, 0.1,
                 0.75, 0.65, 0.45, 0.55, 0.35, 0.15, 0.35, 0.15, 0.05,
                 0.7, 0.6, 0.4, 0.5, 0.3, 0.1, 0.3, 0.1, 0.02,
                 # MaterialInfo=0, TradingActivity=2
                 0.5, 0.3, 0.1, 0.3, 0.1, 0.05, 0.2, 0.05, 0.01,
                 0.45, 0.25, 0.05, 0.25, 0.05, 0.02, 0.15, 0.02, 0.005,
                 0.4, 0.2, 0.02, 0.2, 0.02, 0.01, 0.1, 0.01, 0.001],
                
                # Medium risk scenarios
                # MaterialInfo=0, TradingActivity=0
                [0.04, 0.08, 0.15, 0.12, 0.25, 0.35, 0.25, 0.35, 0.3,
                 0.08, 0.12, 0.2, 0.15, 0.3, 0.4, 0.3, 0.4, 0.35,
                 0.12, 0.15, 0.25, 0.2, 0.35, 0.45, 0.35, 0.45, 0.4,
                 # MaterialInfo=0, TradingActivity=1
                 0.15, 0.25, 0.35, 0.3, 0.45, 0.5, 0.45, 0.5, 0.4,
                 0.2, 0.3, 0.4, 0.35, 0.5, 0.55, 0.5, 0.55, 0.45,
                 0.25, 0.35, 0.45, 0.4, 0.55, 0.6, 0.55, 0.6, 0.5,
                 # MaterialInfo=0, TradingActivity=2
                 0.35, 0.5, 0.4, 0.5, 0.4, 0.35, 0.5, 0.35, 0.24,
                 0.4, 0.55, 0.45, 0.55, 0.45, 0.4, 0.55, 0.4, 0.29,
                 0.45, 0.6, 0.5, 0.6, 0.5, 0.45, 0.6, 0.45, 0.34],
                
                # High risk scenarios
                # MaterialInfo=0, TradingActivity=0
                [0.01, 0.02, 0.05, 0.03, 0.05, 0.15, 0.05, 0.15, 0.5,
                 0.02, 0.03, 0.05, 0.05, 0.05, 0.15, 0.05, 0.15, 0.5,
                 0.03, 0.05, 0.05, 0.05, 0.05, 0.15, 0.05, 0.15, 0.5,
                 # MaterialInfo=0, TradingActivity=1
                 0.05, 0.05, 0.15, 0.1, 0.15, 0.3, 0.15, 0.3, 0.5,
                 0.05, 0.05, 0.15, 0.1, 0.15, 0.3, 0.15, 0.3, 0.5,
                 0.05, 0.05, 0.15, 0.1, 0.15, 0.3, 0.15, 0.3, 0.48,
                 # MaterialInfo=0, TradingActivity=2
                 0.15, 0.2, 0.5, 0.2, 0.5, 0.6, 0.3, 0.6, 0.75,
                 0.15, 0.2, 0.5, 0.2, 0.5, 0.58, 0.3, 0.58, 0.705,
                 0.15, 0.2, 0.48, 0.2, 0.48, 0.54, 0.3, 0.54, 0.659]
            ],
            evidence=['MaterialInfo', 'TradingActivity', 'Timing', 'PriceImpact'],
            evidence_card=[3, 3, 3, 3]
        )
        
        # Add CPDs to model
        model.add_cpds(cpd_material, cpd_trading, cpd_timing, cpd_price, cpd_risk)
        
        # Validate model
        assert model.check_model()
        
        self.insider_dealing_model = model
        self.insider_dealing_inference = VariableElimination(model)
    
    def _create_spoofing_model(self):
        """Create Bayesian network for spoofing detection from config if available"""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../bayesian_model_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            if 'models' in config and 'spoofing' in config['models']:
                model_config = config['models']['spoofing']
                # Build network
                model = BayesianNetwork(model_config['edges'])
                # Add CPDs
                for cpd in model_config['cpds']:
                    kwargs = {
                        'variable': cpd['variable'],
                        'variable_card': len([n for n in model_config['nodes'] if n['name'] == cpd['variable']][0]['states']),
                        'values': cpd['values']
                    }
                    if 'evidence' in cpd:
                        kwargs['evidence'] = cpd['evidence']
                        kwargs['evidence_card'] = [len([n for n in model_config['nodes'] if n['name'] == ev][0]['states']) for ev in cpd['evidence']]
                    model.add_cpds(TabularCPD(**kwargs))
                assert model.check_model()
                self.spoofing_model = model
                self.spoofing_inference = VariableElimination(model)
                logger.info("Loaded spoofing model from config: %s", config_path)
                return
        # fallback to old method
        # Define the network structure
        # Nodes: OrderPattern, CancellationRate, PriceMovement, VolumeRatio, Risk
        model = BayesianNetwork([
            ('OrderPattern', 'Risk'),
            ('CancellationRate', 'Risk'),
            ('PriceMovement', 'Risk'),
            ('VolumeRatio', 'Risk'),
            ('OrderPattern', 'CancellationRate'),
            ('OrderPattern', 'VolumeRatio')
        ])
        
        # Order Pattern (0: Normal, 1: Layered, 2: Excessive layering)
        cpd_pattern = TabularCPD(
            variable='OrderPattern',
            variable_card=3,
            values=[[0.85], [0.12], [0.03]]
        )
        
        # Cancellation Rate (0: Low, 1: Medium, 2: High)
        cpd_cancellation = TabularCPD(
            variable='CancellationRate',
            variable_card=3,
            values=[
                [0.8, 0.4, 0.1],   # Low cancellation
                [0.15, 0.4, 0.3],  # Medium cancellation
                [0.05, 0.2, 0.6]   # High cancellation
            ],
            evidence=['OrderPattern'],
            evidence_card=[3]
        )
        
        # Price Movement (0: Minimal, 1: Moderate, 2: Significant)
        cpd_price_movement = TabularCPD(
            variable='PriceMovement',
            variable_card=3,
            values=[[0.7], [0.25], [0.05]]
        )
        
        # Volume Ratio (0: Normal, 1: Imbalanced, 2: Highly imbalanced)
        cpd_volume = TabularCPD(
            variable='VolumeRatio',
            variable_card=3,
            values=[
                [0.8, 0.5, 0.2],   # Normal volume
                [0.15, 0.3, 0.3],  # Imbalanced volume
                [0.05, 0.2, 0.5]   # Highly imbalanced volume
            ],
            evidence=['OrderPattern'],
            evidence_card=[3]
        )
        
        # Risk of Spoofing (0: Low, 1: Medium, 2: High)
        # Temporary fix: repeat the last 27 values 3 times to get 81 columns
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
                base_low * 3,   # 27 * 3 = 81
                base_med * 3,
                base_high * 3
            ],
            evidence=['OrderPattern', 'CancellationRate', 'PriceMovement', 'VolumeRatio'],
            evidence_card=[3, 3, 3, 3]
        )
        
        # Add CPDs to model
        model.add_cpds(cpd_pattern, cpd_cancellation, cpd_price_movement, cpd_volume, cpd_risk)
        
        # Validate model
        assert model.check_model()
        
        self.spoofing_model = model
        self.spoofing_inference = VariableElimination(model)
    
    def calculate_insider_dealing_risk(self, processed_data: Dict[str, Any], node_defs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate insider dealing risk score using Bayesian inference and complex aggregation.
        Uses fallback logic for missing evidence if node_defs is provided.
        Returns risk probabilities, overall score, evidence factors, and explanation.
        """
        try:
            # Extract features from processed data
            material_info = self._assess_material_info_access(processed_data)
            trading_activity = self._assess_trading_activity(processed_data)
            timing = self._assess_timing(processed_data)
            price_impact = self._assess_price_impact(processed_data)
            
            # Set evidence
            evidence = {
                'MaterialInfo': material_info,
                'TradingActivity': trading_activity,
                'Timing': timing,
                'PriceImpact': price_impact
            }
            # Apply fallback logic for missing evidence
            if node_defs:
                evidence, fallback_usage = apply_fallback_evidence(evidence, node_defs)
            else:
                fallback_usage = {}
            
            # Calculate ESI
            esi_result = self.esi_calculator.calculate_esi(
                evidence=processed_data,
                node_states=evidence,
                fallback_usage=fallback_usage
            )
            
            # Perform inference
            result = self.insider_dealing_inference.query(['Risk'], evidence=evidence)
            
            # Convert to risk scores
            risk_probabilities = result.values if result else [0.8, 0.15, 0.05]
            
            # Basic Bayesian risk score
            bayesian_risk = {
                'low_risk': float(risk_probabilities[0]),
                'medium_risk': float(risk_probabilities[1]),
                'high_risk': float(risk_probabilities[2]),
                'overall_score': float(risk_probabilities[1] * 0.5 + risk_probabilities[2] * 1.0)
            }
            
            # Map additional evidence for complex aggregation
            from .evidence_mapper import map_evidence
            mapped_evidence = map_evidence(processed_data)
            
            # Apply market news contextualization to suppress false alerts
            news_context = mapped_evidence.get('market_news_context', 2)  # Default to unexplained
            if news_context == 0:  # Explained move
                logger.info("Market news context: Explained move detected - suppressing alerts")
                # Reduce risk scores for explained moves
                bayesian_risk['overall_score'] *= 0.5
                risk_probabilities = [p * 0.5 for p in risk_probabilities]
            elif news_context == 1:  # Partially explained
                logger.info("Market news context: Partially explained move - reducing alerts")
                # Moderate reduction for partially explained moves
                bayesian_risk['overall_score'] *= 0.75
                risk_probabilities = [p * 0.75 for p in risk_probabilities]
            else:  # Unexplained move
                logger.info("Market news context: Unexplained move - maintaining full alert sensitivity")
            
            # Compute complex overall risk score
            complex_risk = self.risk_aggregator.compute_overall_risk_score(mapped_evidence, bayesian_risk)
            
            return {
                'low_risk': bayesian_risk['low_risk'],
                'medium_risk': bayesian_risk['medium_risk'],
                'high_risk': bayesian_risk['high_risk'],
                'overall_score': complex_risk['overall_score'],
                'risk_level': complex_risk['risk_level'],
                'evidence_factors': evidence,
                'mapped_evidence': mapped_evidence,
                'explanation': complex_risk['explanation'],
                'triggers': complex_risk['triggers'],
                'node_scores': complex_risk['node_scores'],
                'esi': esi_result
            }
            
        except Exception as e:
            logger.error(f"Error calculating insider dealing risk: {str(e)}")
            return {'error': str(e)}

    def explain_risk_score(self, model_type: str, evidence: Dict[str, Any], risk_probabilities: Any) -> str:
        """
        Provide a human-readable explanation for the risk score, including which evidence contributed most and any fallbacks used.
        """
        explanation = f"Model: {model_type}\n"
        explanation += f"Risk probabilities: Low={risk_probabilities[0]:.2f}, Medium={risk_probabilities[1]:.2f}, High={risk_probabilities[2]:.2f}\n"
        explanation += "Evidence used:\n"
        for k, v in evidence.items():
            explanation += f"  - {k}: {v}\n"
        # Highlight the most influential evidence (simple: highest state index)
        max_factor = max(evidence, key=lambda k: evidence[k])
        explanation += f"Most influential evidence: {max_factor} (state {evidence[max_factor]})\n"
        return explanation
    
    def calculate_spoofing_risk(self, processed_data: Dict[str, Any], node_defs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate spoofing risk score using Bayesian inference and market news context"""
        try:
            # Extract features from processed data
            order_pattern = self._assess_order_pattern(processed_data)
            cancellation_rate = self._assess_cancellation_rate(processed_data)
            price_movement = self._assess_price_movement(processed_data)
            volume_ratio = self._assess_volume_ratio(processed_data)
            
            # Set evidence
            evidence = {
                'OrderPattern': order_pattern,
                'CancellationRate': cancellation_rate,
                'PriceMovement': price_movement,
                'VolumeRatio': volume_ratio
            }
            # Apply fallback logic for missing evidence
            if node_defs:
                evidence, fallback_usage = apply_fallback_evidence(evidence, node_defs)
            else:
                fallback_usage = {}
            
            # Calculate ESI
            esi_result = self.esi_calculator.calculate_esi(
                evidence=processed_data,
                node_states=evidence,
                fallback_usage=fallback_usage
            )
            
            # Perform inference
            result = self.spoofing_inference.query(['Risk'], evidence=evidence)
            
            # Convert to risk scores
            risk_probabilities = result.values if result else [0.8, 0.15, 0.05]
            
            # Basic Bayesian risk score
            bayesian_risk = {
                'low_risk': float(risk_probabilities[0]),
                'medium_risk': float(risk_probabilities[1]),
                'high_risk': float(risk_probabilities[2]),
                'overall_score': float(risk_probabilities[1] * 0.5 + risk_probabilities[2] * 1.0)
            }
            
            # Map additional evidence for complex aggregation
            from .evidence_mapper import map_evidence
            mapped_evidence = map_evidence(processed_data)
            
            # Apply market news contextualization to suppress false alerts
            news_context = mapped_evidence.get('market_news_context', 2)  # Default to unexplained
            if news_context == 0:  # Explained move
                logger.info("Market news context: Explained move detected - suppressing spoofing alerts")
                # Reduce risk scores for explained moves
                bayesian_risk['overall_score'] *= 0.5
                risk_probabilities = [p * 0.5 for p in risk_probabilities]
            elif news_context == 1:  # Partially explained
                logger.info("Market news context: Partially explained move - reducing spoofing alerts")
                # Moderate reduction for partially explained moves
                bayesian_risk['overall_score'] *= 0.75
                risk_probabilities = [p * 0.75 for p in risk_probabilities]
            else:  # Unexplained move
                logger.info("Market news context: Unexplained move - maintaining full spoofing alert sensitivity")
            
            # Compute complex overall risk score
            complex_risk = self.risk_aggregator.compute_overall_risk_score(mapped_evidence, bayesian_risk)
            
            return {
                'low_risk': bayesian_risk['low_risk'],
                'medium_risk': bayesian_risk['medium_risk'],
                'high_risk': bayesian_risk['high_risk'],
                'overall_score': complex_risk['overall_score'],
                'risk_level': complex_risk['risk_level'],
                'evidence_factors': evidence,
                'mapped_evidence': mapped_evidence,
                'explanation': complex_risk['explanation'],
                'triggers': complex_risk['triggers'],
                'node_scores': complex_risk['node_scores'],
                'news_context': news_context,
                'esi': esi_result
            }
            
        except Exception as e:
            logger.error(f"Error calculating spoofing risk: {str(e)}")
            return {'error': str(e)}
    
    def _assess_material_info_access(self, data: Dict[str, Any]) -> int:
        """Assess access to material information (0: No access, 1: Potential, 2: Clear access)"""
        # Simple heuristic - in real implementation, this would be more sophisticated
        trader_role = data.get('trader_info', {}).get('role', 'trader')
        insider_indicators = data.get('insider_indicators', [])
        
        if trader_role in ['executive', 'board_member'] or len(insider_indicators) > 2:
            return 2
        elif trader_role in ['senior_trader', 'analyst'] or len(insider_indicators) > 0:
            return 1
        return 0
    
    def _assess_trading_activity(self, data: Dict[str, Any]) -> int:
        """Assess trading activity unusualness (0: Normal, 1: Unusual, 2: Highly unusual)"""
        trades = data.get('trades', [])
        if not trades:
            return 0
        
        avg_volume = np.mean([trade.get('volume', 0) for trade in trades])
        historical_avg = data.get('historical_metrics', {}).get('avg_volume', avg_volume)
        
        if avg_volume > historical_avg * 5:
            return 2
        elif avg_volume > historical_avg * 2:
            return 1
        return 0
    
    def _assess_timing(self, data: Dict[str, Any]) -> int:
        """Assess timing relative to material events (0: Normal, 1: Suspicious, 2: Highly suspicious)"""
        material_events = data.get('material_events', [])
        trades = data.get('trades', [])
        
        if not material_events or not trades:
            return 0
        
        # Simple timing assessment - check if trades occurred shortly before announcements
        suspicious_timing_count = 0
        for event in material_events:
            event_time_str = event.get('timestamp')
            for trade in trades:
                trade_time_str = trade.get('timestamp')
                # If trade occurred 1-7 days before material event
                if event_time_str and trade_time_str:
                    try:
                        # Convert string timestamps to datetime objects
                        from datetime import datetime
                        event_time = datetime.fromisoformat(event_time_str.replace('Z', '+00:00'))
                        trade_time = datetime.fromisoformat(trade_time_str.replace('Z', '+00:00'))
                        time_diff = (event_time - trade_time).total_seconds() / (24 * 3600)  # days
                        if 1 <= time_diff <= 7:
                            suspicious_timing_count += 1
                    except (ValueError, TypeError):
                        # If timestamp parsing fails, skip this comparison
                        continue
        
        if suspicious_timing_count > 3:
            return 2
        elif suspicious_timing_count > 0:
            return 1
        return 0
    
    def _assess_price_impact(self, data: Dict[str, Any]) -> int:
        """Assess price impact of trades (0: Low, 1: Medium, 2: High)"""
        price_impact = data.get('metrics', {}).get('price_impact', 0)
        
        if price_impact > 0.05:  # 5% impact
            return 2
        elif price_impact > 0.02:  # 2% impact
            return 1
        return 0
    
    def _assess_order_pattern(self, data: Dict[str, Any]) -> int:
        """Assess order pattern for spoofing (0: Normal, 1: Layered, 2: Excessive layering)"""
        orders = data.get('orders', [])
        if not orders:
            return 0
        
        # Simple pattern detection
        large_orders = [o for o in orders if o.get('size', 0) > 10000]
        cancelled_orders = [o for o in orders if o.get('status') == 'cancelled']
        
        layering_ratio = len(cancelled_orders) / len(orders) if orders else 0
        
        if layering_ratio > 0.8 and len(large_orders) > 10:
            return 2
        elif layering_ratio > 0.5:
            return 1
        return 0
    
    def _assess_cancellation_rate(self, data: Dict[str, Any]) -> int:
        """Assess order cancellation rate (0: Low, 1: Medium, 2: High)"""
        orders = data.get('orders', [])
        if not orders:
            return 0
        
        cancelled_count = len([o for o in orders if o.get('status') == 'cancelled'])
        cancellation_rate = cancelled_count / len(orders)
        
        if cancellation_rate > 0.8:
            return 2
        elif cancellation_rate > 0.5:
            return 1
        return 0
    
    def _assess_price_movement(self, data: Dict[str, Any]) -> int:
        """Assess price movement (0: Minimal, 1: Moderate, 2: Significant)"""
        price_movement = data.get('metrics', {}).get('price_movement', 0)
        
        if price_movement > 0.03:  # 3% movement
            return 2
        elif price_movement > 0.01:  # 1% movement
            return 1
        return 0
    
    def _assess_volume_ratio(self, data: Dict[str, Any]) -> int:
        """Assess volume imbalance (0: Normal, 1: Imbalanced, 2: Highly imbalanced)"""
        volume_imbalance = data.get('metrics', {}).get('volume_imbalance', 0)
        
        if volume_imbalance > 0.7:
            return 2
        elif volume_imbalance > 0.4:
            return 1
        return 0
    
    def get_models_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'models_loaded': self.models_loaded,
            'insider_dealing_model': {
                'nodes': list(self.insider_dealing_model.nodes()) if self.insider_dealing_model else [],
                'edges': list(self.insider_dealing_model.edges()) if self.insider_dealing_model else []
            },
            'spoofing_model': {
                'nodes': list(self.spoofing_model.nodes()) if self.spoofing_model else [],
                'edges': list(self.spoofing_model.edges()) if self.spoofing_model else []
            }
        }