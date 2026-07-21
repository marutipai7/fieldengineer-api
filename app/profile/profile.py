import profile

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.hash import pbkdf2_sha256

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
@router.get("/me")
async def get_profile(
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

@router.put("/update")
async def update_profile(
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
@router.post("/signin")
async def field_engineer_signin(
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
async def complete_profile(
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
async def vendor_complete_profile(
    payload: VendorProfileSchema,
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

    profile.company_name = payload.company_name
    profile.owner_manager_name = payload.owner_manager_name

    profile.vendor_type = payload.vendor_type
    profile.legal_business_name = payload.legal_business_name
    profile.business_type = payload.business_type
    profile.industry = payload.industry

    profile.company_registration_number = (
        payload.company_registration_number
    )

    profile.gst_number = payload.gst_number
    profile.pan_number = payload.pan_number

    profile.website = payload.website

    profile.years_in_business = (
        payload.years_in_business
    )

    profile.company_registration_date = (
        payload.company_registration_date
    )

    profile.employee_count = payload.employee_count

    profile.primary_service_category = (
        payload.primary_service_category
    )

    profile.about_business = (
        payload.about_business
    )

    profile.address = payload.address
    profile.city = payload.city
    profile.state = payload.state
    profile.pincode = payload.pincode

    profile.timezone = payload.timezone
    profile.working_hours = payload.working_hours

    profile.profile_image = payload.profile_image
        # ----------------------------
    # Save Vendor Documents
    # ----------------------------
    if payload.documents:

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

        document.gst_certificate = (
            payload.documents.gst_certificate
        )

        document.pan_card = (
            payload.documents.pan_card
        )

        document.registration_certificate = (
            payload.documents.registration_certificate
        )

        document.cancelled_cheque = (
            payload.documents.cancelled_cheque
        )

        document.other_document = (
            payload.documents.other_document
        )
    
    # ----------------------------
    # Save Service Coverage
    # ----------------------------
    if payload.service_coverage:

        db.query(VendorServiceCoverage).filter(
            VendorServiceCoverage.vendor_profile_id == profile.id
        ).delete()

        for item in payload.service_coverage:

            coverage = VendorServiceCoverage(
                vendor_profile_id=profile.id,
                state=item.state,
                city=item.city,
                service_radius=item.service_radius
            )

            db.add(coverage)
            # ----------------------------
    # Save Workforce
    # ----------------------------
    if payload.workforce:

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

        workforce.total_engineers = (
            payload.workforce.total_engineers
        )

        workforce.certified_engineers = (
            payload.workforce.certified_engineers
        )

        workforce.support_staff = (
            payload.workforce.support_staff
        )
        # ----------------------------
    # Save Bank Details
    # ----------------------------
    if payload.bank_details:

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

        bank.account_holder_name = (
            payload.bank_details.account_holder_name
        )

        bank.bank_name = (
            payload.bank_details.bank_name
        )

        bank.account_number = (
            payload.bank_details.account_number
        )

        bank.ifsc_code = (
            payload.bank_details.ifsc_code
        )

        bank.branch_name = (
            payload.bank_details.branch_name
        )
        # ----------------------------
    # Save Notification Preferences
    # ----------------------------
    if payload.notification_preferences:

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

        notification.email_notification = (
            payload.notification_preferences.email_notification
        )

        notification.sms_notification = (
            payload.notification_preferences.sms_notification
        )

        notification.push_notification = (
            payload.notification_preferences.push_notification
        )
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
    payload: VendorProfileSchema,
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

    profile.company_name = payload.company_name
    profile.owner_manager_name = payload.owner_manager_name
    profile.vendor_type = payload.vendor_type
    profile.legal_business_name = payload.legal_business_name
    profile.business_type = payload.business_type
    profile.industry = payload.industry

    profile.company_registration_number = payload.company_registration_number
    profile.gst_number = payload.gst_number
    profile.pan_number = payload.pan_number

    profile.website = payload.website
    profile.years_in_business = payload.years_in_business
    profile.company_registration_date = payload.company_registration_date
    profile.employee_count = payload.employee_count

    profile.primary_service_category = payload.primary_service_category
    profile.about_business = payload.about_business

    profile.address = payload.address
    profile.city = payload.city
    profile.state = payload.state
    profile.pincode = payload.pincode

    profile.timezone = payload.timezone
    profile.working_hours = payload.working_hours
    profile.profile_image = payload.profile_image

    # ----------------------------
    # Update Documents
    # ----------------------------

    if payload.documents:

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

        document.gst_certificate = payload.documents.gst_certificate
        document.pan_card = payload.documents.pan_card
        document.registration_certificate = payload.documents.registration_certificate
        document.cancelled_cheque = payload.documents.cancelled_cheque
        document.other_document = payload.documents.other_document

    # ----------------------------
    # Update Service Coverage
    # ----------------------------

    if payload.service_coverage:

        db.query(VendorServiceCoverage).filter(
            VendorServiceCoverage.vendor_profile_id == profile.id
        ).delete()

        for item in payload.service_coverage:

            coverage = VendorServiceCoverage(
                vendor_profile_id=profile.id,
                state=item.state,
                city=item.city,
                service_radius=item.service_radius
            )

            db.add(coverage)

    # ----------------------------
    # Update Workforce
    # ----------------------------

    if payload.workforce:

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

        workforce.total_engineers = payload.workforce.total_engineers
        workforce.certified_engineers = payload.workforce.certified_engineers
        workforce.support_staff = payload.workforce.support_staff

    # ----------------------------
    # Update Bank Details
    # ----------------------------

    if payload.bank_details:

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

        bank.account_holder_name = payload.bank_details.account_holder_name
        bank.bank_name = payload.bank_details.bank_name
        bank.account_number = payload.bank_details.account_number
        bank.ifsc_code = payload.bank_details.ifsc_code
        bank.branch_name = payload.bank_details.branch_name

    # ----------------------------
    # Update Notification
    # ----------------------------

    if payload.notification_preferences:

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

        notification.email_notification = payload.notification_preferences.email_notification
        notification.sms_notification = payload.notification_preferences.sms_notification
        notification.push_notification = payload.notification_preferences.push_notification

    db.commit()
    db.refresh(profile)

    return {
        "message": "Vendor profile updated successfully",
        "profile_id": profile.id
    }


