from pydantic import BaseModel, EmailStr
from app.profile.models import UserRole
from datetime import date
from typing import Optional
from datetime import time



class SignupSchema(BaseModel):
    email: EmailStr
    phone_number: str
    password: str
    role: UserRole

    company_name: Optional[str] = None
    owner_manager_name: Optional[str] = None
    vendor_type: Optional[str] = None


class SigninSchema(BaseModel):
    email: EmailStr
    password: str


class RequestOTPSchema(BaseModel):
    email: EmailStr


class VerifyOTPSchema(BaseModel):
    email: EmailStr
    otp: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponseSchema(BaseModel):
    message: str





class UserProfileSchema(BaseModel):
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    profile_image: Optional[str] = None


class AddressCreateSchema(BaseModel):
    address_type: str
    name: str
    flat_no: str
    street: str
    city: str
    state: str
    country: str
    postal_code: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    is_default: bool = False






# class AddressCreateSchema(BaseModel):
#     address_type: str
#     name: str
#     flat_no: str
#     street: str
#     city: str
#     state: str
#     country: str
#     postal_code: str
#     latitude: Optional[str] = None
#     longitude: Optional[str] = None
#     is_default: bool = False


class AddressUpdateSchema(BaseModel):
    address_type: Optional[str] = None
    name: Optional[str] = None
    flat_no: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    is_default: Optional[bool] = None

class FieldEngineerProfileSchema(BaseModel):
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    profile_image: Optional[str] = None

    is_associated_with_vendor: bool = False

    vendor_id: Optional[int] = None
    years_of_experience_id: Optional[int] = None
    primary_specialization_id: Optional[int] = None

    documents: Optional["FieldEngineerDocumentSchema"] = None
    availability: Optional[list["FieldEngineerAvailabilitySchema"]] = None


class FieldEngineerDocumentSchema(BaseModel):
    identity_proof: Optional[str] = None
    education_certificate: Optional[str] = None
    work_company_id: Optional[str] = None
    certification: Optional[str] = None
    experience_certificate: Optional[str] = None
    driving_license: Optional[str] = None


class FieldEngineerAvailabilitySchema(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time
    is_available: bool = True


class FieldEngineerServiceAreaSchema(BaseModel):
    primary_city: str
    service_radius: int
    preferred_work_areas: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
# FieldEngineerProfileSchema.model_rebuild()




class FEAddressCreateSchema(BaseModel):
    address_type: str

    country: str
    state: str
    postal_code: str

    area_locality: str
    city: str

    address_line1: str
    address_line2: Optional[str] = None

    latitude: Optional[str] = None
    longitude: Optional[str] = None

    is_default: bool = False


class FEAddressUpdateSchema(BaseModel):
    address_type: Optional[str] = None

    country: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None

    area_locality: Optional[str] = None
    city: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None

    latitude: Optional[str] = None
    longitude: Optional[str] = None

    is_default: Optional[bool] = None





class VendorSignupSchema(BaseModel):
    # User Table
    email: EmailStr
    phone_number: str
    password: str

    # Vendor Profile Table
    company_name: str
    owner_manager_name: str
    vendor_type: str


class VendorDocumentSchema(BaseModel):
    gst_certificate: Optional[str] = None
    pan_card: Optional[str] = None
    registration_certificate: Optional[str] = None
    cancelled_cheque: Optional[str] = None
    other_document: Optional[str] = None


class VendorServiceCoverageSchema(BaseModel):
    state: Optional[str] = None
    city: Optional[str] = None
    service_radius: Optional[int] = None


class VendorWorkforceSchema(BaseModel):
    total_engineers: Optional[int] = 0
    certified_engineers: Optional[int] = 0
    support_staff: Optional[int] = 0


class VendorBankDetailSchema(BaseModel):
    account_holder_name: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None


class VendorNotificationPreferenceSchema(BaseModel):
    email_notification: bool = True
    sms_notification: bool = False
    push_notification: bool = True

class VendorProfileSchema(BaseModel):
    company_name: str
    owner_manager_name: str

    vendor_type: Optional[str] = None
    legal_business_name: Optional[str] = None
    business_type: Optional[str] = None
    industry: Optional[str] = None

    company_registration_number: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None

    website: Optional[str] = None

    years_in_business: Optional[int] = None
    company_registration_date: Optional[date] = None
    employee_count: Optional[int] = None

    primary_service_category: Optional[str] = None
    about_business: Optional[str] = None

    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    timezone: Optional[str] = None
    working_hours: Optional[str] = None

    profile_image: Optional[str] = None

    documents: Optional[VendorDocumentSchema] = None
    service_coverage: Optional[list[VendorServiceCoverageSchema]] = None
    workforce: Optional[VendorWorkforceSchema] = None
    bank_details: Optional[VendorBankDetailSchema] = None
    notification_preferences: Optional[VendorNotificationPreferenceSchema] = None


FieldEngineerProfileSchema.model_rebuild()

VendorProfileSchema.model_rebuild()


