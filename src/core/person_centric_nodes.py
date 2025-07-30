"""
Person-Centric Bayesian Nodes for Individual Surveillance

This module extends the existing Bayesian node library to support person-level
clustering and evidence aggregation across linked accounts for all risk typologies.

Features:
- Person-level evidence nodes that aggregate across accounts
- Cross-account correlation nodes
- Identity confidence weighting
- Typology-agnostic node templates
- Evidence strength scoring with person context
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from src.core.node_library import BayesianNode, EvidenceNode, RiskFactorNode, OutcomeNode
from src.models.person_centric import RiskTypology, PersonRiskProfile, EvidenceType
from src.models.trading_data import RawTradeData

logger = logging.getLogger(__name__)


class PersonEvidenceNode(EvidenceNode):
    """
    Evidence node that aggregates data across all accounts linked to a person
    """
    
    def __init__(
        self,
        name: str,
        states: List[str],
        person_id: str,
        evidence_type: EvidenceType = EvidenceType.TRADING_PATTERN,
        description: str = "",
        fallback_prior: Optional[List[float]] = None,
        identity_confidence: float = 1.0
    ):
        super().__init__(name, states, description, fallback_prior)
        self.person_id = person_id
        self.evidence_type = evidence_type
        self.identity_confidence = identity_confidence
        self.linked_accounts: Set[str] = set()
        self.evidence_sources: Dict[str, Any] = {}
        self.cross_account_patterns: Dict[str, float] = {}
        
    def add_account_evidence(self, account_id: str, evidence_data: Dict[str, Any]):
        """Add evidence from a specific account"""
        self.linked_accounts.add(account_id)
        self.evidence_sources[account_id] = evidence_data
        
    def calculate_aggregated_state(self) -> int:
        """
        Calculate aggregated state across all linked accounts
        
        Returns:
            State index based on aggregated evidence
        """
        if not self.evidence_sources:
            return 0  # Default to first state (typically "low" or "normal")
            
        # Aggregate evidence strength across accounts
        total_strength = 0.0
        account_count = len(self.evidence_sources)
        
        for account_id, evidence in self.evidence_sources.items():
            strength = evidence.get("strength", 0.0)
            # Weight by identity confidence
            weighted_strength = strength * self.identity_confidence
            total_strength += weighted_strength
            
        # Average strength with cross-account bonus
        avg_strength = total_strength / account_count if account_count > 0 else 0.0
        
        # Add cross-account correlation bonus
        cross_account_bonus = self._calculate_cross_account_bonus()
        final_strength = min(avg_strength + cross_account_bonus, 1.0)
        
        # Map to state index
        return self._strength_to_state_index(final_strength)
    
    def _calculate_cross_account_bonus(self) -> float:
        """Calculate bonus for cross-account activity patterns"""
        if len(self.linked_accounts) <= 1:
            return 0.0
            
        # Base bonus for multi-account activity
        base_bonus = 0.1 * min(len(self.linked_accounts) - 1, 3) / 3  # Max 0.1 for 4+ accounts
        
        # Pattern correlation bonus
        pattern_bonus = 0.0
        if self.cross_account_patterns:
            avg_correlation = np.mean(list(self.cross_account_patterns.values()))
            pattern_bonus = avg_correlation * 0.2  # Max 0.2 bonus
            
        return base_bonus + pattern_bonus
    
    def _strength_to_state_index(self, strength: float) -> int:
        """Map evidence strength to state index"""
        if len(self.states) == 2:  # Binary states (e.g., normal/suspicious)
            return 1 if strength > 0.5 else 0
        elif len(self.states) == 3:  # Three states (e.g., low/medium/high)
            if strength < 0.33:
                return 0
            elif strength < 0.67:
                return 1
            else:
                return 2
        else:  # Four or more states
            return min(int(strength * len(self.states)), len(self.states) - 1)
    
    def get_evidence_summary(self) -> Dict[str, Any]:
        """Get summary of aggregated evidence"""
        return {
            "person_id": self.person_id,
            "evidence_type": self.evidence_type,
            "linked_accounts": list(self.linked_accounts),
            "account_count": len(self.linked_accounts),
            "identity_confidence": self.identity_confidence,
            "cross_account_patterns": self.cross_account_patterns,
            "aggregated_state": self.calculate_aggregated_state(),
            "state_name": self.states[self.calculate_aggregated_state()]
        }


class PersonTradingPatternNode(PersonEvidenceNode):
    """Person-level trading pattern evidence node"""
    
    def __init__(self, person_id: str, identity_confidence: float = 1.0):
        super().__init__(
            name=f"Q1_PersonTradingPattern_{person_id}",
            states=["normal", "suspicious", "highly_suspicious"],
            person_id=person_id,
            evidence_type=EvidenceType.TRADING_PATTERN,
            description=f"Trading patterns aggregated across all accounts for person {person_id}",
            fallback_prior=[0.7, 0.25, 0.05],
            identity_confidence=identity_confidence
        )
        
    def analyze_trading_patterns(self, trades_by_account: Dict[str, List[RawTradeData]]):
        """Analyze trading patterns across accounts"""
        for account_id, trades in trades_by_account.items():
            if not trades:
                continue
                
            # Analyze patterns for this account
            pattern_analysis = self._analyze_account_patterns(trades)
            self.add_account_evidence(account_id, pattern_analysis)
            
        # Calculate cross-account correlations
        self._calculate_cross_account_correlations(trades_by_account)
    
    def _analyze_account_patterns(self, trades: List[RawTradeData]) -> Dict[str, Any]:
        """Analyze trading patterns for a single account"""
        if not trades:
            return {"strength": 0.0, "patterns": []}
            
        patterns = []
        strength = 0.0
        
        # Volume concentration analysis
        total_volume = sum(t.quantity for t in trades)
        if total_volume > 100000:  # Large volume threshold
            patterns.append("large_volume")
            strength += 0.3
            
        # Rapid succession analysis
        if len(trades) >= 5:
            patterns.append("rapid_succession")
            strength += 0.2
            
        # Time clustering analysis
        if self._detect_time_clustering(trades):
            patterns.append("time_clustering")
            strength += 0.3
            
        # Price impact analysis
        if self._detect_price_impact_patterns(trades):
            patterns.append("price_impact")
            strength += 0.4
            
        return {
            "strength": min(strength, 1.0),
            "patterns": patterns,
            "trade_count": len(trades),
            "total_volume": total_volume
        }
    
    def _detect_time_clustering(self, trades: List[RawTradeData]) -> bool:
        """Detect temporal clustering in trades"""
        if len(trades) < 3:
            return False
            
        # Simple clustering detection based on time gaps
        timestamps = []
        for trade in trades:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(trade.execution_timestamp.replace('Z', '+00:00'))
                timestamps.append(dt.timestamp())
            except:
                continue
                
        if len(timestamps) < 3:
            return False
            
        timestamps.sort()
        gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_gap = np.mean(gaps)
        
        # Count gaps significantly smaller than average
        small_gaps = sum(1 for gap in gaps if gap < avg_gap * 0.3)
        return small_gaps >= 2
    
    def _detect_price_impact_patterns(self, trades: List[RawTradeData]) -> bool:
        """Detect patterns suggesting price manipulation"""
        # Simplified price impact detection
        # In real implementation, this would analyze price movements relative to trades
        
        # Check for alternating buy/sell patterns (potential wash trading indicator)
        if len(trades) < 4:
            return False
            
        directions = []
        for trade in trades:
            directions.append(trade.direction.value if hasattr(trade.direction, 'value') else str(trade.direction))
            
        # Look for alternating patterns
        alternating_count = 0
        for i in range(len(directions) - 1):
            if directions[i] != directions[i + 1]:
                alternating_count += 1
                
        # High alternation ratio suggests potential manipulation
        alternation_ratio = alternating_count / (len(directions) - 1) if len(directions) > 1 else 0
        return alternation_ratio > 0.7
    
    def _calculate_cross_account_correlations(self, trades_by_account: Dict[str, List[RawTradeData]]):
        """Calculate correlations between accounts"""
        if len(trades_by_account) <= 1:
            return
            
        accounts = list(trades_by_account.keys())
        correlations = {}
        
        for i, account1 in enumerate(accounts):
            for account2 in accounts[i+1:]:
                correlation = self._calculate_account_correlation(
                    trades_by_account[account1], 
                    trades_by_account[account2]
                )
                correlations[f"{account1}_{account2}"] = correlation
                
        self.cross_account_patterns = correlations
    
    def _calculate_account_correlation(
        self, 
        trades1: List[RawTradeData], 
        trades2: List[RawTradeData]
    ) -> float:
        """Calculate correlation between two accounts"""
        if not trades1 or not trades2:
            return 0.0
            
        # Timing correlation
        timing_corr = self._calculate_timing_correlation(trades1, trades2)
        
        # Instrument correlation
        instruments1 = set(t.symbol for t in trades1)
        instruments2 = set(t.symbol for t in trades2)
        
        if not instruments1 or not instruments2:
            instrument_corr = 0.0
        else:
            intersection = instruments1.intersection(instruments2)
            union = instruments1.union(instruments2)
            instrument_corr = len(intersection) / len(union)
            
        return (timing_corr + instrument_corr) / 2
    
    def _calculate_timing_correlation(
        self, 
        trades1: List[RawTradeData], 
        trades2: List[RawTradeData]
    ) -> float:
        """Calculate timing correlation between accounts"""
        if not trades1 or not trades2:
            return 0.0
            
        # Count trades within 5-minute windows
        from datetime import datetime
        
        synchronized_count = 0
        total_comparisons = 0
        
        for trade1 in trades1:
            for trade2 in trades2:
                total_comparisons += 1
                try:
                    dt1 = datetime.fromisoformat(trade1.execution_timestamp.replace('Z', '+00:00'))
                    dt2 = datetime.fromisoformat(trade2.execution_timestamp.replace('Z', '+00:00'))
                    
                    time_diff = abs((dt1 - dt2).total_seconds())
                    if time_diff <= 300:  # Within 5 minutes
                        synchronized_count += 1
                except:
                    continue
                    
        return synchronized_count / total_comparisons if total_comparisons > 0 else 0.0


class PersonCommunicationNode(PersonEvidenceNode):
    """Person-level communication evidence node"""
    
    def __init__(self, person_id: str, identity_confidence: float = 1.0):
        super().__init__(
            name=f"Q2_PersonCommunication_{person_id}",
            states=["benign", "suspicious", "highly_suspicious"],
            person_id=person_id,
            evidence_type=EvidenceType.COMMUNICATION,
            description=f"Communication patterns aggregated across all channels for person {person_id}",
            fallback_prior=[0.8, 0.15, 0.05],
            identity_confidence=identity_confidence
        )
        
    def analyze_communications(self, comms_by_channel: Dict[str, List[Dict[str, Any]]]):
        """Analyze communication patterns across channels"""
        for channel_id, comms in comms_by_channel.items():
            if not comms:
                continue
                
            comm_analysis = self._analyze_channel_communications(comms)
            self.add_account_evidence(channel_id, comm_analysis)
    
    def _analyze_channel_communications(self, comms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze communications for a single channel"""
        if not comms:
            return {"strength": 0.0, "indicators": []}
            
        indicators = []
        strength = 0.0
        
        # Sensitive keyword analysis
        sensitive_count = self._count_sensitive_communications(comms)
        if sensitive_count > 0:
            indicators.append("sensitive_content")
            strength += min(sensitive_count / len(comms), 0.5)
            
        # External communication analysis
        external_count = sum(1 for c in comms if c.get("external", False))
        if external_count > len(comms) * 0.3:  # >30% external
            indicators.append("high_external_ratio")
            strength += 0.3
            
        # Timing analysis (burst communications)
        if self._detect_communication_bursts(comms):
            indicators.append("communication_bursts")
            strength += 0.2
            
        return {
            "strength": min(strength, 1.0),
            "indicators": indicators,
            "comm_count": len(comms),
            "sensitive_count": sensitive_count,
            "external_count": external_count
        }
    
    def _count_sensitive_communications(self, comms: List[Dict[str, Any]]) -> int:
        """Count communications with sensitive content"""
        sensitive_keywords = [
            "insider", "tip", "confidential", "material", "non-public",
            "announcement", "merger", "acquisition", "earnings"
        ]
        
        sensitive_count = 0
        for comm in comms:
            content = comm.get("content", "").lower()
            if any(keyword in content for keyword in sensitive_keywords):
                sensitive_count += 1
                
        return sensitive_count
    
    def _detect_communication_bursts(self, comms: List[Dict[str, Any]]) -> bool:
        """Detect burst patterns in communications"""
        if len(comms) < 3:
            return False
            
        # Extract timestamps
        timestamps = []
        for comm in comms:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(comm.get("timestamp", "").replace('Z', '+00:00'))
                timestamps.append(dt.timestamp())
            except:
                continue
                
        if len(timestamps) < 3:
            return False
            
        timestamps.sort()
        
        # Look for clusters of communications within short time windows
        burst_count = 0
        for i in range(len(timestamps) - 2):
            # Check if 3 communications within 10 minutes
            if timestamps[i + 2] - timestamps[i] <= 600:  # 10 minutes
                burst_count += 1
                
        return burst_count >= 1


