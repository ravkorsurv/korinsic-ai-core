# Kor.ai Data Processor - Comprehensive Data Model

## Overview

The Kor.ai surveillance platform is designed to detect market abuse risks such as insider dealing and spoofing in commodities and energy trading. This document provides a comprehensive data model covering all data structures, relationships, and business logic.

## Core Data Architecture

### 1. Data Processing Pipeline

#### DataProcessor Class
**Purpose**: Main data processing pipeline for trading data transformation and feature extraction

**Key Methods**:
- `process(raw_data)` - Main processing pipeline
- `generate_simulation_data()` - Generate test scenarios
- Feature extractors for volume, price, timing, and order metrics

---

## Primary Data Models

### 1. Trading Data Models

#### Trade Entity
```python
class Trade:
    id: str                    # Unique trade identifier
    timestamp: datetime        # Trade execution time (ISO format)
    instrument: str           # Financial instrument code
    volume: float             # Trade volume
    price: float              # Trade price
    side: str                 # 'buy' or 'sell'
    trader_id: str            # ID of executing trader
    value: float              # Calculated: volume * price
```

**Relationships**:
- Many-to-One with Trader
- Many-to-Many with MaterialEvents (via instruments)

#### Order Entity
```python
class Order:
    id: str                    # Unique order identifier
    timestamp: datetime        # Order placement time
    instrument: str           # Financial instrument code
    size: float               # Order size
    price: float              # Order price
    side: str                 # 'buy' or 'sell'
    status: str               # 'filled', 'cancelled', 'pending'
    trader_id: str            # ID of trader placing order
    cancellation_time: datetime # Time of cancellation (if applicable)
```

**Relationships**:
- Many-to-One with Trader
- One-to-Many with Trades (when filled)

#### Trader Entity
```python
class Trader:
    id: str                    # Unique trader identifier
    name: str                  # Trader name
    role: str                  # 'executive', 'board_member', 'senior_trader', 'trader', 'analyst'
    department: str            # Department/division
    access_level: str          # 'high', 'standard', 'restricted'
    start_date: datetime       # Employment start date
    supervisors: List[str]     # List of supervisor IDs
```

**Relationships**:
- One-to-Many with Trades
- One-to-Many with Orders
- One-to-Many with Alerts

#### MaterialEvent Entity
```python
class MaterialEvent:
    id: str                    # Unique event identifier
    timestamp: datetime        # Event occurrence time
    type: str                  # 'earnings_announcement', 'merger', 'regulatory_change', etc.
    description: str           # Event description
    instruments_affected: List[str] # List of affected instruments
    materiality_score: float   # 0.0 to 1.0, importance score
```

**Relationships**:
- Many-to-Many with Trades (via instruments)
- Used in timing analysis for insider dealing detection

#### MarketData Entity
```python
class MarketData:
    volatility: float          # Market volatility measure
    volume: float              # Total market volume
    price_movement: float      # Price movement percentage
    liquidity: float           # Market liquidity measure
    market_hours: bool         # Whether market is open
```

---

### 2. Bayesian Risk Model

#### BayesianNode Entity
```python
class BayesianNode:
    name: str                  # Node name (e.g., 'MaterialInfo', 'TradingActivity')
    states: List[str]          # Possible states (e.g., ['Low', 'Medium', 'High'])
    description: str           # Node description
    fallback_prior: List[float] # Prior probabilities for each state
    evidence_value: int        # Current evidence state (0, 1, 2)
    probability: float         # Current probability
    confidence: float          # Confidence in evidence
```

**Node Types**:

##### Insider Dealing Model Nodes
1. **MaterialInfo Node**
   - States: ['No access', 'Potential access', 'Clear access']
   - Fallback Prior: [0.7, 0.25, 0.05]

2. **TradingActivity Node**
   - States: ['Normal', 'Unusual', 'Highly unusual']
   - Fallback Prior: [0.8, 0.15, 0.05]

3. **Timing Node**
   - States: ['Normal', 'Suspicious', 'Highly suspicious']
   - Fallback Prior: [0.9, 0.08, 0.02]

4. **PriceImpact Node**
   - States: ['Low', 'Medium', 'High']
   - Fallback Prior: [0.8, 0.15, 0.05]

