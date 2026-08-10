from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.auth_utils import get_current_user_email
from app.core.database import get_db

from app.profile.models import User, UserProfile

from app.booking.models import (
    Service,
    SubService,
    FieldEngineerService,
)

from app.booking.schemas import (
    ServiceResponse,
    SubServiceResponse,
    FieldEngineerServiceCreate,
    FieldEngineerServiceResponse,
)


router = APIRouter(
    prefix="/field-engineer",
    tags=["Field Engineer Services"]
)

@router.get(
    "/master/services",
    response_model=list[ServiceResponse]
)
def get_services(
    db: Session = Depends(get_db)
):
    return (
        db.query(Service)
        .order_by(Service.service_name)
        .all()
    )

@router.get(
    "/master/services/{service_id}/sub-services",
    response_model=list[SubServiceResponse]
)
def get_sub_services(
    service_id: int,
    db: Session = Depends(get_db)
):
    sub_services = (
        db.query(SubService)
        .filter(SubService.service_id == service_id)
        .order_by(SubService.sub_service_name)
        .all()
    )

    return sub_services

@router.post("/services")
def save_services(
    services: list[FieldEngineerServiceCreate],
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
):
    print("\n========== SAVE SERVICES ==========")
    print("AUTH EMAIL:", current_user_email)

    # 1. Get user
    user = (
        db.query(User)
        .filter(User.email == current_user_email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    print("USER ID:", user.id)
    print("USER EMAIL:", user.email)

    # 2. Get profile
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

    print("PROFILE ID:", profile.id)
    print("PROFILE USER ID:", profile.user_id)

    # 3. Save services
    for service in services:

        print(
            "REQUEST SERVICE:",
            "service_id =", service.service_id,
            "sub_service_id =", service.sub_service_id,
            "price =", service.price
        )

        existing_service = (
            db.query(FieldEngineerService)
            .filter(
                FieldEngineerService.field_engineer_id == profile.id,
                FieldEngineerService.service_id == service.service_id,
                FieldEngineerService.sub_service_id == service.sub_service_id,
            )
            .first()
        )

        if existing_service:

            print(
                "UPDATING EXISTING:",
                existing_service.id,
                "field_engineer_id =",
                existing_service.field_engineer_id
            )

            existing_service.price = service.price

        else:

            new_service = FieldEngineerService(
                field_engineer_id=profile.id,
                service_id=service.service_id,
                sub_service_id=service.sub_service_id,
                price=service.price,
            )

            db.add(new_service)

            print(
                "CREATING:",
                "field_engineer_id =", profile.id,
                "service_id =", service.service_id,
                "sub_service_id =", service.sub_service_id
            )

    db.commit()

    # 4. IMPORTANT: read database again AFTER commit
    saved_services = (
        db.query(FieldEngineerService)
        .filter(
            FieldEngineerService.field_engineer_id == profile.id
        )
        .all()
    )

    print("\n========== AFTER COMMIT ==========")

    for s in saved_services:
        print(
            "DB SERVICE:",
            "id =", s.id,
            "field_engineer_id =", s.field_engineer_id,
            "service_id =", s.service_id,
            "sub_service_id =", s.sub_service_id,
            "price =", s.price
        )

    print("===================================\n")

    return {
        "message": "Services saved successfully",
        "profile_id": profile.id,
        "services": [
            {
                "id": s.id,
                "field_engineer_id": s.field_engineer_id,
                "service_id": s.service_id,
                "sub_service_id": s.sub_service_id,
                "price": str(s.price),
            }
            for s in saved_services
        ]
    }

@router.get(
    "/services",
    response_model=list[FieldEngineerServiceResponse]
)
def get_services(
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
):
    # Get logged-in user
    user = (
        db.query(User)
        .filter(User.email == current_user_email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Get field engineer profile
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

    services = (
        db.query(
            FieldEngineerService.id,
            FieldEngineerService.service_id,
            Service.service_name,
            FieldEngineerService.sub_service_id,
            SubService.sub_service_name,
            FieldEngineerService.price,
        )
        .join(
            Service,
            Service.id == FieldEngineerService.service_id
        )
        .join(
            SubService,
            SubService.id == FieldEngineerService.sub_service_id
        )
        .filter(
            FieldEngineerService.field_engineer_id == profile.id
        )
        .all()
    )

    return [
        FieldEngineerServiceResponse(
            id=service.id,
            service_id=service.service_id,
            service_name=service.service_name,
            sub_service_id=service.sub_service_id,
            sub_service_name=service.sub_service_name,
            price=service.price,
        )
        for service in services
    ]

@router.put("/services/{id}")
def update_service(
    id: int,
    service: FieldEngineerServiceCreate,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
):
    # Get logged-in user
    user = (
        db.query(User)
        .filter(User.email == current_user_email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Get field engineer profile
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

    # Find the saved service
    existing_service = (
        db.query(FieldEngineerService)
        .filter(
            FieldEngineerService.id == id,
            FieldEngineerService.field_engineer_id == profile.id,
        )
        .first()
    )

    if not existing_service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    # Check if another record already has the same service + sub-service
    duplicate = (
        db.query(FieldEngineerService)
        .filter(
            FieldEngineerService.field_engineer_id == profile.id,
            FieldEngineerService.service_id == service.service_id,
            FieldEngineerService.sub_service_id == service.sub_service_id,
            FieldEngineerService.id != id,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="This service and sub-service already exist."
        )

    # Update values
    existing_service.service_id = service.service_id
    existing_service.sub_service_id = service.sub_service_id
    existing_service.price = service.price

    db.commit()
    db.refresh(existing_service)

    return {
        "message": "Service updated successfully"
    }

@router.delete("/services/{id}")
def delete_service(
    id: int,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
):
    # Get logged-in user
    user = (
        db.query(User)
        .filter(User.email == current_user_email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Get field engineer profile
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

    # Find the service
    service = (
        db.query(FieldEngineerService)
        .filter(
            FieldEngineerService.id == id,
            FieldEngineerService.field_engineer_id == profile.id,
        )
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    db.delete(service)
    db.commit()

    return {
        "message": "Service deleted successfully"
    }