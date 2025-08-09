# Evidence Mapping Implementation Summary - All Models

## Overview
All Bayesian models in the Kor.ai Risk Engine now support the standard evidence mapping pattern, ensuring consistency across the platform.

## Completed Implementations

### 1. Economic Withholding ✅
- **Evidence Nodes (15)**: fuel_cost_variance, plant_efficiency, marginal_cost_deviation, heat_rate_variance, load_factor, market_tightness, competitive_context, transmission_constraint, bid_shape_anomaly, offer_withdrawal_pattern, cross_plant_coordination, capacity_utilization, markup_consistency, opportunity_pricing, fuel_price_correlation
- **Status**: Fully implemented with backward compatibility

### 2. Spoofing ✅
- **Evidence Nodes (6)**: order_clustering, price_impact_ratio, volume_participation, order_behavior, intent_to_execute, order_cancellation
- **Status**: Implemented with dual mode (legacy/new) support

### 3. Market Cornering ✅
- **Evidence Nodes (6)**: market_concentration, position_accumulation, supply_control, liquidity_manipulation, price_distortion, delivery_constraint
- **Status**: Fully integrated with standard mapper

### 4. Circular Trading ✅
- **Evidence Nodes (6)**: counterparty_relationship, risk_transfer_analysis, price_negotiation_pattern, settlement_coordination, beneficial_ownership, trade_sequence_analysis
- **Status**: Fully integrated with standard mapper

### 5. Cross-Desk Collusion ✅
- **Evidence Nodes (6)**: comms_metadata, profit_motivation, order_behavior, cross_venue_coordination, access_pattern, market_segmentation
- **Status**: Fully integrated with standard mapper

### 6. Commodity Manipulation ✅
- **Evidence Nodes (6)**: liquidity_context, benchmark_timing, order_clustering, price_impact_ratio, volume_participation, cross_venue_coordination
- **Status**: Fully integrated (reuses nodes from other models)

### 7. Insider Dealing ✅
- **Evidence Nodes (enhanced)**: trade_pattern, comms_intent, pnl_drift, news_timing, state_information_access, announcement_correlation, profit_motivation, access_pattern, order_behavior, comms_metadata, mnpi_access
- **Enhanced BN Integration**: In the latent-intent model, `mnpi_access` feeds `latent_intent` (keeps `risk_factor` at 4 parents: trade_pattern, comms_intent, pnl_drift, latent_intent). Aggregator ignores external `mnpi_access` to avoid double-counting when present in the BN.
- **Performance variant**: `build_insider_dealing_bn_with_latent_intent_grouped()` groups evidence into two intermediates (`intent_behavior_aggregate`, `access_timing_aggregate`), reducing `latent_intent` parent combinations from 3^8 = 6561 to 3^4 = 81. Uses structured CPDs (softmax-based) for aggregates and latent intent with monotonic constraints, enabling calibration and linear parameter growth.
- **Mapping**:
  - `mnpi_access`: from HR/market data (executive/high or >2 indicators → clear; senior/≥1 indicator → potential; else none)
  - `news_timing`: explicit mapper based on minutes proximity to price-sensitive news
  - `state_information_access`: explicit mapper from state access indicators
- **Threshold constants**: `HIGHLY_SUSPICIOUS_MINUTES = 5`, `SUSPICIOUS_MINUTES = 60` (in `core/evidence_mapper.py`) replace magic numbers.
- **Status**: Enhanced model preferred; baseline retained for backward compatibility.

### 8. Wash Trade Detection ✅
- **Evidence Nodes (6)**: wash_trade_likelihood, signal_distortion_index, algo_reaction_sensitivity, strategy_leg_overlap, price_impact_anomaly, implied_liquidity_conflict
- **Status**: Original implementation already uses standard pattern

## Key Features

### 1. Centralized Evidence Mapping
All evidence mapping functions are centralized in `src/core/evidence_mapper.py`:
- 50+ mapping functions covering all models
- Consistent numeric state mapping (0, 1, 2)
- Reusable functions across models with similar nodes

### 2. Standardized Data Flow
```
Raw Data → DataProcessor → Evidence Mapper → Numeric Evidence → Bayesian Model → Risk Score
```

### 3. Unified API Integration
All models can be analyzed through:
- Individual methods: `analyze_<model_type>()`
- Unified endpoint: `/api/v1/analyze`

### 4. Evidence Format
**Input Structure**:
```json
{
  "model_type": {
    "data_source_1": {...},
    "data_source_2": {...}
  }
}
```

**Mapped Evidence**:
```json
{
  "node_name": 0,  // Numeric state (0, 1, or 2)
  "another_node": 1
}
```

## Usage Examples

### Analyze Multiple Models
```python
from src.core.bayesian_engine import BayesianEngine

engine = BayesianEngine()

# Analyze with processed data
results = {
    'insider_dealing': engine.analyze_insider_dealing(processed_data),
    'spoofing': engine.analyze_spoofing(processed_data),
    'market_cornering': engine.analyze_market_cornering(processed_data),
    'circular_trading': engine.analyze_circular_trading(processed_data),
    'cross_desk_collusion': engine.analyze_cross_desk_collusion(processed_data),
    'commodity_manipulation': engine.analyze_commodity_manipulation(processed_data),
    'economic_withholding': engine.analyze_economic_withholding(processed_data)
}
```

### Direct Evidence Mapping
```python
from src.core.evidence_mapper import (
    map_spoofing_evidence,
    map_market_cornering_evidence,
    map_circular_trading_evidence
)

# Map specific model evidence
spoofing_evidence = map_spoofing_evidence(spoofing_data)
cornering_evidence = map_market_cornering_evidence(cornering_data)
circular_evidence = map_circular_trading_evidence(circular_data)
```

## Benefits

1. **Consistency**: All models follow the same evidence mapping pattern
2. **Maintainability**: Centralized mapping logic in one file
3. **Extensibility**: Easy to add new nodes or models
4. **Testability**: Standardized format simplifies testing
5. **Reusability**: Common nodes shared across models

## Node Reuse Matrix

| Node | Economic Withholding | Spoofing | Market Cornering | Circular Trading | Cross-Desk Collusion | Commodity Manipulation |
|------|---------------------|----------|------------------|------------------|---------------------|----------------------|
| price_impact_ratio | ✓ | ✓ | | | | ✓ |
| volume_participation | ✓ | ✓ | | | | ✓ |
| liquidity_context | ✓ | | | | | ✓ |
| benchmark_timing | ✓ | | | | | ✓ |
| order_clustering | | ✓ | | | | ✓ |
| cross_venue_coordination | | | | | ✓ | ✓ |
| order_behavior | | ✓ | | | ✓ | |
| profit_motivation | ✓ | | | | ✓ | |

## Next Steps

1. **Performance Optimization**: Consider caching mapped evidence for repeated analyses
2. **Validation Layer**: Add input validation for each data source
3. **Dynamic Thresholds**: Make evidence mapping thresholds configurable
4. **Monitoring**: Add metrics for evidence quality and coverage