# DQSI KDE-Level Scoring Methodology - Mathematical Foundation

## 🎯 **Purpose: Attestation of Calculation Methodology**

This document provides the mathematical foundation and step-by-step calculation methodology for Data Quality Sufficiency Index (DQSI) KDE-level scoring, enabling stakeholders to understand and verify how quality scores are derived.

---

## 📊 **1. Overall DQSI Calculation Framework**

### **Formula:**
```
DQSI_Score = Σ(KDE_Score × Risk_Weight × Tier_Weight) / Σ(Risk_Weight × Tier_Weight)
```

### **Where:**
- **KDE_Score**: Individual Key Data Element score (0.0 to 1.0)
- **Risk_Weight**: Business risk weighting (High=3, Medium=2, Low=1)
- **Tier_Weight**: Tier importance (Foundational=1.0, Enhanced=0.75)

### **Critical KDE Cap Rule:**
```
IF any Critical_KDE_Score < 0.5 THEN DQSI_Score = MIN(DQSI_Score, 0.75)
```

---

## 🔢 **2. Seven-Dimensional DQSI Framework**

### **Dimensional Structure:**
```
FOUNDATIONAL TIER (4 dimensions):
├── Completeness (5 sub-dimensions)
├── Conformity (4 sub-dimensions)
├── Timeliness (3 sub-dimensions)
└── Coverage (2 sub-dimensions)

ENHANCED TIER (3 dimensions):
├── Accuracy (2 sub-dimensions)
├── Uniqueness (1 sub-dimension)
└── Consistency (1 sub-dimension)

TOTAL: 7 dimensions, 17 sub-dimensions
```

### **Step 1: Sub-Dimension Assessment**
Each KDE is assessed across applicable sub-dimensions based on strategy:

#### **Completeness Dimension (5 sub-dimensions):**
```
1. presence_check: null_rate scoring
2. mandatory_field_check: required field validation
3. conditional_completeness: business rule completeness
4. record_completeness: complete record validation
5. temporal_completeness: time-series completeness
```

#### **Conformity Dimension (4 sub-dimensions):**
```
1. format_check: regex pattern validation
2. length_check: field length validation
3. type_check: data type validation
4. range_check: numeric/date range validation
```

#### **Timeliness Dimension (3 sub-dimensions):**
```
1. freshness_check: data recency validation
2. currency_check: up-to-date validation
3. temporal_consistency: time sequence validation
```

#### **Coverage Dimension (2 sub-dimensions):**
```
1. volume_check: expected volume validation
2. scope_check: coverage completeness validation
```

#### **Accuracy Dimension (2 sub-dimensions):**
```
1. precision_check: decimal precision validation
2. accuracy_check: golden source comparison
```

#### **Uniqueness Dimension (1 sub-dimension):**
```
1. duplicate_check: uniqueness validation
```

#### **Consistency Dimension (1 sub-dimension):**
```
1. consistency_check: cross-field consistency validation
```

### **Step 2: KDE Scoring Process**

#### **Individual KDE Score Calculation:**
```
For each KDE:
1. Identify applicable sub-dimensions based on strategy
2. Score each applicable sub-dimension (0.0 to 1.0)
3. Calculate dimension scores
4. Weight by tier importance
5. Apply risk weighting
```

#### **Sub-Dimension Scoring Examples:**

**Presence Check (Completeness):**
```
null_rate = null_records / total_records

Score = CASE
    WHEN null_rate = 0.00 THEN 1.0
    WHEN null_rate ≤ 0.02 THEN 0.95
    WHEN null_rate ≤ 0.05 THEN 0.90
    WHEN null_rate ≤ 0.10 THEN 0.80
    WHEN null_rate ≤ 0.20 THEN 0.60
    WHEN null_rate ≤ 0.50 THEN 0.30
    ELSE 0.10
END
```

**Format Check (Conformity):**
```
valid_rate = valid_format_records / total_non_null_records

Score = CASE
    WHEN valid_rate ≥ 0.98 THEN 1.0
    WHEN valid_rate ≥ 0.95 THEN 0.9
    WHEN valid_rate ≥ 0.85 THEN 0.8
    WHEN valid_rate ≥ 0.75 THEN 0.7
    WHEN valid_rate ≥ 0.60 THEN 0.5
    WHEN valid_rate ≥ 0.40 THEN 0.3
    ELSE 0.1
END
```

**Freshness Check (Timeliness):**
```
Age Category Scoring:
- Age ≤ 1 hour: 1.0
- Age ≤ 4 hours: 0.9
- Age ≤ 24 hours: 0.7
- Age ≤ 7 days: 0.4
- Age ≤ 30 days: 0.2
- Age > 30 days: 0.1

freshness_score = Σ(record_age_score) / total_records
```

**Volume Check (Coverage):**
```
expected_volume = historical_average_volume
actual_volume = current_record_count
volume_ratio = actual_volume / expected_volume

Score = CASE
    WHEN volume_ratio ≥ 0.95 AND volume_ratio ≤ 1.05 THEN 1.0
    WHEN volume_ratio ≥ 0.90 AND volume_ratio ≤ 1.10 THEN 0.9
    WHEN volume_ratio ≥ 0.80 AND volume_ratio ≤ 1.20 THEN 0.8
    WHEN volume_ratio ≥ 0.70 AND volume_ratio ≤ 1.30 THEN 0.6
    ELSE 0.3
END
```

### **Step 3: Synthetic KDE Integration**

#### **Synthetic Timeliness KDE:**
```
Synthetic_Timeliness_Score = Σ(timestamp_freshness_scores) / total_timestamp_fields

Applied to: All data flows with timestamp fields
Risk Weight: High (3)
Tier Weight: Foundational (1.0)
```

#### **Synthetic Coverage KDE:**
```
Synthetic_Coverage_Score = (volume_score + scope_score) / 2

volume_score = current_volume / expected_volume (capped at 1.0)
scope_score = covered_entities / total_expected_entities

Applied to: All data flows
Risk Weight: High (3)
Tier Weight: Foundational (1.0)
```

---

## 📈 **3. Worked Example: trader_id KDE**

### **Sample Data Analysis:**
- **Total Records**: 10,000
- **Null Records**: 200 (2% null rate)
- **Valid Format**: 9,700 of 9,800 non-null (99% valid)
- **Expected Format**: `^[A-Z]{3}[0-9]{4}$`
- **Risk Level**: High (Weight = 3)
- **Tier**: Foundational (Weight = 1.0)
- **Strategy**: Role-Aware Producer (all 7 dimensions active)

### **Step-by-Step Calculation:**

#### **Step 1: Dimensional Assessment**
```
COMPLETENESS DIMENSION:
├── presence_check: null_rate = 2% → Score = 0.95
├── mandatory_field_check: required field → Score = 1.0
├── conditional_completeness: N/A (no business rules)
├── record_completeness: N/A (single field)
└── temporal_completeness: N/A (not time-series)
Completeness Score = (0.95 + 1.0) / 2 = 0.975

CONFORMITY DIMENSION:
├── format_check: 99% valid → Score = 1.0
├── length_check: all 7 chars → Score = 1.0  
├── type_check: all strings → Score = 1.0
└── range_check: N/A (string field)
Conformity Score = (1.0 + 1.0 + 1.0) / 3 = 1.0

TIMELINESS DIMENSION:
├── freshness_check: N/A (not timestamp)
├── currency_check: N/A (not timestamp)
└── temporal_consistency: N/A (not timestamp)
Timeliness Score = N/A (not applicable)

COVERAGE DIMENSION:
├── volume_check: N/A (field-level KDE)
└── scope_check: N/A (field-level KDE)
Coverage Score = N/A (not applicable)

ACCURACY DIMENSION:
├── precision_check: N/A (string field)
└── accuracy_check: N/A (no golden source)
Accuracy Score = N/A (not applicable)

UNIQUENESS DIMENSION:
├── duplicate_check: N/A (not required unique)
Uniqueness Score = N/A (not applicable)

CONSISTENCY DIMENSION:
├── consistency_check: N/A (single field)
Consistency Score = N/A (not applicable)
```

#### **Step 2: KDE Score Aggregation**
```
Applied Dimensions: Completeness, Conformity
Tier Weights: Both Foundational (1.0)

KDE_Score = (Completeness_Score × 1.0) + (Conformity_Score × 1.0) / 2
          = (0.975 × 1.0) + (1.0 × 1.0) / 2
          = 1.975 / 2
          = 0.988
```

#### **Step 3: Risk-Weighted Contribution**
```
Contribution = KDE_Score × Risk_Weight × Tier_Weight
             = 0.988 × 3 × 1.0
             = 2.964
```

### **Synthetic KDE Examples:**

