import json
import redis

from sqlalchemy.orm import Session

from app.core.config import settings
from app.notifications.models import Notification


redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def create_notification(
    *,
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    db: Session,
    entity_type: str | None = None,
    entity_id: int | None = None,
    notification_type_display: str = "info",
    metadata: dict | None = None,
) -> Notification:
    """
    Central notification creator.

    Creates and stores an in-app notification
    for a specific user.
    """

    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        entity_type=entity_type,
        entity_id=entity_id,
        type=notification_type_display,
        notification_metadata=metadata or {},
    )

    # db.add(notification)
    # db.commit()
    # db.refresh(notification)

    # return notification


    db.add(notification)
    db.commit()
    db.refresh(notification)

    payload = {
       "id": str(notification.id),
        "user_id": notification.user_id,
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "entity_type": notification.entity_type,
        "entity_id": notification.entity_id,
        "type": notification.type,
        "metadata": notification.notification_metadata or {},
        "is_read": notification.is_read,
        "created_at": (
            notification.created_at.isoformat()
            if notification.created_at
            else None
        ),
    }

    redis_client.publish(
        "notifications",
        json.dumps(payload),
    )

    return notification