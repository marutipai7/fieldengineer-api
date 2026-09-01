from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.profile.models import User, UserProfile
from app.booking.models import FieldEngineerService
from app.utils.auth_utils import get_current_user_mobile
from app.booking.schemas import LeadListResponse
from app.booking.models import BookingStatus

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
    response_model=list[LeadListResponse]
)
async def get_lead_list(
    db: Session = Depends(get_db),
    current_user_mobile: str = Depends(get_current_user_mobile)
):
    # 1. Get logged-in user
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

    # 2. Get Field Engineer profile
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user.id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Field Engineer profile not found"
        )

    # 3. Get services of this Field Engineer
    engineer_services = (
        db.query(FieldEngineerService)
        .filter(
            FieldEngineerService.field_engineer_id == profile.id
        )
        .all()
    )

    service_set = {
        (
            service.service_id,
            service.sub_service_id
        )
        for service in engineer_services
    }

    # 4. Get bookings
    bookings = (
        db.query(Booking)
        .order_by(Booking.created_at.desc())
        .all()
    )

    response = []

    for booking in bookings:

        # 5. Check service + sub-service match
        is_match = (
            booking.service_id,
            booking.sub_service_id
        ) in service_set

        # 6. Already accepted?
        already_accepted = (
            booking.accepted_field_engineer_id is not None
        )

        # 7. Can accept only if service matches
        #    and nobody has accepted it yet
        can_accept = (
            is_match
            and not already_accepted
            and booking.bid_status != "CLOSED"
        )

        response.append(
            LeadListResponse(
                booking_number=booking.booking_number,
                status=(
                    booking.booking_status.value
                    if booking.booking_status
                    else None
                ),
                can_accept=can_accept
            )
        )

    return response


@router.get(
    "/{booking_id}",
    response_model=LeadResponse
)
async def get_lead_by_id(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user_mobile: str = Depends(get_current_user_mobile)
):
    user = db.execute(
        select(User).where(User.mobile_number == current_user_mobile)
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

@router.post("/{booking_id}/accept")
async def accept_lead(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user_mobile: str = Depends(get_current_user_mobile)
):
    # 1. Find logged-in user
    user = db.execute(
        select(User).where(User.mobile_number == current_user_mobile)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # 2. Find field engineer profile
    profile = db.execute(
        select(UserProfile).where(
            UserProfile.user_id == user.id
        )
    ).scalars().first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Field Engineer profile not found"
        )

    # 3. Find the lead
    booking = db.execute(
        select(Booking).where(
            Booking.id == booking_id
        )
    ).scalars().first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    # 4. Check whether this engineer provides
    #    the service required by this lead
    engineer_service = db.execute(
        select(FieldEngineerService).where(
            FieldEngineerService.field_engineer_id == profile.id,
            FieldEngineerService.service_id == booking.service_id,
            FieldEngineerService.sub_service_id == booking.sub_service_id,
        )
    ).scalars().first()

    if not engineer_service:
        raise HTTPException(
            status_code=403,
            detail="You cannot accept this lead because the service does not match your added services"
        )

    # 5. Check whether somebody has already accepted it
    if booking.accepted_field_engineer_id is not None:
        raise HTTPException(
            status_code=409,
            detail="This lead has already been accepted"
        )

    # 6. Accept the lead
    booking.accepted_field_engineer_id = profile.id

    # 7. Update booking status
    booking.booking_status = BookingStatus.CONFIRMED

    # 8. Close the lead
    booking.bid_status = "CLOSED"

    db.commit()
    db.refresh(booking)

    # 9. Fetch related data
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

    contact_person = db.execute(
        select(SiteContactPerson).where(
            SiteContactPerson.booking_id == booking.id
        )
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
            "message": "Lead accepted successfully",
            "booking_id": booking.id,
            "booking_number": booking.booking_number
        }

@router.post("/{booking_id}/reject")
async def reject_lead(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user_mobile: str = Depends(get_current_user_mobile)
):
    user = (
        db.execute(
            select(User).where(
                User.mobile_number == current_user_mobile
            )
        )
        .scalars()
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    profile = (
        db.execute(
            select(UserProfile).where(
                UserProfile.user_id == user.id
            )
        )
        .scalars()
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Field Engineer profile not found"
        )

    booking = (
        db.execute(
            select(Booking).where(
                Booking.id == booking_id
            )
        )
        .scalars()
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    if booking.accepted_field_engineer_id is not None:
        raise HTTPException(
            status_code=409,
            detail="This lead has already been accepted"
        )

    return {
        "message": "Lead rejected successfully",
        "booking_id": booking.id,
        "booking_number": booking.booking_number
    }
