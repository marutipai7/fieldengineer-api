from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select


from app.core.database import get_db
from app.utils.auth_utils import get_current_user_email

from app.profile.models import (
    User,
    UserProfile,
    UserAddress
)

from app.profile.schemas import (
    UserProfileSchema,
    AddressCreateSchema,
    AddressUpdateSchema
)

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
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



@router.get("/me")
async def get_profile(
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_email,
        db
    )

    return {
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role.value,
        "profile": {
            "full_name": profile.full_name if profile else None,
            "date_of_birth": profile.date_of_birth if profile else None,
            "gender": profile.gender if profile else None,
            "profile_image": profile.profile_image if profile else None
        }
    }
@router.put("/update")
async def update_profile(
    payload: UserProfileSchema,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_email,
        db
    )

    if not profile:
        profile = UserProfile(
            user_id=user.id
        )
        db.add(profile)

    profile.full_name = payload.full_name
    profile.date_of_birth = payload.date_of_birth
    profile.gender = payload.gender
    profile.profile_image = payload.profile_image

    db.commit()

    return {
        "message": "Profile updated successfully"
    }

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

    return {
        "message": "Address added successfully"
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