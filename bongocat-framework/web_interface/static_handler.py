"""Static Handler - Serve static files for web interface"""

import os
import mimetypes
from flask import send_from_directory, abort
from typing import Optional


class StaticHandler:
    def __init__(self, static_dir: str = None):
        self.static_dir = static_dir or os.path.join(os.path.dirname(__file__), 'static')
        
        # Ensure static directory exists
        if not os.path.exists(self.static_dir):
            os.makedirs(self.static_dir)
    
    def serve_file(self, filename: str) -> Optional[str]:
        """Serve static file"""
        try:
            return send_from_directory(self.static_dir, filename)
        except FileNotFoundError:
            abort(404)
    
    def get_file_path(self, filename: str) -> str:
        """Get full path to static file"""
        return os.path.join(self.static_dir, filename)
    
    def file_exists(self, filename: str) -> bool:
        """Check if static file exists"""
        return os.path.exists(self.get_file_path(filename))
    
    def get_mime_type(self, filename: str) -> str:
        """Get MIME type for file"""
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    def create_default_files(self):
        """Create default static files if they don't exist"""
        
        # Create default CSS
        css_content = """
/* BongoCat Web Interface Styles */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
    --dark-color: #343a40;
    --light-color: #f8f9fa;
}

.bongocat-header {
    background: linear-gradient(135deg, var(--primary-color), var(--info-color));
    color: white;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 20px;
}

.status-card {
    border-left: 4px solid var(--success-color);
    transition: transform 0.2s;
}

.status-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.scraper-form {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.log-entry {
    padding: 8px 12px;
    margin: 4px 0;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.9em;
}

.log-entry.info { background-color: #e3f2fd; }
.log-entry.warning { background-color: #fff3e0; }
.log-entry.error { background-color: #ffebee; }
.log-entry.debug { background-color: #f3e5f5; }

.progress-container {
    margin: 20px 0;
}

.result-display {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 15px;
    max-height: 400px;
    overflow-y: auto;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.loading {
    animation: pulse 1.5s infinite;
}
"""
        
        css_path = os.path.join(self.static_dir, 'style.css')
        if not os.path.exists(css_path):
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
        
        # Create default JavaScript
        js_content = """
// BongoCat Web Interface JavaScript

class BongoCatUI {
    constructor() {
        this.socket = io();
        this.initializeEventListeners();
        this.connectWebSocket();
    }
    
    initializeEventListeners() {
        // Scraper form submission
        const scraperForm = document.getElementById('scraper-form');
        if (scraperForm) {
            scraperForm.addEventListener('submit', this.handleScraperSubmit.bind(this));
        }
        
        // Export buttons
        const exportButtons = document.querySelectorAll('.export-btn');
        exportButtons.forEach(btn => {
            btn.addEventListener('click', this.handleExport.bind(this));
        });
    }
    
    connectWebSocket() {
        this.socket.on('connect', () => {
            console.log('Connected to BongoCat server');
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('scraper_update', (data) => {
            this.handleScraperUpdate(data);
        });
        
        this.socket.on('scraper_complete', (data) => {
            this.handleScraperComplete(data);
        });
        
        this.socket.on('status_update', (data) => {
            this.handleStatusUpdate(data);
        });
        
        this.socket.on('log_message', (data) => {
            this.handleLogMessage(data);
        });
    }
    
    updateConnectionStatus(connected) {
        const indicator = document.querySelector('.connection-status');
        if (indicator) {
            indicator.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
            indicator.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }
    
    async handleScraperSubmit(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        
        const payload = {
            url: formData.get('url'),
            options: {
                use_browser: formData.get('use_browser') === 'on',
                wait_time: parseInt(formData.get('wait_time')) || 2,
                selectors: this.parseSelectors(formData.get('selectors'))
            }
        };
        
        try {
            this.showLoading('Starting scrape...');
            
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            this.displayResult(result);
            
        } catch (error) {
            this.showError('Scraping failed: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    parseSelectors(selectorString) {
        if (!selectorString) return {};
        
        try {
            return JSON.parse(selectorString);
        } catch {
            // Parse simple key:selector format
            const selectors = {};
            selectorString.split(',').forEach(pair => {
                const [key, selector] = pair.split(':').map(s => s.trim());
                if (key && selector) {
                    selectors[key] = selector;
                }
            });
            return selectors;
        }
    }
    
    handleScraperUpdate(data) {
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar && data.progress) {
            progressBar.style.width = data.progress + '%';
        }
        
        this.addLogEntry('info', `Scraper update: ${data.message || 'Processing...'}`);
    }
    
    handleScraperComplete(data) {
        this.displayResult({ success: true, result: data.result });
        this.addLogEntry('info', 'Scraping completed successfully');
    }
    
    handleStatusUpdate(data) {
        const statusElements = document.querySelectorAll('[data-status]');
        statusElements.forEach(el => {
            const statusKey = el.dataset.status;
            if (data.data && data.data[statusKey] !== undefined) {
                el.textContent = data.data[statusKey];
            }
        });
    }
    
    handleLogMessage(data) {
        this.addLogEntry(data.level.toLowerCase(), data.message);
    }
    
    addLogEntry(level, message) {
        const logContainer = document.getElementById('log-container');
        if (!logContainer) return;
        
        const entry = document.createElement('div');
        entry.className = `log-entry ${level}`;
        entry.innerHTML = `
            <span class="log-timestamp">${new Date().toLocaleTimeString()}</span>
            <span class="log-level">[${level.toUpperCase()}]</span>
            <span class="log-message">${message}</span>
        `;
        
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Keep only last 100 entries
        while (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }
    
    displayResult(result) {
        const resultContainer = document.getElementById('result-container');
        if (!resultContainer) return;
        
        if (result.success) {
            resultContainer.innerHTML = `
                <h5>Scraping Result</h5>
                <div class="result-display">
                    <pre>${JSON.stringify(result.result, null, 2)}</pre>
                </div>
                <div class="mt-3">
                    <button class="btn btn-primary export-btn" data-format="json">Export JSON</button>
                    <button class="btn btn-secondary export-btn" data-format="csv">Export CSV</button>
                </div>
            `;
            
            // Re-attach export listeners
            resultContainer.querySelectorAll('.export-btn').forEach(btn => {
                btn.addEventListener('click', this.handleExport.bind(this));
            });
        } else {
            resultContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Error</h5>
                    <p>${result.error}</p>
                </div>
            `;
        }
    }
    
    async handleExport(event) {
        const format = event.target.dataset.format;
        const resultData = this.getResultData();
        
        if (!resultData) {
            this.showError('No data to export');
            return;
        }
        
        try {
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data: resultData,
                    format: format,
                    filename: `bongocat_export_${Date.now()}.${format}`
                })
            });
            
            const result = await response.json();
            if (result.success) {
                this.showSuccess(`Data exported to ${result.filepath}`);
            } else {
                this.showError('Export failed: ' + result.error);
            }
            
        } catch (error) {
            this.showError('Export failed: ' + error.message);
        }
    }
    
    getResultData() {
        const resultDisplay = document.querySelector('.result-display pre');
        if (!resultDisplay) return null;
        
        try {
            return JSON.parse(resultDisplay.textContent);
        } catch {
            return null;
        }
    }
    
    showLoading(message = 'Loading...') {
        this.showAlert('info', message, 'loading-alert');
    }
    
    hideLoading() {
        const alert = document.getElementById('loading-alert');
        if (alert) alert.remove();
    }
    
    showSuccess(message) {
        this.showAlert('success', message);
    }
    
    showError(message) {
        this.showAlert('danger', message);
    }
    
    showAlert(type, message, id = null) {
        const alertContainer = document.getElementById('alert-container') || document.body;
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        if (id) alert.id = id;
        
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.bongoCatUI = new BongoCatUI();
});
"""
        
        js_path = os.path.join(self.static_dir, 'app.js')
        if not os.path.exists(js_path):
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content)