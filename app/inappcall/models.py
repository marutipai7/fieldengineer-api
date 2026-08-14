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

    # User receiving the call
    receiver_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

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

    call = relationship(
        "CallSession",
        back_populates="participants",
    )

    user = relationship("User")