# Qatar Risk Typology Implementation Plan

## Implementation Strategy

**Consolidation Approach**: Extend existing insider dealing model + create 3 new focused models rather than 5 separate models.

### Models to Implement:
1. **Enhanced Insider Dealing Model** (extend existing) - covers news timing + state information
2. **Commodity Market Manipulation Model** (new) - illiquid contracts + benchmark interference  
3. **Circular Trading Detection Model** (new) - fictitious/wash trades
4. **Cross-Desk Collusion Model** (new) - coordination detection

**Total Development Time Estimate: 18-20 hours**

---

## Phase 1: Enhance Existing Insider Dealing Model (4-5 hours)

### Files to Modify:

#### 1. `src/models/bayesian/insider_dealing/nodes.py`
**Changes**: Add new evidence nodes for Qatar requirements
**Time**: 1.5 hours

```python
# Add these new node definitions to self.node_definitions:
'news_timing': {
    'type': 'news_timing',
    'states': ['normal_timing', 'suspicious_timing', 'highly_suspicious_timing'],
    'description': 'News-trade timing analysis',
    'fallback_prior': [0.85, 0.12, 0.03]
},
'state_information_access': {
    'type': 'state_information',
    'states': ['no_access', 'potential_access', 'clear_access'],
    'description': 'State-level information access',
    'fallback_prior': [0.88, 0.1, 0.02]
},
'announcement_correlation': {
    'type': 'evidence',
    'states': ['no_correlation', 'weak_correlation', 'strong_correlation'],
    'description': 'Trading correlation with announcements',
    'fallback_prior': [0.80, 0.15, 0.05]
}
```

#### 2. `src/models/bayesian/insider_dealing/model.py`
**Changes**: Update required nodes for Qatar context
**Time**: 1 hour

```python
def get_required_nodes(self) -> List[str]:
    if self.use_latent_intent:
        return [
            'trade_pattern', 'comms_intent', 'pnl_drift',
            'profit_motivation', 'access_pattern', 'order_behavior', 'comms_metadata',
            'news_timing', 'state_information_access', 'announcement_correlation'  # NEW
        ]
    else:
        return [
            'trade_pattern', 'comms_intent', 'pnl_drift', 
            'news_timing', 'state_information_access'  # NEW
        ]
```

#### 3. `src/core/node_library.py`
**Changes**: Add new node classes
**Time**: 1.5 hours

```python
class NewsTimingNode(EvidenceNode):
    """News-trade timing analysis node"""
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["normal_timing", "suspicious_timing", "highly_suspicious_timing"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)

class StateInformationNode(EvidenceNode):
    """State-level information access node"""
    def __init__(self, name: str, description: str = "", fallback_prior: Optional[List[float]] = None):
        states = ["no_access", "potential_access", "clear_access"]
        super().__init__(name, states, description=description, fallback_prior=fallback_prior)
```

#### 4. `src/core/model_construction.py`
**Changes**: Update CPT structure for enhanced model
**Time**: 1 hour

```python
# Update build_insider_dealing_bn_with_latent_intent() to include new nodes
# Add CPDs for news_timing, state_information_access, announcement_correlation
# Update latent_intent CPD to include new evidence paths
```

---

## Phase 2: Create Commodity Market Manipulation Model (5-6 hours)

### New Files to Create:

#### 1. `src/models/bayesian/commodity_manipulation/`
**New Directory Structure**:
```
src/models/bayesian/commodity_manipulation/
├── __init__.py
├── model.py
├── nodes.py
├── config.py
```

#### 2. `src/models/bayesian/commodity_manipulation/model.py`
**Time**: 2.5 hours

```python
class CommodityManipulationModel:
    """Commodity market manipulation detection model"""
    
    def get_required_nodes(self) -> List[str]:
        return [
            'liquidity_context',
            'benchmark_timing', 
            'order_clustering',
            'price_impact_ratio',
            'volume_participation',
            'cross_venue_coordination',
            'latent_manipulation_intent'
        ]
```

