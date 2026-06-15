from pydantic import BaseModel, EmailStr
from app.profile.models import UserRole


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