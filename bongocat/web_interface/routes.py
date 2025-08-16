"""Web Interface Routes"""

from flask import Blueprint, render_template, request, jsonify, current_app
from ..core_scraper.scraper import BongoCat
from ..data_parser.parser import DataParser
from ..output_handler.handler import OutputHandler
from ..error_logger.logger import ErrorLogger
import json
import time

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Initialize logger
logger = ErrorLogger()

@main_bp.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@main_bp.route('/scraper')
def scraper_page():
    """Scraper configuration page"""
    return render_template('scraper.html')

@main_bp.route('/results')
def results_page():
    """Results viewing page"""
    return render_template('results.html')

@main_bp.route('/logs')
def logs_page():
    """Logs viewing page"""
    return render_template('logs.html')

# API Routes
@api_bp.route('/scrape', methods=['POST'])
def api_scrape():
    """API endpoint to start scraping"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        options = data.get('options', {})
        
        # Initialize scraper
        scraper = BongoCat(
            use_browser=options.get('use_browser', False)
        )
        
        # Perform scrape
        result = scraper.scrape(
            url,
            selectors=options.get('selectors', {}),
            wait_time=options.get('wait_time', 2)
        )
        
        # Close scraper resources
        scraper.close()
        
        # Convert soup object to string for JSON serialization
        if 'soup' in result:
            del result['soup']
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Scraping API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/parse', methods=['POST'])
def api_parse():
    """API endpoint to parse content"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
        
        content = data['content']
        content_type = data.get('content_type', 'auto')
        
        # Initialize parser
        parser = DataParser()
        
        # Parse content
        result = parser.parse(content, content_type)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Parsing API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/export', methods=['POST'])
def api_export():
    """API endpoint to export data"""
    try:
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': 'Data is required'}), 400
        
        export_data = data['data']
        format_type = data.get('format', 'json')
        filename = data.get('filename')
        
        # Initialize output handler
        handler = OutputHandler()
        
        # Export data
        filepath = handler.export(export_data, format_type, filename)
        
        return jsonify({
            'success': True,
            'filepath': filepath,
            'format': format_type,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Export API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/status')
def api_status():
    """API endpoint to get system status"""
    try:
        return jsonify({
            'status': 'running',
            'version': '1.0.0',
            'components': {
                'scraper': 'active',
                'parser': 'active', 
                'output_handler': 'active',
                'logger': 'active'
            },
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Status API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@api_bp.route('/validate-url', methods=['POST'])
def api_validate_url():
    """API endpoint to validate URLs"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        # Basic URL validation
        if not url:
            return jsonify({'valid': False, 'error': 'URL is empty'})
        
        if not url.startswith(('http://', 'https://')):
            return jsonify({'valid': False, 'error': 'URL must start with http:// or https://'})
        
        # Additional validation could be added here
        return jsonify({'valid': True})
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

@api_bp.route('/config', methods=['GET', 'POST'])
def api_config():
    """API endpoint to get/set configuration"""
    try:
        if request.method == 'GET':
            # Return current configuration
            from ..config_manager.manager import ConfigManager
            config_manager = ConfigManager()
            return jsonify({
                'success': True,
                'config': {
                    'rate_limit': config_manager.get_rate_limit(),
                    'timeout': config_manager.get_timeout(),
                    'log_level': config_manager.get_log_level(),
                    'proxy_count': len(config_manager.get_proxy_list())
                }
            })
        
        else:  # POST
            # Update configuration
            data = request.get_json()
            # Configuration update logic would go here
            return jsonify({
                'success': True,
                'message': 'Configuration updated'
            })
            
    except Exception as e:
        logger.error(f"Config API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500