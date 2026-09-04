import enum
import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.profile.models import User


class NotificationDisplayType(str, enum.Enum):
    """Enum for notification display type/category."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROMOTION = "promotion"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    notification_type = Column(
        String(50),
        nullable=False,
    )

    entity_type = Column(
        String(50),
        nullable=True,
    )

    entity_id = Column(
        Integer,
        nullable=True,
    )

    type = Column(
        String(50),
        default="info",
        nullable=False,
    )

    notification_metadata = Column(
        JSONB,
        default=dict,
        nullable=False,
    )

    is_read = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "idx_notifications_user_is_read",
            "user_id",
            "is_read",
        ),
        Index(
            "idx_notifications_user_created_at",
            "user_id",
            created_at.desc(),
        ),
        Index(
            "idx_notifications_user_type",
            "user_id",
            "notification_type",
        ),
        CheckConstraint(
            "type IN ('info', 'success', 'warning', 'error', 'promotion')",
            name="ck_notification_type",
        ),
    )

    def to_dict(self) -> dict:
        """Serialize notification to dict for WebSocket/JSON delivery."""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "type": (
                self.type
                if isinstance(self.type, str)
                else (self.type.value if self.type else "info")
            ),
            "metadata": self.notification_metadata or {},
            "is_read": self.is_read,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }


class FCMDeviceToken(Base):
    __tablename__ = "fcm_device_tokens"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    token = Column(
        Text,
        nullable=False,
        unique=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User")

    __table_args__ = (
        Index(
            "idx_fcm_device_tokens_user_id",
            "user_id",
        ),
    )
class NotificationPreferences(Base):
    __tablename__ = "notification_preferences"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ALL
    all_priority_jobs = Column(Boolean, default=True, nullable=False)
    all_new_job_requests = Column(Boolean, default=True, nullable=False)
    all_job_assigned = Column(Boolean, default=True, nullable=False)
    all_job_reminders = Column(Boolean, default=True, nullable=False)
    all_job_updates = Column(Boolean, default=True, nullable=False)
    all_chat_messages = Column(Boolean, default=True, nullable=False)
    all_missed_messages_reminder = Column(Boolean, default=True, nullable=False)
    all_payment_received = Column(Boolean, default=True, nullable=False)
    all_payout_updates = Column(Boolean, default=True, nullable=False)
    all_app_updates = Column(Boolean, default=True, nullable=False)
    all_maintenance_alerts = Column(Boolean, default=True, nullable=False)

    # Bookings
    booking_new_job_requests = Column(Boolean, default=True, nullable=False)
    booking_job_assigned = Column(Boolean, default=True, nullable=False)
    booking_job_reminders = Column(Boolean, default=True, nullable=False)
    booking_job_updates = Column(Boolean, default=True, nullable=False)

    # Engineer
    engineer_priority_jobs = Column(Boolean, default=True, nullable=False)
    engineer_job_assigned = Column(Boolean, default=True, nullable=False)
    engineer_job_updates = Column(Boolean, default=True, nullable=False)

    # Communication
    communication_chat_messages = Column(Boolean, default=True, nullable=False)
    communication_missed_messages_reminder = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User")