class PersonTimingNode(PersonEvidenceNode):
    """Person-level timing evidence node"""
    
    def __init__(self, person_id: str, identity_confidence: float = 1.0):
        super().__init__(
            name=f"Q3_PersonTiming_{person_id}",
            states=["normal", "suspicious", "highly_suspicious"],
            person_id=person_id,
            evidence_type=EvidenceType.TIMING_ANOMALY,
            description=f"Timing patterns aggregated across all activities for person {person_id}",
            fallback_prior=[0.75, 0.2, 0.05],
            identity_confidence=identity_confidence
        )
        
    def analyze_timing_patterns(
        self, 
        trades_by_account: Dict[str, List[RawTradeData]],
        comms_by_channel: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        news_events: Optional[List[Dict[str, Any]]] = None
    ):
        """Analyze timing patterns across all activities"""
        
        # Analyze trading timing
        for account_id, trades in trades_by_account.items():
            if trades:
                timing_analysis = self._analyze_trading_timing(trades, news_events)
                self.add_account_evidence(f"trading_{account_id}", timing_analysis)
                
        # Analyze communication timing
        if comms_by_channel:
            for channel_id, comms in comms_by_channel.items():
                if comms:
                    comm_timing_analysis = self._analyze_communication_timing(comms, news_events)
                    self.add_account_evidence(f"comm_{channel_id}", comm_timing_analysis)
    
    def _analyze_trading_timing(
        self, 
        trades: List[RawTradeData], 
        news_events: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Analyze timing patterns in trading"""
        if not trades:
            return {"strength": 0.0, "patterns": []}
            
        patterns = []
        strength = 0.0
        
        # Off-hours trading analysis
        off_hours_count = self._count_off_hours_trades(trades)
        if off_hours_count > 0:
            patterns.append("off_hours_trading")
            strength += min(off_hours_count / len(trades), 0.4)
            
        # Pre-announcement trading (if news events available)
        if news_events:
            pre_announcement_count = self._count_pre_announcement_trades(trades, news_events)
            if pre_announcement_count > 0:
                patterns.append("pre_announcement_trading")
                strength += min(pre_announcement_count / len(trades), 0.6)
                
        # Rapid succession patterns
        if self._detect_rapid_succession(trades):
            patterns.append("rapid_succession")
            strength += 0.3
            
        return {
            "strength": min(strength, 1.0),
            "patterns": patterns,
            "off_hours_count": off_hours_count,
            "total_trades": len(trades)
        }
    
    def _count_off_hours_trades(self, trades: List[RawTradeData]) -> int:
        """Count trades executed outside normal market hours"""
        off_hours_count = 0
        
        for trade in trades:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(trade.execution_timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                
                # Simplified market hours (9 AM to 4 PM)
                if hour < 9 or hour > 16:
                    off_hours_count += 1
            except:
                continue
                
        return off_hours_count
    
    def _count_pre_announcement_trades(
        self, 
        trades: List[RawTradeData], 
        news_events: List[Dict[str, Any]]
    ) -> int:
        """Count trades that occurred before relevant news announcements"""
        pre_announcement_count = 0
        
        for trade in trades:
            try:
                from datetime import datetime
                trade_time = datetime.fromisoformat(trade.execution_timestamp.replace('Z', '+00:00'))
                
                # Check if trade occurred within 24 hours before any news event
                for event in news_events:
                    event_time = datetime.fromisoformat(event.get("timestamp", "").replace('Z', '+00:00'))
                    time_diff = (event_time - trade_time).total_seconds()
                    
                    # Trade within 24 hours before announcement
                    if 0 < time_diff <= 86400:  # 24 hours in seconds
                        # Check if trade involves same instrument as news
                        if trade.symbol == event.get("symbol"):
                            pre_announcement_count += 1
                            break
            except:
                continue
                
        return pre_announcement_count
    
    def _detect_rapid_succession(self, trades: List[RawTradeData]) -> bool:
        """Detect rapid succession trading patterns"""
        if len(trades) < 3:
            return False
            
        # Sort trades by timestamp
        sorted_trades = sorted(trades, key=lambda t: t.execution_timestamp)
        
        rapid_sequences = 0
        for i in range(len(sorted_trades) - 2):
            try:
                from datetime import datetime
                t1 = datetime.fromisoformat(sorted_trades[i].execution_timestamp.replace('Z', '+00:00'))
                t3 = datetime.fromisoformat(sorted_trades[i + 2].execution_timestamp.replace('Z', '+00:00'))
                
                # 3 trades within 5 minutes
                if (t3 - t1).total_seconds() <= 300:
                    rapid_sequences += 1
            except:
                continue
                
        return rapid_sequences >= 1
    
    def _analyze_communication_timing(
        self, 
        comms: List[Dict[str, Any]], 
        news_events: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Analyze timing patterns in communications"""
        if not comms:
            return {"strength": 0.0, "patterns": []}
            
        patterns = []
        strength = 0.0
        
        # Pre-announcement communications
        if news_events:
            pre_announcement_count = self._count_pre_announcement_comms(comms, news_events)
            if pre_announcement_count > 0:
                patterns.append("pre_announcement_comms")
                strength += min(pre_announcement_count / len(comms), 0.5)
                
        return {
            "strength": min(strength, 1.0),
            "patterns": patterns,
            "total_comms": len(comms)
        }
    
    def _count_pre_announcement_comms(
        self, 
        comms: List[Dict[str, Any]], 
        news_events: List[Dict[str, Any]]
    ) -> int:
        """Count communications that occurred before news announcements"""
        pre_announcement_count = 0
        
        for comm in comms:
            try:
                from datetime import datetime
                comm_time = datetime.fromisoformat(comm.get("timestamp", "").replace('Z', '+00:00'))
                
                for event in news_events:
                    event_time = datetime.fromisoformat(event.get("timestamp", "").replace('Z', '+00:00'))
                    time_diff = (event_time - comm_time).total_seconds()
                    
                    # Communication within 48 hours before announcement
                    if 0 < time_diff <= 172800:  # 48 hours
                        pre_announcement_count += 1
                        break
            except:
                continue
                
        return pre_announcement_count


class PersonAccessNode(PersonEvidenceNode):
    """Person-level access and role evidence node"""
    
    def __init__(self, person_id: str, identity_confidence: float = 1.0):
        super().__init__(
            name=f"Q4_PersonAccess_{person_id}",
            states=["low_access", "medium_access", "high_access"],
            person_id=person_id,
            evidence_type=EvidenceType.ACCESS_PRIVILEGE,
            description=f"Access and role information for person {person_id}",
            fallback_prior=[0.6, 0.3, 0.1],
            identity_confidence=identity_confidence
        )
        
    def analyze_access_patterns(self, person_profile: PersonRiskProfile):
        """Analyze access patterns from person profile"""
        access_analysis = self._analyze_role_access(person_profile)
        self.add_account_evidence("role_access", access_analysis)
        
        # Analyze desk access
        desk_analysis = self._analyze_desk_access(person_profile)
        self.add_account_evidence("desk_access", desk_analysis)
    
    def _analyze_role_access(self, person_profile: PersonRiskProfile) -> Dict[str, Any]:
        """Analyze role-based access"""
        if not person_profile.primary_role:
            return {"strength": 0.2, "level": "unknown"}
            
        role = person_profile.primary_role.lower()
        
        # Define access levels based on role
        high_access_roles = ["executive", "head", "director", "chief", "portfolio_manager"]
        medium_access_roles = ["senior_trader", "trader", "analyst", "sales"]
        
        if any(hr_role in role for hr_role in high_access_roles):
            return {"strength": 0.8, "level": "high", "role": role}
        elif any(mr_role in role for mr_role in medium_access_roles):
            return {"strength": 0.5, "level": "medium", "role": role}
        else:
            return {"strength": 0.2, "level": "low", "role": role}
    
    def _analyze_desk_access(self, person_profile: PersonRiskProfile) -> Dict[str, Any]:
        """Analyze desk-based access"""
        if not person_profile.linked_desks:
            return {"strength": 0.2, "sensitivity": "unknown"}
            
        sensitive_desks = ["prop", "proprietary", "research", "investment_banking", "trading"]
        
        max_sensitivity = 0.0
        sensitive_desk_count = 0
        
        for desk in person_profile.linked_desks:
            desk_lower = desk.lower()
            if any(sd in desk_lower for sd in sensitive_desks):
                sensitive_desk_count += 1
                if "prop" in desk_lower or "research" in desk_lower:
                    max_sensitivity = max(max_sensitivity, 0.8)
                elif "investment_banking" in desk_lower:
                    max_sensitivity = max(max_sensitivity, 0.9)
                else:
                    max_sensitivity = max(max_sensitivity, 0.6)
                    
        return {
            "strength": max_sensitivity,
            "sensitivity": "high" if max_sensitivity > 0.7 else "medium" if max_sensitivity > 0.4 else "low",
            "sensitive_desk_count": sensitive_desk_count,
            "total_desks": len(person_profile.linked_desks)
        }


class PersonRiskNode(RiskFactorNode):
    """
    Person-level risk node that aggregates evidence across all linked accounts
    """
    
    def __init__(
        self, 
        person_id: str, 
        risk_typology: RiskTypology,
        identity_confidence: float = 1.0
    ):
        self.person_id = person_id
        self.risk_typology = risk_typology
        self.identity_confidence = identity_confidence
        
        super().__init__(
            name=f"PersonRisk_{risk_typology.value}_{person_id}",
            states=["low_risk", "medium_risk", "high_risk"],
            description=f"Person-level {risk_typology.value} risk for {person_id}",
            fallback_prior=[0.8, 0.15, 0.05]
        )
        
        # Evidence nodes that feed into this risk node
        self.evidence_nodes: Dict[str, PersonEvidenceNode] = {}
        self.cross_typology_priors: Dict[RiskTypology, float] = {}
        
    def add_evidence_node(self, node: PersonEvidenceNode):
        """Add an evidence node that contributes to this risk assessment"""
        self.evidence_nodes[node.name] = node
        
    def set_cross_typology_prior(self, source_typology: RiskTypology, prior_strength: float):
        """Set prior from another risk typology"""
        self.cross_typology_priors[source_typology] = prior_strength
        
    def calculate_risk_probability(self) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate risk probability based on all evidence nodes
        
        Returns:
            Tuple of (risk_probability, evidence_summary)
        """
        if not self.evidence_nodes:
            return 0.1, {"error": "No evidence nodes available"}
            
        # Aggregate evidence from all nodes
        evidence_scores = {}
        total_weight = 0.0
        weighted_score = 0.0
        
        # Standard evidence weights
        evidence_weights = {
            EvidenceType.TRADING_PATTERN: 0.4,
            EvidenceType.COMMUNICATION: 0.25,
            EvidenceType.TIMING_ANOMALY: 0.2,
            EvidenceType.ACCESS_PRIVILEGE: 0.15
        }
        
        for node_name, node in self.evidence_nodes.items():
            evidence_type = node.evidence_type
            weight = evidence_weights.get(evidence_type, 0.1)
            
            # Get evidence strength
            evidence_summary = node.get_evidence_summary()
            state_index = evidence_summary["aggregated_state"]
            
            # Convert state to strength score
            strength = state_index / (len(node.states) - 1) if len(node.states) > 1 else 0.0
            
            # Weight by identity confidence
            confidence_weighted_strength = strength * self.identity_confidence
            
            evidence_scores[evidence_type] = {
                "strength": strength,
                "confidence_weighted": confidence_weighted_strength,
                "weight": weight,
                "state": node.states[state_index],
                "account_count": evidence_summary["account_count"]
            }
            
            weighted_score += confidence_weighted_strength * weight
            total_weight += weight
            
        # Calculate base risk probability
        base_risk = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Apply cross-typology priors
        cross_typology_adjustment = self._calculate_cross_typology_adjustment()
        
        # Final risk probability
        final_risk = min(base_risk + cross_typology_adjustment, 1.0)
        
        # Prepare evidence summary
        evidence_summary = {
            "person_id": self.person_id,
            "risk_typology": self.risk_typology.value,
            "base_risk": base_risk,
            "cross_typology_adjustment": cross_typology_adjustment,
            "final_risk": final_risk,
            "identity_confidence": self.identity_confidence,
            "evidence_scores": evidence_scores,
            "cross_typology_priors": {k.value: v for k, v in self.cross_typology_priors.items()}
        }
        
        return final_risk, evidence_summary
    
    def _calculate_cross_typology_adjustment(self) -> float:
        """Calculate adjustment based on cross-typology signals"""
        if not self.cross_typology_priors:
            return 0.0
            
        # Simple weighted average of cross-typology signals
        total_adjustment = 0.0
        total_weight = 0.0
        
        # Define weights for different typology influences
        typology_influence_weights = {
            RiskTypology.INSIDER_DEALING: 0.3,
            RiskTypology.SPOOFING: 0.25,
            RiskTypology.WASH_TRADING: 0.2,
            RiskTypology.FRONT_RUNNING: 0.15,
            RiskTypology.MARKET_MANIPULATION: 0.1
        }
        
        for source_typology, prior_strength in self.cross_typology_priors.items():
            weight = typology_influence_weights.get(source_typology, 0.1)
            total_adjustment += prior_strength * weight * 0.2  # Max 20% adjustment
            total_weight += weight
            
        return total_adjustment / total_weight if total_weight > 0 else 0.0
    
    def get_risk_explanation(self) -> Dict[str, Any]:
        """Get detailed explanation of risk assessment"""
        risk_prob, evidence_summary = self.calculate_risk_probability()
        
        # Determine risk level
        if risk_prob < 0.33:
            risk_level = "low"
        elif risk_prob < 0.67:
            risk_level = "medium"
        else:
            risk_level = "high"
            
        # Identify key drivers
        key_drivers = []
        if "evidence_scores" in evidence_summary:
            for evidence_type, scores in evidence_summary["evidence_scores"].items():
                if scores["confidence_weighted"] > 0.5:
                    key_drivers.append({
                        "type": evidence_type,
                        "strength": scores["strength"],
                        "state": scores["state"],
                        "accounts": scores["account_count"]
                    })
        
        return {
            "person_id": self.person_id,
            "risk_typology": self.risk_typology.value,
            "risk_probability": risk_prob,
            "risk_level": risk_level,
            "key_drivers": key_drivers,
            "cross_typology_influence": len(self.cross_typology_priors) > 0,
            "identity_confidence": self.identity_confidence,
            "evidence_summary": evidence_summary
        }


def create_person_risk_nodes(
    person_id: str, 
    risk_typology: RiskTypology,
    identity_confidence: float = 1.0
) -> Tuple[PersonRiskNode, Dict[str, PersonEvidenceNode]]:
    """
    Factory function to create a complete set of person-centric nodes for a risk typology
    
    Args:
        person_id: The person identifier
        risk_typology: The risk typology to model
        identity_confidence: Confidence in person identity resolution
        
    Returns:
        Tuple of (risk_node, evidence_nodes_dict)
    """
    
    # Create evidence nodes
    evidence_nodes = {
        EvidenceType.TRADING_PATTERN.value: PersonTradingPatternNode(person_id, identity_confidence),
        EvidenceType.COMMUNICATION.value: PersonCommunicationNode(person_id, identity_confidence),
        EvidenceType.TIMING_ANOMALY.value: PersonTimingNode(person_id, identity_confidence),
        EvidenceType.ACCESS_PRIVILEGE.value: PersonAccessNode(person_id, identity_confidence)
    }
    
    # Create risk node
    risk_node = PersonRiskNode(person_id, risk_typology, identity_confidence)
    
    # Connect evidence nodes to risk node
    for node in evidence_nodes.values():
        risk_node.add_evidence_node(node)
        
    return risk_node, evidence_nodes