5. **Risk Node**
   - States: ['Low', 'Medium', 'High']
   - Output node for final risk assessment

##### Spoofing Model Nodes
1. **OrderPattern Node**
   - States: ['Normal', 'Layered', 'Excessive layering']
   - Fallback Prior: [0.85, 0.12, 0.03]

2. **CancellationRate Node**
   - States: ['Low', 'Medium', 'High']
   - Fallback Prior: [0.8, 0.15, 0.05]

3. **PriceMovement Node**
   - States: ['Minimal', 'Moderate', 'Significant']
   - Fallback Prior: [0.7, 0.25, 0.05]

4. **VolumeRatio Node**
   - States: ['Normal', 'Imbalanced', 'Highly imbalanced']
   - Fallback Prior: [0.8, 0.15, 0.05]

#### RiskScore Entity
```python
class RiskScore:
    model_type: str            # 'insider_dealing', 'spoofing', 'latent_intent'
    overall_score: float       # Overall risk score (0.0 to 1.0)
    high_risk: float           # Probability of high risk
    medium_risk: float         # Probability of medium risk
    low_risk: float            # Probability of low risk
    evidence_factors: Dict[str, int] # Node evidence values
    news_context: int          # 0=explained, 1=partial, 2=unexplained
    high_nodes: List[str]      # Nodes in high risk state
    critical_nodes: List[str]  # Nodes in critical risk state
    explanation: str           # Human-readable explanation
    esi: EvidenceSufficiencyIndex # Evidence quality metrics
```

#### EvidenceSufficiencyIndex Entity
```python
class EvidenceSufficiencyIndex:
    evidence_sufficiency_index: float    # Overall ESI score (0.0 to 1.0)
    esi_badge: str                      # 'Weak', 'Moderate', 'Strong'
    node_count: int                     # Number of active nodes
    mean_confidence: str                # 'Low', 'Medium', 'High'
    fallback_ratio: float               # Ratio of nodes using fallback
    contribution_spread: str            # 'Uneven', 'Balanced'
    clusters: List[str]                 # Active evidence clusters
    components: ESIComponents           # Detailed ESI components
```

#### ESIComponents Entity
```python
class ESIComponents:
    node_activation_ratio: float        # Ratio of active nodes
    mean_confidence_score: float        # Average confidence
    fallback_ratio: float               # Fallback usage ratio
    contribution_entropy: float         # Distribution entropy
    cross_cluster_diversity: float      # Cross-cluster evidence
```

---

### 3. Alert Management System

#### Alert Entity
```python
class Alert:
    id: str                    # Unique alert identifier
    type: str                  # 'INSIDER_DEALING', 'SPOOFING', 'OVERALL_RISK'
    severity: str              # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    timestamp: datetime        # Alert generation time
    risk_score: float          # Associated risk score
    trader_id: str             # ID of trader involved
    description: str           # Alert description
    evidence: Dict[str, Any]   # Supporting evidence
    recommended_actions: List[str] # Recommended actions
    instruments: List[str]     # Affected instruments
    timeframe: str             # 'intraday', 'daily', 'weekly', 'extended'
    news_context: int          # News context suppression flag
    high_nodes: List[str]      # High-risk Bayesian nodes
    critical_nodes: List[str]  # Critical-risk Bayesian nodes
    explanation: str           # Human-readable explanation
    esi: EvidenceSufficiencyIndex # Evidence quality
```

**Relationships**:
- Many-to-One with Trader
- One-to-Many with RegulatoryRationale

#### AlertThreshold Entity
```python
class AlertThreshold:
    alert_type: str            # 'insider_dealing', 'spoofing', 'overall_risk'
    severity: str              # 'medium', 'high', 'critical'
    threshold_value: float     # Threshold for alert generation
```

---

### 4. Risk Calculation Models

#### RiskCalculator Entity
```python
class RiskCalculator:
    risk_weights: Dict[str, float]     # Model weights
    contextual_factors: Dict[str, Dict] # Contextual multipliers
```

#### RiskBreakdown Entity
```python
class RiskBreakdown:
    base_scores: Dict[str, float]      # Base risk scores by model
    weighted_scores: Dict[str, float]  # Weighted risk scores
    contextual_factors: Dict[str, Any] # Applied contextual factors
    overall_risk: float                # Final overall risk score
```

