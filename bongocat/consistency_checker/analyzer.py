"""Code Analyzer - Analyzes Python code for consistency checking"""

import ast
import os
from typing import Dict, List, Any


class CodeAnalyzer:
    """Analyzes Python code structure and patterns"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_component(self, component_path: str, component_name: str) -> Dict[str, Any]:
        """Analyze entire component directory"""
        if not os.path.exists(component_path):
            return {'error': f'Component path not found: {component_path}'}
        
        files_analyzed = []
        total_lines = 0
        total_functions = 0
        total_classes = 0
        import_patterns = []
        error_patterns = []
        
        # Analyze all Python files in component
        for root, dirs, files in os.walk(component_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_analysis = self.analyze_file(file_path)
                    
                    if 'error' not in file_analysis:
                        files_analyzed.append({
                            'file': file,
                            'path': file_path,
                            'analysis': file_analysis
                        })
                        
                        total_lines += file_analysis['line_count']
                        total_functions += file_analysis['function_count']
                        total_classes += file_analysis['class_count']
                        import_patterns.extend(file_analysis['imports'])
                        error_patterns.extend(file_analysis['error_handling'])
        
        return {
            'component_name': component_name,
            'component_path': component_path,
            'file_count': len(files_analyzed),
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'files': files_analyzed,
            'import_patterns': import_patterns,
            'error_patterns': error_patterns,
            'analysis_timestamp': __import__('time').time()
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze individual Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            analyzer = FileAnalyzer()
            analyzer.visit(tree)
            
            return {
                'file_path': file_path,
                'line_count': len(content.splitlines()),
                'function_count': len(analyzer.functions),
                'class_count': len(analyzer.classes),
                'imports': analyzer.imports,
                'functions': analyzer.functions,
                'classes': analyzer.classes,
                'error_handling': analyzer.error_handlers,
                'docstrings': analyzer.docstrings,
                'type_annotations': analyzer.type_annotations,
                'complexity_score': analyzer.calculate_complexity()
            }
            
        except Exception as e:
            return {'error': f'Failed to analyze {file_path}: {str(e)}'}


class FileAnalyzer(ast.NodeVisitor):
    """AST visitor for detailed file analysis"""
    
    def __init__(self):
        self.imports = []
        self.functions = []
        self.classes = []
        self.error_handlers = []
        self.docstrings = []
        self.type_annotations = []
        self.complexity_score = 0
    
    def visit_Import(self, node):
        """Visit import statement"""
        for alias in node.names:
            self.imports.append({
                'type': 'import',
                'module': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from...import statement"""
        for alias in node.names:
            self.imports.append({
                'type': 'from_import',
                'module': node.module,
                'name': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definition"""
        # Check for type annotations
        has_annotations = bool(node.returns or any(arg.annotation for arg in node.args.args))
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'args': [arg.arg for arg in node.args.args],
            'has_docstring': bool(docstring),
            'docstring': docstring,
            'has_type_annotations': has_annotations,
            'is_private': node.name.startswith('_'),
            'is_async': isinstance(node, ast.AsyncFunctionDef)
        })
        
        if docstring:
            self.docstrings.append({
                'type': 'function',
                'name': node.name,
                'docstring': docstring,
                'line': node.lineno
            })
        
        if has_annotations:
            self.type_annotations.append({
                'type': 'function',
                'name': node.name,
                'line': node.lineno
            })
        
        self.complexity_score += 1  # Base complexity for function
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definition"""
        docstring = ast.get_docstring(node)
        
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        self.classes.append({
            'name': node.name,
            'line': node.lineno,
            'methods': methods,
            'has_docstring': bool(docstring),
            'docstring': docstring,
            'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
            'is_private': node.name.startswith('_')
        })
        
        if docstring:
            self.docstrings.append({
                'type': 'class',
                'name': node.name,
                'docstring': docstring,
                'line': node.lineno
            })
        
        self.complexity_score += 2  # Higher complexity for classes
        self.generic_visit(node)
    
    def visit_Try(self, node):
        """Visit try-except block"""
        exception_types = []
        for handler in node.handlers:
            if handler.type:
                if isinstance(handler.type, ast.Name):
                    exception_types.append(handler.type.id)
                else:
                    exception_types.append(str(handler.type))
            else:
                exception_types.append('Exception')  # Bare except
        
        self.error_handlers.append({
            'line': node.lineno,
            'exception_types': exception_types,
            'has_finally': bool(node.finalbody),
            'has_else': bool(node.orelse)
        })
        
        self.complexity_score += len(node.handlers)
        self.generic_visit(node)
    
    def visit_If(self, node):
        """Visit if statement"""
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Visit for loop"""
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Visit while loop"""
        self.complexity_score += 1
        self.generic_visit(node)
    
    def calculate_complexity(self) -> int:
        """Calculate McCabe complexity score"""
        return max(1, self.complexity_score)