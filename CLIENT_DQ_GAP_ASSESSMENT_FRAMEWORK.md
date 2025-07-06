# Client Data Quality Gap Assessment Framework

## 🎯 Overview
This framework provides a structured approach to assess current data quality practices at client sites and implement the DQSI scoring system tailored to their specific environment with **mixed-role support**.

## 📋 Phase 1: Current State Assessment

### 1.1 Data Flow Discovery & Role Mapping
**What to Assess:**
- **Data Sources**: Trading systems, order management, settlement, reference data
- **Data Flows**: Real-time feeds, batch processes, manual inputs
- **System Architecture**: **Mixed-role identification by data flow**
- **Integration Points**: APIs, file transfers, databases, message queues

**Key Questions:**
```
• Which data flows are CONSUMED (external sources)?
• Which data flows are PRODUCED (internal generation)?
• What are the critical data feeds and their SLAs?
• Where do data quality issues typically occur?
```

### 1.2 Role-Based Data Flow Mapping
**Mixed-Role Architecture Assessment:**

| Data Flow Type | Role | Source/Destination | DQSI Strategy |
|----------------|------|-------------------|---------------|
| **Market Data** | Consumer | Bloomberg, Reuters, Exchange feeds | Consumer validation |
| **Trading Data** | Consumer | OMS, Settlement systems | Consumer validation |
| **Reference Data** | Consumer | Vendor feeds, master data | Consumer validation |
| **Alert Data** | Producer | Surveillance system output | Producer validation |
| **Case Data** | Producer | Compliance case management | Producer validation |
| **Regulatory Reports** | Producer | Internal report generation | Producer validation |

**Example Client Architecture:**
```yaml
# Mixed-Role Data Flow Configuration
data_flows:
  # CONSUMER FLOWS - Foundational dimensions focus
  market_data:
    role: consumer
    source: "Bloomberg/Reuters"
    dimensions: [completeness, conformity, timeliness, coverage]
    
  trading_data:
    role: consumer  
    source: "OMS/Settlement"
    dimensions: [completeness, conformity, timeliness, coverage]
    
  reference_data:
    role: consumer
    source: "Vendor feeds"
    dimensions: [completeness, conformity, timeliness, coverage]
    
  # PRODUCER FLOWS - Full 7 dimensions
  surveillance_alerts:
    role: producer
    destination: "Case Management System"
    dimensions: [completeness, conformity, timeliness, coverage, accuracy, uniqueness, consistency]
    
  compliance_cases:
    role: producer
    destination: "Regulatory Reporting"
    dimensions: [completeness, conformity, timeliness, coverage, accuracy, uniqueness, consistency]
    
  regulatory_reports:
    role: producer
    destination: "External regulators"
    dimensions: [completeness, conformity, timeliness, coverage, accuracy, uniqueness, consistency]
```

### 1.3 Existing DQ Practices Inventory
**Current Capabilities Assessment by Data Flow:**

| Data Flow | Current Capability | DQSI Mapping | Role-Specific Focus |
|-----------|-------------------|--------------|-------------------|
| **Market Data (Consumer)** | Basic feed monitoring | freshness, volume_profile | Input validation only |
| **Trading Data (Consumer)** | ETL null checks | null_presence, data_type | Input validation only |
| **Alert Data (Producer)** | Manual review | ALL sub-dimensions | Full validation required |
| **Case Data (Producer)** | Workflow validation | ALL sub-dimensions | Full validation required |

### 1.3 Technology Stack Assessment
**Current Tooling:**
- Data quality tools (Informatica, Talend, custom scripts)
- Monitoring systems (alerts, dashboards)
- Data governance platforms
- Testing frameworks
- Configuration management

**Integration Points:**
- APIs for real-time scoring
- Batch processing capabilities
- Alert/case management systems
- Reporting and visualization tools

## 📊 Phase 2: DQSI Configuration Elements

### 2.1 KDE Identification & Role-Specific Risk Mapping
**Data Flow-Specific KDE Discovery:**

