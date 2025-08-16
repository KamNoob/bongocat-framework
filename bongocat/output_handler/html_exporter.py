"""HTML Export functionality"""

from typing import Any


class HtmlExporter:
    def export(self, data: Any, filepath: str):
        """Export data to HTML file"""
        html_content = self._generate_html(data)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html(self, data: Any) -> str:
        """Generate HTML representation of data"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>BongoCat Export</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .json { background-color: #f8f8f8; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>BongoCat Data Export</h1>
"""
        
        if isinstance(data, list) and data and isinstance(data[0], dict):
            html += self._dict_list_to_table(data)
        else:
            html += f'<div class="json"><pre>{str(data)}</pre></div>'
        
        html += """
</body>
</html>"""
        return html
    
    def _dict_list_to_table(self, data: list) -> str:
        """Convert list of dicts to HTML table"""
        if not data:
            return ""
        
        headers = list(data[0].keys())
        table = "<table><thead><tr>"
        
        for header in headers:
            table += f"<th>{header}</th>"
        table += "</tr></thead><tbody>"
        
        for row in data:
            table += "<tr>"
            for header in headers:
                table += f"<td>{row.get(header, '')}</td>"
            table += "</tr>"
        
        table += "</tbody></table>"
        return table