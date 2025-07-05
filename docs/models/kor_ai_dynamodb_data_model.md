# Kor.ai DynamoDB Data Model - Modern NoSQL Design

## Overview

This document provides a comprehensive DynamoDB data model for the Kor.ai surveillance platform, designed with **access patterns first** approach, leveraging modern NoSQL principles including single-table design, denormalization, and strategic use of Global Secondary Indexes (GSIs).

## Design Philosophy

### 1. Access Patterns First
- Model data around how it will be queried
- Minimize the number of queries needed
- Design for scale and performance
- Avoid expensive scan operations

### 2. Single Table Design
- Store multiple entity types in one table
- Use composite partition/sort keys
- Leverage GSIs for different access patterns
- Denormalize related data

### 3. No Joins Philosophy
- Embed related data within documents
- Pre-aggregate commonly accessed data
- Use batch operations for multi-item queries

---

## Primary Access Patterns

### Core Access Patterns Identified

1. **Trader-Centric Queries**
   - Get trader profile with recent activity summary
   - Get all trades for a trader in time range
   - Get all orders for a trader in time range
   - Get all alerts for a trader

2. **Alert Management**
   - Get alerts by severity (HIGH, CRITICAL)
   - Get alerts by type (INSIDER_DEALING, SPOOFING)
   - Get alerts in time range
   - Get alert with full regulatory rationale

3. **Risk Analysis**
   - Get risk scores for analysis period
   - Get risk trends for trader
   - Get risk breakdown by instrument

4. **Regulatory Reporting**
   - Get STOR records for reporting
   - Get regulatory rationales by date
   - Get audit trail for compliance

5. **Real-time Surveillance**
   - Get active alerts requiring attention
   - Get recent trading activity for monitoring
   - Get material events affecting instruments

---

## DynamoDB Table Design

### Main Table: `kor-ai-surveillance`

#### Primary Key Structure
```
PK (Partition Key): Entity identifier with type prefix
SK (Sort Key): Entity-specific sort key with timestamp or hierarchy
```

#### Key Patterns
```
PK Format Examples:
- TRADER#trader_001
- ALERT#alert_20241215_143022
- RISK#trader_001#2024-12-15
- EVENT#event_001
- INSTRUMENT#ENERGY_CORP

SK Format Examples:
- PROFILE (for trader profile)
- TRADE#2024-12-15T14:30:22Z#trade_001
- ORDER#2024-12-15T14:30:22Z#order_001
- ALERT#2024-12-15T14:30:22Z#INSIDER_DEALING
- RISK_SCORE#2024-12-15T14:30:22Z
- RATIONALE#alert_20241215_143022
```

---

## Entity Data Models

### 1. Trader Profile Entity
```json
{
  "PK": "TRADER#trader_001",
  "SK": "PROFILE",
  "EntityType": "TRADER_PROFILE",
  "TraderID": "trader_001",
  "Name": "John Doe",
  "Role": "senior_trader",
  "Department": "Energy Trading",
  "AccessLevel": "high",
  "StartDate": "2023-01-15T00:00:00Z",
  "Supervisors": ["supervisor_001", "supervisor_002"],
  "Status": "active",
  "LastUpdated": "2024-12-15T14:30:22Z",
  "RiskProfile": {
    "CurrentRiskLevel": "MEDIUM",
    "LastAlertDate": "2024-12-14T09:15:00Z",
    "TotalAlerts": 15,
    "HighRiskAlerts": 3,
    "ActiveInvestigations": 1
  },
  "TradingMetrics": {
    "AvgDailyVolume": 150000,
    "AvgDailyTrades": 45,
    "PrimaryInstruments": ["ENERGY_CORP", "OIL_FUTURE_X"],
    "LastTradeDate": "2024-12-15T14:25:00Z"
  },
  "TTL": 1735689600
}
```

