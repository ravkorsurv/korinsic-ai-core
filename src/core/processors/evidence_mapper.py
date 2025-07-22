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


def map_evidence(raw_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Map all raw input data to evidence node state indices for the BN.
    Returns a dict: {node_name: state_index}
    """
    return {
        "trade_pattern": map_trade_pattern(raw_data.get("trade", {})),
        "comms_intent": map_comms_intent(raw_data.get("comms", {})),
        "pnl_drift": map_pnl_drift(raw_data.get("pnl", {})),
        "mnpi_access": map_mnpi_access(
            raw_data.get("hr", {}), raw_data.get("market", {})
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
