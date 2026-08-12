"""
Notification Service

Centralized service for creating and publishing notifications.
Handles DB insertion + Redis pub/sub integration.
"""

import json
import logging
from functools import wraps
from typing import Any, Callable, Optional

import redis.asyncio as redis
from firebase_admin import messaging
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.core.database import get_redis
from app.notifications.firebase import initialize_firebase
from app.notifications.models import FCMDeviceToken, Notification
from app.notifications.schemas import NotificationCreate, NotificationType

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for creating notifications and publishing to Redis.

    Flow:
    1. Insert into PostgreSQL
    2. Commit and refresh
    3. Publish to Redis channel
    4. Return saved object
    """

    @staticmethod
    async def create_notification(
        db: Session,
        redis_client: redis.Redis,
        data: NotificationCreate,
    ) -> Notification:
        """
        Create a notification and publish to Redis.

        Args:
            db: Session for database operations
            redis_client: Redis async client
            data: NotificationCreate schema

        Returns:
            Saved Notification object

        Behavior:
            - If DB fails: exception propagates
            - If Redis fails: logs error but does not rollback DB
        """

        try:
            notification = Notification(
                user_id=data.user_id,
                title=data.title,
                message=data.message,
                notification_type=data.notification_type.value,
                entity_type=data.entity_type,
                entity_id=data.entity_id,
                notification_metadata=data.metadata or {},
            )

            db.add(notification)
            db.commit()
            db.refresh(notification)

            logger.info(
                f"Notification created: id={notification.id}, user_id={data.user_id}"
            )

            payload = notification.to_dict()

            try:
                await redis_client.publish("notifications", json.dumps(payload))
                logger.debug(f"Published to Redis: {notification.id}")
            except Exception as redis_exc:
                logger.error(f"Redis publish failed (non-blocking): {redis_exc}")

            return notification

        except Exception as exc:
            logger.error(f"Failed to create notification: {exc}")
            db.rollback()
            raise

    @staticmethod
    async def save_fcm_token(
        db: Session,
        user_id: int,
        fcm_token: str,
    ):
        """
        Save/update FCM token.

        Rules:
        - One user -> One token
        - One token -> One user
        """

        try:
            # ----------------------------------------------------
            # 1. Check if this user already has a token
            # ----------------------------------------------------
            if user_record := db.execute(
                select(FCMDeviceToken).where(
                    FCMDeviceToken.user_id == user_id
                )
            ).scalar_one_or_none():

                # Same token already saved
                if user_record.token == fcm_token:
                    return user_record

                # Check whether this token belongs to another user
                if duplicate_token := db.execute(
                    select(FCMDeviceToken).where(
                        FCMDeviceToken.token == fcm_token
                    )
                ).scalar_one_or_none():
                    db.delete(duplicate_token)
                    db.flush()

                # Update current user's token
                user_record.token = fcm_token

                db.commit()
                db.refresh(user_record)

                return user_record

            # ----------------------------------------------------
            # 2. User doesn't exist
            # ----------------------------------------------------
            if token_record := db.execute(
                select(FCMDeviceToken).where(
                    FCMDeviceToken.token == fcm_token
                )
            ).scalar_one_or_none():
                # Same device logged into another account.
                # Remove old mapping.
                db.delete(token_record)
                db.flush()

            new_record = FCMDeviceToken(
                user_id=user_id,
                token=fcm_token,
            )

            db.add(new_record)

            db.commit()
            db.refresh(new_record)

            return new_record

        except Exception:
            db.rollback()
            raise

    @staticmethod
    async def send_push_notification(
        db: Session,
        user_id: int,
        title: str,
        body: str,
        data: dict | None = None,
    ):
        """
        Send push notification to a user using Firebase Cloud Messaging.
        """

        initialize_firebase()

        token_record = db.execute(
            select(FCMDeviceToken).where(
                FCMDeviceToken.user_id == user_id
            )
        ).scalar_one_or_none()

        if not token_record:
            logger.warning(
                f"No FCM token found for user_id={user_id}"
            )
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={
                    k: str(v)
                    for k, v in (data or {}).items()
                },
                token=token_record.token,
            )

            response = messaging.send(message)
            print("Firebase Message ID:", response)

            logger.info(
                f"Push notification sent successfully. "
                f"user_id={user_id}, message_id={response}"
            )

            return True

        except Exception as exc:
            logger.exception(
                f"Failed to send push notification "
                f"to user_id={user_id}: {exc}"
            )

            return False
    
    @staticmethod
    async def appointment_created(
        db: Session,
        patient_user_id: int,
        appointment_id: int,
        patient_name: str,
    ):
        """
        Send notification when appointment is created.
        Notification sent to patient.
        """
        try:
            logger.info(f"📢 [APPOINTMENT_CREATED] Starting for user {patient_user_id}, appointment {appointment_id}")
            
            redis_client = await get_redis()
            logger.info("✓ Redis client obtained")
            
            notification = Notification(
                user_id=patient_user_id,
                title="Appointment Created",
                message="Your appointment request has been created. Doctors will start bidding on it.",
                notification_type=NotificationType.SYSTEM_ALERT.value,
                entity_type="appointment",
                entity_id=appointment_id,
                notification_metadata={"appointment_id": appointment_id, "patient_name": patient_name},
            )
            
            logger.info(f"📝 Notification object created: {notification}")
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            logger.info(f"✓ Notification saved to DB: id={notification.id}, user_id={notification.user_id}")
            
            # Publish to Redis
            try:
                payload = {
                    "id": str(notification.id),
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                logger.info(f"📤 Publishing to Redis: {payload}")
                result = await redis_client.publish("notifications", json.dumps(payload))
                logger.info(f"✓ Published to Redis successfully. Subscriber count: {result}")
            except Exception as redis_exc:
                logger.error(f"❌ Redis publish failed: {redis_exc}", exc_info=True)
            
            logger.info(f"✓ Appointment created notification sent to user {patient_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send appointment_created notification: {e}", exc_info=True)

    @staticmethod
    async def bid_received(
        db: Session,
        patient_user_id: int,
        doctor_name: str,
        appointment_id: int,
        bid_id: int,
        bid_amount: float,
    ):
        """
        Send notification to patient when doctor places a bid on appointment.
        """
        try:
            redis_client = await get_redis()
            
            notification = Notification(
                user_id=patient_user_id,
                title=f"💰 New Bid from {doctor_name}",
                message=f"Dr. {doctor_name} has placed a bid of ₹{bid_amount} on your appointment.",
                notification_type=NotificationType.BID_RECEIVED.value,
                entity_type="bid",
                entity_id=bid_id,
                notification_metadata={
                    "appointment_id": appointment_id,
                    "doctor_name": doctor_name,
                    "bid_amount": bid_amount,
                    "bid_id": bid_id
                },
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Publish to Redis
            try:
                payload = {
                    "id": str(notification.id),
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                await redis_client.publish("notifications", json.dumps(payload))
            except Exception as redis_exc:
                logger.error(f"Redis publish failed: {redis_exc}")
            
            logger.info(f"✓ Bid received notification sent to user {patient_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send bid_received notification: {e}", exc_info=True)

    @staticmethod
    async def bid_accepted(
        db: Session,
        doctor_user_id: int,
        patient_name: str,
        appointment_id: int,
        bid_id: int,
    ):
        """
        Send notification to doctor when patient accepts their bid.
        """
        try:
            redis_client = await get_redis()
            
            notification = Notification(
                user_id=doctor_user_id,
                title=f"✅ Bid Accepted by {patient_name}",
                message=f"Your bid has been accepted! Appointment has been confirmed with {patient_name}.",
                notification_type=NotificationType.APPOINTMENT_CONFIRMED.value,
                entity_type="appointment",
                entity_id=appointment_id,
                notification_metadata={
                    "appointment_id": appointment_id,
                    "patient_name": patient_name,
                    "bid_id": bid_id,
                    "status": "accepted"
                },
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Publish to Redis
            try:
                payload = {
                    "id": str(notification.id),
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                await redis_client.publish("notifications", json.dumps(payload))
            except Exception as redis_exc:
                logger.error(f"Redis publish failed: {redis_exc}")
            
            logger.info(f"✓ Bid accepted notification sent to user {doctor_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send bid_accepted notification: {e}", exc_info=True)

    @staticmethod
    async def bid_rejected(
        db: Session,
        doctor_user_id: int,
        patient_name: str,
        appointment_id: int,
        bid_id: int,
    ):
        """
        Send notification to doctor when patient rejects their bid.
        """
        try:
            redis_client = await get_redis()
            
            notification = Notification(
                user_id=doctor_user_id,
                title="❌ Bid Rejected",
                message=f"Your bid for appointment with {patient_name} has been rejected. Other doctors may be considered.",
                notification_type=NotificationType.SYSTEM_ALERT.value,
                entity_type="appointment",
                entity_id=appointment_id,
                notification_metadata={
                    "appointment_id": appointment_id,
                    "patient_name": patient_name,
                    "bid_id": bid_id,
                    "status": "rejected"
                },
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Publish to Redis
            try:
                payload = {
                    "id": str(notification.id),
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                await redis_client.publish("notifications", json.dumps(payload))
            except Exception as redis_exc:
                logger.error(f"Redis publish failed: {redis_exc}")
            
            logger.info(f"✓ Bid rejected notification sent to user {doctor_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send bid_rejected notification: {e}", exc_info=True)

    @staticmethod
    async def appointment_created_notify_doctors(
        db: Session,
        specialization_ids: list,
        appointment_id: int,
        patient_name: str,
    ):
        """
        Send notification to doctors when patient creates an appointment.
        Notifies all doctors with specializations matching the appointment.
        
        Args:
            db: Session for database operations
            specialization_ids: List of specialization IDs from the appointment
            appointment_id: ID of the created appointment
            patient_name: Name of the patient
        """
        try:
            if not specialization_ids :
                logger.warning("No specialization IDs provided for doctor notification")
                return
            
            from app.profile.models import DoctorProfile
            from app.profile.models import User as UserModel
            
            redis_client = await get_redis()
            
            # Query doctors with matching specializations
            doctors = db.execute(
                select(DoctorProfile).where(
                    DoctorProfile.specialty_id.in_(specialization_ids),
                    DoctorProfile.is_verified == True,
                )
            ).scalars().all()
            
            if not doctors:
                logger.info(f"No verified doctors found with specializations: {specialization_ids}")
                return
            
            logger.info(f"Notifying {len(doctors)} doctors about new appointment {appointment_id}")
            
            # Send notification to each doctor
            for doctor in doctors:
                try:
                    notification = Notification(
                        user_id=doctor.user_id,
                        title="🏥 New Appointment Request",
                        message=f"A patient {patient_name} has requested an appointment in your specialization. Place a bid to secure the appointment.",
                        notification_type=NotificationType.SYSTEM_ALERT.value,
                        entity_type="appointment",
                        entity_id=appointment_id,
                        notification_metadata={
                            "appointment_id": appointment_id,
                            "patient_name": patient_name,
                            "doctor_id": doctor.id,
                            "specialization_id": doctor.specialty_id
                        },
                    )
                    
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)
                    
                    # Publish to Redis
                    try:
                        payload = {
                            "id": str(notification.id),
                            "user_id": notification.user_id,
                            "title": notification.title,
                            "message": notification.message,
                            "notification_type": notification.notification_type,
                            "entity_type": notification.entity_type,
                            "entity_id": notification.entity_id,
                            "is_read": notification.is_read,
                            "created_at": notification.created_at.isoformat() if notification.created_at else None,
                        }
                        # await redis_client.publish("notifications", json.dumps(payload))
                    except Exception as redis_exc:
                        logger.error(f"Redis publish failed for doctor {doctor.user_id}: {redis_exc}")
                    
                    logger.info(f"✓ Appointment notification sent to doctor (user_id={doctor.user_id})")
                    
                except Exception as doctor_notif_exc:
                    logger.error(f"Failed to notify doctor {doctor.user_id}: {doctor_notif_exc}", exc_info=True)
                    # Continue with next doctor even if one fails
                    continue
            
            logger.info(f"✓ All appointment notifications sent to doctors for appointment {appointment_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send appointment notifications to doctors: {e}", exc_info=True)

    @staticmethod
    async def appointment_created_notify_hospitals(
        db: Session,
        appointment_id: int,
        patient_name: str,
    ):
        """
        Send notification to hospitals when patient creates a hospital appointment.
        Notifies all verified hospitals.
        """
        try:
            from app.profile.models import HospitalProfile
            
            redis_client = await get_redis()
            
            # Query all verified hospitals
            hospitals = db.execute(
                select(HospitalProfile).where(HospitalProfile.is_verified == True)
            ).scalars().unique().all()
            
            if not hospitals:
                logger.info(f"No verified hospitals found for appointment {appointment_id}")
                return
            
            logger.info(f"Notifying {len(hospitals)} hospitals about new appointment {appointment_id}")
            
            # Send notification to each hospital
            for hospital in hospitals:
                try:
                    notification = Notification(
                        user_id=hospital.user_id,
                        title="🏥 New Hospital Appointment Request",
                        message=f"A patient {patient_name} has requested a hospital appointment. Place a bid to secure it.",
                        notification_type=NotificationType.SYSTEM_ALERT.value,
                        entity_type="hospital_appointment",
                        entity_id=appointment_id,
                        notification_metadata={
                            "appointment_id": appointment_id,
                            "patient_name": patient_name,
                            "hospital_id": hospital.id,
                        },
                    )
                    
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)
                    
                    # Publish to Redis
                    try:
                        payload = {
                            "id": str(notification.id),
                            "user_id": notification.user_id,
                            "title": notification.title,
                            "message": notification.message,
                            "notification_type": notification.notification_type,
                            "entity_type": notification.entity_type,
                            "entity_id": notification.entity_id,
                            "is_read": notification.is_read,
                            "created_at": notification.created_at.isoformat() if notification.created_at else None,
                        }
                        # await redis_client.publish("notifications", json.dumps(payload))
                    except Exception as redis_exc:
                        logger.error(f"Redis publish failed for hospital {hospital.user_id}: {redis_exc}")
                    
                    logger.info(f"✓ Hospital appointment notification sent to hospital (user_id={hospital.user_id})")
                    
                except Exception as hospital_notif_exc:
                    logger.error(f"Failed to notify hospital {hospital.user_id}: {hospital_notif_exc}", exc_info=True)
                    continue
            
            logger.info(f"✓ All hospital appointment notifications sent for appointment {appointment_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send hospital appointment notifications: {e}", exc_info=True)

    @staticmethod
    async def appointment_created_notify_labs(
        db: Session,
        appointment_id: int,
        patient_name: str,
    ):
        """
        Send notification to labs when patient creates a lab appointment.
        Notifies all verified labs.
        """
        try:
            from app.profile.models import LabProfile
            
            redis_client = await get_redis()
            
            # Query all verified labs
            labs = db.execute(
                select(LabProfile).where(LabProfile.is_verified == True)
            ).scalars().unique().all()
            
            if not labs:
                logger.info(f"No verified labs found for appointment {appointment_id}")
                return
            
            logger.info(f"Notifying {len(labs)} labs about new appointment {appointment_id}")
            
            # Send notification to each lab
            for lab in labs:
                try:
                    notification = Notification(
                        user_id=lab.user_id,
                        title="🧪 New Lab Appointment Request",
                        message=f"A patient {patient_name} has requested a lab appointment. Place a bid to secure it.",
                        notification_type=NotificationType.SYSTEM_ALERT.value,
                        entity_type="lab_appointment",
                        entity_id=appointment_id,
                        notification_metadata={
                            "appointment_id": appointment_id,
                            "patient_name": patient_name,
                            "lab_id": lab.id,
                        },
                    )
                    
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)
                    
                    # Publish to Redis
                    try:
                        payload = {
                            "id": str(notification.id),
                            "user_id": notification.user_id,
                            "title": notification.title,
                            "message": notification.message,
                            "notification_type": notification.notification_type,
                            "entity_type": notification.entity_type,
                            "entity_id": notification.entity_id,
                            "is_read": notification.is_read,
                            "created_at": notification.created_at.isoformat() if notification.created_at else None,
                        }
                        await redis_client.publish("notifications", json.dumps(payload))
                    except Exception as redis_exc:
                        logger.error(f"Redis publish failed for lab {lab.user_id}: {redis_exc}")
                    
                    logger.info(f"✓ Lab appointment notification sent to lab (user_id={lab.user_id})")
                    
                except Exception as lab_notif_exc:
                    logger.error(f"Failed to notify lab {lab.user_id}: {lab_notif_exc}", exc_info=True)
                    continue
            
            logger.info(f"✓ All lab appointment notifications sent for appointment {appointment_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send lab appointment notifications: {e}", exc_info=True)

    @staticmethod
    async def hospital_bid_received(
        db: Session,
        patient_user_id: int,
        hospital_name: str,
        appointment_id: int,
        bid_id: int,
        bid_amount: float,
    ):
        """
        Send notification to patient when hospital places a bid.
        """
        try:
            redis_client = await get_redis()
            
            notification = Notification(
                user_id=patient_user_id,
                title=f"💰 New Bid from {hospital_name}",
                message=f"{hospital_name} has placed a bid of ₹{bid_amount} on your hospital appointment.",
                notification_type=NotificationType.BID_RECEIVED.value,
                entity_type="hospital_bid",
                entity_id=bid_id,
                notification_metadata={
                    "appointment_id": appointment_id,
                    "hospital_name": hospital_name,
                    "bid_amount": bid_amount,
                    "bid_id": bid_id
                },
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Publish to Redis
            try:
                payload = {
                    "id": str(notification.id),
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                await redis_client.publish("notifications", json.dumps(payload))
            except Exception as redis_exc:
                logger.error(f"Redis publish failed: {redis_exc}")
            
            logger.info(f"✓ Hospital bid received notification sent to user {patient_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send hospital_bid_received notification: {e}", exc_info=True)

    @staticmethod
    async def lab_bid_received(
        db: Session,
        patient_user_id: int,
        lab_name: str,
        appointment_id: int,
        bid_id: int,
        bid_amount: float,
    ):
        """
        Send notification to patient when lab places a bid.
        """
        try:
            redis_client = await get_redis()
            
            notification = Notification(
                user_id=patient_user_id,
                title=f"💰 New Bid from {lab_name}",
                message=f"{lab_name} has placed a bid of ₹{bid_amount} on your lab appointment.",
                notification_type=NotificationType.BID_RECEIVED.value,
                entity_type="lab_bid",
                entity_id=bid_id,
                notification_metadata={
                    "appointment_id": appointment_id,
                    "lab_name": lab_name,
                    "bid_amount": bid_amount,
                    "bid_id": bid_id
                },
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Publish to Redis
            try:
                payload = {
                    "id": str(notification.id),
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                await redis_client.publish("notifications", json.dumps(payload))
            except Exception as redis_exc:
                logger.error(f"Redis publish failed: {redis_exc}")
            
            logger.info(f"✓ Lab bid received notification sent to user {patient_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send lab_bid_received notification: {e}", exc_info=True)

    @staticmethod
    async def hospital_bid_accepted(
        db: Session,
        hospital_user_id: int,
        patient_name: str,
        appointment_id: int,
        bid_id: int,
    ):
        """
        Send notification to hospital when patient accepts their bid.
        """
        try:
            redis_client = await get_redis()
            
            notification = Notification(
                user_id=hospital_user_id,
                title="✅ Bid Accepted",
                message="Your hospital bid has been accepted! Appointment confirmed with {patient_name}.",
                notification_type=NotificationType.APPOINTMENT_CONFIRMED.value,
                entity_type="hospital_appointment",
                entity_id=appointment_id,
                notification_metadata={
                    "appointment_id": appointment_id,
                    "patient_name": patient_name,
                    "bid_id": bid_id,
                    "status": "accepted"
                },
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Publish to Redis
            try:
                payload = {
                    "id": str(notification.id),
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                await redis_client.publish("notifications", json.dumps(payload))
            except Exception as redis_exc:
                logger.error(f"Redis publish failed: {redis_exc}")
            
            logger.info(f"✓ Hospital bid accepted notification sent to user {hospital_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send hospital_bid_accepted notification: {e}", exc_info=True)

    @staticmethod
    async def lab_bid_accepted(
        db: Session,
        lab_user_id: int,
        patient_name: str,
        appointment_id: int,
        bid_id: int,
    ):
        """
        Send notification to lab when patient accepts their bid.
        """
        try:
            redis_client = await get_redis()
            
            notification = Notification(
                user_id=lab_user_id,
                title="✅ Bid Accepted",
                message="Your lab bid has been accepted! Appointment confirmed with {patient_name}.",
                notification_type=NotificationType.APPOINTMENT_CONFIRMED.value,
                entity_type="lab_appointment",
                entity_id=appointment_id,
                notification_metadata={
                    "appointment_id": appointment_id,
                    "patient_name": patient_name,
                    "bid_id": bid_id,
                    "status": "accepted"
                },
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Publish to Redis
            try:
                payload = {
                    "id": str(notification.id),
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                await redis_client.publish("notifications", json.dumps(payload))
            except Exception as redis_exc:
                logger.error(f"Redis publish failed: {redis_exc}")
            
            logger.info(f"✓ Lab bid accepted notification sent to user {lab_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send lab_bid_accepted notification: {e}", exc_info=True)

    @staticmethod
    async def appointment_created_notify_pharmacies(
        db: Session,
        order_id: int,
        patient_name: str,
    ):
        """
        Send notification to all verified pharmacies about a new pharmacy order.
        """
        try:
            redis_client = await get_redis()
            from app.profile.models import PharmacyProfile
            
            # Get all verified pharmacies
            pharmacies = db.execute(
                select(PharmacyProfile).where(PharmacyProfile.is_verified == True)
            ).scalars().unique().all()
            
            for pharmacy in pharmacies:
                try:
                    notification = Notification(
                        user_id=pharmacy.user_id,
                        title="💊 New Order Request",
                        message="New medicine order from {patient_name}! View order details and place your bid.",
                        notification_type=NotificationType.SYSTEM_ALERT.value,
                        entity_type="pharmacy_order",
                        entity_id=order_id,
                        notification_metadata={
                            "order_id": order_id,
                            "patient_name": patient_name,
                            "notification_type": "new_order"
                        },
                    )
                    
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)
                    
                    # Publish to Redis
                    try:
                        payload = {
                            "id": str(notification.id),
                            "user_id": notification.user_id,
                            "title": notification.title,
                            "message": notification.message,
                            "notification_type": notification.notification_type,
                            "entity_type": notification.entity_type,
                            "entity_id": notification.entity_id,
                            "is_read": notification.is_read,
                            "created_at": notification.created_at.isoformat() if notification.created_at else None,
                        }
                        await redis_client.publish("notifications", json.dumps(payload))
                    except Exception as redis_exc:
                        logger.error(f"Redis publish failed for pharmacy {pharmacy.id}: {redis_exc}")
                except Exception as pharmacy_exc:
                    logger.error(f"Failed to send notification to pharmacy {pharmacy.id}: {pharmacy_exc}")
            
            logger.info(f"✓ New order notifications sent to {len(pharmacies)} verified pharmacies")
        except Exception as e:
            logger.error(f"❌ Failed to send order notifications to pharmacies: {e}", exc_info=True)

    @staticmethod
    async def pharmacy_bid_received(
        db: Session,
        patient_user_id: int,
        pharmacy_name: str,
        bid_amount: str,
        order_id: int,
        bid_id: int,
    ):
        """
