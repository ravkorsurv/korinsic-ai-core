"""
Evidence Mapper for Kor.ai Bayesian Risk Engine
Maps raw input data/events to Bayesian Network evidence node states.
Supports multiple data sources: trades, market data, HR, sales, communications, PnL.
"""

from typing import Dict, Any, List
import numpy as np
from datetime import datetime, timedelta

def map_trade_pattern(trade_data: Dict[str, Any]) -> int:
    """
    Map raw trade data to trade_pattern node state index.
    Returns 0 for 'normal', 1 for 'suspicious'.
    """
    # Example logic: Replace with real business rules
    if trade_data.get("suspicious_flag", False):
        return 1  # suspicious
    return 0  # normal

def map_comms_intent(comms_data: Dict[str, Any]) -> int:
    """
    Map raw comms data to comms_intent node state index.
    Returns 0 for 'benign', 1 for 'suspicious', 2 for 'malicious'.
    """
    # Example logic: Replace with real NLP/intent detection
    intent = comms_data.get("intent", "benign")
    if intent == "malicious":
        return 2
    elif intent == "suspicious":
        return 1
    return 0

def map_pnl_drift(pnl_data: Dict[str, Any]) -> int:
    """
    Map raw PnL data to pnl_drift node state index.
    Returns 0 for 'normal', 1 for 'anomalous'.
    """
    # Example logic: Replace with real statistical test
    if abs(pnl_data.get("drift", 0)) > pnl_data.get("threshold", 10000):
        return 1  # anomalous
    return 0  # normal

def map_mnpi_access(hr_data: Dict[str, Any], market_data: Dict[str, Any]) -> int:
    """
    Map HR and market data to MNPI access node state.
    Returns 0 for 'no_access', 1 for 'potential_access', 2 for 'clear_access'.
    """
    access_level = hr_data.get("access_level", "standard")
    role = hr_data.get("role", "trader")
    insider_indicators = hr_data.get("insider_indicators", [])
    
    # Check for clear access indicators
    if (access_level in ["executive", "board", "high"] or 
        role in ["executive", "board_member", "cfo", "ceo"] or
        len(insider_indicators) > 2):
        return 2  # clear_access
    
    # Check for potential access
    elif (access_level in ["senior", "medium"] or 
          role in ["senior_trader", "analyst", "manager"] or
          len(insider_indicators) > 0):
        return 1  # potential_access
    
    return 0  # no_access

def map_trade_direction(trade_data: Dict[str, Any], market_data: Dict[str, Any]) -> int:
    """
    Map trade direction relative to market movement.
    Returns 0 for 'aligned', 1 for 'neutral', 2 for 'contrarian'.
    """
    trades = trade_data.get("trades", [])
    if not trades:
        return 1  # neutral
    
    market_direction = market_data.get("price_movement", 0)
    if market_direction == 0:
        return 1  # neutral
    
    # Calculate average trade direction
    buy_volume = sum(t.get("volume", 0) for t in trades if t.get("side") == "buy")
    sell_volume = sum(t.get("volume", 0) for t in trades if t.get("side") == "sell")
    
    if buy_volume == 0 and sell_volume == 0:
        return 1  # neutral
    
    trade_direction = (buy_volume - sell_volume) / (buy_volume + sell_volume)
    
    # Check if trade direction is contrarian to market
    if (market_direction > 0 and trade_direction < -0.3) or (market_direction < 0 and trade_direction > 0.3):
        return 2  # contrarian
    elif abs(trade_direction) < 0.1:
        return 1  # neutral
    else:
        return 0  # aligned

def map_risk_profile(hr_data: Dict[str, Any], historical_data: Dict[str, Any]) -> int:
    """
    Map known risk profile based on HR and historical data.
    Returns 0 for 'low_risk', 1 for 'medium_risk', 2 for 'high_risk'.
    """
    risk_score = 0
    
    # HR risk factors
    disciplinary_actions = hr_data.get("disciplinary_actions", 0)
    risk_score += disciplinary_actions * 2
    
    compliance_violations = hr_data.get("compliance_violations", 0)
    risk_score += compliance_violations * 3
    
    # Historical risk factors
    historical_alerts = historical_data.get("alert_count", 0)
    risk_score += min(historical_alerts, 5)
    
    if risk_score >= 8:
        return 2  # high_risk
    elif risk_score >= 4:
        return 1  # medium_risk
    return 0  # low_risk

