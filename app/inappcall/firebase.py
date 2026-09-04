import logging
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy import text

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent

SERVICE_ACCOUNT_KEY = BASE_DIR / "credentials" / "medocr-f6ddc-firebase-adminsdk-fbsvc-0bdd169219.json"


def initialize_firebase():
    """
    Initialize Firebase Admin SDK only once.
    """

    if firebase_admin._apps:
        return firebase_admin.get_app()

    cred = credentials.Certificate(str(SERVICE_ACCOUNT_KEY))

    return firebase_admin.initialize_app(cred)


def save_fcm_token(db, user_id: int, token: str) -> None:
    """Store one FCM token per user without notification-service coupling."""
    db.execute(
        text(
            "DELETE FROM fcm_device_tokens "
            "WHERE token = :token AND user_id <> :user_id"
        ),
        {"token": token, "user_id": user_id},
    )
    db.execute(
        text("DELETE FROM fcm_device_tokens WHERE user_id = :user_id"),
        {"user_id": user_id},
    )
    db.execute(
        text(
            "INSERT INTO fcm_device_tokens (user_id, token) "
            "VALUES (:user_id, :token)"
        ),
        {"user_id": user_id, "token": token},
    )
    db.commit()


def send_push_notification(
    db,
    user_id: int,
    title: str,
    body: str,
    data: dict | None = None,
) -> bool:
    """Send an FCM push using the token registered for a user."""
    try:
        token = db.execute(
            text(
                "SELECT token FROM fcm_device_tokens "
                "WHERE user_id = :user_id"
            ),
            {"user_id": user_id},
        ).scalar()

        if not token:
            logger.error(
                "FCM PUSH FAILED: No token found for user_id=%s",
                user_id,
            )
            return False

        logger.info(
            "FCM token found for user_id=%s",
            user_id,
        )

        logger.info("Initializing Firebase...")
        initialize_firebase()

        logger.info("Firebase initialized. Sending FCM...")

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={
                key: str(value)
                for key, value in (data or {}).items()
            },
            token=token,
        )

        response = messaging.send(message)

        logger.info(
            "FCM PUSH SUCCESS for user_id=%s, response=%s",
            user_id,
            response,
        )

        return True

    except Exception as e:
        logger.exception(
            "FCM PUSH FAILED for user_id=%s: %s",
            user_id,
            str(e),
        )
        return False