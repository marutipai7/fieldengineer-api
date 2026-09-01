from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.hash import pbkdf2_sha256

from app.core.database import get_db

from app.profile.models import (
    User,
    UserProfile,
    VendorProfile,
    UserRole
)
from app.profile.schemas import (
    SignupSchema,
    SigninSchema,
    RequestOTPSchema,
    VerifyOTPSchema,
)

from app.utils.auth_utils import create_access_token
from app.utils.otp_utils import (
    send_otp_to_user,
    verify_otp_for_user,
    otp_store
)

router = APIRouter(
    prefix="/auth",
    tags=["Registration"]
)





@router.post("/request-otp")
async def request_otp(
    payload: RequestOTPSchema,
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.mobile_number == payload.mobile_number)
    ).scalars().first()

    if payload.action == "signup":

        if user:
            raise HTTPException(
                status_code=400,
                detail="Mobile number already registered"
            )

    else:

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if user.role != payload.role:
            raise HTTPException(
                status_code=400,
                detail="Invalid role"
            )

    send_otp_to_user(payload.mobile_number)
    otp_store[payload.mobile_number]["role"] = payload.role
    otp_store[payload.mobile_number]["action"] = payload.action
    otp = otp_store[payload.mobile_number]["otp"]

    return {
        "message": "OTP sent successfully",
        "OTP": otp  # For testing purposes, return the OTP in the response
    }



@router.post("/verify-otp")
async def verify_otp(
    payload: VerifyOTPSchema,
    db: Session = Depends(get_db)
):
    is_valid = verify_otp_for_user(
        payload.mobile_number,
        payload.otp
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    stored_data = otp_store.get(payload.mobile_number)

    if not stored_data:
        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    role = stored_data["role"]
    request_action = stored_data["action"]
    verify_action = payload.action

    user = db.execute(
        select(User).where(User.mobile_number == payload.mobile_number)
    ).scalars().first()

    # -----------------------------
    # CREATE USER WHEN REQUIRED
    # -----------------------------
    if not user:

        if request_action == "signup":

            user = User(
                mobile_number=payload.mobile_number,
                password_hash="OTP_LOGIN",
                role=role,
                is_verified=True
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            if role in [
                UserRole.USER,
                UserRole.FIELD_ENGINEER
            ]:

                db.add(
                    UserProfile(
                        user_id=user.id
                    )
                )

            elif role == UserRole.VENDOR:

                db.add(
                    VendorProfile(
                        user_id=user.id
                    )
                )

            db.commit()

        else:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

    # -----------------------------
    # EMAIL ALREADY EXISTS DURING
    # NORMAL SIGNUP
    # -----------------------------
    elif (
        request_action == "signup"
        and verify_action == "signup"
    ):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    token = create_access_token(
        {
            "sub": user.mobile_number
        }
    )

    return {
        "message": "Success",
        "role": user.role.value,
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/signup")
async def signup(
    payload: SignupSchema,
    db: Session = Depends(get_db)
):
    #Check if email already exists
    result = db.execute(
        select(User).where(User.mobile_number == payload.mobile_number)
    )

    if existing_user := result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )

    # # Create User
    user = User(
        mobile_number=payload.mobile_number,
        password_hash=pbkdf2_sha256.hash(payload.password),
        role=payload.role,
        is_verified=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

#     # Create UserProfile for Customer & Field Engineer
#     if payload.role in [UserRole.USER, UserRole.FIELD_ENGINEER]:

#         user_profile = UserProfile(
#             user_id=user.id
#         )

#         db.add(user_profile)
#         db.commit()

#     # Create VendorProfile for Vendor
#     if payload.role == UserRole.VENDOR:

#         vendor_profile = VendorProfile(
#             user_id=user.id
#         )

#         db.add(vendor_profile)
#         db.commit()

    return {
        "message": "User registered successfully",
        "role": user.role.value
    }


@router.post("/signin")
async def signin(
    payload: SigninSchema,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(User).where(User.mobile_number == payload.mobile_number)
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(            status_code=401,
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
        

    return {
        "message": "Credentials verified successfully"
    }
@router.post("/signin")
async def signin(
    payload: SigninSchema,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(User).where(User.mobile_number == payload.mobile_number)
    )

    user = result.scalars().first()

    print("INPUT EMAIL =", payload.mobile_number)
    print("INPUT PASSWORD =", payload.password)
    print("USER FOUND =", user)

    if user:
        print("DB EMAIL =", User.mobile_number)
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
#        )

    return{
        "message": "Credentials verified successfully",
        "role": user.role.value
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