```yaml
# Mixed-Role KDE Configuration
kde_mappings:
  # CONSUMER DATA FLOWS
  market_data_flow:
    role: consumer
    kdes:
      price: {risk: high, weight: 3, validation: input_only}
      volume: {risk: medium, weight: 2, validation: input_only}
      timestamp: {risk: high, weight: 3, validation: input_only}
      
  trading_data_flow:
    role: consumer  
    kdes:
      trader_id: {risk: high, weight: 3, validation: input_only}
      trade_time: {risk: high, weight: 3, validation: input_only}
      notional: {risk: medium, weight: 2, validation: input_only}
      
  # PRODUCER DATA FLOWS  
  alert_data_flow:
    role: producer
    kdes:
      alert_id: {risk: high, weight: 3, validation: full_validation}
      alert_type: {risk: high, weight: 3, validation: full_validation}
      confidence_score: {risk: high, weight: 3, validation: full_validation}
      trader_id: {risk: high, weight: 3, validation: full_validation}
      
  case_data_flow:
    role: producer
    kdes:
      case_id: {risk: high, weight: 3, validation: full_validation}
      case_status: {risk: high, weight: 3, validation: full_validation}
      evidence_score: {risk: high, weight: 3, validation: full_validation}
      related_alerts: {risk: medium, weight: 2, validation: full_validation}
```

### 2.2 Mixed-Role Strategy Configuration

#### **Client Type Assessment with Data Flow Granularity:**

| Client Profile | Consumer Strategy | Producer Strategy | Implementation |
|----------------|-------------------|-------------------|----------------|
| **Startup Trading Firm** | Fallback | Role-Aware (Basic) | Limited producer capabilities |
| **Mid-Size Investment Bank** | Role-Aware Consumer | Role-Aware Producer | Full mixed-role implementation |
| **Large Investment Bank** | Role-Aware Consumer | Role-Aware Producer | Enhanced mixed-role implementation |
| **Regulatory Entity** | Role-Aware Consumer | Role-Aware Producer | Maximum validation both roles |

#### **Mixed-Role Strategy Configuration:**

```python
# Mixed-Role Strategy Selection Logic
def determine_mixed_role_strategy(client_profile, data_flows):
    strategies = {}
    
    for flow_name, flow_config in data_flows.items():
        if flow_config['role'] == 'consumer':
            # Consumer strategy - foundational focus
            strategies[flow_name] = {
                'strategy': 'role_aware_consumer',
                'dimensions': ['completeness', 'conformity', 'timeliness', 'coverage'],
                'subdimensions': 9,
                'validation_depth': 'input_validation'
            }
        elif flow_config['role'] == 'producer':
            # Producer strategy - full validation
            strategies[flow_name] = {
                'strategy': 'role_aware_producer', 
                'dimensions': ['completeness', 'conformity', 'timeliness', 'coverage', 
                              'accuracy', 'uniqueness', 'consistency'],
                'subdimensions': 17,
                'validation_depth': 'full_validation'
            }
    
    return strategies
```

### 2.3 Sub-Dimension Customization by Data Flow

**Role-Specific Sub-Dimension Selection:**

```yaml
# Consumer Data Flows - Foundational Sub-Dimensions
consumer_subdimensions:
  completeness:
    - null_presence
    - field_population
  conformity:
    - data_type
    - format
    - length
    - range
  timeliness:
    - freshness
  coverage:
    - volume_profile
    - coverage_baseline

# Producer Data Flows - Full Sub-Dimensions  
producer_subdimensions:
  completeness:
    - null_presence
    - field_population
  conformity:
    - data_type
    - format
    - length
    - range
  timeliness:
    - freshness
    - lag_detection
  coverage:
    - volume_profile
    - volume_reconciliation
    - coverage_baseline
  accuracy:
    - precision
    - value_accuracy
    - referential_accuracy
  uniqueness:
    - duplicate_detection
    - cross_system_uniqueness
  consistency:
    - internal_consistency
    - cross_system_consistency
```

## 🔧 Phase 3: Scoring Calibration

### 3.1 Baseline Establishment

