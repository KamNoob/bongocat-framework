"""
Main Data Parser - Coordinates different parsing strategies
"""

import json
import re
from ..types import Any, Dict, List, Optional, Union

from .html_parser import HtmlParser
from .json_parser import JsonParser
from .xml_parser import XmlParser
from .csv_parser import CsvParser
from .text_cleaner import TextCleaner
from ..error_logger.logger import ErrorLogger


class DataParser:
    """Main data parser that coordinates different parsing strategies"""
    
    def __init__(self, config: Dict = None):
        """Initialize data parser with configuration"""
        self.config = config or {}
        self.logger = ErrorLogger()
        
        # Initialize specialized parsers
        self.html_parser = HtmlParser(self.config.get('html', {}))
        self.json_parser = JsonParser(self.config.get('json', {}))
        self.xml_parser = XmlParser(self.config.get('xml', {}))
        self.csv_parser = CsvParser(self.config.get('csv', {}))
        self.text_cleaner = TextCleaner(self.config.get('text_cleaning', {}))
    
    def parse(self, content: str, content_type: str = 'auto', **kwargs) -> Dict[str, Any]:
        """
        Parse content based on type
        
        Args:
            content: Raw content to parse
            content_type: Type of content ('html', 'json', 'xml', 'csv', 'text', 'auto')
            **kwargs: Additional parsing options
            
        Returns:
            Parsed and structured data
        """
        try:
            # Auto-detect content type if not specified
            if content_type == 'auto':
                content_type = self._detect_content_type(content)
            
            self.logger.info(f"Parsing content as {content_type}")
            
            # Route to appropriate parser
            if content_type == 'html':
                return self._parse_html(content, **kwargs)
            elif content_type == 'json':
                return self._parse_json(content, **kwargs)
            elif content_type == 'xml':
                return self._parse_xml(content, **kwargs)
            elif content_type == 'csv':
                return self._parse_csv(content, **kwargs)
            elif content_type == 'text':
                return self._parse_text(content, **kwargs)
            else:
                self.logger.warning(f"Unknown content type: {content_type}")
                return self._parse_text(content, **kwargs)
                
        except Exception as e:
            self.logger.error(f"Parsing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content_type': content_type,
                'raw_content': content[:500] + '...' if len(content) > 500 else content
            }
    
    def _detect_content_type(self, content: str) -> str:
        """Auto-detect content type"""
        content_stripped = content.strip()
        
        # Check for JSON - avoid creating temporary objects in exception handling
        if (content_stripped.startswith('{') and content_stripped.endswith('}')) or \
           (content_stripped.startswith('[') and content_stripped.endswith(']')):
            try:
                json.loads(content_stripped)
                return 'json'
            except (json.JSONDecodeError, ValueError):
                # Specific exception handling without temp object creation
                pass
        
        # Check for XML
        if content_stripped.startswith('<?xml') or \
           (content_stripped.startswith('<') and content_stripped.endswith('>')):
            return 'xml'
        
        # Check for HTML
        if '<html' in content_stripped.lower() or \
           '<body' in content_stripped.lower() or \
           '<!doctype html' in content_stripped.lower():
            return 'html'
        
        # Check for CSV (basic heuristic)
        lines = content_stripped.split('\n')[:5]  # Check first 5 lines
        if len(lines) > 1:
            delimiters = [',', ';', '\t', '|']
            for delimiter in delimiters:
                if all(delimiter in line for line in lines if line.strip()):
                    return 'csv'
        
        # Default to text
        return 'text'
    
    def _parse_html(self, content: str, **kwargs) -> Dict[str, Any]:
        """Parse HTML content"""
        result = self.html_parser.parse(content, **kwargs)
        result['content_type'] = 'html'
        return result
    
    def _parse_json(self, content: str, **kwargs) -> Dict[str, Any]:
        """Parse JSON content"""
        result = self.json_parser.parse(content, **kwargs)
        result['content_type'] = 'json'
        return result
    
    def _parse_xml(self, content: str, **kwargs) -> Dict[str, Any]:
        """Parse XML content"""
        result = self.xml_parser.parse(content, **kwargs)
        result['content_type'] = 'xml'
        return result
    
    def _parse_csv(self, content: str, **kwargs) -> Dict[str, Any]:
        """Parse CSV content"""
        result = self.csv_parser.parse(content, **kwargs)
        result['content_type'] = 'csv'
        return result
    
    def _parse_text(self, content: str, **kwargs) -> Dict[str, Any]:
        """Parse plain text content with streaming approach to reduce memory usage"""
        # Stream processing for large text content
        original_length = len(content)
        
        # Use generator for memory-efficient text cleaning
        cleaned_text_gen = self.text_cleaner.clean_stream(content)
        
        # Only store cleaned text if explicitly requested or for small content
        include_cleaned = kwargs.get('include_cleaned', original_length < 10000)
        
        if include_cleaned:
            cleaned_text = self.text_cleaner.clean(content)
            patterns = self._extract_text_patterns(cleaned_text)
            word_count = len(cleaned_text.split())
            line_count = len(cleaned_text.split('\n'))
            cleaned_length = len(cleaned_text)
        else:
            # Process in chunks for large content
            cleaned_text = None
            patterns = self._extract_text_patterns_streaming(content)
            word_count, line_count, cleaned_length = self._count_text_stats_streaming(content)
        
        return {
            'success': True,
            'content_type': 'text',
            'cleaned_text': cleaned_text,
            'original_length': original_length,
            'cleaned_length': cleaned_length,
            'patterns': patterns,
            'word_count': word_count,
            'line_count': line_count,
            'streaming_mode': not include_cleaned
        }
    
    def _extract_text_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract common patterns from text"""
        patterns = {}
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        patterns['emails'] = re.findall(email_pattern, text)
        
        # URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        patterns['urls'] = re.findall(url_pattern, text)
        
        # Phone numbers (basic pattern)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        patterns['phone_numbers'] = re.findall(phone_pattern, text)
        
        # Numbers
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        patterns['numbers'] = re.findall(number_pattern, text)
        
        return patterns
    
    def _extract_text_patterns_streaming(self, text: str, chunk_size: int = 8192) -> Dict[str, List[str]]:
        """Extract patterns from large text using streaming approach"""
        patterns = {'emails': [], 'urls': [], 'phone_numbers': [], 'numbers': []}
        
        # Process text in chunks to avoid memory issues
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            chunk_patterns = self._extract_text_patterns(chunk)
            
            # Merge patterns
            for key, values in chunk_patterns.items():
                if key in patterns:
                    patterns[key].extend(values)
        
        # Remove duplicates while preserving order
        for key in patterns:
            patterns[key] = list(dict.fromkeys(patterns[key]))
        
        return patterns
    
    def _count_text_stats_streaming(self, text: str, chunk_size: int = 8192) -> tuple:
        """Count text statistics in streaming fashion for large texts"""
        word_count = 0
        line_count = text.count('\n') + 1  # Simple line count
        cleaned_length = 0
        
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            cleaned_chunk = self.text_cleaner.clean(chunk)
            word_count += len(cleaned_chunk.split())
            cleaned_length += len(cleaned_chunk)
        
        return word_count, line_count, cleaned_length
    
    def extract_structured_data(self, content: str, schema: Dict, **kwargs) -> Dict[str, Any]:
        """Extract data based on provided schema"""
        try:
            content_type = self._detect_content_type(content)
            parsed = self.parse(content, content_type, **kwargs)
            
            if not parsed.get('success', False):
                return parsed
            
            # Apply schema-based extraction
            extracted_data = {}
            
            for field, selector in schema.items():
                try:
                    if content_type == 'html' and 'data' in parsed:
                        # Lazy load BeautifulSoup only when needed for HTML parsing
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(content, 'html.parser')
                        elements = soup.select(selector)
                        if elements:
                            extracted_data[field] = [elem.get_text(strip=True) for elem in elements]
                        else:
                            extracted_data[field] = []
                    elif content_type == 'json' and 'data' in parsed:
                        # JSON path extraction (simplified)
                        extracted_data[field] = self._extract_json_path(parsed['data'], selector)
                    else:
                        extracted_data[field] = None
                        
                except Exception as e:
                    self.logger.warning(f"Failed to extract {field}: {str(e)}")
                    extracted_data[field] = None
            
            return {
                'success': True,
                'content_type': content_type,
                'extracted_data': extracted_data,
                'schema_applied': schema
            }
            
        except Exception as e:
            self.logger.error(f"Schema-based extraction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'schema': schema
            }
    
    def _extract_json_path(self, data: Any, path: str, max_depth: int = 20) -> Any:
        """Extract data from JSON using dot notation path with depth limiting"""
        if not path or max_depth <= 0:
            return None
            
        try:
            current = data
            keys = path.split('.')
            
            # Limit traversal depth to prevent excessive recursion
            if len(keys) > max_depth:
                self.logger.warning(f"JSON path depth {len(keys)} exceeds maximum {max_depth}")
                keys = keys[:max_depth]
            
            for depth, key in enumerate(keys):
                if depth >= max_depth:
                    break
                    
                if isinstance(current, dict):
                    current = current.get(key)
                elif isinstance(current, list) and key.isdigit():
                    idx = int(key)
                    if 0 <= idx < len(current):
                        current = current[idx]
                    else:
                        return None
                else:
                    return None
                    
                # Early exit if we hit None
                if current is None:
                    break
                    
            return current
        except (ValueError, IndexError, TypeError) as e:
            self.logger.debug(f"JSON path extraction error: {str(e)}")
            return None
        except Exception:
            # Catch-all for unexpected errors without creating temp objects
            return None