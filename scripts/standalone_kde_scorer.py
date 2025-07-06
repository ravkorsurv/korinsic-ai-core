#!/usr/bin/env python3
"""
Standalone KDE Scorer for Current State Assessment

This tool runs KDE-level scoring on existing client data to:
1. Baseline current data quality
2. Identify critical KDEs with issues  
3. Generate actionable improvement recommendations
4. Build business case for full DQSI implementation
"""

import pandas as pd
import numpy as np
import re
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
import os


class StandaloneKDEScorer:
    """Standalone KDE scorer for existing data assessment"""
    
    def __init__(self):
        self.kde_configs = {}
        self.scoring_results = {}
        self.assessment_timestamp = datetime.now()
    
    def load_config_from_dict(self, config: Dict[str, Any]):
        """Load KDE configuration from dictionary"""
        self.kde_configs = config
    
    def score_dataframe(self, df: pd.DataFrame, data_flow_name: str = "default") -> Dict[str, Any]:
        """Score KDEs from a pandas DataFrame"""
        
        print(f"📊 Scoring data flow: {data_flow_name}")
        print(f"   Records: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        print()
        
        kde_scores = {}
        kde_details = {}
        
        for kde_name, kde_config in self.kde_configs.items():
            if kde_name not in df.columns:
                print(f"   ⚠️  KDE '{kde_name}' not found in data - skipping")
                continue
            
            # Score this KDE
            score, details = self._score_kde_column(df[kde_name], kde_config, kde_name)
            kde_scores[kde_name] = score
            kde_details[kde_name] = details
            
            # Status indicator
            status = "🟢" if score >= 0.8 else "🟡" if score >= 0.7 else "🔴" if score >= 0.5 else "⚫"
            print(f"   {status} {kde_name}: {score:.3f}")
        
        # Calculate overall DQSI score
        overall_score = self._calculate_overall_dqsi_score(kde_scores)
        
        result = {
            'data_flow': data_flow_name,
            'assessment_timestamp': self.assessment_timestamp.isoformat(),
            'record_count': len(df),
            'kde_scores': kde_scores,
            'kde_details': kde_details,
            'overall_dqsi_score': overall_score,
            'critical_kdes': [k for k, v in kde_scores.items() if v < 0.5],
            'poor_kdes': [k for k, v in kde_scores.items() if 0.5 <= v < 0.7],
            'quality_status': self._determine_quality_status(overall_score)
        }
        
        print()
        print(f"📈 Overall DQSI Score: {overall_score:.3f} ({result['quality_status']})")
        print()
        
        return result
    
    def _score_kde_column(self, data: pd.Series, kde_config: Dict, kde_name: str) -> tuple:
        """Score individual KDE column with detailed breakdown"""
        
        scores = {}
        details = {
            'total_records': len(data),
            'null_count': data.isnull().sum(),
            'unique_count': data.nunique(),
            'data_type': kde_config.get('data_type', 'string'),
            'validations_applied': []
        }
        
        # 1. Null Presence (always checked)
        scores['null_presence'] = self._score_null_presence(data)
        details['validations_applied'].append('null_presence')
        details['null_rate'] = data.isnull().sum() / len(data)
        
        # 2. Format Validation
        if 'format_pattern' in kde_config:
            scores['format'] = self._score_format(data, kde_config['format_pattern'])
            details['validations_applied'].append('format')
            details['format_violations'] = self._count_format_violations(data, kde_config['format_pattern'])
        
        # 3. Range Validation
        if 'valid_range' in kde_config:
            scores['range'] = self._score_range(data, kde_config['valid_range'])
            details['validations_applied'].append('range')
            details['range_violations'] = self._count_range_violations(data, kde_config['valid_range'])
        
        # 4. Data Type Specific Validations
        data_type = kde_config.get('data_type', 'string')
        
        if data_type == 'timestamp':
            scores['freshness'] = self._score_timestamp_freshness(data)
            details['validations_applied'].append('freshness')
            details['avg_age_hours'] = self._calculate_avg_age_hours(data)
            
        elif data_type == 'numeric':
            scores['precision'] = self._score_numeric_precision(data)
            details['validations_applied'].append('precision')
            details['decimal_places'] = self._analyze_decimal_places(data)
            
        elif data_type == 'categorical':
            if 'valid_values' in kde_config:
                scores['reference'] = self._score_categorical_reference(data, kde_config['valid_values'])
                details['validations_applied'].append('reference')
                details['invalid_categories'] = self._count_invalid_categories(data, kde_config['valid_values'])
        
        # 5. Uniqueness (if required)
        if kde_config.get('unique_required', False):
            scores['uniqueness'] = self._score_uniqueness(data)
            details['validations_applied'].append('uniqueness')
            details['duplicate_count'] = len(data) - data.nunique()
        
        # 6. Business Rule Validations
        if 'business_rules' in kde_config:
            for rule_name, rule_config in kde_config['business_rules'].items():
                rule_score = self._apply_business_rule(data, rule_config)
                scores[f'business_rule_{rule_name}'] = rule_score
                details['validations_applied'].append(f'business_rule_{rule_name}')
        
        # Calculate weighted KDE score
        if scores:
            # Weight sub-dimensions by importance
            weights = {
                'null_presence': 0.3,
                'format': 0.25,
                'range': 0.2,
                'freshness': 0.15,
                'precision': 0.15,
                'reference': 0.2,
                'uniqueness': 0.15
            }
            
            weighted_sum = 0
            total_weight = 0
            
            for subdim, score in scores.items():
                weight = weights.get(subdim, 0.1)  # Default weight for business rules
                weighted_sum += score * weight
                total_weight += weight
            
            final_score = weighted_sum / total_weight if total_weight > 0 else 0.5
        else:
            final_score = 0.5
        
        # Apply business adjustments
        final_score = self._apply_business_adjustments(final_score, kde_config, details)
        
        details['final_score'] = final_score
        details['sub_dimension_scores'] = scores
        
        return final_score, details
    
    def _score_null_presence(self, data: pd.Series) -> float:
        """Score null presence"""
        null_rate = data.isnull().sum() / len(data)
        
        if null_rate == 0.0:
            return 1.0
        elif null_rate <= 0.02:
            return 0.95
        elif null_rate <= 0.05:
            return 0.9
        elif null_rate <= 0.10:
            return 0.8
        elif null_rate <= 0.20:
            return 0.6
        elif null_rate <= 0.50:
            return 0.3
        else:
            return 0.1
    
    def _score_format(self, data: pd.Series, pattern: str) -> float:
        """Score format validation"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0.0
        
        try:
            valid_count = non_null_data.astype(str).str.match(pattern, na=False).sum()
            valid_rate = valid_count / len(non_null_data)
            
            if valid_rate >= 0.98:
                return 1.0
            elif valid_rate >= 0.95:
                return 0.9
            elif valid_rate >= 0.85:
                return 0.8
            elif valid_rate >= 0.75:
                return 0.7
            elif valid_rate >= 0.60:
                return 0.5
            elif valid_rate >= 0.40:
                return 0.3
            else:
                return 0.1
        except Exception:
            return 0.5  # Default if pattern matching fails
    
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
                # Convert to numeric if possible
                if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                    value = float(value)
                
                in_range = True
                if min_val is not None and value < min_val:
                    in_range = False
                if max_val is not None and value > max_val:
                    in_range = False
                
                if in_range:
                    in_range_count += 1
                    
            except (ValueError, TypeError):
                continue
        
        range_rate = in_range_count / len(non_null_data)
        
        if range_rate >= 0.98:
            return 1.0
        elif range_rate >= 0.95:
            return 0.9
        elif range_rate >= 0.85:
            return 0.8
        elif range_rate >= 0.75:
            return 0.7
        elif range_rate >= 0.60:
            return 0.5
        elif range_rate >= 0.40:
            return 0.3
        else:
            return 0.1
    
    def _score_timestamp_freshness(self, data: pd.Series) -> float:
        """Score timestamp freshness"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0.0
        
        current_time = datetime.now()
        fresh_score = 0
        
        for timestamp_str in non_null_data:
            try:
                # Try multiple timestamp formats
                ts = None
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d', 
                           '%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S']:
                    try:
                        ts = datetime.strptime(str(timestamp_str).strip(), fmt)
                        break
                    except ValueError:
                        continue
                
                if ts is None:
                    # Try pandas parsing as fallback
                    ts = pd.to_datetime(timestamp_str, errors='coerce')
                    if pd.isna(ts):
                        continue
                
                age = current_time - ts
                
                if age <= timedelta(minutes=30):
                    fresh_score += 1.0  # Very fresh
                elif age <= timedelta(hours=4):
                    fresh_score += 0.9  # Fresh
                elif age <= timedelta(hours=24):
                    fresh_score += 0.7  # Acceptable
                elif age <= timedelta(days=7):
                    fresh_score += 0.4  # Stale
                elif age <= timedelta(days=30):
                    fresh_score += 0.2  # Very stale
                else:
                    fresh_score += 0.1  # Ancient
                    
            except Exception:
                continue
        
        if len(non_null_data) > 0:
            freshness_rate = fresh_score / len(non_null_data)
            return max(0.0, min(1.0, freshness_rate))
        else:
            return 0.0
    
    def _score_uniqueness(self, data: pd.Series) -> float:
        """Score uniqueness"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0.0
        
        unique_rate = len(non_null_data.unique()) / len(non_null_data)
        
        if unique_rate >= 0.99:
            return 1.0
        elif unique_rate >= 0.98:
            return 0.9
        elif unique_rate >= 0.95:
            return 0.8
        elif unique_rate >= 0.90:
            return 0.7
        elif unique_rate >= 0.80:
            return 0.5
        elif unique_rate >= 0.60:
            return 0.3
        else:
            return 0.1
    
    def _calculate_overall_dqsi_score(self, kde_scores: Dict[str, float]) -> float:
        """Calculate overall DQSI score using risk weights"""
        if not kde_scores:
            return 0.0
        
        weighted_sum = 0
        total_weights = 0
        
        for kde_name, score in kde_scores.items():
            # Get weight from config, default to medium (2)
            kde_config = self.kde_configs.get(kde_name, {})
            risk = kde_config.get('risk', 'medium')
            
            # Convert risk to weight
            weight_map = {'high': 3, 'medium': 2, 'low': 1}
            weight = weight_map.get(risk, 2)
            
            weighted_sum += score * weight
            total_weights += weight
        
        return weighted_sum / total_weights if total_weights > 0 else 0.0
    
    def _determine_quality_status(self, score: float) -> str:
        """Determine quality status from score"""
        if score >= 0.8:
            return "GOOD"
        elif score >= 0.7:
            return "ACCEPTABLE"
        elif score >= 0.5:
            return "POOR"
        else:
            return "CRITICAL"
    
    def _apply_business_adjustments(self, score: float, kde_config: Dict, details: Dict) -> float:
        """Apply business-specific score adjustments"""
        adjusted_score = score
        
        # Penalty for high-risk KDEs with issues
        if kde_config.get('risk') == 'high' and score < 0.8:
            adjusted_score *= 0.9  # 10% penalty for high-risk issues
        
        # Penalty for excessive nulls in critical fields
        if details.get('null_rate', 0) > 0.10 and kde_config.get('critical', False):
            adjusted_score *= 0.85  # 15% penalty for critical field nulls
        
        return max(0.0, min(1.0, adjusted_score))
    
    def _count_format_violations(self, data: pd.Series, pattern: str) -> int:
        """Count format violations"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0
        
        try:
            valid_count = non_null_data.astype(str).str.match(pattern, na=False).sum()
            return len(non_null_data) - valid_count
        except Exception:
            return len(non_null_data)  # Assume all invalid if pattern fails

    def _count_range_violations(self, data: pd.Series, valid_range: Dict) -> int:
        """Count range violations"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0
        
        min_val = valid_range.get('min')
        max_val = valid_range.get('max')
        
        violations = 0
        for value in non_null_data:
            try:
                if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                    value = float(value)
                
                if min_val is not None and value < min_val:
                    violations += 1
                elif max_val is not None and value > max_val:
                    violations += 1
                    
            except (ValueError, TypeError):
                violations += 1
        
        return violations
    
    def _calculate_avg_age_hours(self, data: pd.Series) -> float:
        """Calculate average age of timestamps in hours"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0.0
        
        current_time = datetime.now()
        total_age_hours = 0
        valid_timestamps = 0
        
        for timestamp_str in non_null_data:
            try:
                ts = pd.to_datetime(timestamp_str, errors='coerce')
                if pd.notna(ts):
                    age = current_time - ts
                    total_age_hours += age.total_seconds() / 3600
                    valid_timestamps += 1
            except:
                continue
        
        return total_age_hours / valid_timestamps if valid_timestamps > 0 else 0.0
    
    def _score_numeric_precision(self, data: pd.Series) -> float:
        """Score numeric precision"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0.0
        
        precision_count = 0
        for value in non_null_data:
            try:
                # Check if it's a valid number
                float_val = float(value)
                # Check for reasonable precision (not too many decimal places)
                str_val = str(value)
                if '.' in str_val:
                    decimal_places = len(str_val.split('.')[1])
                    if decimal_places <= 6:  # Reasonable precision
                        precision_count += 1
                    else:
                        precision_count += 0.5  # Excessive precision
                else:
                    precision_count += 1  # Integer is fine
            except (ValueError, TypeError):
                continue
        
        precision_rate = precision_count / len(non_null_data)
        
        if precision_rate >= 0.95:
            return 1.0
        elif precision_rate >= 0.85:
            return 0.9
        elif precision_rate >= 0.75:
            return 0.8
        elif precision_rate >= 0.60:
            return 0.6
        else:
            return 0.3
    
    def _analyze_decimal_places(self, data: pd.Series) -> Dict[str, Any]:
        """Analyze decimal places in numeric data"""
        non_null_data = data.dropna()
        decimal_places = []
        
        for value in non_null_data:
            try:
                str_val = str(value)
                if '.' in str_val:
                    places = len(str_val.split('.')[1])
                    decimal_places.append(places)
                else:
                    decimal_places.append(0)
            except:
                continue
        
        if decimal_places:
            return {
                'avg_decimal_places': sum(decimal_places) / len(decimal_places),
                'max_decimal_places': max(decimal_places),
                'min_decimal_places': min(decimal_places)
            }
        else:
            return {'avg_decimal_places': 0, 'max_decimal_places': 0, 'min_decimal_places': 0}
    
    def _score_categorical_reference(self, data: pd.Series, valid_values: List[str]) -> float:
        """Score categorical reference validation"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0.0
        
        valid_set = set(valid_values)
        valid_count = sum(1 for value in non_null_data if str(value) in valid_set)
        valid_rate = valid_count / len(non_null_data)
        
        if valid_rate >= 0.98:
            return 1.0
        elif valid_rate >= 0.95:
            return 0.9
        elif valid_rate >= 0.85:
            return 0.8
        elif valid_rate >= 0.75:
            return 0.7
        elif valid_rate >= 0.60:
            return 0.5
        else:
            return 0.3
    
    def _count_invalid_categories(self, data: pd.Series, valid_values: List[str]) -> int:
        """Count invalid categories"""
        non_null_data = data.dropna()
        if len(non_null_data) == 0:
            return 0
        
        valid_set = set(valid_values)
        invalid_count = sum(1 for value in non_null_data if str(value) not in valid_set)
        return invalid_count
    
    def _apply_business_rule(self, data: pd.Series, rule_config: Dict) -> float:
        """Apply business rule validation"""
        # This is a placeholder for business rule validation
        # In practice, this would implement specific business logic
        
        rule_type = rule_config.get('type', 'custom')
        
        if rule_type == 'not_negative':
            non_null_data = data.dropna()
            if len(non_null_data) == 0:
                return 0.0
            
            valid_count = 0
            for value in non_null_data:
                try:
                    if float(value) >= 0:
                        valid_count += 1
                except (ValueError, TypeError):
                    continue
            
            return valid_count / len(non_null_data) if len(non_null_data) > 0 else 0.0
        
        # Default business rule score
        return 0.8
    
    def generate_assessment_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive assessment report"""
        
        report = []
        report.append("=" * 70)
        report.append("CURRENT STATE KDE ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Summary
        report.append(f"Assessment Date: {results['assessment_timestamp']}")
        report.append(f"Data Flow: {results['data_flow']}")
        report.append(f"Records Analyzed: {results['record_count']:,}")
        report.append("")
        
        # Overall score
        score = results['overall_dqsi_score']
        status = results['quality_status']
        
        report.append(f"OVERALL DQSI SCORE: {score:.3f} ({score*100:.1f}%)")
        report.append(f"QUALITY STATUS: {status}")
        
        if status == "CRITICAL":
            report.append("🚨 IMMEDIATE ACTION REQUIRED")
        elif status == "POOR":
            report.append("⚠️  SIGNIFICANT IMPROVEMENTS NEEDED")
        elif status == "ACCEPTABLE":
            report.append("🟡 MINOR IMPROVEMENTS RECOMMENDED")
        else:
            report.append("✅ GOOD QUALITY - MAINTAIN CURRENT STANDARDS")
        
        report.append("")
        
        # Individual KDE scores
        report.append("INDIVIDUAL KDE SCORES:")
        report.append("-" * 30)
        
        for kde_name, kde_score in sorted(results['kde_scores'].items(), key=lambda x: x[1]):
            config = self.kde_configs.get(kde_name, {})
            risk = config.get('risk', 'medium')
            
            status_icon = "🟢" if kde_score >= 0.8 else "🟡" if kde_score >= 0.7 else "🔴" if kde_score >= 0.5 else "⚫"
            
            report.append(f"  {status_icon} {kde_name}: {kde_score:.3f} ({risk} risk)")
            
            # Add details if available
            if kde_name in results.get('kde_details', {}):
                details = results['kde_details'][kde_name]
                if details.get('null_rate', 0) > 0.05:
                    report.append(f"     ⚠️  {details['null_rate']:.1%} null values")
                if details.get('format_violations', 0) > 0:
                    report.append(f"     ⚠️  {details['format_violations']} format violations")
        
        report.append("")
        
        # Critical issues
        if results['critical_kdes']:
            report.append("🚨 CRITICAL ISSUES (Score < 0.5):")
            report.append("-" * 35)
            for kde in results['critical_kdes']:
                report.append(f"  • {kde}")
            report.append("")
        
        # Priority improvements
        if results['poor_kdes']:
            report.append("⚠️  PRIORITY IMPROVEMENTS (Score 0.5-0.7):")
            report.append("-" * 40)
            for kde in results['poor_kdes']:
                report.append(f"  • {kde}")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS:")
        report.append("-" * 15)
        
        if results['critical_kdes']:
            report.append("1. IMMEDIATE: Address critical KDE issues")
            report.append("   - Implement data validation rules")
            report.append("   - Fix data pipeline issues")
            report.append("   - Add data quality monitoring")
            report.append("")
        
        if results['poor_kdes']:
            report.append("2. SHORT-TERM: Improve poor-scoring KDEs")
            report.append("   - Enhance data cleansing processes")
            report.append("   - Implement business rule validation")
            report.append("   - Add automated quality checks")
            report.append("")
        
        if score < 0.5:
            report.append("3. STRATEGIC: Implement comprehensive DQ program")
            report.append("   - Deploy full DQSI system")
            report.append("   - Establish data governance")
            report.append("   - Train staff on data quality")
        elif score < 0.7:
            report.append("3. STRATEGIC: Enhance data quality processes")
            report.append("   - Implement role-aware DQSI")
            report.append("   - Add advanced validation rules")
            report.append("   - Establish quality monitoring")
        else:
            report.append("3. STRATEGIC: Maintain and optimize")
            report.append("   - Continue monitoring")
            report.append("   - Fine-tune thresholds")
            report.append("   - Expand to other data flows")
        
        report.append("")
        
        # Next steps
        report.append("NEXT STEPS:")
        report.append("-" * 11)
        report.append("1. Address critical issues identified above")
        report.append("2. Implement systematic data quality improvements")
        report.append("3. Consider full DQSI implementation for ongoing monitoring")
        report.append("4. Establish regular data quality assessments")
        
        return "\n".join(report)


def create_sample_kde_config() -> Dict[str, Any]:
    """Create sample KDE configuration for trading data"""
    return {
        'trader_id': {
            'data_type': 'string',
            'format_pattern': r'^[A-Z]{3}[0-9]{4}$',
            'risk': 'high',
            'critical': True,
            'description': 'Unique trader identifier'
        },
        'trade_time': {
            'data_type': 'timestamp',
            'risk': 'high',
            'critical': True,
            'description': 'Trade execution timestamp'
        },
        'notional': {
            'data_type': 'numeric',
            'valid_range': {'min': 0, 'max': 1000000000},
            'risk': 'high',
            'critical': True,
            'description': 'Trade notional amount'
        },
        'quantity': {
            'data_type': 'numeric',
            'valid_range': {'min': 1, 'max': 10000000},
            'risk': 'medium',
            'description': 'Trade quantity'
        },
        'price': {
            'data_type': 'numeric',
            'valid_range': {'min': 0, 'max': 100000},
            'risk': 'medium',
            'description': 'Trade price'
        },
        'instrument': {
            'data_type': 'categorical',
            'format_pattern': r'^[A-Z]{3,5}$',
            'risk': 'low',
            'description': 'Financial instrument code'
        },
        'desk_id': {
            'data_type': 'categorical',
            'format_pattern': r'^[A-Z]{2,4}$',
            'risk': 'low',
            'description': 'Trading desk identifier'
        }
    }


def main():
    """Main function for standalone execution"""
    parser = argparse.ArgumentParser(description='Standalone KDE Quality Scorer')
    parser.add_argument('file_path', help='Path to CSV file to analyze')
    parser.add_argument('--config', help='Path to KDE configuration YAML file')
    parser.add_argument('--output', help='Output file for results (JSON)')
    parser.add_argument('--flow-name', default='trading_data', help='Name of data flow')
    
    args = parser.parse_args()
    
    # Initialize scorer
    scorer = StandaloneKDEScorer()
    
    # Load configuration
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        scorer.load_config_from_dict(config)
    else:
        print("📋 Using sample KDE configuration for trading data")
        scorer.load_config_from_dict(create_sample_kde_config())
    
    # Load and score data
    print(f"📂 Loading data from: {args.file_path}")
    
    try:
        df = pd.read_csv(args.file_path)
        print(f"✅ Loaded {len(df):,} records with {len(df.columns)} columns")
        print()
        
        # Score the data
        results = scorer.score_dataframe(df, args.flow_name)
        
        # Generate report
        report = scorer.generate_assessment_report(results)
        print(report)
        
        # Save results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())