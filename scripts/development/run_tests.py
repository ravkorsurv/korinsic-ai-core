#!/usr/bin/env python3
"""
Comprehensive test runner for Kor.ai surveillance platform.
Executes all test types: unit, integration, e2e, performance, and security.
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_results.log')
    ]
)

logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'results': {},
            'summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'coverage': 0.0,
                'duration': 0.0
            }
        }
        
    def run_command(self, cmd, cwd=None):
        """Run a shell command and return the result."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd or self.project_root
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            logger.error(f"Command failed: {cmd}. Error: {e}")
            return False, "", str(e)

    def run_unit_tests(self):
        """Run unit tests with coverage."""
        logger.info("Running unit tests...")
        
        cmd = (
            "python -m pytest tests/unit/ "
            "--cov=src "
            "--cov-report=html:htmlcov "
            "--cov-report=json:coverage.json "
            "--cov-report=term "
            "--cov-fail-under=80 "
            "--junitxml=test_results_unit.xml "
            "--tb=short "
            "-v"
        )
        
        success, stdout, stderr = self.run_command(cmd)
        
        # Parse coverage from JSON report
        coverage = 0.0
        try:
            with open(self.project_root / 'coverage.json', 'r') as f:
                coverage_data = json.load(f)
                coverage = coverage_data.get('totals', {}).get('percent_covered', 0.0)
        except FileNotFoundError:
            logger.warning("Coverage report not found")
        
        self.test_results['results']['unit_tests'] = {
            'success': success,
            'coverage': coverage,
            'stdout': stdout,
            'stderr': stderr
        }
        
        return success

    def run_integration_tests(self):
        """Run integration tests."""
        logger.info("Running integration tests...")
        
        cmd = (
            "python -m pytest tests/integration/ "
            "--junitxml=test_results_integration.xml "
            "--tb=short "
            "-v"
        )
        
        success, stdout, stderr = self.run_command(cmd)
        
        self.test_results['results']['integration_tests'] = {
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        }
        
        return success

    def run_e2e_tests(self):
        """Run end-to-end tests."""
        logger.info("Running end-to-end tests...")
        
        cmd = (
            "python -m pytest tests/e2e/ "
            "--junitxml=test_results_e2e.xml "
            "--tb=short "
            "-v"
        )
        
        success, stdout, stderr = self.run_command(cmd)
        
        self.test_results['results']['e2e_tests'] = {
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        }
        
        return success

    def run_performance_tests(self):
        """Run performance tests."""
        logger.info("Running performance tests...")
        
        cmd = (
            "python -m pytest tests/performance/ "
            "--junitxml=test_results_performance.xml "
            "--tb=short "
            "-v"
        )
        
        success, stdout, stderr = self.run_command(cmd)
        
        self.test_results['results']['performance_tests'] = {
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        }
        
        return success

    def run_security_tests(self):
        """Run security tests using bandit."""
        logger.info("Running security tests...")
        
        # Run bandit security scanner
        cmd = "bandit -r src/ -f json -o security_report.json"
        success, stdout, stderr = self.run_command(cmd)
        
        # Parse security report
        security_issues = []
        try:
            with open(self.project_root / 'security_report.json', 'r') as f:
                security_data = json.load(f)
                security_issues = security_data.get('results', [])
        except FileNotFoundError:
            logger.warning("Security report not found")
        
        # Consider success if no high or medium severity issues
        high_issues = [i for i in security_issues if i.get('issue_severity') in ['HIGH', 'MEDIUM']]
        security_success = len(high_issues) == 0
        
        self.test_results['results']['security_tests'] = {
            'success': security_success,
            'issues_found': len(security_issues),
            'high_severity_issues': len(high_issues),
            'stdout': stdout,
            'stderr': stderr
        }
        
        return security_success

    def run_dependency_check(self):
        """Check for vulnerable dependencies."""
        logger.info("Checking dependencies for vulnerabilities...")
        
        cmd = "safety check --json"
        success, stdout, stderr = self.run_command(cmd)
        
        # Parse safety report
        vulnerabilities = []
        try:
            if stdout:
                safety_data = json.loads(stdout)
                vulnerabilities = safety_data if isinstance(safety_data, list) else []
        except json.JSONDecodeError:
            logger.warning("Could not parse safety report")
        
        dependency_success = len(vulnerabilities) == 0
        
        self.test_results['results']['dependency_check'] = {
            'success': dependency_success,
            'vulnerabilities_found': len(vulnerabilities),
            'stdout': stdout,
            'stderr': stderr
        }
        
        return dependency_success

    def run_code_quality_checks(self):
        """Run code quality checks."""
        logger.info("Running code quality checks...")
        
        # Run black formatter check
        black_success, black_stdout, black_stderr = self.run_command("black --check src/")
        
        # Run flake8 linter
        flake8_success, flake8_stdout, flake8_stderr = self.run_command("flake8 src/")
        
        # Run mypy type checker
        mypy_success, mypy_stdout, mypy_stderr = self.run_command("mypy src/")
        
        quality_success = black_success and flake8_success and mypy_success
        
        self.test_results['results']['code_quality'] = {
            'success': quality_success,
            'black': {'success': black_success, 'stdout': black_stdout, 'stderr': black_stderr},
            'flake8': {'success': flake8_success, 'stdout': flake8_stdout, 'stderr': flake8_stderr},
            'mypy': {'success': mypy_success, 'stdout': mypy_stdout, 'stderr': mypy_stderr}
        }
        
        return quality_success

    def generate_report(self):
        """Generate comprehensive test report."""
        logger.info("Generating test report...")
        
        # Calculate summary statistics
        results = self.test_results['results']
        
        # Count total success/failure
        all_results = [
            results.get('unit_tests', {}).get('success', False),
            results.get('integration_tests', {}).get('success', False),
            results.get('e2e_tests', {}).get('success', False),
            results.get('performance_tests', {}).get('success', False),
            results.get('security_tests', {}).get('success', False),
            results.get('dependency_check', {}).get('success', False),
            results.get('code_quality', {}).get('success', False)
        ]
        
        passed = sum(all_results)
        total = len(all_results)
        
        self.test_results['summary'].update({
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'coverage': results.get('unit_tests', {}).get('coverage', 0.0),
            'success_rate': (passed / total * 100) if total > 0 else 0
        })
        
        # Save JSON report
        with open(self.project_root / 'test_report.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        # Generate HTML report
        self.generate_html_report()
        
        return passed == total

    def generate_html_report(self):
        """Generate HTML test report."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Results Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
                .warning {{ color: orange; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .summary {{ background-color: #f9f9f9; }}
                pre {{ background-color: #f5f5f5; padding: 10px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Test Results Report</h1>
                <p>Generated: {timestamp}</p>
                <p>Success Rate: {success_rate:.1f}%</p>
            </div>
            
            <div class="section summary">
                <h2>Summary</h2>
                <ul>
                    <li>Total Tests: {total_tests}</li>
                    <li>Passed: {passed_tests}</li>
                    <li>Failed: {failed_tests}</li>
                    <li>Coverage: {coverage:.1f}%</li>
                </ul>
            </div>
            
            {sections}
        </body>
        </html>
        """
        
        sections = []
        for test_type, result in self.test_results['results'].items():
            status_class = "success" if result.get('success', False) else "failure"
            section_html = f"""
            <div class="section">
                <h3 class="{status_class}">{test_type.replace('_', ' ').title()}</h3>
                <p>Status: <span class="{status_class}">{'PASSED' if result.get('success', False) else 'FAILED'}</span></p>
                {f"<p>Coverage: {result.get('coverage', 0):.1f}%</p>" if 'coverage' in result else ""}
                {f"<p>Issues Found: {result.get('issues_found', 0)}</p>" if 'issues_found' in result else ""}
            </div>
            """
            sections.append(section_html)
        
        html_content = html_template.format(
            timestamp=self.test_results['timestamp'],
            success_rate=self.test_results['summary']['success_rate'],
            total_tests=self.test_results['summary']['total_tests'],
            passed_tests=self.test_results['summary']['passed_tests'],
            failed_tests=self.test_results['summary']['failed_tests'],
            coverage=self.test_results['summary']['coverage'],
            sections='\n'.join(sections)
        )
        
        with open(self.project_root / 'test_report.html', 'w') as f:
            f.write(html_content)

    def run_all_tests(self, test_types=None):
        """Run all specified test types."""
        start_time = datetime.now()
        
        if test_types is None:
            test_types = ['unit', 'integration', 'e2e', 'performance', 'security', 'dependencies', 'quality']
        
        logger.info(f"Starting test execution: {', '.join(test_types)}")
        
        success = True
        
        if 'unit' in test_types:
            success &= self.run_unit_tests()
        
        if 'integration' in test_types:
            success &= self.run_integration_tests()
        
        if 'e2e' in test_types:
            success &= self.run_e2e_tests()
        
        if 'performance' in test_types:
            success &= self.run_performance_tests()
        
        if 'security' in test_types:
            success &= self.run_security_tests()
        
        if 'dependencies' in test_types:
            success &= self.run_dependency_check()
        
        if 'quality' in test_types:
            success &= self.run_code_quality_checks()
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        self.test_results['summary']['duration'] = duration
        
        # Generate report
        self.generate_report()
        
        logger.info(f"Test execution completed in {duration:.2f} seconds")
        logger.info(f"Overall success: {success}")
        
        return success

def main():
    parser = argparse.ArgumentParser(description='Run comprehensive tests for Kor.ai platform')
    parser.add_argument(
        '--types',
        nargs='*',
        choices=['unit', 'integration', 'e2e', 'performance', 'security', 'dependencies', 'quality'],
        default=None,
        help='Test types to run (default: all)'
    )
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Run only fast tests (unit + integration + quality)'
    )
    parser.add_argument(
        '--ci',
        action='store_true',
        help='Run in CI mode (all tests, strict failure on any issue)'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.fast:
        test_types = ['unit', 'integration', 'quality']
    elif args.ci:
        test_types = ['unit', 'integration', 'e2e', 'performance', 'security', 'dependencies', 'quality']
    else:
        test_types = args.types
    
    success = runner.run_all_tests(test_types)
    
    if not success:
        logger.error("Some tests failed!")
        sys.exit(1)
    
    logger.info("All tests passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()