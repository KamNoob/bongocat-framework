"""CSV Export functionality"""

import csv
from typing import Any, List, Dict


class CsvExporter:
    def export(self, data: Any, filepath: str):
        """Export data to CSV file"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        else:
            # Convert simple data to CSV format
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if isinstance(data, dict):
                    for key, value in data.items():
                        writer.writerow([key, value])
                else:
                    writer.writerow([str(data)])