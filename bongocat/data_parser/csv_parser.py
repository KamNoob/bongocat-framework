"""CSV Parser - Specialized CSV content parsing"""

import csv
import io
from typing import Dict, Any, List


class CsvParser:
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def parse(self, csv_content: str, **kwargs) -> Dict[str, Any]:
        try:
            delimiter = kwargs.get('delimiter', ',')
            reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)
            rows = list(reader)
            
            return {
                'success': True,
                'data': rows,
                'row_count': len(rows),
                'columns': reader.fieldnames if reader.fieldnames else [],
                'delimiter': delimiter
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"CSV parse error: {str(e)}",
                'content_preview': csv_content[:200]
            }