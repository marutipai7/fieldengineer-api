import profile

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.hash import pbkdf2_sha256
from fastapi import Form, File, UploadFile
import shutil
import os
from fastapi import Request
from datetime import date


from app.profile.schemas import VendorProfileSchema

from app.profile.models import (
    VendorProfile,
    VendorDocument,
    VendorServiceCoverage,
    VendorWorkforce,
    VendorBankDetail,
    VendorNotificationPreference,
)



from app.utils.auth_utils import (
    create_access_token,
    get_current_user_email
)

from app.profile.schemas import (
    SigninSchema,
    FieldEngineerProfileSchema
)


from app.core.database import get_db
from app.utils.auth_utils import get_current_user_email

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



# @router.get("/me")
# async def get_profile(
#     current_user_email: str = Depends(get_current_user_email),
#     db: Session = Depends(get_db)
# ):
#     user, profile = get_user_and_profile(
#         current_user_email,
#         db
#     )

#     return {
#         "email": user.email,
#         "phone_number": user.phone_number,
#         "role": user.role.value,
#         "profile": {
#             "full_name": profile.full_name if profile else None,
#             "date_of_birth": profile.date_of_birth if profile else None,
#             "gender": profile.gender if profile else None,
#             "profile_image": profile.profile_image if profile else None
#         }
#     }

