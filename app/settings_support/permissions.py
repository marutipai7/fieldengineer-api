from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.profile.models import User
from app.settings_support.models import UserPermission
from app.utils.auth_utils import get_current_user_mobile
from app.settings_support.schemas import PermissionUpdateSchema


router = APIRouter(
    prefix="/permissions",
    tags=["Settings & Support"],
)


def get_or_create_permissions(
    user_id: int,
    db: Session,
):
    permissions = (
        db.query(UserPermission)
        .filter(UserPermission.user_id == user_id)
        .first()
    )

    if not permissions:
        permissions = UserPermission(
            user_id=user_id,
            location=False,
            camera=False,
            microphone=False,
            notifications=False,
        )

        db.add(permissions)
        db.commit()
        db.refresh(permissions)

    return permissions


@router.get("/")
async def get_permissions(
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.mobile_number == current_user_mobile)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    permissions = get_or_create_permissions(
        user.id,
        db,
    )

    return {
        "success": True,
        "message": "Permissions fetched successfully",
        "data": {
            "location": permissions.location,
            "camera": permissions.camera,
            "microphone": permissions.microphone,
            "notifications": permissions.notifications,
        },
    }


@router.put("/")
async def update_permissions(
    payload: PermissionUpdateSchema,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.mobile_number == current_user_mobile)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    permissions = get_or_create_permissions(
        user.id,
        db,
    )

    if payload.location is not None:
        permissions.location = payload.location

    if payload.camera is not None:
        permissions.camera = payload.camera

    if payload.microphone is not None:
        permissions.microphone = payload.microphone

    if payload.notifications is not None:
        permissions.notifications = payload.notifications

    db.commit()
    db.refresh(permissions)

    return {
        "success": True,
        "message": "Permissions updated successfully",
        "data": {
            "location": permissions.location,
            "camera": permissions.camera,
            "microphone": permissions.microphone,
            "notifications": permissions.notifications,
        },
    }