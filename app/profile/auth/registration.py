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

    # --------------------------------------------------------
    # Validate action
    # --------------------------------------------------------

    if payload.action not in ["signup", "signin"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be signup or signin"
        )

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    result = db.execute(
        select(User).where(
            User.mobile_number == payload.mobile_number
        )
    )

    user = result.scalars().first()

    # ========================================================
    # SIGNUP
    # ========================================================

    if payload.action == "signup":

        # Mobile already registered
        if user:
            raise HTTPException(
                status_code=400,
                detail="Mobile number already registered"
            )

    # ========================================================
    # SIGNIN
    # ========================================================

    elif payload.action == "signin":

        # User must exist
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Check role
        if user.role != payload.role:
            raise HTTPException(
                status_code=400,
                detail="Invalid role"
            )

    # --------------------------------------------------------
    # Generate and send OTP
    # --------------------------------------------------------

    send_otp_to_user(payload.mobile_number)

    # Store role and action along with OTP
    otp_store[payload.mobile_number]["role"] = payload.role
    otp_store[payload.mobile_number]["action"] = payload.action

    otp = otp_store[payload.mobile_number]["otp"]

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": "OTP sent successfully",
        "mobile_number": payload.mobile_number,
        "action": payload.action,
        "role": payload.role.value,
        "OTP": otp   # Remove this in production
    }




@router.post("/verify-otp")
async def verify_otp(
    payload: VerifyOTPSchema,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Validate action
    # --------------------------------------------------------

    if payload.action not in ["signup", "signin"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be signup or signin"
        )

    # --------------------------------------------------------
    # Get OTP data
    # --------------------------------------------------------

    stored_data = otp_store.get(payload.mobile_number)

    if not stored_data:
        raise HTTPException(
            status_code=400,
            detail="OTP expired or not requested"
        )

    # --------------------------------------------------------
    # Check action
    # --------------------------------------------------------

    if stored_data.get("action") != payload.action:
        raise HTTPException(
            status_code=400,
            detail="OTP action does not match"
        )

    # --------------------------------------------------------
    # Verify OTP
    # --------------------------------------------------------

    is_valid = verify_otp_for_user(
        payload.mobile_number,
        payload.otp
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    # --------------------------------------------------------
    # Get role stored during request OTP
    # --------------------------------------------------------

    role = stored_data.get("role")

    if not role:
        raise HTTPException(
            status_code=400,
            detail="OTP role information missing"
        )

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    result = db.execute(
        select(User).where(
            User.mobile_number == payload.mobile_number
        )
    )

    user = result.scalars().first()

    # ========================================================
    # SIGNUP
    # ========================================================

    if payload.action == "signup":

        # User should not already exist
        if user:
            raise HTTPException(
                status_code=400,
                detail="Mobile number already registered"
            )

        # ----------------------------------------------------
        # Create User
        # ----------------------------------------------------

        user = User(
            mobile_number=payload.mobile_number,
            password_hash="OTP_LOGIN",
            role=role,
            is_verified=True,
            is_active=True
        )

        db.add(user)
        db.flush()

        # ----------------------------------------------------
        # Create User Profile
        # ----------------------------------------------------

        if role in [
            UserRole.USER,
            UserRole.FIELD_ENGINEER
        ]:

            user_profile = UserProfile(
                user_id=user.id
            )

            db.add(user_profile)

        # ----------------------------------------------------
        # Create Vendor Profile
        # ----------------------------------------------------

        elif role == UserRole.VENDOR:

            vendor_profile = VendorProfile(
                user_id=user.id
            )

            db.add(vendor_profile)

        # ----------------------------------------------------
        # Commit User
        # ----------------------------------------------------

        db.commit()
        db.refresh(user)

        # ----------------------------------------------------
        # Remove OTP
        # ----------------------------------------------------

        otp_store.pop(payload.mobile_number, None)

        # ----------------------------------------------------
        # Create JWT for SIGNUP
        # ----------------------------------------------------

        token = create_access_token(
            {
                "sub": user.mobile_number
            }
        )

        # ----------------------------------------------------
        # Return signup response with token
        # ----------------------------------------------------

        return {
            "message": "Signup successful",
            "user_id": user.id,
            "mobile_number": user.mobile_number,
            "role": user.role.value,
            "access_token": token,
            "token_type": "bearer"
        }

    # ========================================================
    # SIGNIN
    # ========================================================

    elif payload.action == "signin":

        # User must exist
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # ----------------------------------------------------
        # Check role
        # ----------------------------------------------------

        if user.role != role:
            raise HTTPException(
                status_code=400,
                detail="Invalid role"
            )

        # ----------------------------------------------------
        # Mark verified
        # ----------------------------------------------------

        user.is_verified = True

        db.commit()
        db.refresh(user)

        # ----------------------------------------------------
        # Remove OTP
        # ----------------------------------------------------

        otp_store.pop(payload.mobile_number, None)

        # ----------------------------------------------------
        # Create JWT for SIGNIN
        # ----------------------------------------------------

        token = create_access_token(
            {
                "sub": user.mobile_number
            }
        )

        # ----------------------------------------------------
        # Return signin response with token
        # ----------------------------------------------------

        return {
            "message": "Signin successful",
            "user_id": user.id,
            "mobile_number": user.mobile_number,
            "role": user.role.value,
            "access_token": token,
            "token_type": "bearer"
        }



# @router.post("/signup")
# async def signup(
#     payload: SignupSchema,
#     db: Session = Depends(get_db)
# ):
#     #Check if email already exists
#     result = db.execute(
#         select(User).where(User.mobile_number == payload.mobile_number)
#     )

#     if existing_user := result.scalars().first():
#         raise HTTPException(
#             status_code=400,
#             detail="Mobile number already registered"
#         )

#     # # Create User
#     user = User(
#         mobile_number=payload.mobile_number,
#         password_hash=pbkdf2_sha256.hash(payload.password),
#         role=payload.role,
#         is_verified=False
#     )

#     db.add(user)
#     db.commit()
#     db.refresh(user)

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


# @router.post("/signin")
# async def signin(
#     payload: SigninSchema,
#     db: Session = Depends(get_db)
# ):
#     result = db.execute(
#         select(User).where(User.mobile_number == payload.mobile_number)
#     )

#     user = result.scalars().first()

#     if not user:
#         raise HTTPException(            status_code=401,
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
# @router.post("/signin")
# async def signin(
#     payload: SigninSchema,
#     db: Session = Depends(get_db)
# ):
#     result = db.execute(
#         select(User).where(User.mobile_number == payload.mobile_number)
#     )

#     user = result.scalars().first()

#     print("INPUT EMAIL =", payload.mobile_number)
#     print("INPUT PASSWORD =", payload.password)
#     print("USER FOUND =", user)

#     if user:
#         print("DB EMAIL =", User.mobile_number)
#         print("DB HASH =", user.password_hash)
#         print(
#             "PASSWORD MATCH =",
#         pbkdf2_sha256.verify(
#                 payload.password,
#                 user.password_hash
#             )
#         )

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
# #        )

#     return{
#         "message": "Credentials verified successfully",
#         "role": user.role.value
#     }




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