# @router.put("/update")
# async def update_profile(
#     payload: UserProfileSchema,
#     current_user_email: str = Depends(get_current_user_email),
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
@router.post("/complete-profile")
async def complete_field_engineer_profile(

    full_name: str = Form(...),
    date_of_birth: date = Form(None),
    gender: str = Form(None),

    is_associated_with_vendor: bool = Form(False),

    vendor_id: int = Form(None),
    years_of_experience_id: int = Form(None),
    primary_specialization_id: int = Form(None),

    primary_city: str = Form(None),
    service_radius: int = Form(None),
    preferred_work_areas: str = Form(None),
    latitude: str = Form(None),
    longitude: str = Form(None),

    profile_image: UploadFile = File(None),

    identity_proof: UploadFile = File(None),
    education_certificate: UploadFile = File(None),
    work_company_id: UploadFile = File(None),
    certification: UploadFile = File(None),
    experience_certificate: UploadFile = File(None),
    driving_license: UploadFile = File(None),

    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(User).where(User.email == payload.email)
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if user.role.value != "field_engineer":
        raise HTTPException(
            status_code=403,
            detail="Only Field Engineer can login"
        )

    if not pbkdf2_sha256.verify(
        payload.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        {"sub": user.email}
    )

    return {
        "message": "Field Engineer signed in successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value
    }

@router.post("/complete-profile")
async def complete_field_engineer_profile(
    payload: FieldEngineerProfileSchema,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(
            User.email == current_user_email
        )
    ).scalars().first()

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

    # ----------------------------
    # Save Profile
    # ----------------------------
    profile.full_name = payload.full_name
    profile.date_of_birth = payload.date_of_birth
    profile.gender = payload.gender
    profile.profile_image = payload.profile_image

    profile.is_associated_with_vendor = (
        payload.is_associated_with_vendor
    )

    profile.vendor_id = payload.vendor_id
    profile.years_of_experience_id = (
        payload.years_of_experience_id
    )
    profile.primary_specialization_id = (
        payload.primary_specialization_id
    )

    # ----------------------------
    # Save Documents
    # ----------------------------
    if payload.documents:

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

        document.identity_proof = payload.documents.identity_proof
        document.education_certificate = (
            payload.documents.education_certificate
        )
        document.work_company_id = (
            payload.documents.work_company_id
        )
        document.certification = (
            payload.documents.certification
        )
        document.experience_certificate = (
            payload.documents.experience_certificate
        )
        document.driving_license = (
            payload.documents.driving_license
        )

    # ----------------------------
    # Save Availability
    # ----------------------------
    if payload.availability:

        db.query(FieldEngineerAvailability).filter(
            FieldEngineerAvailability.field_engineer_id == profile.id
        ).delete()

        for item in payload.availability:

            availability = FieldEngineerAvailability(
                field_engineer_id=profile.id,
                day_of_week=item.day_of_week,
                start_time=item.start_time,
                end_time=item.end_time,
                is_available=item.is_available
            )

            db.add(availability)

    db.commit()
    db.refresh(profile)

    return {
        "message": "Field Engineer profile completed successfully",
        "profile_id": profile.id
    }


@router.get("/profile")
async def get_field_engineer_profile(
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_email,
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

    availability = db.execute(
        select(FieldEngineerAvailability).where(
            FieldEngineerAvailability.field_engineer_id == profile.id
        )
    ).scalars().all()

    return {
        "email": user.email,
        "phone_number": user.phone_number,
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




@router.put("/profile")
async def update_field_engineer_profile(
    payload: FieldEngineerProfileSchema,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_email,
        db
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    # ----------------------------
    # Update Profile
    # ----------------------------
    profile.full_name = payload.full_name
    profile.date_of_birth = payload.date_of_birth
    profile.gender = payload.gender
    profile.profile_image = payload.profile_image

    profile.is_associated_with_vendor = (
        payload.is_associated_with_vendor
    )

    profile.vendor_id = payload.vendor_id

    profile.years_of_experience_id = (
        payload.years_of_experience_id
    )

    profile.primary_specialization_id = (
        payload.primary_specialization_id
    )

    # ----------------------------
    # Update Documents
    # ----------------------------
    if payload.documents:

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

        document.identity_proof = payload.documents.identity_proof
        document.education_certificate = payload.documents.education_certificate
        document.work_company_id = payload.documents.work_company_id
        document.certification = payload.documents.certification
        document.experience_certificate = payload.documents.experience_certificate
        document.driving_license = payload.documents.driving_license

    # ----------------------------
    # Update Availability
    # ----------------------------
    if payload.availability:

        db.query(FieldEngineerAvailability).filter(
            FieldEngineerAvailability.field_engineer_id == profile.id
        ).delete()

        for item in payload.availability:

            availability = FieldEngineerAvailability(
                field_engineer_id=profile.id,
                day_of_week=item.day_of_week,
                start_time=item.start_time,
                end_time=item.end_time,
                is_available=item.is_available
            )

            db.add(availability)

    db.commit()
    db.refresh(profile)

    return {
        "message": "Field Engineer profile updated successfully",
        "profile_id": profile.id
    }





@router.post("/vendor/signin")
async def vendor_signin(
    payload: SigninSchema,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(User).where(User.email == payload.email)
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=403,
            detail="Only Vendor can login"
        )

    if not pbkdf2_sha256.verify(
        payload.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        {"sub": user.email}
    )

    return {
        "message": "Vendor signed in successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value
    }


@router.post("/vendor/complete-profile")
# async def vendor_complete_profile(
#     payload: VendorProfileSchema,
# async def vendor_complete_profile(
async def vendor_complete_profile(
    request: Request,

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
    other_document: UploadFile = File(None),

    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    
    form = await request.form()

    print("========== FORM DATA ==========")

    for key, value in form.items():
       print(key, "=", value)

    print("===============================")
    user = db.execute(
        select(User).where(
            User.email == current_user_email
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
    # Save Vendor Profile
    # ----------------------------

    # profile.company_name = payload.company_name
    # profile.owner_manager_name = payload.owner_manager_name
    print("company_name =", company_name)
    print("vendor_type =", vendor_type)
    print("legal_business_name =", legal_business_name)
    print("business_type =", business_type)
    print("industry =", industry)
    print("gst_number =", gst_number)
    print("website =", website)
    print("years_in_business =", years_in_business)
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
    # ----------------------------
    # Save Vendor Documents
    # ----------------------------
   # ----------------------------
   # Save Vendor Documents
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
    # ----------------------------
    # Save Service Coverage
    # ----------------------------
    # if payload.service_coverage:

    #     db.query(VendorServiceCoverage).filter(
    #         VendorServiceCoverage.vendor_profile_id == profile.id
    #     ).delete()

    #     for item in payload.service_coverage:

    #         coverage = VendorServiceCoverage(
    #             vendor_profile_id=profile.id,
    #             state=item.state,
    #             city=item.city,
    #             service_radius=item.service_radius
    #         )

    #         db.add(coverage)
            # ----------------------------
    # Save Workforce
    # ----------------------------
    # if payload.workforce:

    #     workforce = db.execute(
    #         select(VendorWorkforce).where(
    #             VendorWorkforce.vendor_profile_id == profile.id
    #         )
    #     ).scalars().first()

    #     if not workforce:
    #         workforce = VendorWorkforce(
    #             vendor_profile_id=profile.id
    #         )
    #         db.add(workforce)

    #     workforce.total_engineers = (
    #         payload.workforce.total_engineers
    #     )

    #     workforce.certified_engineers = (
    #         payload.workforce.certified_engineers
    #     )

    #     workforce.support_staff = (
    #         payload.workforce.support_staff
    #     )
        # ----------------------------
    # # Save Bank Details
    # # ----------------------------
    # if payload.bank_details:

    #     bank = db.execute(
    #         select(VendorBankDetail).where(
    #             VendorBankDetail.vendor_profile_id == profile.id
    #         )
    #     ).scalars().first()

    #     if not bank:
    #         bank = VendorBankDetail(
    #             vendor_profile_id=profile.id
    #         )
    #         db.add(bank)

    #     bank.account_holder_name = (
    #         payload.bank_details.account_holder_name
    #     )

    #     bank.bank_name = (
    #         payload.bank_details.bank_name
    #     )

    #     bank.account_number = (
    #         payload.bank_details.account_number
    #     )

    #     bank.ifsc_code = (
    #         payload.bank_details.ifsc_code
    #     )

    #     bank.branch_name = (
    #         payload.bank_details.branch_name
    #     )
    #     # ----------------------------
    # # Save Notification Preferences
    # # ----------------------------
    # if payload.notification_preferences:

    #     notification = db.execute(
    #         select(VendorNotificationPreference).where(
    #             VendorNotificationPreference.vendor_profile_id == profile.id
    #         )
    #     ).scalars().first()

    #     if not notification:
    #         notification = VendorNotificationPreference(
    #             vendor_profile_id=profile.id
    #         )
    #         db.add(notification)

    #     notification.email_notification = (
    #         payload.notification_preferences.email_notification
    #     )

    #     notification.sms_notification = (
    #         payload.notification_preferences.sms_notification
    #     )

    #     notification.push_notification = (
    #         payload.notification_preferences.push_notification
    #     )
    print(profile.vendor_type)
    print(profile.legal_business_name)
    print(profile.business_type)
    print(profile.industry)
    print(profile.gst_number)
    db.commit()
    db.refresh(profile)

    return {
        "message": "Vendor profile completed successfully",
        "profile_id": profile.id
    }
    

@router.get("/vendor/profile")
async def get_vendor_profile(
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.email == current_user_email)
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



@router.put("/vendor/profile")
async def update_vendor_profile(

    company_name: str = Form(...),
    owner_manager_name: str = Form(...),

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

    profile_image: UploadFile = File(None),

    gst_certificate: UploadFile = File(None),
    pan_card: UploadFile = File(None),
    registration_certificate: UploadFile = File(None),
    cancelled_cheque: UploadFile = File(None),
    other_document: UploadFile = File(None),

    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):

    user = db.execute(
        select(User).where(
            User.email == current_user_email
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