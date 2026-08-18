from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship


from app.core.database import Base
from app.chat import models
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    participants = relationship(
        "ChatParticipant",
        back_populates="chat_session",
        cascade="all, delete"
    )

    messages = relationship(
        "ChatHistory",
        back_populates="chat_session",
        cascade="all, delete"
    )


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    chat_session = relationship(
        "ChatSession",
        back_populates="participants"
    )

    user = relationship(
        "User"
    )


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id"),
        nullable=False
    )

    sender_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    message_type = Column(
        String,
        nullable=False
    )
    # text / image / file

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    chat_session = relationship(
        "ChatSession",
        back_populates="messages"
    )

    sender = relationship(
        "User"
    )