**Historical Data Analysis:**
```python
# Calibration Process
def calibrate_client_scoring(historical_data):
    baseline_metrics = {
        'null_rate': calculate_null_percentage(historical_data),
        'format_error_rate': calculate_format_errors(historical_data),
        'timeliness_p95': calculate_delay_percentile(historical_data, 95),
        'volume_variance': calculate_volume_variance(historical_data)
    }
    
    # Adjust scoring thresholds based on client baseline
    scoring_thresholds = {
        'acceptable_null_rate': baseline_metrics['null_rate'] * 0.8,
        'good_timeliness': baseline_metrics['timeliness_p95'] * 0.5,
        'volume_drop_alert': baseline_metrics['volume_variance'] * 2
    }
    
    return scoring_thresholds
```

### 3.2 Business Impact Weighting

**Client-Specific Weight Adjustments:**

| Business Focus | Weight Adjustments | Rationale |
|----------------|-------------------|-----------|
| **High-Frequency Trading** | Timeliness × 1.5 | Latency critical |
| **Risk Management** | Accuracy × 1.3 | Precision critical |
| **Compliance Heavy** | Completeness × 1.2 | Audit requirements |
| **Multi-Asset** | Consistency × 1.4 | Cross-system sync |

### 3.3 Comparison Type Configuration

**Reference Source Mapping:**

```yaml
comparison_configurations:
  reference_tables:
    instrument_master: "BLOOMBERG_SYMBOLOGY"
    trader_directory: "HR_SYSTEM" 
    venue_codes: "FIX_STANDARD"
    
  golden_sources:
    pricing: "BLOOMBERG_PRICING"
    settlements: "SETTLEMENT_SYSTEM"
    positions: "POSITION_SYSTEM"
    
  cross_system_validation:
    trade_matching: ["OMS", "SETTLEMENT", "RISK"]
    position_reconciliation: ["TRADING", "ACCOUNTING", "RISK"]
    
  trend_baselines:
    volume_patterns: "90_DAY_ROLLING"
    timing_patterns: "30_DAY_AVERAGE"
```

## 📈 Phase 4: Implementation Approach

### 4.1 Pilot Implementation

**Week 1-2: Discovery**
```
• Data source inventory
• System architecture mapping
• Stakeholder interviews
• Current DQ process documentation
```

**Week 3-4: Configuration**
```
• KDE identification and risk mapping
• Strategy selection based on client profile
• Sub-dimension customization
• Reference source integration
```

**Week 5-6: Calibration**
```
• Historical data analysis
• Baseline establishment
• Scoring threshold tuning
• Business impact weighting
```

**Week 7-8: Pilot Deployment**
```
• Limited scope implementation
• Real-time scoring validation
• Alert/case integration testing
• Stakeholder feedback collection
```

### 4.2 Client Configuration Template

```yaml
# Client: ABC Investment Bank
client_config:
  name: "ABC Investment Bank"
  profile:
    type: "tier2_bank"
    strategy: "role_aware"
    
  kde_mappings:
    # Client-specific critical KDEs
    trader_id: {tier: "high", weight: 3, business_critical: true}
    client_account: {tier: "high", weight: 3, regulatory: true}
    notional_usd: {tier: "high", weight: 3, risk_impact: "high"}
    
  sub_dimensions:
    enabled:
      - null_presence
      - data_type
      - format
      - freshness
      - volume_reconciliation  # Producer requirement
      - value_accuracy         # Regulatory requirement
      
  thresholds:
    critical_null_rate: 0.01    # 1% max missing data
    acceptable_delay: "5min"    # 5 minute freshness SLA
    volume_drop_alert: 0.20     # 20% volume drop triggers alert
    
  integration:
    alert_system: "TIBCO_EMS"
    case_management: "CUSTOM_CMS"
    reporting: "TABLEAU"
    
  governance:
    review_frequency: "monthly"
    escalation_threshold: 0.60
    audit_retention: "7_years"
```

## 🎯 Phase 5: Gap Analysis Output

### 5.1 Current State Scoring by Data Flow

