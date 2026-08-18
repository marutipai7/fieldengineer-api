from sqlalchemy.ext.asyncio import AsyncSession
from app.notifications.models import Notification


async def create_notification(
    *,
    user_id: int,
    title: str,
    message: str,
    db: AsyncSession,
    reference_type: str | None = None,
    reference_id: int | None = None,
):
    """
    Central notification creator.
    Use for all in-app alerts.
    """

    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        reference_type=reference_type,
        reference_id=reference_id,
    )

    db.add(notification)
    await db.commit()
    await db.refresh(notification)

    return notification
