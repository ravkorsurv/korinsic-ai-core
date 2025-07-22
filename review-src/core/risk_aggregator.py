"""
Complex Risk Aggregator for Kor.ai Bayesian Risk Engine
Computes overall risk scores from multiple evidence nodes and implements configurable multi-node triggers.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class NodeConfig:
    """Configuration for a risk node"""

    name: str
    weight: float = 1.0
    high_threshold: int = 2  # State index considered "high"
    critical_threshold: int = 2  # State index considered "critical"
    description: str = ""


@dataclass
class AggregationConfig:
    """Configuration for risk aggregation"""

    base_weight: float = 1.0
    multi_node_threshold: int = 2  # Number of high nodes to trigger alert
    critical_node_threshold: int = 1  # Number of critical nodes to trigger alert
    exponential_penalty: float = 1.5  # Penalty multiplier for multiple high nodes
    pnl_loss_multiplier: float = 2.0  # Extra weight for PnL losses


class ComplexRiskAggregator:
    """
    Complex risk aggregation system that considers multiple evidence nodes
    and implements configurable multi-node triggers.
    """

    def __init__(self, config: Optional[AggregationConfig] = None):
        self.config = config or AggregationConfig()
        self.node_configs = self._initialize_node_configs()

    def _initialize_node_configs(self) -> Dict[str, NodeConfig]:
        """Initialize default node configurations"""
        return {
            "mnpi_access": NodeConfig(
                name="mnpi_access",
                weight=3.0,  # High weight for MNPI access
                high_threshold=1,  # potential_access or higher
                critical_threshold=2,  # clear_access
                description="Access to Material Nonpublic Information",
            ),
            "pnl_loss_spike": NodeConfig(
                name="pnl_loss_spike",
                weight=2.5,  # High weight for PnL losses
                high_threshold=1,  # small_loss or higher
                critical_threshold=2,  # large_loss
                description="Recent PnL spike resulting in loss",
            ),
            "trade_direction": NodeConfig(
                name="trade_direction",
                weight=2.0,  # Medium-high weight for contrarian trades
                high_threshold=2,  # contrarian
                critical_threshold=2,  # contrarian
                description="Trade direction relative to market",
            ),
            "risk_profile": NodeConfig(
                name="risk_profile",
                weight=2.0,  # Medium-high weight for known risk
                high_threshold=1,  # medium_risk or higher
                critical_threshold=2,  # high_risk
                description="Known risk profile from HR/historical data",
            ),
            "timing_proximity": NodeConfig(
                name="timing_proximity",
                weight=1.5,  # Medium weight for timing
                high_threshold=1,  # suspicious or higher
                critical_threshold=2,  # highly_suspicious
                description="Timing proximity to material events",
            ),
            "comms_intent": NodeConfig(
                name="comms_intent",
                weight=1.5,  # Medium weight for communications
                high_threshold=1,  # suspicious or higher
                critical_threshold=2,  # malicious
                description="Communication intent analysis",
            ),
            "trade_pattern": NodeConfig(
                name="trade_pattern",
                weight=1.0,  # Standard weight
                high_threshold=1,  # suspicious
                critical_threshold=1,  # suspicious
                description="Unusual trading patterns",
            ),
            "sales_activity": NodeConfig(
                name="sales_activity",
                weight=1.0,  # Standard weight
                high_threshold=1,  # unusual or higher
                critical_threshold=2,  # highly_unusual
                description="Unusual sales/client activity",
            ),
            "pnl_drift": NodeConfig(
                name="pnl_drift",
                weight=1.0,  # Standard weight
                high_threshold=1,  # anomalous
                critical_threshold=1,  # anomalous
                description="PnL drift anomalies",
            ),
            "market_news_context": NodeConfig(
                name="market_news_context",
                weight=1.5,  # Medium-high weight for news context
                high_threshold=1,  # partially_explained or higher
                critical_threshold=2,  # unexplained_move
                description="Market news contextualization (explained move suppressor)",
            ),
        }

    def compute_overall_risk_score(
        self, evidence: Dict[str, int], bayesian_risk: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Compute complex overall risk score from multiple evidence nodes and Bayesian risk.

        Args:
            evidence: Dict of node_name -> state_index
            bayesian_risk: Dict with 'low_risk', 'medium_risk', 'high_risk' probabilities

        Returns:
            Dict with overall risk score, breakdown, and trigger information
        """
        # Calculate weighted node scores
        node_scores = {}
        total_weighted_score = 0.0
        total_weight = 0.0

        high_nodes = []
        critical_nodes = []

        for node_name, state_idx in evidence.items():
            if node_name not in self.node_configs:
                continue

            config = self.node_configs[node_name]

            # Normalize state index to 0-1 scale (assuming 3 states max)
            normalized_score = min(state_idx / 2.0, 1.0)

            # Apply node-specific weight
            weighted_score = normalized_score * config.weight

            # Apply PnL loss multiplier if applicable
            if node_name == "pnl_loss_spike" and state_idx > 0:
                weighted_score *= self.config.pnl_loss_multiplier

            node_scores[node_name] = {
                "state_index": state_idx,
                "normalized_score": normalized_score,
                "weighted_score": weighted_score,
                "weight": config.weight,
                "description": config.description,
            }

            total_weighted_score += weighted_score
            total_weight += config.weight

            # Track high and critical nodes
            if state_idx >= config.high_threshold:
                high_nodes.append(node_name)
            if state_idx >= config.critical_threshold:
                critical_nodes.append(node_name)

        # Calculate base overall score
        base_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

        # Apply exponential penalty for multiple high nodes
        if len(high_nodes) >= self.config.multi_node_threshold:
            penalty_multiplier = self.config.exponential_penalty ** (
                len(high_nodes) - self.config.multi_node_threshold + 1
            )
            base_score *= penalty_multiplier
            logger.info(
                f"Applied multi-node penalty: {penalty_multiplier:.2f}x for {len(high_nodes)} high nodes"
            )

        # Combine with Bayesian risk score
        bayesian_score = bayesian_risk.get("overall_score", 0.0)

        # Final overall score: 70% from evidence aggregation, 30% from Bayesian
        overall_score = (base_score * 0.7) + (bayesian_score * 0.3)

        # Determine risk level
        risk_level = self._determine_risk_level(
            overall_score, len(high_nodes), len(critical_nodes)
        )

        # Generate explanation
        explanation = self._generate_explanation(
            overall_score,
            base_score,
            bayesian_score,
            high_nodes,
            critical_nodes,
            node_scores,
        )

        return {
            "overall_score": min(overall_score, 1.0),  # Cap at 1.0
            "base_score": base_score,
            "bayesian_score": bayesian_score,
            "risk_level": risk_level,
            "high_nodes": high_nodes,
            "critical_nodes": critical_nodes,
            "node_scores": node_scores,
            "explanation": explanation,
            "triggers": {
                "multi_node_trigger": len(high_nodes)
                >= self.config.multi_node_threshold,
                "critical_node_trigger": len(critical_nodes)
                >= self.config.critical_node_threshold,
                "high_node_count": len(high_nodes),
                "critical_node_count": len(critical_nodes),
            },
        }

    def _determine_risk_level(
        self, overall_score: float, high_node_count: int, critical_node_count: int
    ) -> str:
        """Determine risk level based on score and node counts"""
        if critical_node_count >= self.config.critical_node_threshold:
            return "CRITICAL"
        elif high_node_count >= self.config.multi_node_threshold:
            return "HIGH"
        elif overall_score >= 0.7:
            return "HIGH"
        elif overall_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_explanation(
        self,
        overall_score: float,
        base_score: float,
        bayesian_score: float,
        high_nodes: List[str],
        critical_nodes: List[str],
        node_scores: Dict[str, Dict],
    ) -> str:
        """Generate human-readable explanation of the risk score"""
        explanation = f"Overall Risk Score: {overall_score:.3f}\n"
        explanation += f"Risk Level: {self._determine_risk_level(overall_score, len(high_nodes), len(critical_nodes))}\n\n"

        explanation += f"Score Breakdown:\n"
        explanation += f"  - Evidence Aggregation: {base_score:.3f}\n"
        explanation += f"  - Bayesian Inference: {bayesian_score:.3f}\n\n"

        if high_nodes:
            explanation += f"High-Risk Nodes ({len(high_nodes)}):\n"
            for node in high_nodes:
                score_info = node_scores[node]
                explanation += f"  - {score_info['description']}: State {score_info['state_index']} (Score: {score_info['weighted_score']:.2f})\n"

        if critical_nodes:
            explanation += f"\nCritical Nodes ({len(critical_nodes)}):\n"
            for node in critical_nodes:
                score_info = node_scores[node]
                explanation += f"  - {score_info['description']}: State {score_info['state_index']} (Score: {score_info['weighted_score']:.2f})\n"

        # Highlight top contributors
        top_contributors = sorted(
            node_scores.items(), key=lambda x: x[1]["weighted_score"], reverse=True
        )[:3]
        explanation += f"\nTop Risk Contributors:\n"
        for node_name, score_info in top_contributors:
            explanation += (
                f"  - {score_info['description']}: {score_info['weighted_score']:.2f}\n"
            )

        return explanation

    def update_node_config(self, node_name: str, **kwargs) -> bool:
        """Update configuration for a specific node"""
        if node_name not in self.node_configs:
            return False

        config = self.node_configs[node_name]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        logger.info(f"Updated config for node '{node_name}': {kwargs}")
        return True

    def get_node_configs(self) -> Dict[str, NodeConfig]:
        """Get current node configurations"""
        return self.node_configs.copy()
