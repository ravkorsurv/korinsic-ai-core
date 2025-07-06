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

## 🔢 **2. Individual KDE Score Calculation**

### **Step 1: Sub-Dimension Scoring**
Each KDE is assessed across multiple sub-dimensions:

```
KDE_Score = Σ(SubDimension_Score × SubDimension_Weight) / Σ(SubDimension_Weight)
```

### **Sub-Dimension Weights:**
- **Null Presence**: 30% (most critical)
- **Format Validation**: 25%
- **Range Validation**: 20%
- **Freshness/Timeliness**: 15%
- **Uniqueness**: 10%

### **Step 2: Sub-Dimension Scoring Logic**

#### **Null Presence Score:**
```
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

#### **Format Validation Score:**
```
valid_rate = valid_records / total_non_null_records

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

#### **Range Validation Score:**
```
in_range_rate = records_in_valid_range / total_numeric_records

Score = CASE
    WHEN in_range_rate ≥ 0.98 THEN 1.0
    WHEN in_range_rate ≥ 0.95 THEN 0.9
    WHEN in_range_rate ≥ 0.85 THEN 0.8
    WHEN in_range_rate ≥ 0.75 THEN 0.7
    WHEN in_range_rate ≥ 0.60 THEN 0.5
    ELSE 0.3
END
```

#### **Freshness Score (for timestamps):**
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

---

## 📈 **3. Worked Example: trader_id KDE**

### **Sample Data Analysis:**
- **Total Records**: 10,000
- **Null Records**: 200 (2% null rate)
- **Valid Format**: 9,700 of 9,800 non-null (99% valid)
- **Expected Format**: `^[A-Z]{3}[0-9]{4}$`
- **Risk Level**: High (Weight = 3)
- **Tier**: Foundational (Weight = 1.0)

### **Step-by-Step Calculation:**

#### **Step 1: Sub-Dimension Scores**
```
Null Presence Score:
null_rate = 200/10,000 = 0.02 = 2%
Since null_rate ≤ 0.02, Score = 0.95

Format Validation Score:
valid_rate = 9,700/9,800 = 0.99 = 99%
Since valid_rate ≥ 0.98, Score = 1.0

Range Validation: N/A (string field)
Freshness: N/A (not timestamp)
Uniqueness: N/A (not required to be unique)
```

#### **Step 2: Weighted KDE Score**
```
KDE_Score = (0.95 × 0.30) + (1.0 × 0.25) + (0 × 0.20) + (0 × 0.15) + (0 × 0.10)
          = 0.285 + 0.25 + 0 + 0 + 0
          = 0.535

Normalized for applied weights:
KDE_Score = 0.535 / (0.30 + 0.25) = 0.535 / 0.55 = 0.973
```

#### **Step 3: Risk-Weighted Contribution**
```
Contribution = KDE_Score × Risk_Weight × Tier_Weight
             = 0.973 × 3 × 1.0
             = 2.919
```

---

## 🎯 **4. Complete DQSI Example**

### **Sample Portfolio Assessment:**
| KDE | Score | Risk | Tier | Weight | Contribution |
|-----|-------|------|------|--------|-------------|
| trader_id | 0.973 | High (3) | Found (1.0) | 3.0 | 2.919 |
| trade_time | 0.840 | High (3) | Found (1.0) | 3.0 | 2.520 |
| notional | 0.933 | High (3) | Found (1.0) | 3.0 | 2.799 |
| quantity | 0.887 | Med (2) | Found (1.0) | 2.0 | 1.774 |
| accuracy_score | 0.650 | High (3) | Enh (0.75) | 2.25 | 1.463 |
| consistency_score | 0.720 | Med (2) | Enh (0.75) | 1.5 | 1.080 |

### **Final DQSI Calculation:**
```
Total_Contribution = 2.919 + 2.520 + 2.799 + 1.774 + 1.463 + 1.080 = 12.555
Total_Weight = 3.0 + 3.0 + 3.0 + 2.0 + 2.25 + 1.5 = 14.75

DQSI_Score = 12.555 / 14.75 = 0.851
```

### **Critical KDE Check:**
```
Critical KDEs: trader_id, trade_time, notional
Minimum Critical Score: MIN(0.973, 0.840, 0.933) = 0.840

Since 0.840 ≥ 0.5, no cap applied
Final DQSI Score: 0.851
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