"""WebSocket Handler - Real-time communication with web interface"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from typing import Dict, Any
import time


class WebSocketHandler:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.connected_clients = {}
        self.active_scrapers = {}
    
    def register_events(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.sid
            self.connected_clients[client_id] = {
                'connected_at': time.time(),
                'active': True
            }
            
            emit('status', {
                'connected': True,
                'server_status': 'running',
                'timestamp': time.time()
            })
            
            print(f"Client {client_id} connected")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.sid
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
            
            print(f"Client {client_id} disconnected")
        
        @self.socketio.on('join_scraper_room')
        def handle_join_scraper_room(data):
            """Join room for scraper updates"""
            scraper_id = data.get('scraper_id')
            if scraper_id:
                join_room(f"scraper_{scraper_id}")
                emit('joined_room', {
                    'room': f"scraper_{scraper_id}",
                    'timestamp': time.time()
                })
        
        @self.socketio.on('leave_scraper_room')
        def handle_leave_scraper_room(data):
            """Leave scraper room"""
            scraper_id = data.get('scraper_id')
            if scraper_id:
                leave_room(f"scraper_{scraper_id}")
                emit('left_room', {
                    'room': f"scraper_{scraper_id}",
                    'timestamp': time.time()
                })
        
        @self.socketio.on('get_status')
        def handle_get_status():
            """Get current system status"""
            emit('status_update', {
                'connected_clients': len(self.connected_clients),
                'active_scrapers': len(self.active_scrapers),
                'server_uptime': time.time(),
                'timestamp': time.time()
            })
    
    def broadcast_scraper_update(self, scraper_id: str, update_data: Dict[str, Any]):
        """Broadcast scraper progress update"""
        self.socketio.emit('scraper_update', {
            'scraper_id': scraper_id,
            'data': update_data,
            'timestamp': time.time()
        }, room=f"scraper_{scraper_id}")
    
    def broadcast_status_update(self, status_data: Dict[str, Any]):
        """Broadcast general status update to all clients"""
        self.socketio.emit('status_update', {
            'data': status_data,
            'timestamp': time.time()
        })
    
    def broadcast_log_message(self, log_data: Dict[str, Any]):
        """Broadcast log message to clients"""
        self.socketio.emit('log_message', {
            'level': log_data.get('level'),
            'message': log_data.get('message'),
            'module': log_data.get('module'),
            'timestamp': log_data.get('timestamp', time.time())
        })
    
    def notify_scraper_complete(self, scraper_id: str, result_data: Dict[str, Any]):
        """Notify clients that scraper has completed"""
        self.socketio.emit('scraper_complete', {
            'scraper_id': scraper_id,
            'result': result_data,
            'timestamp': time.time()
        }, room=f"scraper_{scraper_id}")
        
        # Remove from active scrapers
        if scraper_id in self.active_scrapers:
            del self.active_scrapers[scraper_id]
    
    def get_connected_clients_count(self) -> int:
        """Get number of connected clients"""
        return len(self.connected_clients)
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get information about connected clients"""
        return {
            'count': len(self.connected_clients),
            'clients': self.connected_clients.copy(),
            'active_scrapers': len(self.active_scrapers)
        }