#### ContextualFactor Entity
```python
class ContextualFactor:
    factor_type: str           # 'trader_role', 'volume', 'timeframe', 'market_conditions'
    value: str                 # Factor value
    multiplier: float          # Risk multiplier
```

---

### 5. Regulatory Compliance Models

#### RegulatoryRationale Entity
```python
class RegulatoryRationale:
    deterministic_narrative: str       # Structured narrative
    inference_paths: List[InferencePath] # Bayesian inference paths
    voi_analysis: Dict[str, Any]       # Value of Information analysis
    sensitivity_report: Dict[str, Any]  # Sensitivity analysis
    regulatory_frameworks: List[str]    # Applicable regulations
    audit_trail: Dict[str, Any]        # Audit trail information
```

#### InferencePath Entity
```python
class InferencePath:
    node_name: str             # Bayesian node name
    evidence_value: int        # Evidence state (0, 1, 2)
    probability: float         # Node probability
    contribution: float        # Contribution to overall risk
    rationale: str             # Explanation for this node
    confidence: float          # Confidence in evidence
    regulatory_relevance: str  # Regulatory relevance
```

#### STORRecord Entity
```python
class STORRecord:
    record_id: str             # Unique STOR record ID
    timestamp: datetime        # Record creation time
    trader_id: str             # Trader identifier
    instrument: str            # Primary instrument
    transaction_type: str      # Transaction type
    suspicious_indicators: List[str] # List of suspicious indicators
    risk_score: float          # Risk score
    regulatory_rationale: str  # Regulatory explanation
    evidence_details: Dict[str, Any] # Evidence details
    compliance_officer_notes: str # Compliance notes
```

---

### 6. Metrics and Analysis Models

#### TradingMetrics Entity
```python
class TradingMetrics:
    avg_volume: float          # Average trading volume
    volume_std: float          # Volume standard deviation
    volume_imbalance: float    # Buy/sell volume imbalance
    total_volume: float        # Total volume
    price_impact: float        # Price impact measure
    price_volatility: float    # Price volatility
    price_movement: float      # Price movement direction
    pre_event_trading: int     # Pre-event trading count
    timing_concentration: float # Timing concentration measure
    cancellation_ratio: float  # Order cancellation ratio
    order_frequency: float     # Order frequency
```

#### HistoricalMetrics Entity
```python
class HistoricalMetrics:
    avg_volume: float          # Historical average volume
    avg_frequency: float       # Historical average frequency
    avg_price_impact: float    # Historical average price impact
```

---

### 7. Latent Intent Model (Advanced)

#### LatentIntentNode Entity
```python
class LatentIntentNode:
    latent_intent_no: float    # Probability of no intent
    latent_intent_potential: float # Probability of potential intent
    latent_intent_clear: float # Probability of clear intent
```

#### ConvergingEvidenceNode Entity
```python
class ConvergingEvidenceNode:
    profit_motivation: float   # Profit motivation score
    access_pattern: float      # Access pattern score
    order_behavior: float      # Order behavior score
    comms_metadata: float      # Communications metadata score
```

---

## Data Relationships and Dependencies

### Entity Relationship Diagram

```
Trader ||--o{ Trade : executes
Trader ||--o{ Order : places
Trader ||--o{ Alert : triggers

Trade }o--|| Instrument : involves
Order }o--|| Instrument : involves
MaterialEvent }o--o{ Instrument : affects

Trade ||--o{ TradingMetrics : generates
Order ||--o{ TradingMetrics : generates

BayesianNode }o--o{ RiskScore : contributes_to
RiskScore ||--o{ Alert : triggers
Alert ||--o{ RegulatoryRationale : requires

RiskScore ||--|| EvidenceSufficiencyIndex : includes
Alert ||--|| STORRecord : exports_to
```

### Data Flow Architecture

```
Raw Trading Data → DataProcessor → ProcessedData
                                      ↓
ProcessedData → BayesianEngine → RiskScore
                                      ↓
RiskScore → AlertGenerator → Alert
                                      ↓
Alert → RegulatoryExplainability → RegulatoryRationale
                                      ↓
RegulatoryRationale → STORRecord/CSV Export
```

---

