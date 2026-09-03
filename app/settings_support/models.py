from sqlalchemy import Column, Integer, Boolean, ForeignKey
from app.core.database import Base
from sqlalchemy.dialects.postgresql import JSONB

class UserPermission(Base):
    __tablename__ = "user_permissions"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    location = Column(Boolean, nullable=False, default=False)
    communication = Column(Boolean, nullable=False, default=False)
    notifications = Column(Boolean, nullable=False, default=False)
    camera = Column(Boolean, nullable=False, default=False)
    media = Column(Boolean, nullable=False, default=False)
    audio = Column(Boolean, nullable=False, default=False)
    payment = Column(Boolean, nullable=False, default=False)
    security = Column(Boolean, nullable=False, default=False)
    network = Column(Boolean, nullable=False, default=False)
    device = Column(Boolean, nullable=False, default=False)

class UserNotificationPreference(Base):
    __tablename__ = "user_notification_preferences"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Main notification switch
    enable_notification = Column(Boolean, nullable=False, default=True)

    # Notification channels
    push_notification = Column(Boolean, nullable=False, default=True)
    sms_notification = Column(Boolean, nullable=False, default=True)
    email_notification = Column(Boolean, nullable=False, default=True)

    # Push notification preferences
    push_priority_jobs = Column(Boolean, nullable=False, default=True)
    push_new_job_requests = Column(Boolean, nullable=False, default=True)
    push_job_assigned = Column(Boolean, nullable=False, default=True)
    push_job_reminders = Column(Boolean, nullable=False, default=True)
    push_job_updates = Column(Boolean, nullable=False, default=True)
    push_chat_messages = Column(Boolean, nullable=False, default=True)
    push_missed_messages_reminder = Column(Boolean, nullable=False, default=True)
    push_payment_received = Column(Boolean, nullable=False, default=True)
    push_payout_updates = Column(Boolean, nullable=False, default=True)
    push_app_updates = Column(Boolean, nullable=False, default=True)
    push_maintenance_alerts = Column(Boolean, nullable=False, default=True)

    # SMS notification preferences
    sms_priority_jobs = Column(Boolean, nullable=False, default=True)
    sms_new_job_requests = Column(Boolean, nullable=False, default=True)
    sms_job_assigned = Column(Boolean, nullable=False, default=True)
    sms_job_reminders = Column(Boolean, nullable=False, default=True)
    sms_job_updates = Column(Boolean, nullable=False, default=True)
    sms_chat_messages = Column(Boolean, nullable=False, default=True)
    sms_missed_messages_reminder = Column(Boolean, nullable=False, default=True)
    sms_payment_received = Column(Boolean, nullable=False, default=True)
    sms_payout_updates = Column(Boolean, nullable=False, default=True)
    sms_app_updates = Column(Boolean, nullable=False, default=True)
    sms_maintenance_alerts = Column(Boolean, nullable=False, default=True)

    # Email notification preferences
    email_priority_jobs = Column(Boolean, nullable=False, default=True)
    email_new_job_requests = Column(Boolean, nullable=False, default=True)
    email_job_assigned = Column(Boolean, nullable=False, default=True)
    email_job_reminders = Column(Boolean, nullable=False, default=True)
    email_job_updates = Column(Boolean, nullable=False, default=True)
    email_chat_messages = Column(Boolean, nullable=False, default=True)
    email_missed_messages_reminder = Column(Boolean, nullable=False, default=True)
    email_payment_received = Column(Boolean, nullable=False, default=True)
    email_payout_updates = Column(Boolean, nullable=False, default=True)
    email_app_updates = Column(Boolean, nullable=False, default=True)
    email_maintenance_alerts = Column(Boolean, nullable=False, default=True)