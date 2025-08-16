"""Template Renderer - Handles template rendering with context"""

from flask import render_template_string
from typing import Dict, Any
import os


class TemplateRenderer:
    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), 'templates')
    
    def render(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """Render template with context"""
        context = context or {}
        
        # Add default context variables
        context.update({
            'app_name': 'BongoCat',
            'version': '1.0.0'
        })
        
        template_path = os.path.join(self.template_dir, template_name)
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            return render_template_string(template_content, **context)
            
        except FileNotFoundError:
            return self._get_default_template(template_name, context)
    
    def _get_default_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Get default template if file not found"""
        base_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ app_name }} - {{ page_title | default('Dashboard') }}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background-color: #f8f9fa; }
        .main-content { padding: 20px; }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
        .status-active { background-color: #28a745; }
        .status-inactive { background-color: #dc3545; }
        .status-warning { background-color: #ffc107; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky pt-3">
                    <h4>{{ app_name }}</h4>
                    <ul class="nav flex-column">
                        <li class="nav-item"><a class="nav-link" href="/">Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link" href="/scraper">Scraper</a></li>
                        <li class="nav-item"><a class="nav-link" href="/results">Results</a></li>
                        <li class="nav-item"><a class="nav-link" href="/logs">Logs</a></li>
                    </ul>
                </div>
            </nav>
            
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                {% block content %}
                <h1>{{ page_title | default('Welcome to BongoCat') }}</h1>
                <p>{{ content | default('Select an option from the sidebar to get started.') }}</p>
                {% endblock %}
            </main>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script>
        // Initialize Socket.IO connection
        const socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to BongoCat server');
        });
        
        socket.on('status_update', function(data) {
            console.log('Status update:', data);
            // Update UI based on status
        });
    </script>
</body>
</html>
"""
        
        return render_template_string(base_template, **context)