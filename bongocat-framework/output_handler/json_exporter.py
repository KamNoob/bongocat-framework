"""JSON Export functionality"""

import json
from typing import Any


class JsonExporter:
    def export(self, data: Any, filepath: str):
        """Export data to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)