def map_timing_proximity(trade_data: Dict[str, Any], market_data: Dict[str, Any]) -> int:
    """
    Map timing proximity to material events.
    Returns 0 for 'normal', 1 for 'suspicious', 2 for 'highly_suspicious'.
    """
    material_events = market_data.get("material_events", [])
    trades = trade_data.get("trades", [])
    
    if not material_events or not trades:
        return 0
    
    suspicious_count = 0
    for event in material_events:
        event_time_str = event.get("timestamp")
        if not event_time_str:
            continue
            
        try:
            event_time = datetime.fromisoformat(event_time_str.replace('Z', '+00:00'))
            for trade in trades:
                trade_time_str = trade.get("timestamp")
                if not trade_time_str:
                    continue
                    
                trade_time = datetime.fromisoformat(trade_time_str.replace('Z', '+00:00'))
                time_diff = (event_time - trade_time).total_seconds() / (24 * 3600)  # days
                
                # Suspicious if trade within 1-7 days before material event
                if 1 <= time_diff <= 7:
                    suspicious_count += 1
        except (ValueError, TypeError):
            continue
    
    if suspicious_count > 3:
        return 2  # highly_suspicious
    elif suspicious_count > 0:
        return 1  # suspicious
    return 0  # normal

def map_pnl_loss_spike(pnl_data: Dict[str, Any]) -> int:
    """
    Map recent PnL spike that resulted in a loss.
    Returns 0 for 'no_spike', 1 for 'small_loss', 2 for 'large_loss'.
    """
    recent_pnl = pnl_data.get("recent_pnl", [])
    if not recent_pnl:
        return 0
    
    # Calculate PnL volatility and check for loss spikes
    pnl_values = [float(p.get("value", 0)) for p in recent_pnl]
    if not pnl_values:
        return 0
    
    # Check for recent losses
    recent_losses = [p for p in pnl_values if p < 0]
    if not recent_losses:
        return 0
    
    # Calculate loss magnitude
    max_loss = abs(min(recent_losses))
    avg_pnl = np.mean([abs(p) for p in pnl_values])
    
    if max_loss > avg_pnl * 3:
        return 2  # large_loss
    elif max_loss > avg_pnl * 1.5:
        return 1  # small_loss
    return 0  # no_spike

def map_sales_activity(sales_data: Dict[str, Any]) -> int:
    """
    Map sales activity for unusual patterns.
    Returns 0 for 'normal', 1 for 'unusual', 2 for 'highly_unusual'.
    """
    client_activity = sales_data.get("client_activity", {})
    unusual_clients = client_activity.get("unusual_count", 0)
    activity_volume = client_activity.get("volume_change", 0)
    
    if unusual_clients > 5 or abs(activity_volume) > 0.5:
        return 2  # highly_unusual
    elif unusual_clients > 2 or abs(activity_volume) > 0.2:
        return 1  # unusual
    return 0  # normal

def map_market_news_context(market_data: Dict[str, Any], news_data: Dict[str, Any]) -> int:
    """
    Map market news contextualization to suppress false alerts when price movements are explained by public events.
    Returns 0 for 'explained_move', 1 for 'partially_explained', 2 for 'unexplained_move'.
    
    This implements the "explained move suppressor" node to reduce false alerts.
    """
    price_movement = market_data.get("price_movement", 0)
    material_events = market_data.get("material_events", [])
    news_events = news_data.get("news_events", [])
    
    if abs(price_movement) < 0.01:  # Less than 1% movement
        return 0  # explained_move (no significant movement)
    
    # Check if price movement aligns with expected direction from news/events
    explained_moves = 0
    total_events = len(material_events) + len(news_events)
    
    if total_events == 0:
        return 2  # unexplained_move (no events to explain movement)
    
    # Analyze material events
    for event in material_events:
        event_type = event.get("type", "")
        event_impact = event.get("expected_impact", 0)  # Expected price impact
        materiality = event.get("materiality_score", 0)
        
        # Check if event explains price movement
        if (abs(event_impact) > 0.005 and  # Event has significant expected impact
            materiality > 0.7 and  # Event is material
            ((price_movement > 0 and event_impact > 0) or  # Both positive
             (price_movement < 0 and event_impact < 0))):   # Both negative
            explained_moves += 1
    
    # Analyze news events
    for news in news_events:
        news_sentiment = news.get("sentiment", 0)  # -1 to 1 scale
        news_impact = news.get("market_impact", 0)
        news_relevance = news.get("relevance_score", 0)
        
        # Check if news explains price movement
        if (abs(news_impact) > 0.003 and  # News has significant impact
            news_relevance > 0.6 and  # News is relevant
            ((price_movement > 0 and news_sentiment > 0.2) or  # Positive news, positive move
             (price_movement < 0 and news_sentiment < -0.2))):  # Negative news, negative move
            explained_moves += 1
    
    # Calculate explanation ratio
    explanation_ratio = explained_moves / total_events if total_events > 0 else 0
    
    if explanation_ratio >= 0.7:
        return 0  # explained_move (most movement explained by events)
    elif explanation_ratio >= 0.3:
        return 1  # partially_explained (some movement explained)
    else:
        return 2  # unexplained_move (little to no explanation)

