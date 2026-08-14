import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.inappcall import service
from app.inappcall.models import CallStatus, CallType
from app.inappcall.schemas import (
    CallCreate,
    CallParticipantCreate,
    CallResponse,
    CallStatusUpdate,
    GroupCallCreate,
)
from app.core.database import get_db, get_redis
from app.utils.auth_utils import get_current_user_object
from app.notifications.service import NotificationService
from app.notifications.schemas import NotificationCreate, NotificationType

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/inappcall",
    tags=["In-App Call"],
)


@router.post(
    "/create",
    response_model=CallResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_call(
    data: CallCreate,
    current_user: dict = Depends(get_current_user_object),
    db: Session = Depends(get_db),
):
    call = service.create_call(
        db=db,
        caller_id=current_user[0].id,
        receiver_id=data.receiver_id,
        call_type=CallType(data.call_type),
        notes=data.notes,
    )

    try:
        redis_client = await get_redis()

        notification_title = "Incoming Call"
        notification_message = (
            f"You have an incoming {call.call_type.value} call"
        )
        notification_type = NotificationType.INCOMING_CALL
        entity_type = "call"
        entity_id = call.id

        await NotificationService.create_notification(
            db=db,
            redis_client=redis_client,
            data=NotificationCreate(
                user_id=call.receiver_id,
                title=notification_title,
                message=notification_message,
                notification_type=notification_type,
                entity_type=entity_type,
                entity_id=entity_id,
                metadata={
                    "auto_generated": True,
                    "call_id": call.id,
                    "room_id": call.room_id,
                    "join_url": call.join_url,
                    "caller_id": call.caller_id,
                },
            ),
        )

        try:
            logger.info(
                f"🔥 About to send FCM notification "
                f"to user_id={call.receiver_id}"
            )
            fcm_result = await NotificationService.send_push_notification(
                db=db,
                user_id=call.receiver_id,
                title=notification_title,
                body=notification_message,
                data={
                    "notification_type": notification_type.value,
                    "entity_type": entity_type,
                    "entity_id": str(entity_id or ""),
                },
            )
            logger.info(f"🔥 FCM send result: {fcm_result}")
        except Exception as exc:
            logger.exception(
                "FCM call notification failed (non-blocking) "
                "for user_id=%s: %s",
                call.receiver_id,
                exc,
            )

    except Exception as exc:
        logger.error(
            f"Failed to create call notification: {exc}"
        )

    return call


@router.post(
    "/group",
    response_model=CallResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_group_call(
    data: GroupCallCreate,
    current_user: dict = Depends(get_current_user_object),
    db: Session = Depends(get_db),
):
    call = service.create_group_call(
        db=db,
        caller_id=current_user[0].id,
        participant_ids=data.participant_ids,
        call_type=CallType(data.call_type),
        notes=data.notes,
    )

    return call


@router.post(
    "/{call_id}/participants",
)
def add_participant(
    call_id: int,
    data: CallParticipantCreate,
    current_user: dict = Depends(get_current_user_object),
    db: Session = Depends(get_db),
):
    call = service.get_call(db, call_id)

    if not call:
        raise HTTPException(
            status_code=404,
            detail="Call not found",
        )

    participant = service.add_participant(
        db=db,
        call_id=call_id,
        user_id=data.user_id,
    )

    return participant


@router.patch(
    "/{call_id}/status",
    response_model=CallResponse,
)
def update_call_status(
    call_id: int,
    data: CallStatusUpdate,
    current_user: dict = Depends(get_current_user_object),
    db: Session = Depends(get_db),
):
    try:
        call_status = CallStatus(data.status)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid call status",
        )

    call = service.update_call_status(
        db=db,
        call_id=call_id,
        status=call_status,
    )

    if not call:
        raise HTTPException(
            status_code=404,
            detail="Call not found",
        )

    return call


@router.get(
    "/{call_id}",
    response_model=CallResponse,
)
def get_call(
    call_id: int,
    current_user: dict = Depends(get_current_user_object),
    db: Session = Depends(get_db),
):
    call = service.get_call(
        db=db,
        call_id=call_id,
    )

    if not call:
        raise HTTPException(
            status_code=404,
            detail="Call not found",
        )

    return call
