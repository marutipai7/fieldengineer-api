from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.profile.models import User, UserProfile
from app.booking.models import FieldEngineerService
from app.utils.auth_utils import get_current_user_email

from app.booking.models import (
    Booking,
    SiteDetail,
    BookingAddress,
    SiteContactPerson,
    AccessInformation,
    BookingSchedule,
    BookingDocument,
)
from app.booking.schemas import (
    LeadResponse,
    SiteDetailResponse,
    BookingAddressResponse,
    SiteContactPersonResponse,
    AccessInformationResponse,
    BookingScheduleResponse,
    BookingDocumentResponse,
)

router = APIRouter(
    prefix="/lead",
    tags=["Lead"]
)


def _build_lead_response(
    booking,
    site_detail,
    address,
    contact_person,
    access_info,
    schedule,
    documents,
    match_score: int,
    can_accept: bool,
) -> LeadResponse:
    return LeadResponse(
        id=booking.id,
        user_id=booking.user_id,
        booking_number=booking.booking_number,

        service_type=booking.service_type.value if booking.service_type else None,
        description=booking.description,

        budget_min=booking.budget_min,
        budget_max=booking.budget_max,

        service_id=booking.service_id,
        sub_service_id=booking.sub_service_id,

        requirement_description=booking.requirement_description,

        bid_status=booking.bid_status,
        booking_status=booking.booking_status.value if booking.booking_status else None,

        created_at=booking.created_at,
        updated_at=booking.updated_at,

        site_detail=SiteDetailResponse.model_validate(site_detail) if site_detail else None,
        address=BookingAddressResponse.model_validate(address) if address else None,
        contact_person=SiteContactPersonResponse.model_validate(contact_person) if contact_person else None,
        access_information=AccessInformationResponse.model_validate(access_info) if access_info else None,
        schedule=BookingScheduleResponse.model_validate(schedule) if schedule else None,
        documents=[BookingDocumentResponse.model_validate(doc) for doc in documents],
        match_score=match_score,
        can_accept=can_accept,
    )


@router.get(
    "/list",
    response_model=list[LeadResponse]
)
async def get_lead_list(
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    user = db.execute(
        select(User).where(User.email == current_user_email)
    ).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    ).scalars().first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Field Engineer profile not found"
        )

    engineer_services = db.execute(
        select(FieldEngineerService).where(
            FieldEngineerService.field_engineer_id == profile.id
        )
    ).scalars().all()

    service_set = {
        (service.service_id, service.sub_service_id)
        for service in engineer_services
    }

    bookings = db.execute(
        select(Booking).order_by(Booking.created_at.desc())
    ).scalars().all()

    if not bookings:
        return []

    booking_ids = [b.id for b in bookings]

    site_details = db.execute(
        select(SiteDetail).where(SiteDetail.booking_id.in_(booking_ids))
    ).scalars().all()
    site_detail_map = {sd.booking_id: sd for sd in site_details}

    addresses = db.execute(
        select(BookingAddress).where(BookingAddress.booking_id.in_(booking_ids))
    ).scalars().all()
    address_map = {a.booking_id: a for a in addresses}

    contact_persons = db.execute(
        select(SiteContactPerson).where(SiteContactPerson.booking_id.in_(booking_ids))
    ).scalars().all()
    contact_map = {c.booking_id: c for c in contact_persons}

    access_infos = db.execute(
        select(AccessInformation).where(AccessInformation.booking_id.in_(booking_ids))
    ).scalars().all()
    access_map = {ai.booking_id: ai for ai in access_infos}

    schedules = db.execute(
        select(BookingSchedule).where(BookingSchedule.booking_id.in_(booking_ids))
    ).scalars().all()
    schedule_map = {s.booking_id: s for s in schedules}

    documents = db.execute(
        select(BookingDocument).where(BookingDocument.booking_id.in_(booking_ids))
    ).scalars().all()
    documents_map: dict[int, list[BookingDocument]] = {}
    for doc in documents:
        documents_map.setdefault(doc.booking_id, []).append(doc)

    response = []

    for booking in bookings:

        is_match = (
            booking.service_id,
            booking.sub_service_id,
        ) in service_set

        match_score = 100 if is_match else 0
        can_accept = is_match

        lead = _build_lead_response(
            booking=booking,
            site_detail=site_detail_map.get(booking.id),
            address=address_map.get(booking.id),
            contact_person=contact_map.get(booking.id),
            access_info=access_map.get(booking.id),
            schedule=schedule_map.get(booking.id),
            documents=documents_map.get(booking.id, []),
            match_score=match_score,
            can_accept=can_accept,
        )

        response.append(lead)

    return response


@router.get(
    "/{booking_id}",
    response_model=LeadResponse
)
async def get_lead_by_id(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    user = db.execute(
        select(User).where(User.email == current_user_email)
    ).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    booking = db.execute(
        select(Booking).where(Booking.id == booking_id)
    ).scalars().first()

    if not booking:
        raise HTTPException(status_code=404, detail="Lead not found")

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
        select(AccessInformation).where(AccessInformation.booking_id == booking.id)
    ).scalars().first()

    schedule = db.execute(
        select(BookingSchedule).where(BookingSchedule.booking_id == booking.id)
    ).scalars().first()

    documents = db.execute(
        select(BookingDocument).where(BookingDocument.booking_id == booking.id)
    ).scalars().all()

    profile = db.execute(
    select(UserProfile).where(UserProfile.user_id == user.id)
    ).scalars().first()

    engineer_services = db.execute(
        select(FieldEngineerService).where(
            FieldEngineerService.field_engineer_id == profile.id
        )
    ).scalars().all()

    service_set = {
        (service.service_id, service.sub_service_id)
        for service in engineer_services
    }

    is_match = (
        booking.service_id,
        booking.sub_service_id,
    ) in service_set

    match_score = 100 if is_match else 0
    can_accept = is_match

    return _build_lead_response(
    booking=booking,
    site_detail=site_detail,
    address=address,
    contact_person=contact_person,
    access_info=access_info,
    schedule=schedule,
    documents=documents,
    match_score=match_score,
    can_accept=can_accept,
)