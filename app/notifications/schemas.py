from datetime import datetime
<<<<<<< HEAD
from typing import Any
=======
from enum import Enum
from typing import Optional
from uuid import UUID
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6

from pydantic import BaseModel, ConfigDict, Field


<<<<<<< HEAD
class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str

    notification_type: str

    entity_type: str | None = None
    entity_id: int | None = None

    type: str = "info"

    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: int
    title: str
    message: str

    notification_type: str

    entity_type: str | None = None
    entity_id: int | None = None

    type: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    is_read: bool
    created_at: datetime | None = None
=======
class NotificationType(str, Enum):
    """Enum for notification types."""

    BID_RECEIVED = "bid_received"
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_REMINDER = "appointment_reminder"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    ORDER_PLACED = "order_placed"
    ORDER_DISPATCHED = "order_dispatched"
    ORDER_DELIVERED = "order_delivered"
    RATING_RECEIVED = "rating_received"
    COUPON_NEW = "coupon_new"
    SYSTEM_ALERT = "system_alert"
    REVIEW_RECEIVED = "review_received"


class NotificationDisplayType(str, Enum):
    """Enum for notification display type/category."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROMOTION = "promotion"


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""

    user_id: int
    title: str
    message: str
    notification_type: NotificationType
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    type: NotificationDisplayType = NotificationDisplayType.INFO
    metadata: dict = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    user_id: int
    title: str
    message: str
    notification_type: NotificationType
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    type: NotificationDisplayType = NotificationDisplayType.INFO
    notification_metadata: dict = Field(default_factory=dict)
    is_read: bool
    created_at: datetime | None = None


class NotificationUpdate(BaseModel):
    """Schema for updating notification (e.g., marking as read)."""

    is_read: Optional[bool] = None


class UnreadCountResponse(BaseModel):
    """Schema for unread count response."""

    unread_count: int


class FCMTokenRequest(BaseModel):
    """Schema for saving/updating FCM token."""

    fcm_token: str


class FCMTokenResponse(BaseModel):
    """Schema for FCM token response."""

    success: bool
    message: str
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
