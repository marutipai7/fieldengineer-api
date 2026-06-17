import enum

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy import Enum as SqlEnum

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    booking_number = Column(String(50), unique=True, nullable=False)

    service_type = Column(String(255))
    description = Column(Text)

    booking_status = Column(
        SqlEnum(BookingStatus),
        default=BookingStatus.PENDING
    )

    scheduled_date = Column(String(50))
    scheduled_time = Column(String(50))

    address = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )