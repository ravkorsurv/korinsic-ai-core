"""
Evidence Mapper for Kor.ai Bayesian Risk Engine
Maps raw input data/events to Bayesian Network evidence node states.
Supports multiple data sources: trades, market data, HR, sales, communications, PnL.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np


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
    if (
        access_level in ["executive", "board", "high"]
        or role in ["executive", "board_member", "cfo", "ceo"]
        or len(insider_indicators) > 2
    ):
        return 2  # clear_access

    # Check for potential access
    elif (
        access_level in ["senior", "medium"]
        or role in ["senior_trader", "analyst", "manager"]
        or len(insider_indicators) > 0
    ):
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
    if (market_direction > 0 and trade_direction < -0.3) or (
        market_direction < 0 and trade_direction > 0.3
    ):
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


def map_timing_proximity(
    trade_data: Dict[str, Any], market_data: Dict[str, Any]
) -> int:
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
            event_time = datetime.fromisoformat(event_time_str.replace("Z", "+00:00"))
            for trade in trades:
                trade_time_str = trade.get("timestamp")
                if not trade_time_str:
                    continue

                trade_time = datetime.fromisoformat(
                    trade_time_str.replace("Z", "+00:00")
                )
                time_diff = (event_time - trade_time).total_seconds() / (
                    24 * 3600
                )  # days

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


def map_market_news_context(
    market_data: Dict[str, Any], news_data: Dict[str, Any]
) -> int:
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
        if (
            abs(event_impact) > 0.005  # Event has significant expected impact
            and materiality > 0.7  # Event is material
            and (
                (price_movement > 0 and event_impact > 0)  # Both positive
                or (price_movement < 0 and event_impact < 0)
            )
        ):  # Both negative
            explained_moves += 1

    # Analyze news events
    for news in news_events:
        news_sentiment = news.get("sentiment", 0)  # -1 to 1 scale
        news_impact = news.get("market_impact", 0)
        news_relevance = news.get("relevance_score", 0)

        # Check if news explains price movement
        if (
            abs(news_impact) > 0.003  # News has significant impact
            and news_relevance > 0.6  # News is relevant
            and (
                (
                    price_movement > 0 and news_sentiment > 0.2
                )  # Positive news, positive move
                or (price_movement < 0 and news_sentiment < -0.2)
            )
        ):  # Negative news, negative move
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


def map_wash_trade_likelihood(
    trade_data: Dict[str, Any], counterparty_data: Dict[str, Any]
) -> int:
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


def map_signal_distortion_index(
    market_data: Dict[str, Any], trade_data: Dict[str, Any]
) -> int:
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


def map_algo_reaction_sensitivity(
    market_data: Dict[str, Any], trade_data: Dict[str, Any]
) -> int:
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


def map_strategy_leg_overlap(
    trade_data: Dict[str, Any], strategy_data: Dict[str, Any]
) -> int:
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


def map_price_impact_anomaly(
    market_data: Dict[str, Any], historical_data: Dict[str, Any]
) -> int:
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


def map_implied_liquidity_conflict(
    venue_data: Dict[str, Any], trade_data: Dict[str, Any]
) -> int:
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
        "mnpi_access": map_mnpi_access(
            raw_data.get("hr", {}), raw_data.get("market", {})
        ),
        "state_information_access": map_state_information_access(
            raw_data.get("state_information", {})
        ),
        "news_timing": map_news_timing(
            raw_data.get("trade", {}), raw_data.get("news", {})
        ),
        "trade_direction": map_trade_direction(
            raw_data.get("trade", {}), raw_data.get("market", {})
        ),
        "risk_profile": map_risk_profile(
            raw_data.get("hr", {}), raw_data.get("historical", {})
        ),
        "timing_proximity": map_timing_proximity(
            raw_data.get("trade", {}), raw_data.get("market", {})
        ),
        "pnl_loss_spike": map_pnl_loss_spike(raw_data.get("pnl", {})),
        "sales_activity": map_sales_activity(raw_data.get("sales", {})),
        "market_news_context": map_market_news_context(
            raw_data.get("market", {}), raw_data.get("news", {})
        ),
    }

    # Add wash trade detection evidence mapping
    if "wash_trade" in raw_data:
        wash_trade_evidence = map_wash_trade_evidence(raw_data["wash_trade"])
        evidence.update(wash_trade_evidence)

    # Add economic withholding evidence mapping
    if "economic_withholding" in raw_data:
        ew_evidence = map_economic_withholding_evidence(raw_data["economic_withholding"])
        evidence.update(ew_evidence)

    # Add spoofing evidence mapping
    if "spoofing" in raw_data:
        spoofing_evidence = map_spoofing_evidence(raw_data["spoofing"])
        evidence.update(spoofing_evidence)
    
    # Add market cornering evidence mapping
    if "market_cornering" in raw_data:
        cornering_evidence = map_market_cornering_evidence(raw_data["market_cornering"])
        evidence.update(cornering_evidence)
    
    # Add circular trading evidence mapping
    if "circular_trading" in raw_data:
        circular_evidence = map_circular_trading_evidence(raw_data["circular_trading"])
        evidence.update(circular_evidence)
    
    # Add cross-desk collusion evidence mapping
    if "cross_desk_collusion" in raw_data:
        collusion_evidence = map_cross_desk_collusion_evidence(raw_data["cross_desk_collusion"])
        evidence.update(collusion_evidence)
    
    # Add commodity manipulation evidence mapping
    if "commodity_manipulation" in raw_data:
        commodity_evidence = map_commodity_manipulation_evidence(raw_data["commodity_manipulation"])
        evidence.update(commodity_evidence)

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
        "wash_trade_likelihood": map_wash_trade_likelihood(
            trade_data, counterparty_data
        ),
        "signal_distortion_index": map_signal_distortion_index(market_data, trade_data),
        "algo_reaction_sensitivity": map_algo_reaction_sensitivity(
            market_data, trade_data
        ),
        "strategy_leg_overlap": map_strategy_leg_overlap(trade_data, strategy_data),
        "price_impact_anomaly": map_price_impact_anomaly(market_data, historical_data),
        "implied_liquidity_conflict": map_implied_liquidity_conflict(
            venue_data, trade_data
        ),
    }


# NEW: Economic Withholding Evidence Mappers

def map_fuel_cost_variance(plant_data: Dict[str, Any], cost_analysis: Dict[str, Any]) -> int:
    """
    Map fuel cost variance evidence from plant and cost analysis data.
    Returns 0 for 'aligned', 1 for 'moderate_variance', 2 for 'high_variance'.
    """
    if not cost_analysis:
        return 0  # Default to aligned
    
    anomalies = cost_analysis.get('anomaly_detection', {})
    fuel_anomalies = anomalies.get('fuel_cost_anomalies', [])
    
    if any(a.get('severity') == 'high' for a in fuel_anomalies):
        return 2  # high_variance
    elif fuel_anomalies:
        return 1  # moderate_variance
    return 0  # aligned


def map_plant_efficiency(plant_data: Dict[str, Any], cost_analysis: Dict[str, Any]) -> int:
    """
    Map plant efficiency evidence.
    Returns 0 for 'optimal', 1 for 'suboptimal', 2 for 'significantly_impaired'.
    """
    if not cost_analysis:
        return 0  # Default to optimal
    
    anomalies = cost_analysis.get('anomaly_detection', {})
    efficiency_anomalies = anomalies.get('efficiency_anomalies', [])
    
    if any(a.get('severity') == 'high' for a in efficiency_anomalies):
        return 2  # significantly_impaired
    elif efficiency_anomalies:
        return 1  # suboptimal
    return 0  # optimal


def map_marginal_cost_deviation(counterfactual_results: Dict[str, Any]) -> int:
    """
    Map marginal cost deviation evidence.
    Returns 0 for 'cost_reflective', 1 for 'moderate_markup', 2 for 'excessive_markup'.
    """
    if not counterfactual_results or 'comparisons' not in counterfactual_results:
        return 0  # Default to cost_reflective
    
    comparisons = counterfactual_results['comparisons']
    if not comparisons:
        return 0
    
    avg_markup = max(comp.get('average_markup', 0) for comp in comparisons)
    
    if avg_markup > 0.20:
        return 2  # excessive_markup
    elif avg_markup > 0.10:
        return 1  # moderate_markup
    return 0  # cost_reflective


def map_heat_rate_variance(plant_data: Dict[str, Any], operational_data: Dict[str, Any]) -> int:
    """
    Map heat rate variance evidence.
    Returns 0 for 'consistent', 1 for 'moderate_variance', 2 for 'significant_variance'.
    """
    # Extract heat rate variance from operational data if available
    variance = operational_data.get('heat_rate_variance', 0) if operational_data else 0
    
    if variance > 0.15:  # More than 15% variance
        return 2  # significant_variance
    elif variance > 0.05:  # More than 5% variance
        return 1  # moderate_variance
    return 0  # consistent


def map_load_factor(market_data: Dict[str, Any]) -> int:
    """
    Map system load factor evidence.
    Returns 0 for 'low_demand', 1 for 'normal_demand', 2 for 'peak_demand'.
    """
    load_factor = market_data.get('load_factor', 'normal_demand')
    
    # Handle both string and numeric load factor
    if isinstance(load_factor, str):
        if load_factor == 'peak_demand':
            return 2
        elif load_factor == 'normal_demand':
            return 1
        else:  # low_demand
            return 0
    else:
        # Numeric load factor (percentage)
        if load_factor > 0.85:
            return 2  # peak_demand
        elif load_factor > 0.5:
            return 1  # normal_demand
        else:
            return 0  # low_demand


def map_market_tightness(market_data: Dict[str, Any]) -> int:
    """
    Map market tightness evidence.
    Returns 0 for 'surplus', 1 for 'balanced', 2 for 'tight'.
    """
    tightness = market_data.get('market_tightness', 'balanced')
    
    if isinstance(tightness, str):
        if tightness == 'tight':
            return 2
        elif tightness == 'balanced':
            return 1
        else:  # surplus
            return 0
    else:
        # Numeric reserve margin
        if tightness < 0.1:  # Less than 10% reserve
            return 2  # tight
        elif tightness < 0.2:  # Less than 20% reserve
            return 1  # balanced
        else:
            return 0  # surplus


def map_competitive_context(market_data: Dict[str, Any]) -> int:
    """
    Map competitive context evidence.
    Returns 0 for 'competitive', 1 for 'concentrated', 2 for 'monopolistic'.
    """
    # Could use HHI or market concentration metrics
    hhi = market_data.get('hhi', 0)
    
    if hhi > 2500:
        return 2  # monopolistic
    elif hhi > 1500:
        return 1  # concentrated
    return 0  # competitive


def map_transmission_constraint(market_data: Dict[str, Any]) -> int:
    """
    Map transmission constraint evidence.
    Returns 0 for 'unconstrained', 1 for 'moderate_constraints', 2 for 'severe_constraints'.
    """
    constraints = market_data.get('transmission_constraints', 'unconstrained')
    
    if isinstance(constraints, str):
        if constraints == 'severe_constraints':
            return 2
        elif constraints == 'moderate_constraints':
            return 1
        else:
            return 0
    else:
        # Numeric congestion level
        if constraints > 0.7:
            return 2  # severe_constraints
        elif constraints > 0.3:
            return 1  # moderate_constraints
        else:
            return 0  # unconstrained


def map_bid_shape_anomaly(bid_analysis: Dict[str, Any]) -> int:
    """
    Map bid shape anomaly evidence.
    Returns 0 for 'normal_curve', 1 for 'stepped_curve', 2 for 'manipulative_curve'.
    """
    if not bid_analysis:
        return 0
    
    anomaly_score = bid_analysis.get('anomaly_score', 0)
    curve_type = bid_analysis.get('curve_type', 'normal')
    
    if anomaly_score > 0.8 or curve_type == 'manipulative':
        return 2  # manipulative_curve
    elif anomaly_score > 0.5 or curve_type == 'stepped':
        return 1  # stepped_curve
    return 0  # normal_curve


def map_offer_withdrawal_pattern(withdrawal_data: Dict[str, Any]) -> int:
    """
    Map offer withdrawal pattern evidence.
    Returns 0 for 'normal_availability', 1 for 'selective_withdrawal', 2 for 'systematic_withholding'.
    """
    if not withdrawal_data:
        return 0
    
    withdrawal_rate = withdrawal_data.get('withdrawal_rate', 0)
    pattern_score = withdrawal_data.get('pattern_score', 0)
    
    if withdrawal_rate > 0.3 or pattern_score > 0.8:
        return 2  # systematic_withholding
    elif withdrawal_rate > 0.15 or pattern_score > 0.5:
        return 1  # selective_withdrawal
    return 0  # normal_availability


def map_cross_plant_coordination(coordination_data: Dict[str, Any]) -> int:
    """
    Map cross-plant coordination evidence.
    Returns 0 for 'independent_operation', 1 for 'coordinated_operation', 2 for 'systematic_coordination'.
    """
    if not coordination_data:
        return 0
    
    correlation_score = coordination_data.get('correlation_score', 0)
    coordination_events = coordination_data.get('coordination_events', 0)
    
    if correlation_score > 0.8 or coordination_events > 5:
        return 2  # systematic_coordination
    elif correlation_score > 0.5 or coordination_events > 2:
        return 1  # coordinated_operation
    return 0  # independent_operation


def map_capacity_utilization(plant_data: Dict[str, Any], operational_data: Dict[str, Any]) -> int:
    """
    Map capacity utilization evidence.
    Returns 0 for 'full_utilization', 1 for 'partial_utilization', 2 for 'artificial_limitation'.
    """
    if not operational_data:
        return 0
    
    utilization_rate = operational_data.get('utilization_rate', 1.0)
    artificial_limit_detected = operational_data.get('artificial_limit_detected', False)
    
    if artificial_limit_detected or utilization_rate < 0.5:
        return 2  # artificial_limitation
    elif utilization_rate < 0.8:
        return 1  # partial_utilization
    return 0  # full_utilization


def map_markup_consistency(pricing_data: Dict[str, Any]) -> int:
    """
    Map markup consistency evidence.
    Returns 0 for 'consistent_markup', 1 for 'variable_markup', 2 for 'strategic_markup'.
    """
    if not pricing_data:
        return 0
    
    markup_variance = pricing_data.get('markup_variance', 0)
    strategic_pattern = pricing_data.get('strategic_pattern_detected', False)
    
    if strategic_pattern or markup_variance > 0.5:
        return 2  # strategic_markup
    elif markup_variance > 0.2:
        return 1  # variable_markup
    return 0  # consistent_markup


def map_opportunity_pricing(pricing_data: Dict[str, Any], market_data: Dict[str, Any]) -> int:
    """
    Map opportunity pricing evidence.
    Returns 0 for 'cost_based', 1 for 'opportunistic', 2 for 'exploitative'.
    """
    if not pricing_data:
        return 0
    
    price_spike_ratio = pricing_data.get('price_spike_ratio', 1.0)
    scarcity_pricing = pricing_data.get('scarcity_pricing_detected', False)
    
    if scarcity_pricing and price_spike_ratio > 3.0:
        return 2  # exploitative
    elif price_spike_ratio > 1.5:
        return 1  # opportunistic
    return 0  # cost_based


def map_fuel_price_correlation(pricing_data: Dict[str, Any], fuel_prices: Dict[str, float]) -> int:
    """
    Map fuel price correlation evidence.
    Returns 0 for 'strong_correlation', 1 for 'weak_correlation', 2 for 'no_correlation'.
    """
    if not pricing_data:
        return 0  # Default to strong correlation
    
    correlation_coefficient = pricing_data.get('fuel_price_correlation', 1.0)
    
    if abs(correlation_coefficient) < 0.3:
        return 2  # no_correlation
    elif abs(correlation_coefficient) < 0.7:
        return 1  # weak_correlation
    return 0  # strong_correlation


def map_economic_withholding_evidence(ew_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Map economic withholding specific evidence from raw data.
    Returns a dict: {node_name: state_index} for economic withholding nodes.
    """
    plant_data = ew_data.get('plant_data', {})
    market_data = ew_data.get('market_data', {})
    cost_analysis = ew_data.get('cost_analysis', {})
    counterfactual_results = ew_data.get('counterfactual_results', {})
    operational_data = ew_data.get('operational_data', {})
    bid_analysis = ew_data.get('bid_analysis', {})
    withdrawal_data = ew_data.get('withdrawal_data', {})
    coordination_data = ew_data.get('coordination_data', {})
    pricing_data = ew_data.get('pricing_data', {})
    fuel_prices = ew_data.get('fuel_prices', {})
    
    return {
        "fuel_cost_variance": map_fuel_cost_variance(plant_data, cost_analysis),
        "plant_efficiency": map_plant_efficiency(plant_data, cost_analysis),
        "marginal_cost_deviation": map_marginal_cost_deviation(counterfactual_results),
        "heat_rate_variance": map_heat_rate_variance(plant_data, operational_data),
        "load_factor": map_load_factor(market_data),
        "market_tightness": map_market_tightness(market_data),
        "competitive_context": map_competitive_context(market_data),
        "transmission_constraint": map_transmission_constraint(market_data),
        "bid_shape_anomaly": map_bid_shape_anomaly(bid_analysis),
        "offer_withdrawal_pattern": map_offer_withdrawal_pattern(withdrawal_data),
        "cross_plant_coordination": map_cross_plant_coordination(coordination_data),
        "capacity_utilization": map_capacity_utilization(plant_data, operational_data),
        "markup_consistency": map_markup_consistency(pricing_data),
        "opportunity_pricing": map_opportunity_pricing(pricing_data, market_data),
        "fuel_price_correlation": map_fuel_price_correlation(pricing_data, fuel_prices),
        # Note: Reused nodes from other models (already mapped)
        "price_impact_ratio": map_price_impact_ratio(market_data, {}, {}),
        "volume_participation": map_volume_participation(ew_data.get('trade', {}), market_data),
        "liquidity_context": map_liquidity_context(market_data, ew_data.get('venue', {})),
        "order_clustering": map_order_clustering(ew_data.get('trade', {}), market_data),
        "benchmark_timing": map_benchmark_timing(ew_data.get('trade', {}), market_data),
    }