#### 3. `src/models/bayesian/commodity_manipulation/nodes.py`
**Time**: 1.5 hours

```python
class CommodityManipulationNodes:
    """Node definitions for commodity manipulation model"""
    
    def __init__(self):
        self.node_definitions = {
            'liquidity_context': {
                'type': 'liquidity_context',
                'states': ['liquid', 'moderate', 'illiquid'],
                'description': 'Market liquidity conditions',
                'fallback_prior': [0.6, 0.3, 0.1]
            },
            'benchmark_timing': {
                'type': 'benchmark_timing',
                'states': ['outside_window', 'near_window', 'during_window'],
                'description': 'Benchmark window activity',
                'fallback_prior': [0.8, 0.15, 0.05]
            },
            # ... additional nodes
        }
```

#### 4. `src/models/bayesian/commodity_manipulation/config.py`
**Time**: 1 hour

```python
class CommodityManipulationConfig:
    """Configuration for commodity manipulation model"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.default_config = {
            'risk_thresholds': {
                'low_risk': 0.25,
                'medium_risk': 0.55,
                'high_risk': 0.75
            },
            'model_parameters': {
                'use_latent_intent': True,
                'benchmark_window_sensitivity': 0.8
            }
        }
```

#### 5. Update `src/core/node_library.py`
**Time**: 1 hour

```python
class LiquidityContextNode(EvidenceNode):
    """Market liquidity conditions node"""
    
class BenchmarkTimingNode(EvidenceNode):
    """Benchmark window timing node"""
    
class OrderClusteringNode(EvidenceNode):
    """Order clustering analysis node"""
```

---

## Phase 3: Create Circular Trading Detection Model (4-5 hours)

### New Files to Create:

#### 1. `src/models/bayesian/circular_trading/`
**New Directory Structure**:
```
src/models/bayesian/circular_trading/
├── __init__.py
├── model.py  
├── nodes.py
├── config.py
```

#### 2. `src/models/bayesian/circular_trading/model.py`
**Time**: 2 hours

```python
class CircularTradingModel:
    """Circular/wash trading detection model"""
    
    def get_required_nodes(self) -> List[str]:
        return [
            'counterparty_relationship',
            'risk_transfer_analysis', 
            'price_negotiation_pattern',
            'settlement_coordination',
            'beneficial_ownership',
            'trade_sequence_analysis',
            'latent_coordination_intent'
        ]
```

#### 3. `src/models/bayesian/circular_trading/nodes.py`
**Time**: 1.5 hours

#### 4. `src/models/bayesian/circular_trading/config.py`
**Time**: 0.5 hours

#### 5. Update `src/core/node_library.py`
**Time**: 1 hour

```python
class CounterpartyRelationshipNode(EvidenceNode):
    """Counterparty relationship analysis"""
    
class RiskTransferNode(EvidenceNode):
    """Risk transfer analysis"""
    
class CoordinationLatentIntentNode(LatentIntentNode):
    """Latent coordination intent"""
```

---

## Phase 4: Create Cross-Desk Collusion Model (4-5 hours)

### New Files to Create:

#### 1. `src/models/bayesian/cross_desk_collusion/`
**New Directory Structure**:
```
src/models/bayesian/cross_desk_collusion/
├── __init__.py
├── model.py
├── nodes.py  
├── config.py
```

#### 2. `src/models/bayesian/cross_desk_collusion/model.py`
**Time**: 2 hours

```python
class CrossDeskCollusionModel:
    """Cross-desk collusion detection model"""
    
    def get_required_nodes(self) -> List[str]:
        return [
            'trading_correlation',
            'communication_patterns',
            'profit_sharing_indicators',
            'order_synchronization', 
            'information_sharing',
            'market_segmentation',
            'latent_collusion_intent'
        ]
```

