# 📌 Person-Centric Surveillance in Korinsic

## Overview

This document describes the implementation of **Individual-Centric Surveillance** in Korinsic, transitioning from account-based alerts to person-based probabilistic detection across all risk typologies.

### 🧠 Rationale

Traditional surveillance systems rely on static, account-level rules (e.g., "Account A traded before news X"). However, individuals frequently operate across multiple accounts, desks, or entities — especially in complex structures like broker-dealer hybrids, asset managers, or regional affiliates.

To effectively identify misconduct such as insider dealing, spoofing, or front-running, Korinsic now models person-centric behavior by resolving identities across fragmented data streams and assigning probabilistic abuse scores at the individual level — not just per trade or per account.

## 🧱 Architecture Overview

The person-centric surveillance system consists of four main pillars:

### 1. Entity Resolution Layer (Identity Graph)
**Location**: `src/core/entity_resolution.py`

- **Input**: Trading accounts, email IDs, desk affiliation, HR data, comms handles
- **Output**: Unique PersonID with confidence weighting per identity link
- **Tools**: Probabilistic record linkage, fuzzy matching, HR data overrides
- **Maintained**: Dynamic graph to update new links over time

### 2. Person-Level Evidence Aggregation
**Location**: `src/core/person_evidence_aggregator.py`

- **Input**: Trading data, communication data, timing events across all linked accounts
- **Output**: Aggregated evidence profiles with cross-account correlation analysis
- **Features**: Pattern detection, temporal analysis, cross-account synchronization

### 3. Cross-Typology Signal Sharing
**Location**: `src/core/cross_typology_engine.py`

- **Input**: Risk assessments from different typologies
- **Output**: Cross-typology signals that influence priors
- **Features**: Dynamic correlation matrix, signal decay, escalation factors

### 4. Person-Centric Alert Generation
**Location**: `src/core/person_centric_alert_generator.py`

- **Input**: Aggregated evidence and cross-typology signals
- **Output**: PersonID-based probabilistic alerts with regulatory rationale
- **Features**: STOR eligibility, explainability, evidence trails

## 🚀 Quick Start

### Installation

```python
# The system integrates with the existing Korinsic infrastructure
from src.core.person_centric_surveillance_engine import create_surveillance_engine

# Create the surveillance engine
engine = create_surveillance_engine("config/person_centric_surveillance.json")
```

### Basic Usage

```python
from src.models.person_centric import RiskTypology
from src.models.trading_data import RawTradeData

# Example trade data
trades = [
    RawTradeData(
        trade_id="trade_001",
        execution_timestamp="2024-01-15T10:30:00Z",
        instrument="equity",
        symbol="AAPL",
        trader_id="account_001",
        trader_name="John Smith",
        # ... other fields
    )
]

# Process surveillance data
results = engine.process_surveillance_data(
    trade_data=trades,
    target_typologies=[RiskTypology.INSIDER_DEALING, RiskTypology.SPOOFING]
)

# Access results
print(f"Alerts generated: {results['alerts_generated']}")
for alert in results['alerts']:
    print(f"Person {alert['person_name']}: {alert['probability_score']:.1%} risk")
```

## 📊 Data Models

### Core Person-Centric Models

#### PersonRiskProfile
```python
@dataclass
class PersonRiskProfile:
    person_id: str
    primary_name: Optional[str]
    linked_accounts: Set[str]
    linked_desks: Set[str]
    identity_confidence: float
    risk_scores: Dict[RiskTypology, float]
    cross_risk_correlations: Dict[str, float]
    aggregated_evidence: Dict[str, Any]
```

#### PersonCentricAlert
```python
@dataclass
class PersonCentricAlert:
    alert_id: str
    person_id: str
    risk_typology: RiskTypology
    severity: AlertSeverity
    probability_score: float  # 0.0 to 1.0
    confidence_score: float   # 0.0 to 1.0
    involved_accounts: List[str]
    cross_account_patterns: List[Dict[str, Any]]
    regulatory_rationale: str
    stor_eligible: bool
    explanation_summary: str
```

## 🔧 Configuration

The system uses a comprehensive configuration file at `config/person_centric_surveillance.json`:

### Key Configuration Sections

#### Entity Resolution
```json
{
  "entity_resolution": {
    "identity_matching": {
      "name_similarity_threshold": 0.8,
      "email_similarity_threshold": 0.9,
      "fuzzy_match_threshold": 0.85,
      "hr_override_enabled": true
    }
  }
}
```

#### Evidence Aggregation
```json
{
  "evidence_aggregation": {
    "evidence_weights": {
      "trading_pattern": 0.4,
      "communication": 0.25,
      "timing": 0.2,
      "access": 0.15
    }
  }
}
```

#### Cross-Typology Correlations
```json
{
  "cross_typology_engine": {
    "typology_correlations": {
      "insider_dealing": {
        "front_running": 0.7,
        "market_manipulation": 0.6
      },
      "spoofing": {
        "market_manipulation": 0.8,
        "wash_trading": 0.6
      }
    }
  }
}
```

## 🎯 Key Features

### 1. Identity Resolution with Confidence Scoring

```python
# Resolve person identity across multiple data sources
person_id, confidence = entity_resolution.resolve_trading_data_person_id({
    'account_id': 'trader_001',
    'name': 'John Smith',
    'email': 'john.smith@firm.com',
    'desk': 'equity_trading'
})

# Confidence scoring based on:
# - Name similarity (fuzzy matching)
# - Email domain matching
# - Desk/role consistency
# - HR data overrides
```

### 2. Cross-Account Pattern Detection

```python
# Detect patterns across multiple accounts
patterns = [
    {
        "type": "timing_synchronization",
        "description": "Synchronized trading activity across multiple accounts",
        "risk_factor": 0.7
    },
    {
        "type": "volume_distribution", 
        "description": "Suspicious volume distribution across accounts",
        "risk_factor": 0.6
    }
]
```

### 3. Cross-Typology Signal Sharing

```python
# Signals influence between risk types
if insider_dealing_score > 0.6:
    # Boost front-running assessment
    front_running_prior += 0.3 * correlation_strength
    
    # Boost market manipulation assessment  
    market_manipulation_prior += 0.2 * correlation_strength
```

### 4. Enhanced Alert Output

Instead of:
> "Account 87A triggered alert for spoofing."

We output:
> "PersonID 142 — linked to 3 accounts and 2 desks — has a 74% likelihood of spoofing on July 28 trade activity, influenced by clustered timing, price layering patterns, and repeated cancellations."

## 🔍 Alert Example

```json
{
  "alert_id": "person_alert_a1b2c3d4",
  "person_id": "person_12345678",
  "person_name": "John Smith",
  "risk_typology": "insider_dealing",
  "severity": "high",
  "probability_score": 0.74,
  "confidence_score": 0.89,
  "involved_accounts": ["account_001", "account_002", "account_003"],
  "involved_desks": ["equity_trading", "derivatives"],
  "account_count": 3,
  "desk_count": 2,
  "cross_account_patterns": [
    {
      "type": "timing_synchronization",
      "description": "Synchronized trading activity across multiple accounts",
      "evidence": {
        "sync_events": 5,
        "sync_ratio": 0.83
      }
    }
  ],
  "related_typologies": {
    "front_running": 0.42,
    "market_manipulation": 0.31
  },
  "escalation_factors": [
    "Multiple risk typologies involved (3)",
    "Strong cross-typology correlations (2)",
    "STOR filing eligible"
  ],
  "regulatory_rationale": "Individual John Smith (PersonID: person_12345678) exhibits suspicious insider_dealing patterns across 3 linked accounts and 2 desks. Strong evidence observed in: trading patterns, timing patterns. Cross-account patterns detected: Synchronized trading activity across multiple accounts. Potential violation of insider dealing regulations (MAR Article 8).",
  "stor_eligible": true,
  "explanation_summary": "John Smith shows 74.0% likelihood of insider_dealing across 3 linked accounts. Key evidence: trading patterns, timing patterns. Cross-account coordination detected in 1 patterns. Escalation factors: 3 identified."
}
```

