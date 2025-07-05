# Dynamic Bayesian Model Construction System

## Overview

The Bayesian Risk Engine now supports **true dynamic model construction** where Bayesian network structures (nodes, edges, CPDs) are loaded from configuration files rather than hardcoded. This enables:

- **Runtime model modifications** without code changes
- **Multiple model types** (insider dealing, spoofing, etc.)
- **Advanced features** like fallback priors and node descriptions
- **Global settings** for thresholds and multipliers
- **Extensible architecture** for new risk types

## Architecture

### 1. Configuration-Driven Model Loading

The system loads models from `bayesian_model_config.json` with this structure:

```json
{
  "models": {
    "insider_dealing": {
      "nodes": [...],
      "edges": [...],
      "cpds": [...]
    },
    "spoofing": {
      "nodes": [...],
      "edges": [...],
      "cpds": [...]
    }
  },
  "global_settings": {
    "default_fallback_prior": [0.8, 0.15, 0.05],
    "news_context_suppression": {...},
    "risk_thresholds": {...}
  }
}
```

### 2. Node Definition

Each node includes:
- **name**: Node identifier
- **states**: Possible values (e.g., ["Low", "Medium", "High"])
- **description**: Human-readable description
- **fallback_prior**: Default probabilities when evidence is missing

```json
{
  "name": "MaterialInfo",
  "states": ["No access", "Potential access", "Clear access"],
  "description": "Access to material non-public information",
  "fallback_prior": [0.7, 0.25, 0.05]
}
```

### 3. Edge Definition

Edges define the Bayesian network structure:

```json
[
  ["MaterialInfo", "Risk"],
  ["TradingActivity", "Risk"],
  ["MaterialInfo", "Timing"]
]
```

### 4. CPD (Conditional Probability Distribution)

CPDs define the probability tables:

```json
{
  "variable": "Risk",
  "evidence": ["MaterialInfo", "TradingActivity", "Timing", "PriceImpact"],
  "values": [[0.95, 0.9, ...], [0.04, 0.08, ...], [0.01, 0.02, ...]]
}
```

## Features

### ✅ Dynamic Model Loading
- Models are loaded from config at runtime
- Fallback to hardcoded models if config missing
- Automatic validation of model structure

### ✅ Multiple Model Support
- **Insider Dealing**: 5 nodes, 6 edges, 5 CPDs
- **Spoofing**: 5 nodes, 6 edges, 5 CPDs
- Extensible for new risk types

### ✅ Advanced Node Features
- **Descriptions**: Human-readable node explanations
- **Fallback Priors**: Default probabilities for missing evidence
- **State Validation**: Automatic state count validation

### ✅ Global Settings
- **News Context Suppression**: Configurable multipliers for explained moves
- **Risk Thresholds**: Adjustable low/medium/high risk boundaries
- **Default Fallback Prior**: Global default for missing evidence

### ✅ Runtime Modifications
- Add new nodes without code changes
- Modify CPDs through config updates
- Restart engine to apply changes

## Usage Examples

### 1. Basic Model Loading

```python
from core.bayesian_engine import BayesianEngine

# Loads models from config automatically
bayesian_engine = BayesianEngine()

# Get model information
models_info = bayesian_engine.get_models_info()
print(f"Models loaded: {models_info['models_loaded']}")
```

### 2. Risk Calculation

```python
# Calculate insider dealing risk
insider_result = bayesian_engine.calculate_insider_dealing_risk(processed_data)
print(f"Risk Score: {insider_result['overall_score']}")
print(f"Risk Level: {insider_result['risk_level']}")

# Calculate spoofing risk
spoofing_result = bayesian_engine.calculate_spoofing_risk(processed_data)
print(f"Risk Score: {spoofing_result['overall_score']}")
print(f"Risk Level: {spoofing_result['risk_level']}")
```

### 3. Adding a New Node

To add a new node "MarketVolatility":

1. **Add to config**:
```json
{
  "name": "MarketVolatility",
  "states": ["Low", "Medium", "High"],
  "description": "Market volatility level",
  "fallback_prior": [0.6, 0.3, 0.1]
}
```

2. **Add edge** (optional):
```json
["MarketVolatility", "Risk"]
```

3. **Add CPD**:
```json
{
  "variable": "MarketVolatility",
  "values": [[0.6], [0.3], [0.1]]
}
```

4. **Restart engine** to load new model

### 4. Modifying Global Settings

```json
{
  "global_settings": {
    "news_context_suppression": {
      "explained_move_multiplier": 0.3,  // More aggressive suppression
      "partial_move_multiplier": 0.6,
      "unexplained_move_multiplier": 1.0
    },
    "risk_thresholds": {
      "low_risk": 0.2,    // More sensitive
      "medium_risk": 0.5,
      "high_risk": 0.7
    }
  }
}
```

## Testing

### Test Scripts

1. **`test_dynamic_model.py`**: Basic dynamic model functionality
2. **`test_advanced_features.py`**: Advanced features and extensibility
3. **`test_engine_integration.py`**: Full system integration

### Running Tests

```bash
# Test basic functionality
python test_dynamic_model.py

# Test advanced features
python test_advanced_features.py

# Test full integration
python test_engine_integration.py
```

## Extending the System

### Adding New Risk Types

1. **Add model to config**:
```json
"market_manipulation": {
  "nodes": [...],
  "edges": [...],
  "cpds": [...]
}
```

2. **Add model creation method**:
```python
def _create_market_manipulation_model(self):
    # Load from config or fallback
```

3. **Add risk calculation method**:
```python
def calculate_market_manipulation_risk(self, data):
    # Implement risk calculation
```

4. **Update evidence mapper** for new data sources

### Best Practices

1. **Backup config** before modifications
2. **Validate CPDs** when adding new parents to existing nodes
3. **Test thoroughly** after model changes
4. **Document node meanings** in descriptions
5. **Use meaningful state names** for clarity

## Benefits

### 🔧 **Flexibility**
- Modify models without code deployment
- A/B test different model configurations
- Rapid prototyping of new risk factors

### 📊 **Maintainability**
- Clear separation of model logic and structure
- Version control for model configurations
- Easy rollback to previous configurations

### 🚀 **Scalability**
- Add new risk types without code changes
- Support multiple model variants
- Configurable thresholds and parameters

### 🎯 **Accuracy**
- Fine-tune probabilities through config
- Adjust sensitivity without redeployment
- Domain expert input without developer involvement

## Conclusion

The dynamic model construction system transforms the Bayesian Risk Engine from a static, hardcoded system into a flexible, configurable platform that can adapt to changing requirements and new risk types without code modifications. This enables rapid iteration, domain expert involvement, and operational flexibility while maintaining the sophisticated risk detection capabilities.

The system successfully demonstrates:
- ✅ **True dynamic model construction**
- ✅ **Multiple model type support**
- ✅ **Advanced configuration features**
- ✅ **Runtime modification capabilities**
- ✅ **Extensible architecture**
- ✅ **Comprehensive testing framework**

This represents a significant advancement in the system's flexibility and operational capabilities. 