"""Data Formatter - Format data for different export types"""

from typing import Any, Dict, List


class DataFormatter:
    @staticmethod
    def format_for_csv(data: Any) -> List[Dict]:
        """Format data for CSV export"""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            return [{'value': str(data)}]
    
    @staticmethod
    def format_for_table(data: Any) -> Dict:
        """Format data for table display"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return {
                'headers': list(data[0].keys()),
                'rows': [[row.get(header, '') for header in data[0].keys()] for row in data]
            }
        return {'headers': ['Data'], 'rows': [[str(data)]]}
    
    @staticmethod
    def flatten_dict(data: Dict, prefix: str = '') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                items.extend(DataFormatter.flatten_dict(value, new_key).items())
            else:
                items.append((new_key, value))
        return dict(items)