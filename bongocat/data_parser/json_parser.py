"""JSON Parser - Specialized JSON content parsing"""

import json
from typing import Dict, Any, List, Union


class JsonParser:
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def parse(self, json_content: str, **kwargs) -> Dict[str, Any]:
        try:
            data = json.loads(json_content)
            return {
                'success': True,
                'data': data,
                'type': type(data).__name__,
                'size': self._calculate_size(data)
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"JSON decode error: {str(e)}",
                'content_preview': json_content[:200]
            }
    
    def _calculate_size(self, data: Any) -> Dict[str, int]:
        if isinstance(data, dict):
            return {'keys': len(data), 'type': 'object'}
        elif isinstance(data, list):
            return {'items': len(data), 'type': 'array'}
        else:
            return {'type': 'primitive'}