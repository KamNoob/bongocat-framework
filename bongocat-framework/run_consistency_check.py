#!/usr/bin/env python3
"""
BongoCat Consistency Check Runner

This script runs the comprehensive consistency check and generates the audit report
exactly as shown in the original Qwen AI session.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from consistency_checker.checker import ConsistencyChecker
from consistency_checker.reporter import ConsistencyReporter

def main():
    """Run the BongoCat consistency check and generate report"""
    
    print("🔍 BongoCat Final Package - Consistency Check & Packaging")
    print()
    
    # Initialize consistency checker
    checker = ConsistencyChecker()
    
    # Run comprehensive consistency check
    results = checker.run_full_consistency_check()
    
    # Generate the console output that matches the original Qwen format
    reporter = ConsistencyReporter()
    console_output = reporter.generate_console_output(results)
    
    # Display the results
    print(console_output)
    
    # Save detailed report
    report_file = checker.export_detailed_report('consistency_audit_report.json')
    print(f"\n📁 Detailed audit report saved to: {report_file}")
    
    return results

if __name__ == '__main__':
    main()