#### **Synthetic Timeliness KDE:**
```
Data Flow: trading_data_feed
Timestamp Fields: [trade_time, settlement_time, booking_time]

trade_time freshness: 0.85 (avg 2 hours old)
settlement_time freshness: 0.60 (avg 1 day old)  
booking_time freshness: 0.90 (avg 1 hour old)

Synthetic_Timeliness_Score = (0.85 + 0.60 + 0.90) / 3 = 0.783

Risk Weight: High (3)
Tier Weight: Foundational (1.0)
Contribution: 0.783 × 3 × 1.0 = 2.349
```

#### **Synthetic Coverage KDE:**
```
Data Flow: trading_data_feed
Expected Volume: 50,000 records/day
Actual Volume: 48,500 records/day
Volume Ratio: 48,500/50,000 = 0.97

Expected Scope: 15 trading desks
Actual Scope: 14 trading desks  
Scope Ratio: 14/15 = 0.93

volume_score = 0.97 → Score = 1.0 (within 95-105% range)
scope_score = 0.93 → Score = 0.9 (within 90-110% range)

Synthetic_Coverage_Score = (1.0 + 0.9) / 2 = 0.95

Risk Weight: High (3)  
Tier Weight: Foundational (1.0)
Contribution: 0.95 × 3 × 1.0 = 2.85
```

---

## 🎯 **4. Complete DQSI Example**

### **Sample Data Flow Assessment: trading_data_feed**

#### **Regular KDEs:**
| KDE | Dimensions Applied | Score | Risk | Tier | Weight | Contribution |
|-----|-------------------|-------|------|------|--------|-------------|
| trader_id | Completeness, Conformity | 0.988 | High (3) | Found (1.0) | 3.0 | 2.964 |
| trade_time | Completeness, Conformity, Timeliness | 0.840 | High (3) | Found (1.0) | 3.0 | 2.520 |
| notional | Completeness, Conformity, Accuracy | 0.933 | High (3) | Found (1.0) | 3.0 | 2.799 |
| quantity | Completeness, Conformity | 0.887 | Med (2) | Found (1.0) | 2.0 | 1.774 |
| price | Completeness, Conformity, Accuracy | 0.725 | Med (2) | Found (1.0) | 2.0 | 1.450 |
| instrument | Completeness, Conformity, Uniqueness | 0.680 | Low (1) | Found (1.0) | 1.0 | 0.680 |

#### **Synthetic KDEs:**
| KDE | Dimensions Applied | Score | Risk | Tier | Weight | Contribution |
|-----|-------------------|-------|------|------|--------|-------------|
| synthetic_timeliness | Timeliness (all timestamp fields) | 0.783 | High (3) | Found (1.0) | 3.0 | 2.349 |
| synthetic_coverage | Coverage (volume + scope) | 0.950 | High (3) | Found (1.0) | 3.0 | 2.850 |

#### **Enhanced Tier KDEs (Role-Aware Producer only):**
| KDE | Dimensions Applied | Score | Risk | Tier | Weight | Contribution |
|-----|-------------------|-------|------|------|--------|-------------|
| cross_system_accuracy | Accuracy (golden source) | 0.650 | High (3) | Enh (0.75) | 2.25 | 1.463 |
| consistency_validation | Consistency (cross-field) | 0.720 | Med (2) | Enh (0.75) | 1.5 | 1.080 |

### **Dimensional Breakdown:**
```
FOUNDATIONAL TIER (Applied to all strategies):
├── Completeness: 6 KDEs assessed
├── Conformity: 6 KDEs assessed  
├── Timeliness: 1 synthetic KDE + 1 timestamp KDE
└── Coverage: 1 synthetic KDE

ENHANCED TIER (Role-Aware Producer only):
├── Accuracy: 2 KDEs assessed + 1 synthetic
├── Uniqueness: 1 KDE assessed
└── Consistency: 1 KDE assessed
```

### **Final DQSI Calculation:**
```
Regular KDEs Contribution = 2.964 + 2.520 + 2.799 + 1.774 + 1.450 + 0.680 = 12.187
Synthetic KDEs Contribution = 2.349 + 2.850 = 5.199
Enhanced KDEs Contribution = 1.463 + 1.080 = 2.543

Total_Contribution = 12.187 + 5.199 + 2.543 = 19.929

Regular KDEs Weight = 3.0 + 3.0 + 3.0 + 2.0 + 2.0 + 1.0 = 14.0
Synthetic KDEs Weight = 3.0 + 3.0 = 6.0
Enhanced KDEs Weight = 2.25 + 1.5 = 3.75

Total_Weight = 14.0 + 6.0 + 3.75 = 23.75

DQSI_Score = 19.929 / 23.75 = 0.839
```