# NEW: Wash Trade Detection Evidence Mappers

def map_wash_trade_likelihood(trade_data: Dict[str, Any], counterparty_data: Dict[str, Any]) -> int:
    """
    Map wash trade likelihood evidence from trade and counterparty data.
    Returns 0 for 'low_probability', 1 for 'medium_probability', 2 for 'high_probability'.
    """
    likelihood_score = 0.0
    
    # LEI exact match (strongest indicator)
    lei_match = counterparty_data.get("lei_exact_match", False)
    if lei_match:
        likelihood_score += 0.4
    elif counterparty_data.get("lei_affiliate_match", False):
        likelihood_score += 0.3
    
    # Same entity trading
    same_entity = counterparty_data.get("same_entity_flag", False)
    if same_entity:
        likelihood_score += 0.3
    
    # Algorithmic framework match
    algo_match = trade_data.get("algo_framework_match", 0)
    likelihood_score += algo_match * 0.15
    
    # Time delta (simultaneous trades)
    time_delta = trade_data.get("time_delta_ms", 1000)
    if time_delta < 1:
        likelihood_score += 0.1
    elif time_delta < 100:
        likelihood_score += 0.05
    
    # Strategy execution flags
    strategy_flags = trade_data.get("strategy_execution_flags", [])
    if any(flag in ["implied_strategy", "time_spread"] for flag in strategy_flags):
        likelihood_score += 0.05
    
    if likelihood_score >= 0.7:
        return 2  # high_probability
    elif likelihood_score >= 0.4:
        return 1  # medium_probability
    return 0  # low_probability

def map_signal_distortion_index(market_data: Dict[str, Any], trade_data: Dict[str, Any]) -> int:
    """
    Map signal distortion index from order book and trade data.
    Returns 0 for 'minimal_distortion', 1 for 'moderate_distortion', 2 for 'high_distortion'.
    """
    distortion_score = 0.0
    
    # Order book impact
    pre_orderbook = market_data.get("pre_trade_orderbook", {})
    post_orderbook = market_data.get("post_trade_orderbook", {})
    
    if pre_orderbook and post_orderbook:
        # Volume at best bid/ask change
        pre_volume = pre_orderbook.get("volume_at_best", 0)
        post_volume = post_orderbook.get("volume_at_best", 0)
        if pre_volume > 0:
            volume_change = abs(post_volume - pre_volume) / pre_volume
            distortion_score += min(volume_change, 0.3)
        
        # Order book imbalance change
        pre_imbalance = pre_orderbook.get("imbalance", 0)
        post_imbalance = post_orderbook.get("imbalance", 0)
        imbalance_change = abs(post_imbalance - pre_imbalance)
        distortion_score += min(imbalance_change * 0.5, 0.25)
    
    # Quote frequency distortion (flickering)
    quote_freq_ratio = market_data.get("quote_frequency_ratio", 1.0)
    if quote_freq_ratio > 2.0:
        distortion_score += min((quote_freq_ratio - 1.0) / 4.0, 0.2)
    
    # Spread manipulation
    spread_change = market_data.get("spread_change_ratio", 0)
    if abs(spread_change) > 0.15:
        distortion_score += min(abs(spread_change), 0.15)
    
    # Price volatility spike
    volatility_spike = market_data.get("short_term_volatility_spike", 0)
    distortion_score += min(volatility_spike * 0.1, 0.1)
    
    if distortion_score >= 0.6:
        return 2  # high_distortion
    elif distortion_score >= 0.3:
        return 1  # moderate_distortion
    return 0  # minimal_distortion

def map_algo_reaction_sensitivity(market_data: Dict[str, Any], trade_data: Dict[str, Any]) -> int:
    """
    Map algorithmic reaction sensitivity from post-trade market behavior.
    Returns 0 for 'low_sensitivity', 1 for 'medium_sensitivity', 2 for 'high_sensitivity'.
    """
    sensitivity_score = 0.0
    
    # Reaction time delta (< 100ms is suspicious)
    reaction_time = market_data.get("algo_reaction_time_ms", 1000)
    if reaction_time < 50:
        sensitivity_score += 0.3
    elif reaction_time < 100:
        sensitivity_score += 0.2
    elif reaction_time < 500:
        sensitivity_score += 0.1
    
    # Order flow clustering after trade
    order_clustering = market_data.get("order_clustering_ratio", 0)
    sensitivity_score += min(order_clustering * 0.25, 0.25)
    
    # Passive/aggressive quoting ratio changes
    pa_ratio_change = market_data.get("passive_aggressive_ratio_change", 0)
    sensitivity_score += min(abs(pa_ratio_change) * 0.2, 0.2)
    
    # Volume participation changes
    volume_participation_change = market_data.get("volume_participation_change", 0)
    sensitivity_score += min(abs(volume_participation_change) * 0.15, 0.15)
    
    # Number of algorithms reacting
    reacting_algos = market_data.get("reacting_algorithms_count", 0)
    sensitivity_score += min(reacting_algos * 0.05, 0.1)
    
    if sensitivity_score >= 0.65:
        return 2  # high_sensitivity
    elif sensitivity_score >= 0.35:
        return 1  # medium_sensitivity
    return 0  # low_sensitivity

def map_strategy_leg_overlap(trade_data: Dict[str, Any], strategy_data: Dict[str, Any]) -> int:
    """
    Map strategy leg overlap for commodity derivatives and multi-leg trades.
    Returns 0 for 'no_overlap', 1 for 'partial_overlap', 2 for 'full_overlap'.
    """
    overlap_score = 0.0
    
    # Time spread detection (commodity derivatives)
    time_spread_detected = strategy_data.get("time_spread_detected", False)
    if time_spread_detected:
        overlap_score += 0.2
    
    # Cross-contract matching
    cross_contract_ratio = strategy_data.get("cross_contract_matching_ratio", 0)
    overlap_score += cross_contract_ratio * 0.25
    
    # Same entity leg matching
    same_entity_legs = strategy_data.get("same_entity_legs_ratio", 0)
    overlap_score += same_entity_legs * 0.3
    
    # Third-party risk validation (should be low for wash trades)
    third_party_risk = strategy_data.get("third_party_risk_transfer", 1.0)
    if third_party_risk < 0.3:  # Low risk transfer = high overlap
        overlap_score += 0.2
    
    # Leg execution timing correlation
    leg_timing_correlation = strategy_data.get("leg_timing_correlation", 0)
    overlap_score += min(leg_timing_correlation * 0.15, 0.15)
    
    if overlap_score >= 0.7:
        return 2  # full_overlap
    elif overlap_score >= 0.4:
        return 1  # partial_overlap
    return 0  # no_overlap

def map_price_impact_anomaly(market_data: Dict[str, Any], historical_data: Dict[str, Any]) -> int:
    """
    Map price impact anomaly from price movement patterns.
    Returns 0 for 'normal_impact', 1 for 'unusual_impact', 2 for 'anomalous_impact'.
    """
    anomaly_score = 0.0
    
    # Immediate mean reversion (within 10-60 seconds)
    reversion_time = market_data.get("mean_reversion_time_seconds", 300)
    if reversion_time < 10:
        anomaly_score += 0.35
    elif reversion_time < 30:
        anomaly_score += 0.2
    elif reversion_time < 60:
        anomaly_score += 0.1
    
    # Price spike/fade magnitude
    price_spike = market_data.get("price_spike_magnitude", 0)
    if price_spike > 0.02:  # > 2% spike
        anomaly_score += min(price_spike * 5, 0.3)
    
    # Volatility baseline deviation
    volatility_z_score = market_data.get("volatility_z_score", 0)
    if abs(volatility_z_score) > 3.0:  # Extreme deviation
        anomaly_score += min(abs(volatility_z_score) / 10, 0.2)
    
    # Volume vs price impact ratio anomaly
    volume_impact_ratio = market_data.get("volume_price_impact_ratio", 1.0)
    expected_ratio = historical_data.get("average_volume_impact_ratio", 1.0)
    if expected_ratio > 0:
        ratio_deviation = abs(volume_impact_ratio - expected_ratio) / expected_ratio
        if ratio_deviation > 0.5:  # 50% deviation from expected
            anomaly_score += min(ratio_deviation * 0.2, 0.15)
    
    if anomaly_score >= 0.7:
        return 2  # anomalous_impact
    elif anomaly_score >= 0.4:
        return 1  # unusual_impact
    return 0  # normal_impact