# NEW: Spoofing Evidence Mappers

def map_order_behavior(order_data: Dict[str, Any]) -> int:
    """
    Map order behavior evidence.
    Returns 0 for 'normal_behavior', 1 for 'unusual_behavior', 2 for 'suspicious_behavior'.
    """
    if not order_data:
        return 0
    
    # Check for suspicious patterns
    rapid_modifications = order_data.get('rapid_modification_count', 0)
    layer_count = order_data.get('order_layer_count', 0)
    price_deviation = order_data.get('price_deviation_from_mid', 0)
    
    if rapid_modifications > 10 or layer_count > 5 or abs(price_deviation) > 0.05:
        return 2  # suspicious_behavior
    elif rapid_modifications > 5 or layer_count > 3 or abs(price_deviation) > 0.02:
        return 1  # unusual_behavior
    return 0  # normal_behavior


def map_intent_to_execute(order_data: Dict[str, Any], execution_data: Dict[str, Any]) -> int:
    """
    Map intent to execute evidence.
    Returns 0 for 'genuine_intent', 1 for 'uncertain_intent', 2 for 'no_intent'.
    """
    if not order_data:
        return 0
    
    fill_rate = execution_data.get('fill_rate', 1.0) if execution_data else 1.0
    cancel_rate = order_data.get('cancellation_rate', 0)
    time_to_cancel = order_data.get('avg_time_to_cancel_ms', float('inf'))
    
    if cancel_rate > 0.9 or time_to_cancel < 100:
        return 2  # no_intent
    elif cancel_rate > 0.7 or time_to_cancel < 500:
        return 1  # uncertain_intent
    return 0  # genuine_intent


