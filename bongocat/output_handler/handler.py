"""Main Output Handler"""

import os
from typing import Any, Dict, List, Union
from .json_exporter import JsonExporter
from .csv_exporter import CsvExporter
from .xml_exporter import XmlExporter
from .html_exporter import HtmlExporter


class OutputHandler:
    def __init__(self):
        self.exporters = {
            'json': JsonExporter(),
            'csv': CsvExporter(), 
            'xml': XmlExporter(),
            'html': HtmlExporter()
        }
    
    def export(self, data: Union[Dict, List], format: str, filename: str = None) -> str:
        """Export data to specified format"""
        if format not in self.exporters:
            raise ValueError(f"Unsupported format: {format}")
        
        exporter = self.exporters[format]
        
        if filename is None:
            filename = f"bongocat_output.{format}"
        
        filepath = os.path.join(os.getcwd(), filename)
        exporter.export(data, filepath)
        
        return filepath