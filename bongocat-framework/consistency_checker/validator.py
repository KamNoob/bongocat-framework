"""Consistency Validator - Validates consistency check results"""

from typing import Dict, List, Any, Optional, Tuple
import os
import re


class ConsistencyValidator:
    """Validates consistency check results and ensures quality"""
    
    def __init__(self):
        self.validation_rules = {
            'completeness': self._validate_completeness,
            'accuracy': self._validate_accuracy,
            'coverage': self._validate_coverage,
            'fix_quality': self._validate_fix_quality
        }
    
    def validate_consistency_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate entire consistency check results"""
        validation_results = {
            'overall_valid': True,
            'validation_issues': [],
            'quality_score': 0,
            'recommendations': []
        }
        
        # Run all validation checks
        for validation_type, validator in self.validation_rules.items():
            try:
                result = validator(results)
                validation_results[validation_type] = result
                
                if not result.get('valid', True):
                    validation_results['overall_valid'] = False
                    validation_results['validation_issues'].extend(result.get('issues', []))
                
                # Add to quality score
                validation_results['quality_score'] += result.get('score', 0)
                
                # Add recommendations
                validation_results['recommendations'].extend(result.get('recommendations', []))
                
            except Exception as e:
                validation_results['validation_issues'].append({
                    'type': validation_type,
                    'error': f'Validation failed: {str(e)}'
                })
                validation_results['overall_valid'] = False
        
        # Normalize quality score (out of 100)
        validation_results['quality_score'] = min(100, validation_results['quality_score'] / len(self.validation_rules) * 25)
        
        return validation_results
    
    def _validate_completeness(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that consistency check covered all required areas"""
        required_components = [
            'core_scraper', 'data_parser', 'config_manager', 
            'output_handler', 'error_logger', 'web_interface', 'testing_suite'
        ]
        
        scan_results = results.get('scan_results', {})
        scanned_components = list(scan_results.keys())
        
        missing_components = [comp for comp in required_components if comp not in scanned_components]
        
        issues = []
        if missing_components:
            issues.append({
                'type': 'missing_components',
                'components': missing_components,
                'message': f'Missing analysis for components: {", ".join(missing_components)}'
            })
        
        # Check if minimum file count was analyzed
        total_files = results.get('statistics', {}).get('total_files', 0)
        if total_files < 30:  # Expect at least 30+ files in full project
            issues.append({
                'type': 'insufficient_files',
                'count': total_files,
                'message': f'Only {total_files} files analyzed, expected more comprehensive coverage'
            })
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'score': 100 if len(issues) == 0 else max(0, 100 - len(issues) * 20),
            'recommendations': ['Run consistency check on all project components'] if issues else []
        }
    
    def _validate_accuracy(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate accuracy of issue detection and fixes"""
        consistency_issues = results.get('consistency_issues', [])
        fixed_issues = results.get('fixed_issues', [])
        
        issues = []
        
        # Check if Core Scraper System has the expected 4 issues (as shown in original Qwen output)
        core_scraper_issues = [issue for issue in consistency_issues if issue.get('component') == 'core_scraper']
        if len(core_scraper_issues) != 4:
            issues.append({
                'type': 'core_scraper_issue_count',
                'expected': 4,
                'actual': len(core_scraper_issues),
                'message': f'Core Scraper System should have 4 issues, found {len(core_scraper_issues)}'
            })
        
        # Validate fix success rate
        total_issues = len(consistency_issues)
        total_fixed = len(fixed_issues)
        
        if total_issues > 0:
            fix_rate = (total_fixed / total_issues) * 100
            if fix_rate < 90:  # Expect at least 90% fix success rate
                issues.append({
                    'type': 'low_fix_rate',
                    'rate': fix_rate,
                    'message': f'Fix success rate {fix_rate:.1f}% is below expected 90%'
                })
        
        # Check for proper issue categorization
        expected_issue_types = ['import_inconsistency', 'naming_convention', 'error_handling', 'documentation']
        found_types = set(issue.get('type') for issue in consistency_issues)
        
        if not any(issue_type in found_types for issue_type in expected_issue_types):
            issues.append({
                'type': 'missing_issue_types',
                'message': 'No common consistency issue types detected'
            })
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'score': max(0, 100 - len(issues) * 15),
            'recommendations': ['Review issue detection algorithms'] if issues else []
        }
    
    def _validate_coverage(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate coverage of consistency checking"""
        scan_results = results.get('scan_results', {})
        
        issues = []
        total_coverage_score = 0
        component_count = 0
        
        for component_name, component_data in scan_results.items():
            component_count += 1
            
            # Check file coverage
            file_count = component_data.get('file_count', 0)
            if file_count < 3:  # Expect at least 3 files per component
                issues.append({
                    'type': 'low_file_coverage',
                    'component': component_name,
                    'count': file_count,
                    'message': f'{component_name} has only {file_count} files analyzed'
                })
            
            # Check analysis depth
            total_functions = component_data.get('total_functions', 0)
            if total_functions == 0:
                issues.append({
                    'type': 'no_functions_analyzed',
                    'component': component_name,
                    'message': f'No functions found in {component_name} analysis'
                })
            
            # Calculate component coverage score
            component_score = min(100, (file_count * 10) + (total_functions * 2))
            total_coverage_score += component_score
        
        # Calculate average coverage
        avg_coverage = total_coverage_score / max(component_count, 1)
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'score': min(100, avg_coverage),
            'coverage_percentage': avg_coverage,
            'recommendations': ['Improve analysis depth for all components'] if avg_coverage < 80 else []
        }
    
    def _validate_fix_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality of applied fixes"""
        fixed_issues = results.get('fixed_issues', [])
        
        issues = []
        
        if not fixed_issues:
            issues.append({
                'type': 'no_fixes_applied',
                'message': 'No fixes were applied during consistency check'
            })
            return {
                'valid': False,
                'issues': issues,
                'score': 0,
                'recommendations': ['Ensure fixes are properly applied and recorded']
            }
        
        # Check fix descriptions
        fixes_without_description = [fix for fix in fixed_issues if not fix.get('fix_applied')]
        if fixes_without_description:
            issues.append({
                'type': 'missing_fix_descriptions',
                'count': len(fixes_without_description),
                'message': f'{len(fixes_without_description)} fixes lack proper descriptions'
            })
        
        # Validate fix types match issue types
        issue_types = set(issue.get('type') for issue in results.get('consistency_issues', []))
        fix_types = set(fix.get('type') for fix in fixed_issues)
        
        unmatched_types = issue_types - fix_types
        if unmatched_types:
            issues.append({
                'type': 'unmatched_fix_types',
                'types': list(unmatched_types),
                'message': f'Some issue types were not addressed: {", ".join(unmatched_types)}'
            })
        
        # Check for proper timestamps
        fixes_without_timestamp = [fix for fix in fixed_issues if not fix.get('fix_timestamp')]
        if fixes_without_timestamp:
            issues.append({
                'type': 'missing_timestamps',
                'count': len(fixes_without_timestamp),
                'message': 'Some fixes missing timestamps'
            })
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'score': max(0, 100 - len(issues) * 10),
            'recommendations': ['Improve fix tracking and documentation'] if issues else []
        }
    
    def validate_component_analysis(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis results for a specific component"""
        validation_result = {
            'valid': True,
            'issues': [],
            'quality_metrics': {}
        }
        
        # Check file count
        file_count = component_data.get('file_count', 0)
        validation_result['quality_metrics']['file_coverage'] = file_count
        
        if file_count == 0:
            validation_result['valid'] = False
            validation_result['issues'].append('No files found in component')
        
        # Check code metrics
        total_lines = component_data.get('total_lines', 0)
        total_functions = component_data.get('total_functions', 0)
        
        validation_result['quality_metrics']['lines_of_code'] = total_lines
        validation_result['quality_metrics']['function_count'] = total_functions
        
        if total_lines == 0:
            validation_result['valid'] = False
            validation_result['issues'].append('No code lines analyzed')
        
        if total_functions == 0 and file_count > 1:
            validation_result['issues'].append('No functions detected in multi-file component')
        
        return validation_result
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate human-readable validation report"""
        report = "Consistency Check Validation Report\n"
        report += "=" * 38 + "\n\n"
        
        # Overall status
        status = "PASSED" if validation_results['overall_valid'] else "FAILED"
        report += f"Overall Status: {status}\n"
        report += f"Quality Score: {validation_results['quality_score']:.1f}/100\n\n"
        
        # Issues
        if validation_results['validation_issues']:
            report += "Issues Found:\n"
            report += "-" * 13 + "\n"
            for issue in validation_results['validation_issues']:
                report += f"• {issue.get('message', str(issue))}\n"
            report += "\n"
        
        # Recommendations
        if validation_results['recommendations']:
            report += "Recommendations:\n"
            report += "-" * 16 + "\n"
            for rec in validation_results['recommendations']:
                report += f"• {rec}\n"
            report += "\n"
        
        # Detailed validation results
        for validation_type, result in validation_results.items():
            if validation_type in ['overall_valid', 'validation_issues', 'quality_score', 'recommendations']:
                continue
                
            if isinstance(result, dict):
                report += f"\n{validation_type.title()} Validation:\n"
                report += f"  Status: {'PASSED' if result.get('valid', True) else 'FAILED'}\n"
                report += f"  Score: {result.get('score', 0):.1f}/100\n"
                
                if result.get('issues'):
                    report += "  Issues:\n"
                    for issue in result['issues']:
                        report += f"    • {issue.get('message', str(issue))}\n"
        
        return report