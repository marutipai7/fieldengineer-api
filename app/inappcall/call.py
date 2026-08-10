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
from app.core.database import get_db
from app.utils.auth_utils import get_current_user_object


router = APIRouter(
    prefix="/inappcall",
    tags=["In-App Call"],
)


@router.post(
    "/create",
    response_model=CallResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_call(
    data: CallCreate,
    current_user: dict = Depends(get_current_user_object),
    db: Session = Depends(get_db),
):
    call = service.create_call(
        db=db,
        caller_id=current_user[0].id,
        call_type=CallType(data.call_type),
        appointment_id=data.appointment_id,
        appointment_reference=data.appointment_reference,
        notes=data.notes,
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
        appointment_id=data.appointment_id,
        appointment_reference=data.appointment_reference,
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