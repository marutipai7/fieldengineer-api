from typing import Dict, Set

from fastapi import WebSocket


class WebSocketManager:
    """
    Manages active WebSocket connections per user.

    Supports multiple connections for the same user.
    """

    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
    ) -> None:
        """
        Accept and register a WebSocket connection.
        """

        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)

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
            return

        dead_connections = []

        for websocket in list(self.active_connections[user_id]):
            try:
                await websocket.send_json(payload)

            except Exception:
                dead_connections.append(websocket)

        for websocket in dead_connections:
            self.active_connections[user_id].discard(websocket)

        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

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