from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.hash import pbkdf2_sha256

from app.core.database import get_db

from app.profile.models import User
from app.profile.schemas import (
    SignupSchema,
    SigninSchema,
    RequestOTPSchema,
    VerifyOTPSchema
)

from app.utils.auth_utils import create_access_token
from app.utils.otp_utils import (
    send_otp_to_user,
    verify_otp_for_user,
    otp_store
)
from app.utils.mail_utils import send_email

router = APIRouter(
    prefix="/auth",
    tags=["Registration"]
)


@router.post("/signup")
async def signup(
    payload: SignupSchema,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(User).where(User.email == payload.email)
    )
    

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        email=payload.email,
        password_hash=pbkdf2_sha256.hash(payload.password),
        role=payload.role,
        is_verified=False
    )

    db.add(user)
    db.commit()

    return {
        "message": "User registered successfully"
    }


# @router.post("/signin")
# async def signin(
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

#     if not pbkdf2_sha256.verify(
#         payload.password,
#         user.password_hash
#     ):
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid credentials"
#         )

#     return {
#         "message": "Credentials verified successfully"
#     }
@router.post("/signin")
async def signin(
    payload: SigninSchema,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(User).where(User.email == payload.email)
    )

    user = result.scalars().first()

    print("INPUT EMAIL =", payload.email)
    print("INPUT PASSWORD =", payload.password)
    print("USER FOUND =", user)

    if user:
        print("DB EMAIL =", user.email)
        print("DB HASH =", user.password_hash)
        print(
            "PASSWORD MATCH =",
            pbkdf2_sha256.verify(
                payload.password,
                user.password_hash
            )
        )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not pbkdf2_sha256.verify(
        payload.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # return {
    #     "message": "Credentials verified successfully",
    #      "role": user.role.value
    # }
    token = create_access_token(
        {"sub": user.email}
    )

    return {
       "message": "Credentials verified successfully",
        "role": user.role.value,
        "access_token": token,
        "token_type": "bearer"
    }



@router.post("/request-otp")
async def request_otp(
    payload: RequestOTPSchema
):
    send_otp_to_user(payload.email)

    otp = otp_store[payload.email]["otp"]

    await send_email(
        recipient=payload.email,
        subject="OTP Verification",
        body=f"Your OTP is {otp}"
    )

    return {
        "message": "OTP sent successfully"
    }


# @router.post("/verify-otp")
# async def verify_otp(
#     payload: VerifyOTPSchema,
#     db: Session = Depends(get_db)
# ):
#     is_valid = verify_otp_for_user(
#         payload.email,
#         payload.otp
#     )

#     if not is_valid:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid OTP"
#         )

    # result = db.execute(
    #     select(User).where(User.email == payload.email)
    # )

    # user = result.scalars().first()

    # if not user:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="User not found"
    #     )

    # user.is_verified = True
    # db.commit()

    # token = create_access_token(
    #     {"sub": user.email}
    # )

    # return {
    #     "access_token": token,
    #     "token_type": "bearer"
    # }
@router.post("/verify-otp")
async def verify_otp(
    payload: VerifyOTPSchema
):
    is_valid = verify_otp_for_user(
        payload.email,
        payload.otp
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    return {
        "message": "OTP verified successfully"
    }