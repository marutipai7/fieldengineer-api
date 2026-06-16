from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.utils.auth_utils import get_current_user_email

from app.profile.models import (
    User,
    UserProfile,
    UserAddress
)

from app.profile.schemas import (
    AddressCreateSchema,
    AddressUpdateSchema
)
router = APIRouter(
    prefix="/profile",
    tags=["Address"]
)
def get_user_and_profile(
    email: str,
    db: Session
):
    user = db.execute(
        select(User).where(User.email == email)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    profile = db.execute(
        select(UserProfile).where(
            UserProfile.user_id == user.id
        )
    ).scalars().first()

    return user, profile


@router.post("/address")
async def create_address(
    payload: AddressCreateSchema,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_email,
        db
    )

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Please complete profile first"
        )

    address = UserAddress(
        profile_id=profile.id,
        address_type=payload.address_type,
        name=payload.name,
        flat_no=payload.flat_no,
        street=payload.street,
        city=payload.city,
        state=payload.state,
        country=payload.country,
        postal_code=payload.postal_code,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_default=payload.is_default
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return {
        "message": "Address added successfully",
        "address_id": str(address.id)
    }
@router.get("/address")
async def get_addresses(
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_email,
        db
    )

    if not profile:
        return []

    addresses = db.execute(
        select(UserAddress).where(
            UserAddress.profile_id == profile.id
        )
    ).scalars().all()

    return [
        {
            "id": str(address.id),
            "address_type": address.address_type,
            "name": address.name,
            "flat_no": address.flat_no,
            "street": address.street,
            "city": address.city,
            "state": address.state,
            "country": address.country,
            "postal_code": address.postal_code,
            "latitude": address.latitude,
            "longitude": address.longitude,
            "is_default": address.is_default
        }
        for address in addresses
    ]
@router.put("/address/{address_id}")
async def update_address(
    address_id: UUID,
    payload: AddressUpdateSchema,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_email,
        db
    )

    address = db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.profile_id == profile.id
        )
    ).scalars().first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)

    return {
        "message": "Address updated successfully"
    }
@router.delete("/address/{address_id}")
async def delete_address(
    address_id: UUID,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_email,
        db
    )
    print("========== DEBUG ==========")
    print("Current User:", current_user_email)
    print("Profile ID:", profile.id)
    print("Address ID from URL:", address_id)


    address = db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.profile_id == profile.id
        )
    ).scalars().first()
    print("Address Found:", address)

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    db.delete(address)
    db.commit()

    return {
        "message": "Address deleted successfully"
    }