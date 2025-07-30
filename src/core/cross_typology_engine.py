"""
Cross-Typology Signal Sharing Engine

This engine implements cross-typology awareness by sharing risk signals between
different risk typologies at the person level. It enables sophisticated risk
clustering and escalating monitoring based on correlated suspicious behavior
across multiple risk categories.

Features:
- Signal propagation between risk typologies
- Dynamic prior adjustment based on cross-signals
- Risk correlation analysis
- Escalation factor calculation
- Evidence sharing and reinforcement
"""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from src.models.person_centric import (
    RiskTypology, 
    CrossTypologySignal, 
    PersonRiskProfile,
    PersonCentricEvidence,
    SignalDirection
)
from .person_centric_nodes import PersonRiskNode

logger = logging.getLogger(__name__)


class CrossTypologyEngine:
    """
    Engine for managing cross-typology signal sharing and risk correlation
    """
    
    def __init__(self):
        # Signal storage and management
        self.active_signals: Dict[str, List[CrossTypologySignal]] = defaultdict(list)
        self.signal_history: List[CrossTypologySignal] = []
        self.person_risk_nodes: Dict[str, Dict[RiskTypology, PersonRiskNode]] = defaultdict(dict)
        
        # Configuration for cross-typology relationships
        self.typology_correlations = self._initialize_typology_correlations()
        self.signal_weights = self._initialize_signal_weights()
        self.escalation_thresholds = self._initialize_escalation_thresholds()
        
        # Signal decay parameters
        self.signal_decay_hours = 48  # Signals decay over 48 hours
        self.min_signal_strength = 0.1  # Minimum strength to maintain signal
        
    def _initialize_typology_correlations(self) -> Dict[Tuple[RiskTypology, RiskTypology], float]:
        """Initialize correlation strengths between risk typologies"""
        correlations = {}
        
        # Define known correlations between risk typologies
        # Higher values indicate stronger correlations
        
        # Insider dealing correlations
        correlations[(RiskTypology.INSIDER_DEALING, RiskTypology.FRONT_RUNNING)] = 0.7
        correlations[(RiskTypology.INSIDER_DEALING, RiskTypology.MARKET_MANIPULATION)] = 0.6
        correlations[(RiskTypology.INSIDER_DEALING, RiskTypology.WASH_TRADING)] = 0.4
        
        # Spoofing correlations
        correlations[(RiskTypology.SPOOFING, RiskTypology.MARKET_MANIPULATION)] = 0.8
        correlations[(RiskTypology.SPOOFING, RiskTypology.WASH_TRADING)] = 0.6
        correlations[(RiskTypology.SPOOFING, RiskTypology.FRONT_RUNNING)] = 0.5
        
        # Wash trading correlations
        correlations[(RiskTypology.WASH_TRADING, RiskTypology.MARKET_MANIPULATION)] = 0.7
        correlations[(RiskTypology.WASH_TRADING, RiskTypology.FRONT_RUNNING)] = 0.5
        
        # Front running correlations
        correlations[(RiskTypology.FRONT_RUNNING, RiskTypology.MARKET_MANIPULATION)] = 0.6
        
        # Cross-desk collusion has moderate correlation with all others
        for typology in [RiskTypology.INSIDER_DEALING, RiskTypology.SPOOFING, 
                        RiskTypology.WASH_TRADING, RiskTypology.FRONT_RUNNING,
                        RiskTypology.MARKET_MANIPULATION]:
            correlations[(RiskTypology.CROSS_DESK_COLLUSION, typology)] = 0.5
            correlations[(typology, RiskTypology.CROSS_DESK_COLLUSION)] = 0.5
        
        # Make correlations symmetric
        symmetric_correlations = {}
        for (t1, t2), strength in correlations.items():
            symmetric_correlations[(t1, t2)] = strength
            symmetric_correlations[(t2, t1)] = strength
            
        return symmetric_correlations
    
    def _initialize_signal_weights(self) -> Dict[RiskTypology, float]:
        """Initialize weights for different typologies as signal sources"""
        return {
            RiskTypology.INSIDER_DEALING: 0.9,  # High weight - strong predictor
            RiskTypology.SPOOFING: 0.8,
            RiskTypology.MARKET_MANIPULATION: 0.8,
            RiskTypology.FRONT_RUNNING: 0.7,
            RiskTypology.WASH_TRADING: 0.6,
            RiskTypology.CROSS_DESK_COLLUSION: 0.7
        }
    
    def _initialize_escalation_thresholds(self) -> Dict[str, float]:
        """Initialize thresholds for escalation decisions"""
        return {
            "cross_signal_strength": 0.6,  # Minimum strength for cross-typology signal
            "escalation_threshold": 0.7,   # Threshold for escalation
            "high_risk_threshold": 0.8,    # Threshold for high-risk classification
            "multiple_typology_bonus": 0.2  # Bonus for multiple typology involvement
        }
    
    def register_person_risk_node(self, person_id: str, typology: RiskTypology, risk_node: PersonRiskNode):
        """Register a person's risk node for cross-typology analysis"""
        self.person_risk_nodes[person_id][typology] = risk_node
        logger.info(f"Registered risk node for person {person_id}, typology {typology.value}")
    
    def analyze_cross_typology_signals(self, person_id: str) -> List[CrossTypologySignal]:
        """
        Analyze and generate cross-typology signals for a person
        
        Args:
            person_id: The person to analyze
            
        Returns:
            List of generated cross-typology signals
        """
        if person_id not in self.person_risk_nodes:
            logger.warning(f"No risk nodes found for person {person_id}")
            return []
        
        person_nodes = self.person_risk_nodes[person_id]
        generated_signals = []
        
        # Calculate risk probabilities for all typologies
        typology_risks = {}
        for typology, risk_node in person_nodes.items():
            risk_prob, _ = risk_node.calculate_risk_probability()
            typology_risks[typology] = risk_prob
        
        # Generate signals between typologies
        for source_typology, source_risk in typology_risks.items():
            if source_risk < self.escalation_thresholds["cross_signal_strength"]:
                continue  # Skip low-risk sources
                
            for target_typology in typology_risks.keys():
                if source_typology == target_typology:
                    continue
                    
                # Calculate signal strength based on correlation and source risk
                signal = self._calculate_cross_typology_signal(
                    person_id, source_typology, target_typology, source_risk
                )
                
                if signal and signal.signal_strength >= self.min_signal_strength:
                    generated_signals.append(signal)
                    
        # Store and apply signals
        self.active_signals[person_id].extend(generated_signals)
        self._apply_signals_to_nodes(person_id, generated_signals)
        
        logger.info(f"Generated {len(generated_signals)} cross-typology signals for person {person_id}")
        return generated_signals
    
    def _calculate_cross_typology_signal(
        self, 
        person_id: str, 
        source_typology: RiskTypology, 
        target_typology: RiskTypology,
        source_risk: float
    ) -> Optional[CrossTypologySignal]:
        """Calculate cross-typology signal strength and direction"""
        
        # Get correlation strength between typologies
        correlation_key = (source_typology, target_typology)
        base_correlation = self.typology_correlations.get(correlation_key, 0.0)
        
        if base_correlation < 0.1:  # Too weak to generate signal
            return None
        
        # Calculate signal strength
        source_weight = self.signal_weights.get(source_typology, 0.5)
        signal_strength = source_risk * base_correlation * source_weight
        
        # Determine signal direction
                    signal_direction = SignalDirection.POSITIVE if signal_strength > 0 else SignalDirection.NEUTRAL
        
        # Calculate impact on target typology's prior
        impact_on_prior = signal_strength * 0.3  # Max 30% impact on prior
        
        # Get shared evidence
        shared_evidence = self._identify_shared_evidence(person_id, source_typology, target_typology)
        
        # Calculate correlation factors
        correlation_factors = self._calculate_correlation_factors(
            person_id, source_typology, target_typology
        )
        
        return CrossTypologySignal(
            person_id=person_id,
            source_typology=source_typology,
            target_typology=target_typology,
            signal_strength=signal_strength,
            signal_direction=signal_direction,
            shared_evidence=shared_evidence,
            correlation_factors=correlation_factors,
            impact_on_prior=impact_on_prior,
            confidence_adjustment=signal_strength * 0.1  # Small confidence boost
        )
    
    def _identify_shared_evidence(
        self, 
        person_id: str, 
        source_typology: RiskTypology, 
        target_typology: RiskTypology
    ) -> List[str]:
        """Identify evidence that supports both typologies"""
        
        shared_evidence = []
        
        # Get risk nodes for both typologies
        source_node = self.person_risk_nodes[person_id].get(source_typology)
        target_node = self.person_risk_nodes[person_id].get(target_typology)
        
        if not source_node or not target_node:
            return shared_evidence
        
        # Check for shared evidence patterns
        source_evidence = source_node.evidence_nodes
        target_evidence = target_node.evidence_nodes
        
        # Look for overlapping evidence types with high strength
        for evidence_type in source_evidence.keys():
            if evidence_type in target_evidence:
                source_summary = source_evidence[evidence_type].get_evidence_summary()
                target_summary = target_evidence[evidence_type].get_evidence_summary()
                
                # If both show suspicious activity in same evidence type
                if (source_summary["aggregated_state"] > 0 and 
                    target_summary["aggregated_state"] > 0):
                    shared_evidence.append(f"{evidence_type}_correlation")
        
        # Add specific patterns based on typology combinations
        if source_typology == RiskTypology.INSIDER_DEALING and target_typology == RiskTypology.FRONT_RUNNING:
            shared_evidence.extend(["timing_correlation", "information_advantage"])
        elif source_typology == RiskTypology.SPOOFING and target_typology == RiskTypology.MARKET_MANIPULATION:
            shared_evidence.extend(["price_impact_correlation", "order_pattern_similarity"])
        
        return shared_evidence
    
    def _calculate_correlation_factors(
        self, 
        person_id: str, 
        source_typology: RiskTypology, 
        target_typology: RiskTypology
    ) -> Dict[str, float]:
        """Calculate specific correlation factors between typologies"""
        
        factors = {}
        
        # Get evidence from both typologies
        source_node = self.person_risk_nodes[person_id].get(source_typology)
        target_node = self.person_risk_nodes[person_id].get(target_typology)
        
        if not source_node or not target_node:
            return factors
        
        # Calculate timing correlation
        factors["timing_correlation"] = self._calculate_timing_correlation_factor(
            source_node, target_node
        )
        
        # Calculate account overlap factor
        factors["account_overlap"] = self._calculate_account_overlap_factor(
            source_node, target_node
        )
        
        # Calculate evidence strength correlation
        factors["evidence_strength_correlation"] = self._calculate_evidence_strength_correlation(
            source_node, target_node
        )
        
        # Add typology-specific factors
        if source_typology == RiskTypology.INSIDER_DEALING:
            factors["information_access_factor"] = 0.8
        elif source_typology == RiskTypology.SPOOFING:
            factors["market_impact_factor"] = 0.7
        
        return factors
    
    def _calculate_timing_correlation_factor(
        self, 
        source_node: PersonRiskNode, 
        target_node: PersonRiskNode
    ) -> float:
        """
        Calculate timing correlation between two risk nodes based on suspicious timing patterns.
        
        This method analyzes the temporal patterns of suspicious activities across different
        risk typologies for the same person to determine if they exhibit coordinated timing
        that could indicate related market abuse behaviors.
        
        Args:
            source_node: The source risk node (e.g., insider dealing)
            target_node: The target risk node (e.g., spoofing)
            
        Returns:
            float: Correlation factor between 0.0 and 1.0 where:
                   - 0.8: Both typologies show strong suspicious timing patterns (high correlation)
                   - 0.4: One typology shows suspicious timing (moderate correlation)  
                   - 0.1: Neither shows suspicious timing (low correlation)
                   - 0.0: No timing evidence available (no correlation)
        
        Logic:
            The correlation is highest when both risk typologies demonstrate suspicious
            timing patterns, suggesting coordinated market abuse activities. This supports
            cross-typology signal propagation where timing evidence in one area (e.g.,
            pre-announcement trading in insider dealing) can strengthen suspicion in
            related areas (e.g., coordinated spoofing around the same time).
        """
        
        source_timing = source_node.evidence_nodes.get("Q3_PersonTiming_" + source_node.person_id)
        target_timing = target_node.evidence_nodes.get("Q3_PersonTiming_" + target_node.person_id)
        
        if not source_timing or not target_timing:
            return 0.0
        
        source_state = source_timing.calculate_aggregated_state()
        target_state = target_timing.calculate_aggregated_state()
        
        # Higher correlation if both show suspicious timing
        if source_state > 0 and target_state > 0:
            return 0.8
        elif source_state > 0 or target_state > 0:
            return 0.4
        else:
            return 0.1
    
    def _calculate_account_overlap_factor(
        self, 
        source_node: PersonRiskNode, 
        target_node: PersonRiskNode
    ) -> float:
        """Calculate account overlap factor between risk nodes"""
        
        # Get account sets from evidence nodes
        source_accounts = set()
        target_accounts = set()
        
        for evidence_node in source_node.evidence_nodes.values():
            source_accounts.update(evidence_node.linked_accounts)
        
        for evidence_node in target_node.evidence_nodes.values():
            target_accounts.update(evidence_node.linked_accounts)
        
        if not source_accounts or not target_accounts:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = source_accounts.intersection(target_accounts)
        union = source_accounts.union(target_accounts)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_evidence_strength_correlation(
        self, 
        source_node: PersonRiskNode, 
        target_node: PersonRiskNode
    ) -> float:
        """Calculate correlation between evidence strengths"""
        
        source_strengths = []
        target_strengths = []
        
        # Get evidence strengths for common evidence types
        common_types = set(source_node.evidence_nodes.keys()).intersection(
            set(target_node.evidence_nodes.keys())
        )
        
        for evidence_type in common_types:
            source_summary = source_node.evidence_nodes[evidence_type].get_evidence_summary()
            target_summary = target_node.evidence_nodes[evidence_type].get_evidence_summary()
            
            source_strength = source_summary["aggregated_state"] / (len(source_summary.get("state_name", "")) - 1) if len(source_summary.get("state_name", "")) > 1 else 0
            target_strength = target_summary["aggregated_state"] / (len(target_summary.get("state_name", "")) - 1) if len(target_summary.get("state_name", "")) > 1 else 0
            
            source_strengths.append(source_strength)
            target_strengths.append(target_strength)
        
        if len(source_strengths) < 2:
            return 0.0
        
        # Calculate Pearson correlation
        try:
            correlation = np.corrcoef(source_strengths, target_strengths)[0, 1]
            return max(0.0, correlation) if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    def _apply_signals_to_nodes(self, person_id: str, signals: List[CrossTypologySignal]):
        """Apply cross-typology signals to target risk nodes"""
        
        for signal in signals:
            target_node = self.person_risk_nodes[person_id].get(signal.target_typology)
            if target_node:
                target_node.set_cross_typology_prior(
                    signal.source_typology, 
                    signal.impact_on_prior
                )
                logger.debug(f"Applied signal from {signal.source_typology.value} to {signal.target_typology.value} for person {person_id}")
    
    def calculate_escalation_factors(self, person_id: str) -> List[str]:
        """
        Calculate escalation factors based on cross-typology signals
        
        Args:
            person_id: The person to analyze
            
        Returns:
            List of escalation factor descriptions
        """
        escalation_factors = []
        
        if person_id not in self.active_signals:
            return escalation_factors
        
        person_signals = self.active_signals[person_id]
        
        # Count active typologies
        active_typologies = set()
        high_strength_signals = 0
        
        for signal in person_signals:
            active_typologies.add(signal.source_typology)
            active_typologies.add(signal.target_typology)
            
            if signal.signal_strength > self.escalation_thresholds["escalation_threshold"]:
                high_strength_signals += 1
        
        # Multiple typology involvement
        if len(active_typologies) >= 3:
            escalation_factors.append(f"Multiple risk typologies involved ({len(active_typologies)})")
        
        # High-strength cross-signals
        if high_strength_signals >= 2:
            escalation_factors.append(f"Strong cross-typology correlations ({high_strength_signals})")
        
        # Specific escalation patterns
        typology_names = [t.value for t in active_typologies]
        
        if "insider_dealing" in typology_names and "front_running" in typology_names:
            escalation_factors.append("Insider dealing + front running pattern detected")
        
        if "spoofing" in typology_names and "market_manipulation" in typology_names:
            escalation_factors.append("Market manipulation pattern detected")
        
        if len(active_typologies) >= 4:
            escalation_factors.append("Systematic abuse pattern across multiple typologies")
        
        return escalation_factors
    
    def get_person_cross_typology_summary(self, person_id: str) -> Dict[str, Any]:
        """Get comprehensive cross-typology summary for a person"""
        
        if person_id not in self.person_risk_nodes:
            return {"error": f"No risk nodes found for person {person_id}"}
        
        # Calculate current risk levels
        risk_levels = {}
        for typology, risk_node in self.person_risk_nodes[person_id].items():
            risk_prob, evidence_summary = risk_node.calculate_risk_probability()
            risk_levels[typology.value] = {
                "probability": risk_prob,
                "level": "high" if risk_prob > 0.67 else "medium" if risk_prob > 0.33 else "low",
                "cross_typology_adjustment": evidence_summary.get("cross_typology_adjustment", 0.0)
            }
        
        # Get active signals
        active_signals = []
        if person_id in self.active_signals:
            for signal in self.active_signals[person_id]:
                active_signals.append(signal.to_dict())
        
        # Calculate escalation factors
        escalation_factors = self.calculate_escalation_factors(person_id)
        
        # Determine overall risk assessment
        max_risk = max(risk_levels.values(), key=lambda x: x["probability"])["probability"] if risk_levels else 0.0
        cross_typology_boost = sum(r["cross_typology_adjustment"] for r in risk_levels.values())
        
        overall_assessment = {
            "max_individual_risk": max_risk,
            "cross_typology_boost": cross_typology_boost,
            "combined_risk": min(max_risk + cross_typology_boost, 1.0),
            "escalation_recommended": len(escalation_factors) > 0 or max_risk > 0.8
        }
        
        return {
            "person_id": person_id,
            "risk_levels": risk_levels,
            "active_signals": active_signals,
            "escalation_factors": escalation_factors,
            "overall_assessment": overall_assessment,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def cleanup_expired_signals(self):
        """Remove expired signals based on decay parameters"""
        
        current_time = datetime.now(timezone.utc)
        
        for person_id in list(self.active_signals.keys()):
            active_signals = []
            
            for signal in self.active_signals[person_id]:
                # Calculate signal age
                signal_age = (current_time - signal.signal_timestamp).total_seconds() / 3600  # hours
                
                # Apply decay
                if signal_age < self.signal_decay_hours:
                    decay_factor = 1.0 - (signal_age / self.signal_decay_hours)
                    decayed_strength = signal.signal_strength * decay_factor
                    
                    if decayed_strength >= self.min_signal_strength:
                        # Update signal strength
                        signal.signal_strength = decayed_strength
                        signal.impact_on_prior = decayed_strength * 0.3
                        active_signals.append(signal)
            
            if active_signals:
                self.active_signals[person_id] = active_signals
            else:
                del self.active_signals[person_id]
        
        logger.info(f"Signal cleanup completed. Active signals for {len(self.active_signals)} persons.")
    
    def update_typology_correlations(self, correlations: Dict[Tuple[RiskTypology, RiskTypology], float]):
        """
        Update typology correlation matrix with new correlation values.
        
        Args:
            correlations: Dictionary mapping risk typology pairs to correlation values.
                         Keys are tuples of (source_typology, target_typology) and values
                         are correlation coefficients in the range [0.0, 1.0] where:
                         - 0.0: No correlation between typologies
                         - 0.5: Moderate correlation 
                         - 1.0: Strong correlation
                         
                         Example:
                         {
                             (RiskTypology.INSIDER_DEALING, RiskTypology.SPOOFING): 0.7,
                             (RiskTypology.SPOOFING, RiskTypology.MARKET_MANIPULATION): 0.8
                         }
        """
        self.typology_correlations.update(correlations)
        logger.info("Updated typology correlation matrix")
    
    def get_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Get correlation matrix in readable format"""
        
        matrix = {}
        all_typologies = list(RiskTypology)
        
        for t1 in all_typologies:
            matrix[t1.value] = {}
            for t2 in all_typologies:
                if t1 == t2:
                    matrix[t1.value][t2.value] = 1.0
                else:
                    correlation = self.typology_correlations.get((t1, t2), 0.0)
                    matrix[t1.value][t2.value] = correlation
        
        return matrix