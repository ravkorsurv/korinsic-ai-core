import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Data processing pipeline for trading data transformation and feature extraction
    """

    def __init__(self):
        self.feature_extractors = {
            "volume_metrics": self._extract_volume_metrics,
            "price_metrics": self._extract_price_metrics,
            "timing_metrics": self._extract_timing_metrics,
            "order_metrics": self._extract_order_metrics,
        }

    def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing pipeline for incoming trading data"""
        try:
            # Patch: extract trader_info from hr_data if not present
            trader_info = raw_data.get("trader_info")
            if not trader_info and "hr_data" in raw_data:
                trader_info = {
                    "id": raw_data["hr_data"].get("employee_id"),
                    "role": (
                        "executive"
                        if raw_data["hr_data"].get("access_level") == "high"
                        else "trader"
                    ),
                    "access_level": raw_data["hr_data"].get("access_level", "standard"),
                    "department": raw_data["hr_data"].get("department", "trading"),
                }
            # Patch: extract volatility and price_movement from price_change if missing
            market_data = raw_data.get("market_data", {})
            if "volatility" not in market_data and "price_change" in market_data:
                market_data["volatility"] = abs(market_data["price_change"])
            if "price_movement" not in market_data and "price_change" in market_data:
                market_data["price_movement"] = market_data["price_change"]
            processed_data = {
                "raw_data": raw_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "trades": self._process_trades(raw_data.get("trades", [])),
                "orders": self._process_orders(raw_data.get("orders", [])),
                "trader_info": self._process_trader_info(trader_info or {}),
                "market_data": self._process_market_data(market_data),
                "material_events": self._process_material_events(
                    raw_data.get("material_events", [])
                ),
                "historical_metrics": self._calculate_historical_metrics(raw_data),
                "metrics": {},
            }

            # Extract features
            for feature_type, extractor in self.feature_extractors.items():
                processed_data["metrics"].update(extractor(processed_data))

            # Add derived fields
            processed_data["timeframe"] = self._determine_timeframe(
                processed_data["trades"]
            )
            processed_data["instruments"] = list(
                set(
                    [
                        t.get("instrument")
                        for t in processed_data["trades"]
                        if t.get("instrument")
                    ]
                )
            )
            processed_data["insider_indicators"] = self._identify_insider_indicators(
                processed_data
            )

            logger.info(
                f"Processed {len(processed_data['trades'])} trades and {len(processed_data['orders'])} orders"
            )
            return processed_data

        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise

    def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for process to support E2E tests."""
        return self.process(raw_data)

    def _process_trades(self, trades: List[Dict]) -> List[Dict]:
        """Process and normalize trade data"""
        processed_trades = []
        for trade in trades:
            processed_trade = {
                "id": trade.get("id"),
                "timestamp": self._normalize_timestamp(trade.get("timestamp")),
                "instrument": trade.get("instrument"),
                "volume": float(trade.get("volume", 0)),
                "price": float(trade.get("price", 0)),
                "side": trade.get("side", "unknown"),
                "trader_id": trade.get("trader_id"),
                "value": float(trade.get("volume", 0)) * float(trade.get("price", 0)),
            }
            processed_trades.append(processed_trade)
        return processed_trades

    def _process_orders(self, orders: List[Dict]) -> List[Dict]:
        """Process and normalize order data"""
        processed_orders = []
        for order in orders:
            processed_order = {
                "id": order.get("id"),
                "timestamp": self._normalize_timestamp(order.get("timestamp")),
                "instrument": order.get("instrument"),
                "size": float(order.get("size", 0)),
                "price": float(order.get("price", 0)),
                "side": order.get("side", "unknown"),
                "status": order.get("status", "unknown"),
                "trader_id": order.get("trader_id"),
                "cancellation_time": self._normalize_timestamp(
                    order.get("cancellation_time")
                ),
            }
            processed_orders.append(processed_order)
        return processed_orders

    def _process_trader_info(self, trader_info: Dict) -> Dict:
        """Process trader information"""
        return {
            "id": trader_info.get("id"),
            "name": trader_info.get("name"),
            "role": trader_info.get("role", "trader"),
            "department": trader_info.get("department"),
            "access_level": trader_info.get("access_level", "standard"),
            "start_date": trader_info.get("start_date"),
            "supervisors": trader_info.get("supervisors", []),
        }

    def _process_market_data(self, market_data: Dict) -> Dict:
        """Process market context data"""
        return {
            "volatility": market_data.get("volatility", 0),
            "volume": market_data.get("volume", 0),
            "price_movement": market_data.get("price_movement", 0),
            "liquidity": market_data.get("liquidity", 0),
            "market_hours": market_data.get("market_hours", True),
        }

    def _process_material_events(self, events: List[Dict]) -> List[Dict]:
        """Process material events that could indicate insider information"""
        processed_events = []
        for event in events:
            processed_event = {
                "id": event.get("id"),
                "timestamp": self._normalize_timestamp(event.get("timestamp")),
                "type": event.get("type"),
                "description": event.get("description"),
                "instruments_affected": event.get("instruments_affected", []),
                "materiality_score": event.get("materiality_score", 0),
            }
            processed_events.append(processed_event)
        return processed_events

    def _extract_volume_metrics(self, data: Dict) -> Dict:
        """Extract volume-based metrics"""
        trades = data["trades"]
        if not trades:
            return {"avg_volume": 0, "volume_std": 0, "volume_imbalance": 0}

        volumes = [t["volume"] for t in trades]
        buy_volume = sum([t["volume"] for t in trades if t["side"] == "buy"])
        sell_volume = sum([t["volume"] for t in trades if t["side"] == "sell"])
        total_volume = buy_volume + sell_volume

        return {
            "avg_volume": np.mean(volumes),
            "volume_std": np.std(volumes),
            "volume_imbalance": (
                abs(buy_volume - sell_volume) / total_volume if total_volume > 0 else 0
            ),
            "total_volume": total_volume,
        }

    def _extract_price_metrics(self, data: Dict) -> Dict:
        """Extract price-based metrics"""
        trades = data["trades"]
        if not trades:
            return {"price_impact": 0, "price_volatility": 0}

        prices = [t["price"] for t in trades]
        if len(prices) < 2:
            return {"price_impact": 0, "price_volatility": 0}

        price_change = (prices[-1] - prices[0]) / prices[0] if prices[0] > 0 else 0
        price_volatility = (
            np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0
        )

        return {
            "price_impact": abs(price_change),
            "price_volatility": price_volatility,
            "price_movement": price_change,
        }

    def _extract_timing_metrics(self, data: Dict) -> Dict:
        """Extract timing-based metrics"""
        trades = data["trades"]
        events = data["material_events"]

        if not trades:
            return {"pre_event_trading": 0, "timing_concentration": 0}

        # Count trades before material events
        pre_event_count = 0
        for event in events:
            if event["timestamp"]:
                event_time = datetime.fromisoformat(
                    event["timestamp"].replace("Z", "+00:00")
                )
                for trade in trades:
                    if trade["timestamp"]:
                        trade_time = datetime.fromisoformat(
                            trade["timestamp"].replace("Z", "+00:00")
                        )
                        if 0 < (event_time - trade_time).days <= 7:
                            pre_event_count += 1

        # Calculate timing concentration
        if len(trades) > 1:
            timestamps = [
                datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00"))
                for t in trades
                if t["timestamp"]
            ]
            if timestamps:
                time_span = (
                    max(timestamps) - min(timestamps)
                ).total_seconds() / 3600  # hours
                timing_concentration = len(trades) / max(time_span, 1)
            else:
                timing_concentration = 0
        else:
            timing_concentration = 0

        return {
            "pre_event_trading": pre_event_count,
            "timing_concentration": timing_concentration,
        }

    def _extract_order_metrics(self, data: Dict) -> Dict:
        """Extract order-based metrics"""
        orders = data["orders"]
        if not orders:
            return {"cancellation_ratio": 0, "order_frequency": 0}

        cancelled_count = len([o for o in orders if o["status"] == "cancelled"])
        cancellation_ratio = cancelled_count / len(orders)

        # Calculate order frequency
        if len(orders) > 1:
            timestamps = [
                datetime.fromisoformat(o["timestamp"].replace("Z", "+00:00"))
                for o in orders
                if o["timestamp"]
            ]
            if timestamps:
                time_span = (
                    max(timestamps) - min(timestamps)
                ).total_seconds() / 60  # minutes
                order_frequency = len(orders) / max(time_span, 1)
            else:
                order_frequency = 0
        else:
            order_frequency = 0

        return {
            "cancellation_ratio": cancellation_ratio,
            "order_frequency": order_frequency,
        }

    def _calculate_historical_metrics(self, raw_data: Dict) -> Dict:
        """Calculate historical baseline metrics"""
        historical = raw_data.get("historical_data", {})
        return {
            "avg_volume": historical.get("avg_volume", 1000),
            "avg_frequency": historical.get("avg_frequency", 10),
            "avg_price_impact": historical.get("avg_price_impact", 0.001),
        }

    def _determine_timeframe(self, trades: List[Dict]) -> str:
        """Determine the timeframe of the trading data"""
        if not trades:
            return "unknown"

        timestamps = [
            datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00"))
            for t in trades
            if t["timestamp"]
        ]
        if not timestamps:
            return "unknown"

        time_span = (max(timestamps) - min(timestamps)).total_seconds()

        if time_span < 3600:  # 1 hour
            return "intraday"
        elif time_span < 86400:  # 1 day
            return "daily"
        elif time_span < 604800:  # 1 week
            return "weekly"
        else:
            return "extended"

    def _identify_insider_indicators(self, data: Dict) -> List[str]:
        """Identify potential insider indicators"""
        indicators = []

        trader = data["trader_info"]
        if trader["role"] in ["executive", "board_member"]:
            indicators.append("executive_role")

        if trader["access_level"] == "high":
            indicators.append("high_access_level")

        # Check for unusual trading patterns
        metrics = data["metrics"]
        if metrics.get("timing_concentration", 0) > 10:
            indicators.append("concentrated_timing")

        if metrics.get("pre_event_trading", 0) > 0:
            indicators.append("pre_event_activity")

        return indicators

    def _normalize_timestamp(self, timestamp) -> str:
        """Normalize timestamp to ISO format"""
        if not timestamp:
            return None

        if isinstance(timestamp, str):
            return timestamp
        elif isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).isoformat() + "Z"
        elif isinstance(timestamp, datetime):
            return timestamp.isoformat() + "Z"
        else:
            return str(timestamp)

    def generate_simulation_data(
        self, scenario_type: str, parameters: Dict
    ) -> Dict[str, Any]:
        """Generate simulated trading data for testing"""
        np.random.seed(parameters.get("seed", 42))

        if scenario_type == "insider_dealing":
            return self._generate_insider_scenario(parameters)
        elif scenario_type == "spoofing":
            return self._generate_spoofing_scenario(parameters)
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")

    def _generate_insider_scenario(self, params: Dict) -> Dict[str, Any]:
        """Generate insider dealing simulation data"""
        num_trades = params.get("num_trades", 50)
        base_time = datetime.now(timezone.utc) - timedelta(days=7)

        # Generate material event
        event_time = base_time + timedelta(days=5)
        material_event = {
            "id": "event_001",
            "timestamp": event_time.isoformat() + "Z",
            "type": "earnings_announcement",
            "description": "Quarterly earnings announcement",
            "instruments_affected": ["STOCK_A"],
            "materiality_score": 0.8,
        }

        # Generate trades clustered before the event
        trades = []
        for i in range(num_trades):
            # Higher probability of trades closer to event
            days_before_event = np.random.exponential(2)
            trade_time = event_time - timedelta(days=days_before_event)

            trade = {
                "id": f"trade_{i:03d}",
                "timestamp": trade_time.isoformat() + "Z",
                "instrument": "STOCK_A",
                "volume": np.random.lognormal(8, 1),  # Large volumes
                "price": 100 + np.random.normal(0, 2),
                "side": "buy",
                "trader_id": "trader_insider",
            }
            trades.append(trade)

        return {
            "trades": trades,
            "orders": [],
            "trader_info": {
                "id": "trader_insider",
                "role": "senior_trader",
                "access_level": "high",
            },
            "material_events": [material_event],
            "market_data": {"volatility": 0.02},
        }

    def _generate_spoofing_scenario(self, params: Dict) -> Dict[str, Any]:
        """Generate spoofing simulation data"""
        num_orders = params.get("num_orders", 100)
        base_time = datetime.now(timezone.utc) - timedelta(hours=1)

        orders = []
        trades = []

        for i in range(num_orders):
            order_time = base_time + timedelta(seconds=i * 10)

            # Generate large orders that will be cancelled
            if i % 5 == 0:  # Every 5th order is a real trade
                order = {
                    "id": f"order_{i:03d}",
                    "timestamp": order_time.isoformat() + "Z",
                    "instrument": "FUTURE_X",
                    "size": np.random.normal(1000, 200),
                    "price": 50 + np.random.normal(0, 0.1),
                    "side": "buy",
                    "status": "filled",
                    "trader_id": "trader_spoofer",
                }

                # Add corresponding trade
                trade = {
                    "id": f"trade_{i:03d}",
                    "timestamp": order_time.isoformat() + "Z",
                    "instrument": "FUTURE_X",
                    "volume": order["size"],
                    "price": order["price"],
                    "side": order["side"],
                    "trader_id": "trader_spoofer",
                }
                trades.append(trade)
            else:
                # Large orders that get cancelled
                order = {
                    "id": f"order_{i:03d}",
                    "timestamp": order_time.isoformat() + "Z",
                    "instrument": "FUTURE_X",
                    "size": np.random.normal(5000, 1000),  # Much larger
                    "price": 50 + np.random.normal(0, 0.1),
                    "side": "sell",
                    "status": "cancelled",
                    "trader_id": "trader_spoofer",
                    "cancellation_time": (
                        order_time + timedelta(seconds=30)
                    ).isoformat()
                    + "Z",
                }

            orders.append(order)

        return {
            "trades": trades,
            "orders": orders,
            "trader_info": {
                "id": "trader_spoofer",
                "role": "trader",
                "access_level": "standard",
            },
            "material_events": [],
            "market_data": {"volatility": 0.015},
        }
