from pydantic import BaseModel, EmailStr
from app.profile.models import UserRole
from datetime import date
from typing import Optional
from datetime import time


class SignupSchema(BaseModel):
    email: EmailStr
    password: str
    role: UserRole


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
FieldEngineerProfileSchema.model_rebuild()



