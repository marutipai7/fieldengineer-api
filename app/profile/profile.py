import profile
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.hash import pbkdf2_sha256
from fastapi import Form, File, UploadFile
import shutil
import os
from fastapi import Request
from datetime import date
from typing import Optional


from app.profile.schemas import VendorProfileSchema

from app.profile.models import (
    User,
    UserRole,
    UserProfile,
    CustomerIdentity,
    CustomerBusiness,
    CustomerDocument,
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
    request: Request,

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
    print("========== FE COMPLETE PROFILE API CALLED ==========")
    form = await request.form()

    print("===== FORM DATA =====")

    for key, value in form.items():
      print(key, "=", value)

    print("=====================")
    

    user = db.execute(
        select(User).where(
            User.email == current_user_email
        )
    ).scalars().first()
    print("========== POST USER ==========")
    print("Current Email:", current_user_email)
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

    # ----------------------------
    # Save Profile
    # ----------------------------
    # profile.full_name = payload.full_name
    # profile.date_of_birth = payload.date_of_birth
    # profile.gender = payload.gender
    # profile.profile_image = payload.profile_image
    if full_name is not None:
        profile.full_name = full_name

    if date_of_birth is not None:
       profile.date_of_birth = date_of_birth

    if gender is not None:
       profile.gender = gender

    if is_associated_with_vendor is not None:
        profile.is_associated_with_vendor = is_associated_with_vendor

    if vendor_id is not None:
       profile.vendor_id = vendor_id

    if years_of_experience_id is not None:
        profile.years_of_experience_id = years_of_experience_id

    if primary_specialization_id is not None:
        profile.primary_specialization_id = primary_specialization_id

    # profile.is_associated_with_vendor = is_associated_with_vendor
    # profile.vendor_id = vendor_id
    # profile.is_associated_with_vendor = is_associated_with_vendor

    # if is_associated_with_vendor:
    #     profile.vendor_id = vendor_id
    # else:
    #     profile.vendor_id = None
    # profile.years_of_experience_id = years_of_experience_id
    # profile.primary_specialization_id = primary_specialization_id
    # ----------------------------
    # Save Profile Image
    # ----------------------------

    if profile_image:

       os.makedirs("uploads/field_engineer", exist_ok=True)

       image_path = f"uploads/field_engineer/{profile_image.filename}"

       with open(image_path, "wb") as buffer:
           shutil.copyfileobj(profile_image.file, buffer)

       profile.profile_image = image_path


    # profile.is_associated_with_vendor = (
    #     payload.is_associated_with_vendor
    # )

    # profile.vendor_id = payload.vendor_id
    # profile.years_of_experience_id = (
    #     payload.years_of_experience_id
    # )
    # profile.primary_specialization_id = (
    #     payload.primary_specialization_id
    # )
    # ----------------------------
    ###Save Documents###
    #----------------------------
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


    # ----------------------------
    # Save Availability
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
    # ----------------------------
    # Save Availability
    # ----------------------------

    availability = FieldEngineerAvailability(
        field_engineer_id=profile.id,
        day_of_week=1,
        start_time="10:00:00",
        end_time="19:00:00",
        is_available=True
    )

    db.add(availability)
    print("========== DOCUMENT VALUES ==========")
    print("Profile ID:", profile.id)
    print("Identity:", document.identity_proof)
    print("Education:", document.education_certificate)
    print("Company:", document.work_company_id)
    print("Certification:", document.certification)
    print("Experience:", document.experience_certificate)
    print("License:", document.driving_license)
    print("====================================")
    print("========== POST DOCUMENT ==========")
    print("Profile ID:", profile.id)
    print("Identity:", document.identity_proof)
    print("Education:", document.education_certificate)
    print("Company:", document.work_company_id)
    print("Certification:", document.certification)
    print("Experience:", document.experience_certificate)
    print("License:", document.driving_license)
    print("===================================")



    availability_data = db.execute(
        select(FieldEngineerAvailability).where(
            FieldEngineerAvailability.field_engineer_id == profile.id
        )
    ).scalars().all()

    print("========== AVAILABILITY ==========")
    print("Profile ID:", profile.id)

    for item in availability_data:
        print(
            item.day_of_week,
            item.start_time,
            item.end_time,
            item.is_available
        )

    print("==================================")

    db.commit()
    db.refresh(profile)

    return {
        "message": "Field Engineer profile completed successfully",
        "profile_id": profile.id
    }


@router.get("/field-engineer/me")
async def get_field_engineer_profile(
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    # Get logged in user
    user = db.execute(
        select(User).where(User.email == current_user_email)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    print("========== GET API ==========")
    print("Current Email:", current_user_email)
    print("User ID:", user.id)
    print("Role:", user.role)

    # Check role
    # if user.role != UserRole.field_engineer:
    if user.role != UserRole.FIELD_ENGINEER:
        raise HTTPException(
            status_code=403,
            detail="Only Field Engineer can access this API"
        )

    # Get profile
    profile = db.execute(
        select(UserProfile).where(
            UserProfile.user_id == user.id
        )
    ).scalars().first()

    print("Profile:", profile)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    # Get documents
    document = db.execute(
        select(FieldEngineerDocument).where(
            FieldEngineerDocument.user_profile_id == profile.id
        )
    ).scalars().first()
    print("Profile:", profile)

    # Get availability
    availability = db.execute(
        select(FieldEngineerAvailability).where(
            FieldEngineerAvailability.field_engineer_id == profile.id
        )
    ).scalars().all()

    print("Profile:", profile)

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




# @router.put("/profile")
@router.put("/update")
async def update_field_engineer_profile(
    full_name: str = Form(None),
    date_of_birth: date = Form(None),
    gender: str = Form(None),
    is_associated_with_vendor: bool = Form(None),
    vendor_id: Optional[int] = Form(None),
    years_of_experience_id: int = Form(None),
    primary_specialization_id: int = Form(None),

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
    profile.full_name = full_name
    profile.date_of_birth = date_of_birth   
    profile.gender = gender
    profile.is_associated_with_vendor = is_associated_with_vendor
    profile.vendor_id = vendor_id
    profile.years_of_experience_id = years_of_experience_id
    profile.primary_specialization_id = primary_specialization_id

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

    db.commit()
    db.refresh(profile)

    return {
        "message": "Field Engineer profile updated successfully",
        "profile_id": profile.id
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

# Complete Customer Profile

@router.post("/customer/complete-profile")
async def complete_customer_profile(

    # Personal Details
    full_name: str = Form(...),
    date_of_birth: date = Form(...),
    gender: str = Form(...),
    profile_image: UploadFile = File(None),
    email: str = Form(...),
    phone_number: str = Form(...),

    # Identity
    identity_type: str = Form(...),
    identity_number: str = Form(...),
    front_image: UploadFile = File(None),
    back_image: UploadFile = File(None),

    # Business
    company_name: str = Form(...),
    business_type: str = Form(...),
    industry: str = Form(...),
    website: Optional[str] = Form(None),
    office_address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    pincode: str = Form(...),
    gst_number: Optional[str] = Form(None),
    tax_number: Optional[str] = Form(None),
    authorized_person_name: str = Form(...),
    designation: str = Form(...),
    work_email: str = Form(...),

    # Documents
    gst_certificate: UploadFile = File(None),
    tax_identification_card: UploadFile = File(None),
    company_registration_certificate: UploadFile = File(None),
    moa_aoa: UploadFile = File(None),
    bank_account_proof: UploadFile = File(None),

    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):

    user, profile = get_user_and_profile(
        current_user_email,
        db
    )

    if user.role != UserRole.USER:
        raise HTTPException(
            status_code=403,
            detail="Only Customer can complete profile"
        )

    if not profile:
        profile = UserProfile(
            user_id=user.id
        )
        db.add(profile)
        db.flush()

    os.makedirs("uploads", exist_ok=True)

    def save_file(file: UploadFile):
        if not file:
            return None

        filename = f"{uuid.uuid4()}_{file.filename}"
        path = os.path.join("uploads", filename)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return path

    # ---------------------------------------
    # User Profile
    # ---------------------------------------

    profile.full_name = full_name
    profile.date_of_birth = date_of_birth
    profile.gender = gender

    profile_image_path = save_file(profile_image)

    if profile_image_path:
        profile.profile_image = profile_image_path

    user.email = email
    user.phone_number = phone_number

    # ---------------------------------------
    # Customer Identity
    # ---------------------------------------

    identity = db.execute(
        select(CustomerIdentity).where(
            CustomerIdentity.user_profile_id == profile.id
        )
    ).scalars().first()

    if not identity:
        identity = CustomerIdentity(
            user_profile_id=profile.id
        )
        db.add(identity)

    identity.identity_type = identity_type
    identity.identity_number = identity_number

    front_path = save_file(front_image)
    if front_path:
        identity.front_image = front_path

    back_path = save_file(back_image)
    if back_path:
        identity.back_image = back_path

    # ---------------------------------------
    # Customer Business
    # ---------------------------------------

    business = db.execute(
        select(CustomerBusiness).where(
            CustomerBusiness.user_profile_id == profile.id
        )
    ).scalars().first()

    if not business:
        business = CustomerBusiness(
            user_profile_id=profile.id
        )
        db.add(business)

    business.company_name = company_name
    business.business_type = business_type
    business.industry = industry
    business.website = website
    business.office_address = office_address
    business.city = city
    business.state = state
    business.pincode = pincode
    business.gst_number = gst_number
    business.tax_number = tax_number
    business.authorized_person_name = authorized_person_name
    business.designation = designation
    business.work_email = work_email
    # ---------------------------------------
    # Customer Documents
    # ---------------------------------------

    documents = db.execute(
        select(CustomerDocument).where(
            CustomerDocument.user_profile_id == profile.id
        )
    ).scalars().first()

    if not documents:
        documents = CustomerDocument(
            user_profile_id=profile.id
        )
        db.add(documents)

    gst_path = save_file(gst_certificate)
    if gst_path:
        documents.gst_certificate = gst_path

    tax_path = save_file(tax_identification_card)
    if tax_path:
        documents.tax_identification_card = tax_path

    company_path = save_file(company_registration_certificate)
    if company_path:
        documents.company_registration_certificate = company_path

    moa_path = save_file(moa_aoa)
    if moa_path:
        documents.moa_aoa = moa_path

    bank_path = save_file(bank_account_proof)
    if bank_path:
        documents.bank_account_proof = bank_path


    print("========== CUSTOMER PROFILE ==========")
    print("User ID:", user.id)
    print("Profile ID:", profile.id)
    print("======================================")

    db.commit()
    db.refresh(profile)

    return {
        "message": "Customer profile completed successfully",
        "profile_id": profile.id,
        "email": user.email,
        "phone_number": user.phone_number
    }

# Get Customer Profile

@router.get("/customer/profile")
async def get_customer_profile(
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    user, profile = get_user_and_profile(
        current_user_email,
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

    return {

        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role.value,

        "profile": {
            "full_name": profile.full_name,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "profile_image": profile.profile_image
        },

        "identity": {
            "identity_type": identity.identity_type if identity else None,
            "identity_number": identity.identity_number if identity else None,
            "front_image": identity.front_image if identity else None,
            "back_image": identity.back_image if identity else None,
            "verified": identity.verified if identity else False
        },

        "business": {
            "company_name": business.company_name if business else None,
            "business_type": business.business_type if business else None,
            "industry": business.industry if business else None,
            "website": business.website if business else None,
            "office_address": business.office_address if business else None,
            "city": business.city if business else None,
            "state": business.state if business else None,
            "pincode": business.pincode if business else None,
            "gst_number": business.gst_number if business else None,
            "tax_number": business.tax_number if business else None,
            "authorized_person_name": business.authorized_person_name if business else None,
            "designation": business.designation if business else None,
            "work_email": business.work_email if business else None,
        },

        "documents": {
            "gst_certificate": documents.gst_certificate if documents else None,
            "tax_identification_card": documents.tax_identification_card if documents else None,
            "company_registration_certificate": documents.company_registration_certificate if documents else None,
            "moa_aoa": documents.moa_aoa if documents else None,
            "bank_account_proof": documents.bank_account_proof if documents else None,
            "other_document": documents.other_document if documents else None,
        }
    }

# Update Customer Profile

@router.put("/customer/profile")
async def update_customer_profile(

    # Personal
    full_name: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    date_of_birth: Optional[date] = Form(None),
    gender: Optional[str] = Form(None),
    email: Optional[str] = Form(None),

    profile_image: UploadFile = File(None),

    # Identity
    identity_type: Optional[str] = Form(None),
    identity_number: Optional[str] = Form(None),

    front_image: UploadFile = File(None),
    back_image: UploadFile = File(None),

    # Business
    company_name: Optional[str] = Form(None),
    business_type: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    website: Optional[str] = Form(None),

    office_address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),

    gst_number: Optional[str] = Form(None),
    tax_number: Optional[str] = Form(None),

    authorized_person_name: Optional[str] = Form(None),
    designation: Optional[str] = Form(None),
    work_email: Optional[str] = Form(None),

    # Documents
    gst_certificate: UploadFile = File(None),
    tax_identification_card: UploadFile = File(None),
    company_registration_certificate: UploadFile = File(None),
    moa_aoa: UploadFile = File(None),
    bank_account_proof: UploadFile = File(None),

    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):

    user, profile = get_user_and_profile(
        current_user_email,
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
    
    if email is not None:
        raise HTTPException(
        status_code=400,
        detail="Primary email cannot be updated."
        )

    os.makedirs("uploads", exist_ok=True)

    def save_file(file: UploadFile):
        if not file:
            return None

        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join("uploads", filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return file_path

    # -------------------------
    # Update User
    # -------------------------

    if phone_number is not None:
        user.phone_number = phone_number

    # Email is taken from JWT/current_user_email.
    # Do not allow updating the login email.

    # -------------------------
    # Update Profile
    # -------------------------

    if full_name is not None:
        profile.full_name = full_name

    if date_of_birth is not None:
        profile.date_of_birth = date_of_birth

    if gender is not None:
        profile.gender = gender

    image = save_file(profile_image)
    if image:
        profile.profile_image = image

    # -------------------------
    # Identity
    # -------------------------

    identity = db.execute(
        select(CustomerIdentity).where(
            CustomerIdentity.user_profile_id == profile.id
        )
    ).scalars().first()

    if not identity:
        identity = CustomerIdentity(
            user_profile_id=profile.id
        )
        db.add(identity)

    if identity_type is not None:
        identity.identity_type = identity_type

    if identity_number is not None:
        identity.identity_number = identity_number

    front = save_file(front_image)
    if front:
        identity.front_image = front

    back = save_file(back_image)
    if back:
        identity.back_image = back

    # -------------------------
    # Business
    # -------------------------

    business = db.execute(
        select(CustomerBusiness).where(
            CustomerBusiness.user_profile_id == profile.id
        )
    ).scalars().first()

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

    if website is not None:
        business.website = website

    if office_address is not None:
        business.office_address = office_address

    if city is not None:
        business.city = city

    if state is not None:
        business.state = state

    if pincode is not None:
        business.pincode = pincode

    if gst_number is not None:
        business.gst_number = gst_number

    if tax_number is not None:
        business.tax_number = tax_number

    if authorized_person_name is not None:
        business.authorized_person_name = authorized_person_name

    if designation is not None:
        business.designation = designation

    if work_email is not None:
        business.work_email = work_email

    # -------------------------
    # Documents
    # -------------------------

    documents = db.execute(
        select(CustomerDocument).where(
            CustomerDocument.user_profile_id == profile.id
        )
    ).scalars().first()

    if not documents:
        documents = CustomerDocument(
            user_profile_id=profile.id
        )
        db.add(documents)

    gst = save_file(gst_certificate)
    if gst:
        documents.gst_certificate = gst

    tax = save_file(tax_identification_card)
    if tax:
        documents.tax_identification_card = tax

    company = save_file(company_registration_certificate)
    if company:
        documents.company_registration_certificate = company

    moa = save_file(moa_aoa)
    if moa:
        documents.moa_aoa = moa

    bank = save_file(bank_account_proof)
    if bank:
        documents.bank_account_proof = bank

    db.commit()
    db.refresh(profile)

    return {
        "success": True,
        "message": "Customer profile updated successfully",
        "email": user.email,
        "profile_id": profile.id
    }