#### 3. `src/models/bayesian/cross_desk_collusion/nodes.py`
**Time**: 1.5 hours

#### 4. `src/models/bayesian/cross_desk_collusion/config.py`
**Time**: 0.5 hours

#### 5. Update `src/core/node_library.py`
**Time**: 1 hour

```python
class TradingCorrelationNode(EvidenceNode):
    """Cross-desk trading correlation"""
    
class CommunicationPatternNode(EvidenceNode):
    """Communication pattern analysis"""
    
class CollusionLatentIntentNode(LatentIntentNode):
    """Latent collusion intent"""
```

---

## Phase 5: Integration and Registry Updates (1-2 hours)

### Files to Modify:

#### 1. `src/models/bayesian/registry.py`
**Changes**: Register new models
**Time**: 0.5 hours

```python
def register_qatar_models(self):
    """Register Qatar-specific models"""
    self.register_model('commodity_manipulation', CommodityManipulationModel)
    self.register_model('circular_trading', CircularTradingModel)
    self.register_model('cross_desk_collusion', CrossDeskCollusionModel)
```

#### 2. `src/models/bayesian/__init__.py`
**Changes**: Add new model imports
**Time**: 0.5 hours

#### 3. `src/core/regulatory_explainability.py`
**Changes**: Add Qatar-specific regulatory mappings
**Time**: 1 hour

```python
self.qatar_regulatory_basis_map = {
    'insider_dealing': 'QFMA Code of Market Conduct Article 6 - Insider Dealing',
    'commodity_manipulation': 'QFMA Code of Market Conduct Article 5 - Market Manipulation',
    'circular_trading': 'QFMA Code of Market Conduct Article 7 - Misleading Practices',
    'cross_desk_collusion': 'QFMA Code of Market Conduct Article 9 - Market Abuse'
}
```

---

## Phase 6: Configuration and Testing (3-4 hours)

### New Files to Create:

#### 1. `config/qatar_market_conduct.json`
**Time**: 1 hour

```json
{
    "qfma_compliance": {
        "risk_thresholds": {
            "insider_dealing": {"low_risk": 0.20, "medium_risk": 0.50, "high_risk": 0.70},
            "commodity_manipulation": {"low_risk": 0.25, "medium_risk": 0.55, "high_risk": 0.75},
            "circular_trading": {"low_risk": 0.30, "medium_risk": 0.60, "high_risk": 0.80},
            "cross_desk_collusion": {"low_risk": 0.35, "medium_risk": 0.65, "high_risk": 0.85}
        }
    }
}
```

#### 2. `tests/unit/test_qatar_models.py`
**Time**: 2 hours

```python
class TestQatarModels:
    """Test suite for Qatar-specific models"""
    
    def test_enhanced_insider_dealing_model(self):
        """Test enhanced insider dealing with news timing"""
        
    def test_commodity_manipulation_model(self):
        """Test commodity manipulation detection"""
        
    def test_circular_trading_model(self):
        """Test circular trading detection"""
        
    def test_cross_desk_collusion_model(self):
        """Test cross-desk collusion detection"""
```

#### 3. `tests/fixtures/qatar_test_data.json`
**Time**: 1 hour

---

## Summary

**Total Implementation Time: 18-20 hours**

### File Creation Summary:
- **New Model Directories**: 3 new model directories (12 new files)
- **Modified Existing Files**: 6 files  
- **New Config Files**: 2 files
- **New Test Files**: 2 files

### Key Benefits of This Approach:
1. **Reuses existing insider dealing model** - just extends it for Qatar requirements
2. **Focused new models** - only create what's truly needed
3. **Maintains existing architecture** - uses established patterns
4. **Backward compatible** - doesn't break existing functionality

### Next Steps After Implementation:
1. Performance testing with Qatar-specific data
2. Regulatory validation with QFMA requirements
3. Documentation updates
4. Deployment planning