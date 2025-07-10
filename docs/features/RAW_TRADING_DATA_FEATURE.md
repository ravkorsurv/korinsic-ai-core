# Raw Trading Data Feature

## Overview

The Raw Trading Data feature provides analysts with comprehensive access to detailed trading information underlying market abuse alerts. This feature enables deep investigation and analysis of trading patterns, execution details, and market context that triggered surveillance alerts.

## Key Features

### 1. Comprehensive Trade Data
- **Execution timestamps** - Precise timing of trade executions
- **Traded prices** - Actual execution prices and market context
- **Instruments** - Full instrument identification and classification
- **Direction** - Buy/sell trade direction
- **Quantities** - Executed volumes and notional values
- **Market context** - Bid/ask spreads, market volume, price deviations

### 2. Order Analysis
- **Order lifecycle** - Complete order history from placement to execution/cancellation
- **Order types** - Market, limit, stop orders with price details
- **Fill analysis** - Partial fills, execution times, and fill rates
- **Risk indicators** - Automated flagging of suspicious order patterns

### 3. Trading Summaries
- **Aggregated metrics** - Volume, notional, trade counts by direction
- **Risk analysis** - Price impact, execution patterns, session distribution
- **P&L tracking** - Realized and unrealized profit/loss calculations
- **Compliance data** - Regulatory reporting fields and audit trails

## API Endpoints

### 1. Get Raw Data for Alert
```
POST /api/v1/raw-data/alert/{alert_id}
```

**Purpose**: Retrieve comprehensive raw trading data for a specific alert.

**Request Body**:
```json
{
  "trades": [...],
  "orders": [...],
  "trader_info": {...},
  "market_data": {...}
}
```

**Response**:
```json
{
  "status": "success",
  "alert_id": "insider_20240101_120000",
  "raw_trading_data": {
    "alert_id": "insider_20240101_120000",
    "raw_trades": [
      {
        "trade_id": "trade_001",
        "execution_timestamp": "2024-01-01T12:00:00Z",
        "instrument": "AAPL",
        "instrument_type": "equity",
        "symbol": "AAPL",
        "exchange": "NASDAQ",
        "direction": "buy",
        "quantity": 1000,
        "executed_price": 150.25,
        "notional_value": 150250.00,
        "trader_id": "trader_001",
        "trader_name": "John Smith",
        "trader_role": "senior_trader",
        "market_session": "regular",
        "bid_price": 150.20,
        "ask_price": 150.30,
        "spread": 0.10,
        "price_deviation": 0.033,
        "alert_ids": ["insider_20240101_120000"]
      }
    ],
    "raw_orders": [
      {
        "order_id": "order_001",
        "order_timestamp": "2024-01-01T11:59:45Z",
        "status": "filled",
        "instrument": "AAPL",
        "side": "buy",
        "order_type": "market",
        "quantity": 1000,
        "filled_quantity": 1000,
        "remaining_quantity": 0,
        "avg_fill_price": 150.25,
        "trader_id": "trader_001"
      }
    ],
    "summary": {
      "total_trades": 1,
      "total_orders": 1,
      "total_volume": 1000,
      "total_notional": 150250.00,
      "buy_trades": 1,
      "sell_trades": 0,
      "avg_trade_size": 1000,
      "price_impact": 0.033
    }
  }
}
```

### 2. Get Raw Data for Trader
```
GET /api/v1/raw-data/trader/{trader_id}?start_date={start}&end_date={end}
```

**Purpose**: Retrieve raw trading data for a specific trader within a date range.

**Parameters**:
- `trader_id`: Trader identifier
- `start_date`: Start date (ISO format)
- `end_date`: End date (ISO format)

### 3. Get Trading Data Summary
```
POST /api/v1/raw-data/summary/{alert_id}
```

**Purpose**: Get aggregated trading metrics and analysis for an alert.

### 4. Export Raw Data
```
POST /api/v1/raw-data/export/csv/{alert_id}
POST /api/v1/raw-data/export/json/{alert_id}
```

**Purpose**: Export raw trading data as CSV or JSON files for offline analysis.

### 5. Comprehensive Analysis
```
POST /api/v1/raw-data/analyze/{alert_id}
```

**Purpose**: Perform comprehensive analysis combining raw data with risk scores and regulatory context.

### 6. Search Raw Data
```
POST /api/v1/raw-data/search
```

**Purpose**: Search raw trading data based on criteria.

**Request Body**:
```json
{
  "trader_id": "trader_001",
  "instrument": "AAPL",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "direction": "buy",
  "min_quantity": 500,
  "max_quantity": 5000,
  "min_price": 140.00,
  "max_price": 160.00
}
```

## Data Models

### RawTradeData
Comprehensive trade execution data including:
- **Identifiers**: trade_id, order_id, parent_order_id
- **Execution details**: timestamp, settlement_date
- **Financial data**: instrument, symbol, exchange, direction, quantity, price, notional_value
- **Market context**: bid_price, ask_price, spread, market_volume
- **Trader context**: trader_id, trader_name, trader_role, desk, book
- **Risk data**: position_before, position_after, pnl_realized, pnl_unrealized
- **Timing analysis**: order_timestamp, time_to_execution, market_session
- **Compliance**: counterparty, commission, fees, reference_price, price_deviation