### 2. Trading Activity Entity (Denormalized)
```json
{
  "PK": "TRADER#trader_001",
  "SK": "TRADE#2024-12-15T14:30:22Z#trade_001",
  "EntityType": "TRADE",
  "TradeID": "trade_001",
  "Timestamp": "2024-12-15T14:30:22Z",
  "Instrument": "ENERGY_CORP",
  "Volume": 100000,
  "Price": 50.25,
  "Side": "buy",
  "Value": 5025000,
  "TraderInfo": {
    "TraderID": "trader_001",
    "Name": "John Doe",
    "Role": "senior_trader",
    "AccessLevel": "high"
  },
  "RiskIndicators": {
    "PreEventTrade": true,
    "UnusualVolume": true,
    "PriceImpact": 0.025,
    "TimingScore": 0.8
  },
  "RelatedEvents": [
    {
      "EventID": "event_001",
      "Type": "earnings_announcement",
      "DaysUntilEvent": 1,
      "MaterialityScore": 0.9
    }
  ],
  "ProcessedMetrics": {
    "VolumeRatio": 3.2,
    "PriceMovement": 0.025,
    "MarketImpact": 0.15
  },
  "GSI1PK": "INSTRUMENT#ENERGY_CORP",
  "GSI1SK": "TRADE#2024-12-15T14:30:22Z",
  "GSI2PK": "DATE#2024-12-15",
  "GSI2SK": "TRADE#14:30:22#trader_001",
  "TTL": 1767225600
}
```

### 3. Alert Entity (Comprehensive)
```json
{
  "PK": "ALERT#alert_20241215_143022",
  "SK": "METADATA",
  "EntityType": "ALERT",
  "AlertID": "alert_20241215_143022",
  "Type": "INSIDER_DEALING",
  "Severity": "HIGH",
  "Timestamp": "2024-12-15T14:30:22Z",
  "Status": "ACTIVE",
  "RiskScore": 0.85,
  "TraderInfo": {
    "TraderID": "trader_001",
    "Name": "John Doe",
    "Role": "senior_trader",
    "AccessLevel": "high",
    "Department": "Energy Trading"
  },
  "Description": "Potential insider dealing detected for senior_trader with 15 trades. High-risk nodes: MaterialInfo, Timing.",
  "Evidence": {
    "RiskScores": {
      "OverallScore": 0.85,
      "HighRisk": 0.75,
      "MediumRisk": 0.20,
      "LowRisk": 0.05,
      "ModelType": "insider_dealing"
    },
    "BayesianNodes": {
      "MaterialInfo": {
        "State": "Clear access",
        "Probability": 0.85,
        "Confidence": 0.90
      },
      "TradingActivity": {
        "State": "Highly unusual",
        "Probability": 0.75,
        "Confidence": 0.85
      },
      "Timing": {
        "State": "Highly suspicious",
        "Probability": 0.80,
        "Confidence": 0.95
      }
    },
    "TradingMetrics": {
      "TradesCount": 15,
      "TotalVolume": 1500000,
      "PreEventTrades": 12,
      "UnusualVolumeRatio": 3.2,
      "PriceImpact": 0.025
    },
    "MaterialEvents": [
      {
        "EventID": "event_001",
        "Type": "earnings_announcement",
        "Timestamp": "2024-12-16T09:00:00Z",
        "MaterialityScore": 0.9
      }
    ]
  },
  "ESI": {
    "EvidenceSufficiencyIndex": 0.84,
    "ESIBadge": "Strong",
    "NodeCount": 4,
    "MeanConfidence": "High",
    "FallbackRatio": 0.0,
    "ContributionSpread": "Balanced",
    "Clusters": ["PnL", "MNPI", "TradePattern"]
  },
  "Instruments": ["ENERGY_CORP", "OIL_FUTURE_X"],
  "Timeframe": "daily",
  "NewsContext": 2,
  "HighNodes": ["MaterialInfo", "Timing"],
  "CriticalNodes": ["MaterialInfo"],
  "RecommendedActions": [
    "Immediate investigation required",
    "Freeze trader account pending review",
    "Review all recent trades and communications"
  ],
  "AssignedTo": "compliance_officer_001",
  "Investigation": {
    "Status": "IN_PROGRESS",
    "StartDate": "2024-12-15T14:35:00Z",
    "Priority": "HIGH",
    "Notes": "Initial review started"
  },
  "GSI1PK": "TRADER#trader_001",
  "GSI1SK": "ALERT#2024-12-15T14:30:22Z#HIGH",
  "GSI2PK": "SEVERITY#HIGH",
  "GSI2SK": "ALERT#2024-12-15T14:30:22Z",
  "GSI3PK": "TYPE#INSIDER_DEALING",
  "GSI3SK": "ALERT#2024-12-15T14:30:22Z",
  "TTL": 1767225600
}
```

