from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.profile.models import User, UserProfile
from app.utils.auth_utils import get_current_user_object


router = APIRouter(
    prefix="/field-engineer",
    tags=["Field Engineer Work Preference"]
)


class WorkPreferenceRequest(BaseModel):
    work_preference: str


@router.put("/work-preference")
async def update_work_preference(
    data: WorkPreferenceRequest,
    current_user=Depends(get_current_user_object),
    db=Depends(get_db)
):
    user, profile = current_user

    if user.role != "field_engineer":
        raise HTTPException(
            status_code=403,
            detail="Only field engineers can update work preference"
        )

    if data.work_preference not in ["single", "team"]:
        raise HTTPException(
            status_code=400,
            detail="work_preference must be either 'single' or 'team'"
        )

    profile.work_preference = data.work_preference

    db.commit()
    db.refresh(profile)

    return {
        "success": True,
        "message": "Work preference updated successfully",
        "work_preference": profile.work_preference
    }

@router.get("/work-preference")
async def get_work_preference(
    current_user=Depends(get_current_user_object),
    db=Depends(get_db)
):
    user, profile = current_user

    if user.role != "field_engineer":
        raise HTTPException(
            status_code=403,
            detail="Only field engineers can access work preference"
        )

    return {
        "success": True,
        "work_preference": profile.work_preference
    }