### RawOrderData
Comprehensive order lifecycle data including:
- **Identifiers**: order_id, parent_order_id, client_order_id
- **Lifecycle**: order_timestamp, status, last_update_timestamp
- **Order details**: instrument, symbol, exchange, side, order_type
- **Quantities**: quantity, filled_quantity, remaining_quantity
- **Pricing**: order_price, avg_fill_price, limit_price, stop_price
- **Execution**: fills, partial_fills, time_in_force
- **Market context**: bid_at_order, ask_at_order, mid_at_order
- **Risk indicators**: cancellation patterns, order size flags

### TradingDataSummary
Aggregated trading metrics including:
- **Volume metrics**: total_volume, total_notional, avg_trade_size
- **Direction analysis**: buy_trades, sell_trades, buy_volume, sell_volume
- **Risk metrics**: price_impact, largest_trade, order_cancel_rate
- **Timing analysis**: trades_by_session, avg_execution_time
- **P&L summary**: total_pnl, unrealized_pnl

## Usage Examples

### 1. Investigate Insider Trading Alert
```python
import requests

# Get raw data for alert
response = requests.post(
    'http://localhost:5000/api/v1/raw-data/alert/insider_20240101_120000',
    json={
        "trades": [...],
        "orders": [...],
        "trader_info": {...}
    }
)

raw_data = response.json()['raw_trading_data']

# Analyze execution patterns
for trade in raw_data['raw_trades']:
    print(f"Trade: {trade['quantity']} {trade['instrument']} at {trade['executed_price']}")
    print(f"Price deviation: {trade['price_deviation']:.2f}%")
    print(f"Market session: {trade['market_session']}")
```

### 2. Export Data for Regulatory Reporting
```python
# Export as CSV
response = requests.post(
    'http://localhost:5000/api/v1/raw-data/export/csv/insider_20240101_120000',
    json={...}
)

# Save file
with open('raw_trading_data.csv', 'wb') as f:
    f.write(response.content)
```

### 3. Search for Patterns
```python
# Search for large trades
response = requests.post(
    'http://localhost:5000/api/v1/raw-data/search',
    json={
        "trader_id": "trader_001",
        "min_quantity": 10000,
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-01-31T23:59:59Z"
    }
)

results = response.json()['results']
print(f"Found {results['total_trades']} large trades")
```

## Alert Integration

All alerts now include raw trading data access:

```json
{
  "id": "insider_20240101_120000",
  "type": "INSIDER_DEALING",
  "severity": "HIGH",
  "raw_data_available": true,
  "raw_data_endpoint": "/api/v1/raw-data/alert/insider_20240101_120000"
}
```

## Best Practices

### 1. Data Analysis
- Use the summary endpoint first to get an overview before diving into detailed data
- Export data for complex analysis using external tools
- Combine raw data with risk scores for comprehensive investigations

### 2. Performance
- Raw data endpoints cache results for efficiency
- Use search functionality to filter large datasets
- Consider date ranges when querying trader data

### 3. Compliance
- All raw data includes audit trails and regulatory fields
- Export functionality provides compliance-ready formats
- Data retention follows regulatory requirements

### 4. Investigation Workflow
1. **Alert Review**: Check alert details and raw_data_available flag
2. **Summary Analysis**: Get trading data summary for quick overview
3. **Detailed Investigation**: Access full raw trade and order data
4. **Pattern Analysis**: Use search to find related activities
5. **Documentation**: Export data for regulatory reporting

## Integration with Existing Features

### Regulatory Explainability
Raw trading data integrates with regulatory rationale generation:
- Trade details support evidence compilation
- Order patterns enhance regulatory narratives
- Market context provides justification for risk scores

### STOR Reporting
Raw data feeds directly into STOR record generation:
- Execution details populate transaction fields
- Risk indicators support suspicious activity descriptions
- Market context enhances regulatory justification

### Risk Assessment
Raw trading data enhances risk calculation:
- Execution timing improves insider dealing detection
- Order patterns strengthen spoofing identification
- Market context provides price manipulation evidence

## Troubleshooting

### Common Issues
1. **No data returned**: Ensure alert has associated trading data
2. **Export failures**: Check data size and format requirements
3. **Search timeout**: Narrow search criteria or use date ranges
4. **Missing fields**: Verify data processor includes all required fields

### Error Codes
- `400`: Invalid request or missing parameters
- `404`: Alert or trader not found
- `500`: Internal server error or data processing failure

## Future Enhancements

### Planned Features
1. **Real-time streaming**: Live raw data updates for active alerts
2. **Advanced analytics**: Machine learning-based pattern detection
3. **Visualization**: Interactive charts and graphs for data exploration
4. **Batch processing**: Bulk export and analysis capabilities
5. **API rate limiting**: Enhanced security and performance controls

### Integration Opportunities
1. **Third-party tools**: Integration with trading analysis platforms
2. **Regulatory systems**: Direct feeds to compliance databases
3. **Alerting systems**: Real-time notifications for data anomalies
4. **Reporting tools**: Integration with business intelligence platforms