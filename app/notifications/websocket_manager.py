<<<<<<< HEAD
=======
"""
WebSocket Connection Manager

Maintains in-memory tracking of active WebSocket connections.
Supports multiple connections per user.
Thread-safe for async operations.
"""

import logging
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
from typing import Dict, Set

from fastapi import WebSocket

<<<<<<< HEAD
=======
logger = logging.getLogger(__name__)

>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6

class WebSocketManager:
    """
    Manages active WebSocket connections per user.

<<<<<<< HEAD
    Supports multiple connections for the same user.
=======
    Features:
    - Multiple connections per user (multi-device support)
    - Send to specific user
    - Auto-cleanup on connection failure
    - Async-safe
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
    """

    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
<<<<<<< HEAD

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
    ) -> None:
        """
        Accept and register a WebSocket connection.
        """

=======
        self._lock = None

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        """Register a new WebSocket connection for a user."""
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
<<<<<<< HEAD

    async def disconnect(
        self,
        user_id: int,
        websocket: WebSocket,
    ) -> None:
        """
        Remove a WebSocket connection.
        """

        if user_id not in self.active_connections:
            return

        self.active_connections[user_id].discard(websocket)

        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_to_user(
        self,
        user_id: int,
        payload: dict,
    ) -> None:
        """
        Send notification to all active connections
        belonging to the user.
        """

        if user_id not in self.active_connections:
=======
        logger.info(
            f"WebSocket connected: user_id={user_id}, total={len(self.active_connections[user_id])}"
        )

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        """Remove a WebSocket connection for a user."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

            logger.info(f"WebSocket disconnected: user_id={user_id}")

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        """Send a message to all active connections of a user."""
        if user_id not in self.active_connections:
            logger.debug(f"User {user_id} not connected; notification will be queued")
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
            return

        dead_connections = []

        for websocket in list(self.active_connections[user_id]):
            try:
                await websocket.send_json(payload)
<<<<<<< HEAD

            except Exception:
                dead_connections.append(websocket)

        for websocket in dead_connections:
            self.active_connections[user_id].discard(websocket)
=======
                logger.debug(f"Message sent to user {user_id}")
            except Exception as exc:
                logger.warning(f"Failed to send message to user {user_id}: {exc}")
                dead_connections.append(websocket)

        for ws in dead_connections:
            self.active_connections[user_id].discard(ws)
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6

        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

<<<<<<< HEAD
    def get_connected_users(self) -> list[int]:
        """
        Return IDs of users currently connected.
        """

        return list(self.active_connections.keys())

    def get_connection_count(self, user_id: int) -> int:
        """
        Return number of active connections for a user.
        """

        return len(
            self.active_connections.get(user_id, set())
        )


ws_manager = WebSocketManager()
=======
    def get_connected_users(self) -> list:
        """Return list of connected user IDs."""
        return list(self.active_connections.keys())

    def get_connection_count(self, user_id: int) -> int:
        """Get number of active connections for a user."""
        return len(self.active_connections.get(user_id, set()))


ws_manager = WebSocketManager()
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
