from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.booking.models import Booking, BookingStatus
from sqlalchemy import select, func, distinct
import json
from sqlalchemy import select
import re
from app.profile.models import UserProfile
from pathlib import Path
import uuid
import random
from app.booking.schemas import ServiceDetailCreateSchema
from app.booking.models import (
    Booking,
    SiteDetail,
    BookingAddress,
    SiteContactPerson,
    AccessInformation,
    BookingSchedule,
    BookingDocument,
    ServiceDetail
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

from app.booking.models import (
    Service,
    SubService,
    FieldEngineerService,
)


from app.core.database import get_db
from app.utils.auth_utils import get_current_user_mobile

from app.profile.models import User, UserProfile
from app.booking.models import Booking
from app.booking.schemas import BookingCreate, OfferDetailsResponse


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
    ServiceDetailResponse,
    SiteTypeResponse,
    ProjectTypeResponse,
    LeadResponse
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


# Customer Service Details API
@router.get(
    "/services/{service_id}",
    response_model=ServiceDetailResponse
)
async def get_service_details(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = db.execute(
        select(Service).where(
            Service.id == service_id
        )
    ).scalars().first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    sub_services = db.execute(
        select(SubService).where(
            SubService.service_id == service_id
        ).order_by(SubService.sub_service_name)
    ).scalars().all()

    # Aggregate engineer availability & budget range for this service
    stats = db.execute(
        select(
            func.count(distinct(FieldEngineerService.field_engineer_id)).label("total_engineers"),
            func.min(FieldEngineerService.price).label("budget_min"),
            func.max(FieldEngineerService.price).label("budget_max")
        ).where(
            FieldEngineerService.service_id == service_id
        )
    ).first()

    # whats_included is stored as a JSON-encoded list of strings
    whats_included: list[str] = []
    if service.whats_included:
        try:
            parsed = json.loads(service.whats_included)
            if isinstance(parsed, list):
                whats_included = [str(item) for item in parsed]
            else:
                whats_included = [str(parsed)]
        except (ValueError, TypeError):
            # Fallback: treat as comma/newline separated plain text
            whats_included = [
                item.strip()
                for item in re.split(r"[,\n]", service.whats_included)
                if item.strip()
            ]

    return ServiceDetailResponse(
        id=service.id,
        service_name=service.service_name,
        image_url=service.image_url,
        about_service=service.about_service,
        whats_included=whats_included,
        min_duration_hours=service.min_duration_hours or 2,
        total_engineers_available=(stats.total_engineers or 0) if stats else 0,
        budget_min=float(stats.budget_min) if stats and stats.budget_min is not None else None,
        budget_max=float(stats.budget_max) if stats and stats.budget_max is not None else None,
        sub_services=sub_services
    )


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
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(
            User.mobile_number == current_user_mobile
        )
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    booking = Booking(
        user_id=user.id,
        booking_number=f"BK-{random.randint(100000, 999999)}",

        budget_min=payload.budget_min,
        budget_max=payload.budget_max,

        service_id=payload.service_id,
        sub_service_id=payload.sub_service_id,

        requirement_description=payload.requirement_description,
        scope_of_work=payload.scope_of_work,
        special_requirements=payload.special_requirements
    )

    db.add(booking)
    db.flush()

    # -----------------------------
    # SITE DETAILS
    # -----------------------------
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

    # -----------------------------
    # ADDRESS
    # -----------------------------
    address = BookingAddress(
        booking_id=booking.id,
        country_id=payload.address.country_id,
        state_id=payload.address.state_id,
        pin_code=payload.address.pin_code,
        area_locality=payload.address.area_locality,
        city=payload.address.city,
        address_line_1=payload.address.address_line_1,
        address_line_2=payload.address.address_line_2,
        latitude=payload.address.latitude,
        longitude=payload.address.longitude
    )
    db.add(address)

    # -----------------------------
    # CONTACT PERSON
    # -----------------------------
    contact_person = SiteContactPerson(
        booking_id=booking.id,
        contact_person_name=payload.contact_person.contact_person_name,
        mobile_number=payload.contact_person.mobile_number,
        alternate_number=payload.contact_person.alternate_number,
        email=payload.contact_person.email,
        department=payload.contact_person.department
    )
    db.add(contact_person)

    # -----------------------------
    # ACCESS INFORMATION
    # -----------------------------
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

    # -----------------------------
    # SCHEDULE
    # -----------------------------
    schedule = BookingSchedule(
        booking_id=booking.id,
        scheduled_date=payload.schedule.scheduled_date,
        scheduled_time=payload.schedule.scheduled_time,
        urgency_level=payload.schedule.urgency_level,
        single_day=payload.schedule.single_day,
        estimated_duration_hours=payload.schedule.estimated_duration_hours,
        notes=payload.schedule.notes
    )
    db.add(schedule)

    # -----------------------------
    # DOCUMENTS
    # -----------------------------
    for doc in payload.documents:
        document = BookingDocument(
            booking_id=booking.id,
            file_name=doc.file_name,
            file_url=doc.file_url,
            file_size=doc.file_size
        )
        db.add(document)

    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking created successfully",
        "booking_id": str(booking.id)
    }


@router.get("/")
async def get_bookings(
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(
            User.mobile_number == current_user_mobile
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

    result = []

    for booking in bookings:

        site_detail = db.execute(
            select(SiteDetail).where(
                SiteDetail.booking_id == booking.id
            )
        ).scalars().first()

        address = db.execute(
            select(BookingAddress).where(
                BookingAddress.booking_id == booking.id
            )
        ).scalars().first()

        schedule = db.execute(
            select(BookingSchedule).where(
                BookingSchedule.booking_id == booking.id
            )
        ).scalars().first()

        result.append({
            "id": str(booking.id),
            "booking_number": booking.booking_number,
            "service_id": booking.service_id,
            "sub_service_id": booking.sub_service_id,
            "booking_status": booking.booking_status.value,

            "budget_min": booking.budget_min,
            "budget_max": booking.budget_max,

            "requirement_description": booking.requirement_description,
            "scope_of_work": booking.scope_of_work,
            "special_requirements": booking.special_requirements,

            "site_details": {
                "site_name": site_detail.site_name if site_detail else None,
                "company_name": site_detail.company_name if site_detail else None,
                "site_type_id": site_detail.site_type_id if site_detail else None,
                "project_type_id": site_detail.project_type_id if site_detail else None,
                "floor_number": site_detail.floor_number if site_detail else None,
                "building_wing": site_detail.building_wing if site_detail else None,
                "landmark": site_detail.landmark if site_detail else None
            },

            "address": {
                "country_id": address.country_id if address else None,
                "state_id": address.state_id if address else None,
                "pin_code": address.pin_code if address else None,
                "area_locality": address.area_locality if address else None,
                "city": address.city if address else None,
                "address_line_1": address.address_line_1 if address else None,
                "address_line_2": address.address_line_2 if address else None,
                "latitude": address.latitude if address else None,
                "longitude": address.longitude if address else None
            },

            "schedule": {
                "scheduled_date": schedule.scheduled_date if schedule else None,
                "scheduled_time": schedule.scheduled_time if schedule else None,
                "urgency_level": schedule.urgency_level if schedule else None,
                "single_day": schedule.single_day if schedule else False,
                "estimated_duration_hours": (
                    schedule.estimated_duration_hours
                    if schedule else None
                ),
                "notes": schedule.notes if schedule else None
            }
        })

    return result


@router.get("/{booking_id}")
async def get_booking_details(
    booking_id: int,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.mobile_number == current_user_mobile)
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

    # Related records
    site_detail = db.execute(
        select(SiteDetail).where(SiteDetail.booking_id == booking.id)
    ).scalars().first()

    address = db.execute(
        select(BookingAddress).where(BookingAddress.booking_id == booking.id)
    ).scalars().first()

    contact_person = db.execute(
        select(SiteContactPerson).where(SiteContactPerson.booking_id == booking.id)
    ).scalars().first()

    access_info = db.execute(
        select(AccessInformation).where(
            AccessInformation.booking_id == booking.id
        )
    ).scalars().first()

    schedule = db.execute(
        select(BookingSchedule).where(
            BookingSchedule.booking_id == booking.id
        )
    ).scalars().first()

    documents = db.execute(
        select(BookingDocument).where(
            BookingDocument.booking_id == booking.id
        )
    ).scalars().all()

    return {
        "id": str(booking.id),
        "booking_number": booking.booking_number,

        "service_type": booking.service_type,
        "service_id": booking.service_id,
        "sub_service_id": booking.sub_service_id,

        "budget_min": booking.budget_min,
        "budget_max": booking.budget_max,

        "requirement_description": booking.requirement_description,
        "scope_of_work": booking.scope_of_work,
        "special_requirements": booking.special_requirements,

        "booking_status": booking.booking_status.value,

        "site_details": {
            "site_name": site_detail.site_name if site_detail else None,
            "company_name": site_detail.company_name if site_detail else None,
            "site_type_id": site_detail.site_type_id if site_detail else None,
            "project_type_id": site_detail.project_type_id if site_detail else None,
            "floor_number": site_detail.floor_number if site_detail else None,
            "building_wing": site_detail.building_wing if site_detail else None,
            "landmark": site_detail.landmark if site_detail else None
        },

        "address": {
            "country_id": address.country_id if address else None,
            "state_id": address.state_id if address else None,
            "pin_code": address.pin_code if address else None,
            "area_locality": address.area_locality if address else None,
            "city": address.city if address else None,
            "address_line_1": address.address_line_1 if address else None,
            "address_line_2": address.address_line_2 if address else None,
            "latitude": address.latitude if address else None,
            "longitude": address.longitude if address else None
        },

        "contact_person": {
            "contact_person_name": (
                contact_person.contact_person_name
                if contact_person else None
            ),
            "mobile_number": (
                contact_person.mobile_number
                if contact_person else None
            ),
            "alternate_number": (
                contact_person.alternate_number
                if contact_person else None
            ),
            "email": (
                contact_person.email
                if contact_person else None
            ),
            "department": (
                contact_person.department
                if contact_person else None
            )
        },

        "access_information": {
            "entry_instructions": (
                access_info.entry_instructions
                if access_info else None
            ),
            "security_gate_details": (
                access_info.security_gate_details
                if access_info else None
            ),
            "parking_availability": (
                access_info.parking_availability
                if access_info else None
            ),
            "access_timing": (
                access_info.access_timing
                if access_info else None
            ),
            "visitor_pass_required": (
                access_info.visitor_pass_required
                if access_info else False
            ),
            "night_shift_access": (
                access_info.night_shift_access
                if access_info else False
            ),
            "weekend_access": (
                access_info.weekend_access
                if access_info else False
            ),
            "id_verification_required": (
                access_info.id_verification_required
                if access_info else False
            )
        },

        "schedule": {
            "scheduled_date": (
                schedule.scheduled_date
                if schedule else None
            ),
            "scheduled_time": (
                schedule.scheduled_time
                if schedule else None
            ),
            "urgency_level": (
                schedule.urgency_level
                if schedule else None
            ),
            "single_day": (
                schedule.single_day
                if schedule else False
            ),
            "estimated_duration_hours": (
                schedule.estimated_duration_hours
                if schedule else None
            ),
            "notes": (
                schedule.notes
                if schedule else None
            )
        },

        "documents": [
            {
                "file_name": doc.file_name,
                "file_url": doc.file_url,
                "file_size": doc.file_size
            }
            for doc in documents
        ],

        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }

@router.get(
    "/{booking_id}/offer-details",
    response_model=OfferDetailsResponse,
)
@router.get(
    "/{booking_id}/offer_details",
    response_model=OfferDetailsResponse,
    include_in_schema=False,
)
@router.get(
    "/{booking_id}/customer-offer-details",
    response_model=OfferDetailsResponse,
    include_in_schema=False,
)
async def get_customer_offer_details(
    booking_id: int,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    # 1. Find logged-in customer
    user = db.execute(
        select(User).where(
            User.mobile_number == current_user_mobile
        )
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # 2. Find customer's booking
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

    # 3. Get service
    service = db.execute(
        select(Service).where(
            Service.id == booking.service_id
        )
    ).scalars().first()

    # 4. Get sub-service
    sub_service = db.execute(
        select(SubService).where(
            SubService.id == booking.sub_service_id
        )
    ).scalars().first()

    # 5. Default: no engineer / no offer yet
    accepted_field_engineer = None
    offer_price = None
    has_offer = False

    # 6. If engineer has been assigned, get engineer + price
    if booking.accepted_field_engineer_id is not None:

        accepted_profile = db.execute(
            select(UserProfile).where(
                UserProfile.id == booking.accepted_field_engineer_id
            )
        ).scalars().first()

        if accepted_profile:

            accepted_user = db.execute(
                select(User).where(
                    User.id == accepted_profile.user_id
                )
            ).scalars().first()

            engineer_service = db.execute(
                select(FieldEngineerService).where(
                    FieldEngineerService.field_engineer_id == accepted_profile.id,
                    FieldEngineerService.service_id == booking.service_id,
                    FieldEngineerService.sub_service_id == booking.sub_service_id
                )
            ).scalars().first()

            if engineer_service:
                offer_price = float(engineer_service.price)
                has_offer = True

            accepted_field_engineer = {
                "id": accepted_profile.id,
                "user_id": accepted_profile.user_id,
                "full_name": accepted_profile.full_name,
                "mobile_number": (
                    accepted_user.mobile_number
                    if accepted_user else None
                ),
                "profile_image": accepted_profile.profile_image,
                "work_preference": accepted_profile.work_preference,
            }

    # 7. Return offer details
    return OfferDetailsResponse(
        booking_id=booking.id,
        booking_number=booking.booking_number,
        service_name=service.service_name if service else None,
        sub_service_name=(
            sub_service.sub_service_name
            if sub_service else None
        ),
        budget_min=booking.budget_min,
        budget_max=booking.budget_max,
        offer_price=offer_price,
        status=(
            booking.booking_status.value
            if booking.booking_status else None
        ),
        has_offer=has_offer,
        accepted_field_engineer=accepted_field_engineer,
    )


@router.put("/{booking_id}")
async def update_booking(
    booking_id: int,
    payload: BookingCreate,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.mobile_number == current_user_mobile)
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
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.mobile_number == current_user_mobile)
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

# User Accept API

@router.post("/{booking_id}/accept-offer")
async def user_accept_booking(
    booking_id: int,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.mobile_number == current_user_mobile)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    print("USER ID:", user.id)

    booking = (
    db.query(Booking)
    .filter(Booking.id == booking_id)
    .first()
)

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found for this user"
        )

    if booking.accepted_field_engineer_id is None:
        raise HTTPException(
            status_code=400,
            detail="No Field Engineer has been assigned to this booking"
        )

    booking.booking_status = BookingStatus.CONFIRMED

    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking accepted successfully",
        "booking_id": booking.id,
        "booking_number": booking.booking_number,
        "status": booking.booking_status.value
    }

# User Reject API

@router.post("/{booking_id}/reject-offer")
async def user_reject_booking(
    booking_id: int,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.mobile_number == current_user_mobile)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id,
            Booking.user_id == user.id
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    booking.booking_status = BookingStatus.CANCELLED

    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking rejected successfully",
        "booking_id": booking.id,
        "booking_number": booking.booking_number,
        "status": booking.booking_status.value
    }


# Upload Booking Documents

@router.post("/{booking_id}/documents")
async def upload_booking_documents(
    booking_id: int,
    files: list[UploadFile] = File(...),
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.mobile_number == current_user_mobile)
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

    # Upload directory: uploads/booking/{booking_id}/
    upload_dir = Path(f"uploads/booking/{booking_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_documents = []

    for file in files:
        content = await file.read()

        original_filename = file.filename or "document"
        extension = Path(original_filename).suffix
        filename = f"{uuid.uuid4().hex}{extension}"

        saved_path = upload_dir / filename

        with open(saved_path, "wb") as buffer:
            buffer.write(content)

        document = BookingDocument(
            booking_id=booking.id,
            file_name=original_filename,
            file_url=str(saved_path),
            file_size=str(len(content))
        )

        db.add(document)
        saved_documents.append(document)

    db.commit()

    for document in saved_documents:
        db.refresh(document)

    return {
        "message": "Documents uploaded successfully",
        "booking_id": booking.id,
        "documents": [
            {
                "id": document.id,
                "file_name": document.file_name,
                "file_url": document.file_url,
                "file_size": document.file_size
            }
            for document in saved_documents
        ]
    }

# @router.post("/service-details")
# async def create_service_detail(
#     payload: ServiceDetailCreateSchema,
#     db: Session = Depends(get_db)
# ):
#     # Check whether service exists
#     service = db.execute(
#         select(Service).where(
#             Service.id == payload.service_id
#         )
#     ).scalars().first()

#     if not service:
#         raise HTTPException(
#             status_code=404,
#             detail="Service not found"
#         )

#     # Check whether details already exist
#     existing_detail = db.execute(
#         select(ServiceDetail).where(
#             ServiceDetail.service_id == payload.service_id
#         )
#     ).scalars().first()

#     if existing_detail:
#         raise HTTPException(
#             status_code=400,
#             detail="Service details already exist for this service"
#         )

#     # Create service details
#     service_detail = ServiceDetail(
#         service_id=payload.service_id,
#         image_url=payload.image_url,
#         engineers_available=payload.engineers_available,
#         price_per_hour=payload.price_per_hour,
#         min_duration_hours=payload.min_duration_hours,
#         service_tags=payload.service_tags,
#         about_service=payload.about_service,
#         whats_included=payload.whats_included
#     )

#     db.add(service_detail)
#     db.commit()
#     db.refresh(service_detail)

#     return {
#         "message": "Service details created successfully",
#         "service_detail_id": service_detail.id,
#         "service_id": service_detail.service_id
#     }

@router.get("/service-details/{service_id}")
async def get_service_detail(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = db.execute(
        select(Service).where(
            Service.id == service_id
        )
    ).scalars().first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    service_detail = db.execute(
        select(ServiceDetail).where(
            ServiceDetail.service_id == service_id
        )
    ).scalars().first()

    if not service_detail:
        raise HTTPException(
            status_code=404,
            detail="Service details not found"
        )

    return {
        "service_id": service.id,
        "service_name": service.service_name,
        "icon": service.icon,

        "image_url": service_detail.image_url,
        "engineers_available": service_detail.engineers_available,
        "price_per_hour": service_detail.price_per_hour,
        "min_duration_hours": service_detail.min_duration_hours,
        "service_tags": service_detail.service_tags,
        "about_service": service_detail.about_service,
        "whats_included": service_detail.whats_included
    }