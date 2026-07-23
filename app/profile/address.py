from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select


from app.core.database import get_db
from app.utils.auth_utils import get_current_user_email

from app.profile.models import (
    User,
    UserProfile,
    UserAddress,
    UserRole
)
from app.profile.schemas import (
    AddressCreateSchema,
    AddressUpdateSchema,
    
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
    print("========== ADDRESS DEBUG ==========")
    print("Current Email:", current_user_email)
    print("User ID:", user.id)
    print("Role:", user.role)
    print("Profile:", profile)

    print("===================================")

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Please complete profile first"
        )

    address = UserAddress(
        profile_id=profile.id,
        address_type=payload.address_type,

        name=payload.address_line1 if user.role == UserRole.FIELD_ENGINEER else payload.name,

        flat_no=payload.area_locality if user.role == UserRole.FIELD_ENGINEER else payload.flat_no,

        street=payload.address_line2 if user.role == UserRole.FIELD_ENGINEER else payload.street,

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
        "address_id": address.id
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

    result = []

    for address in addresses:

        if user.role == UserRole.FIELD_ENGINEER:
            result.append({
                "id": address.id,
                "address_type": address.address_type,
                "country": address.country,
                "state": address.state,
                "postal_code": address.postal_code,
                "city": address.city,
                "area_locality": address.flat_no,
                "address_line1": address.name,
                "address_line2": address.street,
                "latitude": address.latitude,
                "longitude": address.longitude,
                "is_default": address.is_default
            })

        else:
            result.append({
                "id": address.id,
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
            })

    return result




@router.put("/address/{address_id}")
async def update_address(
    address_id: int,
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

    if payload.address_type is not None:
        address.address_type = payload.address_type

    # Customer / Field Engineer Mapping
    if user.role == UserRole.FIELD_ENGINEER:

        if payload.address_line1 is not None:
            address.name = payload.address_line1

        if payload.area_locality is not None:
            address.flat_no = payload.area_locality

        if payload.address_line2 is not None:
            address.street = payload.address_line2

    else:

        if payload.name is not None:
            address.name = payload.name

        if payload.flat_no is not None:
            address.flat_no = payload.flat_no

        if payload.street is not None:
            address.street = payload.street

    if payload.city is not None:
        address.city = payload.city

    if payload.state is not None:
        address.state = payload.state

    if payload.country is not None:
        address.country = payload.country

    if payload.postal_code is not None:
        address.postal_code = payload.postal_code

    if payload.latitude is not None:
        address.latitude = payload.latitude

    if payload.longitude is not None:
        address.longitude = payload.longitude

    if payload.is_default is not None:
        address.is_default = payload.is_default

    db.commit()
    db.refresh(address)

    return {
        "message": "Address updated successfully"
    }



@router.delete("/address/{address_id}")
async def delete_address(
    address_id: int,
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


