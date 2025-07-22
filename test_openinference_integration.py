#!/usr/bin/env python3
"""
Complete OpenInference Integration Test Suite

This script runs all OpenInference-related tests and provides a comprehensive
report on the AI observability integration status.
"""

import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

def run_command(cmd, cwd=None):
    """Run a command and return success, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd.split() if isinstance(cmd, str) else cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_dependencies():
    """Check if OpenInference dependencies are installed"""
    print("🔍 Checking OpenInference dependencies...")
    
    dependencies = [
        'openinference-instrumentation',
        'openinference-semantic-conventions',
        'opentelemetry-api',
        'opentelemetry-sdk'
    ]
    
    missing_deps = []
    for dep in dependencies:
        success, _, _ = run_command(f"python -c 'import {dep.replace('-', '_')}'")
        if not success:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("   Run: ./setup_openinference.sh to install")
        return False
    else:
        print("✅ All OpenInference dependencies are installed")
        return True

def test_ai_observability_module():
    """Test the AI observability module"""
    print("\n🧪 Testing AI observability module...")
    
    success, stdout, stderr = run_command("python -m pytest tests/unit/test_ai_observability.py -v")
    
    if success:
        print("✅ AI observability unit tests passed")
        return True
    else:
        print("❌ AI observability unit tests failed")
        print(f"Error: {stderr}")
        return False

def test_e2e_integration():
    """Test E2E integration"""
    print("\n🔄 Testing E2E integration...")
    
    success, stdout, stderr = run_command("python tests/e2e/test_openinference_e2e.py")
    
    if success:
        print("✅ OpenInference E2E tests passed")
        return True
    else:
        print("❌ OpenInference E2E tests failed")
        print(f"Error: {stderr}")
        return False

def test_standalone_integration():
    """Test standalone integration"""
    print("\n🎯 Testing standalone integration...")
    
    success, stdout, stderr = run_command("python test_ai_observability.py")
    
    if success:
        print("✅ Standalone AI observability test passed")
        return True
    else:
        print("❌ Standalone AI observability test failed")
        print(f"Error: {stderr}")
        return False

def test_enhanced_e2e():
    """Test enhanced E2E framework"""
    print("\n🚀 Testing enhanced E2E framework...")
    
    success, stdout, stderr = run_command("python tests/e2e/test_e2e_enhanced.py")
    
    if success:
        print("✅ Enhanced E2E tests passed (with OpenInference integration)")
        return True
    else:
        print("❌ Enhanced E2E tests failed")
        print(f"Error: {stderr}")
        return False

def test_full_test_suite():
    """Test the full test suite with AI observability"""
    print("\n📋 Testing full test suite...")
    
    success, stdout, stderr = run_command("python scripts/development/run_tests.py --types ai_observability")
    
    if success:
        print("✅ Full test suite AI observability tests passed")
        return True
    else:
        print("❌ Full test suite AI observability tests failed")
        print(f"Error: {stderr}")
        return False

def generate_report(results):
    """Generate a comprehensive test report"""
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'openinference_integration_status': 'COMPLETE' if passed_tests == total_tests else 'PARTIAL',
        'total_test_categories': total_tests,
        'passed_test_categories': passed_tests,
        'failed_test_categories': total_tests - passed_tests,
        'success_rate': success_rate,
        'test_results': results,
        'recommendations': []
    }
    
    # Add recommendations based on results
    if not results.get('dependencies', False):
        report['recommendations'].append("Install OpenInference dependencies using ./setup_openinference.sh")
    
    if not results.get('unit_tests', False):
        report['recommendations'].append("Fix AI observability unit tests")
    
    if not results.get('e2e_tests', False):
        report['recommendations'].append("Fix OpenInference E2E integration tests")
    
    if passed_tests == total_tests:
        report['recommendations'].append("OpenInference integration is fully functional and ready for production")
    
    return report

def main():
    """Run all OpenInference integration tests"""
    print("🧠 Korinsic OpenInference Integration Test Suite")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run all tests
    results = {
        'dependencies': check_dependencies(),
        'unit_tests': False,
        'e2e_tests': False,
        'standalone_test': False,
        'enhanced_e2e': False,
        'full_suite': False
    }
    
    # Only run other tests if dependencies are available
    if results['dependencies']:
        results['unit_tests'] = test_ai_observability_module()
        results['e2e_tests'] = test_e2e_integration()
        results['standalone_test'] = test_standalone_integration()
        results['enhanced_e2e'] = test_enhanced_e2e()
        results['full_suite'] = test_full_test_suite()
    
    duration = time.time() - start_time
    
    # Generate report
    report = generate_report(results)
    
    print("\n" + "=" * 60)
    print("📊 OpenInference Integration Test Results")
    print(f"Total Test Categories: {report['total_test_categories']}")
    print(f"Passed: {report['passed_test_categories']}")
    print(f"Failed: {report['failed_test_categories']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print(f"Duration: {duration:.2f} seconds")
    
    print(f"\n🎯 Integration Status: {report['openinference_integration_status']}")
    
    if report['recommendations']:
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   • {rec}")
    
    # Save detailed report
    with open('openinference_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved: openinference_test_report.json")
    
    # Return appropriate exit code
    if report['openinference_integration_status'] == 'COMPLETE':
        print("\n🎉 OpenInference integration is fully functional!")
        return 0
    else:
        print("\n⚠️  OpenInference integration needs attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
