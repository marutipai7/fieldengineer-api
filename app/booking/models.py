import enum

# from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy import Enum as SqlEnum

from app.core.database import Base
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Text,
    Integer,
    Float
)


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
class BidStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
class ServiceType(str, enum.Enum):
    LAPTOP_REPAIR = "Laptop Repair"
    DESKTOP_REPAIR = "Desktop Repair"
    NETWORK_ISSUE = "Network Issue"
    SOFTWARE_INSTALLATION = "Software Installation"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True,  autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE")
    )

    booking_number = Column(String(50), unique=True)

    service_type = Column(
        SqlEnum(ServiceType),
        nullable=False
    )

    description = Column(Text)

    scheduled_date = Column(String(50))

    scheduled_time = Column(String(50))

    address = Column(Text)

    budget_min = Column(Float)

    budget_max = Column(Float)

    service_id = Column(
        Integer,
        ForeignKey("services.id"),
        default=1
    )

    sub_service_id = Column(
        Integer,
        ForeignKey("sub_services.id"),
        default=1
    )

    requirement_description = Column(Text)

    # bid_status = Column(
    #     SqlEnum(BidStatus),
    #     default=BidStatus.OPEN
    # )
    bid_status = Column(
        String(50),
        default="OPEN"
    )

    booking_status = Column(
        SqlEnum(BookingStatus),
        default=BookingStatus.PENDING
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


# class Booking(Base):
#     __tablename__ = "bookings"

#     id = Column(
#         Integer,
#         primary_key=True,
#         autoincrement=True
#     )

#     user_id = Column(
#         Integer,
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     booking_number = Column(String(50), unique=True, nullable=False)

#     # service_type = Column(String(255))
#     # service_type = Column(
#     #     SqlEnum(ServiceType),
#     #     nullable=False
#     # )
#     description = Column(Text)

#     booking_status = Column(
#         SqlEnum(BookingStatus),
#         default=BookingStatus.PENDING
#     )

#     scheduled_date = Column(String(50))
#     scheduled_time = Column(String(50))

#     address = Column(Text)

#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     updated_at = Column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         onupdate=func.now()
#     )
# class Booking(Base):
#     __tablename__ = "bookings"

#     id = Column(
#         Integer,
#         primary_key=True,
#         autoincrement=True
#     )

#     user_id = Column(
#         Integer,
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     booking_number = Column(
#         String(50),
#         unique=True,
#         nullable=False
#     )

#     budget_min = Column(Float)

#     budget_max = Column(Float)

#     service_id = Column(
#         Integer,
#         ForeignKey("services.id"),
#         nullable=False,
#         default=1
#     )

#     sub_service_id = Column(
#         Integer,
#         ForeignKey("sub_services.id"),
#         nullable=False,
#         default=1
#     )

#     requirement_description = Column(Text)

#     bid_status = Column(
#         SqlEnum(BidStatus),
#         default=BidStatus.OPEN
#     )

#     booking_status = Column(
#         SqlEnum(BookingStatus),
#         default=BookingStatus.PENDING
#     )

#     created_at = Column(
#         DateTime(timezone=True),
#         server_default=func.now()
#     )

#     updated_at = Column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         onupdate=func.now()
#     )
    
class Service(Base):
    __tablename__ = "services"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    service_name = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
class SubService(Base):
    __tablename__ = "sub_services"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    service_id = Column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False
    )

    sub_service_name = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
class SiteType(Base):
    __tablename__ = "site_types"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    site_type_name = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
class ProjectType(Base):
    __tablename__ = "project_types"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    project_type_name = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
class BookingDocument(Base):
    __tablename__ = "booking_documents"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False
    )

    file_name = Column(String(255))

    file_url = Column(Text)

    file_size = Column(String(50))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
#SiteDetail Table
class SiteDetail(Base):
    __tablename__ = "site_details"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False
    )

    site_name = Column(String(255), nullable=False)

    company_name = Column(String(255), nullable=False)

    site_type_id = Column(
        Integer,
        ForeignKey("site_types.id"),
        nullable=False,
        default=1
    )

    project_type_id = Column(
        Integer,
        ForeignKey("project_types.id"),
        nullable=False,
        default=1
    )

    floor_number = Column(String(100))

    building_wing = Column(String(255))

    landmark = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
#BookingAddress Table
class BookingAddress(Base):
    __tablename__ = "booking_addresses"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False
    )

    country = Column(String(100))

    state = Column(String(100))

    pin_code = Column(String(20))

    area_locality = Column(String(255))

    city = Column(String(100))

    address_line_1 = Column(Text)

    address_line_2 = Column(Text)

    latitude = Column(Float)

    longitude = Column(Float)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
#SiteContactPerson
class SiteContactPerson(Base):
    __tablename__ = "site_contact_persons"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False
    )

    contact_person_name = Column(
        String(255),
        nullable=False
    )

    mobile_number = Column(String(20))

    alternate_number = Column(String(20))

    email = Column(String(255))

    department = Column(String(255))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
#Access Information
class AccessInformation(Base):
    __tablename__ = "access_information"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False
    )

    entry_instructions = Column(Text)

    security_gate_details = Column(Text)

    parking_availability = Column(String(100))

    access_timing = Column(String(100))

    visitor_pass_required = Column(Integer, default=0)

    night_shift_access = Column(Integer, default=0)

    weekend_access = Column(Integer, default=0)

    id_verification_required = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
#Booking Schedule
class BookingSchedule(Base):
    __tablename__ = "booking_schedules"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False
    )

    scheduled_date = Column(String(50))

    scheduled_time = Column(String(50))

    estimated_duration_hours = Column(Integer)

    notes = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
