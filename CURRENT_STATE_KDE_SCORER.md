# Current State KDE Scoring Implementation Guide

## 🎯 **Challenge: Implementing KDE Scoring on Existing Systems**

Your clients don't have the DQSI system yet - but they need to assess their **current data quality** using KDE-level scoring to:
1. **Baseline their current state**
2. **Identify critical KDEs with issues**
3. **Prioritize improvement efforts** 
4. **Build business case** for DQSI implementation

---

## 📊 **4 Implementation Approaches Based on Data Access**

### **Approach 1: Database/SQL Access**
*Best for: Direct database access to trading/surveillance data*

```sql
-- Example: KDE-level scoring via SQL queries
-- Target: trader_id KDE assessment

-- Step 1: Basic data profiling
WITH kde_analysis AS (
    SELECT 
        'trader_id' as kde_name,
        COUNT(*) as total_records,
        COUNT(trader_id) as non_null_count,
        COUNT(DISTINCT trader_id) as unique_count,
        
        -- Null presence scoring
        CASE 
            WHEN (COUNT(trader_id) * 1.0 / COUNT(*)) >= 0.95 THEN 1.0
            WHEN (COUNT(trader_id) * 1.0 / COUNT(*)) >= 0.90 THEN 0.9
            WHEN (COUNT(trader_id) * 1.0 / COUNT(*)) >= 0.80 THEN 0.8
            ELSE 0.5
        END as null_presence_score,
        
        -- Format validation scoring
        CASE 
            WHEN SUM(CASE WHEN trader_id ~ '^[A-Z]{3}[0-9]{4}$' THEN 1 ELSE 0 END) * 1.0 / COUNT(trader_id) >= 0.95 THEN 1.0
            WHEN SUM(CASE WHEN trader_id ~ '^[A-Z]{3}[0-9]{4}$' THEN 1 ELSE 0 END) * 1.0 / COUNT(trader_id) >= 0.85 THEN 0.9
            WHEN SUM(CASE WHEN trader_id ~ '^[A-Z]{3}[0-9]{4}$' THEN 1 ELSE 0 END) * 1.0 / COUNT(trader_id) >= 0.75 THEN 0.8
            ELSE 0.5
        END as format_score,
        
        -- Uniqueness validation
        CASE 
            WHEN COUNT(DISTINCT trader_id) * 1.0 / COUNT(trader_id) >= 0.98 THEN 1.0
            WHEN COUNT(DISTINCT trader_id) * 1.0 / COUNT(trader_id) >= 0.95 THEN 0.9
            WHEN COUNT(DISTINCT trader_id) * 1.0 / COUNT(trader_id) >= 0.90 THEN 0.8
            ELSE 0.5
        END as uniqueness_score
        
    FROM trading_data 
    WHERE trade_date >= CURRENT_DATE - INTERVAL '30 days'
)

-- Step 2: Aggregate KDE score
SELECT 
    kde_name,
    total_records,
    non_null_count,
    unique_count,
    null_presence_score,
    format_score,
    uniqueness_score,
    
    -- Calculate weighted KDE score
    (null_presence_score * 0.4 + format_score * 0.3 + uniqueness_score * 0.3) as kde_score,
    
    -- Interpretation
    CASE 
        WHEN (null_presence_score * 0.4 + format_score * 0.3 + uniqueness_score * 0.3) >= 0.8 THEN 'GOOD'
        WHEN (null_presence_score * 0.4 + format_score * 0.3 + uniqueness_score * 0.3) >= 0.7 THEN 'ACCEPTABLE'
        WHEN (null_presence_score * 0.4 + format_score * 0.3 + uniqueness_score * 0.3) >= 0.5 THEN 'POOR'
        ELSE 'CRITICAL'
    END as quality_status
    
FROM kde_analysis;
```

### **Approach 2: File/CSV Analysis** 
*Best for: Exported data files, CSV dumps, batch extracts*

