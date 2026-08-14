from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


# Call Status
class CallStatus(str, enum.Enum):
    CREATED = "CREATED"
    RINGING = "RINGING"
    JOINED = "JOINED"
    ONGOING = "ONGOING"
    ENDED = "ENDED"
    MISSED = "MISSED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


# Call Type
class CallType(str, enum.Enum):
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"


# Call Session Model
class CallSession(Base):
    __tablename__ = "call_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

<<<<<<< HEAD
    # Calling room
=======
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
    room_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # User who starts the call
    caller_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

<<<<<<< HEAD
=======
    # User receiving the call
    receiver_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
    call_type = Column(
        Enum(CallType),
        default=CallType.VIDEO,
        nullable=False,
    )

    status = Column(
        Enum(CallStatus),
        default=CallStatus.CREATED,
        nullable=False,
    )

<<<<<<< HEAD
    appointment_id = Column(
        Integer,
        nullable=True,
    )

    appointment_reference = Column(
        String(100),
        nullable=True,
    )

=======
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
    notes = Column(
        Text,
        nullable=True,
    )

    join_url = Column(
        Text,
        nullable=True,
    )

    token = Column(
        Text,
        nullable=True,
    )

    duration = Column(
        Integer,
        default=0,
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    ended_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

<<<<<<< HEAD
    caller = relationship("User")

    participants = relationship(
        "CallParticipant",
=======
    caller = relationship(
        "User",
        foreign_keys=[caller_id],
    )

    receiver = relationship(
        "User",
        foreign_keys=[receiver_id],
    )

    participants = relationship(
        "CallParticipant",
        back_populates="call",
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
        cascade="all, delete-orphan",
    )


# Call Participant Model
class CallParticipant(Base):
    __tablename__ = "call_participants"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    call_id = Column(
        Integer,
        ForeignKey(
            "call_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    peer_name = Column(
        String(255),
        nullable=True,
    )

    peer_avatar = Column(
        String(500),
        nullable=True,
    )

    presenter = Column(
        Boolean,
        default=False,
    )

    audio_enabled = Column(
        Boolean,
        default=True,
    )

    video_enabled = Column(
        Boolean,
        default=True,
    )

    screen_enabled = Column(
        Boolean,
        default=False,
    )

    joined_at = Column(
        DateTime,
        nullable=True,
    )

    left_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

<<<<<<< HEAD
    call = relationship("CallSession")
=======
    call = relationship(
        "CallSession",
        back_populates="participants",
    )
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6

    user = relationship("User")