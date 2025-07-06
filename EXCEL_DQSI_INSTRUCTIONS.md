# Excel DQSI Calculator - Usage Instructions

## 🎯 **Quick Setup Guide**

### **Step 1: Import the Template**
1. Download `DQSI_Excel_Template.csv`
2. Open in Excel
3. Use **Data → Text to Columns** to separate into proper columns
4. **Save as Excel workbook** (.xlsx)

### **Step 2: Enter Your Data**
Go to the **Raw_Data** section and update:
- **Total_Records**: Your actual record counts
- **Null_Records**: Count of null/empty values  
- **Valid_Format**: Count of records matching expected format
- **Valid_Range**: Count of records within valid ranges
- **Fresh_Records**: Count of recent/current records
- **Expected_Vol** & **Actual_Vol**: For coverage calculation

### **Step 3: View Results** 
Check the **Summary** section for:
- **Final_DQSI_Score**: Your overall quality score
- **Quality_Status**: GOOD/ACCEPTABLE/POOR/CRITICAL
- **Critical_KDE_Check**: PASSED/FAILED validation
- **Confidence_Index**: Reliability of the score

---

## 📊 **What You Get**

### **Immediate Attestation Value:**
✅ **"X is running"**: DQSI calculation engine with 7-dimensional framework  
✅ **"Tells us Y"**: Final score of 0.839 (83.9% quality) with HIGH confidence  
✅ **"HOW calculated"**: Every formula visible and auditable in Excel

### **Sample Results:**
```
Final DQSI Score: 0.839 (83.9%)
Quality Status: GOOD
Critical KDE Check: PASSED
Confidence Index: 0.791 (79.1%)
Strategy: Role-Aware Producer (7 dimensions, 17 sub-dimensions)
```

### **Individual KDE Breakdown:**
```
trader_id: 0.988 (Completeness + Conformity)
trade_time: 0.853 (Completeness + Conformity + Timeliness)  
notional: 0.933 (Completeness + Accuracy)
synthetic_timeliness: 0.783 (System-level timeliness)
synthetic_coverage: 0.950 (Volume + scope coverage)
```

---

## 🔧 **Key Features for Stakeholders**

### **Complete Mathematical Transparency:**
- **Every calculation visible** in Excel cells
- **Risk weights applied**: High=3, Medium=2, Low=1
- **Tier weights shown**: Foundational=1.0, Enhanced=0.75
- **Critical KDE cap**: Prevents false confidence

### **7-Dimensional Framework:**
```
FOUNDATIONAL (4 dimensions): Completeness, Conformity, Timeliness, Coverage
ENHANCED (3 dimensions): Accuracy, Uniqueness, Consistency
SYNTHETIC KDES: System-level timeliness and coverage metrics
```

### **Strategy Comparison Built-in:**
- **Fallback**: 4 dimensions, ~65% score
- **Role-Aware Consumer**: 4 dimensions, ~75% score  
- **Role-Aware Producer**: 7 dimensions, 83.9% score

---

## 🎯 **Business Use Cases**

### **For Executives:**
- **Single score**: 83.9% quality = "GOOD" rating
- **Clear interpretation**: Ready for business use
- **Confidence measure**: 79.1% reliability

### **For Auditors:**
- **Formula transparency**: Every calculation visible
- **Reproducible results**: Same inputs = same outputs
- **Mathematical soundness**: Risk-weighted, tier-adjusted

### **For Regulators:**
- **Documented methodology**: Complete audit trail
- **Critical KDE validation**: Safety mechanisms in place
- **Strategy differentiation**: Appropriate for firm size/complexity

---

## 📋 **Customization Options**

### **Change Risk Levels:**
Update Column B in Raw_Data: `High/Medium/Low`

### **Adjust Tier Classifications:**
Update Column C in Raw_Data: `Foundational/Enhanced`

### **Modify Scoring Thresholds:**
Edit the nested IF formulas in SubDim_Calc section

### **Add/Remove KDEs:**
- Insert/delete rows in Raw_Data section
- Copy formulas down in other sections
- Update range references as needed

---

## 🚀 **Ready for Immediate Use**

This Excel template provides **complete DQSI calculation capability** that stakeholders can:
- **Download and use today**
- **Customize for their data**
- **Audit every calculation**
- **Present to regulators**
- **Use for attestation**

The methodology is **mathematically sound**, **fully transparent**, and implements the complete **7-dimensional DQSI framework** with synthetic KDEs and critical KDE caps - exactly what you need for stakeholder attestation!