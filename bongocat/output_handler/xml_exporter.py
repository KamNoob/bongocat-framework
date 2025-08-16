"""XML Export functionality"""

import xml.etree.ElementTree as ET
from typing import Any


class XmlExporter:
    def export(self, data: Any, filepath: str):
        """Export data to XML file"""
        root = ET.Element("bongocat_data")
        self._dict_to_xml(data, root)
        tree = ET.ElementTree(root)
        tree.write(filepath, encoding='utf-8', xml_declaration=True)
    
    def _dict_to_xml(self, data: Any, parent: ET.Element):
        """Convert dict/list to XML elements"""
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(parent, str(key))
                self._dict_to_xml(value, child)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                child = ET.SubElement(parent, f"item_{i}")
                self._dict_to_xml(item, child)
        else:
            parent.text = str(data)