from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.booking.models import Booking, BookingStatus
from sqlalchemy import select


from app.core.database import get_db
from app.utils.auth_utils import get_current_user_email

from app.profile.models import User
from app.booking.models import Booking
from app.booking.schemas import BookingCreate


router = APIRouter(
    prefix="/booking",
    tags=["Booking"]
)


@router.post("/")
async def create_booking(
    payload: BookingCreate,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(
            User.email == current_user_email
        )
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    booking = Booking(
        user_id=user.id,
        # booking_number=f"BK-{uuid.uuid4().hex[:8].upper()}",
        service_type=payload.service_type,
        description=payload.description,
        scheduled_date=str(payload.scheduled_date),
        scheduled_time=str(payload.scheduled_time),
        address=payload.address
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking created successfully",
        "booking_id": str(booking.id)
    }


@router.get("/")
async def get_bookings(
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(
            User.email == current_user_email
        )
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    bookings = db.execute(
        select(Booking).where(
            Booking.user_id == user.id
        )
    ).scalars().all()

    return [
        {
            "id": str(booking.id),
            "booking_number": booking.booking_number,
            "service_type": booking.service_type,
            "description": booking.description,
            "booking_status": booking.booking_status.value,
            "scheduled_date": booking.scheduled_date,
            "scheduled_time": booking.scheduled_time,
            "address": booking.address
        }
        for booking in bookings
    ]



@router.get("/{booking_id}")
async def get_booking(
    booking_id: int,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(
            User.email == current_user_email
        )
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    booking = db.execute(
        select(Booking).where(
            Booking.id == booking_id,
            Booking.user_id == user.id
        )
    ).scalars().first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return {
        "id": str(booking.id),
        "booking_number": booking.booking_number,
        "service_type": booking.service_type,
        "description": booking.description,
        "booking_status": booking.booking_status.value,
        "scheduled_date": booking.scheduled_date,
        "scheduled_time": booking.scheduled_time,
        "address": booking.address
    }
@router.put("/{booking_id}")
async def update_booking(
    booking_id: int,
    payload: BookingCreate,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.email == current_user_email)
    ).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    booking = db.execute(
        select(Booking).where(
            Booking.id == booking_id,
            Booking.user_id == user.id
        )
    ).scalars().first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.service_type = payload.service_type
    booking.description = payload.description
    booking.scheduled_date = str(payload.scheduled_date)
    booking.scheduled_time = str(payload.scheduled_time)
    booking.address = payload.address

    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking updated successfully"
    }
@router.put("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.email == current_user_email)
    ).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    booking = db.execute(
        select(Booking).where(
            Booking.id == booking_id,
            Booking.user_id == user.id
        )
    ).scalars().first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.booking_status = BookingStatus.CANCELLED

    db.commit()

    return {
        "message": "Booking cancelled successfully"
    }