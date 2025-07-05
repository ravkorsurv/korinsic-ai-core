"""
Data generators for creating realistic test data.
"""

import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


def generate_trade_data(num_trades: int = 10, 
                       instruments: Optional[List[str]] = None,
                       traders: Optional[List[str]] = None,
                       start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Generate realistic trade data for testing.
    
    Args:
        num_trades: Number of trades to generate
        instruments: List of instrument names to use
        traders: List of trader IDs to use
        start_time: Starting timestamp for trades
        
    Returns:
        List of trade dictionaries
    """
    if instruments is None:
        instruments = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX"]
    
    if traders is None:
        traders = [f"trader_{i:03d}" for i in range(1, 21)]  # 20 traders
    
    if start_time is None:
        start_time = datetime(2024, 1, 1, 9, 0, 0)  # Market open
    
    trades = []
    current_time = start_time
    
    # Base prices for instruments
    base_prices = {instrument: random.uniform(50.0, 500.0) for instrument in instruments}
    
    for i in range(num_trades):
        instrument = random.choice(instruments)
        trader_id = random.choice(traders)
        
        # Price movement (small random walk)
        price_change = random.uniform(-0.02, 0.02)  # ±2% movement
        base_prices[instrument] *= (1 + price_change)
        
        trade = {
            "id": f"trade_{i+1:06d}",
            "timestamp": current_time.isoformat() + "Z",
            "instrument": instrument,
            "volume": random.randint(100, 100000),
            "price": round(base_prices[instrument], 2),
            "side": random.choice(["buy", "sell"]),
            "trader_id": trader_id,
            "execution_venue": random.choice(["NYSE", "NASDAQ", "LSE", "XETRA"]),
            "order_type": random.choice(["market", "limit", "stop"])
        }
        
        trades.append(trade)
        
        # Advance time by 1-30 minutes randomly
        current_time += timedelta(minutes=random.randint(1, 30))
    
    return trades


def generate_order_data(num_orders: int = 20,
                       instruments: Optional[List[str]] = None,
                       traders: Optional[List[str]] = None,
                       start_time: Optional[datetime] = None,
                       cancellation_rate: float = 0.3) -> List[Dict[str, Any]]:
    """
    Generate realistic order data for testing.
    
    Args:
        num_orders: Number of orders to generate
        instruments: List of instrument names to use
        traders: List of trader IDs to use
        start_time: Starting timestamp for orders
        cancellation_rate: Proportion of orders that are cancelled
        
    Returns:
        List of order dictionaries
    """
    if instruments is None:
        instruments = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX"]
    
    if traders is None:
        traders = [f"trader_{i:03d}" for i in range(1, 21)]
    
    if start_time is None:
        start_time = datetime(2024, 1, 1, 9, 0, 0)
    
    orders = []
    current_time = start_time
    
    # Base prices for instruments
    base_prices = {instrument: random.uniform(50.0, 500.0) for instrument in instruments}
    
    for i in range(num_orders):
        instrument = random.choice(instruments)
        trader_id = random.choice(traders)
        
        # Determine order status
        is_cancelled = random.random() < cancellation_rate
        status = "cancelled" if is_cancelled else random.choice(["filled", "partial", "pending"])
        
        # Price variation for limit orders
        base_price = base_prices[instrument]
        price_variation = random.uniform(-0.05, 0.05)  # ±5% from base
        order_price = round(base_price * (1 + price_variation), 2)
        
        order = {
            "id": f"order_{i+1:06d}",
            "timestamp": current_time.isoformat() + "Z",
            "instrument": instrument,
            "volume": random.randint(100, 200000),
            "price": order_price,
            "side": random.choice(["buy", "sell"]),
            "status": status,
            "trader_id": trader_id,
            "order_type": random.choice(["limit", "market", "stop", "stop_limit"])
        }
        
        orders.append(order)
        
        # Advance time by 30 seconds to 10 minutes
        current_time += timedelta(seconds=random.randint(30, 600))
    
    return orders


def generate_material_events(num_events: int = 5,
                           instruments: Optional[List[str]] = None,
                           start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Generate realistic material events for testing.
    
    Args:
        num_events: Number of events to generate
        instruments: List of instrument names to use
        start_time: Starting timestamp for events
        
    Returns:
        List of material event dictionaries
    """
    if instruments is None:
        instruments = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX"]
    
    if start_time is None:
        start_time = datetime(2024, 1, 1, 8, 0, 0)  # Before market open
    
    event_types = [
        "earnings_announcement",
        "merger_announcement", 
        "regulatory_approval",
        "product_launch",
        "executive_departure",
        "dividend_announcement",
        "guidance_update",
        "partnership_announcement"
    ]
    
    descriptions = {
        "earnings_announcement": [
            "Quarterly earnings announcement",
            "Strong earnings beat expectations",
            "Disappointing quarterly results",
            "Revenue guidance update"
        ],
        "merger_announcement": [
            "Strategic acquisition announcement",
            "Merger proposal received",
            "Deal completion announcement"
        ],
        "regulatory_approval": [
            "FDA approval received",
            "Regulatory clearance granted",
            "Compliance investigation launched"
        ],
        "product_launch": [
            "New product announcement",
            "Major software release",
            "Innovation breakthrough"
        ],
        "executive_departure": [
            "CEO resignation announced",
            "CFO departure",
            "Leadership transition"
        ],
        "dividend_announcement": [
            "Dividend increase announced",
            "Special dividend declared",
            "Dividend policy change"
        ],
        "guidance_update": [
            "Guidance raised for quarter",
            "Outlook revised downward",
            "Forward guidance provided"
        ],
        "partnership_announcement": [
            "Strategic partnership formed",
            "Joint venture announced",
            "Collaboration agreement signed"
        ]
    }
    
    events = []
    current_time = start_time
    
    for i in range(num_events):
        event_type = random.choice(event_types)
        affected_instruments = random.sample(instruments, random.randint(1, 3))
        
        event = {
            "id": f"event_{i+1:03d}",
            "timestamp": current_time.isoformat() + "Z",
            "type": event_type,
            "description": random.choice(descriptions[event_type]),
            "instruments_affected": affected_instruments,
            "expected_impact": round(random.uniform(0.02, 0.20), 3),
            "materiality_score": round(random.uniform(0.5, 1.0), 2),
            "public_release": current_time.isoformat() + "Z"
        }
        
        events.append(event)
        
        # Advance time by 1-7 days
        current_time += timedelta(days=random.randint(1, 7))
    
    return events


def generate_market_data(instruments: Optional[List[str]] = None,
                        volatility_regime: str = "normal") -> Dict[str, Any]:
    """
    Generate realistic market data for testing.
    
    Args:
        instruments: List of instrument names
        volatility_regime: Market volatility regime ('low', 'normal', 'high', 'crisis')
        
    Returns:
        Market data dictionary
    """
    if instruments is None:
        instruments = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    
    # Volatility ranges based on regime
    volatility_ranges = {
        "low": (0.01, 0.02),
        "normal": (0.02, 0.05),
        "high": (0.05, 0.10),
        "crisis": (0.10, 0.30)
    }
    
    vol_min, vol_max = volatility_ranges[volatility_regime]
    
    market_data = {
        "volatility": round(random.uniform(vol_min, vol_max), 4),
        "liquidity": round(random.uniform(0.3, 0.95), 2),
        "price_movement": round(random.uniform(-0.15, 0.15), 4),
        "volume": random.randint(500000, 5000000),
        "bid_ask_spread": round(random.uniform(0.001, 0.05), 4),
        "market_cap": random.randint(1000000000, 2000000000000),  # $1B to $2T
        "average_volume": random.randint(400000, 2000000),
        "sector_performance": round(random.uniform(-0.05, 0.05), 4),
        "market_sentiment": round(random.uniform(-1.0, 1.0), 2)
    }
    
    # Add instrument-specific data
    market_data["instruments"] = {}
    for instrument in instruments:
        market_data["instruments"][instrument] = {
            "price": round(random.uniform(50.0, 500.0), 2),
            "volume": random.randint(100000, 1000000),
            "volatility": round(random.uniform(vol_min, vol_max), 4),
            "beta": round(random.uniform(0.5, 2.0), 2)
        }
    
    return market_data


def generate_trader_profiles(num_traders: int = 20,
                           departments: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Generate realistic trader profiles for testing.
    
    Args:
        num_traders: Number of trader profiles to generate
        departments: List of department names
        
    Returns:
        List of trader profile dictionaries
    """
    if departments is None:
        departments = ["equity_trading", "fixed_income", "derivatives", "commodities", 
                      "forex", "management", "sales", "research"]
    
    roles = ["trader", "senior_trader", "head_trader", "portfolio_manager", 
             "executive", "analyst", "sales_trader", "risk_manager"]
    
    access_levels = ["low", "medium", "high"]
    clearance_levels = ["standard", "elevated", "executive"]
    
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", 
                   "Lisa", "William", "Jennifer", "James", "Amy", "Christopher", "Maria"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", 
                  "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez"]
    
    traders = []
    
    for i in range(num_traders):
        # Generate realistic hire date (1-15 years ago)
        hire_date = datetime.now() - timedelta(days=random.randint(365, 5475))
        
        trader = {
            "id": f"trader_{i+1:03d}",
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "role": random.choice(roles),
            "access_level": random.choice(access_levels),
            "department": random.choice(departments),
            "hire_date": hire_date.strftime("%Y-%m-%d"),
            "clearance_level": random.choice(clearance_levels),
            "years_experience": random.randint(1, 20),
            "performance_rating": round(random.uniform(2.0, 5.0), 1),
            "compliance_training_date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        }
        
        traders.append(trader)
    
    return traders


def generate_news_data(num_articles: int = 10,
                      instruments: Optional[List[str]] = None,
                      start_time: Optional[datetime] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate realistic news data for testing.
    
    Args:
        num_articles: Number of news articles to generate
        instruments: List of instrument names
        start_time: Starting timestamp for news
        
    Returns:
        News data dictionary with news_events list
    """
    if instruments is None:
        instruments = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX"]
    
    if start_time is None:
        start_time = datetime(2024, 1, 1, 6, 0, 0)  # Early morning
    
    sources = ["Reuters", "Bloomberg", "WSJ", "FT", "CNBC", "MarketWatch", "Yahoo Finance"]
    
    headline_templates = [
        "{company} reports strong quarterly earnings",
        "{company} shares surge on positive outlook", 
        "{company} faces regulatory scrutiny",
        "{company} announces major acquisition",
        "{company} stock drops on disappointing results",
        "{company} CEO steps down unexpectedly",
        "{company} launches innovative new product",
        "{company} expands into new markets"
    ]
    
    news_events = []
    current_time = start_time
    
    for i in range(num_articles):
        instrument = random.choice(instruments)
        company_name = instrument  # Simplified - use ticker as company name
        
        headline = random.choice(headline_templates).format(company=company_name)
        
        # Sentiment: positive news gets positive sentiment, negative gets negative
        if any(word in headline.lower() for word in ["strong", "surge", "positive", "launches", "expands"]):
            sentiment = round(random.uniform(0.3, 1.0), 2)
        elif any(word in headline.lower() for word in ["drops", "disappointing", "scrutiny", "steps down"]):
            sentiment = round(random.uniform(-1.0, -0.3), 2)
        else:
            sentiment = round(random.uniform(-0.2, 0.2), 2)
        
        news_event = {
            "id": f"news_{i+1:03d}",
            "timestamp": current_time.isoformat() + "Z",
            "headline": headline,
            "sentiment": sentiment,
            "market_impact": round(abs(sentiment) * random.uniform(0.5, 1.5), 3),
            "relevance_score": round(random.uniform(0.6, 1.0), 2),
            "source": random.choice(sources),
            "instruments_affected": [instrument]
        }
        
        news_events.append(news_event)
        
        # Advance time by 30 minutes to 4 hours
        current_time += timedelta(minutes=random.randint(30, 240))
    
    return {"news_events": news_events}