```python
#!/usr/bin/env python3
"""
Standalone KDE Scorer for CSV/File Data
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any

class CurrentStateKDEScorer:
    """Scores KDEs from existing CSV/file data"""
    
    def __init__(self):
        self.kde_configs = {}
        self.scoring_results = {}
    
    def load_kde_config(self, config_file: str):
        """Load KDE configuration from existing system mapping"""
        import yaml
        with open(config_file, 'r') as f:
            self.kde_configs = yaml.safe_load(f)
    
    def score_csv_file(self, file_path: str, kde_mappings: Dict[str, Dict]) -> Dict[str, float]:
        """Score KDEs from a CSV file"""
        
        # Load data
        df = pd.read_csv(file_path)
        kde_scores = {}
        
        for kde_name, kde_config in kde_mappings.items():
            if kde_name not in df.columns:
                print(f"Warning: KDE '{kde_name}' not found in data")
                continue
                
            # Score this KDE
            kde_score = self._score_kde_column(df[kde_name], kde_config)
            kde_scores[kde_name] = kde_score
            
            print(f"KDE '{kde_name}': {kde_score:.3f}")
        
        return kde_scores
    
    def _score_kde_column(self, data: pd.Series, kde_config: Dict) -> float:
        """Score individual KDE column"""
        
        # Sub-dimension scores
        scores = {}
        
        # 1. Null presence
        scores['null_presence'] = self._score_null_presence(data)
        
        # 2. Format validation
        if 'format_pattern' in kde_config:
            scores['format'] = self._score_format(data, kde_config['format_pattern'])
        
        # 3. Range validation  
        if 'valid_range' in kde_config:
            scores['range'] = self._score_range(data, kde_config['valid_range'])
        
        # 4. Type-specific validation
        data_type = kde_config.get('data_type', 'string')
        if data_type == 'timestamp':
            scores['freshness'] = self._score_timestamp_freshness(data)
        elif data_type == 'numeric':
            scores['precision'] = self._score_numeric_precision(data)
        elif data_type == 'categorical':
            scores['reference'] = self._score_categorical_reference(data, kde_config.get('valid_values', []))
        
        # 5. Uniqueness (if required)
        if kde_config.get('unique_required', False):
            scores['uniqueness'] = self._score_uniqueness(data)
        
        # Aggregate sub-dimension scores
        if scores:
            return sum(scores.values()) / len(scores)
        else:
            return 0.5  # Default for minimal validation
    
    def _score_null_presence(self, data: pd.Series) -> float:
        """Score null presence"""
        null_rate = data.isnull().sum() / len(data)
        
        if null_rate == 0.0:
            return 1.0
        elif null_rate <= 0.05:
            return 0.9
        elif null_rate <= 0.10:
            return 0.8
        elif null_rate <= 0.20:
            return 0.6
        else:
            return 0.3
    
    def _score_format(self, data: pd.Series, pattern: str) -> float:
        """Score format validation"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0.0
            
        valid_count = non_null_data.astype(str).str.match(pattern).sum()
        valid_rate = valid_count / len(non_null_data)
        
        if valid_rate >= 0.95:
            return 1.0
        elif valid_rate >= 0.85:
            return 0.9
        elif valid_rate >= 0.75:
            return 0.8
        elif valid_rate >= 0.60:
            return 0.6
        else:
            return 0.3
    
    def _score_range(self, data: pd.Series, valid_range: Dict) -> float:
        """Score range validation"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0.0
        
        min_val = valid_range.get('min')
        max_val = valid_range.get('max')
        
        in_range_count = 0
        for value in non_null_data:
            try:
                if min_val is not None and value < min_val:
                    continue
                if max_val is not None and value > max_val:
                    continue
                in_range_count += 1
            except:
                continue
        
        range_rate = in_range_count / len(non_null_data)
        
        if range_rate >= 0.95:
            return 1.0
        elif range_rate >= 0.85:
            return 0.9
        elif range_rate >= 0.75:
            return 0.8
        elif range_rate >= 0.60:
            return 0.6
        else:
            return 0.3
    
    def _score_timestamp_freshness(self, data: pd.Series) -> float:
        """Score timestamp freshness"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0.0
        
        current_time = datetime.now()
        fresh_count = 0
        
        for timestamp_str in non_null_data:
            try:
                # Try multiple timestamp formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d']:
                    try:
                        ts = datetime.strptime(str(timestamp_str), fmt)
                        break
                    except:
                        continue
                else:
                    continue
                
                age = current_time - ts
                if age <= timedelta(hours=1):
                    fresh_count += 1
                elif age <= timedelta(hours=24):
                    fresh_count += 0.7
                elif age <= timedelta(days=7):
                    fresh_count += 0.4
                else:
                    fresh_count += 0.1
                    
            except:
                continue
        
        freshness_rate = fresh_count / len(non_null_data)
        
        if freshness_rate >= 0.90:
            return 1.0
        elif freshness_rate >= 0.70:
            return 0.8
        elif freshness_rate >= 0.50:
            return 0.6
        else:
            return 0.3
    
    def _score_uniqueness(self, data: pd.Series) -> float:
        """Score uniqueness"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0.0
        
        unique_rate = len(non_null_data.unique()) / len(non_null_data)
        
        if unique_rate >= 0.98:
            return 1.0
        elif unique_rate >= 0.95:
            return 0.9
        elif unique_rate >= 0.90:
            return 0.8
        elif unique_rate >= 0.80:
            return 0.6
        else:
            return 0.3
    
    def generate_assessment_report(self, kde_scores: Dict[str, float], kde_configs: Dict) -> str:
        """Generate assessment report"""
        
        report = []
        report.append("=" * 50)
        report.append("CURRENT STATE KDE ASSESSMENT REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Calculate overall score
        if kde_scores:
            # Apply risk weights
            weighted_sum = 0
            total_weights = 0
            
            for kde_name, score in kde_scores.items():
                config = kde_configs.get(kde_name, {})
                weight = config.get('weight', 1)
                
                weighted_sum += score * weight
                total_weights += weight
            
            overall_score = weighted_sum / total_weights if total_weights > 0 else 0
            
            report.append(f"OVERALL DQSI SCORE: {overall_score:.3f} ({overall_score*100:.1f}%)")
            
            if overall_score >= 0.8:
                status = "GOOD - Ready for production"
            elif overall_score >= 0.7:
                status = "ACCEPTABLE - Minor improvements needed"
            elif overall_score >= 0.5:
                status = "POOR - Significant improvements required"
            else:
                status = "CRITICAL - Immediate action required"
            
            report.append(f"STATUS: {status}")
            report.append("")
        
        # Individual KDE scores
        report.append("INDIVIDUAL KDE SCORES:")
        report.append("-" * 25)
        
        for kde_name, score in sorted(kde_scores.items(), key=lambda x: x[1]):
            config = kde_configs.get(kde_name, {})
            risk = config.get('risk', 'medium')
            
            if score >= 0.8:
                status = "GOOD"
            elif score >= 0.7:
                status = "ACCEPTABLE"
            elif score >= 0.5:
                status = "POOR"
            else:
                status = "CRITICAL"
            
            report.append(f"  {kde_name}: {score:.3f} ({status}) - {risk} risk")
        
        report.append("")
        
        # Recommendations
        critical_kdes = [name for name, score in kde_scores.items() if score < 0.5]
        poor_kdes = [name for name, score in kde_scores.items() if 0.5 <= score < 0.7]
        
        report.append("RECOMMENDATIONS:")
        report.append("-" * 15)
        
        if critical_kdes:
            report.append(f"IMMEDIATE ACTION: Fix critical KDEs: {', '.join(critical_kdes)}")
        
        if poor_kdes:
            report.append(f"PRIORITY: Improve poor KDEs: {', '.join(poor_kdes)}")
        
        if overall_score < 0.5:
            report.append("FOCUS: Implement basic data validation and cleansing")
        elif overall_score < 0.7:
            report.append("FOCUS: Systematic data quality improvement program")
        else:
            report.append("FOCUS: Optimize and maintain current quality levels")
        
        return "\n".join(report)


# Example usage
def assess_current_trading_data():
    """Example assessment of current trading data"""
    
    scorer = CurrentStateKDEScorer()
    
    # Define KDE configuration based on their current system
    kde_configs = {
        'trader_id': {
            'data_type': 'string',
            'format_pattern': r'^[A-Z]{3}[0-9]{4}$',
            'unique_required': False,
            'weight': 3,
            'risk': 'high'
        },
        'trade_time': {
            'data_type': 'timestamp',
            'weight': 3,
            'risk': 'high'
        },
        'notional': {
            'data_type': 'numeric',
            'valid_range': {'min': 0, 'max': 1000000000},
            'weight': 3,
            'risk': 'high'
        },
        'quantity': {
            'data_type': 'numeric',
            'valid_range': {'min': 1, 'max': 10000000},
            'weight': 2,
            'risk': 'medium'
        },
        'instrument': {
            'data_type': 'categorical',
            'format_pattern': r'^[A-Z]{3,4}$',
            'weight': 1,
            'risk': 'low'
        }
    }
    
    # Score their current data
    kde_scores = scorer.score_csv_file('current_trading_data.csv', kde_configs)
    
    # Generate report
    report = scorer.generate_assessment_report(kde_scores, kde_configs)
    print(report)
    
    return kde_scores

if __name__ == "__main__":
    assess_current_trading_data()
```

