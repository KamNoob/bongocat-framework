"""Test Runner - Main test execution engine"""

import unittest
import sys
import time
from typing import Dict, List, Any, Optional
from io import StringIO
import importlib
import traceback


class TestRunner:
    def __init__(self, verbosity: int = 2):
        self.verbosity = verbosity
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def discover_tests(self, start_dir: str = '.') -> unittest.TestSuite:
        """Discover all test cases"""
        loader = unittest.TestLoader()
        return loader.discover(start_dir, pattern='test_*.py')
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all discovered tests"""
        self.start_time = time.time()
        
        # Create test suite
        suite = self.discover_tests()
        
        # Run tests with custom result collector
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=self.verbosity,
            resultclass=DetailedTestResult
        )
        
        result = runner.run(suite)
        self.end_time = time.time()
        
        # Compile results
        self.results = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped),
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1)) * 100,
            'duration': self.end_time - self.start_time,
            'failure_details': [{'test': str(test), 'error': error} for test, error in result.failures],
            'error_details': [{'test': str(test), 'error': error} for test, error in result.errors],
            'output': stream.getvalue()
        }
        
        return self.results
    
    def run_specific_tests(self, test_patterns: List[str]) -> Dict[str, Any]:
        """Run specific test patterns"""
        self.start_time = time.time()
        
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        
        for pattern in test_patterns:
            try:
                # Try to load as module.class.method
                if '.' in pattern:
                    module_name, test_name = pattern.rsplit('.', 1)
                    module = importlib.import_module(module_name)
                    suite.addTest(loader.loadTestsFromName(test_name, module))
                else:
                    # Try to load as module
                    module = importlib.import_module(pattern)
                    suite.addTests(loader.loadTestsFromModule(module))
            except Exception as e:
                print(f"Failed to load test {pattern}: {e}")
        
        # Run the suite
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=self.verbosity)
        result = runner.run(suite)
        
        self.end_time = time.time()
        
        self.results = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1)) * 100,
            'duration': self.end_time - self.start_time,
            'output': stream.getvalue()
        }
        
        return self.results
    
    def run_component_tests(self, component_name: str) -> Dict[str, Any]:
        """Run tests for specific component"""
        test_module = f"test_{component_name}"
        return self.run_specific_tests([test_module])
    
    def generate_report(self) -> str:
        """Generate detailed test report"""
        if not self.results:
            return "No test results available"
        
        report = f"""
BongoCat Test Report
==================

Test Summary:
- Tests Run: {self.results['tests_run']}
- Failures: {self.results['failures']}
- Errors: {self.results['errors']}
- Skipped: {self.results.get('skipped', 0)}
- Success Rate: {self.results['success_rate']:.1f}%
- Duration: {self.results['duration']:.2f}s

"""
        
        if self.results['failures']:
            report += "Failures:\n"
            for failure in self.results['failure_details']:
                report += f"- {failure['test']}: {failure['error']}\n"
            report += "\n"
        
        if self.results['errors']:
            report += "Errors:\n"
            for error in self.results['error_details']:
                report += f"- {error['test']}: {error['error']}\n"
        
        return report
    
    def get_coverage_report(self) -> Dict[str, Any]:
        """Get code coverage information"""
        # Mock coverage data for now
        return {
            'overall_coverage': 85.6,
            'component_coverage': {
                'core_scraper': 92.3,
                'data_parser': 88.7,
                'config_manager': 95.1,
                'output_handler': 87.4,
                'error_logger': 79.2,
                'web_interface': 73.8,
                'testing_suite': 91.5
            },
            'lines_covered': 2847,
            'lines_total': 3325,
            'branches_covered': 1205,
            'branches_total': 1456
        }


class DetailedTestResult(unittest.TestResult):
    """Enhanced test result collector"""
    
    def __init__(self, stream=None, descriptions=None, verbosity=None):
        super().__init__(stream, descriptions, verbosity)
        self.test_details = []
    
    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.time()
    
    def stopTest(self, test):
        super().stopTest(test)
        duration = time.time() - self.start_time
        self.test_details.append({
            'test': str(test),
            'duration': duration,
            'status': 'passed' if test not in [t[0] for t in self.failures + self.errors] else 'failed'
        })