## Configuration and Settings

### Global Settings Entity
```python
class GlobalSettings:
    default_fallback_prior: List[float] # Default prior probabilities
    news_context_suppression: NewsContextSettings
    risk_thresholds: RiskThresholdSettings
```

### NewsContextSettings Entity
```python
class NewsContextSettings:
    explained_move_multiplier: float    # 0.5 - suppress when explained
    partial_move_multiplier: float      # 0.75 - reduce when partial
    unexplained_move_multiplier: float  # 1.0 - normal when unexplained
```

### RiskThresholdSettings Entity
```python
class RiskThresholdSettings:
    low_risk: float            # 0.3 - Low risk threshold
    medium_risk: float         # 0.6 - Medium risk threshold
    high_risk: float           # 0.8 - High risk threshold
```

---

## Database Schema (Conceptual)

### Core Tables

#### traders_table
```sql
CREATE TABLE traders (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    role VARCHAR(50),
    department VARCHAR(100),
    access_level VARCHAR(20),
    start_date TIMESTAMP,
    supervisors JSON
);
```

#### trades_table
```sql
CREATE TABLE trades (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP,
    instrument VARCHAR(50),
    volume DECIMAL(15,2),
    price DECIMAL(10,4),
    side VARCHAR(10),
    trader_id VARCHAR(50),
    value DECIMAL(20,2),
    FOREIGN KEY (trader_id) REFERENCES traders(id)
);
```

#### orders_table
```sql
CREATE TABLE orders (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP,
    instrument VARCHAR(50),
    size DECIMAL(15,2),
    price DECIMAL(10,4),
    side VARCHAR(10),
    status VARCHAR(20),
    trader_id VARCHAR(50),
    cancellation_time TIMESTAMP,
    FOREIGN KEY (trader_id) REFERENCES traders(id)
);
```

#### material_events_table
```sql
CREATE TABLE material_events (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP,
    type VARCHAR(50),
    description TEXT,
    instruments_affected JSON,
    materiality_score DECIMAL(3,2)
);
```

#### alerts_table
```sql
CREATE TABLE alerts (
    id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(30),
    severity VARCHAR(20),
    timestamp TIMESTAMP,
    risk_score DECIMAL(5,4),
    trader_id VARCHAR(50),
    description TEXT,
    evidence JSON,
    recommended_actions JSON,
    instruments JSON,
    timeframe VARCHAR(20),
    news_context INTEGER,
    high_nodes JSON,
    critical_nodes JSON,
    explanation TEXT,
    esi JSON,
    FOREIGN KEY (trader_id) REFERENCES traders(id)
);
```

#### risk_scores_table
```sql
CREATE TABLE risk_scores (
    id VARCHAR(50) PRIMARY KEY,
    model_type VARCHAR(30),
    overall_score DECIMAL(5,4),
    high_risk DECIMAL(5,4),
    medium_risk DECIMAL(5,4),
    low_risk DECIMAL(5,4),
    evidence_factors JSON,
    news_context INTEGER,
    high_nodes JSON,
    critical_nodes JSON,
    explanation TEXT,
    esi JSON,
    created_at TIMESTAMP
);
```

#### regulatory_rationales_table
```sql
CREATE TABLE regulatory_rationales (
    id VARCHAR(50) PRIMARY KEY,
    alert_id VARCHAR(50),
    deterministic_narrative TEXT,
    inference_paths JSON,
    voi_analysis JSON,
    sensitivity_report JSON,
    regulatory_frameworks JSON,
    audit_trail JSON,
    created_at TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES alerts(id)
);
```

---

## Data Validation Rules

### Business Rules

1. **Trade Validation**
   - Volume > 0
   - Price > 0
   - Timestamp must be valid
   - Trader must exist
   - Side must be 'buy' or 'sell'

2. **Order Validation**
   - Size > 0
   - Price > 0
   - Status must be valid enum
   - Cancellation time must be after placement time

3. **Risk Score Validation**
   - All probabilities must sum to 1.0
   - Overall score must be between 0.0 and 1.0
   - Evidence factors must be valid integers (0, 1, 2)

4. **Alert Validation**
   - Severity must match score thresholds
   - Type must match triggering risk model
   - Trader must exist

### Data Constraints

