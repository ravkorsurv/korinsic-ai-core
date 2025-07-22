"""
Trading Data Service

This service provides comprehensive raw trading data extraction and aggregation
capabilities for analyst investigations of market abuse alerts.
"""

import logging
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np

from models.trading_data import (
    OrderStatus,
    RawOrderData,
    RawTradeData,
    TradeDirection,
    TradingDataSummary,
)

logger = logging.getLogger(__name__)


class TradingDataService:
    """
    Service for extracting and aggregating raw trading data for analyst investigations
    """

    def __init__(self):
        self.raw_trades_cache = {}
        self.raw_orders_cache = {}
        self.data_summaries = {}

    def extract_raw_trades_for_alert(
        self, alert_id: str, processed_data: Dict[str, Any]
    ) -> List[RawTradeData]:
        """
        Extract comprehensive raw trade data for a specific alert

        Args:
            alert_id: Alert identifier
            processed_data: Processed trading data from data processor

        Returns:
            List of comprehensive raw trade data
        """
        try:
            raw_trades = []
            trades = processed_data.get("trades", [])
            trader_info = processed_data.get("trader_info", {})
            market_data = processed_data.get("market_data", {})

            for trade in trades:
                # Calculate additional metrics
                notional = trade.get(
                    "value", trade.get("volume", 0) * trade.get("price", 0)
                )

                # Determine market session
                market_session = self._determine_market_session(trade.get("timestamp"))

                # Calculate price deviation from reference
                reference_price = market_data.get(
                    "reference_price", trade.get("price", 0)
                )
                price_deviation = self._calculate_price_deviation(
                    trade.get("price", 0), reference_price
                )

                # Create comprehensive trade data
                raw_trade = RawTradeData(
                    trade_id=trade.get(
                        "id", f"trade_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
                    ),
                    execution_timestamp=trade.get(
                        "timestamp", datetime.utcnow().isoformat()
                    ),
                    instrument=trade.get("instrument", "UNKNOWN"),
                    instrument_type=self._determine_instrument_type(
                        trade.get("instrument", "")
                    ),
                    symbol=trade.get("instrument", "UNKNOWN"),
                    exchange=self._determine_exchange(trade.get("instrument", "")),
                    direction=TradeDirection(trade.get("side", "unknown")),
                    quantity=float(trade.get("volume", 0)),
                    executed_price=float(trade.get("price", 0)),
                    notional_value=float(notional),
                    trader_id=trade.get("trader_id", trader_info.get("id", "unknown")),
                    # Optional fields with enhanced data
                    order_id=trade.get("order_id"),
                    trader_name=trader_info.get("name"),
                    trader_role=trader_info.get("role"),
                    desk=trader_info.get("department"),
                    book=trader_info.get("book"),
                    market_session=market_session,
                    bid_price=market_data.get("bid_price"),
                    ask_price=market_data.get("ask_price"),
                    mid_price=market_data.get("mid_price"),
                    spread=self._calculate_spread(
                        market_data.get("bid_price"), market_data.get("ask_price")
                    ),
                    market_volume=market_data.get("volume"),
                    reference_price=reference_price,
                    price_deviation=price_deviation,
                    alert_ids=[alert_id],
                    data_source="surveillance_platform",
                )

                raw_trades.append(raw_trade)

            # Cache the results
            self.raw_trades_cache[alert_id] = raw_trades

            logger.info(f"Extracted {len(raw_trades)} raw trades for alert {alert_id}")
            return raw_trades

        except Exception as e:
            logger.error(f"Error extracting raw trades for alert {alert_id}: {str(e)}")
            raise

    def extract_raw_orders_for_alert(
        self, alert_id: str, processed_data: Dict[str, Any]
    ) -> List[RawOrderData]:
        """
        Extract comprehensive raw order data for a specific alert

        Args:
            alert_id: Alert identifier
            processed_data: Processed trading data from data processor

        Returns:
            List of comprehensive raw order data
        """
        try:
            raw_orders = []
            orders = processed_data.get("orders", [])
            trader_info = processed_data.get("trader_info", {})
            market_data = processed_data.get("market_data", {})

            for order in orders:
                # Calculate filled and remaining quantities
                filled_qty = float(order.get("filled_quantity", 0))
                total_qty = float(order.get("size", 0))
                remaining_qty = max(0, total_qty - filled_qty)

                # Determine order status
                status = OrderStatus(order.get("status", "unknown"))

                # Calculate notional value
                notional = total_qty * order.get("price", 0)

                # Create comprehensive order data
                raw_order = RawOrderData(
                    order_id=order.get(
                        "id", f"order_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
                    ),
                    order_timestamp=order.get(
                        "timestamp", datetime.utcnow().isoformat()
                    ),
                    status=status,
                    instrument=order.get("instrument", "UNKNOWN"),
                    instrument_type=self._determine_instrument_type(
                        order.get("instrument", "")
                    ),
                    symbol=order.get("instrument", "UNKNOWN"),
                    exchange=self._determine_exchange(order.get("instrument", "")),
                    side=TradeDirection(order.get("side", "unknown")),
                    order_type=self._determine_order_type(order),
                    quantity=total_qty,
                    filled_quantity=filled_qty,
                    remaining_quantity=remaining_qty,
                    trader_id=order.get("trader_id", trader_info.get("id", "unknown")),
                    # Optional fields
                    client_order_id=order.get("client_order_id"),
                    last_update_timestamp=order.get("last_update"),
                    order_price=order.get("price"),
                    avg_fill_price=order.get("avg_fill_price"),
                    limit_price=order.get("limit_price"),
                    stop_price=order.get("stop_price"),
                    time_in_force=order.get("time_in_force", "DAY"),
                    cancellation_timestamp=order.get("cancellation_time"),
                    cancellation_reason=order.get("cancellation_reason"),
                    bid_at_order=market_data.get("bid_price"),
                    ask_at_order=market_data.get("ask_price"),
                    mid_at_order=market_data.get("mid_price"),
                    trader_name=trader_info.get("name"),
                    strategy=order.get("strategy"),
                    notional_value=notional,
                    alert_ids=[alert_id],
                    risk_indicators=self._identify_order_risk_indicators(order),
                    data_source="surveillance_platform",
                )

                raw_orders.append(raw_order)

            # Cache the results
            self.raw_orders_cache[alert_id] = raw_orders

            logger.info(f"Extracted {len(raw_orders)} raw orders for alert {alert_id}")
            return raw_orders

        except Exception as e:
            logger.error(f"Error extracting raw orders for alert {alert_id}: {str(e)}")
            raise

    def generate_trading_data_summary(
        self,
        alert_id: str,
        raw_trades: List[RawTradeData],
        raw_orders: List[RawOrderData],
    ) -> TradingDataSummary:
        """
        Generate comprehensive trading data summary for an alert

        Args:
            alert_id: Alert identifier
            raw_trades: Raw trade data
            raw_orders: Raw order data

        Returns:
            Trading data summary
        """
        try:
            if not raw_trades and not raw_orders:
                logger.warning(f"No trade or order data available for alert {alert_id}")
                return TradingDataSummary(
                    summary_id=f"summary_{alert_id}",
                    start_date=datetime.utcnow().isoformat(),
                    end_date=datetime.utcnow().isoformat(),
                    alert_id=alert_id,
                )

            # Determine date range
            all_timestamps = []
            for trade in raw_trades:
                all_timestamps.append(trade.execution_timestamp)
            for order in raw_orders:
                all_timestamps.append(order.order_timestamp)

            all_timestamps = [t for t in all_timestamps if t]
            start_date = (
                min(all_timestamps) if all_timestamps else datetime.utcnow().isoformat()
            )
            end_date = (
                max(all_timestamps) if all_timestamps else datetime.utcnow().isoformat()
            )

            # Calculate trade metrics
            total_volume = sum(trade.quantity for trade in raw_trades)
            total_notional = sum(trade.notional_value for trade in raw_trades)

            # Direction analysis
            buy_trades = len(
                [t for t in raw_trades if t.direction == TradeDirection.BUY]
            )
            sell_trades = len(
                [t for t in raw_trades if t.direction == TradeDirection.SELL]
            )
            buy_volume = sum(
                t.quantity for t in raw_trades if t.direction == TradeDirection.BUY
            )
            sell_volume = sum(
                t.quantity for t in raw_trades if t.direction == TradeDirection.SELL
            )

            # Risk metrics
            trade_sizes = [trade.quantity for trade in raw_trades]
            avg_trade_size = np.mean(trade_sizes) if trade_sizes else 0
            largest_trade = max(trade_sizes) if trade_sizes else 0

            # Calculate price impact
            price_impact = self._calculate_aggregate_price_impact(raw_trades)

            # Order analysis
            cancelled_orders = len(
                [o for o in raw_orders if o.status == OrderStatus.CANCELLED]
            )
            order_cancel_rate = cancelled_orders / len(raw_orders) if raw_orders else 0

            # Execution time analysis
            execution_times = self._calculate_execution_times(raw_orders, raw_trades)
            avg_execution_time = np.mean(execution_times) if execution_times else 0

            # Session analysis
            trades_by_session = self._analyze_trades_by_session(raw_trades)

            # P&L calculation
            total_pnl = sum(trade.pnl_realized or 0 for trade in raw_trades)
            unrealized_pnl = sum(trade.pnl_unrealized or 0 for trade in raw_trades)

            # Get unique values
            instruments = list(set(trade.instrument for trade in raw_trades))
            exchanges = list(set(trade.exchange for trade in raw_trades))

            # Get trader ID
            trader_id = (
                raw_trades[0].trader_id
                if raw_trades
                else (raw_orders[0].trader_id if raw_orders else None)
            )

            summary = TradingDataSummary(
                summary_id=f"summary_{alert_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                start_date=start_date,
                end_date=end_date,
                alert_id=alert_id,
                trader_id=trader_id,
                total_trades=len(raw_trades),
                total_orders=len(raw_orders),
                total_volume=total_volume,
                total_notional=total_notional,
                instruments_traded=instruments,
                exchanges_used=exchanges,
                buy_trades=buy_trades,
                sell_trades=sell_trades,
                buy_volume=buy_volume,
                sell_volume=sell_volume,
                avg_trade_size=avg_trade_size,
                largest_trade=largest_trade,
                price_impact=price_impact,
                trades_by_session=trades_by_session,
                order_cancel_rate=order_cancel_rate,
                avg_execution_time=avg_execution_time,
                total_pnl=total_pnl,
                unrealized_pnl=unrealized_pnl,
            )

            # Cache the summary
            self.data_summaries[alert_id] = summary

            logger.info(f"Generated trading data summary for alert {alert_id}")
            return summary

        except Exception as e:
            logger.error(
                f"Error generating trading data summary for alert {alert_id}: {str(e)}"
            )
            raise

    def get_raw_trading_data_for_alert(
        self, alert_id: str, processed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get comprehensive raw trading data for an alert

        Args:
            alert_id: Alert identifier
            processed_data: Processed trading data

        Returns:
            Dictionary containing raw trades, orders, and summary
        """
        try:
            # Extract raw data
            raw_trades = self.extract_raw_trades_for_alert(alert_id, processed_data)
            raw_orders = self.extract_raw_orders_for_alert(alert_id, processed_data)

            # Generate summary
            summary = self.generate_trading_data_summary(
                alert_id, raw_trades, raw_orders
            )

            return {
                "alert_id": alert_id,
                "raw_trades": [trade.to_dict() for trade in raw_trades],
                "raw_orders": [order.to_dict() for order in raw_orders],
                "summary": summary.to_dict(),
                "extraction_timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Error getting raw trading data for alert {alert_id}: {str(e)}"
            )
            raise

    def get_raw_trading_data_for_trader(
        self, trader_id: str, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """
        Get raw trading data for a specific trader within a date range

        Args:
            trader_id: Trader identifier
            start_date: Start date (ISO format)
            end_date: End date (ISO format)

        Returns:
            Dictionary containing raw trades and orders for the trader
        """
        try:
            # Filter cached data for the trader
            trader_trades = []
            trader_orders = []

            for alert_id, trades in self.raw_trades_cache.items():
                for trade in trades:
                    if (
                        trade.trader_id == trader_id
                        and start_date <= trade.execution_timestamp <= end_date
                    ):
                        trader_trades.append(trade)

            for alert_id, orders in self.raw_orders_cache.items():
                for order in orders:
                    if (
                        order.trader_id == trader_id
                        and start_date <= order.order_timestamp <= end_date
                    ):
                        trader_orders.append(order)

            # Generate summary
            summary = self.generate_trading_data_summary(
                f"trader_{trader_id}", trader_trades, trader_orders
            )

            return {
                "trader_id": trader_id,
                "date_range": {"start": start_date, "end": end_date},
                "raw_trades": [trade.to_dict() for trade in trader_trades],
                "raw_orders": [order.to_dict() for order in trader_orders],
                "summary": summary.to_dict(),
                "extraction_timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Error getting raw trading data for trader {trader_id}: {str(e)}"
            )
            raise

    def _determine_market_session(self, timestamp: str) -> str:
        """Determine market session based on timestamp"""
        try:
            if not timestamp:
                return "unknown"

            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            hour = dt.hour

            if 4 <= hour < 9:
                return "pre-market"
            elif 9 <= hour < 16:
                return "regular"
            elif 16 <= hour < 20:
                return "after-hours"
            else:
                return "extended"

        except:
            return "unknown"

    def _determine_instrument_type(self, instrument: str) -> str:
        """Determine instrument type based on instrument identifier"""
        if not instrument:
            return "unknown"

        instrument_upper = instrument.upper()
        if "FUTURE" in instrument_upper or "FUT" in instrument_upper:
            return "future"
        elif "OPTION" in instrument_upper or "OPT" in instrument_upper:
            return "option"
        elif "BOND" in instrument_upper:
            return "bond"
        elif "FX" in instrument_upper or "FOREX" in instrument_upper:
            return "forex"
        else:
            return "equity"

    def _determine_exchange(self, instrument: str) -> str:
        """Determine exchange based on instrument identifier"""
        if not instrument:
            return "UNKNOWN"

        # This is a simplified mapping - in practice, you'd have a proper lookup
        if "NYSE" in instrument.upper():
            return "NYSE"
        elif "NASDAQ" in instrument.upper():
            return "NASDAQ"
        elif "LSE" in instrument.upper():
            return "LSE"
        else:
            return "EXCHANGE"

    def _determine_order_type(self, order: Dict) -> str:
        """Determine order type based on order data"""
        if order.get("limit_price"):
            return "limit"
        elif order.get("stop_price"):
            return "stop"
        elif order.get("order_type"):
            return order["order_type"]
        else:
            return "market"

    def _calculate_price_deviation(
        self, executed_price: float, reference_price: float
    ) -> float:
        """Calculate price deviation percentage"""
        if not reference_price or reference_price == 0:
            return 0.0
        return ((executed_price - reference_price) / reference_price) * 100

    def _calculate_spread(
        self, bid_price: Optional[float], ask_price: Optional[float]
    ) -> Optional[float]:
        """Calculate bid-ask spread"""
        if bid_price and ask_price:
            return ask_price - bid_price
        return None

    def _identify_order_risk_indicators(self, order: Dict) -> List[str]:
        """Identify risk indicators for an order"""
        indicators = []

        if order.get("status") == "cancelled":
            indicators.append("cancelled_order")

        if order.get("size", 0) > 10000:
            indicators.append("large_order")

        if order.get("cancellation_time"):
            # Calculate time to cancellation
            order_time = datetime.fromisoformat(
                order["timestamp"].replace("Z", "+00:00")
            )
            cancel_time = datetime.fromisoformat(
                order["cancellation_time"].replace("Z", "+00:00")
            )
            if (cancel_time - order_time).total_seconds() < 60:
                indicators.append("quick_cancellation")

        return indicators

    def _calculate_aggregate_price_impact(self, trades: List[RawTradeData]) -> float:
        """Calculate aggregate price impact across trades"""
        if not trades:
            return 0.0

        total_impact = 0.0
        for trade in trades:
            if trade.price_deviation:
                total_impact += abs(trade.price_deviation)

        return total_impact / len(trades)

    def _calculate_execution_times(
        self, orders: List[RawOrderData], trades: List[RawTradeData]
    ) -> List[float]:
        """Calculate execution times for orders that resulted in trades"""
        execution_times = []

        for order in orders:
            if order.status == OrderStatus.FILLED:
                # Find corresponding trades
                for trade in trades:
                    if trade.order_id == order.order_id:
                        try:
                            order_time = datetime.fromisoformat(
                                order.order_timestamp.replace("Z", "+00:00")
                            )
                            trade_time = datetime.fromisoformat(
                                trade.execution_timestamp.replace("Z", "+00:00")
                            )
                            execution_time = (trade_time - order_time).total_seconds()
                            execution_times.append(execution_time)
                        except:
                            continue

        return execution_times

    def _analyze_trades_by_session(self, trades: List[RawTradeData]) -> Dict[str, int]:
        """Analyze trades by market session"""
        session_counts = {}

        for trade in trades:
            session = trade.market_session or "unknown"
            session_counts[session] = session_counts.get(session, 0) + 1

        return session_counts