### **Approach 3: API/Real-time Stream Analysis**
*Best for: Live trading systems, real-time feeds*

```python
"""
Real-time KDE Scoring for Live Data Streams
"""

import asyncio
import json
from datetime import datetime
from collections import deque
from typing import Dict, Any

class RealTimeKDEScorer:
    """Score KDEs from real-time data streams"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.data_windows = {}
        self.current_scores = {}
        
    async def process_stream_message(self, message: Dict[str, Any], flow_name: str):
        """Process incoming stream message"""
        
        # Initialize window for this flow
        if flow_name not in self.data_windows:
            self.data_windows[flow_name] = deque(maxlen=self.window_size)
        
        # Add message to window
        self.data_windows[flow_name].append({
            'timestamp': datetime.now(),
            'data': message
        })
        
        # Score KDEs if we have enough data
        if len(self.data_windows[flow_name]) >= 100:  # Minimum sample
            await self._score_window(flow_name)
    
    async def _score_window(self, flow_name: str):
        """Score KDEs for current data window"""
        
        window_data = list(self.data_windows[flow_name])
        kde_scores = {}
        
        # Extract KDE values from window
        for kde_name in self._get_flow_kdes(flow_name):
            values = []
            for record in window_data:
                if kde_name in record['data']:
                    values.append(record['data'][kde_name])
                else:
                    values.append(None)
            
            # Score this KDE
            kde_scores[kde_name] = self._score_kde_values(values, kde_name)
        
        self.current_scores[flow_name] = kde_scores
        
        # Trigger alerts if scores drop
        await self._check_quality_alerts(flow_name, kde_scores)
    
    def _get_flow_kdes(self, flow_name: str) -> List[str]:
        """Get KDEs for this data flow"""
        # This would be configured based on the client's data flows
        kde_mappings = {
            'trading_feed': ['trader_id', 'trade_time', 'notional', 'quantity'],
            'market_data': ['symbol', 'price', 'volume', 'timestamp'],
            'alerts': ['alert_id', 'alert_type', 'confidence_score']
        }
        return kde_mappings.get(flow_name, [])
    
    async def _check_quality_alerts(self, flow_name: str, kde_scores: Dict[str, float]):
        """Check for quality degradation and trigger alerts"""
        
        for kde_name, score in kde_scores.items():
            if score < 0.5:  # Critical threshold
                await self._send_alert(f"CRITICAL: {flow_name}.{kde_name} score dropped to {score:.3f}")
            elif score < 0.7:  # Warning threshold  
                await self._send_alert(f"WARNING: {flow_name}.{kde_name} score dropped to {score:.3f}")
    
    async def _send_alert(self, message: str):
        """Send quality alert"""
        print(f"[{datetime.now()}] QUALITY ALERT: {message}")
        # Could integrate with their existing alerting system
```

