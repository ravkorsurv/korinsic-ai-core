#!/usr/bin/env python3
"""
Code quality checker for Kor.ai surveillance platform.
Runs linting, formatting, type checking, and other quality checks.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class QualityChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'summary': {
                'total_checks': 0,
                'passed_checks': 0,
                'failed_checks': 0
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
            return False, "", str(e)
    
    def check_black_formatting(self):
        """Check code formatting with black."""
        print("🎨 Checking code formatting with black...")
        
        # Check if formatting is needed
        cmd = "black --check --diff src/ tests/"
        success, stdout, stderr = self.run_command(cmd)
        
        self.results['checks']['black'] = {
            'name': 'Black Code Formatting',
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'description': 'Code formatting check with black'
        }
        
        if not success:
            print("❌ Code formatting issues found")
            print("💡 Run 'black src/ tests/' to fix formatting")
        else:
            print("✅ Code formatting is correct")
        
        return success
    
    def check_flake8_linting(self):
        """Check code linting with flake8."""
        print("🔍 Checking code linting with flake8...")
        
        cmd = "flake8 src/ tests/ --statistics --count"
        success, stdout, stderr = self.run_command(cmd)
        
        self.results['checks']['flake8'] = {
            'name': 'Flake8 Linting',
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'description': 'Code linting with flake8'
        }
        
        if not success:
            print("❌ Linting issues found")
            print(f"Issues:\n{stdout}")
        else:
            print("✅ No linting issues found")
        
        return success
    
    def check_mypy_typing(self):
        """Check type annotations with mypy."""
        print("🔢 Checking type annotations with mypy...")
        
        cmd = "mypy src/ --ignore-missing-imports --show-error-codes"
        success, stdout, stderr = self.run_command(cmd)
        
        self.results['checks']['mypy'] = {
            'name': 'MyPy Type Checking',
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'description': 'Type annotation checking with mypy'
        }
        
        if not success:
            print("❌ Type checking issues found")
            print(f"Issues:\n{stdout}")
        else:
            print("✅ No type checking issues found")
        
        return success
    
    def check_isort_imports(self):
        """Check import sorting with isort."""
        print("📦 Checking import sorting with isort...")
        
        cmd = "isort --check-only --diff src/ tests/"
        success, stdout, stderr = self.run_command(cmd)
        
        self.results['checks']['isort'] = {
            'name': 'Import Sorting',
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'description': 'Import sorting check with isort'
        }
        
        if not success:
            print("❌ Import sorting issues found")
            print("💡 Run 'isort src/ tests/' to fix import sorting")
        else:
            print("✅ Import sorting is correct")
        
        return success
    
    def check_docstring_coverage(self):
        """Check docstring coverage."""
        print("📝 Checking docstring coverage...")
        
        cmd = "docformatter --check --diff src/"
        success, stdout, stderr = self.run_command(cmd)
        
        # Also check for basic docstring presence
        missing_docstrings = []
        for py_file in Path("src").rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if 'def ' in content and '"""' not in content:
                        missing_docstrings.append(str(py_file))
            except Exception:
                pass
        
        docstring_success = len(missing_docstrings) == 0
        
        self.results['checks']['docstrings'] = {
            'name': 'Docstring Coverage',
            'success': docstring_success,
            'stdout': f"Files missing docstrings: {missing_docstrings}",
            'stderr': "",
            'description': 'Docstring coverage check'
        }
        
        if not docstring_success:
            print("❌ Some files missing docstrings")
            for file in missing_docstrings[:5]:  # Show first 5
                print(f"  - {file}")
        else:
            print("✅ Docstring coverage is adequate")
        
        return docstring_success
    
    def check_complexity(self):
        """Check code complexity with radon."""
        print("🧮 Checking code complexity...")
        
        cmd = "radon cc src/ --min C --json"
        success, stdout, stderr = self.run_command(cmd)
        
        complex_functions = []
        if success and stdout:
            try:
                complexity_data = json.loads(stdout)
                for file_path, functions in complexity_data.items():
                    for func in functions:
                        if func.get('rank', 'A') in ['C', 'D', 'E', 'F']:
                            complex_functions.append({
                                'file': file_path,
                                'function': func.get('name', 'unknown'),
                                'complexity': func.get('complexity', 0),
                                'rank': func.get('rank', 'A')
                            })
            except json.JSONDecodeError:
                pass
        
        complexity_success = len(complex_functions) == 0
        
        self.results['checks']['complexity'] = {
            'name': 'Code Complexity',
            'success': complexity_success,
            'stdout': json.dumps(complex_functions, indent=2),
            'stderr': stderr,
            'description': 'Code complexity check with radon'
        }
        
        if not complexity_success:
            print(f"❌ Found {len(complex_functions)} complex functions")
            for func in complex_functions[:3]:  # Show first 3
                print(f"  - {func['file']}:{func['function']} (rank: {func['rank']})")
        else:
            print("✅ Code complexity is acceptable")
        
        return complexity_success
    
    def check_dead_code(self):
        """Check for dead code with vulture."""
        print("🦅 Checking for dead code...")
        
        cmd = "vulture src/ --min-confidence 60 --sort-by-size"
        success, stdout, stderr = self.run_command(cmd)
        
        # Vulture returns non-zero if dead code is found
        dead_code_found = not success and stdout
        
        self.results['checks']['dead_code'] = {
            'name': 'Dead Code Detection',
            'success': not dead_code_found,
            'stdout': stdout,
            'stderr': stderr,
            'description': 'Dead code detection with vulture'
        }
        
        if dead_code_found:
            print("❌ Potential dead code found")
            print("💡 Review the findings as they may be false positives")
        else:
            print("✅ No obvious dead code found")
        
        return not dead_code_found
    
    def check_security_issues(self):
        """Check for security issues with bandit."""
        print("🔒 Checking for security issues...")
        
        cmd = "bandit -r src/ -f json -o bandit_report.json"
        success, stdout, stderr = self.run_command(cmd)
        
        security_issues = []
        try:
            with open(self.project_root / 'bandit_report.json', 'r') as f:
                security_data = json.load(f)
                security_issues = security_data.get('results', [])
        except FileNotFoundError:
            pass
        
        # Consider high/medium issues as failures
        high_issues = [i for i in security_issues if i.get('issue_severity') in ['HIGH', 'MEDIUM']]
        security_success = len(high_issues) == 0
        
        self.results['checks']['security'] = {
            'name': 'Security Check',
            'success': security_success,
            'stdout': f"Total issues: {len(security_issues)}, High/Medium: {len(high_issues)}",
            'stderr': stderr,
            'description': 'Security issue detection with bandit'
        }
        
        if not security_success:
            print(f"❌ Found {len(high_issues)} high/medium security issues")
            for issue in high_issues[:3]:  # Show first 3
                print(f"  - {issue.get('filename', 'unknown')}: {issue.get('test_name', 'unknown')}")
        else:
            print("✅ No significant security issues found")
        
        return security_success
    
    def generate_report(self):
        """Generate quality check report."""
        print("\n📊 Generating quality report...")
        
        # Calculate summary
        checks = self.results['checks']
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks.values() if check['success'])
        failed_checks = total_checks - passed_checks
        
        self.results['summary'] = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
        }
        
        # Save JSON report
        with open(self.project_root / 'quality_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate HTML report
        self.generate_html_report()
        
        # Print summary
        print(f"\n📋 Quality Check Summary")
        print("=" * 50)
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {failed_checks}")
        print(f"Success Rate: {self.results['summary']['success_rate']:.1f}%")
        
        return failed_checks == 0
    
    def generate_html_report(self):
        """Generate HTML quality report."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Code Quality Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; }
                .success { color: green; }
                .failure { color: red; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
                .summary { background-color: #f9f9f9; }
                pre { background-color: #f5f5f5; padding: 10px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Code Quality Report</h1>
                <p>Generated: {timestamp}</p>
                <p>Success Rate: {success_rate:.1f}%</p>
            </div>
            
            <div class="section summary">
                <h2>Summary</h2>
                <ul>
                    <li>Total Checks: {total_checks}</li>
                    <li>Passed: {passed_checks}</li>
                    <li>Failed: {failed_checks}</li>
                </ul>
            </div>
            
            {sections}
        </body>
        </html>
        """
        
        sections = []
        for check_name, check_data in self.results['checks'].items():
            status_class = "success" if check_data['success'] else "failure"
            section_html = f"""
            <div class="section">
                <h3 class="{status_class}">{check_data['name']}</h3>
                <p>Status: <span class="{status_class}">{'PASSED' if check_data['success'] else 'FAILED'}</span></p>
                <p>{check_data['description']}</p>
                {f"<pre>{check_data['stdout'][:500]}...</pre>" if check_data['stdout'] else ""}
            </div>
            """
            sections.append(section_html)
        
        html_content = html_template.format(
            timestamp=self.results['timestamp'],
            success_rate=self.results['summary']['success_rate'],
            total_checks=self.results['summary']['total_checks'],
            passed_checks=self.results['summary']['passed_checks'],
            failed_checks=self.results['summary']['failed_checks'],
            sections='\n'.join(sections)
        )
        
        with open(self.project_root / 'quality_report.html', 'w') as f:
            f.write(html_content)
    
    def run_all_checks(self, check_types=None):
        """Run all quality checks."""
        print("🔍 Starting code quality checks...")
        print("=" * 50)
        
        if check_types is None:
            check_types = ['formatting', 'linting', 'typing', 'imports', 'docstrings', 'complexity', 'dead_code', 'security']
        
        success = True
        
        if 'formatting' in check_types:
            success &= self.check_black_formatting()
        
        if 'linting' in check_types:
            success &= self.check_flake8_linting()
        
        if 'typing' in check_types:
            success &= self.check_mypy_typing()
        
        if 'imports' in check_types:
            success &= self.check_isort_imports()
        
        if 'docstrings' in check_types:
            success &= self.check_docstring_coverage()
        
        if 'complexity' in check_types:
            success &= self.check_complexity()
        
        if 'dead_code' in check_types:
            success &= self.check_dead_code()
        
        if 'security' in check_types:
            success &= self.check_security_issues()
        
        # Check OpenInference integration if available
        success &= self.check_openinference_integration()
        
        # Generate report
        report_success = self.generate_report()
    
    def check_openinference_integration(self):
        """Check OpenInference integration components."""
        print("🔍 Checking OpenInference integration...")
        
        try:
            # Test basic imports
            sys.path.insert(0, str(self.project_root / 'src'))
            from utils.openinference_tracer import KorinsicOpenInferenceTracer, get_tracer
            
            # Test tracer initialization
            tracer = KorinsicOpenInferenceTracer({'enabled': False})
            
            # Test singleton pattern
            tracer1 = get_tracer()
            tracer2 = get_tracer()
            assert tracer1 is tracer2, "Singleton pattern not working"
            
            # Test context manager
            with tracer.trace_bayesian_inference('test_model') as span:
                pass  # Span may be None if OpenTelemetry not available
            
            print("✅ OpenInference integration check passed")
            
            self.results['checks']['openinference_integration'] = {
                'success': True,
                'message': 'OpenInference integration components working correctly'
            }
            self.results['summary']['total_checks'] += 1
            self.results['summary']['passed_checks'] += 1
            
            return True
            
        except ImportError as e:
            print(f"⚠️  OpenInference components not available: {e}")
            self.results['checks']['openinference_integration'] = {
                'success': True,  # Not a failure if optional components missing
                'message': f'OpenInference components not available (optional): {e}'
            }
            self.results['summary']['total_checks'] += 1
            self.results['summary']['passed_checks'] += 1
            return True
            
        except Exception as e:
            print(f"❌ OpenInference integration check failed: {e}")
            self.results['checks']['openinference_integration'] = {
                'success': False,
                'message': f'OpenInference integration check failed: {e}'
            }
            self.results['summary']['total_checks'] += 1
            self.results['summary']['failed_checks'] += 1
            return False
        
        return success and report_success

def main():
    parser = argparse.ArgumentParser(description='Run code quality checks for Kor.ai platform')
    parser.add_argument(
        '--checks',
        nargs='*',
        choices=['formatting', 'linting', 'typing', 'imports', 'docstrings', 'complexity', 'dead_code', 'security'],
        default=None,
        help='Quality checks to run (default: all)'
    )
    parser.add_argument(
        '--essential',
        action='store_true',
        help='Run only essential checks (formatting, linting, typing)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix issues automatically where possible'
    )
    
    args = parser.parse_args()
    
    if args.fix:
        print("🔧 Attempting to fix issues automatically...")
        subprocess.run("black src/ tests/", shell=True)
        subprocess.run("isort src/ tests/", shell=True)
        subprocess.run("docformatter --in-place src/", shell=True)
        print("✅ Auto-fix completed")
    
    checker = QualityChecker()
    
    if args.essential:
        check_types = ['formatting', 'linting', 'typing']
    else:
        check_types = args.checks
    
    success = checker.run_all_checks(check_types)
    
    if not success:
        print("\n❌ Some quality checks failed!")
        sys.exit(1)
    
    print("\n✅ All quality checks passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()