def map_order_cancellation(order_data: Dict[str, Any]) -> int:
    """
    Map order cancellation pattern evidence.
    Returns 0 for 'normal_cancellation', 1 for 'suspicious_cancellation', 2 for 'manipulative_cancellation'.
    """
    if not order_data:
        return 0
    
    cancel_rate = order_data.get('cancellation_rate', 0)
    rapid_cancels = order_data.get('rapid_cancel_count', 0)
    cancel_after_price_move = order_data.get('cancel_after_price_move_rate', 0)
    
    if cancel_rate > 0.95 or rapid_cancels > 20 or cancel_after_price_move > 0.8:
        return 2  # manipulative_cancellation
    elif cancel_rate > 0.8 or rapid_cancels > 10 or cancel_after_price_move > 0.5:
        return 1  # suspicious_cancellation
    return 0  # normal_cancellation


def map_spoofing_evidence(spoofing_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Map spoofing specific evidence from raw data.
    Returns a dict: {node_name: state_index} for spoofing nodes.
    """
    order_data = spoofing_data.get('order_data', {})
    market_data = spoofing_data.get('market_data', {})
    execution_data = spoofing_data.get('execution_data', {})
    trade_data = spoofing_data.get('trade_data', {})
    
    return {
        "order_clustering": map_order_clustering(order_data, market_data),
        "price_impact_ratio": map_price_impact_ratio(market_data, {}, {}),
        "volume_participation": map_volume_participation(trade_data, market_data),
        "order_behavior": map_order_behavior(order_data),
        "intent_to_execute": map_intent_to_execute(order_data, execution_data),
        "order_cancellation": map_order_cancellation(order_data),
    }


# NEW: Market Cornering Evidence Mappers

def map_market_concentration(position_data: Dict[str, Any], market_data: Dict[str, Any]) -> int:
    """
    Map market concentration evidence.
    Returns 0 for 'dispersed', 1 for 'concentrated', 2 for 'highly_concentrated'.
    """
    concentration_ratio = position_data.get('concentration_ratio', 0) if position_data else 0
    hhi = market_data.get('herfindahl_index', 0) if market_data else 0
    top_holder_share = position_data.get('top_holder_share', 0) if position_data else 0
    
    if concentration_ratio > 0.7 or hhi > 3000 or top_holder_share > 0.5:
        return 2  # highly_concentrated
    elif concentration_ratio > 0.4 or hhi > 1800 or top_holder_share > 0.3:
        return 1  # concentrated
    return 0  # dispersed


def map_position_accumulation(position_data: Dict[str, Any], trading_data: Dict[str, Any]) -> int:
    """
    Map position accumulation pattern evidence.
    Returns 0 for 'normal_accumulation', 1 for 'systematic_accumulation', 2 for 'aggressive_accumulation'.
    """
    if not position_data:
        return 0
    
    accumulation_rate = position_data.get('accumulation_rate', 0)
    position_growth = position_data.get('position_growth_rate', 0)
    stealth_trading = trading_data.get('stealth_trading_score', 0) if trading_data else 0
    
    if accumulation_rate > 0.8 or position_growth > 0.5 or stealth_trading > 0.7:
        return 2  # aggressive_accumulation
    elif accumulation_rate > 0.5 or position_growth > 0.3 or stealth_trading > 0.4:
        return 1  # systematic_accumulation
    return 0  # normal_accumulation


def map_supply_control(position_data: Dict[str, Any], delivery_data: Dict[str, Any]) -> int:
    """
    Map supply control evidence.
    Returns 0 for 'limited_control', 1 for 'significant_control', 2 for 'dominant_control'.
    """
    position_pct = position_data.get('position_percentage', 0) if position_data else 0
    deliverable_pct = delivery_data.get('deliverable_control_pct', 0) if delivery_data else 0
    warehouse_control = delivery_data.get('warehouse_control_pct', 0) if delivery_data else 0
    
    if position_pct > 0.6 or deliverable_pct > 0.7 or warehouse_control > 0.5:
        return 2  # dominant_control
    elif position_pct > 0.3 or deliverable_pct > 0.4 or warehouse_control > 0.3:
        return 1  # significant_control
    return 0  # limited_control


def map_liquidity_manipulation(market_data: Dict[str, Any], trading_data: Dict[str, Any]) -> int:
    """
    Map liquidity manipulation evidence.
    Returns 0 for 'normal_liquidity', 1 for 'constrained_liquidity', 2 for 'manipulated_liquidity'.
    """
    bid_ask_spread = market_data.get('bid_ask_spread', 0) if market_data else 0
    liquidity_ratio = market_data.get('liquidity_ratio', 1) if market_data else 1
    quote_stuffing = trading_data.get('quote_stuffing_score', 0) if trading_data else 0
    
    if bid_ask_spread > 0.05 or liquidity_ratio < 0.2 or quote_stuffing > 0.7:
        return 2  # manipulated_liquidity
    elif bid_ask_spread > 0.02 or liquidity_ratio < 0.5 or quote_stuffing > 0.4:
        return 1  # constrained_liquidity
    return 0  # normal_liquidity


def map_price_distortion(market_data: Dict[str, Any], benchmark_data: Dict[str, Any]) -> int:
    """
    Map price distortion evidence.
    Returns 0 for 'fair_pricing', 1 for 'moderate_distortion', 2 for 'extreme_distortion'.
    """
    price_deviation = market_data.get('price_deviation_from_fair', 0) if market_data else 0
    volatility_spike = market_data.get('volatility_spike', 0) if market_data else 0
    benchmark_deviation = benchmark_data.get('benchmark_deviation', 0) if benchmark_data else 0
    
    if abs(price_deviation) > 0.1 or volatility_spike > 3 or abs(benchmark_deviation) > 0.15:
        return 2  # extreme_distortion
    elif abs(price_deviation) > 0.05 or volatility_spike > 2 or abs(benchmark_deviation) > 0.08:
        return 1  # moderate_distortion
    return 0  # fair_pricing


def map_delivery_constraint(delivery_data: Dict[str, Any], futures_data: Dict[str, Any]) -> int:
    """
    Map delivery constraint evidence.
    Returns 0 for 'normal_delivery', 1 for 'constrained_delivery', 2 for 'blocked_delivery'.
    """
    delivery_squeeze = delivery_data.get('delivery_squeeze_indicator', 0) if delivery_data else 0
    warehouse_queues = delivery_data.get('warehouse_queue_days', 0) if delivery_data else 0
    futures_convergence = futures_data.get('convergence_failure', False) if futures_data else False
    
    if delivery_squeeze > 0.8 or warehouse_queues > 30 or futures_convergence:
        return 2  # blocked_delivery
    elif delivery_squeeze > 0.5 or warehouse_queues > 14:
        return 1  # constrained_delivery
    return 0  # normal_delivery


def map_market_cornering_evidence(cornering_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Map market cornering specific evidence from raw data.
    Returns a dict: {node_name: state_index} for market cornering nodes.
    """
    position_data = cornering_data.get('position_data', {})
    market_data = cornering_data.get('market_data', {})
    trading_data = cornering_data.get('trading_data', {})
    delivery_data = cornering_data.get('delivery_data', {})
    benchmark_data = cornering_data.get('benchmark_data', {})
    futures_data = cornering_data.get('futures_data', {})
    
    return {
        "market_concentration": map_market_concentration(position_data, market_data),
        "position_accumulation": map_position_accumulation(position_data, trading_data),
        "supply_control": map_supply_control(position_data, delivery_data),
        "liquidity_manipulation": map_liquidity_manipulation(market_data, trading_data),
        "price_distortion": map_price_distortion(market_data, benchmark_data),
        "delivery_constraint": map_delivery_constraint(delivery_data, futures_data),
    }


# NEW: Circular Trading Evidence Mappers

def map_counterparty_relationship(counterparty_data: Dict[str, Any]) -> int:
    """
    Map counterparty relationship evidence.
    Returns 0 for 'unrelated', 1 for 'connected', 2 for 'closely_related'.
    """
    if not counterparty_data:
        return 0
    
    common_ownership = counterparty_data.get('common_ownership_pct', 0)
    shared_addresses = counterparty_data.get('shared_addresses', False)
    historical_correlation = counterparty_data.get('trading_correlation', 0)
    
    if common_ownership > 0.5 or shared_addresses or historical_correlation > 0.8:
        return 2  # closely_related
    elif common_ownership > 0.2 or historical_correlation > 0.5:
        return 1  # connected
    return 0  # unrelated


def map_risk_transfer_analysis(trade_data: Dict[str, Any], position_data: Dict[str, Any]) -> int:
    """
    Map risk transfer analysis evidence.
    Returns 0 for 'genuine_transfer', 1 for 'limited_transfer', 2 for 'no_transfer'.
    """
    net_position_change = position_data.get('net_position_change', 1) if position_data else 1
    risk_reduction = trade_data.get('risk_reduction_score', 1) if trade_data else 1
    hedge_effectiveness = trade_data.get('hedge_effectiveness', 1) if trade_data else 1
    
    if abs(net_position_change) < 0.1 or risk_reduction < 0.2 or hedge_effectiveness < 0.3:
        return 2  # no_transfer
    elif abs(net_position_change) < 0.5 or risk_reduction < 0.5 or hedge_effectiveness < 0.6:
        return 1  # limited_transfer
    return 0  # genuine_transfer


def map_price_negotiation_pattern(trade_data: Dict[str, Any], market_data: Dict[str, Any]) -> int:
    """
    Map price negotiation pattern evidence.
    Returns 0 for 'market_driven', 1 for 'coordinated', 2 for 'artificial'.
    """
    price_improvement = trade_data.get('price_improvement_rate', 0) if trade_data else 0
    spread_capture = trade_data.get('spread_capture_pct', 0) if trade_data else 0
    market_deviation = abs(trade_data.get('price_vs_market', 0)) if trade_data else 0
    
    if price_improvement < 0.1 or spread_capture > 0.8 or market_deviation > 0.05:
        return 2  # artificial
    elif price_improvement < 0.3 or spread_capture > 0.5 or market_deviation > 0.02:
        return 1  # coordinated
    return 0  # market_driven


def map_settlement_coordination(settlement_data: Dict[str, Any]) -> int:
    """
    Map settlement coordination patterns evidence.
    Returns 0 for 'independent', 1 for 'synchronized', 2 for 'coordinated'.
    """
    if not settlement_data:
        return 0
    
    timing_correlation = settlement_data.get('settlement_timing_correlation', 0)
    matched_settlements = settlement_data.get('matched_settlement_pct', 0)
    fail_correlation = settlement_data.get('fail_correlation', 0)
    
    if timing_correlation > 0.9 or matched_settlements > 0.8 or fail_correlation > 0.7:
        return 2  # coordinated
    elif timing_correlation > 0.6 or matched_settlements > 0.5 or fail_correlation > 0.4:
        return 1  # synchronized
    return 0  # independent


def map_beneficial_ownership(ownership_data: Dict[str, Any]) -> int:
    """
    Map beneficial ownership evidence.
    Returns 0 for 'separate_ownership', 1 for 'shared_interests', 2 for 'common_ownership'.
    """
    if not ownership_data:
        return 0
    
    ultimate_beneficiary_match = ownership_data.get('ultimate_beneficiary_match', False)
    ownership_overlap = ownership_data.get('ownership_overlap_pct', 0)
    control_person_match = ownership_data.get('control_person_match', False)
    
    if ultimate_beneficiary_match or ownership_overlap > 0.5 or control_person_match:
        return 2  # common_ownership
    elif ownership_overlap > 0.2:
        return 1  # shared_interests
    return 0  # separate_ownership


def map_trade_sequence_analysis(trade_data: Dict[str, Any], pattern_data: Dict[str, Any]) -> int:
    """
    Map trade sequence analysis evidence.
    Returns 0 for 'random_sequence', 1 for 'structured_sequence', 2 for 'circular_sequence'.
    """
    sequence_score = pattern_data.get('sequence_pattern_score', 0) if pattern_data else 0
    circularity_index = pattern_data.get('circularity_index', 0) if pattern_data else 0
    repetition_rate = trade_data.get('pattern_repetition_rate', 0) if trade_data else 0
    
    if sequence_score > 0.8 or circularity_index > 0.7 or repetition_rate > 0.6:
        return 2  # circular_sequence
    elif sequence_score > 0.5 or circularity_index > 0.4 or repetition_rate > 0.3:
        return 1  # structured_sequence
    return 0  # random_sequence


def map_circular_trading_evidence(circular_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Map circular trading specific evidence from raw data.
    Returns a dict: {node_name: state_index} for circular trading nodes.
    """
    counterparty_data = circular_data.get('counterparty_data', {})
    trade_data = circular_data.get('trade_data', {})
    position_data = circular_data.get('position_data', {})
    market_data = circular_data.get('market_data', {})
    settlement_data = circular_data.get('settlement_data', {})
    ownership_data = circular_data.get('ownership_data', {})
    pattern_data = circular_data.get('pattern_data', {})
    
    return {
        "counterparty_relationship": map_counterparty_relationship(counterparty_data),
        "risk_transfer_analysis": map_risk_transfer_analysis(trade_data, position_data),
        "price_negotiation_pattern": map_price_negotiation_pattern(trade_data, market_data),
        "settlement_coordination": map_settlement_coordination(settlement_data),
        "beneficial_ownership": map_beneficial_ownership(ownership_data),
        "trade_sequence_analysis": map_trade_sequence_analysis(trade_data, pattern_data),
    }


# NEW: Cross-Desk Collusion Evidence Mappers

def map_comms_metadata(comms_data: Dict[str, Any]) -> int:
    """
    Map cross-desk communication patterns evidence.
    Returns 0 for 'normal_comms', 1 for 'unusual_comms', 2 for 'suspicious_comms'.
    """
    if not comms_data:
        return 0
    
    cross_desk_freq = comms_data.get('cross_desk_comm_frequency', 0)
    timing_correlation = comms_data.get('comm_trade_timing_correlation', 0)
    encrypted_ratio = comms_data.get('encrypted_comm_ratio', 0)
    
    if cross_desk_freq > 50 or timing_correlation > 0.8 or encrypted_ratio > 0.7:
        return 2  # suspicious_comms
    elif cross_desk_freq > 20 or timing_correlation > 0.5 or encrypted_ratio > 0.4:
        return 1  # unusual_comms
    return 0  # normal_comms


def map_profit_motivation(pnl_data: Dict[str, Any], trade_data: Dict[str, Any]) -> int:
    """
    Map profit motivation evidence (already defined above, but adding for completeness).
    Returns 0 for 'normal_profit', 1 for 'unusual_profit', 2 for 'suspicious_profit'.
    """
    if not pnl_data:
        return 0
    
    profit_concentration = pnl_data.get('profit_concentration', 0)
    win_rate = pnl_data.get('win_rate', 0.5)
    profit_correlation = pnl_data.get('cross_desk_profit_correlation', 0)
    
    if profit_concentration > 0.8 or win_rate > 0.9 or profit_correlation > 0.8:
        return 2  # suspicious_profit
    elif profit_concentration > 0.6 or win_rate > 0.75 or profit_correlation > 0.5:
        return 1  # unusual_profit
    return 0  # normal_profit


def map_access_pattern(access_data: Dict[str, Any], system_data: Dict[str, Any]) -> int:
    """
    Map information access pattern evidence.
    Returns 0 for 'normal_access', 1 for 'unusual_access', 2 for 'suspicious_access'.
    """
    shared_access = access_data.get('shared_system_access', 0) if access_data else 0
    data_overlap = access_data.get('data_query_overlap', 0) if access_data else 0
    timing_anomaly = system_data.get('access_timing_anomaly', 0) if system_data else 0
    
    if shared_access > 0.7 or data_overlap > 0.8 or timing_anomaly > 0.7:
        return 2  # suspicious_access
    elif shared_access > 0.4 or data_overlap > 0.5 or timing_anomaly > 0.4:
        return 1  # unusual_access
    return 0  # normal_access


def map_market_segmentation(market_data: Dict[str, Any], trade_data: Dict[str, Any]) -> int:
    """
    Map market segmentation evidence.
    Returns 0 for 'competitive', 1 for 'segmented', 2 for 'coordinated_division'.
    """
    overlap_ratio = trade_data.get('desk_overlap_ratio', 1) if trade_data else 1
    territory_score = market_data.get('territory_division_score', 0) if market_data else 0
    competition_index = market_data.get('inter_desk_competition', 1) if market_data else 1
    
    if overlap_ratio < 0.1 or territory_score > 0.8 or competition_index < 0.2:
        return 2  # coordinated_division
    elif overlap_ratio < 0.3 or territory_score > 0.5 or competition_index < 0.5:
        return 1  # segmented
    return 0  # competitive


def map_cross_desk_collusion_evidence(collusion_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Map cross-desk collusion specific evidence from raw data.
    Returns a dict: {node_name: state_index} for cross-desk collusion nodes.
    """
    comms_data = collusion_data.get('comms_data', {})
    pnl_data = collusion_data.get('pnl_data', {})
    order_data = collusion_data.get('order_data', {})
    trade_data = collusion_data.get('trade_data', {})
    venue_data = collusion_data.get('venue_data', {})
    access_data = collusion_data.get('access_data', {})
    system_data = collusion_data.get('system_data', {})
    market_data = collusion_data.get('market_data', {})
    
    return {
        "comms_metadata": map_comms_metadata(comms_data),
        "profit_motivation": map_profit_motivation(pnl_data, trade_data),
        "order_behavior": map_order_behavior(order_data),
        "cross_venue_coordination": map_cross_venue_coordination(venue_data),
        "access_pattern": map_access_pattern(access_data, system_data),
        "market_segmentation": map_market_segmentation(market_data, trade_data),
    }


# Note: Commodity manipulation reuses several nodes already defined:
# - liquidity_context (from economic withholding)
# - benchmark_timing (from economic withholding)
# - order_clustering (from spoofing)
# - price_impact_ratio (from economic withholding/spoofing)
# - volume_participation (from economic withholding/spoofing)
# - cross_venue_coordination (from cross-desk collusion)

def map_commodity_manipulation_evidence(commodity_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Map commodity manipulation specific evidence from raw data.
    Returns a dict: {node_name: state_index} for commodity manipulation nodes.
    """
    market_data = commodity_data.get('market_data', {})
    trade_data = commodity_data.get('trade_data', {})
    venue_data = commodity_data.get('venue_data', {})
    order_data = commodity_data.get('order_data', {})
    
    return {
        "liquidity_context": map_liquidity_context(market_data, venue_data),
        "benchmark_timing": map_benchmark_timing(trade_data, market_data),
        "order_clustering": map_order_clustering(order_data, market_data),
        "price_impact_ratio": map_price_impact_ratio(market_data, {}, {}),
        "volume_participation": map_volume_participation(trade_data, market_data),
        "cross_venue_coordination": map_cross_venue_coordination(venue_data),
    }


def map_state_information_access(state_data: Dict[str, Any]) -> int:
    """
    Map state information access indicators to BN state index.
    Returns 0 for 'no_access', 1 for 'potential_access', 2 for 'clear_access'.
    """
    # Simple heuristic: treat strong signals as clear, weak as potential
    indicators = state_data.get("indicators", 0)
    access_flags = state_data.get("access_flags", [])
    if indicators >= 2 or "privileged_channel" in access_flags:
        return 2
    if indicators >= 1 or "sensitive_meeting" in access_flags:
        return 1
    return 0


def map_news_timing(trade_data: Dict[str, Any], news_data: Dict[str, Any]) -> int:
    """
    Map trade-news timing proximity to BN state index.
    Returns 0 'normal_timing', 1 'suspicious_timing', 2 'highly_suspicious_timing'.
    """
    # Heuristic: use minutes to nearest price-sensitive news
    trades = trade_data.get("trades", [])
    news_events = news_data.get("events", [])
    if not trades or not news_events:
        return 0
    min_minutes = 9999
    for t in trades:
        tt = t.get("timestamp")
        if tt is None:
            continue
        for ev in news_events:
            if not ev.get("price_sensitive", True):
                continue
            nv = ev.get("timestamp")
            if nv is None:
                continue
            try:
                dt = abs((nv - tt).total_seconds()) / 60.0
            except Exception:
                continue
            if dt < min_minutes:
                min_minutes = dt
    if min_minutes <= 5:
        return 2
    if min_minutes <= 60:
        return 1
    return 0
