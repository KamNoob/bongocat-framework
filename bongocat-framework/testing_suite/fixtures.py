"""Test Fixtures - Reusable test data and mock objects"""

import tempfile
import os
from typing import Dict, Any, List


class TestFixtures:
    """Collection of test fixtures and sample data"""
    
    @staticmethod
    def get_sample_html() -> str:
        """Get sample HTML content for testing"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
    <meta name="description" content="Sample page for testing">
</head>
<body>
    <header>
        <h1>Test Website</h1>
        <nav>
            <a href="#home">Home</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
        </nav>
    </header>
    
    <main>
        <section id="content">
            <h2>Main Content</h2>
            <p>This is a paragraph with some <strong>bold text</strong> and <em>italic text</em>.</p>
            
            <ul>
                <li>List item 1</li>
                <li>List item 2</li>
                <li>List item 3</li>
            </ul>
            
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Age</th>
                        <th>City</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Alice</td>
                        <td>30</td>
                        <td>New York</td>
                    </tr>
                    <tr>
                        <td>Bob</td>
                        <td>25</td>
                        <td>San Francisco</td>
                    </tr>
                </tbody>
            </table>
        </section>
        
        <aside>
            <h3>Sidebar</h3>
            <p>Additional information</p>
        </aside>
    </main>
    
    <footer>
        <p>&copy; 2024 Test Website</p>
    </footer>
</body>
</html>
"""
    
    @staticmethod
    def get_sample_json() -> str:
        """Get sample JSON content for testing"""
        return """
{
    "users": [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "profile": {
                "age": 28,
                "city": "Boston",
                "preferences": ["reading", "coding", "hiking"]
            }
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane@example.com",
            "profile": {
                "age": 32,
                "city": "Seattle",
                "preferences": ["photography", "travel", "cooking"]
            }
        }
    ],
    "metadata": {
        "total": 2,
        "page": 1,
        "timestamp": "2024-01-01T12:00:00Z"
    }
}
"""
    
    @staticmethod
    def get_sample_xml() -> str:
        """Get sample XML content for testing"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <book id="1">
        <title>Python Programming</title>
        <author>John Smith</author>
        <price currency="USD">29.99</price>
        <category>Programming</category>
        <published>2023</published>
    </book>
    <book id="2">
        <title>Web Scraping Guide</title>
        <author>Jane Doe</author>
        <price currency="USD">24.99</price>
        <category>Web Development</category>
        <published>2024</published>
    </book>
</catalog>
"""
    
    @staticmethod
    def get_sample_csv() -> str:
        """Get sample CSV content for testing"""
        return """name,age,city,occupation,salary
Alice Johnson,28,New York,Engineer,75000
Bob Wilson,34,San Francisco,Designer,68000
Carol Davis,29,Boston,Developer,72000
David Brown,31,Seattle,Manager,85000
Eva Martinez,26,Austin,Analyst,58000
"""
    
    @staticmethod
    def get_sample_config() -> Dict[str, Any]:
        """Get sample configuration for testing"""
        return {
            "rate_limit": 2.0,
            "timeout": 15,
            "log_level": "DEBUG",
            "proxies": [
                "http://proxy1.example.com:8080",
                "http://proxy2.example.com:8080"
            ],
            "max_retries": 5,
            "user_agents": [
                "Mozilla/5.0 (Test Browser 1.0)",
                "Mozilla/5.0 (Test Browser 2.0)"
            ],
            "output_format": "json"
        }
    
    @staticmethod
    def get_sample_selectors() -> Dict[str, str]:
        """Get sample CSS selectors for testing"""
        return {
            "title": "h1",
            "paragraphs": "p",
            "links": "a[href]",
            "images": "img[src]",
            "headings": "h1, h2, h3",
            "table_rows": "table tr",
            "form_inputs": "form input"
        }
    
    @staticmethod
    def create_temp_config_file(config_data: Dict[str, Any] = None) -> str:
        """Create temporary configuration file"""
        import json
        
        if config_data is None:
            config_data = TestFixtures.get_sample_config()
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(config_data, temp_file, indent=2)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def create_temp_html_file(html_content: str = None) -> str:
        """Create temporary HTML file"""
        if html_content is None:
            html_content = TestFixtures.get_sample_html()
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
        temp_file.write(html_content)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def cleanup_temp_files(file_paths: List[str]):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass  # Ignore cleanup errors
    
    @staticmethod
    def get_sample_scraper_result() -> Dict[str, Any]:
        """Get sample scraper result for testing"""
        return {
            'url': 'http://example.com',
            'status': 'success',
            'status_code': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Content-Length': '1024'
            },
            'content': TestFixtures.get_sample_html(),
            'data': {
                'title': 'Test Website',
                'paragraphs': ['This is a paragraph with some bold text and italic text.'],
                'links': ['#home', '#about', '#contact']
            },
            'timestamp': 1704067200.0
        }
    
    @staticmethod
    def get_sample_parse_result() -> Dict[str, Any]:
        """Get sample parser result for testing"""
        return {
            'success': True,
            'content_type': 'html',
            'basic_info': {
                'title': 'Test Page',
                'total_text_length': 500,
                'tag_count': 25,
                'link_count': 3,
                'image_count': 0,
                'form_count': 0
            },
            'elements': {
                'title': [{'text': 'Test Page', 'tag': 'title'}],
                'headings': [
                    {'text': 'Test Website', 'tag': 'h1'},
                    {'text': 'Main Content', 'tag': 'h2'}
                ],
                'paragraphs': [
                    {'text': 'This is a paragraph with some bold text and italic text.', 'tag': 'p'}
                ]
            },
            'metadata': {
                'lang': 'en',
                'description': 'Sample page for testing',
                'viewport': 'width=device-width, initial-scale=1.0'
            }
        }