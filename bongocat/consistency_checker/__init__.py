"""
Consistency Checker - Main consistency checking and audit system for BongoCat

This system analyzes all project components and generates consistency reports
to identify and resolve inconsistencies across the codebase.
"""

from .checker import ConsistencyChecker
from .analyzer import CodeAnalyzer
from .reporter import ConsistencyReporter
from .rules import ConsistencyRules
from .fixer import ConsistencyFixer
from .validator import ConsistencyValidator

__all__ = [
    "ConsistencyChecker",
    "CodeAnalyzer", 
    "ConsistencyReporter",
    "ConsistencyRules",
    "ConsistencyFixer",
    "ConsistencyValidator"
]