## 🔄 Processing Workflow

### Step 1: Identity Resolution
1. **Input Processing**: Receive trading data, communications, HR records
2. **Fuzzy Matching**: Apply probabilistic matching algorithms
3. **HR Override**: Apply authoritative HR data where available
4. **Graph Update**: Update dynamic identity graph with new links
5. **Confidence Scoring**: Calculate confidence for each identity resolution

### Step 2: Evidence Aggregation
1. **Data Grouping**: Group all data by resolved PersonID
2. **Pattern Analysis**: Analyze patterns within and across accounts
3. **Temporal Analysis**: Detect timing-based suspicious activities
4. **Cross-Account Correlation**: Calculate correlations between accounts
5. **Evidence Weighting**: Apply configurable weights to different evidence types

### Step 3: Cross-Typology Analysis
1. **Risk Calculation**: Calculate base risk for each typology
2. **Signal Generation**: Generate cross-typology signals based on correlations
3. **Prior Adjustment**: Adjust priors based on signals from other typologies
4. **Escalation Detection**: Identify escalation factors
5. **Signal Decay**: Apply time-based decay to signals

### Step 4: Alert Generation
1. **Threshold Checking**: Check if risk exceeds alert thresholds
2. **Severity Assignment**: Determine alert severity based on probability and factors
3. **Evidence Compilation**: Compile primary and supporting evidence
4. **Regulatory Rationale**: Generate regulatory-compliant rationale
5. **STOR Assessment**: Determine STOR filing eligibility
6. **Explainability**: Generate human-readable explanations

## 📈 Performance Metrics

The system tracks comprehensive performance metrics:

```python
{
    "total_persons_processed": 1250,
    "total_alerts_generated": 89,
    "average_processing_time": 2.3,
    "identity_resolution_accuracy": 0.94,
    "cross_typology_signals_generated": 156,
    "alert_distribution": {
        "critical": 12,
        "high": 28,
        "medium": 35,
        "low": 14
    }
}
```

## 🛡️ Regulatory Compliance

### STOR (Suspicious Transaction and Order Reporting)
- **Automatic Assessment**: System automatically assesses STOR eligibility
- **Evidence Compilation**: Compiles cross-account evidence for regulatory filing
- **Rationale Generation**: Generates regulatory-compliant rationale text

### MAR (Market Abuse Regulation) Compliance
- **Article 8 (Insider Dealing)**: Tracks information access, timing correlation, material impact
- **Article 12 (Market Manipulation)**: Tracks price impact, volume patterns, order manipulation

### Explainability Requirements
- **Evidence Trails**: Complete audit trail of evidence aggregation
- **Key Drivers**: Identification of primary risk drivers
- **Cross-Account Analysis**: Documentation of cross-account patterns

## 🔧 Advanced Configuration

### Customizing Identity Resolution
```json
{
  "identity_matching": {
    "name_similarity_threshold": 0.8,
    "email_similarity_threshold": 0.9,
    "fuzzy_match_threshold": 0.85
  },
  "identity_weights": {
    "name_match": 0.4,
    "email_match": 0.3,
    "desk_match": 0.2,
    "role_match": 0.1
  }
}
```

### Tuning Cross-Typology Correlations
```json
{
  "typology_correlations": {
    "insider_dealing": {
      "front_running": 0.7,
      "market_manipulation": 0.6
    }
  },
  "signal_weights": {
    "insider_dealing": 0.9,
    "spoofing": 0.8,
    "market_manipulation": 0.8
  }
}
```

### Alert Thresholds
```json
{
  "probability_thresholds": {
    "minimum_alert": 0.4,
    "stor_eligible": 0.75,
    "immediate_escalation": 0.9
  }
}
```

## 🧪 Testing

### Unit Tests
```bash
# Run entity resolution tests
pytest tests/unit/test_entity_resolution.py

# Run evidence aggregation tests  
pytest tests/unit/test_person_evidence_aggregator.py

# Run cross-typology engine tests
pytest tests/unit/test_cross_typology_engine.py
```

### Integration Tests
```bash
# Run end-to-end person-centric surveillance tests
pytest tests/integration/test_person_centric_e2e.py
```

### Performance Tests
```bash
# Run performance benchmarks
pytest tests/performance/test_person_centric_performance.py
```

## 📊 Monitoring and Alerting

### System Health Monitoring
- **Identity Resolution Accuracy**: Track accuracy of person identification
- **Processing Latency**: Monitor end-to-end processing times
- **Alert Quality**: Track false positive rates and analyst feedback
- **Cross-Typology Effectiveness**: Measure signal effectiveness

### Operational Alerts
- **System Performance Degradation**: Alert on processing slowdowns
- **Identity Resolution Failures**: Alert on high failure rates
- **Data Quality Issues**: Alert on data validation failures

## 🔮 Future Enhancements

### Phase 2 Enhancements
- **Machine Learning Integration**: ML-enhanced pattern recognition
- **Real-Time Processing**: Stream processing for real-time alerts
- **Advanced Correlation Analysis**: More sophisticated correlation algorithms
- **Multi-Jurisdiction Support**: Support for different regulatory frameworks

### Advanced Features
- **Behavioral Modeling**: Individual behavioral baselines
- **Network Analysis**: Social network analysis for collusion detection
- **Sentiment Analysis**: Communication sentiment analysis
- **Predictive Analytics**: Predictive risk modeling

## 📞 Support and Maintenance

### Configuration Updates
```python
# Update system configuration
engine.update_configuration({
    "person_centric_surveillance": {
        "alert_generation": {
            "probability_thresholds": {
                "minimum_alert": 0.35  # Lower threshold
            }
        }
    }
})
```

### System Maintenance
```python
# Perform system cleanup
engine.cleanup()

# Export analysis results
engine.export_results(results, "analysis_results.json")

# Get system status
status = engine.get_system_status()
```

### Troubleshooting

#### Common Issues
1. **Low Identity Resolution Confidence**
   - Check HR data quality
   - Adjust similarity thresholds
   - Verify data consistency

2. **Too Many/Few Alerts**
   - Tune probability thresholds
   - Adjust evidence weights
   - Review cross-typology correlations

3. **Performance Issues**
   - Enable parallel processing
   - Increase batch sizes
   - Review time window configurations

## 📋 Implementation Checklist

- ✅ **Entity Resolution Layer**: Complete identity graph with confidence scoring
- ✅ **Person-Centric Data Models**: Enhanced data structures for individual tracking
- ✅ **Evidence Aggregation**: Cross-account pattern detection and analysis
- ✅ **Cross-Typology Engine**: Signal sharing between risk typologies
- ✅ **Alert Generation**: PersonID-based probabilistic alerts
- ✅ **Configuration Management**: Comprehensive configuration system
- ✅ **Main Orchestration**: Integrated surveillance engine
- ⏳ **Identity Confidence Scoring**: Advanced confidence metrics
- ⏳ **Enhanced Explainability**: Advanced regulatory explainability
- ⏳ **Testing Framework**: Comprehensive test suite

## 🎉 Benefits Achieved

| Feature | Impact |
|---------|--------|
| **Identity-centric scoring** | Captures abuse hidden by fragmented accounts |
| **Typology-agnostic modeling** | Applied uniformly across insider dealing, spoofing, etc |
| **Cross-risk signal sharing** | Enables deeper contextual insight and escalation |
| **Enhanced explainability** | Analyst can follow "per person" driver nodes |
| **Regulatory compliance** | STOR-ready alerts with comprehensive rationale |
| **Reduced false positives** | More accurate risk assessment through data aggregation |

---

*This implementation represents a significant advancement in surveillance technology, moving from reactive account-based monitoring to proactive person-centric risk assessment.*