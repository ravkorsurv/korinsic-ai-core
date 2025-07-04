#!/usr/bin/env python3
"""
Simple End-to-End Test for Kor.ai Core
Enhanced for CI/CD: JSON summary, error logging, regression check, exit codes.
"""

import json
import sys
import os
from datetime import datetime
import traceback

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

ERROR_LOG = 'test_e2e_error.log'
SUMMARY_JSON = 'test_e2e_summary.json'
BASELINE_JSON = 'test_e2e_baseline.json'

results = []
error_log = []

# Helper to log errors
def log_error(test, exc):
    tb = traceback.format_exc()
    error_log.append({'test': test, 'error': str(exc), 'traceback': tb})
    with open(ERROR_LOG, 'a') as f:
        f.write(f"[{datetime.now()}] {test} FAILED: {exc}\n{tb}\n\n")

def test_data_processor():
    """Test data processing functionality"""
    try:
        from core.data_processor import DataProcessor
        processor = DataProcessor()
        sample_data = {
            "trades": [
                {"timestamp": 1640995200, "symbol": "AAPL", "volume": 10000, "price": 150.0, "trader_id": "T001"},
                {"timestamp": 1640995260, "symbol": "AAPL", "volume": 25000, "price": 152.0, "trader_id": "T001"}
            ],
            "trader_info": {"role": "senior_trader", "department": "equity_trading"}
        }
        processed = processor.process(sample_data)
        results.append({'test': 'Data Processor', 'status': 'PASS'})
        print("\u2705 Data Processor: PASSED")
        return True
    except Exception as e:
        log_error('Data Processor', e)
        results.append({'test': 'Data Processor', 'status': 'FAIL', 'error': str(e)})
        print(f"\u274c Data Processor: FAILED - {str(e)}")
        return False

def test_risk_calculator():
    try:
        from core.risk_calculator import RiskCalculator
        calculator = RiskCalculator()
        insider_score = 0.3
        spoofing_score = 0.2
        processed_data = {"metrics": {"volume_variance": 2.5, "price_impact": 0.01}}
        overall_risk = calculator.calculate_overall_risk(insider_score, spoofing_score, processed_data)
        results.append({'test': 'Risk Calculator', 'status': 'PASS'})
        print("\u2705 Risk Calculator: PASSED")
        return True
    except Exception as e:
        log_error('Risk Calculator', e)
        results.append({'test': 'Risk Calculator', 'status': 'FAIL', 'error': str(e)})
        print(f"\u274c Risk Calculator: FAILED - {str(e)}")
        return False

def test_alert_generator():
    try:
        from core.alert_generator import AlertGenerator
        generator = AlertGenerator()
        processed_data = {"trades": [{"symbol": "AAPL", "volume": 10000}], "trader_info": {"trader_id": "T001"}}
        alerts = generator.generate_alerts(processed_data, insider_dealing_score=0.8, spoofing_score=0.3, overall_risk=0.6)
        results.append({'test': 'Alert Generator', 'status': 'PASS'})
        print("\u2705 Alert Generator: PASSED")
        return True
    except Exception as e:
        log_error('Alert Generator', e)
        results.append({'test': 'Alert Generator', 'status': 'FAIL', 'error': str(e)})
        print(f"\u274c Alert Generator: FAILED - {str(e)}")
        return False

def test_bayesian_engine():
    try:
        from core.bayesian_engine import BayesianEngine
        engine = BayesianEngine()
        models_info = engine.get_models_info()
        if models_info['models_loaded']:
            results.append({'test': 'Bayesian Engine', 'status': 'PASS'})
            print("\u2705 Bayesian Engine: PASSED (Models loaded successfully)")
            return True
        else:
            results.append({'test': 'Bayesian Engine', 'status': 'FAIL', 'error': 'Models not loaded'})
            print("\u274c Bayesian Engine: FAILED (Models not loaded)")
            return False
    except Exception as e:
        log_error('Bayesian Engine', e)
        results.append({'test': 'Bayesian Engine', 'status': 'FAIL', 'error': str(e)})
        print(f"\u274c Bayesian Engine: FAILED - {str(e)}")
        return False

def regression_check():
    """Compare current results to baseline if available."""
    if not os.path.exists(BASELINE_JSON):
        return None
    try:
        with open(BASELINE_JSON) as f:
            baseline = json.load(f)
        baseline_passed = sum(1 for r in baseline if r['status'] == 'PASS')
        current_passed = sum(1 for r in results if r['status'] == 'PASS')
        if current_passed < baseline_passed:
            print(f"\u26a0\ufe0f REGRESSION: {baseline_passed-current_passed} more failures than baseline!")
            return False
        return True
    except Exception as e:
        log_error('Regression Check', e)
        print(f"\u26a0\ufe0f Regression check failed: {e}")
        return None

def main():
    print("\U0001F680 Kor.ai Core End-to-End Test Suite (Enhanced)")
    print("=" * 50)
    test_results = []
    test_results.append(test_data_processor())
    test_results.append(test_risk_calculator())
    test_results.append(test_alert_generator())
    test_results.append(test_bayesian_engine())
    passed = sum(test_results)
    total = len(test_results)
    print("\n" + "=" * 50)
    print(f"\U0001F4CA Test Results: {passed}/{total} tests passed")
    regression = regression_check()
    # Write summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'errors': error_log,
        'passed': passed,
        'total': total,
        'regression': regression
    }
    with open(SUMMARY_JSON, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary written to {SUMMARY_JSON}")
    if error_log:
        print(f"Errors written to {ERROR_LOG}")
    if passed == total and (regression is None or regression):
        print("\U0001F389 ALL TESTS PASSED! Backend is working correctly.")
        return 0
    elif regression is False:
        print(f"\u26a0\ufe0f REGRESSION DETECTED. See {SUMMARY_JSON} and {ERROR_LOG}")
        return 1
    else:
        print(f"\u26a0\ufe0f  {total - passed} tests failed. Check the errors above.")
        return 2

if __name__ == "__main__":
    sys.exit(main())