"""Web Interface - User-friendly web dashboard for BongoCat"""

from .app import create_app
from .routes import main_bp, api_bp
from .templates import TemplateRenderer
from .static_handler import StaticHandler
from .dashboard import Dashboard
from .websocket_handler import WebSocketHandler

__all__ = [
    "create_app",
    "main_bp",
    "api_bp",
    "TemplateRenderer", 
    "StaticHandler",
    "Dashboard",
    "WebSocketHandler"
]