**Before DQSI Implementation:**
```yaml
# Consumer Data Flows
market_data_consumer:
  completeness: 70% (Basic feed monitoring)
  conformity: 50% (Limited format validation)
  timeliness: 60% (Feed latency monitoring)
  coverage: 40% (Manual volume tracking)
  consumer_maturity: 55% (DEVELOPING)

trading_data_consumer:
  completeness: 65% (ETL null checking)
  conformity: 45% (Basic type validation)
  timeliness: 30% (No systematic monitoring)
  coverage: 35% (Manual tracking)
  consumer_maturity: 44% (POOR)

# Producer Data Flows  
alert_data_producer:
  completeness: 40% (Manual validation)
  conformity: 30% (Basic format checks)
  timeliness: 20% (No SLA monitoring)
  coverage: 25% (No volume tracking)
  accuracy: 15% (No golden source validation)
  uniqueness: 10% (No duplicate detection)
  consistency: 5% (Manual reconciliation)
  producer_maturity: 21% (CRITICAL)

case_data_producer:
  completeness: 50% (Workflow validation)
  conformity: 35% (Basic format checks)
  timeliness: 25% (Manual tracking)
  coverage: 30% (Excel tracking)
  accuracy: 20% (Periodic validation)
  uniqueness: 15% (Basic duplicate checking)
  consistency: 10% (Manual reconciliation)
  producer_maturity: 26% (CRITICAL)
```

### 5.2 Target State Definition by Role

**After Mixed-Role DQSI Implementation:**
```yaml
# Consumer Data Flows Target
consumer_targets:
  foundational_dimensions: 85%+
    - completeness: 90% (Automated null detection)
    - conformity: 85% (Format validation + reference tables)
    - timeliness: 80% (Real-time freshness monitoring)
    - coverage: 85% (Automated volume monitoring)
  consumer_overall_target: 85% (GOOD)

# Producer Data Flows Target
producer_targets:
  foundational_dimensions: 90%+
    - completeness: 95% (Comprehensive validation)
    - conformity: 90% (Full format + reference validation)
    - timeliness: 85% (Real-time SLA monitoring)
    - coverage: 90% (Full volume reconciliation)
  enhanced_dimensions: 80%+
    - accuracy: 85% (Golden source validation)
    - uniqueness: 80% (Full duplicate detection)
    - consistency: 75% (Cross-system validation)
  producer_overall_target: 86% (GOOD)
```

### 5.3 Mixed-Role Implementation Roadmap

**Priority 1 (Months 1-3): Consumer Data Flows**
```
• Implement consumer strategy for market/trading data
• Basic KDE scoring for input validation
• Completeness and conformity validation
• Feed monitoring and alerting
```

**Priority 2 (Months 4-6): Producer Data Flows Foundation**
```
• Implement producer strategy for alert/case data
• Enhanced KDE scoring
• Foundational dimensions (completeness, conformity, timeliness, coverage)
• Basic alert/case quality monitoring
```

**Priority 3 (Months 7-12): Producer Data Flows Enhanced**
```
• Full 7-dimension validation for produced data
• Accuracy validation against golden sources
• Cross-system consistency checking
• Full regulatory compliance for outputs
```

## 🔍 Phase 6: Ongoing Calibration

### 6.1 Continuous Tuning

**Monthly Reviews:**
- Scoring threshold adjustments
- Business rule updates
- Performance optimization
- Stakeholder feedback integration

**Quarterly Assessments:**
- Strategy effectiveness review
- KDE risk tier adjustments
- Sub-dimension enablement review
- ROI measurement

### 6.2 Success Metrics

**Technical Metrics:**
- DQSI score improvement over time
- Confidence index trends
- System performance (latency, throughput)
- Error reduction rates

**Business Metrics:**
- Reduced manual data quality effort
- Faster issue resolution
- Improved regulatory compliance
- Enhanced decision-making confidence

---

## 🎯 Key Takeaways for Mixed-Role Client Engagements

1. **Map Data Flows First**: Understand which data flows are consumed vs produced
2. **Role-Specific Strategy**: Apply consumer strategy to inputs, producer strategy to outputs
3. **Differential Validation**: Lighter validation for consumed data, full validation for produced data
4. **Phased Implementation**: Start with consumer flows, then enhance producer flows
5. **Business Impact Focus**: Producer data quality directly impacts client reputation and compliance
6. **Continuous Calibration**: Different calibration approaches for consumer vs producer data

This framework recognizes that modern financial institutions operate in **mixed-role environments** where they must validate consumed data differently than produced data, ensuring appropriate data quality standards for each role while optimizing resource allocation.