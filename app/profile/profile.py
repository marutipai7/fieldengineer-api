import profile
import uuid
import secrets
from datetime import datetime, timedelta, date, time
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Request, Path, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from passlib.hash import pbkdf2_sha256
from fastapi import Form, File, UploadFile
import shutil
import os
from fastapi import Request
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import func
from pathlib import Path as FilePath
from uuid import uuid4
from app.booking.models import Booking
from app.payment_method.models import PaymentHistory
from app.profile.models import UserProfile, CustomerBankDetail

from app.booking.models import Booking, FieldEngineerService



from app.profile.schemas import VendorProfileSchema

from app.profile.schemas import (
    GSTVerifyRequest,
    GSTVerifyResponse,
    JoinCompanyRequest,
    LeaveCompanyRequest,
)
import re   

from app.profile.models import (
    User,
    UserRole,
    UserProfile,
    UserAddress,
    FieldEngineerDocument,
    FieldEngineerAvailability,
    FieldEngineerServiceArea,
    CustomerIdentity,
    CustomerBusiness,
    CustomerDocument,
    VendorProfile,
    VendorDocument,
    VendorServiceCoverage,
    VendorWorkforce,
    VendorBankDetail,
    VendorNotificationPreference,
    EngineerInvitation,
    Vendor,
    CustomerBankDetail,
)

from app.utils.auth_utils import (
    create_access_token,
    get_current_user_mobile,
    get_current_user_object,
    check_authorization_key
)

from app.profile.schemas import (
    # SigninSchema,
    FieldEngineerProfileSchema
)


from app.core.database import get_db
from app.utils.auth_utils import get_current_user_mobile
from app.core.config import settings

