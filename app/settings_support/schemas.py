from pydantic import BaseModel
from typing import Optional


class PermissionUpdateSchema(BaseModel):
    location: Optional[bool] = None
    communication: Optional[bool] = None
    notifications: Optional[bool] = None
    camera: Optional[bool] = None
    media: Optional[bool] = None
    audio: Optional[bool] = None
    payment: Optional[bool] = None
    security: Optional[bool] = None
    network: Optional[bool] = None
    device: Optional[bool] = None

class NotificationChannelPreferences(BaseModel):
    priority_jobs: Optional[bool] = None
    new_job_requests: Optional[bool] = None
    job_assigned: Optional[bool] = None
    job_reminders: Optional[bool] = None
    job_updates: Optional[bool] = None
    chat_messages: Optional[bool] = None
    missed_messages_reminder: Optional[bool] = None
    payment_received: Optional[bool] = None
    payout_updates: Optional[bool] = None
    app_updates: Optional[bool] = None
    maintenance_alerts: Optional[bool] = None


class NotificationPreferencesUpdate(BaseModel):
    enable_notification: Optional[bool] = None
    push_notification: Optional[bool] = None
    sms_notification: Optional[bool] = None
    email_notification: Optional[bool] = None
    push_preferences: Optional[NotificationChannelPreferences] = None
    sms_preferences: Optional[NotificationChannelPreferences] = None
    email_preferences: Optional[NotificationChannelPreferences] = None

class NotificationPreferencesResponse(BaseModel):
    success: bool
    message: str
    data: dict