Send notification to patient when a pharmacy places a bid on their order.
        """
        try:
            redis_client = await get_redis()
            
            notification = Notification(
                user_id=patient_user_id,
                title="💰 New Bid from {pharmacy_name}",
                message="A pharmacy has placed a bid of ₹{bid_amount} on your order.",
                notification_type=NotificationType.BID_RECEIVED.value,
                entity_type="pharmacy_bid",
                entity_id=order_id,
                notification_metadata={
                    "order_id": order_id,
                    "bid_id": bid_id,
                    "pharmacy_name": pharmacy_name,
                    "bid_amount": bid_amount,
                    "status": "placed"
                },
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Publish to Redis
            try:
                payload = {
                    "id": str(notification.id),
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                await redis_client.publish("notifications", json.dumps(payload))
            except Exception as redis_exc:
                logger.error(f"Redis publish failed: {redis_exc}")
            
            logger.info(f"✓ Pharmacy bid notification sent to user {patient_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send pharmacy_bid_received notification: {e}", exc_info=True)

    @staticmethod
    async def pharmacy_bid_accepted(
        db: Session,
        pharmacy_user_id: int,
        patient_name: str,
        order_id: int,
        bid_id: int,
    ):
        """
        Send notification to pharmacy when patient accepts their bid.
        """
        try:
            redis_client = await get_redis()
            
            notification = Notification(
                user_id=pharmacy_user_id,
                title="✅ Bid Accepted",
                message="Your pharmacy bid has been accepted! Order confirmed with {patient_name}.",
                notification_type=NotificationType.APPOINTMENT_CONFIRMED.value,
                entity_type="pharmacy_order",
                entity_id=order_id,
                notification_metadata={
                    "order_id": order_id,
                    "patient_name": patient_name,
                    "bid_id": bid_id,
                    "status": "accepted"
                },
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Publish to Redis
            try:
                payload = {
                    "id": str(notification.id),
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                }
                await redis_client.publish("notifications", json.dumps(payload))
            except Exception as redis_exc:
                logger.error(f"Redis publish failed: {redis_exc}")
            
            logger.info(f"✓ Pharmacy bid accepted notification sent to user {pharmacy_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send pharmacy_bid_accepted notification: {e}", exc_info=True)

    @staticmethod
    async def hospital_cancelled_after_accept(
        db: Session,
        patient_user_id: int,
        appointment_id: int,
        hospital_name: str,
    ):
        try:
            redis_client = await get_redis()

            notification = Notification(
                user_id=patient_user_id,
                title="⚠️ Hospital Cancelled Booking",
                message=f"{hospital_name} cancelled your confirmed booking. Please choose another hospital.",
                notification_type=NotificationType.SYSTEM_ALERT.value,
                entity_type="hospital_appointment",
                entity_id=appointment_id,
                notification_metadata={
                    "appointment_id": appointment_id,
                    "hospital_name": hospital_name,
                    "status": "cancelled_after_accept"
                },
            )

            db.add(notification)
            db.commit()
            db.refresh(notification)

            await redis_client.publish("notifications", json.dumps(notification.to_dict()))

        except Exception as e:
            logger.error(f"Hospital cancel notification failed: {e}", exc_info=True)

    @staticmethod
    async def lab_cancelled_after_accept(
        db: Session,
        patient_user_id: int,
        appointment_id: int,
        lab_name: str,
    ):
        try:
            redis_client = await get_redis()

            notification = Notification(
                user_id=patient_user_id,
                title="⚠️ Lab Cancelled Booking",
                message=f"{lab_name} cancelled your confirmed lab booking. Please choose another lab.",
                notification_type=NotificationType.SYSTEM_ALERT.value,
                entity_type="lab_appointment",
                entity_id=appointment_id,
                notification_metadata={
                    "appointment_id": appointment_id,
                    "lab_name": lab_name,
                    "status": "cancelled_after_accept"
                },
            )

            db.add(notification)
            db.commit()
            db.refresh(notification)

            await redis_client.publish("notifications", json.dumps(notification.to_dict()))

        except Exception as e:
            logger.error(f"Lab cancel notification failed: {e}", exc_info=True)

    @staticmethod
    async def pharmacy_cancelled_after_accept(
        db: Session,
        patient_user_id: int,
        order_id: int,
        pharmacy_name: str,
    ):
        try:
            redis_client = await get_redis()

            notification = Notification(
                user_id=patient_user_id,
                title="⚠️ Pharmacy Cancelled Order",
                message=f"{pharmacy_name} cancelled your confirmed order. Please choose another pharmacy.",
                notification_type=NotificationType.SYSTEM_ALERT.value,
                entity_type="pharmacy_order",
                entity_id=order_id,
                notification_metadata={
                    "order_id": order_id,
                    "pharmacy_name": pharmacy_name,
                    "status": "cancelled_after_accept"
                },
            )

            db.add(notification)
            db.commit()
            db.refresh(notification)

            await redis_client.publish("notifications", json.dumps(notification.to_dict()))

        except Exception as e:
            logger.error(f"Pharmacy cancel notification failed: {e}", exc_info=True)

    @staticmethod
    async def doctor_cancelled_after_accept(
        db: Session,
        patient_user_id: int,
        appointment_id: int,
        doctor_name: str,
    ):
        try:
            redis_client = await get_redis()

            notification = Notification(
                user_id=patient_user_id,
                title="⚠️ Doctor Cancelled Appointment",
                message=f"Dr. {doctor_name} cancelled your confirmed appointment. Please choose another doctor.",
                notification_type=NotificationType.SYSTEM_ALERT.value,
                entity_type="appointment",
                entity_id=appointment_id,
                notification_metadata={
                    "appointment_id": appointment_id,
                    "doctor_name": doctor_name,
                    "status": "cancelled_after_accept"
                },
            )

            db.add(notification)
            db.commit()
            db.refresh(notification)

            await redis_client.publish("notifications", json.dumps(notification.to_dict()))

        except Exception as e:
            logger.error(f"Doctor cancel notification failed: {e}", exc_info=True)

def send_notification(
    user_id_param: str = "user_id",
    title: Optional[str] = None,
    message: Optional[str] = None,
    notification_type: NotificationType = NotificationType.SYSTEM_ALERT,
    entity_type: Optional[str] = None,
    entity_id_param: Optional[str] = None,
):
    """
    Decorator to automatically send a notification after function execution.
    
    Args:
        user_id_param: Name of the parameter containing user_id (default: "user_id")
        title: Notification title (can include {var} placeholders from result)
        message: Notification message (can include {var} placeholders from result)
        notification_type: Type of notification (default: SYSTEM_ALERT)
        entity_type: Type of entity (e.g., "order", "appointment")
        entity_id_param: Name of parameter or result key for entity_id
    
    Example usage:
        @send_notification(
            user_id_param="user_id",
            title="Order #{order_id} Created",
            message="Your order has been created successfully",
            notification_type=NotificationType.ORDER_PLACED,
            entity_type="order",
            entity_id_param="order_id"
        )
        async def create_order(user_id: int, ...) -> dict:
            # Your order creation logic
            return {"order_id": 123, "status": "created"}
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Execute the original function
            result = await func(*args, **kwargs)
            
            try:
                # Extract user_id from kwargs or args
                user_id = kwargs.get(user_id_param)
                
                if not user_id:
                    logger.warning(f"send_notification: {user_id_param} not found in function args")
                    return result
                
                # Get db and redis from kwargs
                db = kwargs.get("db")
                if not db:
                    logger.warning("send_notification: db not found in function kwargs")
                    return result
                
                redis_client = await get_redis()
                
                # Extract entity_id if specified
                entity_id = None
                if entity_id_param:
                    # Try to get from result dict first, then from kwargs
                    if isinstance(result, dict) and entity_id_param in result:
                        entity_id = result[entity_id_param]
                    elif entity_id_param in kwargs:
                        entity_id = kwargs[entity_id_param]
                
                # Build notification text with template interpolation
                notify_title = title
                notify_message = message
                
                if isinstance(result, dict):
                    if title:
                        notify_title = title.format(**result)
                    if message:
                        notify_message = message.format(**result)
                
                # Create and send notification
                await NotificationService.create_notification(
                    db=db,
                    redis_client=redis_client,
                    data=NotificationCreate(
                        user_id=user_id,
                        title=notify_title or "Notification",
                        message=notify_message or "Action completed",
                        notification_type=notification_type,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        metadata={"auto_generated": True}
                    )
                )
                
            except Exception as exc:
                logger.error(f"Decorator notification failed (non-blocking): {exc}")
                # Don't fail the original function if notification fails
            
            return result
        
        return wrapper
    
    return decorator


