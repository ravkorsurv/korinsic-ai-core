# Mixed-Role DQSI Scoring Clarification

## 🎯 **Important: KDE-Level Scoring Mechanism**

The **mixed-role framework** is the **configuration layer** that determines:
- Which KDEs to activate per data flow
- Which sub-dimensions to enable per role
- Flow-specific thresholds and validation depth

But the **actual scoring** happens at the **KDE level** using our established engine:

---

## 📊 **DQSI Scoring Flow**

### **1. Configuration Layer (Mixed-Role)**
```yaml
# Mixed-role configuration determines WHAT to score
trading_data_feed:
  role: consumer
  kdes:
    trader_id: {risk: high, weight: 3, validation: input_only}
    trade_time: {risk: high, weight: 3, validation: input_only}
    notional: {risk: high, weight: 3, validation: input_only}
    
surveillance_alerts:
  role: producer
  kdes:
    alert_id: {risk: high, weight: 3, validation: full_validation}
    alert_type: {risk: high, weight: 3, validation: full_validation}
    confidence_score: {risk: high, weight: 3, validation: full_validation}
```

### **2. KDE-Level Scoring Engine**
```python
# Each KDE gets individual score based on validation results
kde_scores = {
    'trader_id': 0.85,      # Individual KDE score (0.0-1.0)
    'trade_time': 0.72,     # Based on validation rules
    'notional': 0.91,       # Invalid scale: 0.1-0.7 for bad data
    'alert_id': 0.94,       # Synthetic KDEs: timeliness, coverage
    'alert_type': 0.88,     # Critical KDE cap: 0.75 if critical missing
    'confidence_score': 0.76
}
```

### **3. Final DQSI Aggregation**
```python
# Formula: Σ(KDE_score × risk_weight × tier_weight) / Σ(weights)
def calculate_dqsi_score(kde_scores, kde_configs):
    weighted_sum = 0
    total_weights = 0
    
    for kde_name, score in kde_scores.items():
        config = kde_configs[kde_name]
        risk_weight = config['weight']  # 3, 2, or 1
        tier_weight = get_tier_weight(kde_name)  # 1.0 or 0.75
        
        weighted_sum += score * risk_weight * tier_weight
        total_weights += risk_weight * tier_weight
    
    return weighted_sum / total_weights
```

---

## 🔧 **Mixed-Role KDE Scoring Example**

### **Client: Investment Bank with Mixed Roles**

**Consumer Flow (Trading Data):**
```yaml
# KDE Configuration
trading_data_kdes:
  trader_id: {risk: high, weight: 3, tier: foundational}    # 1.0 tier weight
  trade_time: {risk: high, weight: 3, tier: foundational}   # 1.0 tier weight
  notional: {risk: high, weight: 3, tier: foundational}     # 1.0 tier weight
  quantity: {risk: medium, weight: 2, tier: foundational}   # 1.0 tier weight
  
# Synthetic KDEs (system-level)
synthetic_kdes:
  trading_timeliness: {risk: high, weight: 3, tier: foundational}  # Feed latency
  trading_coverage: {risk: high, weight: 3, tier: foundational}    # Volume drops
```

**Producer Flow (Alert Data):**
```yaml
# KDE Configuration
alert_data_kdes:
  alert_id: {risk: high, weight: 3, tier: foundational}        # 1.0 tier weight
  alert_type: {risk: high, weight: 3, tier: foundational}      # 1.0 tier weight
  confidence_score: {risk: high, weight: 3, tier: enhanced}    # 0.75 tier weight
  trader_id: {risk: high, weight: 3, tier: enhanced}           # 0.75 tier weight
  
# Synthetic KDEs (system-level)
synthetic_kdes:
  alert_timeliness: {risk: high, weight: 3, tier: foundational}    # Processing SLA
  alert_coverage: {risk: high, weight: 3, tier: foundational}      # Alert volume reconciliation
```

### **KDE-Level Scoring Results**

