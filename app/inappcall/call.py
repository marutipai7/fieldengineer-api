import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.inappcall import service
from app.inappcall.firebase import (
    save_fcm_token as store_fcm_token,
    send_push_notification,
)
from app.inappcall.models import CallStatus, CallType
from app.inappcall.utils import send_incoming_call_notification
from app.inappcall.schemas import (
    CallCreate,
    CallParticipantCreate,
    CallResponse,
    CallStatusUpdate,
    FCMTokenRequest,
    FCMTokenResponse,
    GroupCallCreate,
)
from app.core.database import get_db
from app.utils.auth_utils import (
    check_authorization_key,
    get_current_user_object,
)

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

    send_incoming_call_notification(db=db, call=call)

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
    return service.create_group_call(
        db=db,
        caller_id=current_user[0].id,
        participant_ids=data.participant_ids,
        call_type=CallType(data.call_type),
        notes=data.notes,
    )


@router.post(
    "/{call_id}/participants",
)
def add_participant(
    call_id: int,
    data: CallParticipantCreate,
    current_user: dict = Depends(get_current_user_object),
    db: Session = Depends(get_db),
):
    if call := service.get_call(db, call_id):
        return service.add_participant(
            db=db,
            call_id=call_id,
            user_id=data.user_id,
        )
    raise HTTPException(
        status_code=404,
        detail="Call not found",
    )


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
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid call status",
        )from e

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
@router.post(
    "/fcm-token",
    response_model=FCMTokenResponse,
)
async def save_fcm_token(
    request: FCMTokenRequest,
    db: Session = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user=Depends(get_current_user_object),
):
    user, _ = current_user

    store_fcm_token(db=db, user_id=user.id, token=request.token)
    return FCMTokenResponse(
        message="FCM token saved successfully.",
        token=request.token,
    )
    
@router.post("/test-push")
async def test_push_notification(
    db: Session = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user=Depends(get_current_user_object),
):
    user, _ = current_user

    success = send_push_notification(
        db=db,
        user_id=user.id,
        title="FCM Test",
        body="Hello from Backend 🚀",
        data={
            "type": "test",
            "screen": "home",
        },
    )

    return {
        "success": success,
    }

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
