"""Flask Application Factory with Lazy Loading"""


def create_app(config=None):
    """Create and configure Flask application with lazy imports"""
    # Lazy load Flask and related modules only when creating the app
    from flask import Flask
    from flask_socketio import SocketIO
    from .routes import main_bp, api_bp
    from .websocket_handler import WebSocketHandler
    
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'bongocat-secret-key-change-in-production'
    app.config['DEBUG'] = True
    
    if config:
        app.config.update(config)
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize WebSocket handler
    websocket_handler = WebSocketHandler(socketio)
    websocket_handler.register_events()
    
    # Store socketio instance on app for access elsewhere
    app.socketio = socketio
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app