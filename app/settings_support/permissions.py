from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.profile.models import User
from app.settings_support.models import UserPermission
from app.utils.auth_utils import get_current_user_mobile
from app.settings_support.schemas import PermissionUpdateSchema


router = APIRouter(
    prefix="/settings/permissions",
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
            communication=False,
            notifications=False,
            camera=False,
            media=False,
            audio=False,
            payment=False,
            security=False,
            network=False,
            device=False,
        )

        db.add(permissions)
        db.commit()
        db.refresh(permissions)

    return permissions


@router.get("")
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
            "communication": permissions.communication,
            "notifications": permissions.notifications,
            "camera": permissions.camera,
            "media": permissions.media,
            "audio": permissions.audio,
            "payment": permissions.payment,
            "security": permissions.security,
            "network": permissions.network,
            "device": permissions.device,
        },
    }


@router.put("")
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

    if payload.communication is not None:
        permissions.communication = payload.communication

    if payload.notifications is not None:
        permissions.notifications = payload.notifications

    if payload.camera is not None:
        permissions.camera = payload.camera

    if payload.media is not None:
        permissions.media = payload.media

    if payload.audio is not None:
        permissions.audio = payload.audio

    if payload.payment is not None:
        permissions.payment = payload.payment

    if payload.security is not None:
        permissions.security = payload.security

    if payload.network is not None:
        permissions.network = payload.network

    if payload.device is not None:
        permissions.device = payload.device

    db.commit()
    db.refresh(permissions)

    return {
        "success": True,
        "message": "Permissions updated successfully",
        "data": {
            "location": permissions.location,
            "communication": permissions.communication,
            "notifications": permissions.notifications,
            "camera": permissions.camera,
            "media": permissions.media,
            "audio": permissions.audio,
            "payment": permissions.payment,
            "security": permissions.security,
            "network": permissions.network,
            "device": permissions.device,
        },
    }