### 4. Risk Score Entity
```json
{
  "PK": "TRADER#trader_001",
  "SK": "RISK_SCORE#2024-12-15T14:30:22Z",
  "EntityType": "RISK_SCORE",
  "RiskID": "risk_trader_001_20241215_143022",
  "Timestamp": "2024-12-15T14:30:22Z",
  "TraderID": "trader_001",
  "ModelType": "insider_dealing",
  "OverallScore": 0.85,
  "RiskProbabilities": {
    "HighRisk": 0.75,
    "MediumRisk": 0.20,
    "LowRisk": 0.05
  },
  "EvidenceFactors": {
    "MaterialInfo": 2,
    "TradingActivity": 2,
    "Timing": 2,
    "PriceImpact": 1
  },
  "BayesianAnalysis": {
    "ActiveNodes": 4,
    "HighRiskNodes": ["MaterialInfo", "Timing"],
    "CriticalNodes": ["MaterialInfo"],
    "NodeDetails": {
      "MaterialInfo": {
        "State": "Clear access",
        "Probability": 0.85,
        "Confidence": 0.90,
        "Contribution": 0.35
      },
      "TradingActivity": {
        "State": "Highly unusual",
        "Probability": 0.75,
        "Confidence": 0.85,
        "Contribution": 0.25
      },
      "Timing": {
        "State": "Highly suspicious",
        "Probability": 0.80,
        "Confidence": 0.95,
        "Contribution": 0.30
      },
      "PriceImpact": {
        "State": "Medium",
        "Probability": 0.65,
        "Confidence": 0.75,
        "Contribution": 0.10
      }
    }
  },
  "ContextualFactors": {
    "TraderRoleMultiplier": 1.2,
    "VolumeMultiplier": 1.3,
    "TimeframeMultiplier": 1.0,
    "MarketConditionsMultiplier": 1.1
  },
  "ESI": {
    "EvidenceSufficiencyIndex": 0.84,
    "Components": {
      "NodeActivationRatio": 0.83,
      "MeanConfidenceScore": 0.85,
      "FallbackRatio": 0.0,
      "ContributionEntropy": 0.92,
      "CrossClusterDiversity": 0.71
    }
  },
  "NewsContext": 2,
  "Explanation": "High insider dealing risk detected due to clear access to material information combined with suspicious timing before earnings announcement.",
  "GSI1PK": "DATE#2024-12-15",
  "GSI1SK": "RISK_SCORE#14:30:22#trader_001",
  "GSI2PK": "RISK_LEVEL#HIGH",
  "GSI2SK": "RISK_SCORE#2024-12-15T14:30:22Z",
  "TTL": 1767225600
}
```

### 5. Regulatory Rationale Entity
```json
{
  "PK": "ALERT#alert_20241215_143022",
  "SK": "RATIONALE",
  "EntityType": "REGULATORY_RATIONALE",
  "AlertID": "alert_20241215_143022",
  "RationaleID": "rationale_20241215_143022",
  "Timestamp": "2024-12-15T14:30:22Z",
  "DeterministicNarrative": "Analysis indicates potential insider dealing based on temporal proximity to material event announcement and unusual trading volume patterns.",
  "InferencePaths": [
    {
      "NodeName": "MaterialInfo",
      "EvidenceValue": 2,
      "Probability": 0.85,
      "Contribution": 0.35,
      "Rationale": "Trader has documented access to material non-public information through executive briefings",
      "Confidence": 0.90,
      "RegulatoryRelevance": "MAR Article 8 - Definition of insider information"
    },
    {
      "NodeName": "Timing",
      "EvidenceValue": 2,
      "Probability": 0.80,
      "Contribution": 0.30,
      "Rationale": "Trading activity occurred 24 hours before earnings announcement",
      "Confidence": 0.95,
      "RegulatoryRelevance": "MAR Article 14 - Prohibition of insider dealing"
    }
  ],
  "VOIAnalysis": {
    "CriticalNodes": ["MaterialInfo", "Timing"],
    "InformationGain": 0.45,
    "UncertaintyReduction": 0.60
  },
  "SensitivityReport": {
    "RobustScenarios": ["conservative", "moderate"],
    "SensitiveNodes": ["PriceImpact"],
    "StabilityScore": 0.88
  },
  "RegulatoryFrameworks": [
    "Market Abuse Regulation (MAR)",
    "MiFID II",
    "FCA Handbook"
  ],
  "AuditTrail": {
    "ModelVersion": "v2.1.0",
    "ConfigVersion": "v1.3.0",
    "ProcessingTime": "2024-12-15T14:30:22Z",
    "DataSources": ["trade_feed", "material_events", "trader_profiles"]
  },
  "ComplianceMetadata": {
    "ReviewRequired": true,
    "EscalationLevel": "HIGH",
    "STORRequired": true,
    "ReportingDeadline": "2024-12-16T14:30:22Z"
  },
  "GSI1PK": "COMPLIANCE#PENDING",
  "GSI1SK": "RATIONALE#2024-12-15T14:30:22Z",
  "TTL": 1767225600
}
```