**Trading Data (Consumer Flow):**
```python
# Individual KDE Scores
kde_scores = {
    'trader_id': 0.85,           # Good data quality
    'trade_time': 0.72,          # Some timestamp issues
    'notional': 0.91,            # Clean financial data
    'quantity': 0.88,            # Minor format issues
    'trading_timeliness': 0.65,  # Feed delays
    'trading_coverage': 0.94     # Volume consistent
}

# Weighted Calculation
weighted_sum = (0.85×3×1.0) + (0.72×3×1.0) + (0.91×3×1.0) + (0.88×2×1.0) + (0.65×3×1.0) + (0.94×3×1.0)
             = 2.55 + 2.16 + 2.73 + 1.76 + 1.95 + 2.82 = 13.97

total_weights = (3×1.0) + (3×1.0) + (3×1.0) + (2×1.0) + (3×1.0) + (3×1.0) = 17.0

trading_dqsi_score = 13.97 / 17.0 = 0.822 (82.2%)
```

**Alert Data (Producer Flow):**
```python
# Individual KDE Scores
kde_scores = {
    'alert_id': 0.94,            # Clean alert IDs
    'alert_type': 0.88,          # Some classification issues
    'confidence_score': 0.76,    # Accuracy validation applied
    'trader_id': 0.85,           # Cross-system consistency
    'alert_timeliness': 0.58,    # Processing delays
    'alert_coverage': 0.82       # Volume reconciliation
}

# Weighted Calculation (note different tier weights)
weighted_sum = (0.94×3×1.0) + (0.88×3×1.0) + (0.76×3×0.75) + (0.85×3×0.75) + (0.58×3×1.0) + (0.82×3×1.0)
             = 2.82 + 2.64 + 1.71 + 1.91 + 1.74 + 2.46 = 13.28

total_weights = (3×1.0) + (3×1.0) + (3×0.75) + (3×0.75) + (3×1.0) + (3×1.0) = 16.5

alert_dqsi_score = 13.28 / 16.5 = 0.805 (80.5%)
```

---

## 🎯 **Key Integration Points**

### **1. Mixed-Role Configuration → KDE Selection**
```yaml
# Configuration determines which KDEs to score
consumer_flows:
  - Include: foundational KDEs only
  - Exclude: enhanced validation KDEs
  - Synthetic: basic timeliness, coverage
  
producer_flows:
  - Include: all KDEs (foundational + enhanced)
  - Synthetic: comprehensive timeliness, coverage, accuracy
```

### **2. Flow-Specific Validation Rules**
```python
# Consumer flows: Input validation only
def validate_consumer_kde(kde_value, kde_config):
    if kde_config['validation'] == 'input_only':
        return basic_validation(kde_value)  # Format, null, range checks
    
# Producer flows: Full validation
def validate_producer_kde(kde_value, kde_config):
    if kde_config['validation'] == 'full_validation':
        return comprehensive_validation(kde_value)  # + accuracy, uniqueness, consistency
```

### **3. Critical KDE Cap (0.75 Maximum)**
```python
# Applied regardless of consumer/producer role
def apply_critical_kde_cap(kde_scores, critical_kdes):
    missing_critical = [kde for kde in critical_kdes if kde not in kde_scores]
    
    if missing_critical:
        return min(0.75, calculate_dqsi_score(kde_scores))
    else:
        return calculate_dqsi_score(kde_scores)
```

### **4. Confidence Index Calculation**
```python
# Confidence factors by role
def calculate_confidence_index(kde_scores, data_flow_role):
    base_confidence = len(kde_scores) / total_possible_kdes
    
    # Role-specific modifiers
    if data_flow_role == 'consumer':
        imputation_penalty = 0.05  # Lighter penalty for consumer
    else:  # producer
        imputation_penalty = 0.10  # Stricter penalty for producer
    
    return base_confidence - imputation_penalty
```

---

## 🎯 **Summary**

The **mixed-role framework** is the **configuration layer** that:
- Determines which KDEs to activate per data flow
- Sets role-specific validation depth
- Configures flow-specific thresholds

The **actual scoring** remains **KDE-level** using our established engine:
- Individual KDE scores (0.0-1.0, invalid: 0.1-0.7)
- Risk weights (high=3, medium=2, low=1)
- Tier weights (foundational=1.0, enhanced=0.75)
- Final aggregation: Σ(KDE_score × risk_weight × tier_weight) / Σ(weights)

This ensures **consistent scoring methodology** across all data flows while enabling **role-specific configuration** for practical implementation.