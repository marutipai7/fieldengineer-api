from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.notifications.websocket_manager import ws_manager


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.websocket("/ws/{user_id}")
async def notification_websocket(
    websocket: WebSocket,
    user_id: int,
):
    
    """
    WebSocket connection for real-time notifications.

    Example:
    ws://127.0.0.1:8000/notifications/ws/5
    """
    print(f"WEBSOCKET ROUTE HIT: user_id={user_id}")
    await ws_manager.connect(
        user_id=user_id,
        websocket=websocket,
    )

    try:
        while True:
            # Keep the connection alive.
            # Notifications are pushed from the server,
            # so the client does not need to send anything.
            await websocket.receive_text()

    except WebSocketDisconnect:
        await ws_manager.disconnect(
            user_id=user_id,
            websocket=websocket,
        )

    except Exception:
        await ws_manager.disconnect(
            user_id=user_id,
            websocket=websocket,
        )