### **Approach 4: Sampling-Based Assessment**
*Best for: Large systems where full data access is limited*

```python
"""
Statistical Sampling KDE Assessment
"""

import random
import pandas as pd
from typing import Dict, List

class SamplingKDEAssessment:
    """Assess KDE quality using statistical sampling"""
    
    def __init__(self, confidence_level: float = 0.95, margin_of_error: float = 0.05):
        self.confidence_level = confidence_level
        self.margin_of_error = margin_of_error
    
    def calculate_sample_size(self, population_size: int) -> int:
        """Calculate required sample size for assessment"""
        
        # Simple formula for sample size calculation
        z_score = 1.96  # 95% confidence
        p = 0.5  # Maximum variance assumption
        
        n = (z_score**2 * p * (1-p)) / (self.margin_of_error**2)
        
        # Adjust for finite population
        if population_size < float('inf'):
            n = n / (1 + (n-1)/population_size)
        
        return max(int(n), 100)  # Minimum 100 samples
    
    def assess_kde_sample(self, sample_data: List[Any], kde_config: Dict) -> Dict[str, float]:
        """Assess KDE quality from sample data"""
        
        assessment_results = {
            'sample_size': len(sample_data),
            'null_rate': self._calculate_null_rate(sample_data),
            'format_validity': self._assess_format_validity(sample_data, kde_config),
            'range_validity': self._assess_range_validity(sample_data, kde_config),
            'uniqueness': self._assess_uniqueness(sample_data),
            'kde_score': 0.0,
            'confidence_interval': (0.0, 0.0)
        }
        
        # Calculate overall KDE score
        scores = [
            assessment_results['null_rate'],
            assessment_results['format_validity'],
            assessment_results['range_validity'],
            assessment_results['uniqueness']
        ]
        
        valid_scores = [s for s in scores if s is not None]
        if valid_scores:
            assessment_results['kde_score'] = sum(valid_scores) / len(valid_scores)
            
            # Calculate confidence interval
            std_error = (assessment_results['kde_score'] * (1 - assessment_results['kde_score']) / len(sample_data)) ** 0.5
            margin = 1.96 * std_error
            assessment_results['confidence_interval'] = (
                max(0, assessment_results['kde_score'] - margin),
                min(1, assessment_results['kde_score'] + margin)
            )
        
        return assessment_results


# Example execution script
def run_current_state_assessment():
    """Run assessment on client's current systems"""
    
    print("🔍 Current State KDE Assessment")
    print("=" * 40)
    print()
    
    # Example: Multiple data sources
    data_sources = {
        'trading_database': {
            'type': 'sql',
            'connection': 'postgresql://user:pass@host:5432/trading',
            'tables': ['trades', 'orders', 'positions']
        },
        'market_feed': {
            'type': 'csv',
            'files': ['market_data_2024.csv', 'reference_data.csv']
        },
        'surveillance_alerts': {
            'type': 'api',
            'endpoint': 'https://surveillance.bank.com/api/alerts',
            'sample_size': 1000
        }
    }
    
    # Run assessment for each source
    overall_scores = {}
    
    for source_name, config in data_sources.items():
        print(f"Assessing {source_name}...")
        
        if config['type'] == 'sql':
            # Use SQL approach
            scores = assess_sql_source(config)
        elif config['type'] == 'csv':
            # Use CSV approach  
            scores = assess_csv_files(config['files'])
        elif config['type'] == 'api':
            # Use sampling approach
            scores = assess_api_source(config)
        
        overall_scores[source_name] = scores
        print(f"  Overall Score: {scores.get('overall', 0):.3f}")
    
    # Generate consolidated report
    generate_current_state_report(overall_scores)

if __name__ == "__main__":
    run_current_state_assessment()
```

---

## 🎯 **Implementation Roadmap**

### **Week 1: Data Discovery**
```
• Inventory existing data sources
• Map current KDEs to business fields  
• Identify data access methods
• Select appropriate assessment approach
```

### **Week 2: Assessment Setup**
```
• Deploy KDE scoring scripts
• Configure KDE definitions
• Set up sampling methodology
• Test data access and extraction
```

### **Week 3: Current State Scoring**
```
• Run KDE assessments
• Collect scoring results
• Identify critical quality issues
• Generate baseline report
```

### **Week 4: Action Planning**
```
• Prioritize KDE improvements
• Estimate implementation effort
• Build business case for DQSI
• Plan migration strategy
```

This gives you **immediate KDE-level scoring** on their existing systems, providing the baseline needed to justify and plan the full DQSI implementation!