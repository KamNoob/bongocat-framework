"""Consistency Rules - Defines rules for consistency checking"""

from typing import Dict, List, Any
import re


class ConsistencyRules:
    """Defines and manages consistency checking rules"""
    
    def __init__(self):
        self.rules = {
            'naming_conventions': self._get_naming_rules(),
            'import_patterns': self._get_import_rules(),
            'error_handling': self._get_error_handling_rules(),
            'documentation': self._get_documentation_rules(),
            'type_annotations': self._get_type_annotation_rules(),
            'code_structure': self._get_code_structure_rules()
        }
    
    def _get_naming_rules(self) -> Dict[str, Any]:
        """Rules for naming conventions"""
        return {
            'function_naming': {
                'pattern': r'^[a-z_][a-z0-9_]*$',
                'description': 'Functions should use snake_case',
                'severity': 'medium'
            },
            'class_naming': {
                'pattern': r'^[A-Z][a-zA-Z0-9]*$',
                'description': 'Classes should use PascalCase',
                'severity': 'medium'
            },
            'constant_naming': {
                'pattern': r'^[A-Z][A-Z0-9_]*$',
                'description': 'Constants should use UPPER_CASE',
                'severity': 'low'
            },
            'private_naming': {
                'pattern': r'^_[a-z_][a-z0-9_]*$',
                'description': 'Private methods should start with underscore',
                'severity': 'low'
            }
        }
    
    def _get_import_rules(self) -> Dict[str, Any]:
        """Rules for import organization"""
        return {
            'import_order': {
                'order': ['standard_library', 'third_party', 'local'],
                'description': 'Imports should be ordered: stdlib, third-party, local',
                'severity': 'low'
            },
            'relative_imports': {
                'pattern': 'consistent',
                'description': 'Use consistent relative import patterns within components',
                'severity': 'medium'
            },
            'unused_imports': {
                'check': True,
                'description': 'Remove unused imports',
                'severity': 'low'
            },
            'wildcard_imports': {
                'allowed': False,
                'description': 'Avoid wildcard imports (from module import *)',
                'severity': 'medium'
            }
        }
    
    def _get_error_handling_rules(self) -> Dict[str, Any]:
        """Rules for error handling consistency"""
        return {
            'specific_exceptions': {
                'prefer_specific': True,
                'description': 'Catch specific exceptions rather than bare except',
                'severity': 'high'
            },
            'error_logging': {
                'required': True,
                'description': 'Log errors consistently using the error logger',
                'severity': 'medium'
            },
            'exception_chaining': {
                'preserve_context': True,
                'description': 'Preserve exception context when re-raising',
                'severity': 'medium'
            },
            'cleanup_pattern': {
                'use_finally': True,
                'description': 'Use finally blocks or context managers for cleanup',
                'severity': 'medium'
            }
        }
    
    def _get_documentation_rules(self) -> Dict[str, Any]:
        """Rules for documentation consistency"""
        return {
            'docstring_format': {
                'style': 'google',
                'description': 'Use consistent docstring format (Google style)',
                'severity': 'low'
            },
            'public_method_docs': {
                'required': True,
                'description': 'All public methods must have docstrings',
                'severity': 'medium'
            },
            'class_docs': {
                'required': True,
                'description': 'All classes must have docstrings',
                'severity': 'medium'
            },
            'module_docs': {
                'required': True,
                'description': 'All modules should have module-level docstrings',
                'severity': 'low'
            }
        }
    
    def _get_type_annotation_rules(self) -> Dict[str, Any]:
        """Rules for type annotation consistency"""
        return {
            'function_annotations': {
                'required_for_public': True,
                'description': 'Public functions should have type annotations',
                'severity': 'low'
            },
            'return_annotations': {
                'required': True,
                'description': 'Functions should have return type annotations',
                'severity': 'low'
            },
            'complex_types': {
                'use_typing_module': True,
                'description': 'Use typing module for complex types',
                'severity': 'low'
            }
        }
    
    def _get_code_structure_rules(self) -> Dict[str, Any]:
        """Rules for code structure consistency"""
        return {
            'max_function_length': {
                'lines': 50,
                'description': 'Functions should not exceed 50 lines',
                'severity': 'medium'
            },
            'max_class_length': {
                'lines': 200,
                'description': 'Classes should not exceed 200 lines',
                'severity': 'low'
            },
            'cyclomatic_complexity': {
                'max_score': 10,
                'description': 'Functions should have cyclomatic complexity <= 10',
                'severity': 'medium'
            },
            'nested_depth': {
                'max_depth': 4,
                'description': 'Avoid deeply nested code structures',
                'severity': 'medium'
            }
        }
    
    def get_all_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get all consistency rules"""
        return self.rules
    
    def get_rules_by_category(self, category: str) -> Dict[str, Any]:
        """Get rules for specific category"""
        return self.rules.get(category, {})
    
    def check_naming_convention(self, name: str, name_type: str) -> Dict[str, Any]:
        """Check if name follows naming convention"""
        rules = self._get_naming_rules()
        rule_key = f'{name_type}_naming'
        
        if rule_key not in rules:
            return {'valid': True, 'message': 'No rule defined for this name type'}
        
        rule = rules[rule_key]
        pattern = rule['pattern']
        
        if re.match(pattern, name):
            return {'valid': True, 'message': 'Name follows convention'}
        else:
            return {
                'valid': False,
                'message': rule['description'],
                'severity': rule['severity'],
                'expected_pattern': pattern
            }
    
    def check_import_order(self, imports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if imports follow ordering rules"""
        # Simplified import order checking
        standard_library = {'os', 'sys', 'time', 'json', 'ast', 'inspect', 're', 'typing'}
        
        current_section = None
        issues = []
        
        for imp in imports:
            module = imp.get('module', '')
            
            if any(module.startswith(lib) for lib in standard_library):
                section = 'standard_library'
            elif module.startswith('.'):
                section = 'local'
            else:
                section = 'third_party'
            
            if current_section and section != current_section:
                # Check if we're going backwards in order
                expected_order = ['standard_library', 'third_party', 'local']
                if expected_order.index(section) < expected_order.index(current_section):
                    issues.append({
                        'line': imp.get('line'),
                        'issue': f'Import order violation: {section} after {current_section}',
                        'module': module
                    })
            
            current_section = section
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'message': 'Import order is correct' if not issues else f'{len(issues)} import order issues found'
        }
    
    def validate_error_handling(self, error_handlers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate error handling patterns"""
        issues = []
        
        for handler in error_handlers:
            # Check for bare except clauses
            if 'Exception' in handler.get('exception_types', []):
                issues.append({
                    'line': handler.get('line'),
                    'issue': 'Bare except clause - catch specific exceptions',
                    'severity': 'high'
                })
            
            # Check for too many exception types in single handler
            if len(handler.get('exception_types', [])) > 3:
                issues.append({
                    'line': handler.get('line'),
                    'issue': 'Too many exception types in single handler',
                    'severity': 'medium'
                })
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'message': 'Error handling is consistent' if not issues else f'{len(issues)} error handling issues found'
        }
    
    def get_rule_severity(self, rule_category: str, rule_name: str) -> str:
        """Get severity level for specific rule"""
        category_rules = self.rules.get(rule_category, {})
        rule = category_rules.get(rule_name, {})
        return rule.get('severity', 'medium')