### 6. Material Event Entity
```json
{
  "PK": "EVENT#event_001",
  "SK": "METADATA",
  "EntityType": "MATERIAL_EVENT",
  "EventID": "event_001",
  "Timestamp": "2024-12-16T09:00:00Z",
  "Type": "earnings_announcement",
  "Description": "Quarterly earnings announcement for ENERGY_CORP",
  "MaterialityScore": 0.9,
  "InstrumentsAffected": ["ENERGY_CORP", "ENERGY_CORP_OPTIONS"],
  "EventDetails": {
    "Source": "company_announcement",
    "Significance": "HIGH",
    "PriceImpactExpected": 0.05,
    "VolumeImpactExpected": 2.0
  },
  "RelatedActivity": {
    "PreEventTrades": 45,
    "SuspiciousTraders": ["trader_001", "trader_005"],
    "VolumeSpike": 3.2,
    "PriceMovement": 0.025
  },
  "GSI1PK": "INSTRUMENT#ENERGY_CORP",
  "GSI1SK": "EVENT#2024-12-16T09:00:00Z",
  "GSI2PK": "DATE#2024-12-16",
  "GSI2SK": "EVENT#09:00:00#event_001",
  "TTL": 1767225600
}
```

### 7. STOR Record Entity
```json
{
  "PK": "STOR#stor_20241215_143022",
  "SK": "RECORD",
  "EntityType": "STOR_RECORD",
  "RecordID": "stor_20241215_143022",
  "AlertID": "alert_20241215_143022",
  "Timestamp": "2024-12-15T14:30:22Z",
  "TraderID": "trader_001",
  "Instrument": "ENERGY_CORP",
  "TransactionType": "EQUITY_PURCHASE",
  "SuspiciousIndicators": [
    "Unusual volume before price-sensitive announcement",
    "Access to material non-public information",
    "Temporal proximity to earnings announcement"
  ],
  "RiskScore": 0.85,
  "RegulatoryRationale": "Trading activity demonstrates characteristics consistent with insider dealing as defined under MAR Article 8.",
  "EvidenceDetails": {
    "TradeVolume": 1500000,
    "PriceImpact": 0.025,
    "TimingScore": 0.80,
    "MaterialityScore": 0.90
  },
  "ComplianceOfficerNotes": "Immediate investigation initiated. Trader account frozen pending review.",
  "ReportingStatus": "SUBMITTED",
  "RegulatoryBody": "FCA",
  "SubmissionDate": "2024-12-15T16:00:00Z",
  "GSI1PK": "REGULATORY#SUBMITTED",
  "GSI1SK": "STOR#2024-12-15T14:30:22Z",
  "TTL": 1830297600
}
```

---

## Global Secondary Indexes (GSIs)

### GSI1: Trader Activity Index
```
GSI1PK: TRADER#trader_id or INSTRUMENT#instrument_id
GSI1SK: Activity timestamp with type
Purpose: Query trader activity or instrument activity
```

**Query Patterns:**
- Get all alerts for a trader
- Get all trades for an instrument
- Get activity by trader in time range

### GSI2: Time-Based Index
```
GSI2PK: DATE#YYYY-MM-DD
GSI2SK: Entity type with timestamp
Purpose: Query activities by date
```

**Query Patterns:**
- Get all alerts for a specific date
- Get all trades for a date range
- Get risk scores by date

