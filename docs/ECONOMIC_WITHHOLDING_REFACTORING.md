# Economic Withholding Model Refactoring Summary

## Overview
The economic withholding model has been refactored to align with the standard evidence mapping pattern used by other models in the Kor.ai Bayesian Risk Engine.

## Key Changes

### 1. Evidence Mapping Functions Added to `evidence_mapper.py`
Added 15 new mapping functions for economic withholding evidence nodes:
- `map_fuel_cost_variance()` - Maps fuel cost anomalies to states 0/1/2
- `map_plant_efficiency()` - Maps plant efficiency to optimal/suboptimal/impaired
- `map_marginal_cost_deviation()` - Maps cost markup percentages
- `map_heat_rate_variance()` - Maps heat rate consistency
- `map_load_factor()` - Maps system demand levels
- `map_market_tightness()` - Maps supply-demand balance
- `map_competitive_context()` - Maps market concentration
- `map_transmission_constraint()` - Maps grid constraints
- `map_bid_shape_anomaly()` - Maps bidding curve patterns
- `map_offer_withdrawal_pattern()` - Maps capacity withholding
- `map_cross_plant_coordination()` - Maps coordinated behavior
- `map_capacity_utilization()` - Maps plant usage patterns
- `map_markup_consistency()` - Maps pricing consistency
- `map_opportunity_pricing()` - Maps opportunistic pricing
- `map_fuel_price_correlation()` - Maps fuel-price relationships

### 2. Model Integration Updates

#### Economic Withholding Model (`economic_withholding/model.py`)
- Added `analyze_with_standard_evidence()` method for standard pattern integration
- Added helper methods:
  - `_get_state_index()` - Converts string states to numeric indices
  - `_convert_numeric_to_string_evidence()` - For backward compatibility
- Updated `_extract_evidence_from_analysis()` to use standard mapper

#### Bayesian Engine (`bayesian_engine.py`)
- Added `analyze_economic_withholding()` method following standard pattern
- Updated `get_model_info()` to include economic withholding status

#### Main Application (`app.py`)
- Updated `/api/v1/analyze` endpoint to optionally analyze economic withholding
- Added economic withholding scores to response when relevant data present

### 3. Evidence Format Standardization

**Before (String-based):**
```python
evidence = {
    'fuel_cost_variance': 'high_variance',
    'plant_efficiency': 'suboptimal',
    'load_factor': 'peak_demand'
}
```

**After (Numeric-based):**
```python
evidence = {
    'fuel_cost_variance': 2,  # 0=aligned, 1=moderate, 2=high
    'plant_efficiency': 1,    # 0=optimal, 1=suboptimal, 2=impaired
    'load_factor': 2         # 0=low, 1=normal, 2=peak
}
```

### 4. Backward Compatibility
- Original `analyze_economic_withholding()` method remains unchanged
- New integration method works alongside existing functionality
- String-to-numeric conversion handled internally

## Benefits

1. **Consistency**: Economic withholding now follows the same evidence mapping pattern as other models
2. **Maintainability**: All evidence mapping logic centralized in `evidence_mapper.py`
3. **Integration**: Can be analyzed through standard `/api/v1/analyze` endpoint
4. **Extensibility**: Easy to add new evidence nodes following established pattern

## Usage

### Standard Pattern (New)
```python
# Through BayesianEngine
engine = BayesianEngine()
result = engine.analyze_economic_withholding(processed_data)

# Through unified analyze endpoint
POST /api/v1/analyze
{
    "plant_data": {...},
    "market_data": {...},
    "fuel_prices": {...}
}
```

### Legacy Pattern (Still Supported)
```python
# Direct model usage
model = EconomicWithholdingModel()
result = model.analyze_economic_withholding(
    plant_data={...},
    offers=[...],
    market_data={...},
    fuel_prices={...}
)

# Through dedicated endpoint
POST /api/v1/analyze/economic-withholding
```

## Next Steps

1. Implement evidence mapping for remaining models:
   - Spoofing
   - Market Cornering
   - Circular Trading
   - Cross-Desk Collusion
   - Commodity Manipulation

2. Consider migrating all models to use numeric evidence internally (pgmpy supports both)

3. Add Evidence Sufficiency Index (ESI) calculation for economic withholding