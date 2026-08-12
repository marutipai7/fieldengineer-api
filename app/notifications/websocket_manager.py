"""
WebSocket Connection Manager

Maintains in-memory tracking of active WebSocket connections.
Supports multiple connections per user.
Thread-safe for async operations.
"""

from fastapi import WebSocket
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages active WebSocket connections per user.
    
    Features:
    - Multiple connections per user (multi-device support)
    - Send to specific user
    - Auto-cleanup on connection failure
    - Async-safe
    """

    def __init__(self):
        # Dict[user_id, Set[WebSocket]]
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self._lock = None  # For potential future async locking if needed

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        """
        Register a new WebSocket connection for a user.
        
        Args:
            user_id: User ID
            websocket: WebSocket connection object
        """
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info(f"✓ WebSocket connected: user_id={user_id}, total={len(self.active_connections[user_id])}")

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection for a user.
        
        Args:
            user_id: User ID
            websocket: WebSocket connection object
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Clean up empty user sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            logger.info(f"✓ WebSocket disconnected: user_id={user_id}")

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        """
        Send a message to all active connections of a user.
        Silently ignores if user has no active connections.
        Removes dead connections automatically.
        
        Args:
            user_id: User ID
            payload: Dict to send as JSON
        """
        if user_id not in self.active_connections:
            # User not connected; will be queued via Redis persistence
            logger.debug(f"User {user_id} not connected; notification will be queued")
            return

        # Collect dead connections to remove
        dead_connections = []
        
        for websocket in list(self.active_connections[user_id]):
            try:
                await websocket.send_json(payload)
                logger.debug(f"✓ Message sent to user {user_id}")
            except Exception as exc:
                logger.warning(f"Failed to send message to user {user_id}: {exc}")
                dead_connections.append(websocket)
        
        # Remove dead connections
        for ws in dead_connections:
            self.active_connections[user_id].discard(ws)
        
        # Clean up empty user set
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    def get_connected_users(self) -> list:
        """For monitoring/debugging: return list of connected user IDs"""
        return list(self.active_connections.keys())

    def get_connection_count(self, user_id: int) -> int:
        """Get number of active connections for a user"""
        return len(self.active_connections.get(user_id, set()))


# Global instance
ws_manager = WebSocketManager()

