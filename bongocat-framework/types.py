"""
Centralized typing imports for BongoCat framework
Consolidates commonly used type hints to reduce import overhead
"""

from typing import (
    Any,
    Dict, 
    List,
    Optional,
    Union,
    Callable,
    Tuple,
    Generator,
    Iterator,
    TypeVar,
    Generic,
    Protocol
)

# Common type aliases for the framework
JSONData = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
Headers = Dict[str, str] 
Selectors = Dict[str, str]
ProxyDict = Dict[str, str]
ConfigDict = Dict[str, Any]
StatsDict = Dict[str, Union[int, float, str]]
URLList = List[str]