from app.profile.models import (
    User,
    UserRole,
    UserProfile,
    UserAddress,
    FieldEngineerDocument,
    FieldEngineerAvailability
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
# def get_user_and_profile(
#     email: str,
#     db: Session
# ):
#     user = db.execute(
#         select(User).where(User.email == email)
#     ).scalars().first()

#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="User not found"
#         )

#     profile = db.execute(
#         select(UserProfile).where(
#             UserProfile.user_id == user.id
#         )
#     ).scalars().first()

#     return user, profile


def get_user_and_profile(
    mobile: str,
    db: Session
):
    user = db.execute(
        select(User).where(User.mobile_number == mobile)
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
    current_user_email: str = Depends(get_current_user_mobile),
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

# @router.put("/update")
# async def update_profile(
#     payload: UserProfileSchema,
#     current_user_email: str = Depends(get_current_user_mobile),
#     db: Session = Depends(get_db)
# ):
#     user, profile = get_user_and_profile(
#         current_user_email,
#         db
#     )

#     if not profile:
#         profile = UserProfile(
#             user_id=user.id
#         )
#         db.add(profile)

#     profile.full_name = payload.full_name
#     profile.date_of_birth = payload.date_of_birth
#     profile.gender = payload.gender
#     profile.profile_image = payload.profile_image

#     db.commit()

#     return {
#         "message": "Profile updated successfully"
#     }



@router.post("/address")
async def create_address(
    payload: AddressCreateSchema,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_mobile,
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
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_mobile,
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
@router.get("/status")
async def get_profile_status(
    current_user_email: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_email,
        db
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    role = user.role.value

    # No common profile
    if not profile:
        return {
            "role": role,
            "status": "incomplete"
        }

    # USER
    if user.role == UserRole.USER:
        required_fields = [
            profile.full_name,
            profile.date_of_birth,
            profile.gender,
            profile.profile_image
        ]

    # FIELD ENGINEER
    elif user.role == UserRole.FIELD_ENGINEER:
        required_fields = [
            profile.full_name,
            profile.date_of_birth,
            profile.gender,
            profile.profile_image,
            profile.years_of_experience_id,
            profile.primary_specialization_id,
            profile.work_preference
        ]

    else:
        # Vendor will be handled using VendorProfile
        return {
            "role": role,
            "status": "incomplete"
        }

    is_complete = all(
        value is not None and value != ""
        for value in required_fields
    )

    return {
        "role": role,
        "status": "complete" if is_complete else "incomplete"
    }


@router.get("/get/{user_id}")
async def get_complete_profile(
    user_id: int,
    db: Session = Depends(get_db)
):

    # -------------------------
    # Get User
    # -------------------------
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # -------------------------
    # Get Profile
    # -------------------------
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user.id)
        .first()
    )

    if not profile:
        return {
            "user_id": user.id,
            "mobile_number": user.mobile_number,
            "phone_number": user.phone_number,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "profile": None
        }

    # -------------------------
    # Address
    # -------------------------
    addresses = (
        db.query(UserAddress)
        .filter(
            UserAddress.profile_id == profile.id
        )
        .all()
    )

    address_data = []

    for address in addresses:
        address_data.append({
            "address_id": address.id,
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

    # -------------------------
    # Vendor
    # -------------------------
    vendor_data = None

    if profile.vendor_id:
        vendor = (
            db.query(Vendor)
            .filter(Vendor.id == profile.vendor_id)
            .first()
        )

        if vendor:
            vendor_data = {
                "vendor_id": vendor.id,
                "vendor_name": vendor.vendor_name
            }

    # -------------------------
    # Years of Experience
    # -------------------------
    experience_data = None

    if profile.years_of_experience_id:
        experience = (
            db.query(YearsOfExperience)
            .filter(
                YearsOfExperience.id ==
                profile.years_of_experience_id
            )
            .first()
        )

        if experience:
            experience_data = {
                "id": experience.id,
                "experience": experience.experience
            }

    # -------------------------
    # Primary Specialization
    # -------------------------
    specialization_data = None

    if profile.primary_specialization_id:
        specialization = (
            db.query(PrimarySpecialization)
            .filter(
                PrimarySpecialization.id ==
                profile.primary_specialization_id
            )
            .first()
        )

        if specialization:
            specialization_data = {
                "id": specialization.id,
                "specialization": specialization.specialization
            }

    # -------------------------
    # Uploaded Documents
    # -------------------------
    documents_data = None

    if user.role == UserRole.FIELD_ENGINEER:

        documents = (
            db.query(FieldEngineerDocument)
            .filter(
                FieldEngineerDocument.user_profile_id ==
                profile.id
            )
            .first()
        )

        if documents:
            documents_data = {
                "identity_proof": documents.identity_proof,
                "education_certificate": documents.education_certificate,
                "work_company_id": documents.work_company_id,
                "certification": documents.certification,
                "experience_certificate": documents.experience_certificate,
                "driving_license": documents.driving_license
            }

    # -------------------------
    # Final Response
    # -------------------------
    return {
        "user": {
            "id": user.id,
            "mobile_number": user.mobile_number,
            "phone_number": user.phone_number,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        },

        "profile": {
            "id": profile.id,
            "full_name": profile.full_name,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "profile_image": profile.profile_image,
            "referral_code": profile.referral_code,
            "is_associated_with_vendor":
                profile.is_associated_with_vendor,
            "work_preference": profile.work_preference
        },

        "address": address_data,

        "vendor": vendor_data,

        "years_of_experience": experience_data,

        "primary_specialization": specialization_data,

        "uploaded_documents": documents_data
    }
    
@router.post(
    "/verify-gst",
    response_model=GSTVerifyResponse
)
def verify_gst(
    request: GSTVerifyRequest,
):
    gst_number = request.gst_number.strip().upper()

    # GSTIN format:
    # 2 digits state code
    # 10 characters PAN
    # 1 entity number
    # Z
    # 1 checksum character

    gst_pattern = (
        r"^[0-9]{2}"
        r"[A-Z]{5}[0-9]{4}[A-Z]"
        r"[1-9A-Z]"
        r"Z"
        r"[0-9A-Z]$"
    )

    if not re.match(gst_pattern, gst_number):
        return GSTVerifyResponse(
            gst_number=gst_number,
            is_valid=False,
            message="Invalid GST number format"
        )

    return GSTVerifyResponse(
        gst_number=gst_number,
        is_valid=True,
        message="GST number format is valid"
    )
@router.post("/join-company")
def join_company(
    request: JoinCompanyRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_object),
):
    user = current_user[0]

    # Logged-in user is the Field Engineer
    db_user = (
        db.query(User)
        .filter(User.id == user.id)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check vendor/company
    vendor = (
        db.query(Vendor)
        .filter(Vendor.id == request.vendor_id)
        .first()
    )

    if not vendor:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    # Find the logged-in user's profile
    field_engineer_profile = (
        db.query(UserProfile)
        .filter(
            UserProfile.user_id == user.id
        )
        .first()
    )

    if not field_engineer_profile:
        raise HTTPException(
            status_code=404,
            detail="Field engineer profile not found"
        )

    # Check if already associated
    if field_engineer_profile.is_associated_with_vendor:
        raise HTTPException(
            status_code=400,
            detail="User is already associated with a company"
        )

    # Join company
    field_engineer_profile.vendor_id = request.vendor_id
    field_engineer_profile.is_associated_with_vendor = True

    db.commit()
    db.refresh(field_engineer_profile)

    return {
        "message": "Successfully joined company",
        "user_id": user.id,
        "vendor_id": request.vendor_id,
        "field_engineer_id": field_engineer_profile.id,
        "company_name": vendor.vendor_name,
        "Role": user.role.value
    }
@router.post("/leave-company")
def leave_company(
    request: LeaveCompanyRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_object),
):
    user = current_user[0]

    # Check user
    db_user = (
        db.query(User)
        .filter(User.id == user.id)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Find logged-in user's profile
    field_engineer_profile = (
        db.query(UserProfile)
        .filter(
            UserProfile.user_id == user.id
        )
        .first()
    )

    if not field_engineer_profile:
        raise HTTPException(
            status_code=404,
            detail="Field engineer profile not found"
        )

    # Check current company
    if not field_engineer_profile.is_associated_with_vendor:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with any company"
        )

    # Make sure they are leaving the correct company
    if field_engineer_profile.vendor_id != request.vendor_id:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with this company"
        )

    # Leave company
    field_engineer_profile.vendor_id = None
    field_engineer_profile.is_associated_with_vendor = False

    db.commit()
    db.refresh(field_engineer_profile)

    return {
        "message": "Successfully left company",
        "user_id": user.id,
        "vendor_id": request.vendor_id,
        "field_engineer_id": field_engineer_profile.id,
        "Role": user.role.value
    }
# @router.post("/complete-profile")
# async def complete_field_engineer_profile(

#     full_name: str = Form(...),
#     date_of_birth: date = Form(None),
#     gender: str = Form(None),

#     is_associated_with_vendor: bool = Form(False),

#     vendor_id: int = Form(None),
#     years_of_experience_id: int = Form(None),
#     primary_specialization_id: int = Form(None),

#     primary_city: str = Form(None),
#     service_radius: int = Form(None),
#     preferred_work_areas: str = Form(None),
#     latitude: str = Form(None),
#     longitude: str = Form(None),

#     profile_image: UploadFile = File(None),

#     identity_proof: UploadFile = File(None),
#     education_certificate: UploadFile = File(None),
#     work_company_id: UploadFile = File(None),
#     certification: UploadFile = File(None),
#     experience_certificate: UploadFile = File(None),
#     driving_license: UploadFile = File(None),

#     current_user_email: str = Depends(get_current_user_email),
#     db: Session = Depends(get_db)
# ):
#     result = db.execute(
#         select(User).where(User.email == payload.email)
#     )

#     user = result.scalars().first()

#     if not user:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid credentials"
#         )

#     if user.role.value != "field_engineer":
#         raise HTTPException(
#             status_code=403,
#             detail="Only Field Engineer can login"
#         )

#     if not pbkdf2_sha256.verify(
#         payload.password,
#         user.password_hash
#     ):
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid credentials"
#         )

#     access_token = create_access_token(
#         {"sub": user.email}
#     )

#     return {
#         "message": "Field Engineer signed in successfully",
#         "access_token": access_token,
#         "token_type": "bearer",
#         "role": user.role.value
#     }

# @router.post("/complete-profile")
@router.post("/complete-profile/{step}")
async def complete_field_engineer_profile(
    request: Request,
  
    step: int = Path(...),

    # full_name: str = Form(...),
    full_name: Optional[str] = Form(None),
    date_of_birth: date = Form(None),
    gender: str = Form(None),

    # is_associated_with_vendor: bool = Form(False),
    is_associated_with_vendor: Optional[bool] = Form(None),

    vendor_id: int = Form(None),
    years_of_experience_id: int = Form(None),
    primary_specialization_id: int = Form(None),
    referral_code: Optional[str] = Form(None),
    service_id: Optional[int] = Form(None),
    sub_service_id: Optional[int] = Form(None),
    price: Optional[float] = Form(None),
    account_holder_name: Optional[str] = Form(None),
    bank_name: Optional[str] = Form(None),
    account_number: Optional[str] = Form(None),
    confirm_account_number: Optional[str] = Form(None),
    ifsc_code: Optional[str] = Form(None),
    local_code: Optional[str] = Form(None),
    bank_address: Optional[str] = Form(None),
    email_invoice_for_every_payout: Optional[bool] = Form(None),
    cancelled_cheque: UploadFile = File(None),


    primary_city: str = Form(None),
    service_radius: int = Form(None),
    preferred_work_areas: str = Form(None),
    latitude: str = Form(None),
    longitude: str = Form(None),

    profile_image: UploadFile = File(None),
    day_of_week: int = Form(None),
    start_time: time = Form(None),
    end_time: time = Form(None),
    # is_available: bool = Form(True),
    is_available: Optional[bool] = Form(None),

    identity_proof: UploadFile = File(None),
    education_certificate: UploadFile = File(None),
    work_company_id: UploadFile = File(None),
    certification: UploadFile = File(None),
    experience_certificate: UploadFile = File(None),
    driving_license: UploadFile = File(None),

    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    print("========== FE COMPLETE PROFILE API CALLED ==========")
    form = await request.form()

    print("===== FORM DATA =====")

    for key, value in form.items():
      print(key, "=", value)

    print("=====================")
    

    user = db.execute(
        select(User).where(
            User.mobile_number == current_user_mobile
        )
    ).scalars().first()
    print("========== POST USER ==========")
    print("Current Mobile Number:", current_user_mobile)
    print("User ID:", user.id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role.value != "field_engineer":
        raise HTTPException(
            status_code=403,
            detail="Only Field Engineer can complete profile"
        )

    profile = db.execute(
        select(UserProfile).where(
            UserProfile.user_id == user.id
        )
    ).scalars().first()

    if not profile:
        profile = UserProfile(
            user_id=user.id
        )
        db.add(profile)
        db.flush()
        print("Profile ID:", profile.id)
        print("==============================")
      # ==================================================
    # STEP 1 - COMPLETE YOUR PROFILE
    # ==================================================
    if step == 1:

        if full_name is not None:
            profile.full_name = full_name

        if date_of_birth is not None:
            profile.date_of_birth = date_of_birth

        if gender is not None:
            profile.gender = gender

        # if is_associated_with_vendor is not None:
        #     profile.is_associated_with_vendor = is_associated_with_vendor

        # if vendor_id is not None:
        #     profile.vendor_id = vendor_id
        if is_associated_with_vendor is not None:
            profile.is_associated_with_vendor = is_associated_with_vendor

            if not is_associated_with_vendor:
                profile.vendor_id = None
            elif vendor_id is not None:
                profile.vendor_id = vendor_id


        if years_of_experience_id is not None:
            profile.years_of_experience_id = years_of_experience_id

        if primary_specialization_id is not None:
            profile.primary_specialization_id = primary_specialization_id


        if referral_code is not None:
            profile.referral_code = referral_code

        if profile_image:
            os.makedirs("uploads/field_engineer", exist_ok=True)

            image_path = f"uploads/field_engineer/{profile_image.filename}"

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(profile_image.file, buffer)

            profile.profile_image = image_path

        db.commit()
        db.refresh(profile)

        return {
            "success": True,
            "step": 1,
            "message": "Step 1 completed successfully.",
            "profile_id": profile.id
        }

    # ==================================================
    # STEP 2 - UPLOAD DOCUMENTS
    # ==================================================
    elif step == 2:

        document = db.execute(
            select(FieldEngineerDocument).where(
                FieldEngineerDocument.user_profile_id == profile.id
            )
        ).scalars().first()

        if not document:
            document = FieldEngineerDocument(
                user_profile_id=profile.id
            )
            db.add(document)

        os.makedirs("uploads/field_engineer", exist_ok=True)

        if identity_proof:
            identity_path = f"uploads/field_engineer/{identity_proof.filename}"

            with open(identity_path, "wb") as buffer:
                shutil.copyfileobj(identity_proof.file, buffer)

            document.identity_proof = identity_path

        if education_certificate:
            education_path = f"uploads/field_engineer/{education_certificate.filename}"

            with open(education_path, "wb") as buffer:
                shutil.copyfileobj(education_certificate.file, buffer)

            document.education_certificate = education_path

        if work_company_id:
            company_path = f"uploads/field_engineer/{work_company_id.filename}"

            with open(company_path, "wb") as buffer:
                shutil.copyfileobj(work_company_id.file, buffer)

            document.work_company_id = company_path

        if certification:
            certification_path = f"uploads/field_engineer/{certification.filename}"

            with open(certification_path, "wb") as buffer:
                shutil.copyfileobj(certification.file, buffer)

            document.certification = certification_path

        if experience_certificate:
            experience_path = f"uploads/field_engineer/{experience_certificate.filename}"

            with open(experience_path, "wb") as buffer:
                shutil.copyfileobj(experience_certificate.file, buffer)

            document.experience_certificate = experience_path

        if driving_license:
            license_path = f"uploads/field_engineer/{driving_license.filename}"

            with open(license_path, "wb") as buffer:
                shutil.copyfileobj(driving_license.file, buffer)

            document.driving_license = license_path

        db.commit()
        db.refresh(profile)

        return {
            "success": True,
            "step": 2,
            "message": "Step 2 completed successfully.",
            "profile_id": profile.id
        }
        # ==================================================
    # STEP 3 - SERVICE AREA
    # ==================================================
    elif step == 3:

        service_area = db.execute(
            select(FieldEngineerServiceArea).where(
                FieldEngineerServiceArea.field_engineer_id == profile.id
            )
        ).scalars().first()

        if not service_area:
            service_area = FieldEngineerServiceArea(
                field_engineer_id=profile.id
            )
            db.add(service_area)

        if primary_city is not None:
            service_area.primary_city = primary_city

        if service_radius is not None:
            service_area.service_radius = service_radius

        if preferred_work_areas is not None:
            service_area.preferred_work_areas = preferred_work_areas

        if latitude is not None:
            service_area.latitude = latitude

        if longitude is not None:
            service_area.longitude = longitude

        db.commit()
        db.refresh(profile)

        return {
            "success": True,
            "step": 3,
            "message": "Step 3 completed successfully.",
            "profile_id": profile.id
        }

    # ==================================================
    # STEP 4 - SET YOUR AVAILABILITY
    # ==================================================
    elif step == 4:

        availability = db.execute(
            select(FieldEngineerAvailability).where(
                FieldEngineerAvailability.field_engineer_id == profile.id
            )
        ).scalars().first()

        if not availability:
            availability = FieldEngineerAvailability(
                field_engineer_id=profile.id
            )
            db.add(availability)

        if day_of_week is not None:
            availability.day_of_week = day_of_week

        if start_time is not None:
            availability.start_time = start_time

        if end_time is not None:
            availability.end_time = end_time

        # availability.is_available = is_available
        if is_available is not None:
            availability.is_available = is_available

        print("========== AVAILABILITY ==========")
        print("Profile ID:", profile.id)
        print("Day:", availability.day_of_week)
        print("Start:", availability.start_time)
        print("End:", availability.end_time)
        print("Available:", availability.is_available)
        print("==================================")

        db.commit()
        db.refresh(profile)

        return {
            "success": True,
            "step": 4,
            "message": "Step 4 completed successfully.",
            "profile_id": profile.id
        }
    
    elif step == 5:
        if service_id is None:
            raise HTTPException(status_code=400, detail="service_id is required")

        if sub_service_id is None:
            raise HTTPException(status_code=400, detail="sub_service_id is required")

        if price is None:
           raise HTTPException(status_code=400, detail="price is required")

        existing_service = db.query(FieldEngineerService).filter(
            FieldEngineerService.field_engineer_id == profile.id,
            FieldEngineerService.service_id == service_id,
            FieldEngineerService.sub_service_id == sub_service_id
        ).first()

        if existing_service:
            existing_service.price = price
        else:
            new_service = FieldEngineerService(
               field_engineer_id=profile.id,
               service_id=service_id,
               sub_service_id=sub_service_id,
               price=price
            )
            db.add(new_service)

        db.commit()

        return {
           "success": True,
            "step": step,
            "message": "Service and rate saved successfully",
            "profile_id": profile.id,
            "service_id": service_id,
            "sub_service_id": sub_service_id,
            "price": price
        }
    

    elif step == 6:
        # if account_number and confirm_account_number:
        #    if account_number != confirm_account_number:
        #         raise HTTPException(
        #            status_code=400,
        #            detail="Account number and confirm account number do not match"
        #         )
        if account_number is not None:
            if confirm_account_number is None:
                raise HTTPException(
                   status_code=400,
                   detail="Confirm account number is required"
                )

            if account_number != confirm_account_number:
                raise HTTPException(
                    status_code=400,
                    detail="Account number and confirm account number do not match"
                )

        bank_detail = db.query(CustomerBankDetail).filter(
           CustomerBankDetail.user_profile_id == profile.id
        ).first()

        if not bank_detail:
            bank_detail = CustomerBankDetail(
               user_profile_id=profile.id
            )
            db.add(bank_detail)

        if account_holder_name is not None:
            bank_detail.account_holder_name = account_holder_name

        if bank_name is not None:
            bank_detail.bank_name = bank_name

        if account_number is not None:
            bank_detail.account_number = account_number

        if ifsc_code is not None:
            bank_detail.ifsc_code = ifsc_code

        if local_code is not None:
            bank_detail.local_code = local_code

        if bank_address is not None:
            bank_detail.bank_address = bank_address

        if email_invoice_for_every_payout is not None:
            bank_detail.email_invoice_for_every_payout = (
                email_invoice_for_every_payout
            )

        db.commit()
        db.refresh(bank_detail)

        return {
           "success": True,
            "step": step,
            "message": "Bank and payout details saved successfully",
            "profile_id": profile.id,
            "account_holder_name": bank_detail.account_holder_name,
            "bank_name": bank_detail.bank_name,
            "account_number": bank_detail.account_number,
            "ifsc_code": bank_detail.ifsc_code,
            "local_code": bank_detail.local_code,
            "bank_address": bank_detail.bank_address,
            "email_invoice_for_every_payout": bank_detail.email_invoice_for_every_payout
        }

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid step."
        )








@router.get("/field-engineer/me")
async def get_field_engineer_profile(
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_mobile,
        db
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    document = db.execute(
        select(FieldEngineerDocument).where(
            FieldEngineerDocument.user_profile_id == profile.id
        )
    ).scalars().first()

    service_area = db.execute(
        select(FieldEngineerServiceArea).where(
            FieldEngineerServiceArea.field_engineer_id == profile.id
        )
    ).scalars().first()

    availability = db.execute(
        select(FieldEngineerAvailability).where(
            FieldEngineerAvailability.field_engineer_id == profile.id
        )
    ).scalars().all()


    bank_detail = db.execute(
        select(CustomerBankDetail).where(
            CustomerBankDetail.user_profile_id == profile.id
        )
    ).scalars().first()
    




    services = db.execute(
        select(FieldEngineerService).where(
            FieldEngineerService.field_engineer_id == profile.id
        )
    ).scalars().all()

    return {
        "email": user.email,
        # "phone_number": user.phone_number,
         "phone_number": user.phone_number or user.mobile_number,
        
        "role": user.role.value,

        "profile": {
            "full_name": profile.full_name,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "profile_image": profile.profile_image,
            "is_associated_with_vendor": profile.is_associated_with_vendor,
            "vendor_id": profile.vendor_id,
            "years_of_experience_id": profile.years_of_experience_id,
            "primary_specialization_id": profile.primary_specialization_id
        },

        "documents": {
            "identity_proof": document.identity_proof if document else None,
            "education_certificate": document.education_certificate if document else None,
            "work_company_id": document.work_company_id if document else None,
            "certification": document.certification if document else None,
            "experience_certificate": document.experience_certificate if document else None,
            "driving_license": document.driving_license if document else None
        },

        "service_area": {
            "primary_city": service_area.primary_city if service_area else None,
            "service_radius": service_area.service_radius if service_area else None,
            "preferred_work_areas": service_area.preferred_work_areas if service_area else None,
            "latitude": service_area.latitude if service_area else None,
            "longitude": service_area.longitude if service_area else None
        },


    
        "services": [
           {
                "id": service.id,
                "service_id": service.service_id,
                "sub_service_id": service.sub_service_id,
                "price": float(service.price) if service.price is not None else None
            }
            for service in services
        ],
        



        "bank_details": {
            "account_holder_name": bank_detail.account_holder_name if bank_detail else None,
            "bank_name": bank_detail.bank_name if bank_detail else None,
            "account_number": bank_detail.account_number if bank_detail else None,
            "ifsc_code": bank_detail.ifsc_code if bank_detail else None,
            "local_code": bank_detail.local_code if bank_detail else None,
            "bank_address": bank_detail.bank_address if bank_detail else None,
            "email_invoice_for_every_payout": (
                bank_detail.email_invoice_for_every_payout
                if bank_detail else False
            )
        },
        










        "availability": [
            {
                "day_of_week": item.day_of_week,
                "start_time": item.start_time,
                "end_time": item.end_time,
                "is_available": item.is_available
            }
            for item in availability
        ]
    }

# @router.put("/profile")
@router.put("/update")
async def update_field_engineer_profile(
    full_name: str = Form(None),
    date_of_birth: date = Form(None),
    email: Optional[str] = Form(None),
    
    gender: str = Form(None),
    is_associated_with_vendor: bool = Form(None),
    # vendor_id: Optional[int] = Form(None),
    # years_of_experience_id: int = Form(None),
    # primary_specialization_id: int = Form(None),

    # profile_image: UploadFile = File(None),

    vendor_id: Optional[int] = Form(None),
    years_of_experience_id: int = Form(None),
    primary_specialization_id: int = Form(None),
    referral_code: Optional[str] = Form(None),
    service_id: Optional[int] = Form(None),
    sub_service_id: Optional[int] = Form(None),
    price: Optional[float] = Form(None),
    account_holder_name: Optional[str] = Form(None),
    bank_name: Optional[str] = Form(None),
    account_number: Optional[str] = Form(None),
    confirm_account_number: Optional[str] = Form(None),
    ifsc_code: Optional[str] = Form(None),
    local_code: Optional[str] = Form(None),
    bank_address: Optional[str] = Form(None),
    email_invoice_for_every_payout: Optional[bool] = Form(None),
    cancelled_cheque: UploadFile = File(None),

    # STEP 3 - SERVICE AREA
    primary_city: str = Form(None),
    service_radius: int = Form(None),
    preferred_work_areas: str = Form(None),
    latitude: str = Form(None),
    longitude: str = Form(None),

    # STEP 4 - AVAILABILITY
    day_of_week: int = Form(None),
    start_time: time = Form(None),
    end_time: time = Form(None),
    # is_available: bool = Form(True),
    is_available: Optional[bool] = Form(None),

    profile_image: UploadFile = File(None),
    identity_proof: UploadFile = File(None),
    education_certificate: UploadFile = File(None),
    work_company_id: UploadFile = File(None),
    certification: UploadFile = File(None),
    experience_certificate: UploadFile = File(None),
    driving_license: UploadFile = File(None),

    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_mobile,
        db
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    

    if email is not None:
        user.email = email
    # ----------------------------
    # Update Profile
    # ----------------------------
    # profile.full_name = full_name
    # profile.date_of_birth = date_of_birth   
    # profile.gender = gender
    # profile.is_associated_with_vendor = is_associated_with_vendor
    # profile.vendor_id = vendor_id
    # profile.years_of_experience_id = years_of_experience_id
    # profile.primary_specialization_id = primary_specialization_id



    if full_name is not None:
        profile.full_name = full_name

    if date_of_birth is not None:
        profile.date_of_birth = date_of_birth

    if gender is not None:
        profile.gender = gender

    if is_associated_with_vendor is not None:
        profile.is_associated_with_vendor = is_associated_with_vendor

        if not is_associated_with_vendor:
            profile.vendor_id = None
        elif vendor_id is not None:
           profile.vendor_id = vendor_id

    if years_of_experience_id is not None:
        profile.years_of_experience_id = years_of_experience_id

    if primary_specialization_id is not None:
        profile.primary_specialization_id = primary_specialization_id


    if referral_code is not None:
        profile.referral_code = referral_code

    if profile_image:
        profile.profile_image = save_upload_file(
           profile_image,
           "uploads/field_engineer"
        )
    # ----------------------------
    # Update Documents
    # ----------------------------
    document = db.execute(
        select(FieldEngineerDocument).where(
           FieldEngineerDocument.user_profile_id == profile.id
        )
    ).scalars().first()

    if not document:
        document = FieldEngineerDocument(
            user_profile_id=profile.id
        )
        db.add(document)

    if identity_proof:
        document.identity_proof = save_upload_file(
            identity_proof,
            "uploads/field_engineer"
        )

    if education_certificate:
        document.education_certificate = save_upload_file(
           education_certificate,
           "uploads/field_engineer"
        )

    if work_company_id:
        document.work_company_id = save_upload_file(
           work_company_id,
           "uploads/field_engineer"
        )

    if certification:
        document.certification = save_upload_file(
            certification,
            "uploads/field_engineer"
        )

    if experience_certificate:
        document.experience_certificate = save_upload_file(
             experience_certificate,
             "uploads/field_engineer"
        )

    if driving_license:
        document.driving_license = save_upload_file(
            driving_license,
            "uploads/field_engineer"
        )
    # ----------------------------
    # Update Service Area
    # ----------------------------

    service_area = db.execute(
        select(FieldEngineerServiceArea).where(
            FieldEngineerServiceArea.field_engineer_id == profile.id
        )
    ).scalars().first()

    if not service_area:
        service_area = FieldEngineerServiceArea(
            field_engineer_id=profile.id
        )
        db.add(service_area)

    # service_area.primary_city = primary_city
    # service_area.service_radius = service_radius
    # service_area.preferred_work_areas = preferred_work_areas
    # service_area.latitude = latitude
    # service_area.longitude = longitude
    


    if primary_city is not None:
        service_area.primary_city = primary_city

    if service_radius is not None:
        service_area.service_radius = service_radius

    if preferred_work_areas is not None:
        service_area.preferred_work_areas = preferred_work_areas

    if latitude is not None:
        service_area.latitude = latitude

    if longitude is not None:
        service_area.longitude = longitude
    # ----------------------------
    # Update Availability
    # ----------------------------

    availability = db.execute(
        select(FieldEngineerAvailability).where(
            FieldEngineerAvailability.field_engineer_id == profile.id
        )
    ).scalars().first()

    if not availability:
        availability = FieldEngineerAvailability(
           field_engineer_id=profile.id
        )
        db.add(availability)

    # availability.day_of_week = day_of_week
    # availability.start_time = start_time
    # availability.end_time = end_time
    # availability.is_available = is_available

    if day_of_week is not None:
        availability.day_of_week = day_of_week

    if start_time is not None:
        availability.start_time = start_time

    if end_time is not None:
       availability.end_time = end_time

    if is_available is not None:
       availability.is_available = is_available
    # # ----------------------------
    # Update Availability
    # ----------------------------
    # if payload.availability:

    #     db.query(FieldEngineerAvailability).filter(
    #         FieldEngineerAvailability.field_engineer_id == profile.id
    #     ).delete()

    #     for item in payload.availability:

    #         availability = FieldEngineerAvailability(
    #             field_engineer_id=profile.id,
    #             day_of_week=item.day_of_week,
    #             start_time=item.start_time,
    #             end_time=item.end_time,
    #             is_available=item.is_available
    #         )

    #         db.add(availability)

    
    if service_id is not None and sub_service_id is not None and price is not None:
        existing_service = db.query(FieldEngineerService).filter(
           FieldEngineerService.field_engineer_id == profile.id,
           FieldEngineerService.service_id == service_id,
           FieldEngineerService.sub_service_id == sub_service_id
        ).first()

        if existing_service:
            existing_service.price = price
        else:
            new_service = FieldEngineerService(
               field_engineer_id=profile.id,
               service_id=service_id,
               sub_service_id=sub_service_id,
               price=price
            )
            db.add(new_service)


    if any([
        account_holder_name is not None,
        bank_name is not None,
        account_number is not None,
        ifsc_code is not None,
        local_code is not None,
        bank_address is not None,
        email_invoice_for_every_payout is not None
    ]):
        
    #   if account_number is not None and confirm_account_number is not None:
    #     if account_number != confirm_account_number:
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Account number and confirm account number do not match"
    #         )
        if account_number is not None:
            if confirm_account_number is None:
                raise HTTPException(
                   status_code=400,
                   detail="confirm_account_number is required"
                )

            if account_number != confirm_account_number:
                raise HTTPException(
                    status_code=400,
                    detail="Account number and confirm account number do not match"
                )

    bank_detail = db.query(CustomerBankDetail).filter(
        CustomerBankDetail.user_profile_id == profile.id
    ).first()

    if not bank_detail:
        bank_detail = CustomerBankDetail(
            user_profile_id=profile.id
        )
        db.add(bank_detail)

    if account_holder_name is not None:
        bank_detail.account_holder_name = account_holder_name

    if bank_name is not None:
        bank_detail.bank_name = bank_name

    if account_number is not None:
        bank_detail.account_number = account_number

    if ifsc_code is not None:
        bank_detail.ifsc_code = ifsc_code

    if local_code is not None:
        bank_detail.local_code = local_code

    if bank_address is not None:
        bank_detail.bank_address = bank_address

    if email_invoice_for_every_payout is not None:
        bank_detail.email_invoice_for_every_payout = (
            email_invoice_for_every_payout
        )
    


    db.commit()
    db.refresh(profile)

    # return {
    #     "message": "Field Engineer profile updated successfully",
    #     "profile_id": profile.id
    # }


    return {
        "message": "Field Engineer profile updated successfully",
        "profile": {
            "id": profile.id,
            "full_name": profile.full_name,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "is_associated_with_vendor": profile.is_associated_with_vendor,
            "vendor_id": profile.vendor_id,
            "years_of_experience_id": profile.years_of_experience_id,
            "primary_specialization_id": profile.primary_specialization_id,
            "referral_code": profile.referral_code,
            "profile_image": profile.profile_image,
        }
    }
    
    

# @router.post("/vendor/signin")
# async def vendor_signin(
#     payload: SigninSchema,
#     db: Session = Depends(get_db)
# ):
#     result = db.execute(
#         select(User).where(User.email == payload.email)
#     )

#     user = result.scalars().first()

#     if not user:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid credentials"
#         )

#     if user.role != UserRole.VENDOR:
#         raise HTTPException(
#             status_code=403,
#             detail="Only Vendor can login"
#         )

#     if not pbkdf2_sha256.verify(
#         payload.password,
#         user.password_hash
#     ):
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid credentials"
#         )

#     access_token = create_access_token(
#         {"sub": user.email}
#     )

#     return {
#         "message": "Vendor signed in successfully",
#         "access_token": access_token,
#         "token_type": "bearer",
#         "role": user.role.value
#     }


# @router.post("/vendor/complete-profile")
@router.post("/vendor/complete-profile/{step}")
async def vendor_complete_profile(
    
    request: Request,

    step: int = Path(..., ge=1, le=6),

    company_name: str = Form(...),
    owner_manager_name: str = Form(...),

    # vendor_type: str = Form(...),
    vendor_type: str = Form(None),
    # legal_business_name: str = Form(...),
    legal_business_name: str = Form(None),
    # business_type: str = Form(...),
    business_type: str = Form(None),

    industry: str = Form(None),

    company_registration_number: str = Form(None),
    gst_number: str = Form(None),
    pan_number: str = Form(None),

    website: str = Form(None),
    years_in_business: int = Form(None),
    employee_count: int = Form(None),

    primary_service_category: str = Form(None),
    about_business: str = Form(None),

    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    pincode: str = Form(None),

    timezone: str = Form(None),
    working_hours: str = Form(None),
    # service_state: str = Form(None),
    # service_city: str = Form(None),
    # service_radius: int = Form(None),

    # profile_image: UploadFile = File(...),

    # gst_certificate: UploadFile = File(...),
    # pan_card: UploadFile = File(...),
    # registration_certificate: UploadFile = File(...),
    # cancelled_cheque: UploadFile = File(...),
    # other_document: UploadFile = File(...),


    profile_image: UploadFile = File(None),

    gst_certificate: UploadFile = File(None),
    pan_card: UploadFile = File(None),
    registration_certificate: UploadFile = File(None),
    cancelled_cheque: UploadFile = File(None),
    # other_document: UploadFile = File(None),

    # current_user_email: str = Depends(get_current_user_email),
    # db: Session = Depends(get_db)

    other_document: UploadFile = File(None),

    # =========================
    # STEP 4 - SERVICE COVERAGE
    # =========================
    service_state: str = Form(None),
    service_city: str = Form(None),
    service_radius: int = Form(None),
    # ----------------------------
    # STEP 5 - Workforce
    # ----------------------------

    total_engineers: int = Form(None),
    certified_engineers: int = Form(None),
    support_staff: int = Form(None),
    

    # ----------------------------
    # STEP 6 - Bank Details
    # ----------------------------

    account_holder_name: str = Form(None),
    bank_name: str = Form(None),
    account_number: str = Form(None),
    ifsc_code: str = Form(None),
    branch_name: str = Form(None),

    # ----------------------------
    # STEP 7 - Notification Preferences
    # ----------------------------

    email_notification: bool = Form(True),
    sms_notification: bool = Form(False),
    push_notification: bool = Form(True),

   

    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    
    form = await request.form()

    print("========== FORM DATA ==========")

    for key, value in form.items():
       print(key, "=", value)

    print("===============================")
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

    if user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=403,
            detail="Only Vendor can complete profile"
        )

    profile = db.execute(
        select(VendorProfile).where(
            VendorProfile.user_id == user.id
        )
    ).scalars().first()

    if not profile:
        profile = VendorProfile(
            user_id=user.id
        )
        db.add(profile)
        db.flush()
        # ----------------------------
    # =====================================
    # STEP 1 - VENDOR PROFILE
    # =====================================
    if step == 1:

        profile.company_name = company_name
        profile.owner_manager_name = owner_manager_name
        profile.vendor_type = vendor_type
        profile.legal_business_name = legal_business_name
        profile.business_type = business_type
        profile.industry = industry

        profile.company_registration_number = company_registration_number
        profile.gst_number = gst_number
        profile.pan_number = pan_number

        profile.website = website
        profile.years_in_business = years_in_business
        profile.employee_count = employee_count

        profile.primary_service_category = primary_service_category
        profile.about_business = about_business

        profile.address = address
        profile.city = city
        profile.state = state
        profile.pincode = pincode

        profile.timezone = timezone
        profile.working_hours = working_hours

        if profile_image:

            os.makedirs("uploads/vendor", exist_ok=True)

            image_path = f"uploads/vendor/{profile_image.filename}"

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(profile_image.file, buffer)

            profile.profile_image = image_path

        db.commit()
        db.refresh(profile)

        return {
            "success": True,
            "step": 1,
            "message": "Step 1 completed successfully.",
            "profile_id": profile.id
        }


    # =====================================
    # STEP 2 - DOCUMENTS
    # =====================================
    elif step == 2:

        document = db.execute(
            select(VendorDocument).where(
                VendorDocument.vendor_profile_id == profile.id
            )
        ).scalars().first()

        if not document:
            document = VendorDocument(
                vendor_profile_id=profile.id
            )
            db.add(document)

        os.makedirs("uploads/vendor", exist_ok=True)

        if gst_certificate:
            gst_path = f"uploads/vendor/{gst_certificate.filename}"

            with open(gst_path, "wb") as buffer:
                shutil.copyfileobj(gst_certificate.file, buffer)

            document.gst_certificate = gst_path

        if pan_card:
            pan_path = f"uploads/vendor/{pan_card.filename}"

            with open(pan_path, "wb") as buffer:
                shutil.copyfileobj(pan_card.file, buffer)

            document.pan_card = pan_path

        if registration_certificate:
            reg_path = f"uploads/vendor/{registration_certificate.filename}"

            with open(reg_path, "wb") as buffer:
                shutil.copyfileobj(registration_certificate.file, buffer)

            document.registration_certificate = reg_path

        if cancelled_cheque:
            cheque_path = f"uploads/vendor/{cancelled_cheque.filename}"

            with open(cheque_path, "wb") as buffer:
                shutil.copyfileobj(cancelled_cheque.file, buffer)

            document.cancelled_cheque = cheque_path

        if other_document:
            other_path = f"uploads/vendor/{other_document.filename}"

            with open(other_path, "wb") as buffer:
                shutil.copyfileobj(other_document.file, buffer)

            document.other_document = other_path

        db.commit()
        db.refresh(profile)

        return {
            "success": True,
            "step": 2,
            "message": "Step 2 completed successfully.",
            "profile_id": profile.id
        }
    # =====================================
    # STEP 3 - SERVICE COVERAGE
    # =====================================
    elif step == 3:

        coverage = db.execute(
            select(VendorServiceCoverage).where(
                VendorServiceCoverage.vendor_profile_id == profile.id
            )
        ).scalars().first()

        if not coverage:
            coverage = VendorServiceCoverage(
                vendor_profile_id=profile.id
            )
            db.add(coverage)

        if service_state is not None:
            coverage.state = service_state

        if service_city is not None:
            coverage.city = service_city

        if service_radius is not None:
            coverage.service_radius = service_radius

        db.commit()
        db.refresh(profile)

        return {
            "success": True,
            "step": 3,
            "message": "Step 3 completed successfully.",
            "profile_id": profile.id
        }


    # =====================================
    # STEP 4 - WORKFORCE
    # =====================================
    elif step == 4:

        workforce = db.execute(
            select(VendorWorkforce).where(
                VendorWorkforce.vendor_profile_id == profile.id
            )
        ).scalars().first()

        if not workforce:
            workforce = VendorWorkforce(
                vendor_profile_id=profile.id
            )
            db.add(workforce)

        if total_engineers is not None:
            workforce.total_engineers = total_engineers

        if certified_engineers is not None:
            workforce.certified_engineers = certified_engineers

        if support_staff is not None:
            workforce.support_staff = support_staff

        db.commit()
        db.refresh(profile)

        return {
            "success": True,
            "step": 4,
            "message": "Step 4 completed successfully.",
            "profile_id": profile.id
        }
        # =====================================
    # STEP 5 - BANK DETAILS
    # =====================================
    elif step == 5:

        bank = db.execute(
            select(VendorBankDetail).where(
                VendorBankDetail.vendor_profile_id == profile.id
            )
        ).scalars().first()

        if not bank:
            bank = VendorBankDetail(
                vendor_profile_id=profile.id
            )
            db.add(bank)

        if account_holder_name is not None:
            bank.account_holder_name = account_holder_name

        if bank_name is not None:
            bank.bank_name = bank_name

        if account_number is not None:
            bank.account_number = account_number

        if ifsc_code is not None:
            bank.ifsc_code = ifsc_code

        if branch_name is not None:
            bank.branch_name = branch_name

        db.commit()
        db.refresh(profile)

        return {
            "success": True,
            "step": 5,
            "message": "Step 5 completed successfully.",
            "profile_id": profile.id
        }


    # =====================================
    # STEP 6 - NOTIFICATION PREFERENCES
    # =====================================
    elif step == 6:

        notification = db.execute(
            select(VendorNotificationPreference).where(
                VendorNotificationPreference.vendor_profile_id == profile.id
            )
        ).scalars().first()

        if not notification:
            notification = VendorNotificationPreference(
                vendor_profile_id=profile.id
            )
            db.add(notification)

        if email_notification is not None:
            notification.email_notification = email_notification

        if sms_notification is not None:
            notification.sms_notification = sms_notification

        if push_notification is not None:
            notification.push_notification = push_notification

        db.commit()
        db.refresh(profile)

        return {
            "success": True,
            "step": 6,
            "message": "Vendor profile completed successfully.",
            "profile_id": profile.id
        }

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid step."
        )
    
@router.get("/vendor/profile")
async def get_vendor_profile(
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

    if user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=403,
            detail="Only Vendor can access profile"
        )

    profile = db.execute(
        select(VendorProfile).where(
            VendorProfile.user_id == user.id
        )
    ).scalars().first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Vendor profile not found"
        )

    document = db.execute(
        select(VendorDocument).where(
            VendorDocument.vendor_profile_id == profile.id
        )
    ).scalars().first()

    service_coverage = db.execute(
        select(VendorServiceCoverage).where(
            VendorServiceCoverage.vendor_profile_id == profile.id
        )
    ).scalars().all()

    workforce = db.execute(
        select(VendorWorkforce).where(
            VendorWorkforce.vendor_profile_id == profile.id
        )
    ).scalars().first()

    bank = db.execute(
        select(VendorBankDetail).where(
            VendorBankDetail.vendor_profile_id == profile.id
        )
    ).scalars().first()

    notification = db.execute(
        select(VendorNotificationPreference).where(
            VendorNotificationPreference.vendor_profile_id == profile.id
        )
    ).scalars().first()

    return {
        "profile": {
            "company_name": profile.company_name,
            "owner_manager_name": profile.owner_manager_name,
            "vendor_type": profile.vendor_type,
            "legal_business_name": profile.legal_business_name,
            "business_type": profile.business_type,
            "industry": profile.industry,
            "company_registration_number": profile.company_registration_number,
            "gst_number": profile.gst_number,
            "pan_number": profile.pan_number,
            "website": profile.website,
            "years_in_business": profile.years_in_business,
            "company_registration_date": profile.company_registration_date,
            "employee_count": profile.employee_count,
            "primary_service_category": profile.primary_service_category,
            "about_business": profile.about_business,
            "address": profile.address,
            "city": profile.city,
            "state": profile.state,
            "pincode": profile.pincode,
            "timezone": profile.timezone,
            "working_hours": profile.working_hours,
            "profile_image": profile.profile_image
        },

        "documents": {
            "gst_certificate": document.gst_certificate if document else None,
            "pan_card": document.pan_card if document else None,
            "registration_certificate": document.registration_certificate if document else None,
            "cancelled_cheque": document.cancelled_cheque if document else None,
            "other_document": document.other_document if document else None
        },

        "service_coverage": [
            {
                "state": item.state,
                "city": item.city,
                "service_radius": item.service_radius
            }
            for item in service_coverage
        ],

        "workforce": {
            "total_engineers": workforce.total_engineers if workforce else 0,
            "certified_engineers": workforce.certified_engineers if workforce else 0,
            "support_staff": workforce.support_staff if workforce else 0
        },

        "bank_details": {
            "account_holder_name": bank.account_holder_name if bank else None,
            "bank_name": bank.bank_name if bank else None,
            "account_number": bank.account_number if bank else None,
            "ifsc_code": bank.ifsc_code if bank else None,
            "branch_name": bank.branch_name if bank else None
        },

        "notification_preferences": {
            "email_notification": notification.email_notification if notification else False,
            "sms_notification": notification.sms_notification if notification else False,
            "push_notification": notification.push_notification if notification else False
        }
    }


@router.post("/vendor/invite-engineer")
async def invite_engineer(
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    """
    Generate a new referral link for inviting an engineer.
    Each time this endpoint is called, a new referral link is generated
    with a 1-day expiry.
    """
    user = db.execute(
        select(User).where(User.mobile_number == current_user_mobile)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=403,
            detail="Only Vendor can invite engineers"
        )

    profile = db.execute(
        select(VendorProfile).where(VendorProfile.user_id == user.id)
    ).scalars().first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Vendor profile not found"
        )

    # Generate unique referral token
    referral_token = secrets.token_urlsafe(32)

    # Set expiry to 24 hours from now
    expires_at = datetime.now(timezone.utc) + timedelta(days=1)

    # Create referral link
    referral_link = f"{settings.FRONTEND_URL}/profile/invite/engineer/{referral_token}"

    # Create new invitation record
    invitation = EngineerInvitation(
        vendor_profile_id=profile.id,
        referral_token=referral_token,
        referral_link=referral_link,
        expires_at=expires_at,
        status="pending"
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return {
        "success": True,
        "message": "Engineer invitation generated successfully",
        "data": {
            "invitation_id": invitation.id,
            "referral_link": invitation.referral_link,
            "referral_token": invitation.referral_token,
            "created_at": invitation.created_at,
            "expires_at": invitation.expires_at,
            "status": invitation.status
        }
    }


@router.get("/vendor/invitations")
async def get_vendor_invitations(
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    """
    Get all invitations sent by the current vendor.
    """
    user = db.execute(
        select(User).where(User.mobile_number == current_user_mobile)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=403,
            detail="Only Vendor can access invitations"
        )

    profile = db.execute(
        select(VendorProfile).where(VendorProfile.user_id == user.id)
    ).scalars().first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Vendor profile not found"
        )

    invitations = db.execute(
        select(EngineerInvitation).where(
            EngineerInvitation.vendor_profile_id == profile.id
        )
    ).scalars().all()

    return {
        "success": True,
        "data": [
            {
                "invitation_id": inv.id,
                "referral_link": inv.referral_link,
                "created_at": inv.created_at,
                "expires_at": inv.expires_at,
                "is_used": inv.is_used,
                "status": inv.status
            }
            for inv in invitations
        ]
    }


@router.get("/vendor/invitation/{invitation_id}")
async def get_invitation_details(
    invitation_id: int = Path(...),
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific invitation.
    """
    user = db.execute(
        select(User).where(User.mobile_number == current_user_mobile)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=403,
            detail="Only Vendor can access invitation details"
        )

    profile = db.execute(
        select(VendorProfile).where(VendorProfile.user_id == user.id)
    ).scalars().first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Vendor profile not found"
        )

    invitation = db.execute(
        select(EngineerInvitation).where(
            EngineerInvitation.id == invitation_id,
            EngineerInvitation.vendor_profile_id == profile.id
        )
    ).scalars().first()

    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found"
        )

    return {
        "success": True,
        "data": {
            "invitation_id": invitation.id,
            "referral_link": invitation.referral_link,
            "created_at": invitation.created_at,
            "expires_at": invitation.expires_at,
            "is_used": invitation.is_used,
            "status": invitation.status
        }
    }


@router.delete("/vendor/invitation/{invitation_id}")
async def delete_invitation(
    invitation_id: int = Path(...),
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    """
    Delete/revoke an invitation link.
    """
    user = db.execute(
        select(User).where(User.mobile_number == current_user_mobile)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=403,
            detail="Only Vendor can revoke invitations"
        )

    profile = db.execute(
        select(VendorProfile).where(VendorProfile.user_id == user.id)
    ).scalars().first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Vendor profile not found"
        )

    invitation = db.execute(
        select(EngineerInvitation).where(
            EngineerInvitation.id == invitation_id,
            EngineerInvitation.vendor_profile_id == profile.id
        )
    ).scalars().first()

    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found"
        )

    db.delete(invitation)
    db.commit()

    return {
        "success": True,
        "message": "Invitation deleted successfully"
    }


@router.api_route(
    "/invite/engineer/{token}",
    methods=["GET", "POST"]
)
async def accept_engineer_invitation(
    request: Request,
    token: str = Path(...),
    email: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    current_user_mobile: Optional[str] = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    """
    Handle engineer invitation via referral link.

    GET:
        - Validates the referral token.
        - Returns HTTP 200 with the frontend registration URL.

    POST:
        - Validates the referral token.
        - Requires an authenticated Field Engineer.
        - Consumes the referral link.
        - Updates contact information if provided.
        - Returns HTTP 200 with invitation details.
    """

    # Find invitation
    invitation = db.execute(
        select(EngineerInvitation).where(
            EngineerInvitation.referral_token == token
        )
    ).scalars().first()

    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invalid referral link"
        )

    # Check if already used
    if invitation.is_used:
        raise HTTPException(
            status_code=400,
            detail="This referral link has already been used"
        )

    # Check if expired
    if datetime.now(timezone.utc) > invitation.expires_at:
        invitation.status = "expired"
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="This referral link has expired. Please contact the vendor for a new invitation."
        )

    # Check status
    if invitation.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"This referral link is no longer valid (status: {invitation.status})"
        )

    # ============================================================
    # GET REQUEST
    # ============================================================
    if request.method == "GET":

        redirect_url = (
            f"{settings.FRONTEND_URL}"
            f"/register?referral_token={token}"
        )

        return {
            "success": True,
            "message": "Referral link is valid",
            "data": {
                "invitation_id": invitation.id,
                "redirect_url": redirect_url,
                "referral_token": token,
                "vendor_profile_id": invitation.vendor_profile_id,
                "status": invitation.status,
                "is_used": invitation.is_used
            }
        }

    # ============================================================
    # POST REQUEST
    # ============================================================
    elif request.method == "POST":

        # Authentication required
        if not current_user_mobile:
            raise HTTPException(
                status_code=401,
                detail="Authentication required to consume invitation"
            )

        # Get the current user
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

        # Check if the user is an engineer
        if user.role != UserRole.FIELD_ENGINEER:
            raise HTTPException(
                status_code=403,
                detail="Only field engineers can consume this invitation"
            )

        # Mark invitation as used
        invitation.is_used = True
        invitation.used_by_user_id = user.id
        invitation.status = "accepted"

        # Update contact information if provided
        if email:
            invitation.email = email

        if phone_number:
            invitation.phone_number = phone_number

        db.commit()
        db.refresh(invitation)

        return {
            "success": True,
            "message": "Referral link successfully consumed",
            "data": {
                "invitation_id": invitation.id,
                "referral_link": invitation.referral_link,
                "vendor_profile_id": invitation.vendor_profile_id,
                "status": invitation.status,
                "is_used": invitation.is_used,
                "used_at": datetime.now(timezone.utc)
            }
        }






@router.get("/invite/engineer/{token}/details")
async def get_invitation_details_by_token(
    token: str = Path(...),
    db: Session = Depends(get_db)
):
    """
    Get details of an invitation by token (for frontend validation before redirect).
    """
    invitation = db.execute(
        select(EngineerInvitation).where(
            EngineerInvitation.referral_token == token
        )
    ).scalars().first()

    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invalid referral link"
        )

    # Check expiry
    is_expired = datetime.now(timezone.utc) > invitation.expires_at

    if is_expired and invitation.status == "pending":
        invitation.status = "expired"
        db.commit()

    return {
        "success": True,
        "data": {
            "invitation_id": invitation.id,
            "referral_link": invitation.referral_link,
            "is_used": invitation.is_used,
            "status": invitation.status,
            "created_at": invitation.created_at,
            "expires_at": invitation.expires_at,
            "is_expired": is_expired
        }
    }


@router.put("/vendor/profile")
async def update_vendor_profile(

    # company_name: str = Form(...),
    # owner_manager_name: str = Form(...),
    company_name: str = Form(None),
    owner_manager_name: str = Form(None),

    vendor_type: str = Form(None),
    legal_business_name: str = Form(None),
    business_type: str = Form(None),
    industry: str = Form(None),

    company_registration_number: str = Form(None),
    gst_number: str = Form(None),
    pan_number: str = Form(None),

    website: str = Form(None),
    years_in_business: int = Form(None),
    employee_count: int = Form(None),

    primary_service_category: str = Form(None),
    about_business: str = Form(None),

    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    pincode: str = Form(None),

    timezone: str = Form(None),
    working_hours: str = Form(None),
    account_holder_name: str = Form(None),
    bank_name: str = Form(None),
    account_number: str = Form(None),
    ifsc_code: str = Form(None),
    branch_name: str = Form(None),
    service_state: str = Form(None),
    service_city: str = Form(None),
    service_radius: int = Form(None),
    total_engineers: int = Form(None),
    certified_engineers: int = Form(None),
    support_staff: int = Form(None),
    email_notification: bool = Form(None),
    sms_notification: bool = Form(None),
    push_notification: bool = Form(None),


    profile_image: UploadFile = File(None),

    gst_certificate: UploadFile = File(None),
    pan_card: UploadFile = File(None),
    registration_certificate: UploadFile = File(None),
    cancelled_cheque: UploadFile = File(None),
    other_document: UploadFile = File(None),

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

    if user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=403,
            detail="Only Vendor can update profile"
        )

    profile = db.execute(
        select(VendorProfile).where(
            VendorProfile.user_id == user.id
        )
    ).scalars().first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Vendor profile not found"
        )

    # ----------------------------
    # Update Vendor Profile
    # ----------------------------

    if company_name is not None:
        profile.company_name = company_name

    if owner_manager_name is not None:
        profile.owner_manager_name = owner_manager_name

    if vendor_type is not None:
       profile.vendor_type = vendor_type

    if legal_business_name is not None:
       profile.legal_business_name = legal_business_name

    if business_type is not None:
       profile.business_type = business_type

    if industry is not None:
        profile.industry = industry

    if company_registration_number is not None:
        profile.company_registration_number = company_registration_number

    if gst_number is not None:
        profile.gst_number = gst_number

    if pan_number is not None:
        profile.pan_number = pan_number

    if website is not None:
        profile.website = website

    if years_in_business is not None:
       profile.years_in_business = years_in_business

    if employee_count is not None:
        profile.employee_count = employee_count

    if primary_service_category is not None:
        profile.primary_service_category = primary_service_category

    if about_business is not None:
        profile.about_business = about_business

    if address is not None:
        profile.address = address

    if city is not None:
       profile.city = city

    if state is not None:
        profile.state = state

    if pincode is not None:
       profile.pincode = pincode

    if timezone is not None:
        profile.timezone = timezone

    if working_hours is not None:
        profile.working_hours = working_hours

    # ----------------------------
    # Update Profile Image
    # ----------------------------

    os.makedirs("uploads/vendor", exist_ok=True)

    if profile_image:
        image_path = f"uploads/vendor/{profile_image.filename}"

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)

        profile.profile_image = image_path



    # ----------------------------
    # Update Service Coverage
    # ----------------------------

    coverage = db.execute(
        select(VendorServiceCoverage).where(
            VendorServiceCoverage.vendor_profile_id == profile.id
        )
    ).scalars().first()

    if not coverage:
        coverage = VendorServiceCoverage(
           vendor_profile_id=profile.id
        )
        db.add(coverage)

    if service_state is not None:
        coverage.state = service_state

    if service_city is not None:
       coverage.city = service_city

    if service_radius is not None:
       coverage.service_radius = service_radius


    # ----------------------------
    # Update Workforce
     # ----------------------------

    workforce = db.execute(
        select(VendorWorkforce).where(
           VendorWorkforce.vendor_profile_id == profile.id
        )
    ).scalars().first()

    if not workforce:
        workforce = VendorWorkforce(
            vendor_profile_id=profile.id
        )
    db.add(workforce)

    if total_engineers is not None:
       workforce.total_engineers = total_engineers

    if certified_engineers is not None:
        workforce.certified_engineers = certified_engineers

    if support_staff is not None:
        workforce.support_staff = support_staff





    # ----------------------------
    # Update Bank Details
    # ----------------------------

    bank = db.execute(
        select(VendorBankDetail).where(
            VendorBankDetail.vendor_profile_id == profile.id
        )
    ).scalars().first()

    if not bank:
        bank = VendorBankDetail(
           vendor_profile_id=profile.id
        )
    db.add(bank)

    if account_holder_name is not None:
        bank.account_holder_name = account_holder_name

    if bank_name is not None:
        bank.bank_name = bank_name

    if account_number is not None:
        bank.account_number = account_number

    if ifsc_code is not None:
        bank.ifsc_code = ifsc_code
 
    if branch_name is not None:
        bank.branch_name = branch_name







    # ----------------------------
    # Update Notification Preferences
    # ----------------------------

    notification = db.execute(
        select(VendorNotificationPreference).where(
            VendorNotificationPreference.vendor_profile_id == profile.id
        )
    ).scalars().first()

    if not notification:
        notification = VendorNotificationPreference(
            vendor_profile_id=profile.id
        )
    db.add(notification)

    if email_notification is not None:
        notification.email_notification = email_notification

    if sms_notification is not None:
        notification.sms_notification = sms_notification

    if push_notification is not None:
        notification.push_notification = push_notification
    # ----------------------------
    # Update Vendor Documents
    # ----------------------------

    document = db.execute(
        select(VendorDocument).where(
            VendorDocument.vendor_profile_id == profile.id
        )
    ).scalars().first()

    if not document:
        document = VendorDocument(
            vendor_profile_id=profile.id
        )
        db.add(document)

    if gst_certificate:
        gst_path = f"uploads/vendor/{gst_certificate.filename}"

        with open(gst_path, "wb") as buffer:
            shutil.copyfileobj(gst_certificate.file, buffer)

        document.gst_certificate = gst_path

    if pan_card:
        pan_path = f"uploads/vendor/{pan_card.filename}"

        with open(pan_path, "wb") as buffer:
            shutil.copyfileobj(pan_card.file, buffer)

        document.pan_card = pan_path

    if registration_certificate:
        reg_path = f"uploads/vendor/{registration_certificate.filename}"

        with open(reg_path, "wb") as buffer:
            shutil.copyfileobj(registration_certificate.file, buffer)

        document.registration_certificate = reg_path

    if cancelled_cheque:
        cheque_path = f"uploads/vendor/{cancelled_cheque.filename}"

        with open(cheque_path, "wb") as buffer:
            shutil.copyfileobj(cancelled_cheque.file, buffer)

        document.cancelled_cheque = cheque_path

    if other_document:
        other_path = f"uploads/vendor/{other_document.filename}"

        with open(other_path, "wb") as buffer:
            shutil.copyfileobj(other_document.file, buffer)

        document.other_document = other_path
    db.commit()
    db.refresh(profile)

    return {
        "message": "Vendor profile updated successfully",
        "profile_id": profile.id
    }








# Complete Customer Profile

async def save_customer_uploaded_file(
    file: UploadFile,
    original_filename: str = "customer_document"
):
    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is missing."
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail=f"Uploaded file '{file.filename}' is empty."
        )

    upload_dir = FilePath("uploads/customer")
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = FilePath(file.filename).name
    extension = FilePath(original_name).suffix.lower()

    stored_filename = f"{uuid4().hex}{extension}"

    file_path = upload_dir / stored_filename

    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    return str(file_path)


@router.post("/customer/complete-profile/{step}")
async def complete_customer_profile(
    step: int,
    request: Request,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    if step not in [1, 2, 3, 4, 5, 6]:
        raise HTTPException(
            status_code=400,
            detail="Invalid step. Step must be between 1 and 6."
        )

    form = await request.form()

    def get_text(field_name):
        value = form.get(field_name)

        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            return value if value else None

        return None

    def get_bool(field_name):
        value = get_text(field_name)

        if value is None:
            return False

        return value.lower() in ["true", "1", "yes", "on"]

    # -----------------------------
    # TEXT FORM DATA
    # -----------------------------

    full_name = get_text("full_name")
    email = get_text("email")
    phone_number = get_text("phone_number")

    identity_type = get_text("identity_type")
    identity_full_name = get_text("identity_full_name")
    identity_date_of_birth = get_text("identity_date_of_birth")
    identity_number = get_text("identity_number")

    company_name = get_text("company_name")
    business_type = get_text("business_type")
    industry = get_text("industry")
    company_registration_number = get_text(
        "company_registration_number"
    )
    office_address = get_text("office_address")
    city = get_text("city")
    state = get_text("state")
    pincode = get_text("pincode")
    gst_number = get_text("gst_number")
    pan_number = get_text("pan_number")
    billing_email = get_text("billing_email")
    authorized_person_name = get_text("authorized_person_name")
    designation = get_text("designation")
    work_phone = get_text("work_phone")
    work_email = get_text("work_email")

    account_holder_name = get_text("account_holder_name")
    bank_name = get_text("bank_name")
    account_number = get_text("account_number")
    ifsc_code = get_text("ifsc_code")
    local_code = get_text("local_code")
    bank_address = get_text("bank_address")

    email_invoice_for_every_payout = get_bool(
        "email_invoice_for_every_payout"
    )

    # -----------------------------
    # FILE FORM DATA
    # -----------------------------

    front_image = form.get("front_image")
    back_image = form.get("back_image")

    company_registration_certificate = form.get(
        "company_registration_certificate"
    )

    tax_identification_card = form.get(
        "tax_identification_card"
    )

    gst_certificate = form.get(
        "gst_certificate"
    )

    moa_aoa = form.get("moa_aoa")

    bank_statement = form.get("bank_statement")

    identity_proof = form.get("identity_proof")

    address_proof = form.get("address_proof")

    # -----------------------------
    # GET USER + PROFILE
    # -----------------------------

    user, profile = get_user_and_profile(
        current_user_mobile,
        db
    )

    # =========================================================
    # STEP 1
    # =========================================================

    if step == 1:

        if not user.is_verified:
            raise HTTPException(
                status_code=400,
                detail="Phone number is not verified."
            )

        message = "Step 1 completed successfully."

    # =========================================================
    # STEP 2
    # =========================================================

    elif step == 2:

        if not full_name:
            raise HTTPException(
                status_code=400,
                detail="Full name is required."
            )

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Email is required."
            )

        if not phone_number:
            raise HTTPException(
                status_code=400,
                detail="Phone number is required."
            )

        profile.full_name = full_name
        user.email = email
        user.phone_number = phone_number

        db.add(profile)
        db.add(user)
        db.commit()
        db.refresh(profile)
        db.refresh(user)

        message = "Step 2 completed successfully."

    # =========================================================
    # STEP 3
    # =========================================================

    elif step == 3:

        if not identity_type:
            raise HTTPException(
                status_code=400,
                detail="Identity type is required."
            )

        if not identity_full_name:
            raise HTTPException(
                status_code=400,
                detail="Identity full name is required."
            )

        if not identity_date_of_birth:
            raise HTTPException(
                status_code=400,
                detail="Date of birth is required."
            )

        if not identity_number:
            raise HTTPException(
                status_code=400,
                detail="Identity number is required."
            )

        if front_image is None:
            raise HTTPException(
                status_code=400,
                detail="front_image is required."
            )

        if not getattr(front_image, "filename", None):
            raise HTTPException(
                status_code=400,
                detail="front_image must be a valid uploaded file."
            )

        if back_image is not None and not getattr(back_image, "filename", None):
            raise HTTPException(
                status_code=400,
                detail="back_image must be a valid uploaded file."
            )

        # Parse DOB
        try:
            parsed_dob = date.fromisoformat(
                identity_date_of_birth
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="identity_date_of_birth must be in YYYY-MM-DD format."
            )

        identity = db.execute(
            select(CustomerIdentity).where(
                CustomerIdentity.user_profile_id == profile.id
            )
        ).scalar_one_or_none()

        if not identity:
            identity = CustomerIdentity(
                user_profile_id=profile.id
            )
            db.add(identity)

        identity.identity_type = identity_type
        identity.identity_full_name = identity_full_name
        identity.date_of_birth = parsed_dob
        identity.identity_number = identity_number

        # Save actual uploaded files
        identity.front_image = await save_customer_uploaded_file(
            front_image,
            front_image.filename
        )

        if back_image:
            identity.back_image = await save_customer_uploaded_file(
                back_image,
                back_image.filename
            )

        db.commit()
        db.refresh(identity)

        message = "Step 3 completed successfully."

    # =========================================================
    # STEP 4
    # =========================================================

    elif step == 4:

        business_values = [
            company_name,
            business_type,
            industry,
            company_registration_number,
            office_address,
            city,
            state,
            pincode,
            gst_number,
            pan_number,
            billing_email,
            authorized_person_name,
            designation,
            work_phone,
            work_email
        ]

        has_business_data = any(
            value is not None and str(value).strip()
            for value in business_values
        )

        if not has_business_data:

            profile.customer_type = "individual"

        else:

            profile.customer_type = "business"

            required_business_fields = {
                "company_name": company_name,
                "business_type": business_type,
                "industry": industry,
                "company_registration_number":
                    company_registration_number,
                "office_address": office_address,
                "city": city,
                "state": state,
                "pincode": pincode,
                "gst_number": gst_number,
                "pan_number": pan_number,
                "billing_email": billing_email,
                "authorized_person_name":
                    authorized_person_name,
                "designation": designation,
                "work_phone": work_phone,
                "work_email": work_email
            }

            missing_fields = [
                field
                for field, value in required_business_fields.items()
                if not value
            ]

            if missing_fields:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "Business information is incomplete.",
                        "missing_fields": missing_fields
                    }
                )

            business = db.execute(
                select(CustomerBusiness).where(
                    CustomerBusiness.user_profile_id == profile.id
                )
            ).scalar_one_or_none()

            if not business:
                business = CustomerBusiness(
                    user_profile_id=profile.id
                )
                db.add(business)

            business.company_name = company_name
            business.business_type = business_type
            business.industry = industry
            business.company_registration_number = (
                company_registration_number
            )
            business.office_address = office_address
            business.city = city
            business.state = state
            business.pincode = pincode
            business.gst_number = gst_number
            business.pan_number = pan_number
            business.billing_email = billing_email
            business.authorized_person_name = (
                authorized_person_name
            )
            business.designation = designation
            business.work_phone = work_phone
            business.work_email = work_email

        db.commit()

        message = "Step 4 completed successfully."

    # =========================================================
    # STEP 5
    # =========================================================

    elif step == 5:

        documents = db.execute(
            select(CustomerDocument).where(
                CustomerDocument.user_profile_id == profile.id
            )
        ).scalar_one_or_none()

        if not documents:
            documents = CustomerDocument(
                user_profile_id=profile.id
            )
            db.add(documents)

        if profile.customer_type == "business":

            required_documents = {
                "company_registration_certificate":
                    company_registration_certificate,
                "tax_identification_card":
                    tax_identification_card,
                "gst_certificate":
                    gst_certificate,
                "moa_aoa":
                    moa_aoa,
                "bank_statement":
                    bank_statement
            }

            missing_documents = [
                name
                for name, file in required_documents.items()
                if not file
            ]

            if missing_documents:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "Required business documents are missing.",
                        "missing_documents": missing_documents
                    }
                )

            documents.company_registration_certificate = (
                await save_customer_uploaded_file(
                    company_registration_certificate,
                    company_registration_certificate.filename
                )
            )

            documents.tax_identification_card = (
                await save_customer_uploaded_file(
                    tax_identification_card,
                    tax_identification_card.filename
                )
            )

            documents.gst_certificate = (
                await save_customer_uploaded_file(
                    gst_certificate,
                    gst_certificate.filename
                )
            )

            documents.moa_aoa = (
                await save_customer_uploaded_file(
                    moa_aoa,
                    moa_aoa.filename
                )
            )

            # bank_statement → bank_account_proof
            documents.bank_account_proof = (
                await save_customer_uploaded_file(
                    bank_statement,
                    bank_statement.filename
                )
            )

        else:

            if not identity_proof:
                raise HTTPException(
                    status_code=400,
                    detail="Identity proof is required."
                )

            if not address_proof:
                raise HTTPException(
                    status_code=400,
                    detail="Address proof is required."
                )

            documents.identity_proof = (
                await save_customer_uploaded_file(
                    identity_proof,
                    identity_proof.filename
                )
            )

            documents.address_proof = (
                await save_customer_uploaded_file(
                    address_proof,
                    address_proof.filename
                )
            )

        db.commit()
        db.refresh(documents)

        message = "Step 5 completed successfully."

    # =========================================================
    # STEP 6
    # =========================================================

    elif step == 6:

        required_bank_fields = {
            "account_holder_name": account_holder_name,
            "bank_name": bank_name,
            "account_number": account_number,
            "ifsc_code": ifsc_code,
            "local_code": local_code,
            "bank_address": bank_address
        }

        missing_fields = [
            field
            for field, value in required_bank_fields.items()
            if not value
        ]

        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Bank information is incomplete.",
                    "missing_fields": missing_fields
                }
            )

        bank = db.execute(
            select(CustomerBankDetail).where(
                CustomerBankDetail.user_profile_id == profile.id
            )
        ).scalars().first()

        if not bank:
            bank = CustomerBankDetail(
                user_profile_id=profile.id
            )
            db.add(bank)

        bank.account_holder_name = account_holder_name
        bank.bank_name = bank_name
        bank.account_number = account_number
        bank.ifsc_code = ifsc_code
        bank.local_code = local_code
        bank.bank_address = bank_address
        bank.email_invoice_for_every_payout = (
            email_invoice_for_every_payout
        )

        db.commit()
        db.refresh(bank)

        message = "Step 6 completed successfully."

    # =========================================================
    # COMPLETION CALCULATION
    # =========================================================

    identity = db.execute(
        select(CustomerIdentity).where(
            CustomerIdentity.user_profile_id == profile.id
        )
    ).scalars().first()

    business = db.execute(
        select(CustomerBusiness).where(
            CustomerBusiness.user_profile_id == profile.id
        )
    ).scalars().first()

    documents = db.execute(
        select(CustomerDocument).where(
            CustomerDocument.user_profile_id == profile.id
        )
    ).scalars().first()

    bank = db.execute(
        select(CustomerBankDetail).where(
            CustomerBankDetail.user_profile_id == profile.id
        )
    ).scalars().first()

    completion = calculate_customer_completion(
        user=user,
        profile=profile,
        identity=identity,
        business=business,
        documents=documents,
        bank=bank
    )

    return {
        "success": True,
        "step": step,
        "message": message,
        "completion_percentage": completion["completion_percentage"]
    }
    
# Get Customer Profile

def calculate_customer_completion(
    user,
    profile,
    identity,
    business,
    documents,
    bank
):
    completed_steps = 0

    # =========================================================
    # STEP 1 - PHONE VERIFIED
    # =========================================================

    step1_completed = bool(user.is_verified)

    if step1_completed:
        completed_steps += 1

    # =========================================================
    # STEP 2 - BASIC INFORMATION
    # =========================================================

    step2_completed = bool(
        profile
        and profile.full_name
        and user.email
        and user.phone_number
    )

    if step2_completed:
        completed_steps += 1

    # =========================================================
    # STEP 3 - VERIFY IDENTITY
    # =========================================================

    step3_completed = bool(
        identity
        and identity.identity_type
        and identity.identity_full_name
        and identity.date_of_birth
        and identity.identity_number
    )

    if step3_completed:
        completed_steps += 1

    # =========================================================
    # STEP 4 - BUSINESS INFORMATION
    # =========================================================

    if profile and profile.customer_type == "individual":

        step4_completed = True

    elif profile and profile.customer_type == "business":

        step4_completed = bool(
            business
            and business.company_name
            and business.business_type
            and business.industry
            and business.company_registration_number
            and business.gst_number
            and business.city
            and business.state
            and business.pincode
            and business.office_address
            and business.pan_number
            and business.billing_email
            and business.authorized_person_name
            and business.designation
            and business.work_phone
            and business.work_email
        )

    else:
        step4_completed = False

    if step4_completed:
        completed_steps += 1

    # =========================================================
    # STEP 5 - DOCUMENTS
    # =========================================================

    if profile and profile.customer_type == "individual":

        step5_completed = bool(
            documents
            and documents.identity_proof
            and documents.address_proof
        )

    elif profile and profile.customer_type == "business":

        step5_completed = bool(
            documents
            and documents.company_registration_certificate
            and documents.tax_identification_card
            and documents.gst_certificate
            and documents.moa_aoa
            and documents.bank_account_proof
        )

    else:
        step5_completed = False

    if step5_completed:
        completed_steps += 1

    # =========================================================
    # STEP 6 - BANK & PAYOUT
    # =========================================================

    step6_completed = bool(
        bank
        and bank.account_holder_name
        and bank.bank_name
        and bank.account_number
        and bank.ifsc_code
        and bank.local_code
        and bank.bank_address
        and documents
        and documents.bank_account_proof
    )

    if step6_completed:
        completed_steps += 1

    # =========================================================
    # FINAL CALCULATION
    # =========================================================

    total_steps = 6

    completion_percentage = round(
        (completed_steps / total_steps) * 100
    )

    return {
        "completion_percentage": completion_percentage,
        "completed_steps": completed_steps,
        "total_steps": total_steps,
        "steps": {
            "step_1": step1_completed,
            "step_2": step2_completed,
            "step_3": step3_completed,
            "step_4": step4_completed,
            "step_5": step5_completed,
            "step_6": step6_completed
        }
    }



@router.get("/customer/profile")
async def get_customer_profile(
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):

    # =========================================================
    # GET USER + PROFILE
    # =========================================================

    user, profile =  get_user_and_profile(
        current_user_mobile,
        db
    )

    if user.role != UserRole.USER:
        raise HTTPException(
            status_code=403,
            detail="Only Customer can access profile"
        )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    # =========================================================
    # FETCH CUSTOMER DATA
    # =========================================================

    identity = db.execute(
        select(CustomerIdentity).where(
            CustomerIdentity.user_profile_id == profile.id
        )
    ).scalars().first()

    business = db.execute(
        select(CustomerBusiness).where(
            CustomerBusiness.user_profile_id == profile.id
        )
    ).scalars().first()

    documents = db.execute(
        select(CustomerDocument).where(
            CustomerDocument.user_profile_id == profile.id
        )
    ).scalars().first()

    bank = db.execute(
        select(CustomerBankDetail).where(
            CustomerBankDetail.user_profile_id == profile.id
        )
    ).scalars().first()

    # =========================================================
    # TOTAL BOOKINGS
    # =========================================================

    total_bookings = db.execute(
        select(func.count(Booking.id)).where(
            Booking.user_id == user.id
        )
    ).scalar() or 0

    # =========================================================
    # TOTAL SPENT
    # =========================================================

    total_spent_result = db.execute(
        select(func.sum(PaymentHistory.amount)).where(
            PaymentHistory.user_id == user.id,
            PaymentHistory.status.in_(
                [
                    "success",
                    "completed",
                    "Success"
                ]
            )
        )
    ).scalar()

    total_spent = (
        float(total_spent_result)
        if total_spent_result
        else 0.0
    )

    # =========================================================
    # COMPLETION
    # =========================================================

    completion = calculate_customer_completion(
        user,
        profile,
        identity,
        business,
        documents,
        bank
    )

    # =========================================================
    # DOCUMENT STATUS
    # =========================================================

    def document_status(value, updated_at=None):
        return {
            "uploaded": bool(value),
            "updated_at": (
                updated_at.isoformat()
                if value and updated_at
                else None
            )
        }

    # =========================================================
    # RESPONSE
    # =========================================================

    return {

        "success": True,

        # =====================================================
        # PROFILE COMPLETION
        # =====================================================

        "completion_percentage": (
            completion["completion_percentage"]
        ),

        "completed_steps": (
            completion["completed_steps"]
        ),

        "total_steps": 6,

        "steps": completion["steps"],

        # =====================================================
        # CUSTOMER DATA
        # =====================================================

        "data": {

            "customer_type": profile.customer_type,

            # -------------------------------------------------
            # STEP 2 - BASIC INFORMATION
            # -------------------------------------------------

            "basic_information": {

                "full_name": profile.full_name,

                "email": user.email,

                "phone_number": user.phone_number
            },

            # -------------------------------------------------
            # STEP 3 - VERIFY IDENTITY
            # -------------------------------------------------

            "identity": {

                "id_type": (
                    identity.identity_type
                    if identity
                    else None
                ),

                "full_name": (
                    identity.identity_full_name
                    if identity
                    else None
                ),

                "date_of_birth": (
                    identity.date_of_birth.isoformat()
                    if identity
                    and identity.date_of_birth
                    else None
                ),

                "identity_number": (
                    identity.identity_number
                    if identity
                    else None
                ),

                "verified": (
                    identity.verified
                    if identity
                    else False
                ),

                "front_image_uploaded": (
                    bool(
                        identity
                        and identity.front_image
                    )
                ),

                "back_image_uploaded": (
                    bool(
                        identity
                        and identity.back_image
                    )
                )
            },

            # -------------------------------------------------
            # STEP 4 - BUSINESS INFORMATION
            # -------------------------------------------------

            "business_information": {

                "company_name": (
                    business.company_name
                    if business
                    else None
                ),

                "business_type": (
                    business.business_type
                    if business
                    else None
                ),

                "industry": (
                    business.industry
                    if business
                    else None
                ),

                "company_registration_number": (
                    business.company_registration_number
                    if business
                    else None
                ),

                "gst_number": (
                    business.gst_number
                    if business
                    else None
                ),

                "city": (
                    business.city
                    if business
                    else None
                ),

                "state": (
                    business.state
                    if business
                    else None
                ),

                "pincode": (
                    business.pincode
                    if business
                    else None
                ),

                "office_address": (
                    business.office_address
                    if business
                    else None
                ),

                "pan_number": (
                    business.pan_number
                    if business
                    else None
                ),

                "billing_email": (
                    business.billing_email
                    if business
                    else None
                ),

                "authorized_contact": {

                    "full_name": (
                        business.authorized_person_name
                        if business
                        else None
                    ),

                    "designation": (
                        business.designation
                        if business
                        else None
                    ),

                    "phone": (
                        business.work_phone
                        if business
                        else None
                    ),

                    "email": (
                        business.work_email
                        if business
                        else None
                    )
                }
            },

            # -------------------------------------------------
            # STEP 5 - DOCUMENTS
            # -------------------------------------------------

            "documents": {

                "company_registration_certificate":
                    document_status(
                        documents.company_registration_certificate
                        if documents
                        else None,
                        documents.updated_at
                        if documents
                        else None
                    ),

                "tax_identification_number":
                    document_status(
                        documents.tax_identification_card
                        if documents
                        else None,
                        documents.updated_at
                        if documents
                        else None
                    ),

                "gst_verification":
                    document_status(
                        documents.gst_certificate
                        if documents
                        else None,
                        documents.updated_at
                        if documents
                        else None
                    ),

                "mca_roc_documents":
                    document_status(
                        documents.moa_aoa
                        if documents
                        else None,
                        documents.updated_at
                        if documents
                        else None
                    ),

                "bank_statement":
                    document_status(
                        documents.bank_account_proof
                        if documents
                        else None,
                        documents.updated_at
                        if documents
                        else None
                    ),

                "identity_proof":
                    document_status(
                        documents.identity_proof
                        if documents
                        else None,
                        documents.updated_at
                        if documents
                        else None
                    ),

                "address_proof":
                    document_status(
                        documents.address_proof
                        if documents
                        else None,
                        documents.updated_at
                        if documents
                        else None
                    )
            },

            # -------------------------------------------------
            # STEP 6 - BANK & PAYOUT
            # -------------------------------------------------

            "bank_payout": {

                "account_holder_name": (
                    bank.account_holder_name
                    if bank
                    else None
                ),

                "bank_name": (
                    bank.bank_name
                    if bank
                    else None
                ),

                "account_number": (
                    bank.account_number
                    if bank
                    else None
                ),

                "ifsc_code": (
                    bank.ifsc_code
                    if bank
                    else None
                ),

                "local_code": (
                    bank.local_code
                    if bank
                    else None
                ),

                "bank_address": (
                    bank.bank_address
                    if bank
                    else None
                ),

                "email_invoice_for_every_payout": (
                    bank.email_invoice_for_every_payout
                    if bank
                    else False
                ),

                "bank_statement_uploaded": (
                    bool(
                        documents
                        and documents.bank_account_proof
                    )
                )
            }
        },

        # =====================================================
        # STATISTICS
        # =====================================================

        "statistics": {

            "total_bookings": total_bookings,

            "total_spent": total_spent,

            "last_login_date": (
                user.last_login_at.isoformat()
                if user.last_login_at
                else None
            ),

            "last_update_date": (
                user.updated_at.isoformat()
                if user.updated_at
                else None
            ),

            "account_created_date": (
                user.created_at.isoformat()
                if user.created_at
                else None
            )
        }
    }

# Update Customer Profile

# Update Customer Profile

@router.put("/customer/profile")
async def update_customer_profile(

    # =========================================================
    # STEP 2: Basic Information
    # =========================================================

    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),

    # NOTE:
    # phone_number is intentionally NOT included.
    # Phone number cannot be updated.

    # =========================================================
    # STEP 3: Verify Your Identity
    # =========================================================

    identity_type: Optional[str] = Form(None),
    identity_full_name: Optional[str] = Form(None),
    identity_date_of_birth: Optional[date] = Form(None),
    identity_number: Optional[str] = Form(None),

    front_image: UploadFile = File(None),
    back_image: UploadFile = File(None),

    # =========================================================
    # STEP 4: Business Information
    # =========================================================

    # Company Details
    company_name: Optional[str] = Form(None),
    business_type: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    company_registration_number: Optional[str] = Form(None),

    # Business Address
    gst_number: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),
    office_address: Optional[str] = Form(None),

    # Tax & Billing
    pan_number: Optional[str] = Form(None),
    billing_email: Optional[str] = Form(None),

    # Authorized Contact Person
    authorized_person_name: Optional[str] = Form(None),
    designation: Optional[str] = Form(None),
    work_phone: Optional[str] = Form(None),
    work_email: Optional[str] = Form(None),

    # =========================================================
    # STEP 5: Upload Documents
    # =========================================================

    # Business Customer
    company_registration_certificate: UploadFile = File(None),
    tax_identification_card: UploadFile = File(None),
    gst_certificate: UploadFile = File(None),
    moa_aoa: UploadFile = File(None),

    # Individual Customer
    identity_proof: UploadFile = File(None),
    address_proof: UploadFile = File(None),

    # =========================================================
    # STEP 6: Bank & Payout Setup
    # =========================================================

    account_holder_name: Optional[str] = Form(None),
    bank_name: Optional[str] = Form(None),
    account_number: Optional[str] = Form(None),
    ifsc_code: Optional[str] = Form(None),
    local_code: Optional[str] = Form(None),
    bank_address: Optional[str] = Form(None),

    email_invoice_for_every_payout: Optional[bool] = Form(None),

    bank_statement: UploadFile = File(None),

    # =========================================================
    # AUTH + DB
    # =========================================================

    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):

    # =========================================================
    # GET USER + PROFILE
    # =========================================================

    user, profile = get_user_and_profile(
        current_user_mobile,
        db
    )

    if user.role != UserRole.USER:
        raise HTTPException(
            status_code=403,
            detail="Only Customer can update profile"
        )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    # =========================================================
    # FILE SAVE HELPER
    # =========================================================

    os.makedirs("uploads/customer", exist_ok=True)

    async def save_file(file: UploadFile):
        if not file or not file.filename:
            return None

        original_name = Path(file.filename).name
        extension = Path(original_name).suffix.lower()

        filename = f"{uuid.uuid4().hex}{extension}"
        file_path = os.path.join(
            "uploads/customer",
            filename
        )

        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded file '{file.filename}' is empty."
            )

        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        return file_path

    # =========================================================
    # STEP 2: BASIC INFORMATION
    # =========================================================

    if full_name is not None:
        profile.full_name = full_name

    if email is not None:
        user.email = email

    # phone_number is intentionally NOT updated.

    # =========================================================
    # STEP 3: VERIFY IDENTITY
    # =========================================================

    identity = db.execute(
        select(CustomerIdentity).where(
            CustomerIdentity.user_profile_id == profile.id
        )
    ).scalars().first()

    identity_fields_submitted = any([
        identity_type is not None,
        identity_full_name is not None,
        identity_date_of_birth is not None,
        identity_number is not None,
        front_image is not None,
        back_image is not None
    ])

    if identity_fields_submitted:

        if not identity:
            identity = CustomerIdentity(
                user_profile_id=profile.id
            )
            db.add(identity)

        if identity_type is not None:
            identity.identity_type = identity_type

        if identity_full_name is not None:
            identity.identity_full_name = identity_full_name

        if identity_date_of_birth is not None:
            identity.date_of_birth = identity_date_of_birth

        if identity_number is not None:
            identity.identity_number = identity_number

        if front_image:
            identity.front_image = await save_file(front_image)

        if back_image:
            identity.back_image = await save_file(back_image)

    # =========================================================
    # STEP 4: BUSINESS INFORMATION
    # =========================================================

    business = db.execute(
        select(CustomerBusiness).where(
            CustomerBusiness.user_profile_id == profile.id
        )
    ).scalars().first()

    business_fields_submitted = any([
        company_name is not None,
        business_type is not None,
        industry is not None,
        company_registration_number is not None,
        gst_number is not None,
        city is not None,
        state is not None,
        pincode is not None,
        office_address is not None,
        pan_number is not None,
        billing_email is not None,
        authorized_person_name is not None,
        designation is not None,
        work_phone is not None,
        work_email is not None
    ])

    if business_fields_submitted:

        profile.customer_type = "business"

        if not business:
            business = CustomerBusiness(
                user_profile_id=profile.id
            )
            db.add(business)

        if company_name is not None:
            business.company_name = company_name

        if business_type is not None:
            business.business_type = business_type

        if industry is not None:
            business.industry = industry

        if company_registration_number is not None:
            business.company_registration_number = (
                company_registration_number
            )

        if gst_number is not None:
            business.gst_number = gst_number

        if city is not None:
            business.city = city

        if state is not None:
            business.state = state

        if pincode is not None:
            business.pincode = pincode

        if office_address is not None:
            business.office_address = office_address

        if pan_number is not None:
            business.pan_number = pan_number

        if billing_email is not None:
            business.billing_email = billing_email

        if authorized_person_name is not None:
            business.authorized_person_name = (
                authorized_person_name
            )

        if designation is not None:
            business.designation = designation

        if work_phone is not None:
            business.work_phone = work_phone

        if work_email is not None:
            business.work_email = work_email

    # =========================================================
    # STEP 5: DOCUMENTS
    # =========================================================

    documents = db.execute(
        select(CustomerDocument).where(
            CustomerDocument.user_profile_id == profile.id
        )
    ).scalars().first()

    documents_submitted = any([
        company_registration_certificate is not None,
        tax_identification_card is not None,
        gst_certificate is not None,
        moa_aoa is not None,
        identity_proof is not None,
        address_proof is not None,
        bank_statement is not None
    ])

    if documents_submitted:

        if not documents:
            documents = CustomerDocument(
                user_profile_id=profile.id
            )
            db.add(documents)

        if company_registration_certificate:
            documents.company_registration_certificate = (
                await save_file(
                    company_registration_certificate
                )
            )

        if tax_identification_card:
            documents.tax_identification_card = (
                await save_file(
                    tax_identification_card
                )
            )

        if gst_certificate:
            documents.gst_certificate = (
                await save_file(
                    gst_certificate
                )
            )

        if moa_aoa:
            documents.moa_aoa = (
                await save_file(moa_aoa)
            )

        if identity_proof:
            documents.identity_proof = (
                await save_file(identity_proof)
            )

        if address_proof:
            documents.address_proof = (
                await save_file(address_proof)
            )

        # Bank Statement is stored as bank_account_proof
        if bank_statement:
            documents.bank_account_proof = (
                await save_file(bank_statement)
            )

    # =========================================================
    # STEP 6: BANK & PAYOUT SETUP
    # =========================================================

    bank_details = db.execute(
        select(CustomerBankDetail).where(
            CustomerBankDetail.user_profile_id == profile.id
        )
    ).scalars().first()

    bank_fields_submitted = any([
        account_holder_name is not None,
        bank_name is not None,
        account_number is not None,
        ifsc_code is not None,
        local_code is not None,
        bank_address is not None,
        email_invoice_for_every_payout is not None,
        bank_statement is not None
    ])

    if bank_fields_submitted:

        if not bank_details:
            bank_details = CustomerBankDetail(
                user_profile_id=profile.id
            )
            db.add(bank_details)

        if account_holder_name is not None:
            bank_details.account_holder_name = (
                account_holder_name
            )

        if bank_name is not None:
            bank_details.bank_name = bank_name

        if account_number is not None:
            bank_details.account_number = account_number

        if ifsc_code is not None:
            bank_details.ifsc_code = ifsc_code

        if local_code is not None:
            bank_details.local_code = local_code

        if bank_address is not None:
            bank_details.bank_address = bank_address

        if email_invoice_for_every_payout is not None:
            bank_details.email_invoice_for_every_payout = (
                email_invoice_for_every_payout
            )

    # =========================================================
    # SAVE
    # =========================================================

    db.commit()

    db.refresh(user)
    db.refresh(profile)

    # =========================================================
    # RESPONSE
    # =========================================================

    return {
        "success": True,
        "message": "Customer profile updated successfully",
        "email": user.email,
        "profile_id": profile.id
    }

# ---------------------------------------------------------------
# Backward-compatible router for legacy referral links
# (older links were generated WITHOUT the /profile prefix).
# Redirects /invite/engineer/{token} -> /profile/invite/engineer/{token}
# ---------------------------------------------------------------
invite_redirect_router = APIRouter(
    tags=["Engineer Invitation"]
)


@invite_redirect_router.api_route(
    "/invite/engineer/{token}",
    methods=["GET", "POST"],
)
async def invite_engineer_legacy_redirect(
    request: Request,
    token: str = Path(...),
    current_user_mobile: Optional[str] = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    """
    Handle referral link clicks for both GET and POST.

    Returns HTTP 200 for both methods and provides the frontend
    redirect URL in the response.
    """

    # 1. Find invitation
    invitation = db.execute(
        select(EngineerInvitation).where(
            EngineerInvitation.referral_token == token
        )
    ).scalars().first()

    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invalid referral link"
        )

    # 2. Check expiration
    if datetime.now(timezone.utc) > invitation.expires_at:
        invitation.status = "expired"
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="This referral link has expired. Please contact the vendor for a new invitation."
        )

    # 3. Check invitation status
    if invitation.status not in ["pending", "accepted"]:
        raise HTTPException(
            status_code=400,
            detail=f"This referral link is no longer valid (status: {invitation.status})"
        )

    # 4. Existing authenticated user
    if current_user_mobile:

        user = db.execute(
            select(User).where(
                User.mobile_number == current_user_mobile
            )
        ).scalars().first()

        if user:

            # Field Engineer
            if user.role == UserRole.FIELD_ENGINEER:

                # Consume invitation
                if (
                    not invitation.is_used
                    and invitation.status == "pending"
                ):
                    invitation.is_used = True
                    invitation.used_by_user_id = user.id
                    invitation.status = "accepted"

                    db.commit()
                    db.refresh(invitation)

                redirect_url = (
                    f"{settings.FRONTEND_URL}"
                    f"/engineer/dashboard"
                    f"?referral_token={token}"
                )

                return {
                    "status": "success",
                    "message": "Referral invitation processed successfully",
                    "redirect_url": redirect_url,
                    "referral_token": token
                }

            # Existing non-engineer user
            redirect_url = (
                f"{settings.FRONTEND_URL}"
                f"/dashboard"
                f"?referral_token={token}"
            )

            return {
                "status": "success",
                "message": "Referral invitation processed successfully",
                "redirect_url": redirect_url,
                "referral_token": token
            }

    # 5. New / unauthenticated user
    redirect_url = (
        f"{settings.FRONTEND_URL}"
        f"/register"
        f"?referral_token={token}"
    )

    return {
        "status": "success",
        "message": "Valid referral invitation",
        "redirect_url": redirect_url,
        "referral_token": token
    }