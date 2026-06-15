from pydantic import BaseModel, EmailStr
from app.profile.models import UserRole
from datetime import date
from typing import Optional
from pydantic import BaseModel

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


from pydantic import BaseModel
from datetime import date
from typing import Optional


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