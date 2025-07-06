#!/usr/bin/env python3
"""
Simple KDE Scoring Demo (No External Dependencies)

This demonstrates KDE-level scoring on existing data without requiring
pandas or other external libraries - perfect for quick client assessments.
"""

import csv
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any


class SimpleKDEScorer:
    """Simple KDE scorer using only standard Python libraries"""
    
    def __init__(self):
        self.kde_configs = {
            'trader_id': {
                'data_type': 'string',
                'format_pattern': r'^TR[0-9]{4}$',
                'risk': 'high',
                'description': 'Trader identifier'
            },
            'trade_time': {
                'data_type': 'timestamp',
                'risk': 'high',
                'description': 'Trade timestamp'
            },
            'notional': {
                'data_type': 'numeric',
                'valid_range': {'min': 0, 'max': 1000000000},
                'risk': 'high',
                'description': 'Trade amount'
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
                'description': 'Instrument code'
            },
            'desk_id': {
                'data_type': 'categorical',
                'format_pattern': r'^[A-Z]{2,4}$',
                'risk': 'low',
                'description': 'Trading desk'
            }
        }
    
    def score_csv_file(self, file_path: str) -> Dict[str, Any]:
        """Score KDEs from a CSV file"""
        
        print(f"📂 Loading data from: {file_path}")
        
        # Read CSV data
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        print(f"✅ Loaded {len(data)} records")
        print()
        
        # Score each KDE
        kde_scores = {}
        kde_details = {}
        
        for kde_name, kde_config in self.kde_configs.items():
            if kde_name not in data[0]:
                print(f"   ⚠️  KDE '{kde_name}' not found in data - skipping")
                continue
            
            # Extract column data
            column_data = [row.get(kde_name, '') for row in data]
            
            # Score this KDE
            score, details = self._score_kde_column(column_data, kde_config)
            kde_scores[kde_name] = score
            kde_details[kde_name] = details
            
            # Status indicator
            status = "🟢" if score >= 0.8 else "🟡" if score >= 0.7 else "🔴" if score >= 0.5 else "⚫"
            print(f"   {status} {kde_name}: {score:.3f}")
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(kde_scores)
        
        result = {
            'file_path': file_path,
            'assessment_timestamp': datetime.now().isoformat(),
            'record_count': len(data),
            'kde_scores': kde_scores,
            'kde_details': kde_details,
            'overall_dqsi_score': overall_score,
            'critical_kdes': [k for k, v in kde_scores.items() if v < 0.5],
            'poor_kdes': [k for k, v in kde_scores.items() if 0.5 <= v < 0.7],
            'quality_status': self._determine_status(overall_score)
        }
        
        print()
        print(f"📈 Overall DQSI Score: {overall_score:.3f} ({result['quality_status']})")
        
        return result
    
    def _score_kde_column(self, data: List[str], kde_config: Dict) -> tuple:
        """Score individual KDE column"""
        
        total_records = len(data)
        non_empty = [x for x in data if x and str(x).strip()]
        null_count = total_records - len(non_empty)
        
        scores = {}
        details = {
            'total_records': total_records,
            'null_count': null_count,
            'null_rate': null_count / total_records if total_records > 0 else 0,
            'unique_count': len(set(non_empty)),
            'validations': []
        }
        
        # 1. Null presence
        scores['null_presence'] = self._score_null_presence(data)
        details['validations'].append('null_presence')
        
        # 2. Format validation
        if 'format_pattern' in kde_config and non_empty:
            scores['format'] = self._score_format(non_empty, kde_config['format_pattern'])
            details['validations'].append('format')
            details['format_violations'] = self._count_format_violations(non_empty, kde_config['format_pattern'])
        
        # 3. Range validation
        if 'valid_range' in kde_config and non_empty:
            scores['range'] = self._score_range(non_empty, kde_config['valid_range'])
            details['validations'].append('range')
        
        # 4. Type-specific validation
        data_type = kde_config.get('data_type', 'string')
        if data_type == 'timestamp' and non_empty:
            scores['freshness'] = self._score_timestamp_freshness(non_empty)
            details['validations'].append('freshness')
        
        # Calculate weighted score
        if scores:
            weights = {'null_presence': 0.4, 'format': 0.3, 'range': 0.2, 'freshness': 0.1}
            weighted_sum = sum(scores[k] * weights.get(k, 0.1) for k in scores)
            total_weight = sum(weights.get(k, 0.1) for k in scores)
            final_score = weighted_sum / total_weight
        else:
            final_score = 0.5
        
        details['final_score'] = final_score
        details['sub_scores'] = scores
        
        return final_score, details
    
    def _score_null_presence(self, data: List[str]) -> float:
        """Score null/empty presence"""
        total = len(data)
        empty_count = sum(1 for x in data if not x or not str(x).strip())
        null_rate = empty_count / total if total > 0 else 1.0
        
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
    
    def _score_format(self, data: List[str], pattern: str) -> float:
        """Score format validation"""
        if not data:
            return 0.0
        
        valid_count = 0
        for value in data:
            if re.match(pattern, str(value)):
                valid_count += 1
        
        valid_rate = valid_count / len(data)
        
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
    
    def _score_range(self, data: List[str], valid_range: Dict) -> float:
        """Score range validation"""
        if not data:
            return 0.0
        
        min_val = valid_range.get('min')
        max_val = valid_range.get('max')
        in_range_count = 0
        
        for value in data:
            try:
                num_val = float(value)
                if (min_val is None or num_val >= min_val) and (max_val is None or num_val <= max_val):
                    in_range_count += 1
            except (ValueError, TypeError):
                continue
        
        range_rate = in_range_count / len(data)
        
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
    
    def _score_timestamp_freshness(self, data: List[str]) -> float:
        """Score timestamp freshness"""
        if not data:
            return 0.0
        
        current_time = datetime.now()
        fresh_count = 0
        
        for timestamp_str in data:
            try:
                # Try to parse timestamp
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d']:
                    try:
                        ts = datetime.strptime(timestamp_str, fmt)
                        age = current_time - ts
                        
                        if age <= timedelta(hours=1):
                            fresh_count += 1
                        elif age <= timedelta(hours=24):
                            fresh_count += 0.7
                        elif age <= timedelta(days=7):
                            fresh_count += 0.4
                        else:
                            fresh_count += 0.1
                        break
                    except ValueError:
                        continue
            except:
                continue
        
        freshness_rate = fresh_count / len(data) if data else 0
        
        if freshness_rate >= 0.9:
            return 1.0
        elif freshness_rate >= 0.7:
            return 0.8
        elif freshness_rate >= 0.5:
            return 0.6
        else:
            return 0.3
    
    def _count_format_violations(self, data: List[str], pattern: str) -> int:
        """Count format violations"""
        violations = 0
        for value in data:
            if not re.match(pattern, str(value)):
                violations += 1
        return violations
    
    def _calculate_overall_score(self, kde_scores: Dict[str, float]) -> float:
        """Calculate overall DQSI score"""
        if not kde_scores:
            return 0.0
        
        weighted_sum = 0
        total_weights = 0
        
        for kde_name, score in kde_scores.items():
            kde_config = self.kde_configs.get(kde_name, {})
            risk = kde_config.get('risk', 'medium')
            
            # Risk weights
            weight = {'high': 3, 'medium': 2, 'low': 1}.get(risk, 2)
            
            weighted_sum += score * weight
            total_weights += weight
        
        return weighted_sum / total_weights if total_weights > 0 else 0.0
    
    def _determine_status(self, score: float) -> str:
        """Determine quality status"""
        if score >= 0.8:
            return "GOOD"
        elif score >= 0.7:
            return "ACCEPTABLE"
        elif score >= 0.5:
            return "POOR"
        else:
            return "CRITICAL"
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate assessment report"""
        
        report = []
        report.append("=" * 60)
        report.append("SIMPLE KDE ASSESSMENT REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append(f"File: {results['file_path']}")
        report.append(f"Records: {results['record_count']:,}")
        report.append(f"Assessment: {results['assessment_timestamp']}")
        report.append("")
        
        # Overall score
        score = results['overall_dqsi_score']
        status = results['quality_status']
        
        report.append(f"OVERALL DQSI SCORE: {score:.3f} ({score*100:.1f}%)")
        report.append(f"STATUS: {status}")
        
        if status == "CRITICAL":
            report.append("🚨 IMMEDIATE ACTION REQUIRED")
        elif status == "POOR":
            report.append("⚠️  IMPROVEMENTS NEEDED")
        elif status == "ACCEPTABLE":
            report.append("🟡 MINOR IMPROVEMENTS")
        else:
            report.append("✅ GOOD QUALITY")
        
        report.append("")
        
        # Individual KDE scores
        report.append("KDE SCORES:")
        report.append("-" * 15)
        
        for kde_name, kde_score in sorted(results['kde_scores'].items(), key=lambda x: x[1]):
            risk = self.kde_configs.get(kde_name, {}).get('risk', 'medium')
            status_icon = "🟢" if kde_score >= 0.8 else "🟡" if kde_score >= 0.7 else "🔴" if kde_score >= 0.5 else "⚫"
            report.append(f"  {status_icon} {kde_name}: {kde_score:.3f} ({risk} risk)")
            
            # Show details
            if kde_name in results.get('kde_details', {}):
                details = results['kde_details'][kde_name]
                if details.get('null_rate', 0) > 0.05:
                    report.append(f"     • {details['null_rate']:.1%} missing values")
                if details.get('format_violations', 0) > 0:
                    report.append(f"     • {details['format_violations']} format errors")
        
        report.append("")
        
        # Issues
        if results['critical_kdes']:
            report.append("🚨 CRITICAL ISSUES:")
            for kde in results['critical_kdes']:
                report.append(f"  • {kde}")
            report.append("")
        
        if results['poor_kdes']:
            report.append("⚠️  PRIORITY FIXES:")
            for kde in results['poor_kdes']:
                report.append(f"  • {kde}")
            report.append("")
        
        # Recommendations
        report.append("NEXT STEPS:")
        report.append("-" * 11)
        
        if results['critical_kdes']:
            report.append("1. Fix critical KDE issues immediately")
            report.append("2. Implement data validation rules")
            report.append("3. Monitor data quality ongoing")
        elif results['poor_kdes']:
            report.append("1. Improve poor-scoring KDEs")
            report.append("2. Enhance data cleansing")
            report.append("3. Add quality monitoring")
        else:
            report.append("1. Maintain current quality standards")
            report.append("2. Consider expanding to other data flows")
            report.append("3. Implement full DQSI system")
        
        return "\n".join(report)


def main():
    """Main demonstration"""
    
    scorer = SimpleKDEScorer()
    
    # Check if sample file exists
    import os
    if not os.path.exists('sample_trading_data.csv'):
        print("❌ sample_trading_data.csv not found")
        print("   Run the data generation script first")
        return
    
    print("🔍 Simple KDE Quality Assessment")
    print("=" * 40)
    print()
    
    # Score the data
    results = scorer.score_csv_file('sample_trading_data.csv')
    
    print()
    print(scorer.generate_report(results))
    
    # Save results
    with open('assessment_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print()
    print("💾 Results saved to: assessment_results.json")


if __name__ == "__main__":
    main()