### **Critical KDE Check:**
```
Critical KDEs: trader_id, trade_time, notional, synthetic_timeliness, synthetic_coverage
Minimum Critical Score: MIN(0.988, 0.840, 0.933, 0.783, 0.950) = 0.783

Since 0.783 ≥ 0.5, no cap applied
Final DQSI Score: 0.839
```

### **Strategy Comparison:**
```
FALLBACK STRATEGY (4 dimensions, 5 sub-dimensions):
├── Uses only: Completeness, Conformity, Timeliness, Coverage
├── No Enhanced tier KDEs
├── Simplified validation rules
└── Estimated Score: ~0.65

ROLE-AWARE CONSUMER (4 dimensions, 9 sub-dimensions):
├── Uses: Completeness, Conformity, Timeliness, Coverage
├── Enhanced validation rules
├── Includes synthetic KDEs
└── Estimated Score: ~0.75

ROLE-AWARE PRODUCER (7 dimensions, 17 sub-dimensions):
├── Uses: All 7 dimensions
├── Full validation framework
├── Includes synthetic + enhanced KDEs
└── Calculated Score: 0.839
```

---

## 📊 **5. Confidence Index Calculation**

### **Formula:**
```
Confidence_Index = Base_Confidence × Mode_Modifier × Imputation_Factor × Critical_Factor
```

### **Components:**
- **Base_Confidence**: 0.9 (Role-Aware) or 0.7 (Fallback)
- **Mode_Modifier**: 1.0 (complete data) to 0.8 (partial data)
- **Imputation_Factor**: 1.0 - (imputed_rate × 0.5)
- **Critical_Factor**: 0.85 if critical KDEs missing, else 1.0

### **Example:**
```
Base_Confidence = 0.9 (Role-Aware mode)
Mode_Modifier = 0.95 (5% data unavailable)
Imputation_Factor = 1.0 - (0.15 × 0.5) = 0.925 (15% imputed)
Critical_Factor = 1.0 (no critical KDEs missing)

Confidence_Index = 0.9 × 0.95 × 0.925 × 1.0 = 0.791
```

---

## 🎯 **6. Attestation Summary**

### **System Attestation:**
✅ **"X is running"**: DQSI calculation engine processes KDE data using defined mathematical framework

### **Output Attestation:**
✅ **"Tells us Y"**: System produces:
- **DQSI Score**: 0.851 (85.1% data quality)
- **Confidence Index**: 0.791 (79.1% confidence)
- **Critical KDE Status**: All above threshold
- **Sub-dimension Breakdown**: Detailed scoring by validation type

### **Calculation Attestation:**
✅ **"HOW calculated"**: 
- **Transparent methodology** with documented formulas
- **Step-by-step calculations** that can be verified
- **Risk-weighted aggregation** reflecting business priorities
- **Confidence measures** indicating reliability

### **Validation Attestation:**
✅ **"Mathematically sound"**:
- **Weighted averages** prevent any single KDE from dominating
- **Risk-based prioritization** aligns with business impact
- **Critical KDE caps** prevent false confidence from low-impact high scores
- **Confidence intervals** provide uncertainty quantification

---

## 📋 **7. Stakeholder Interpretation Guide**

### **DQSI Score Interpretation:**
- **0.8 - 1.0**: GOOD - Data suitable for critical business decisions
- **0.7 - 0.8**: ACCEPTABLE - Data usable with minor validation
- **0.5 - 0.7**: POOR - Data requires significant improvement
- **0.0 - 0.5**: CRITICAL - Data unsuitable for business use

### **Confidence Index Interpretation:**
- **0.8 - 1.0**: HIGH - Score is reliable and actionable
- **0.6 - 0.8**: MODERATE - Score directionally correct, some uncertainty
- **0.4 - 0.6**: LOW - Score indicative only, significant uncertainty
- **0.0 - 0.4**: VERY LOW - Score unreliable, more data needed

### **Business Decision Framework:**
```
IF DQSI_Score ≥ 0.8 AND Confidence_Index ≥ 0.8 THEN
    Status = "APPROVED - Data suitable for business use"
ELSE IF DQSI_Score ≥ 0.7 AND Confidence_Index ≥ 0.6 THEN
    Status = "CONDITIONAL - Data usable with validation"
ELSE IF DQSI_Score ≥ 0.5 THEN
    Status = "IMPROVEMENT REQUIRED - Address issues before use"
ELSE
    Status = "REJECTED - Data unsuitable for business use"
```

This methodology provides **complete mathematical transparency** for stakeholder review and regulatory attestation.