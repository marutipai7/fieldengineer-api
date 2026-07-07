from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.booking.models import Booking, BookingStatus
from sqlalchemy import select
from app.booking.models import SiteDetail
import random
from app.booking.models import (
    Booking,
    SiteDetail,
    BookingAddress,
    SiteContactPerson,
    AccessInformation,
    BookingSchedule,
    BookingDocument
)
from app.booking.models import BookingAddress
from app.booking.models import (
    Booking,
    BookingStatus,
    Service,
    SubService,
    SiteType,
    ProjectType,
    SiteDetail,
    BookingAddress,
    SiteContactPerson,
    AccessInformation,
    BookingSchedule,
    BookingDocument
)


from app.core.database import get_db
from app.utils.auth_utils import get_current_user_email

from app.profile.models import User
from app.booking.models import Booking
from app.booking.schemas import BookingCreate


router = APIRouter(
    prefix="/booking",
    tags=["Booking"]
)
from app.booking.models import (
    Service,
    SubService,
    SiteType,
    ProjectType
)

from app.booking.schemas import (
    ServiceResponse,
    SubServiceResponse,
    SiteTypeResponse,
    ProjectTypeResponse
)

from app.booking.models import (
    SiteDetail,
    BookingAddress,
    SiteContactPerson,
    AccessInformation,
    BookingSchedule,
    BookingDocument
)

@router.get(
    "/services",
    response_model=list[ServiceResponse]
)
async def get_services(
    db: Session = Depends(get_db)
):
    return db.execute(
        select(Service)
    ).scalars().all()


@router.get(
    "/sub-services",
    response_model=list[SubServiceResponse]
)
async def get_sub_services(
    db: Session = Depends(get_db)
):
    return db.execute(
        select(SubService)
    ).scalars().all()



@router.get(
    "/site-types",
    response_model=list[SiteTypeResponse]
)
async def get_site_types(
    db: Session = Depends(get_db)
):
    return db.execute(
        select(SiteType)
    ).scalars().all()




@router.get(
    "/project-types",
    response_model=list[ProjectTypeResponse]
)
async def get_project_types(
    db: Session = Depends(get_db)
):
    return db.execute(
        select(ProjectType)
    ).scalars().all()


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

    # booking = Booking(
    #     user_id=user.id,
    #     # booking_number=f"BK-{uuid.uuid4().hex[:8].upper()}",
    #     service_type=payload.service_type,
    #     description=payload.description,
    #     scheduled_date=str(payload.scheduled_date),
    #     scheduled_time=str(payload.scheduled_time),
    #     address=payload.address
    # )
    # booking = Booking(
    #     user_id=user.id,
    #     booking_number=f"BK-{random.randint(100000,999999)}",
    #     service_type=payload.service_type,
    #     description=payload.description,
    #     scheduled_date=str(payload.scheduled_date),
    #     scheduled_time=str(payload.scheduled_time),
    #     address=payload.address
    # )
    booking = Booking(
       user_id=user.id,
       booking_number=f"BK-{random.randint(100000,999999)}",

       budget_min=payload.budget_min,
       budget_max=payload.budget_max,

       service_id=payload.service_id,
       sub_service_id=payload.sub_service_id,

        requirement_description=payload.requirement_description
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)
    site_detail = SiteDetail(
        booking_id=booking.id,

        site_name=payload.site_details.site_name,
        company_name=payload.site_details.company_name,

        site_type_id=payload.site_details.site_type_id,
        project_type_id=payload.site_details.project_type_id,

        floor_number=payload.site_details.floor_number,
        building_wing=payload.site_details.building_wing,
        landmark=payload.site_details.landmark
    )
    db.add(site_detail)
    address = BookingAddress(
        booking_id=booking.id,
        country=payload.address.country,
        state=payload.address.state,
        pin_code=payload.address.pin_code,
        area_locality=payload.address.area_locality,
        city=payload.address.city,
        address_line_1=payload.address.address_line_1,
        address_line_2=payload.address.address_line_2,
        latitude=payload.address.latitude,
        longitude=payload.address.longitude
    )
    db.add(address)

    contact_person = SiteContactPerson(
        booking_id=booking.id,
        contact_person_name=payload.contact_person.contact_person_name,
        mobile_number=payload.contact_person.mobile_number,
        alternate_number=payload.contact_person.alternate_number,
        email=payload.contact_person.email,
        department=payload.contact_person.department
    )

    db.add(contact_person)



     
    access_info = AccessInformation(
        booking_id=booking.id,
        entry_instructions=payload.access_information.entry_instructions,
        security_gate_details=payload.access_information.security_gate_details,
        parking_availability=payload.access_information.parking_availability,
        access_timing=payload.access_information.access_timing,
        visitor_pass_required=payload.access_information.visitor_pass_required,
        night_shift_access=payload.access_information.night_shift_access,
        weekend_access=payload.access_information.weekend_access,
        id_verification_required=payload.access_information.id_verification_required
    )

    db.add(access_info)
     
    schedule = BookingSchedule(
        booking_id=booking.id,
        scheduled_date=payload.schedule.scheduled_date,
        scheduled_time=payload.schedule.scheduled_time,
        estimated_duration_hours=payload.schedule.estimated_duration_hours,
        notes=payload.schedule.notes
    )

    db.add(schedule)
      
    for doc in payload.documents:
        document = BookingDocument(
          booking_id=booking.id,
          file_name=doc.file_name,
          file_url=doc.file_url,
          file_size=doc.file_size
        )

        db.add(document)
    



   
    db.commit()   

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
            # "booking_number": booking.booking_number,
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
        # "booking_number": booking.booking_number,
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

    # booking.service_type = payload.service_type
    # booking.description = payload.description
    # booking.scheduled_date = str(payload.scheduled_date)
    # booking.scheduled_time = str(payload.scheduled_time)
    # booking.address = payload.address
    booking.budget_min = payload.budget_min
    booking.budget_max = payload.budget_max
    booking.service_id = payload.service_id
    booking.sub_service_id = payload.sub_service_id
    booking.requirement_description = payload.requirement_description
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
