"""
Trading Data Models for Raw Trading Data Analysis

This module contains comprehensive data models for raw trading data
that analysts need to investigate alerts and perform detailed analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class TradeDirection(Enum):
    """Trade direction enumeration"""

    BUY = "buy"
    SELL = "sell"
    UNKNOWN = "unknown"


class OrderStatus(Enum):
    """Order status enumeration"""

    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class RawTradeData:
    """
    Comprehensive raw trade data structure for analyst investigations
    """

    # Core trade identifiers (required fields)
    trade_id: str
    execution_timestamp: str
    instrument: str
    instrument_type: str  # equity, future, option, etc.
    symbol: str
    exchange: str
    direction: TradeDirection
    quantity: float
    executed_price: float
    notional_value: float
    trader_id: str

    # Optional fields
    order_id: Optional[str] = None
    parent_order_id: Optional[str] = None
    settlement_date: Optional[str] = None

    # Market data context
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    mid_price: Optional[float] = None
    spread: Optional[float] = None
    market_volume: Optional[float] = None

    # Trader context
    trader_name: Optional[str] = None
    trader_role: Optional[str] = None
    desk: Optional[str] = None
    book: Optional[str] = None

    # Risk and compliance
    position_before: Optional[float] = None
    position_after: Optional[float] = None
    pnl_realized: Optional[float] = None
    pnl_unrealized: Optional[float] = None

    # Timing analysis
    order_timestamp: Optional[str] = None
    time_to_execution: Optional[float] = None  # seconds
    market_session: Optional[str] = None  # pre-market, regular, after-hours

    # Additional context
    counterparty: Optional[str] = None
    commission: Optional[float] = None
    fees: Optional[float] = None
    reference_price: Optional[float] = None  # closing price, vwap, etc.
    price_deviation: Optional[float] = None  # deviation from reference

    # Alert correlation
    alert_ids: List[str] = field(default_factory=list)
    risk_score: Optional[float] = None

    # Metadata
    data_source: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "parent_order_id": self.parent_order_id,
            "execution_timestamp": self.execution_timestamp,
            "settlement_date": self.settlement_date,
            "instrument": self.instrument,
            "instrument_type": self.instrument_type,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "direction": self.direction.value,
            "quantity": self.quantity,
            "executed_price": self.executed_price,
            "notional_value": self.notional_value,
            "bid_price": self.bid_price,
            "ask_price": self.ask_price,
            "mid_price": self.mid_price,
            "spread": self.spread,
            "market_volume": self.market_volume,
            "trader_id": self.trader_id,
            "trader_name": self.trader_name,
            "trader_role": self.trader_role,
            "desk": self.desk,
            "book": self.book,
            "position_before": self.position_before,
            "position_after": self.position_after,
            "pnl_realized": self.pnl_realized,
            "pnl_unrealized": self.pnl_unrealized,
            "order_timestamp": self.order_timestamp,
            "time_to_execution": self.time_to_execution,
            "market_session": self.market_session,
            "counterparty": self.counterparty,
            "commission": self.commission,
            "fees": self.fees,
            "reference_price": self.reference_price,
            "price_deviation": self.price_deviation,
            "alert_ids": self.alert_ids,
            "risk_score": self.risk_score,
            "data_source": self.data_source,
            "created_at": self.created_at,
        }


@dataclass
class RawOrderData:
    """
    Comprehensive raw order data structure for analyst investigations
    """

    # Required fields
    order_id: str
    order_timestamp: str
    status: OrderStatus
    instrument: str
    instrument_type: str
    symbol: str
    exchange: str
    side: TradeDirection
    order_type: str  # market, limit, stop, etc.
    quantity: float
    filled_quantity: float
    remaining_quantity: float
    trader_id: str

    # Optional fields
    parent_order_id: Optional[str] = None
    client_order_id: Optional[str] = None
    last_update_timestamp: Optional[str] = None

    # Price details
    order_price: Optional[float] = None
    avg_fill_price: Optional[float] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None

    # Execution details
    fills: List[str] = field(default_factory=list)  # List of trade IDs
    partial_fills: int = 0

    # Timing analysis
    time_in_force: Optional[str] = None  # GTC, FOK, IOC, DAY
    expiry_timestamp: Optional[str] = None
    cancellation_timestamp: Optional[str] = None
    cancellation_reason: Optional[str] = None

    # Market context
    bid_at_order: Optional[float] = None
    ask_at_order: Optional[float] = None
    mid_at_order: Optional[float] = None

    # Trader context
    trader_name: Optional[str] = None
    strategy: Optional[str] = None

    # Risk and compliance
    notional_value: Optional[float] = None
    margin_requirement: Optional[float] = None

    # Alert correlation
    alert_ids: List[str] = field(default_factory=list)
    risk_indicators: List[str] = field(default_factory=list)

    # Metadata
    data_source: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "order_id": self.order_id,
            "parent_order_id": self.parent_order_id,
            "client_order_id": self.client_order_id,
            "order_timestamp": self.order_timestamp,
            "status": self.status.value,
            "last_update_timestamp": self.last_update_timestamp,
            "instrument": self.instrument,
            "instrument_type": self.instrument_type,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "side": self.side.value,
            "order_type": self.order_type,
            "quantity": self.quantity,
            "filled_quantity": self.filled_quantity,
            "remaining_quantity": self.remaining_quantity,
            "order_price": self.order_price,
            "avg_fill_price": self.avg_fill_price,
            "limit_price": self.limit_price,
            "stop_price": self.stop_price,
            "fills": self.fills,
            "partial_fills": self.partial_fills,
            "time_in_force": self.time_in_force,
            "expiry_timestamp": self.expiry_timestamp,
            "cancellation_timestamp": self.cancellation_timestamp,
            "cancellation_reason": self.cancellation_reason,
            "bid_at_order": self.bid_at_order,
            "ask_at_order": self.ask_at_order,
            "mid_at_order": self.mid_at_order,
            "trader_id": self.trader_id,
            "trader_name": self.trader_name,
            "strategy": self.strategy,
            "notional_value": self.notional_value,
            "margin_requirement": self.margin_requirement,
            "alert_ids": self.alert_ids,
            "risk_indicators": self.risk_indicators,
            "data_source": self.data_source,
            "created_at": self.created_at,
        }


@dataclass
class TradingDataSummary:
    """
    Summary of raw trading data for an alert or investigation
    """

    # Required fields
    summary_id: str
    start_date: str
    end_date: str

    # Optional fields
    alert_id: Optional[str] = None
    trader_id: Optional[str] = None

    # Trade aggregates
    total_trades: int = 0
    total_orders: int = 0
    total_volume: float = 0.0
    total_notional: float = 0.0

    # Instrument breakdown
    instruments_traded: List[str] = field(default_factory=list)
    exchanges_used: List[str] = field(default_factory=list)

    # Direction analysis
    buy_trades: int = 0
    sell_trades: int = 0
    buy_volume: float = 0.0
    sell_volume: float = 0.0

    # Risk metrics
    avg_trade_size: float = 0.0
    largest_trade: float = 0.0
    price_impact: float = 0.0

    # Timing metrics
    trades_by_session: Dict[str, int] = field(default_factory=dict)
    order_cancel_rate: float = 0.0
    avg_execution_time: float = 0.0

    # P&L summary
    total_pnl: float = 0.0
    unrealized_pnl: float = 0.0

    # Metadata
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "summary_id": self.summary_id,
            "alert_id": self.alert_id,
            "trader_id": self.trader_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_trades": self.total_trades,
            "total_orders": self.total_orders,
            "total_volume": self.total_volume,
            "total_notional": self.total_notional,
            "instruments_traded": self.instruments_traded,
            "exchanges_used": self.exchanges_used,
            "buy_trades": self.buy_trades,
            "sell_trades": self.sell_trades,
            "buy_volume": self.buy_volume,
            "sell_volume": self.sell_volume,
            "avg_trade_size": self.avg_trade_size,
            "largest_trade": self.largest_trade,
            "price_impact": self.price_impact,
            "trades_by_session": self.trades_by_session,
            "order_cancel_rate": self.order_cancel_rate,
            "avg_execution_time": self.avg_execution_time,
            "total_pnl": self.total_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "generated_at": self.generated_at,
        }
