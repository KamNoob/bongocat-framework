"""
HTML Parser - Specialized HTML content parsing
"""

from ..types import Dict, List, Any, Optional

# Import for type hints only
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bs4 import BeautifulSoup, Tag


class HtmlParser:
    """Specialized parser for HTML content"""
    
    def __init__(self, config: Dict = None):
        """Initialize HTML parser"""
        self.config = config or {}
        self.default_selectors = {
            'title': 'title',
            'headings': 'h1, h2, h3, h4, h5, h6',
            'paragraphs': 'p',
            'links': 'a[href]',
            'images': 'img[src]',
            'forms': 'form'
        }
    
    def parse(self, html_content: str, **kwargs) -> Dict[str, Any]:
        """Parse HTML content and extract structured data with lazy loading"""
        try:
            # Lazy load BeautifulSoup only when parsing is needed
            from bs4 import BeautifulSoup, Tag
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract basic page information
            basic_info = self._extract_basic_info(soup)
            
            # Extract elements based on selectors
            selectors = kwargs.get('selectors', self.default_selectors)
            extracted_elements = self._extract_elements(soup, selectors)
            
            # Extract metadata
            metadata = self._extract_metadata(soup)
            
            # Extract tables
            tables = self._extract_tables(soup)
            
            return {
                'success': True,
                'basic_info': basic_info,
                'elements': extracted_elements,
                'metadata': metadata,
                'tables': tables,
                'soup_object': soup
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content_preview': html_content[:500] + '...' if len(html_content) > 500 else html_content
            }
    
    def _extract_basic_info(self, soup: 'BeautifulSoup') -> Dict[str, Any]:
        """Extract basic page information"""
        info = {}
        
        # Page title
        title_tag = soup.find('title')
        info['title'] = title_tag.get_text(strip=True) if title_tag else ''
        
        # Character count and structure
        info['total_text_length'] = len(soup.get_text())
        info['tag_count'] = len(soup.find_all())
        info['link_count'] = len(soup.find_all('a', href=True))
        info['image_count'] = len(soup.find_all('img', src=True))
        info['form_count'] = len(soup.find_all('form'))
        
        return info
    
    def _extract_elements(self, soup: 'BeautifulSoup', selectors: Dict[str, str]) -> Dict[str, List[Dict]]:
        """Extract elements based on CSS selectors"""
        elements = {}
        
        for element_type, selector in selectors.items():
            try:
                found_elements = soup.select(selector)
                elements[element_type] = []
                
                for elem in found_elements:
                    element_data = {
                        'text': elem.get_text(strip=True),
                        'tag': elem.name
                    }
                    
                    # Add specific attributes based on element type
                    if element_type == 'links':
                        element_data['href'] = elem.get('href', '')
                        element_data['title'] = elem.get('title', '')
                    elif element_type == 'images':
                        element_data['src'] = elem.get('src', '')
                        element_data['alt'] = elem.get('alt', '')
                        element_data['title'] = elem.get('title', '')
                    elif element_type == 'forms':
                        element_data['action'] = elem.get('action', '')
                        element_data['method'] = elem.get('method', 'get')
                        element_data['input_count'] = len(elem.find_all('input'))
                    
                    elements[element_type].append(element_data)
                    
            except Exception as e:
                elements[element_type] = {'error': str(e)}
        
        return elements
    
    def _extract_metadata(self, soup: 'BeautifulSoup') -> Dict[str, str]:
        """Extract page metadata"""
        metadata = {}
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        # Language
        html_tag = soup.find('html')
        if html_tag:
            metadata['lang'] = html_tag.get('lang', '')
        
        return metadata
    
    def _extract_tables(self, soup: 'BeautifulSoup') -> List[Dict]:
        """Extract table data"""
        tables = []
        table_tags = soup.find_all('table')
        
        for table in table_tags:
            table_data = {
                'headers': [],
                'rows': [],
                'caption': ''
            }
            
            # Extract caption
            caption = table.find('caption')
            if caption:
                table_data['caption'] = caption.get_text(strip=True)
            
            # Extract headers
            header_row = table.find('tr')
            if header_row:
                headers = header_row.find_all(['th', 'td'])
                table_data['headers'] = [header.get_text(strip=True) for header in headers]
            
            # Extract data rows
            rows = table.find_all('tr')[1:] if table.find_all('tr') else []
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    table_data['rows'].append(row_data)
            
            tables.append(table_data)
        
        return tables