def map_implied_liquidity_conflict(venue_data: Dict[str, Any], trade_data: Dict[str, Any]) -> int:
    """
    Map implied liquidity conflicts from venue-level matching facilities.
    Returns 0 for 'no_conflict', 1 for 'potential_conflict', 2 for 'clear_conflict'.
    """
    conflict_score = 0.0
    
    # Venue implied matching facility usage
    implied_matching_used = venue_data.get("implied_matching_facility_used", False)
    if implied_matching_used:
        conflict_score += 0.2
    
    # Internal book vs external execution
    internal_execution_ratio = venue_data.get("internal_execution_ratio", 0)
    if internal_execution_ratio > 0.7:  # High internal execution
        conflict_score += internal_execution_ratio * 0.3
    
    # Strategy order vs single-month contract interaction
    strategy_interaction = venue_data.get("strategy_single_month_interaction", False)
    if strategy_interaction:
        conflict_score += 0.25
    
    # Leg execution source analysis
    leg_execution_sources = venue_data.get("leg_execution_sources", [])
    internal_legs = len([s for s in leg_execution_sources if s == "internal"])
    total_legs = len(leg_execution_sources)
    if total_legs > 0 and internal_legs / total_legs > 0.6:
        conflict_score += 0.2
    
    # Artificial matching detection
    artificial_matching_indicators = venue_data.get("artificial_matching_indicators", 0)
    conflict_score += min(artificial_matching_indicators * 0.1, 0.15)
    
    if conflict_score >= 0.75:
        return 2  # clear_conflict
    elif conflict_score >= 0.4:
        return 1  # potential_conflict
    return 0  # no_conflict

def map_evidence(raw_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Map all raw input data to evidence node state indices for the BN.
    Returns a dict: {node_name: state_index}
    """
    evidence = {
        "trade_pattern": map_trade_pattern(raw_data.get("trade", {})),
        "comms_intent": map_comms_intent(raw_data.get("comms", {})),
        "pnl_drift": map_pnl_drift(raw_data.get("pnl", {})),
        "mnpi_access": map_mnpi_access(raw_data.get("hr", {}), raw_data.get("market", {})),
        "trade_direction": map_trade_direction(raw_data.get("trade", {}), raw_data.get("market", {})),
        "risk_profile": map_risk_profile(raw_data.get("hr", {}), raw_data.get("historical", {})),
        "timing_proximity": map_timing_proximity(raw_data.get("trade", {}), raw_data.get("market", {})),
        "pnl_loss_spike": map_pnl_loss_spike(raw_data.get("pnl", {})),
        "sales_activity": map_sales_activity(raw_data.get("sales", {})),
        "market_news_context": map_market_news_context(raw_data.get("market", {}), raw_data.get("news", {})),
    }
    
    # Add wash trade detection evidence mapping
    if "wash_trade" in raw_data:
        wash_trade_evidence = map_wash_trade_evidence(raw_data["wash_trade"])
        evidence.update(wash_trade_evidence)
    
    return evidence

def map_wash_trade_evidence(wash_trade_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Map wash trade specific evidence from raw data.
    Returns a dict: {node_name: state_index} for wash trade nodes.
    """
    trade_data = wash_trade_data.get("trade", {})
    counterparty_data = wash_trade_data.get("counterparty", {})
    market_data = wash_trade_data.get("market", {})
    strategy_data = wash_trade_data.get("strategy", {})
    venue_data = wash_trade_data.get("venue", {})
    historical_data = wash_trade_data.get("historical", {})
    
    return {
        "wash_trade_likelihood": map_wash_trade_likelihood(trade_data, counterparty_data),
        "signal_distortion_index": map_signal_distortion_index(market_data, trade_data),
        "algo_reaction_sensitivity": map_algo_reaction_sensitivity(market_data, trade_data),
        "strategy_leg_overlap": map_strategy_leg_overlap(trade_data, strategy_data),
        "price_impact_anomaly": map_price_impact_anomaly(market_data, historical_data),
        "implied_liquidity_conflict": map_implied_liquidity_conflict(venue_data, trade_data)
    } 