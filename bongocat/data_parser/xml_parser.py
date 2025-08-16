"""XML Parser - Specialized XML content parsing"""

import xml.etree.ElementTree as ET
from typing import Dict, Any


class XmlParser:
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def parse(self, xml_content: str, **kwargs) -> Dict[str, Any]:
        try:
            root = ET.fromstring(xml_content)
            return {
                'success': True,
                'root_tag': root.tag,
                'data': self._element_to_dict(root),
                'element_count': len(list(root.iter()))
            }
        except ET.ParseError as e:
            return {
                'success': False,
                'error': f"XML parse error: {str(e)}",
                'content_preview': xml_content[:200]
            }
    
    def _element_to_dict(self, element) -> Dict[str, Any]:
        result = {'tag': element.tag}
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        if element.attrib:
            result['attributes'] = element.attrib
        children = list(element)
        if children:
            result['children'] = [self._element_to_dict(child) for child in children]
        return result