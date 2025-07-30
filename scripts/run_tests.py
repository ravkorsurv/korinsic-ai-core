#!/usr/bin/env python3
"""
Test Runner for Person-Centric Surveillance System

This script provides various test execution options for the surveillance system,
including unit tests, integration tests, performance tests, and regulatory compliance tests.

Usage:
    python scripts/run_tests.py --help
    python scripts/run_tests.py --unit
    python scripts/run_tests.py --integration
    python scripts/run_tests.py --e2e
    python scripts/run_tests.py --regulatory
    python scripts/run_tests.py --performance
    python scripts/run_tests.py --all
    python scripts/run_tests.py --coverage
    python scripts/run_tests.py --parallel
"""

import argparse
import subprocess
import sys
import os
import time
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Test runner for the person-centric surveillance system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / "tests"
        
    def run_command(self, cmd: List[str], description: str) -> bool:
        """Run a command and return success status"""
        print(f"\n{'=' * 60}")
        print(f"Running: {description}")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'=' * 60}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=False,
                text=True,
                check=True
            )
            
            elapsed = time.time() - start_time
            print(f"\n✅ {description} completed successfully in {elapsed:.2f}s")
            return True
            
        except subprocess.CalledProcessError as e:
            elapsed = time.time() - start_time
            print(f"\n❌ {description} failed after {elapsed:.2f}s")
            print(f"Exit code: {e.returncode}")
            return False
        except KeyboardInterrupt:
            print(f"\n⚠️ {description} interrupted by user")
            return False
    
    def run_unit_tests(self, parallel: bool = False, coverage: bool = False) -> bool:
        """Run unit tests"""
        cmd = ["python3", "-m", "pytest", "-m", "unit"]
        
        if parallel:
            cmd.extend(["-n", "auto"])
        
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov/unit",
                "--cov-report=term-missing"
            ])
        
        cmd.extend(["-v", "--tb=short"])
        
        return self.run_command(cmd, "Unit Tests")
    
    def run_integration_tests(self, parallel: bool = False, coverage: bool = False) -> bool:
        """Run integration tests"""
        cmd = ["python3", "-m", "pytest", "-m", "integration"]
        
        if parallel:
            cmd.extend(["-n", "auto"])
        
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov/integration",
                "--cov-report=term-missing"
            ])
        
        cmd.extend(["-v", "--tb=short"])
        
        return self.run_command(cmd, "Integration Tests")
    
    def run_e2e_tests(self, coverage: bool = False) -> bool:
        """Run end-to-end tests"""
        cmd = ["python3", "-m", "pytest", "-m", "e2e"]
        
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov/e2e",
                "--cov-report=term-missing"
            ])
        
        cmd.extend(["-v", "--tb=short", "-s"])  # -s for output capture in e2e tests
        
        return self.run_command(cmd, "End-to-End Tests")
    
    def run_regulatory_tests(self, coverage: bool = False) -> bool:
        """Run regulatory compliance tests"""
        cmd = ["python3", "-m", "pytest", "-m", "regulatory"]
        
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov/regulatory",
                "--cov-report=term-missing"
            ])
        
        cmd.extend(["-v", "--tb=short"])
        
        return self.run_command(cmd, "Regulatory Compliance Tests")
    
    def run_performance_tests(self) -> bool:
        """Run performance tests"""
        cmd = [
            "python3", "-m", "pytest", 
            "-m", "performance",
            "-v", "--tb=short",
            "--durations=0"  # Show all test durations
        ]
        
        return self.run_command(cmd, "Performance Tests")
    
    def run_specific_typology_tests(self, typology: str, coverage: bool = False) -> bool:
        """Run tests for a specific risk typology"""
        cmd = ["python3", "-m", "pytest", "-m", typology]
        
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov/{typology}",
                "--cov-report=term-missing"
            ])
        
        cmd.extend(["-v", "--tb=short"])
        
        return self.run_command(cmd, f"{typology.replace('_', ' ').title()} Tests")
    
    def run_component_tests(self, component: str, coverage: bool = False) -> bool:
        """Run tests for a specific component"""
        cmd = ["python3", "-m", "pytest", "-m", component]
        
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov/{component}",
                "--cov-report=term-missing"
            ])
        
        cmd.extend(["-v", "--tb=short"])
        
        return self.run_command(cmd, f"{component.replace('_', ' ').title()} Tests")
    
    def run_all_tests(self, parallel: bool = False, coverage: bool = True) -> bool:
        """Run all tests"""
        cmd = ["python3", "-m", "pytest"]
        
        if parallel:
            cmd.extend(["-n", "auto"])
        
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov/all",
                "--cov-report=term-missing",
                "--cov-report=xml",
                "--cov-fail-under=80"
            ])
        
        cmd.extend([
            "-v", "--tb=short",
            "--durations=10"
        ])
        
        return self.run_command(cmd, "All Tests")
    
    def run_quick_tests(self, parallel: bool = True) -> bool:
        """Run quick tests (unit + fast integration tests)"""
        cmd = [
            "python3", "-m", "pytest",
            "-m", "unit or (integration and not slow)",
            "-v", "--tb=short"
        ]
        
        if parallel:
            cmd.extend(["-n", "auto"])
        
        return self.run_command(cmd, "Quick Tests (Unit + Fast Integration)")
    
    def run_smoke_tests(self) -> bool:
        """Run smoke tests for basic functionality"""
        cmd = [
            "python3", "-m", "pytest",
            "-k", "test_basic or test_simple or test_smoke",
            "-v", "--tb=short",
            "--maxfail=5"  # Stop after 5 failures
        ]
        
        return self.run_command(cmd, "Smoke Tests")
    
    def generate_test_report(self) -> bool:
        """Generate comprehensive test report"""
        cmd = [
            "python3", "-m", "pytest",
            "--html=reports/test_report.html",
            "--self-contained-html",
            "--cov=src",
            "--cov-report=html:htmlcov/report",
            "--cov-report=xml",
            "--junit-xml=reports/junit.xml",
            "-v"
        ]
        
        # Create reports directory
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        return self.run_command(cmd, "Comprehensive Test Report Generation")
    
    def check_test_environment(self) -> bool:
        """Check if test environment is properly set up"""
        print("Checking test environment...")
        
        # Check if pytest is installed
        try:
            subprocess.run(["python3", "-m", "pytest", "--version"], 
                         capture_output=True, check=True)
            print("✅ pytest is installed")
        except subprocess.CalledProcessError:
            print("❌ pytest is not installed. Run: pip install pytest")
            return False
        except FileNotFoundError:
            print("❌ python3 not found. Please install Python 3")
            return False
        
        # Check if test directory exists
        if not self.test_dir.exists():
            print(f"❌ Test directory not found: {self.test_dir}")
            return False
        print(f"✅ Test directory found: {self.test_dir}")
        
        # Check if source directory exists
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            print(f"❌ Source directory not found: {src_dir}")
            return False
        print(f"✅ Source directory found: {src_dir}")
        
        # Check for key test files
        key_test_files = [
            "test_person_centric_surveillance.py",
            "test_regulatory_compliance.py",
            "conftest.py"
        ]
        
        for test_file in key_test_files:
            test_path = self.test_dir / test_file
            if test_path.exists():
                print(f"✅ Found: {test_file}")
            else:
                print(f"⚠️ Missing: {test_file}")
        
        print("✅ Test environment check completed")
        return True
    
    def list_available_tests(self) -> bool:
        """List all available tests"""
        cmd = [
            "python3", "-m", "pytest",
            "--collect-only", "-q"
        ]
        
        return self.run_command(cmd, "List Available Tests")
    
    def run_failed_tests(self) -> bool:
        """Re-run only the tests that failed in the last run"""
        cmd = [
            "python3", "-m", "pytest",
            "--lf",  # Last failed
            "-v", "--tb=short"
        ]
        
        return self.run_command(cmd, "Re-run Failed Tests")


