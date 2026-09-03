from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.profile.models import User
from app.settings_support.models import UserNotificationPreference
from app.settings_support.schemas import NotificationPreferencesUpdate
from app.utils.auth_utils import get_current_user_mobile

router = APIRouter(
    prefix="/notifications",
    tags=["Settings & Support"]
)

# ---------------------------------------------------------
# ALL NOTIFICATION PREFERENCE FIELDS
# ---------------------------------------------------------

NOTIFICATION_FIELDS = [
    # Main channels
    "push_notification",
    "sms_notification",
    "email_notification",

    # Push
    "push_priority_jobs",
    "push_new_job_requests",
    "push_job_assigned",
    "push_job_reminders",
    "push_job_updates",
    "push_chat_messages",
    "push_missed_messages_reminder",
    "push_payment_received",
    "push_payout_updates",
    "push_app_updates",
    "push_maintenance_alerts",

    # SMS
    "sms_priority_jobs",
    "sms_new_job_requests",
    "sms_job_assigned",
    "sms_job_reminders",
    "sms_job_updates",
    "sms_chat_messages",
    "sms_missed_messages_reminder",
    "sms_payment_received",
    "sms_payout_updates",
    "sms_app_updates",
    "sms_maintenance_alerts",

    # Email
    "email_priority_jobs",
    "email_new_job_requests",
    "email_job_assigned",
    "email_job_reminders",
    "email_job_updates",
    "email_chat_messages",
    "email_missed_messages_reminder",
    "email_payment_received",
    "email_payout_updates",
    "email_app_updates",
    "email_maintenance_alerts",
]

# GET OR CREATE PREFERENCES
def get_or_create_notification_preferences(
    user_id: int,
    db: Session,
):
    preferences = (
        db.query(UserNotificationPreference)
        .filter(
            UserNotificationPreference.user_id == user_id
        )
        .first()
    )
    if not preferences:
        preferences = UserNotificationPreference(
            user_id=user_id
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    return preferences

# CONVERT DB DATA TO API RESPONSE

def preferences_to_dict(preferences):

    return {
        "enable_notification": preferences.enable_notification,

        "push_notification": preferences.push_notification,
        "sms_notification": preferences.sms_notification,
        "email_notification": preferences.email_notification,

        "push_preferences": {
            "priority_jobs": preferences.push_priority_jobs,
            "new_job_requests": preferences.push_new_job_requests,
            "job_assigned": preferences.push_job_assigned,
            "job_reminders": preferences.push_job_reminders,
            "job_updates": preferences.push_job_updates,
            "chat_messages": preferences.push_chat_messages,
            "missed_messages_reminder": (
                preferences.push_missed_messages_reminder
            ),
            "payment_received": preferences.push_payment_received,
            "payout_updates": preferences.push_payout_updates,
            "app_updates": preferences.push_app_updates,
            "maintenance_alerts": preferences.push_maintenance_alerts,
        },

        "sms_preferences": {
            "priority_jobs": preferences.sms_priority_jobs,
            "new_job_requests": preferences.sms_new_job_requests,
            "job_assigned": preferences.sms_job_assigned,
            "job_reminders": preferences.sms_job_reminders,
            "job_updates": preferences.sms_job_updates,
            "chat_messages": preferences.sms_chat_messages,
            "missed_messages_reminder": (
                preferences.sms_missed_messages_reminder
            ),
            "payment_received": preferences.sms_payment_received,
            "payout_updates": preferences.sms_payout_updates,
            "app_updates": preferences.sms_app_updates,
            "maintenance_alerts": preferences.sms_maintenance_alerts,
        },

        "email_preferences": {
            "priority_jobs": preferences.email_priority_jobs,
            "new_job_requests": preferences.email_new_job_requests,
            "job_assigned": preferences.email_job_assigned,
            "job_reminders": preferences.email_job_reminders,
            "job_updates": preferences.email_job_updates,
            "chat_messages": preferences.email_chat_messages,
            "missed_messages_reminder": (
                preferences.email_missed_messages_reminder
            ),
            "payment_received": preferences.email_payment_received,
            "payout_updates": preferences.email_payout_updates,
            "app_updates": preferences.email_app_updates,
            "maintenance_alerts": preferences.email_maintenance_alerts,
        },
    }

# SET ALL NOTIFICATIONS

def set_all_notifications(
    preferences,
    value: bool,
):
    """
    Master notification switch.

    If Enable Notification = False:
        Everything becomes False.

    If Enable Notification = True:
        Everything becomes True.
    """

    for field in NOTIFICATION_FIELDS:
        setattr(preferences, field, value)

@router.get("")
async def get_notification_preferences(
    current_user_mobile: str = Depends(
        get_current_user_mobile
    ),
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(
            User.mobile_number == current_user_mobile
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    preferences = get_or_create_notification_preferences(
        user.id,
        db,
    )

    return {
        "success": True,
        "message": "Notification preferences fetched successfully",
        "data": preferences_to_dict(preferences),
    }


@router.put("")
async def update_notification_preferences(
    payload: NotificationPreferencesUpdate,
    current_user_mobile: str = Depends(
        get_current_user_mobile
    ),
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(
            User.mobile_number == current_user_mobile
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    preferences = get_or_create_notification_preferences(
        user.id,
        db,
    )

    if payload.enable_notification is not None:

        preferences.enable_notification = (
            payload.enable_notification
        )

        if payload.enable_notification is False:

            set_all_notifications(
                preferences,
                False,
            )
    
    if payload.push_notification is not None:

            preferences.push_notification = (
                payload.push_notification
            )

    if payload.sms_notification is not None:

            preferences.sms_notification = (
                payload.sms_notification
            )

    if payload.email_notification is not None:

            preferences.email_notification = (
                payload.email_notification
            )

    update_channel_preferences(
            preferences,
            "push",
            payload.push_preferences,
        )

    update_channel_preferences(
            preferences,
            "sms",
            payload.sms_preferences,
        )

    update_channel_preferences(
            preferences,
            "email",
            payload.email_preferences,
        )

    db.commit()
    db.refresh(preferences)

    return {
        "success": True,
        "message": "Notification preferences updated successfully",
        "data": preferences_to_dict(preferences),
    }

def update_channel_preferences(
    preferences,
    channel,
    data,
):

    if data is None:
        return

    fields = [
        "priority_jobs",
        "new_job_requests",
        "job_assigned",
        "job_reminders",
        "job_updates",
        "chat_messages",
        "missed_messages_reminder",
        "payment_received",
        "payout_updates",
        "app_updates",
        "maintenance_alerts",
    ]

    for field in fields:

        value = getattr(
            data,
            field,
            None,
        )

        if value is not None:

            setattr(
                preferences,
                f"{channel}_{field}",
                value,
            )