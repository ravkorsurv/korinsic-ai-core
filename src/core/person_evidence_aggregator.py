"""
Person-Level Evidence Aggregation Service

This service aggregates evidence across all accounts, desks, and data sources
linked to an individual person for comprehensive risk assessment.

Features:
- Cross-account trade pattern aggregation
- Communication data integration
- Temporal pattern analysis
- Evidence strength scoring
- Cross-typology evidence sharing
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from dataclasses import asdict

from src.models.person_centric import (
    PersonCentricEvidence,
    PersonRiskProfile,
    PersonActivitySummary,
    RiskTypology,
    CrossTypologySignal
)
from src.models.trading_data import RawTradeData, TradeDirection
from .entity_resolution import EntityResolutionService, PersonIdentity

logger = logging.getLogger(__name__)


class PersonEvidenceAggregator:
    """
    Aggregates evidence across all accounts and data sources for person-centric analysis
    """
    
    def __init__(self, entity_resolution_service: EntityResolutionService):
        self.entity_resolution = entity_resolution_service
        self.evidence_cache: Dict[str, List[PersonCentricEvidence]] = defaultdict(list)
        self.risk_profiles: Dict[str, PersonRiskProfile] = {}
        
        # Evidence weighting parameters
        self.evidence_weights = {
            "trading_pattern": 0.4,
            "communication": 0.25,
            "timing": 0.2,
            "access": 0.15
        }
        
        # Cross-account correlation thresholds
        self.correlation_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
    
    def aggregate_person_evidence(
        self, 
        person_id: str, 
        trade_data: List[RawTradeData],
        communication_data: Optional[List[Dict[str, Any]]] = None,
        time_window_hours: int = 24
    ) -> PersonRiskProfile:
        """
        Aggregate all evidence for a person across linked accounts
        
        Args:
            person_id: The resolved person ID
            trade_data: List of trade data from all linked accounts
            communication_data: Communication data from all linked sources
            time_window_hours: Time window for evidence aggregation
            
        Returns:
            PersonRiskProfile with aggregated evidence
        """
        logger.info(f"Aggregating evidence for person {person_id}")
        
        # Get person identity information
        person_identity = self._get_person_identity(person_id)
        if not person_identity:
            logger.warning(f"Person identity not found for {person_id}")
            return self._create_empty_profile(person_id)
        
        # Initialize or update risk profile
        if person_id not in self.risk_profiles:
            self.risk_profiles[person_id] = self._initialize_risk_profile(person_identity)
        
        profile = self.risk_profiles[person_id]
        
        # Aggregate trading patterns
        trading_evidence = self._aggregate_trading_evidence(person_id, trade_data, time_window_hours)
        
        # Aggregate communication evidence
        comm_evidence = self._aggregate_communication_evidence(
            person_id, communication_data or [], time_window_hours
        )
        
        # Aggregate timing evidence
        timing_evidence = self._aggregate_timing_evidence(person_id, trade_data, time_window_hours)
        
        # Aggregate access/role evidence
        access_evidence = self._aggregate_access_evidence(person_id, person_identity)
        
        # Update profile with aggregated evidence
        profile.aggregated_evidence = {
            "trading_patterns": trading_evidence,
            "communications": comm_evidence,
            "timing_patterns": timing_evidence,
            "access_patterns": access_evidence
        }
        
        # Calculate cross-account correlations
        profile.cross_risk_correlations = self._calculate_cross_account_correlations(
            person_id, trade_data
        )
        
        # Update evidence sources
        profile.evidence_sources = self._map_evidence_sources(person_id, trade_data, communication_data)
        
        # Update temporal metadata
        profile.last_updated = datetime.now(timezone.utc)
        
        logger.info(f"Evidence aggregation completed for person {person_id}")
        return profile
    
    def _get_person_identity(self, person_id: str) -> Optional[PersonIdentity]:
        """Get person identity from entity resolution service"""
        all_persons = self.entity_resolution.get_all_persons()
        return all_persons.get(person_id)
    
    def _initialize_risk_profile(self, person_identity: PersonIdentity) -> PersonRiskProfile:
        """Initialize a new risk profile from person identity"""
        return PersonRiskProfile(
            person_id=person_identity.person_id,
            primary_name=person_identity.primary_name,
            primary_role=person_identity.primary_role,
            linked_accounts=person_identity.linked_accounts.copy(),
            linked_desks=person_identity.linked_desks.copy(),
            linked_emails=person_identity.linked_emails.copy(),
            identity_confidence=person_identity.confidence_score
        )
    
    def _create_empty_profile(self, person_id: str) -> PersonRiskProfile:
        """Create empty profile for unknown person"""
        return PersonRiskProfile(person_id=person_id, identity_confidence=0.0)
    
    def _aggregate_trading_evidence(
        self, 
        person_id: str, 
        trade_data: List[RawTradeData], 
        time_window_hours: int
    ) -> Dict[str, Any]:
        """Aggregate trading patterns across all linked accounts"""
        
        # Filter trades for this person within time window
        person_trades = self._filter_person_trades(person_id, trade_data, time_window_hours)
        
        if not person_trades:
            return {"strength": 0.0, "patterns": {}, "cross_account_activity": False}
        
        # Group trades by account
        trades_by_account = defaultdict(list)
        for trade in person_trades:
            trades_by_account[trade.trader_id].append(trade)
        
        # Analyze cross-account patterns
        cross_account_patterns = self._analyze_cross_account_patterns(trades_by_account)
        
        # Calculate trading pattern strength
        pattern_strength = self._calculate_trading_pattern_strength(person_trades, cross_account_patterns)
        
        # Identify suspicious patterns
        suspicious_patterns = self._identify_suspicious_trading_patterns(person_trades, cross_account_patterns)
        
        return {
            "strength": pattern_strength,
            "patterns": suspicious_patterns,
            "cross_account_activity": len(trades_by_account) > 1,
            "account_count": len(trades_by_account),
            "total_trades": len(person_trades),
            "cross_account_correlations": cross_account_patterns,
            "temporal_clustering": self._analyze_temporal_clustering(person_trades)
        }
    
    def _aggregate_communication_evidence(
        self, 
        person_id: str, 
        communication_data: List[Dict[str, Any]], 
        time_window_hours: int
    ) -> Dict[str, Any]:
        """Aggregate communication evidence across all linked channels"""
        
        if not communication_data:
            return {"strength": 0.0, "patterns": {}, "sensitive_content": False}
        
        # Filter communications for this person
        person_comms = self._filter_person_communications(person_id, communication_data, time_window_hours)
        
        if not person_comms:
            return {"strength": 0.0, "patterns": {}, "sensitive_content": False}
        
        # Analyze communication patterns
        comm_patterns = self._analyze_communication_patterns(person_comms)
        
        # Detect sensitive content
        sensitive_indicators = self._detect_sensitive_communications(person_comms)
        
        # Calculate communication evidence strength
        comm_strength = self._calculate_communication_strength(person_comms, sensitive_indicators)
        
        return {
            "strength": comm_strength,
            "patterns": comm_patterns,
            "sensitive_content": len(sensitive_indicators) > 0,
            "sensitive_indicators": sensitive_indicators,
            "communication_count": len(person_comms),
            "external_communications": sum(1 for c in person_comms if c.get("external", False))
        }
    
    def _aggregate_timing_evidence(
        self, 
        person_id: str, 
        trade_data: List[RawTradeData], 
        time_window_hours: int
    ) -> Dict[str, Any]:
        """Aggregate timing-based evidence across accounts"""
        
        person_trades = self._filter_person_trades(person_id, trade_data, time_window_hours)
        
        if not person_trades:
            return {"strength": 0.0, "patterns": {}, "suspicious_timing": False}
        
        # Analyze timing patterns
        timing_patterns = self._analyze_timing_patterns(person_trades)
        
        # Detect suspicious timing (e.g., pre-announcement trading)
        suspicious_timing = self._detect_suspicious_timing(person_trades)
        
        # Calculate timing evidence strength
        timing_strength = self._calculate_timing_strength(timing_patterns, suspicious_timing)
        
        return {
            "strength": timing_strength,
            "patterns": timing_patterns,
            "suspicious_timing": len(suspicious_timing) > 0,
            "timing_anomalies": suspicious_timing,
            "cross_account_synchronization": self._analyze_cross_account_timing(person_trades)
        }
    
    def _aggregate_access_evidence(self, person_id: str, person_identity: PersonIdentity) -> Dict[str, Any]:
        """Aggregate access and role-based evidence"""
        
        if not person_identity:
            return {"strength": 0.0, "access_level": "unknown", "sensitive_access": False}
        
        # Analyze role-based access
        access_analysis = self._analyze_role_access(person_identity)
        
        # Check for sensitive information access
        sensitive_access = self._check_sensitive_access(person_identity)
        
        # Calculate access evidence strength
        access_strength = self._calculate_access_strength(access_analysis, sensitive_access)
        
        return {
            "strength": access_strength,
            "access_level": access_analysis.get("level", "unknown"),
            "sensitive_access": sensitive_access,
            "role_risk_factors": access_analysis.get("risk_factors", []),
            "desk_sensitivity": access_analysis.get("desk_sensitivity", "low")
        }
    
    def _filter_person_trades(
        self, 
        person_id: str, 
        trade_data: List[RawTradeData], 
        time_window_hours: int
    ) -> List[RawTradeData]:
        """Filter trades belonging to the person within time window"""
        
        person_accounts = self.entity_resolution.identity_graph.get_person_accounts(person_id)
        if not person_accounts:
            return []
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        person_trades = []
        for trade in trade_data:
            # Check if trade belongs to person's accounts
            if trade.trader_id in person_accounts:
                # Check time window
                try:
                    trade_time = datetime.fromisoformat(trade.execution_timestamp.replace('Z', '+00:00'))
                    if trade_time >= cutoff_time:
                        person_trades.append(trade)
                except (ValueError, AttributeError):
                    # Include trade if timestamp parsing fails
                    person_trades.append(trade)
        
        return person_trades
    
    def _filter_person_communications(
        self, 
        person_id: str, 
        communication_data: List[Dict[str, Any]], 
        time_window_hours: int
    ) -> List[Dict[str, Any]]:
        """Filter communications belonging to the person within time window"""
        
        person_identity = self._get_person_identity(person_id)
        if not person_identity:
            return []
        
        person_identifiers = person_identity.get_all_identifiers()
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        person_comms = []
        for comm in communication_data:
            # Check if communication involves person
            if (comm.get("sender_email") in person_identity.linked_emails or
                comm.get("sender_handle") in person_identity.linked_comm_handles or
                comm.get("sender_id") in person_identity.linked_accounts):
                
                # Check time window
                try:
                    comm_time = datetime.fromisoformat(comm.get("timestamp", "").replace('Z', '+00:00'))
                    if comm_time >= cutoff_time:
                        person_comms.append(comm)
                except (ValueError, AttributeError):
                    person_comms.append(comm)
        
        return person_comms
    
    def _analyze_cross_account_patterns(self, trades_by_account: Dict[str, List[RawTradeData]]) -> Dict[str, Any]:
        """Analyze patterns across multiple accounts"""
        
        if len(trades_by_account) <= 1:
            return {"correlation": 0.0, "synchronized_activity": False, "pattern_strength": 0.0}
        
        # Analyze timing correlations between accounts
        timing_correlations = self._calculate_timing_correlations(trades_by_account)
        
        # Analyze instrument correlations
        instrument_correlations = self._calculate_instrument_correlations(trades_by_account)
        
        # Detect synchronized activity
        synchronized_activity = self._detect_synchronized_activity(trades_by_account)
        
        # Calculate overall pattern strength
        pattern_strength = (timing_correlations + instrument_correlations) / 2
        
        return {
            "correlation": pattern_strength,
            "synchronized_activity": synchronized_activity,
            "pattern_strength": pattern_strength,
            "timing_correlation": timing_correlations,
            "instrument_correlation": instrument_correlations
        }
    
    def _calculate_cross_account_correlations(
        self, 
        person_id: str, 
        trade_data: List[RawTradeData]
    ) -> Dict[str, float]:
        """Calculate correlations between different accounts"""
        
        person_trades = self._filter_person_trades(person_id, trade_data, 24)  # 24-hour window
        
        if len(person_trades) < 2:
            return {}
        
        # Group by account
        trades_by_account = defaultdict(list)
        for trade in person_trades:
            trades_by_account[trade.trader_id].append(trade)
        
        if len(trades_by_account) <= 1:
            return {}
        
        correlations = {}
        accounts = list(trades_by_account.keys())
        
        for i, account1 in enumerate(accounts):
            for account2 in accounts[i+1:]:
                corr_key = f"{account1}_{account2}"
                correlation = self._calculate_account_pair_correlation(
                    trades_by_account[account1], 
                    trades_by_account[account2]
                )
                correlations[corr_key] = correlation
        
        return correlations
    
    def _calculate_account_pair_correlation(
        self, 
        trades1: List[RawTradeData], 
        trades2: List[RawTradeData]
    ) -> float:
        """Calculate correlation between two accounts' trading patterns"""
        
        if not trades1 or not trades2:
            return 0.0
        
        # Simple correlation based on timing and instruments
        timing_correlation = self._calculate_timing_correlation_pair(trades1, trades2)
        instrument_correlation = self._calculate_instrument_correlation_pair(trades1, trades2)
        
        return (timing_correlation + instrument_correlation) / 2
    
    def _calculate_timing_correlations(self, trades_by_account: Dict[str, List[RawTradeData]]) -> float:
        """Calculate timing correlations across accounts"""
        
        accounts = list(trades_by_account.keys())
        if len(accounts) <= 1:
            return 0.0
        
        correlations = []
        for i, account1 in enumerate(accounts):
            for account2 in accounts[i+1:]:
                corr = self._calculate_timing_correlation_pair(
                    trades_by_account[account1], 
                    trades_by_account[account2]
                )
                correlations.append(corr)
        
        return np.mean(correlations) if correlations else 0.0
    
    def _calculate_timing_correlation_pair(
        self, 
        trades1: List[RawTradeData], 
        trades2: List[RawTradeData]
    ) -> float:
        """Calculate timing correlation between two trade lists"""
        
        if not trades1 or not trades2:
            return 0.0
        
        # Convert timestamps to minutes since epoch for correlation
        def to_minutes(timestamp_str):
            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                return dt.timestamp() / 60
            except:
                return 0
        
        times1 = [to_minutes(t.execution_timestamp) for t in trades1]
        times2 = [to_minutes(t.execution_timestamp) for t in trades2]
        
        # Simple correlation: check for trades within same time windows
        correlation_count = 0
        total_comparisons = 0
        
        for t1 in times1:
            for t2 in times2:
                total_comparisons += 1
                if abs(t1 - t2) <= 5:  # Within 5 minutes
                    correlation_count += 1
        
        return correlation_count / total_comparisons if total_comparisons > 0 else 0.0
    
    def _calculate_instrument_correlations(self, trades_by_account: Dict[str, List[RawTradeData]]) -> float:
        """Calculate instrument correlations across accounts"""
        
        accounts = list(trades_by_account.keys())
        if len(accounts) <= 1:
            return 0.0
        
        correlations = []
        for i, account1 in enumerate(accounts):
            for account2 in accounts[i+1:]:
                corr = self._calculate_instrument_correlation_pair(
                    trades_by_account[account1], 
                    trades_by_account[account2]
                )
                correlations.append(corr)
        
        return np.mean(correlations) if correlations else 0.0
    
    def _calculate_instrument_correlation_pair(
        self, 
        trades1: List[RawTradeData], 
        trades2: List[RawTradeData]
    ) -> float:
        """Calculate instrument overlap between two trade lists"""
        
        if not trades1 or not trades2:
            return 0.0
        
        instruments1 = set(t.symbol for t in trades1)
        instruments2 = set(t.symbol for t in trades2)
        
        if not instruments1 or not instruments2:
            return 0.0
        
        intersection = instruments1.intersection(instruments2)
        union = instruments1.union(instruments2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _detect_synchronized_activity(self, trades_by_account: Dict[str, List[RawTradeData]]) -> bool:
        """Detect synchronized trading activity across accounts"""
        
        if len(trades_by_account) <= 1:
            return False
        
        # Check for trades in same instruments within short time windows
        all_trades = []
        for account_trades in trades_by_account.values():
            all_trades.extend(account_trades)
        
        # Sort by timestamp
        all_trades.sort(key=lambda t: t.execution_timestamp)
        
        # Look for clusters of trades from different accounts
        synchronized_clusters = 0
        time_window = 300  # 5 minutes in seconds
        
        for i, trade in enumerate(all_trades):
            if i == 0:
                continue
                
            try:
                current_time = datetime.fromisoformat(trade.execution_timestamp.replace('Z', '+00:00'))
                prev_time = datetime.fromisoformat(all_trades[i-1].execution_timestamp.replace('Z', '+00:00'))
                
                time_diff = (current_time - prev_time).total_seconds()
                
                if (time_diff <= time_window and 
                    trade.trader_id != all_trades[i-1].trader_id and
                    trade.symbol == all_trades[i-1].symbol):
                    synchronized_clusters += 1
            except:
                continue
        
        return synchronized_clusters >= 2
    
    def _calculate_trading_pattern_strength(
        self, 
        person_trades: List[RawTradeData], 
        cross_account_patterns: Dict[str, Any]
    ) -> float:
        """Calculate overall trading pattern strength"""
        
        if not person_trades:
            return 0.0
        
        base_strength = min(len(person_trades) / 10, 1.0)  # Normalize by trade count
        cross_account_bonus = cross_account_patterns.get("pattern_strength", 0.0) * 0.5
        
        return min(base_strength + cross_account_bonus, 1.0)
    
    def _identify_suspicious_trading_patterns(
        self, 
        person_trades: List[RawTradeData], 
        cross_account_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify specific suspicious trading patterns"""
        
        patterns = {}
        
        # Large volume concentration
        total_volume = sum(t.quantity for t in person_trades)
        if total_volume > 100000:  # Threshold for large volume
            patterns["large_volume"] = {"detected": True, "volume": total_volume}
        
        # Rapid succession trading
        if len(person_trades) >= 5:
            patterns["rapid_succession"] = {"detected": True, "trade_count": len(person_trades)}
        
        # Cross-account coordination
        if cross_account_patterns.get("synchronized_activity", False):
            patterns["cross_account_coordination"] = {"detected": True}
        
        return patterns
    
    def _analyze_temporal_clustering(self, person_trades: List[RawTradeData]) -> Dict[str, Any]:
        """Analyze temporal clustering of trades"""
        
        if len(person_trades) < 3:
            return {"clustering_detected": False}
        
        # Convert timestamps and sort
        timestamps = []
        for trade in person_trades:
            try:
                dt = datetime.fromisoformat(trade.execution_timestamp.replace('Z', '+00:00'))
                timestamps.append(dt.timestamp())
            except:
                continue
        
        timestamps.sort()
        
        if len(timestamps) < 3:
            return {"clustering_detected": False}
        
        # Calculate time gaps
        gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_gap = np.mean(gaps)
        std_gap = np.std(gaps)
        
        # Detect clusters (gaps significantly smaller than average)
        cluster_threshold = avg_gap - std_gap if std_gap > 0 else avg_gap / 2
        clusters = sum(1 for gap in gaps if gap < cluster_threshold)
        
        return {
            "clustering_detected": clusters >= 2,
            "cluster_count": clusters,
            "avg_gap_seconds": avg_gap,
            "gap_std": std_gap
        }
    
    def _analyze_communication_patterns(self, person_comms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze communication patterns for suspicious activity"""
        
        if not person_comms:
            return {}
        
        patterns = {
            "volume": len(person_comms),
            "external_ratio": 0.0,
            "timing_patterns": {},
            "content_patterns": {}
        }
        
        # Calculate external communication ratio
        external_count = sum(1 for c in person_comms if c.get("external", False))
        patterns["external_ratio"] = external_count / len(person_comms)
        
        # Analyze timing patterns
        patterns["timing_patterns"] = self._analyze_communication_timing(person_comms)
        
        # Analyze content patterns
        patterns["content_patterns"] = self._analyze_communication_content(person_comms)
        
        return patterns
    
    def _analyze_communication_timing(self, person_comms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze timing patterns in communications"""
        
        if not person_comms:
            return {}
        
        # Extract timestamps
        timestamps = []
        for comm in person_comms:
            try:
                dt = datetime.fromisoformat(comm.get("timestamp", "").replace('Z', '+00:00'))
                timestamps.append(dt)
            except:
                continue
        
        if not timestamps:
            return {}
        
        timestamps.sort()
        
        # Analyze clustering
        if len(timestamps) >= 2:
            gaps = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
            avg_gap = np.mean(gaps)
            
            return {
                "avg_gap_minutes": avg_gap / 60,
                "burst_activity": sum(1 for gap in gaps if gap < 300),  # Within 5 minutes
                "total_communications": len(timestamps)
            }
        
        return {"total_communications": len(timestamps)}
    
    def _analyze_communication_content(self, person_comms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content patterns in communications"""
        
        if not person_comms:
            return {}
        
        # Simple keyword analysis
        sensitive_keywords = ["insider", "tip", "confidential", "material", "announcement", "merger", "earnings"]
        trading_keywords = ["buy", "sell", "trade", "position", "price", "target"]
        
        sensitive_count = 0
        trading_count = 0
        
        for comm in person_comms:
            content = comm.get("content", "").lower()
            if any(keyword in content for keyword in sensitive_keywords):
                sensitive_count += 1
            if any(keyword in content for keyword in trading_keywords):
                trading_count += 1
        
        return {
            "sensitive_content_ratio": sensitive_count / len(person_comms),
            "trading_content_ratio": trading_count / len(person_comms),
            "total_analyzed": len(person_comms)
        }
    
    def _detect_sensitive_communications(self, person_comms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect communications with sensitive content indicators"""
        
        sensitive_indicators = []
        sensitive_keywords = [
            "insider", "tip", "confidential", "material", "non-public",
            "announcement", "merger", "acquisition", "earnings", "guidance"
        ]
        
        for comm in person_comms:
            content = comm.get("content", "").lower()
            matched_keywords = [kw for kw in sensitive_keywords if kw in content]
            
            if matched_keywords:
                sensitive_indicators.append({
                    "communication_id": comm.get("id"),
                    "timestamp": comm.get("timestamp"),
                    "matched_keywords": matched_keywords,
                    "sensitivity_score": len(matched_keywords) / len(sensitive_keywords)
                })
        
        return sensitive_indicators
    
    def _calculate_communication_strength(
        self, 
        person_comms: List[Dict[str, Any]], 
        sensitive_indicators: List[Dict[str, Any]]
    ) -> float:
        """Calculate communication evidence strength"""
        
        if not person_comms:
            return 0.0
        
        base_strength = min(len(person_comms) / 20, 1.0)  # Normalize by communication count
        sensitivity_bonus = len(sensitive_indicators) / len(person_comms) * 0.5
        
        return min(base_strength + sensitivity_bonus, 1.0)
    
    def _analyze_timing_patterns(self, person_trades: List[RawTradeData]) -> Dict[str, Any]:
        """Analyze timing patterns in trades"""
        
        if not person_trades:
            return {}
        
        # Market hours analysis
        market_hours_trades = 0
        pre_market_trades = 0
        after_hours_trades = 0
        
        for trade in person_trades:
            try:
                dt = datetime.fromisoformat(trade.execution_timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                
                if 9 <= hour <= 16:  # Simplified market hours
                    market_hours_trades += 1
                elif hour < 9:
                    pre_market_trades += 1
                else:
                    after_hours_trades += 1
            except:
                continue
        
        total_trades = market_hours_trades + pre_market_trades + after_hours_trades
        
        return {
            "market_hours_ratio": market_hours_trades / total_trades if total_trades > 0 else 0,
            "pre_market_ratio": pre_market_trades / total_trades if total_trades > 0 else 0,
            "after_hours_ratio": after_hours_trades / total_trades if total_trades > 0 else 0,
            "total_analyzed": total_trades
        }
    
    def _detect_suspicious_timing(self, person_trades: List[RawTradeData]) -> List[Dict[str, Any]]:
        """Detect suspicious timing patterns"""
        
        suspicious_events = []
        
        # Check for pre-market trading (potential indicator)
        for trade in person_trades:
            try:
                dt = datetime.fromisoformat(trade.execution_timestamp.replace('Z', '+00:00'))
                if dt.hour < 9 or dt.hour > 16:  # Outside normal market hours
                    suspicious_events.append({
                        "trade_id": trade.trade_id,
                        "timestamp": trade.execution_timestamp,
                        "type": "off_hours_trading",
                        "risk_score": 0.6
                    })
            except:
                continue
        
        return suspicious_events
    
    def _calculate_timing_strength(
        self, 
        timing_patterns: Dict[str, Any], 
        suspicious_timing: List[Dict[str, Any]]
    ) -> float:
        """Calculate timing evidence strength"""
        
        base_strength = 0.0
        
        # Off-hours trading increases strength
        off_hours_ratio = timing_patterns.get("pre_market_ratio", 0) + timing_patterns.get("after_hours_ratio", 0)
        base_strength += off_hours_ratio * 0.7
        
        # Suspicious timing events
        if suspicious_timing:
            base_strength += len(suspicious_timing) / 10 * 0.3
        
        return min(base_strength, 1.0)
    
    def _analyze_cross_account_timing(self, person_trades: List[RawTradeData]) -> Dict[str, Any]:
        """Analyze timing synchronization across accounts"""
        
        if not person_trades:
            return {"synchronization_detected": False}
        
        # Group by account
        trades_by_account = defaultdict(list)
        for trade in person_trades:
            trades_by_account[trade.trader_id].append(trade)
        
        if len(trades_by_account) <= 1:
            return {"synchronization_detected": False}
        
        # Check for synchronized timing
        synchronized_pairs = 0
        total_pairs = 0
        
        accounts = list(trades_by_account.keys())
        for i, account1 in enumerate(accounts):
            for account2 in accounts[i+1:]:
                total_pairs += 1
                if self._check_account_timing_sync(trades_by_account[account1], trades_by_account[account2]):
                    synchronized_pairs += 1
        
        sync_ratio = synchronized_pairs / total_pairs if total_pairs > 0 else 0
        
        return {
            "synchronization_detected": sync_ratio > 0.5,
            "sync_ratio": sync_ratio,
            "synchronized_pairs": synchronized_pairs
        }
    
    def _check_account_timing_sync(
        self, 
        trades1: List[RawTradeData], 
        trades2: List[RawTradeData]
    ) -> bool:
        """Check if two accounts show timing synchronization"""
        
        if not trades1 or not trades2:
            return False
        
        # Check for trades within 5-minute windows
        sync_count = 0
        
        for trade1 in trades1:
            for trade2 in trades2:
                try:
                    dt1 = datetime.fromisoformat(trade1.execution_timestamp.replace('Z', '+00:00'))
                    dt2 = datetime.fromisoformat(trade2.execution_timestamp.replace('Z', '+00:00'))
                    
                    time_diff = abs((dt1 - dt2).total_seconds())
                    if time_diff <= 300:  # Within 5 minutes
                        sync_count += 1
                except:
                    continue
        
        return sync_count >= 2
    
    def _analyze_role_access(self, person_identity: PersonIdentity) -> Dict[str, Any]:
        """Analyze role-based access and risk factors"""
        
        if not person_identity.primary_role:
            return {"level": "unknown", "risk_factors": []}
        
        role = person_identity.primary_role.lower()
        
        # Define role risk levels
        high_risk_roles = ["executive", "head", "director", "chief", "portfolio_manager"]
        medium_risk_roles = ["senior_trader", "trader", "analyst", "sales"]
        
        risk_level = "low"
        risk_factors = []
        
        if any(hr_role in role for hr_role in high_risk_roles):
            risk_level = "high"
            risk_factors.append("senior_executive_role")
        elif any(mr_role in role for mr_role in medium_risk_roles):
            risk_level = "medium"
            risk_factors.append("trading_role")
        
        # Check desk sensitivity
        desk_sensitivity = "low"
        if person_identity.linked_desks:
            sensitive_desks = ["prop", "proprietary", "research", "investment_banking"]
            if any(any(sd in desk.lower() for sd in sensitive_desks) for desk in person_identity.linked_desks):
                desk_sensitivity = "high"
                risk_factors.append("sensitive_desk_access")
        
        return {
            "level": risk_level,
            "risk_factors": risk_factors,
            "desk_sensitivity": desk_sensitivity
        }
    
    def _check_sensitive_access(self, person_identity: PersonIdentity) -> bool:
        """Check if person has access to sensitive information"""
        
        if not person_identity.hr_records:
            return False
        
        # Check HR records for sensitive access indicators
        for hr_record in person_identity.hr_records:
            role = hr_record.get("role", "").lower()
            department = hr_record.get("department", "").lower()
            
            sensitive_indicators = [
                "research", "investment_banking", "proprietary", "executive",
                "compliance", "legal", "risk", "treasury"
            ]
            
            if any(indicator in role or indicator in department for indicator in sensitive_indicators):
                return True
        
        return False
    
    def _calculate_access_strength(
        self, 
        access_analysis: Dict[str, Any], 
        sensitive_access: bool
    ) -> float:
        """Calculate access evidence strength"""
        
        base_strength = 0.0
        
        # Role-based strength
        level = access_analysis.get("level", "low")
        if level == "high":
            base_strength += 0.6
        elif level == "medium":
            base_strength += 0.4
        else:
            base_strength += 0.2
        
        # Sensitive access bonus
        if sensitive_access:
            base_strength += 0.3
        
        # Risk factors bonus
        risk_factor_count = len(access_analysis.get("risk_factors", []))
        base_strength += min(risk_factor_count * 0.1, 0.2)
        
        return min(base_strength, 1.0)
    
    def _map_evidence_sources(
        self, 
        person_id: str, 
        trade_data: List[RawTradeData], 
        communication_data: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, List[str]]:
        """Map evidence sources for traceability"""
        
        sources = defaultdict(list)
        
        # Map trading data sources
        person_trades = self._filter_person_trades(person_id, trade_data, 24)
        for trade in person_trades:
            sources["trading_data"].append(trade.trade_id)
            sources["accounts"].append(trade.trader_id)
        
        # Map communication sources
        if communication_data:
            person_comms = self._filter_person_communications(person_id, communication_data, 24)
            for comm in person_comms:
                sources["communications"].append(comm.get("id", "unknown"))
        
        # Remove duplicates
        for key in sources:
            sources[key] = list(set(sources[key]))
        
        return dict(sources)
    
    def get_person_activity_summary(
        self, 
        person_id: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> PersonActivitySummary:
        """Generate activity summary for a person over a time period"""
        
        # This would integrate with the main data pipeline
        # For now, return a basic summary structure
        return PersonActivitySummary(
            person_id=person_id,
            time_period_start=start_time,
            time_period_end=end_time
        )
    
    def clear_evidence_cache(self, person_id: Optional[str] = None):
        """Clear evidence cache for a person or all persons"""
        if person_id:
            self.evidence_cache.pop(person_id, None)
        else:
            self.evidence_cache.clear()