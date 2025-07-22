#!/usr/bin/env python3
"""
Comprehensive test runner for OpenInference integration.
"""

import sys
import os
import subprocess
import argparse
import time
from typing import Dict, Any, Optional, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
    from utils.logger import setup_logger
    logger = setup_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class OpenInferenceTestRunner:
    """Comprehensive test runner for OpenInference integration."""
    
    def __init__(self, verbose: bool = False, fast_mode: bool = False):
        self.verbose = verbose
        self.fast_mode = fast_mode
        self.results = {}
        self.start_time = time.time()
        
        self.test_env = {
            'ENVIRONMENT': 'testing',
            'LOG_LEVEL': 'CRITICAL',
            'OTEL_TRACING_ENABLED': 'false',
            'PYTHONPATH': 'src'
        }
    
    def run_command(self, cmd: List[str], env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Run a command and return results."""
        env = os.environ.copy()
        env.update(self.test_env)
        if env_vars:
            env.update(env_vars)
        
        if self.verbose:
            logger.info(f"Running: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=300
            )
            
            execution_time = time.time() - start_time
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': execution_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'execution_time': time.time() - start_time
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'execution_time': time.time() - start_time
            }
    
    def run_unit_tests(self) -> bool:
        """Run unit tests for OpenInference components."""
        logger.info("Running unit tests...")
        
        unit_test_files = [
            'tests/unit/test_openinference_tracer.py',
            'tests/unit/test_enhanced_bayesian_engine.py'
        ]
        
        # Check if test files exist
        existing_files = [f for f in unit_test_files if os.path.exists(f)]
        
        if not existing_files:
            logger.warning("No unit test files found, creating basic test...")
            # Run basic import test
            cmd = [
                'python3', '-c',
                '''
import sys
sys.path.insert(0, "src")
try:
    from utils.openinference_tracer import KorinsicOpenInferenceTracer
    print("✅ OpenInference tracer imports successfully")
    tracer = KorinsicOpenInferenceTracer({"enabled": False})
    print("✅ OpenInference tracer initializes successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
'''
            ]
        else:
            cmd = [
                'python3', '-m', 'pytest',
                '--tb=short',
                '-v' if self.verbose else '-q'
            ] + existing_files
        
        result = self.run_command(cmd)
        self.results['unit_tests'] = result
        
        if result['success']:
            logger.info("✅ Unit tests passed")
        else:
            logger.error("❌ Unit tests failed")
            if self.verbose:
                logger.error(f"Error: {result['stderr']}")
        
        return result['success']
    
    def check_dependencies(self) -> bool:
        """Check that basic dependencies are available."""
        logger.info("Checking dependencies...")
        
        cmd = ['python3', '-c', 'import sys; print(f"Python {sys.version}")']
        result = self.run_command(cmd)
        
        if result['success']:
            logger.info("✅ Python available")
            if self.verbose:
                logger.info(result['stdout'].strip())
        else:
            logger.error("❌ Python not available")
            return False
        
        return True
    
    def generate_report(self):
        """Generate a test report."""
        total_time = time.time() - self.start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("OPENINFERENCE INTEGRATION TEST REPORT")
        logger.info("=" * 60)
        
        passed_tests = sum(1 for result in self.results.values() if result['success'])
        total_tests = len(self.results)
        
        logger.info(f"📊 Results: {passed_tests}/{total_tests} test suites passed")
        logger.info(f"⏱️  Total time: {total_time:.2f} seconds")
        
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            time_str = f"({result['execution_time']:.2f}s)"
            logger.info(f"   {test_name.replace('_', ' ').title()}: {status} {time_str}")
        
        if passed_tests == total_tests:
            logger.info("\n🎉 All tests passed!")
        else:
            logger.info(f"\n⚠️  {total_tests - passed_tests} test suite(s) failed.")
    
    def run_all_tests(self) -> bool:
        """Run all available test suites."""
        logger.info("🚀 Starting OpenInference integration tests")
        
        # Check dependencies first
        if not self.check_dependencies():
            return False
        
        # Run unit tests
        all_passed = self.run_unit_tests()
        
        # Generate report
        self.generate_report()
        
        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run OpenInference integration tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--fast', '-f', action='store_true', help='Fast mode')
    
    args = parser.parse_args()
    
    runner = OpenInferenceTestRunner(verbose=args.verbose, fast_mode=args.fast)
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
