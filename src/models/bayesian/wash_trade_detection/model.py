"""
Wash Trade Detection Bayesian Model.

This module provides the main Bayesian model for detecting wash trades
and signal distortion patterns as specified in KOR.AI Model Enhancement.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .config import WashTradeDetectionConfig
from .nodes import WashTradeDetectionNodes

# Add regulatory explainability import
from ....core.regulatory_explainability import (
    RegulatoryExplainabilityEngine,
    EvidenceItem,
    EvidenceType,
    RegulatoryFramework
)

logger = logging.getLogger(__name__)


class WashTradeDetectionModel:
    """
    Bayesian model for wash trade detection and signal distortion analysis.

    This model implements the KOR.AI Model Enhancement for detecting wash trades
    and signal distortion patterns using Bayesian inference with latent intent modeling.
    """

    def __init__(
        self, use_latent_intent: bool = True, config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the wash trade detection model.

        Args:
            use_latent_intent: Whether to use latent intent modeling
            config: Optional configuration dictionary
        """
        self.use_latent_intent = use_latent_intent
        self.config = WashTradeDetectionConfig(config)
        self.nodes = WashTradeDetectionNodes()
        
        # Initialize regulatory explainability engine
        self.explainability_engine = RegulatoryExplainabilityEngine(config or {})

        # Initialize latent intent model if enabled
        self.latent_intent_model = None
        if self.use_latent_intent:
            # TODO: Integrate with existing latent intent model
            pass

        # Model state
        self.is_trained = False
        self.model_version = self.config.get("model_version", "1.0.0")
        self.last_updated = datetime.now()

        # Performance metrics
        self.performance_metrics = {}

        logger.info(
            f"Wash trade detection model initialized (version: {self.model_version})"
        )

    def predict(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make predictions for wash trade detection.

        Args:
            evidence: Evidence data for prediction

        Returns:
            Prediction results including probabilities and risk scores
        """
        try:
            # Validate input evidence
            if not self._validate_evidence(evidence):
                raise ValueError("Invalid evidence provided")

            # Prepare evidence for inference
            processed_evidence = self._preprocess_evidence(evidence)

            # Core requirement nodes inference
            core_predictions = self._predict_core_requirements(processed_evidence)

            # Supporting evidence analysis
            supporting_predictions = self._predict_supporting_evidence(
                processed_evidence
            )

            # Signal distortion analysis
            signal_distortion_analysis = self._analyze_signal_distortion(
                processed_evidence
            )

            # Algo reaction sensitivity analysis
            algo_reaction_analysis = self._analyze_algo_reaction(processed_evidence)

            # Latent intent inference if enabled
            latent_intent_results = {}
            if self.use_latent_intent and self.latent_intent_model:
                latent_intent_results = self._infer_latent_intent(processed_evidence)

            # Risk factor calculation
            risk_factor_score = self._calculate_risk_factor(
                core_predictions, supporting_predictions, latent_intent_results
            )

            # Final wash trade detection
            final_prediction = self._make_final_prediction(
                core_predictions,
                supporting_predictions,
                signal_distortion_analysis,
                algo_reaction_analysis,
                latent_intent_results,
                risk_factor_score,
            )

            # Compile results
            results = {
                "timestamp": datetime.now().isoformat(),
                "model_version": self.model_version,
                "wash_trade_detected": final_prediction["wash_trade_detected"],
                "confidence_score": final_prediction["confidence_score"],
                "risk_score": risk_factor_score,
                "core_requirements": core_predictions,
                "supporting_evidence": supporting_predictions,
                "signal_distortion": signal_distortion_analysis,
                "algo_reaction": algo_reaction_analysis,
                "latent_intent": latent_intent_results,
                "explanation": self._generate_explanation(
                    final_prediction, core_predictions
                ),
            }

            logger.debug(f"Prediction completed: {results['wash_trade_detected']}")
            return results

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise

    def _predict_core_requirements(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict core requirement nodes from KOR.AI Model Enhancement.

        Args:
            evidence: Processed evidence data

        Returns:
            Core requirement predictions
        """
        core_predictions = {}

        # WashTradeLikelihood
        core_predictions["wash_trade_likelihood"] = self._predict_wash_trade_likelihood(
            evidence
        )

        # SignalDistortionIndex
        core_predictions["signal_distortion_index"] = (
            self._predict_signal_distortion_index(evidence)
        )

        # AlgoReactionSensitivity
        core_predictions["algo_reaction_sensitivity"] = (
            self._predict_algo_reaction_sensitivity(evidence)
        )

        # StrategyLegOverlap
        core_predictions["strategy_leg_overlap"] = self._predict_strategy_leg_overlap(
            evidence
        )

        # PriceImpactAnomaly
        core_predictions["price_impact_anomaly"] = self._predict_price_impact_anomaly(
            evidence
        )

        # ImpliedLiquidityConflict
        core_predictions["implied_liquidity_conflict"] = (
            self._predict_implied_liquidity_conflict(evidence)
        )

        return core_predictions

    def _predict_wash_trade_likelihood(
        self, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict wash trade likelihood based on detection logic.

        Args:
            evidence: Evidence data

        Returns:
            Wash trade likelihood prediction
        """
        # Counterparty and seller analysis
        counterparty_match = evidence.get("counterparty_entity_match", 0)
        algo_framework_match = evidence.get("algo_framework_match", 0)
        implied_strategy_execution = evidence.get("implied_strategy_execution", 0)

        # LEI match analysis
        lei_match_score = 0.0
        if "lei_exact_match" in evidence and evidence["lei_exact_match"]:
            lei_match_score = 1.0
        elif "lei_affiliate_match" in evidence and evidence["lei_affiliate_match"]:
            lei_match_score = 0.8

        # Time delta analysis
        time_delta_score = 0.0
        if "trade_time_delta" in evidence:
            time_delta = evidence["trade_time_delta"]
            if time_delta < 1:  # Same millisecond
                time_delta_score = 1.0
            elif time_delta < 100:  # Within 100ms
                time_delta_score = 0.8
            elif time_delta < 1000:  # Within 1 second
                time_delta_score = 0.5

        # Aggregate score
        likelihood_score = (
            lei_match_score * 0.4
            + counterparty_match * 0.3
            + algo_framework_match * 0.15
            + implied_strategy_execution * 0.1
            + time_delta_score * 0.05
        )

        # Convert to probability states
        if likelihood_score >= 0.7:
            state = "high_probability"
            probability = 0.85
        elif likelihood_score >= 0.4:
            state = "medium_probability"
            probability = 0.60
        else:
            state = "low_probability"
            probability = 0.20

        return {
            "state": state,
            "probability": probability,
            "likelihood_score": likelihood_score,
            "contributing_factors": {
                "lei_match": lei_match_score,
                "counterparty_match": counterparty_match,
                "algo_framework_match": algo_framework_match,
                "time_delta": time_delta_score,
            },
        }

    def _predict_signal_distortion_index(
        self, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict signal distortion index based on order book analysis.

        Args:
            evidence: Evidence data

        Returns:
            Signal distortion index prediction
        """
        # Order book impact analysis
        order_book_impact = evidence.get("order_book_impact", 0)
        quote_frequency_distortion = evidence.get("quote_frequency_distortion", 0)
        spread_manipulation = evidence.get("spread_manipulation", 0)

        # Volume at best bid/ask analysis
        volume_impact_score = 0.0
        if "volume_at_best_change" in evidence:
            volume_change = evidence["volume_at_best_change"]
            if abs(volume_change) > 0.5:  # Significant volume change
                volume_impact_score = min(abs(volume_change), 1.0)

        # Order book imbalance analysis
        imbalance_score = 0.0
        if "order_book_imbalance_change" in evidence:
            imbalance_change = evidence["order_book_imbalance_change"]
            if abs(imbalance_change) > 0.3:  # Significant imbalance change
                imbalance_score = min(abs(imbalance_change), 1.0)

        # Quote frequency analysis (flickering)
        flickering_score = 0.0
        if "quote_frequency_ratio" in evidence:
            freq_ratio = evidence["quote_frequency_ratio"]
            if freq_ratio > 2.0:  # Quote frequency doubled
                flickering_score = min(freq_ratio / 5.0, 1.0)

        # Aggregate distortion score
        distortion_score = (
            order_book_impact * 0.25
            + quote_frequency_distortion * 0.25
            + spread_manipulation * 0.20
            + volume_impact_score * 0.15
            + imbalance_score * 0.10
            + flickering_score * 0.05
        )

        # Convert to distortion states
        if distortion_score >= 0.6:
            state = "high_distortion"
            probability = 0.80
        elif distortion_score >= 0.3:
            state = "moderate_distortion"
            probability = 0.55
        else:
            state = "minimal_distortion"
            probability = 0.25

        return {
            "state": state,
            "probability": probability,
            "distortion_score": distortion_score,
            "affected_dimensions": {
                "volume_impact": volume_impact_score,
                "imbalance_impact": imbalance_score,
                "quote_flickering": flickering_score,
            },
        }

    def _predict_algo_reaction_sensitivity(
        self, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict algorithmic reaction sensitivity.

        Args:
            evidence: Evidence data

        Returns:
            Algo reaction sensitivity prediction
        """
        # Order flow clustering analysis
        order_flow_clustering = evidence.get("order_flow_clustering", 0)
        reaction_time_delta = evidence.get("reaction_time_delta", 0)
        passive_aggressive_ratio = evidence.get("passive_aggressive_ratio", 0)

        # Reaction time analysis (<100ms indicates high sensitivity)
        reaction_score = 0.0
        if "algo_reaction_time_ms" in evidence:
            reaction_time = evidence["algo_reaction_time_ms"]
            if reaction_time < 50:  # Ultra-fast reaction
                reaction_score = 1.0
            elif reaction_time < 100:  # Fast reaction
                reaction_score = 0.8
            elif reaction_time < 500:  # Moderate reaction
                reaction_score = 0.4

        # Order clustering after trade
        clustering_score = 0.0
        if "order_clustering_ratio" in evidence:
            clustering_ratio = evidence["order_clustering_ratio"]
            if clustering_ratio > 0.7:  # High clustering
                clustering_score = min(clustering_ratio, 1.0)

        # Passive/aggressive quoting changes
        quoting_score = 0.0
        if "passive_aggressive_change" in evidence:
            pa_change = evidence["passive_aggressive_change"]
            if abs(pa_change) > 0.3:  # Significant change in quoting behavior
                quoting_score = min(abs(pa_change), 1.0)

        # Aggregate sensitivity score
        sensitivity_score = (
            order_flow_clustering * 0.30
            + reaction_time_delta * 0.25
            + passive_aggressive_ratio * 0.20
            + reaction_score * 0.15
            + clustering_score * 0.10
        )

        # Convert to sensitivity states
        if sensitivity_score >= 0.65:
            state = "high_sensitivity"
            probability = 0.75
        elif sensitivity_score >= 0.35:
            state = "medium_sensitivity"
            probability = 0.50
        else:
            state = "low_sensitivity"
            probability = 0.25

        return {
            "state": state,
            "probability": probability,
            "sensitivity_score": sensitivity_score,
            "reaction_factors": {
                "reaction_time": reaction_score,
                "order_clustering": clustering_score,
                "quoting_behavior": quoting_score,
            },
        }

    def _predict_strategy_leg_overlap(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict strategy leg overlap for commodity derivatives.

        Args:
            evidence: Evidence data

        Returns:
            Strategy leg overlap prediction
        """
        # Commodity leg matching analysis
        commodity_leg_matching = evidence.get("commodity_leg_matching", 0)
        third_party_risk_validation = evidence.get("third_party_risk_validation", 0)

        # Time spread analysis
        time_spread_score = 0.0
        if "time_spread_detected" in evidence and evidence["time_spread_detected"]:
            time_spread_score = 0.8

        # Cross-contract matching
        cross_contract_score = 0.0
        if "cross_contract_matching" in evidence:
            cross_contract_score = evidence["cross_contract_matching"]

        # Same entity leg matching
        same_entity_score = 0.0
        if "same_entity_legs" in evidence:
            same_entity_legs = evidence["same_entity_legs"]
            if same_entity_legs > 0.5:  # More than 50% legs from same entity
                same_entity_score = same_entity_legs

        # Aggregate overlap score
        overlap_score = (
            commodity_leg_matching * 0.35
            + third_party_risk_validation * 0.25
            + time_spread_score * 0.20
            + cross_contract_score * 0.15
            + same_entity_score * 0.05
        )

        # Convert to overlap states
        if overlap_score >= 0.7:
            state = "full_overlap"
            probability = 0.85
        elif overlap_score >= 0.4:
            state = "partial_overlap"
            probability = 0.60
        else:
            state = "no_overlap"
            probability = 0.15

        return {
            "state": state,
            "probability": probability,
            "overlap_score": overlap_score,
            "strategy_analysis": {
                "time_spread": time_spread_score,
                "cross_contract": cross_contract_score,
                "same_entity": same_entity_score,
            },
        }

    def _predict_price_impact_anomaly(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict price impact anomaly.

        Args:
            evidence: Evidence data

        Returns:
            Price impact anomaly prediction
        """
        # Mean reversion analysis
        mean_reversion_pattern = evidence.get("mean_reversion_pattern", 0)
        price_spike_fade = evidence.get("price_spike_fade", 0)
        volatility_baseline_deviation = evidence.get("volatility_baseline_deviation", 0)

        # Immediate mean reversion (within 10-30 seconds)
        reversion_score = 0.0
        if "immediate_reversion" in evidence:
            reversion_time = evidence["immediate_reversion"]
            if reversion_time < 10:  # Immediate reversion
                reversion_score = 1.0
            elif reversion_time < 30:  # Quick reversion
                reversion_score = 0.7

        # Price spike/fade analysis
        spike_fade_score = 0.0
        if "price_spike_magnitude" in evidence:
            spike_magnitude = evidence["price_spike_magnitude"]
            if spike_magnitude > 0.02:  # >2% spike
                spike_fade_score = min(spike_magnitude / 0.05, 1.0)

        # Volatility baseline comparison
        volatility_score = 0.0
        if "volatility_z_score" in evidence:
            z_score = evidence["volatility_z_score"]
            if abs(z_score) > 3.0:  # Extreme deviation
                volatility_score = min(abs(z_score) / 5.0, 1.0)

        # Aggregate anomaly score
        anomaly_score = (
            mean_reversion_pattern * 0.35
            + price_spike_fade * 0.30
            + volatility_baseline_deviation * 0.20
            + reversion_score * 0.10
            + spike_fade_score * 0.05
        )

        # Convert to anomaly states
        if anomaly_score >= 0.7:
            state = "anomalous_impact"
            probability = 0.80
        elif anomaly_score >= 0.4:
            state = "unusual_impact"
            probability = 0.55
        else:
            state = "normal_impact"
            probability = 0.25

        return {
            "state": state,
            "probability": probability,
            "anomaly_score": anomaly_score,
            "price_factors": {
                "reversion_speed": reversion_score,
                "spike_magnitude": spike_fade_score,
                "volatility_deviation": volatility_score,
            },
        }

    def _predict_implied_liquidity_conflict(
        self, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict implied liquidity conflict.

        Args:
            evidence: Evidence data

        Returns:
            Implied liquidity conflict prediction
        """
        # Venue implied matching analysis
        venue_implied_matching = evidence.get("venue_implied_matching", 0)
        leg_execution_source = evidence.get("leg_execution_source", 0)

        # Implied matching facility usage
        implied_matching_score = 0.0
        if (
            "implied_matching_detected" in evidence
            and evidence["implied_matching_detected"]
        ):
            implied_matching_score = 0.8

        # Internal book vs external execution
        internal_execution_score = 0.0
        if "internal_execution_ratio" in evidence:
            internal_ratio = evidence["internal_execution_ratio"]
            if internal_ratio > 0.7:  # High internal execution
                internal_execution_score = internal_ratio

        # Strategy order matching
        strategy_matching_score = 0.0
        if "strategy_order_matching" in evidence:
            strategy_matching_score = evidence["strategy_order_matching"]

        # Artificial interaction detection
        artificial_interaction_score = 0.0
        if "artificial_interaction_detected" in evidence:
            artificial_interaction_score = evidence["artificial_interaction_detected"]

        # Aggregate conflict score
        conflict_score = (
            venue_implied_matching * 0.30
            + leg_execution_source * 0.25
            + implied_matching_score * 0.20
            + internal_execution_score * 0.15
            + strategy_matching_score * 0.10
        )

        # Convert to conflict states
        if conflict_score >= 0.75:
            state = "clear_conflict"
            probability = 0.85
        elif conflict_score >= 0.4:
            state = "potential_conflict"
            probability = 0.60
        else:
            state = "no_conflict"
            probability = 0.20

        return {
            "state": state,
            "probability": probability,
            "conflict_score": conflict_score,
            "liquidity_factors": {
                "implied_matching": implied_matching_score,
                "internal_execution": internal_execution_score,
                "strategy_matching": strategy_matching_score,
            },
        }

    def _predict_supporting_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict supporting evidence nodes.

        Args:
            evidence: Evidence data

        Returns:
            Supporting evidence predictions
        """
        supporting_predictions = {}

        # Get supporting evidence nodes
        supporting_nodes = self.nodes.get_supporting_evidence_nodes()

        for node_name in supporting_nodes:
            if node_name in evidence:
                node_value = evidence[node_name]
                supporting_predictions[node_name] = {
                    "value": node_value,
                    "confidence": min(node_value + 0.1, 1.0),
                }

        return supporting_predictions

    def _analyze_signal_distortion(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze signal distortion patterns.

        Args:
            evidence: Evidence data

        Returns:
            Signal distortion analysis
        """
        distortion_analysis = {
            "pre_trade_snapshot": evidence.get("pre_trade_orderbook", {}),
            "post_trade_snapshot": evidence.get("post_trade_orderbook", {}),
            "distortion_detected": False,
            "distortion_magnitude": 0.0,
            "affected_levels": [],
        }

        # Compare pre/post trade snapshots
        if (
            distortion_analysis["pre_trade_snapshot"]
            and distortion_analysis["post_trade_snapshot"]
        ):
            distortion_analysis["distortion_detected"] = True
            distortion_analysis["distortion_magnitude"] = 0.6  # Placeholder calculation

        return distortion_analysis

    def _analyze_algo_reaction(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze algorithmic reaction patterns.

        Args:
            evidence: Evidence data

        Returns:
            Algorithmic reaction analysis
        """
        reaction_analysis = {
            "reaction_detected": False,
            "reaction_time_ms": evidence.get("algo_reaction_time_ms", 0),
            "reaction_magnitude": 0.0,
            "algorithms_affected": [],
        }

        # Check for sub-100ms reactions
        if reaction_analysis["reaction_time_ms"] < 100:
            reaction_analysis["reaction_detected"] = True
            reaction_analysis["reaction_magnitude"] = 0.8

        return reaction_analysis

    def _infer_latent_intent(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infer latent intent using the latent intent model.

        Args:
            evidence: Evidence data

        Returns:
            Latent intent inference results
        """
        if not self.latent_intent_model:
            # Return simplified intent inference without latent intent model
            wash_trade_score = evidence.get("wash_trade_likelihood", 0)
            signal_distortion_score = evidence.get("signal_distortion_index", 0)

            # Simple intent calculation based on evidence scores
            wash_trade_intent = min(wash_trade_score * 0.8, 1.0)
            signal_distortion_intent = min(signal_distortion_score * 0.8, 1.0)
            intent_confidence = (wash_trade_intent + signal_distortion_intent) / 2

            return {
                "wash_trade_intent": wash_trade_intent,
                "signal_distortion_intent": signal_distortion_intent,
                "intent_confidence": intent_confidence,
            }

        # TODO: Integrate with existing latent intent model when available
        return {
            "wash_trade_intent": 0,
            "signal_distortion_intent": 0,
            "intent_confidence": 0,
        }

    def _calculate_risk_factor(
        self,
        core_predictions: Dict[str, Any],
        supporting_predictions: Dict[str, Any],
        latent_intent_results: Dict[str, Any],
    ) -> float:
        """
        Calculate overall risk factor score.

        Args:
            core_predictions: Core requirement predictions
            supporting_predictions: Supporting evidence predictions
            latent_intent_results: Latent intent results

        Returns:
            Risk factor score (0-1)
        """
        # Get risk factor weights
        weights = self.config.get_risk_factor_weights()

        # Calculate weighted score
        risk_score = 0.0

        for node_name, weight in weights.items():
            if node_name in core_predictions:
                node_probability = core_predictions[node_name]["probability"]
                risk_score += weight * node_probability

        # Add latent intent contribution
        if latent_intent_results:
            intent_score = latent_intent_results.get("intent_confidence", 0)
            risk_score += 0.1 * intent_score  # 10% contribution from latent intent

        return min(risk_score, 1.0)

    def _make_final_prediction(
        self,
        core_predictions: Dict[str, Any],
        supporting_predictions: Dict[str, Any],
        signal_distortion_analysis: Dict[str, Any],
        algo_reaction_analysis: Dict[str, Any],
        latent_intent_results: Dict[str, Any],
        risk_factor_score: float,
    ) -> Dict[str, Any]:
        """
        Make final wash trade detection prediction.

        Args:
            core_predictions: Core requirement predictions
            supporting_predictions: Supporting evidence predictions
            signal_distortion_analysis: Signal distortion analysis
            algo_reaction_analysis: Algo reaction analysis
            latent_intent_results: Latent intent results
            risk_factor_score: Risk factor score

        Returns:
            Final prediction
        """
        # Get detection threshold
        threshold = self.config.get("wash_trade_probability_threshold", 0.7)

        # Check if wash trade is detected
        wash_trade_detected = risk_factor_score >= threshold

        # Calculate confidence score
        confidence_score = risk_factor_score

        # High-risk flag for multiple simultaneous triggers
        high_risk_triggers = 0
        for prediction in core_predictions.values():
            if prediction["probability"] > 0.6:
                high_risk_triggers += 1

        high_risk_flag = high_risk_triggers >= 3

        return {
            "wash_trade_detected": wash_trade_detected,
            "confidence_score": confidence_score,
            "high_risk_flag": high_risk_flag,
            "triggered_nodes": high_risk_triggers,
            "threshold_used": threshold,
        }

    def _generate_explanation(
        self, final_prediction: Dict[str, Any], core_predictions: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for the prediction.

        Args:
            final_prediction: Final prediction results
            core_predictions: Core predictions

        Returns:
            Explanation string
        """
        if final_prediction["wash_trade_detected"]:
            explanation = f"Wash trade detected with {final_prediction['confidence_score']:.2%} confidence. "
            explanation += f"Key indicators: "

            high_indicators = []
            for node_name, prediction in core_predictions.items():
                if prediction["probability"] > 0.6:
                    high_indicators.append(node_name.replace("_", " ").title())

            explanation += ", ".join(high_indicators)
        else:
            explanation = "No wash trade detected. Risk factors below threshold."

        return explanation

    def _validate_evidence(self, evidence: Dict[str, Any]) -> bool:
        """
        Validate input evidence.

        Args:
            evidence: Evidence to validate

        Returns:
            True if valid, False otherwise
        """
        # Check for required fields
        required_fields = ["trade_id", "timestamp"]
        for field in required_fields:
            if field not in evidence:
                logger.error(f"Missing required field: {field}")
                return False

        return True

    def _preprocess_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess evidence for inference.

        Args:
            evidence: Raw evidence data

        Returns:
            Processed evidence data
        """
        # Normalize numeric values
        processed = evidence.copy()

        # Add computed fields
        processed["processing_timestamp"] = datetime.now().isoformat()

        return processed

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.

        Returns:
            Model information dictionary
        """
        return {
            "model_name": "wash_trade_detection",
            "model_version": self.model_version,
            "use_latent_intent": self.use_latent_intent,
            "is_trained": self.is_trained,
            "last_updated": self.last_updated.isoformat(),
            "core_nodes": self.nodes.get_core_requirement_nodes(),
            "supporting_nodes": self.nodes.get_supporting_evidence_nodes(),
            "performance_metrics": self.performance_metrics,
        }

    def __str__(self) -> str:
        """String representation of the model."""
        return f"WashTradeDetectionModel(version={self.model_version}, latent_intent={self.use_latent_intent})"

    def __repr__(self) -> str:
        """Detailed string representation of the model."""
        return f"WashTradeDetectionModel({self.get_model_info()})"
    
    def generate_regulatory_explanation(
        self, 
        evidence: Dict[str, Any], 
        inference_result: Dict[str, float],
        account_id: str,
        timestamp: str
    ) -> List[EvidenceItem]:
        """
        Generate regulatory explainability evidence for wash trade detection.
        
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
                    description=f"Wash Trade Detection indicator: {evidence_key} = {evidence_value:.2f}",
                    strength=min(float(evidence_value), 1.0),
                    reliability=0.85,
                    regulatory_relevance={
                        RegulatoryFramework.MAR_ARTICLE_12: 0.9,
                        RegulatoryFramework.STOR_REQUIREMENTS: 0.8
                    },
                    raw_data={
                        'model_type': 'wash_trade_detection',
                        'evidence_node': evidence_key,
                        'score': evidence_value,
                        'inference_result': inference_result
                    }
                ))
        
        return evidence_items
    
    def get_regulatory_framework_mapping(self) -> Dict[RegulatoryFramework, Dict[str, Any]]:
        """
        Get regulatory framework mapping for wash trade detection.
        
        Returns:
            Dictionary mapping regulatory frameworks to their requirements
        """
        return {
            RegulatoryFramework.MAR_ARTICLE_12: {
                "description": "Wash Trade Detection detection and analysis",
                "key_indicators": [
                    'Wash trade patterns',
                    'Signal distortion activities',
                    'Artificial volume creation'
                ],
                "evidence_threshold": 0.7,
                "reporting_requirements": "Detailed pattern analysis required"
            },
            RegulatoryFramework.STOR_REQUIREMENTS: {
                "description": "Suspicious transaction reporting for wash trade detection behavior",
                "key_indicators": [
                    'Wash trade patterns',
                    'Signal distortion activities'
                ],
                "evidence_threshold": 0.6,
                "reporting_requirements": "Transaction-level details required"
            }
        }