### GSI3: Severity/Type Index
```
GSI3PK: SEVERITY#level or TYPE#type
GSI3SK: Timestamp with entity ID
Purpose: Query by alert severity or type
```

**Query Patterns:**
- Get all HIGH severity alerts
- Get all INSIDER_DEALING alerts
- Get CRITICAL alerts requiring attention

### GSI4: Status/Workflow Index
```
GSI4PK: STATUS#status_value
GSI4SK: Timestamp with entity ID
Purpose: Query by processing status
```

**Query Patterns:**
- Get all pending compliance reviews
- Get all active investigations
- Get all submitted STOR records

---

## Access Pattern Implementation

### 1. Get Trader Profile with Recent Activity
```python
# Single query to get trader profile
response = dynamodb.get_item(
    TableName='kor-ai-surveillance',
    Key={
        'PK': {'S': 'TRADER#trader_001'},
        'SK': {'S': 'PROFILE'}
    }
)

# Query recent activity using GSI1
response = dynamodb.query(
    TableName='kor-ai-surveillance',
    IndexName='GSI1',
    KeyConditionExpression='GSI1PK = :pk AND begins_with(GSI1SK, :sk)',
    ExpressionAttributeValues={
        ':pk': {'S': 'TRADER#trader_001'},
        ':sk': {'S': 'ALERT#2024-12'}
    }
)
```

### 2. Get High Severity Alerts
```python
response = dynamodb.query(
    TableName='kor-ai-surveillance',
    IndexName='GSI3',
    KeyConditionExpression='GSI3PK = :pk',
    ExpressionAttributeValues={
        ':pk': {'S': 'SEVERITY#HIGH'}
    }
)
```

### 3. Get Daily Trading Activity
```python
response = dynamodb.query(
    TableName='kor-ai-surveillance',
    IndexName='GSI2',
    KeyConditionExpression='GSI2PK = :pk AND begins_with(GSI2SK, :sk)',
    ExpressionAttributeValues={
        ':pk': {'S': 'DATE#2024-12-15'},
        ':sk': {'S': 'TRADE#'}
    }
)
```

### 4. Get Compliance Pending Items
```python
response = dynamodb.query(
    TableName='kor-ai-surveillance',
    IndexName='GSI4',
    KeyConditionExpression='GSI4PK = :pk',
    ExpressionAttributeValues={
        ':pk': {'S': 'COMPLIANCE#PENDING'}
    }
)
```

---

## Advanced DynamoDB Features

### 1. Time-to-Live (TTL)
```python
# Different TTL policies for different data types
TRADER_PROFILE_TTL = 5 * 365 * 24 * 60 * 60  # 5 years
TRADE_DATA_TTL = 7 * 365 * 24 * 60 * 60      # 7 years
ALERT_TTL = 3 * 365 * 24 * 60 * 60           # 3 years
RISK_SCORE_TTL = 2 * 365 * 24 * 60 * 60      # 2 years
STOR_RECORD_TTL = 10 * 365 * 24 * 60 * 60    # 10 years (regulatory)
```

### 2. DynamoDB Streams
```python
# Enable streams for real-time processing
STREAM_SPECIFICATION = {
    'StreamEnabled': True,
    'StreamViewType': 'NEW_AND_OLD_IMAGES'
}

# Stream processing for:
# - Real-time alert notifications
# - Risk score updates
# - Compliance workflow triggers
# - Audit trail maintenance
```

### 3. Point-in-Time Recovery (PITR)
```python
# Enable PITR for regulatory compliance
PITR_SPECIFICATION = {
    'PointInTimeRecoveryEnabled': True
}
```

### 4. Backup Strategy
```python
# Automated backups configuration
BACKUP_POLICY = {
    'BackupPolicy': {
        'BackupEnabled': True,
        'BackupRetentionPeriod': 35  # days
    }
}
```

---

## Performance Optimization

### 1. Partition Key Design
- **Hot Partition Avoidance**: Use composite keys with random suffixes for high-volume writes
- **Even Distribution**: Distribute load across multiple partitions using trader_id, date, or hash

### 2. Read Patterns Optimization
```python
# Batch reads for related items
batch_get_item({
    'RequestItems': {
        'kor-ai-surveillance': {
            'Keys': [
                {'PK': {'S': 'TRADER#trader_001'}, 'SK': {'S': 'PROFILE'}},
                {'PK': {'S': 'TRADER#trader_001'}, 'SK': {'S': 'RISK_SCORE#2024-12-15T14:30:22Z'}}
            ]
        }
    }
})
```

