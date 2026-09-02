import logging
from uuid import UUID

import jwt
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.notifications.models import Notification
from app.notifications.schemas import (
    FCMTokenRequest,
    FCMTokenResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.notifications.service import NotificationService
from app.notifications.websocket_manager import ws_manager
from app.profile.models import User
from app.utils.auth_utils import (
    check_authorization_key,
    get_current_user_object,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)

ws_router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    user_id = None

    try:
        # -------------------------
        # Validate token before accepting
        # -------------------------
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            email = payload.get("sub")

            if not email:
                await websocket.accept()
                await websocket.close(
                    code=1008,
                    reason="Invalid token: no email",
                )
                logger.warning("WebSocket auth failed: no email in token")
                return

        except jwt.InvalidTokenError as exc:
            await websocket.accept()
            await websocket.close(
                code=1008,
                reason="Invalid token",
            )
            logger.warning(f"WebSocket auth failed: {exc}")
            return

        # -------------------------
        # Get user from database
        # -------------------------
        db: Session = next(get_db())
        try:
            user = db.query(User).filter(User.email == email).first()

            if not user:
                await websocket.accept()
                await websocket.close(
                    code=1008,
                    reason="User not found",
                )
                logger.warning(
                    f"WebSocket auth failed: user not found for email {email}"
                )
                return

            user_id = user.id

        finally:
            db.close()

        logger.info(
            f"WebSocket user authenticated: email={email}, user_id={user_id}"
        )

        # -------------------------
        # Accept WebSocket and add to manager
        # -------------------------
        await ws_manager.connect(user_id, websocket)
        logger.info(f"WebSocket connected: user_id={user_id}")

        # -------------------------
        # Keep socket alive and handle messages
        # -------------------------
        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received from {user_id}: {data}")

                if data == "ping":
                    await websocket.send_text("pong")

            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: user_id={user_id}")

    except Exception as exc:
        logger.exception(f"WebSocket error for user {user_id}: {exc}")

    finally:
        if user_id is not None:
            await ws_manager.disconnect(user_id, websocket)


# ============================================================================
# REST Endpoints
# ============================================================================

@router.get(
    "/",
    response_model=list[NotificationResponse],
)
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    filter_type: str = Query(
        "all",
        pattern="^(all|unread|bidding)$",
    ),
    db: Session = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user=Depends(get_current_user_object),
):
    user, _ = current_user

    query = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
    )

    if filter_type == "unread":
        query = query.filter(
            Notification.is_read.is_(False)
        )

    elif filter_type == "bidding":
        query = query.filter(
            Notification.notification_type == "bid_received"
        )

    return (
        query
        .order_by(desc(Notification.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


# @router.post(
#     "/fcm-token",
#     response_model=FCMTokenResponse,
# )
# async def save_fcm_token(
#     request: FCMTokenRequest,
#     db: Session = Depends(get_db),
#     _auth=Depends(check_authorization_key),
#     current_user=Depends(get_current_user_object),
# ):
#     user, _ = current_user

#     await NotificationService.save_fcm_token(
#         db=db,
#         user_id=user.id,
#         fcm_token=request.fcm_token,
#     )

#     return FCMTokenResponse(
#         success=True,
#         message="FCM token saved successfully.",
#     )

# @router.post("/test-push")
# async def test_push_notification(
#     db: Session = Depends(get_db),
#     _auth=Depends(check_authorization_key),
#     current_user=Depends(get_current_user_object),
# ):
#     user, _ = current_user

#     success = await NotificationService.send_push_notification(
#         db=db,
#         user_id=user.id,
#         title="FCM Test",
#         body="Hello from Backend 🚀",
#         data={
#             "type": "test",
#             "screen": "home",
#         },
#     )

#     return {
#         "success": success,
#     }

# @router.get(
#     "/unread-count",
#     response_model=UnreadCountResponse,
# )
# def get_unread_count(
#     db: Session = Depends(get_db),
#     _auth=Depends(check_authorization_key),
#     current_user=Depends(get_current_user_object),
# ):
#     user, _ = current_user

#     count = (
#         db.query(func.count(Notification.id))
#         .filter(
#             Notification.user_id == user.id,
#             Notification.is_read.is_(False),
#         )
#         .scalar()
#     ) or 0

#     return UnreadCountResponse(
#         unread_count=count,
#     )


# @router.put("/{notification_id:uuid}/read")
# def mark_notification_as_read(
#     notification_id: UUID,
#     db: Session = Depends(get_db),
#     _auth=Depends(check_authorization_key),
#     current_user=Depends(get_current_user_object),
# ):
#     user, _ = current_user

#     notification = (
#         db.query(Notification)
#         .filter(Notification.id == notification_id)
#         .first()
#     )

#     if not notification:
#         raise HTTPException(
#             status_code=404,
#             detail="Notification not found",
#         )

#     if notification.user_id != user.id:
#         raise HTTPException(
#             status_code=403,
#             detail="Not authorized",
#         )

#     notification.is_read = True

#     db.commit()

#     logger.info(
#         f"Notification marked as read: {notification_id}"
#     )

#     return {
#         "success": True,
#         "message": "Marked as read",
#     }


# @router.delete("/{notification_id:uuid}")
# def delete_notification(
#     notification_id: UUID,
#     db: Session = Depends(get_db),
#     _auth=Depends(check_authorization_key),
#     current_user=Depends(get_current_user_object),
# ):
#     user, _ = current_user

#     notification = (
#         db.query(Notification)
#         .filter(Notification.id == notification_id)
#         .first()
#     )

#     if not notification:
#         raise HTTPException(
#             status_code=404,
#             detail="Notification not found",
#         )

#     if notification.user_id != user.id:
#         raise HTTPException(
#             status_code=403,
#             detail="Not authorized",
#         )

#     db.delete(notification)
#     db.commit()

#     logger.info(
#         f"Notification deleted: {notification_id}"
#     )

#     return {
#         "success": True,
#         "message": "Deleted",
#     }


# @router.put("/{notification_id}/read-batch")
# def mark_as_read_batch(
#     notification_ids: list[str] = Query(...),
#     db: Session = Depends(get_db),
#     _auth=Depends(check_authorization_key),
#     current_user=Depends(get_current_user_object),
# ):
#     user, _ = current_user

#     notifications = (
#         db.query(Notification)
#         .filter(
#             Notification.id.in_(notification_ids),
#             Notification.user_id == user.id,
#         )
#         .all()
#     )

#     if not notifications:
#         raise HTTPException(
#             status_code=404,
#             detail="No notifications found",
#         )

#     for notification in notifications:
#         notification.is_read = True

#     db.commit()

#     logger.info(
#         f"{len(notifications)} notifications marked as read"
#     )

#     return {
#         "success": True,
#         "message": (
#             f"Updated {len(notifications)} notifications"
#         ),
#         "count": len(notifications),
#     }