def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(
        description="Test Runner for Person-Centric Surveillance System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py --unit                    # Run unit tests
  python scripts/run_tests.py --integration --parallel  # Run integration tests in parallel
  python scripts/run_tests.py --all --coverage          # Run all tests with coverage
  python scripts/run_tests.py --regulatory              # Run regulatory compliance tests
  python scripts/run_tests.py --performance             # Run performance tests
  python scripts/run_tests.py --typology insider_dealing # Run insider dealing tests
  python scripts/run_tests.py --component entity_resolution # Run entity resolution tests
  python scripts/run_tests.py --quick                   # Run quick tests
  python scripts/run_tests.py --smoke                   # Run smoke tests
  python scripts/run_tests.py --report                  # Generate comprehensive report
        """
    )
    
    # Test type options
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    parser.add_argument("--regulatory", action="store_true", help="Run regulatory compliance tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--quick", action="store_true", help="Run quick tests (unit + fast integration)")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    parser.add_argument("--failed", action="store_true", help="Re-run failed tests")
    
    # Specific test options
    parser.add_argument("--typology", choices=[
        "insider_dealing", "spoofing", "market_manipulation", 
        "front_running", "wash_trading", "cross_desk_collusion"
    ], help="Run tests for specific risk typology")
    
    parser.add_argument("--component", choices=[
        "entity_resolution", "evidence_aggregation", "cross_typology",
        "alert_generation", "explainability"
    ], help="Run tests for specific component")
    
    # Execution options
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive test report")
    
    # Utility options
    parser.add_argument("--check", action="store_true", help="Check test environment")
    parser.add_argument("--list", action="store_true", help="List available tests")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Handle utility options first
    if args.check:
        return 0 if runner.check_test_environment() else 1
    
    if args.list:
        return 0 if runner.list_available_tests() else 1
    
    if args.report:
        return 0 if runner.generate_test_report() else 1
    
    # Check environment before running tests
    if not runner.check_test_environment():
        print("❌ Test environment check failed. Please fix issues before running tests.")
        return 1
    
    success = True
    
    # Run specific test types
    if args.unit:
        success &= runner.run_unit_tests(parallel=args.parallel, coverage=args.coverage)
    
    if args.integration:
        success &= runner.run_integration_tests(parallel=args.parallel, coverage=args.coverage)
    
    if args.e2e:
        success &= runner.run_e2e_tests(coverage=args.coverage)
    
    if args.regulatory:
        success &= runner.run_regulatory_tests(coverage=args.coverage)
    
    if args.performance:
        success &= runner.run_performance_tests()
    
    if args.all:
        success &= runner.run_all_tests(parallel=args.parallel, coverage=args.coverage)
    
    if args.quick:
        success &= runner.run_quick_tests(parallel=args.parallel)
    
    if args.smoke:
        success &= runner.run_smoke_tests()
    
    if args.failed:
        success &= runner.run_failed_tests()
    
    if args.typology:
        success &= runner.run_specific_typology_tests(args.typology, coverage=args.coverage)
    
    if args.component:
        success &= runner.run_component_tests(args.component, coverage=args.coverage)
    
    # If no specific test type was specified, show help
    if not any([
        args.unit, args.integration, args.e2e, args.regulatory, args.performance,
        args.all, args.quick, args.smoke, args.failed, args.typology, args.component
    ]):
        parser.print_help()
        return 0
    
    # Print final result
    if success:
        print("\n🎉 All requested tests completed successfully!")
        return 0
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())