### 3. Write Patterns Optimization
```python
# Batch writes for related data
batch_write_item({
    'RequestItems': {
        'kor-ai-surveillance': [
            {
                'PutRequest': {
                    'Item': trade_item
                }
            },
            {
                'PutRequest': {
                    'Item': risk_score_item
                }
            }
        ]
    }
})
```

### 4. GSI Optimization
- **Sparse GSIs**: Only items with GSI attributes are indexed
- **Projection**: Include only necessary attributes in GSI projections
- **Query Patterns**: Design GSIs around specific query patterns

---

## Cost Optimization

### 1. On-Demand vs Provisioned
```python
# Use On-Demand for unpredictable workloads
BILLING_MODE = 'PAY_PER_REQUEST'

# Use Provisioned for predictable workloads
BILLING_MODE = 'PROVISIONED'
PROVISIONED_THROUGHPUT = {
    'ReadCapacityUnits': 1000,
    'WriteCapacityUnits': 500
}
```

### 2. Item Size Optimization
- **Compress large attributes**: Use compression for large JSON objects
- **Efficient encoding**: Use compact attribute names
- **Remove null values**: Don't store null or empty attributes

### 3. GSI Cost Management
- **Minimal projections**: Only project necessary attributes
- **Sparse indexes**: Use conditional GSI attributes
- **Query optimization**: Use specific queries instead of scans

---

## Security and Compliance

### 1. Encryption
```python
# Encryption at rest
ENCRYPTION_SPECIFICATION = {
    'EncryptionType': 'KMS',
    'KMSMasterKeyId': 'alias/kor-ai-surveillance-key'
}

# Encryption in transit
# Use VPC endpoints and SSL/TLS
```

### 2. Access Control
```python
# IAM policies for fine-grained access
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:region:account:table/kor-ai-surveillance",
            "Condition": {
                "ForAllValues:StringEquals": {
                    "dynamodb:LeadingKeys": ["TRADER#${aws:username}"]
                }
            }
        }
    ]
}
```

### 3. Audit Logging
```python
# CloudTrail integration for all API calls
# VPC Flow Logs for network access
# DynamoDB Streams for data change auditing
```

---

## Monitoring and Alerting

### 1. CloudWatch Metrics
```python
# Key metrics to monitor
METRICS = [
    'ConsumedReadCapacityUnits',
    'ConsumedWriteCapacityUnits',
    'ThrottledRequests',
    'UserErrors',
    'SystemErrors',
    'SuccessfulRequestLatency'
]
```

### 2. Custom Metrics
```python
# Application-specific metrics
CUSTOM_METRICS = [
    'AlertGenerationRate',
    'RiskScoreCalculationTime',
    'ComplianceReviewLatency',
    'STORReportingTime'
]
```

### 3. Alarms and Notifications
```python
# CloudWatch alarms for:
# - High throttling rates
# - Elevated error rates
# - Latency spikes
# - Capacity utilization
```

---

## Migration Strategy

### 1. Data Migration
```python
# Batch migration from relational database
# Use AWS DMS or custom ETL processes
# Validate data integrity during migration
```

### 2. Application Migration
```python
# Gradual migration approach:
# 1. Dual-write to both systems
# 2. Validate data consistency
# 3. Switch read traffic to DynamoDB
# 4. Decommission old system
```

### 3. Testing Strategy
```python
# Load testing with realistic data volumes
# Chaos engineering for resilience testing
# Performance benchmarking
```

---

## Development Best Practices

### 1. Item Design
```python
# Use consistent naming conventions
# Implement proper data validation
# Handle eventual consistency
# Design for horizontal scaling
```

### 2. Error Handling
```python
# Implement exponential backoff
# Handle throttling gracefully
# Use circuit breakers for resilience
# Log errors for troubleshooting
```

### 3. Testing
```python
# Unit tests with DynamoDB Local
# Integration tests with test tables
# Performance tests with production-like data
# Chaos engineering for resilience
```

---

This DynamoDB design provides a modern, scalable, and cost-effective solution for the Kor.ai surveillance platform, optimized for real-time market abuse detection and regulatory compliance reporting.