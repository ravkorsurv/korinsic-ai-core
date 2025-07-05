#!/usr/bin/env python3
"""
Comprehensive test runner for Kor.ai Surveillance Platform.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def run_command(command: List[str], cwd: Optional[Path] = None) -> int:
    """Run a command and return the exit code."""
    try:
        print(f"🔧 Running: {' '.join(command)}")
        result = subprocess.run(command, cwd=cwd or project_root, check=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return 1

def run_unit_tests(verbose: bool = False) -> int:
    """Run unit tests."""
    print("\n🧪 Running Unit Tests")
    print("=" * 50)
    
    command = ["python3", "-m", "pytest", "tests/unit/", "-v" if verbose else "-q"]
    command.extend(["-m", "unit", "--tb=short"])
    
    return run_command(command)

def run_integration_tests(verbose: bool = False) -> int:
    """Run integration tests."""
    print("\n🔗 Running Integration Tests")
    print("=" * 50)
    
    command = ["python3", "-m", "pytest", "tests/integration/", "-v" if verbose else "-q"]
    command.extend(["-m", "integration", "--tb=short"])
    
    return run_command(command)

def run_e2e_tests(verbose: bool = False) -> int:
    """Run end-to-end tests."""
    print("\n🌍 Running End-to-End Tests")
    print("=" * 50)
    
    command = ["python3", "-m", "pytest", "tests/e2e/", "-v" if verbose else "-q"]
    command.extend(["-m", "e2e", "--tb=short", "--disable-warnings"])
    
    return run_command(command)

def run_performance_tests(verbose: bool = False) -> int:
    """Run performance tests."""
    print("\n⚡ Running Performance Tests")
    print("=" * 50)
    
    command = ["python3", "-m", "pytest", "tests/performance/", "-v" if verbose else "-q"]
    command.extend(["-m", "performance", "--tb=short"])
    
    return run_command(command)

def run_coverage_tests() -> int:
    """Run tests with coverage."""
    print("\n📊 Running Tests with Coverage")
    print("=" * 50)
    
    command = [
        "python3", "-m", "pytest", 
        "--cov=src", 
        "--cov-report=html", 
        "--cov-report=term-missing",
        "tests/"
    ]
    
    return run_command(command)

def run_lint_checks() -> int:
    """Run linting checks."""
    print("\n🔍 Running Lint Checks")
    print("=" * 50)
    
    # Run flake8 if available
    flake8_result = run_command(["python3", "-m", "flake8", "src/", "tests/"])
    
    # Run black check if available
    black_result = run_command(["python3", "-m", "black", "--check", "src/", "tests/"])
    
    return max(flake8_result, black_result)

def check_dependencies() -> bool:
    """Check if required dependencies are available."""
    print("\n📦 Checking Dependencies")
    print("=" * 50)
    
    required_packages = ["pytest", "pytest-cov"]
    optional_packages = ["black", "flake8"]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            subprocess.run([sys.executable, "-m", package, "--version"], 
                         capture_output=True, check=True)
            print(f"✅ {package}: Available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_required.append(package)
            print(f"❌ {package}: Missing (required)")
    
    for package in optional_packages:
        try:
            subprocess.run([sys.executable, "-m", package, "--version"], 
                         capture_output=True, check=True)
            print(f"✅ {package}: Available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_optional.append(package)
            print(f"⚠️  {package}: Missing (optional)")
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print("Install with: pip install " + " ".join(missing_required))
        return False
    
    if missing_optional:
        print(f"\n⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("Install with: pip install " + " ".join(missing_optional))
    
    return True

def run_config_tests() -> int:
    """Run configuration system tests."""
    print("\n⚙️ Running Configuration Tests")
    print("=" * 50)
    
    config_test_script = project_root / "scripts" / "development" / "test_config_simple.py"
    
    if config_test_script.exists():
        return run_command(["python3", str(config_test_script)])
    else:
        print("❌ Configuration test script not found")
        return 1

def run_quick_tests() -> int:
    """Run a quick subset of tests for fast feedback."""
    print("\n⚡ Running Quick Test Suite")
    print("=" * 50)
    
    # Run only fast unit tests
    command = [
        "python3", "-m", "pytest", 
        "tests/unit/", 
        "-x",  # Stop on first failure
        "--tb=short",
        "-q"
    ]
    
    return run_command(command)

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Kor.ai Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run e2e tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--lint", action="store_true", help="Run lint checks only")
    parser.add_argument("--config", action="store_true", help="Run configuration tests only")
    parser.add_argument("--quick", action="store_true", help="Run quick test suite")
    parser.add_argument("--all", action="store_true", help="Run all test suites")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies only")
    
    args = parser.parse_args()
    
    print("🧪 Kor.ai Surveillance Platform - Test Runner")
    print("=" * 60)
    
    # Check dependencies first
    if args.check_deps:
        success = check_dependencies()
        return 0 if success else 1
    
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        return 1
    
    # Determine which tests to run
    test_results = []
    
    if args.quick:
        test_results.append(run_quick_tests())
    elif args.unit:
        test_results.append(run_unit_tests(args.verbose))
    elif args.integration:
        test_results.append(run_integration_tests(args.verbose))
    elif args.e2e:
        test_results.append(run_e2e_tests(args.verbose))
    elif args.performance:
        test_results.append(run_performance_tests(args.verbose))
    elif args.coverage:
        test_results.append(run_coverage_tests())
    elif args.lint:
        test_results.append(run_lint_checks())
    elif args.config:
        test_results.append(run_config_tests())
    elif args.all:
        # Run all test suites
        test_results.append(run_config_tests())
        test_results.append(run_unit_tests(args.verbose))
        test_results.append(run_integration_tests(args.verbose))
        test_results.append(run_e2e_tests(args.verbose))
        test_results.append(run_performance_tests(args.verbose))
        test_results.append(run_lint_checks())
    else:
        # Default: run unit and integration tests
        test_results.append(run_config_tests())
        test_results.append(run_unit_tests(args.verbose))
        test_results.append(run_integration_tests(args.verbose))
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result == 0)
    failed_tests = total_tests - passed_tests
    
    if failed_tests == 0:
        print(f"✅ All {total_tests} test suite(s) passed!")
        print("\n🎉 Testing completed successfully!")
        return 0
    else:
        print(f"❌ {failed_tests} out of {total_tests} test suite(s) failed")
        print(f"✅ {passed_tests} test suite(s) passed")
        print("\n💡 Tip: Use --verbose for more detailed output")
        print("💡 Tip: Use --quick for fast feedback during development")
        return 1

if __name__ == "__main__":
    sys.exit(main())