1. **Temporal Constraints**
   - Order placement before cancellation
   - Trade execution after order placement
   - Material events before related trades

2. **Business Logic Constraints**
   - High-access traders trigger higher risk multipliers
   - Executive roles have elevated risk factors
   - Pre-event trading increases insider risk

3. **Bayesian Model Constraints**
   - Node states must be valid
   - Conditional probability tables must be complete
   - Evidence values must map to valid states

---

## API Data Transfer Objects (DTOs)

### Request DTOs

#### AnalyzeRequest
```python
class AnalyzeRequest:
    trades: List[TradeDTO]
    orders: List[OrderDTO]
    trader_info: TraderDTO
    material_events: List[MaterialEventDTO]
    market_data: MarketDataDTO
    use_latent_intent: bool = False
    include_regulatory_rationale: bool = False
```

#### SimulateRequest
```python
class SimulateRequest:
    scenario_type: str         # 'insider_dealing' or 'spoofing'
    parameters: Dict[str, Any]
```

### Response DTOs

#### AnalyzeResponse
```python
class AnalyzeResponse:
    timestamp: str
    analysis_id: str
    risk_scores: Dict[str, RiskScoreDTO]
    alerts: List[AlertDTO]
    regulatory_rationales: List[RegulatoryRationaleDTO]
    processed_data_summary: ProcessedDataSummaryDTO
```

#### AlertDTO
```python
class AlertDTO:
    id: str
    type: str
    severity: str
    timestamp: str
    risk_score: float
    trader_id: str
    description: str
    evidence: Dict[str, Any]
    recommended_actions: List[str]
    instruments: List[str]
    timeframe: str
    news_context: int
    high_nodes: List[str]
    critical_nodes: List[str]
    explanation: str
    esi: EvidenceSufficiencyIndexDTO
```

---

## Performance and Scalability Considerations

### Indexing Strategy

1. **Primary Indexes**
   - traders.id (PK)
   - trades.id (PK)
   - orders.id (PK)
   - alerts.id (PK)

2. **Secondary Indexes**
   - trades.trader_id, trades.timestamp
   - orders.trader_id, orders.timestamp
   - alerts.trader_id, alerts.timestamp
   - alerts.severity, alerts.type

### Data Archiving

1. **Hot Data** (0-90 days)
   - Real-time analysis
   - Active alerts
   - Recent risk scores

2. **Warm Data** (90 days - 2 years)
   - Historical analysis
   - Compliance reporting
   - Audit trails

3. **Cold Data** (2+ years)
   - Long-term storage
   - Regulatory compliance
   - Historical research

### Data Partitioning

1. **Time-based Partitioning**
   - Monthly partitions for trades/orders
   - Quarterly partitions for alerts
   - Annual partitions for regulatory records

2. **Trader-based Partitioning**
   - Separate high-risk traders
   - Department-based partitioning
   - Geographic distribution

---

## Security and Privacy

### Data Classification

1. **Highly Sensitive**
   - Trader personal information
   - Material non-public information
   - Risk scores and alerts

2. **Sensitive**
   - Trading data
   - Order information
   - Market data

3. **Internal**
   - Configuration data
   - System logs
   - Performance metrics

### Access Control

1. **Role-based Access**
   - Compliance officers: Full access
   - Traders: Own data only
   - Auditors: Read-only access
   - Administrators: System configuration

2. **Data Masking**
   - Trader names in non-production
   - Sensitive amounts in logs
   - Personal identifiers in exports

---

## Monitoring and Observability

### System Metrics

1. **Performance Metrics**
   - Request latency
   - Processing time
   - Alert generation rate
   - Database query performance

2. **Business Metrics**
   - Alert accuracy rates
   - False positive rates
   - Risk score distributions
   - Regulatory compliance rates

### Logging and Auditing

1. **Audit Trail**
   - All risk calculations
   - Alert generations
   - Regulatory exports
   - System configuration changes

2. **Data Lineage**
   - Trade data sources
   - Risk calculation paths
   - Alert trigger chains
   - Regulatory reporting flows

---

This comprehensive data model provides a complete overview of the Kor.ai surveillance platform's data architecture, covering all entities, relationships, business rules, and technical considerations for effective market abuse detection and regulatory compliance.