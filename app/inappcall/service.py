import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.inappcall.models import (
    CallSession,
    CallParticipant,
    CallStatus,
    CallType,
)
<<<<<<< HEAD


=======
from app.core.config import settings

def build_join_url(room_id: str) -> str:
    return f"{settings.FRONTEND_URL}/inappcall/{room_id}"
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
def create_room_id():
    return str(uuid.uuid4())


def create_call(
    db: Session,
    caller_id: int,
<<<<<<< HEAD
    call_type: CallType = CallType.VIDEO,
    appointment_id: int | None = None,
    appointment_reference: str | None = None,
    notes: str | None = None,
):
    room_id = create_room_id()
=======
    receiver_id: int,
    call_type: CallType = CallType.VIDEO,
    notes: str | None = None,
):
    room_id = create_room_id()
    join_url = build_join_url(room_id)
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6

    call = CallSession(
        room_id=room_id,
        caller_id=caller_id,
<<<<<<< HEAD
        call_type=call_type,
        status=CallStatus.CREATED,
        appointment_id=appointment_id,
        appointment_reference=appointment_reference,
        notes=notes,
    )

    db.add(call)
    db.commit()
    db.refresh(call)

    # Add caller as the first participant
=======
        receiver_id=receiver_id,
        call_type=call_type,
        status=CallStatus.CREATED,
        notes=notes,
        join_url=join_url,
    )

    db.add(call)
    db.flush()

>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
    caller = CallParticipant(
        call_id=call.id,
        user_id=caller_id,
    )

<<<<<<< HEAD
    db.add(caller)
    db.commit()
=======
    receiver = CallParticipant(
        call_id=call.id,
        user_id=receiver_id,
    )

    db.add_all([caller, receiver])
    db.commit()
    db.refresh(call)
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6

    return call


def create_group_call(
    db: Session,
    caller_id: int,
    participant_ids: list[int],
    call_type: CallType = CallType.VIDEO,
<<<<<<< HEAD
    appointment_id: int | None = None,
    appointment_reference: str | None = None,
    notes: str | None = None,
):
    room_id = create_room_id()
=======
    notes: str | None = None,
):
    room_id = create_room_id()
    join_url = build_join_url(room_id)
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6

    call = CallSession(
        room_id=room_id,
        caller_id=caller_id,
<<<<<<< HEAD
        call_type=call_type,
        status=CallStatus.CREATED,
        appointment_id=appointment_id,
        appointment_reference=appointment_reference,
        notes=notes,
=======
        receiver_id=None,
        call_type=call_type,
        status=CallStatus.CREATED,
        notes=notes,
        join_url=join_url,
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
    )

    db.add(call)
    db.flush()

<<<<<<< HEAD
    # Make sure caller is included
=======
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
    all_participants = set(participant_ids)
    all_participants.add(caller_id)

    for user_id in all_participants:
        participant = CallParticipant(
            call_id=call.id,
            user_id=user_id,
        )
<<<<<<< HEAD

=======
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
        db.add(participant)

    db.commit()
    db.refresh(call)

    return call


def add_participant(
    db: Session,
    call_id: int,
    user_id: int,
):
    participant = CallParticipant(
        call_id=call_id,
        user_id=user_id,
    )

    db.add(participant)
    db.commit()
    db.refresh(participant)

    return participant


def update_call_status(
    db: Session,
    call_id: int,
    status: CallStatus,
):
    call = (
        db.query(CallSession)
        .filter(CallSession.id == call_id)
        .first()
    )

    if not call:
        return None

    call.status = status

    if status == CallStatus.ONGOING:
        call.started_at = datetime.utcnow()

    if status == CallStatus.ENDED:
        call.ended_at = datetime.utcnow()

        if call.started_at:
            call.duration = int(
                (call.ended_at - call.started_at).total_seconds()
            )

    db.commit()
    db.refresh(call)

    return call


def get_call(
    db: Session,
    call_id: int,
):
    return (
        db.query(CallSession)
        .filter(CallSession.id == call_id)
        .first()
    )


def get_user_calls(
    db: Session,
    user_id: int,
):
    return (
        db.query(CallSession)
        .join(
            CallParticipant,
            CallParticipant.call_id == CallSession.id,
        )
        .filter(CallParticipant.user_id == user_id)
        .order_by(CallSession.created_at.desc())
        .all()
    )