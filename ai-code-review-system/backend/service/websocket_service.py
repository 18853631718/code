from flask_socketio import emit, join_room, leave_room
from flask import request
import json

class WebSocketService:
    def __init__(self):
        self.connected_users = {}
        self.active_sessions = {}
    
    def handle_connect(self):
        print(f"Client connected: {request.sid}")
        emit('connected', {'message': 'Connected to server'})
    
    def handle_disconnect(self):
        print(f"Client disconnected: {request.sid}")
        for session_id, users in self.connected_users.items():
            if request.sid in users:
                users.remove(request.sid)
                self._broadcast_user_list(session_id)
    
    def handle_join_session(self, data):
        session_id = data.get('session_id')
        username = data.get('username')
        
        join_room(session_id)
        
        if session_id not in self.connected_users:
            self.connected_users[session_id] = []
        
        self.connected_users[session_id].append({
            'sid': request.sid,
            'username': username
        })
        
        emit('user_joined', {
            'username': username,
            'users': self._get_session_users(session_id)
        }, room=session_id)
        
        self._broadcast_user_list(session_id)
    
    def handle_leave_session(self, data):
        session_id = data.get('session_id')
        username = data.get('username')
        
        leave_room(session_id)
        
        if session_id in self.connected_users:
            self.connected_users[session_id] = [
                u for u in self.connected_users[session_id] 
                if u['sid'] != request.sid
            ]
        
        emit('user_left', {
            'username': username,
            'users': self._get_session_users(session_id)
        }, room=session_id)
    
    def handle_code_change(self, data):
        session_id = data.get('session_id')
        code = data.get('code')
        username = data.get('username')
        
        emit('code_updated', {
            'code': code,
            'username': username
        }, room=session_id, include_self=False)
    
    def handle_cursor_position(self, data):
        session_id = data.get('session_id')
        position = data.get('position')
        username = data.get('username')
        
        emit('cursor_moved', {
            'username': username,
            'position': position
        }, room=session_id, include_self=False)
    
    def handle_comment_added(self, data):
        session_id = data.get('session_id')
        comment = data.get('comment')
        
        emit('comment_added', comment, room=session_id, include_self=False)
    
    def handle_analysis_update(self, data):
        session_id = data.get('session_id')
        analysis_result = data.get('result')
        
        emit('analysis_updated', analysis_result, room=session_id)
    
    def _get_session_users(self, session_id):
        if session_id in self.connected_users:
            return [u['username'] for u in self.connected_users[session_id]]
        return []
    
    def _broadcast_user_list(self, session_id):
        emit('user_list', {
            'users': self._get_session_users(session_id)
        }, room=session_id)


websocket_service = WebSocketService()

def socket_handlers(socketio):
    
    @socketio.on('connect')
    def handle_connect():
        websocket_service.handle_connect()
    
    @socketio.on('disconnect')
    def handle_disconnect():
        websocket_service.handle_disconnect()
    
    @socketio.on('join_session')
    def handle_join_session(data):
        websocket_service.handle_join_session(data)
    
    @socketio.on('leave_session')
    def handle_leave_session(data):
        websocket_service.handle_leave_session(data)
    
    @socketio.on('code_change')
    def handle_code_change(data):
        websocket_service.handle_code_change(data)
    
    @socketio.on('cursor_position')
    def handle_cursor_position(data):
        websocket_service.handle_cursor_position(data)
    
    @socketio.on('comment_added')
    def handle_comment_added(data):
        websocket_service.handle_comment_added(data)
    
    @socketio.on('analysis_update')
    def handle_analysis_update(data):
        websocket_service.handle_analysis_update(data)
