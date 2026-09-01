# import uuid
import re
import jwt
import random
import string

from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordBearer
from fastapi import Header, Depends, status, HTTPException

from app.core.database import get_db
from app.core.config import settings
from app.profile.models import User, UserProfile, VendorProfile


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def generate_referral_code(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))


async def generate_unique_referral_code(db: Session):
    while True:
        code = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=8
            )
        )

        result = db.execute(
            select(UserProfile).where(
                UserProfile.referral_code == code
            )
        )

        if not result.scalars().first():
            return code


def is_email(contact: str) -> bool:
    return bool(
        re.match(
            r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            contact
        )
    )


def generate_random_string(length_min=8, length_max=10):
    length = random.randint(length_min, length_max)

    raw_password = ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )

    return pbkdf2_sha256.hash(raw_password)


def create_access_token(
    data: dict,
    expires_delta: timedelta = None
):
    to_encode = data.copy()

    expire = datetime.now() + (
        expires_delta
        or timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def check_authorization_key(
    authorization_key: str = Header(...)
):
    if authorization_key != settings.AUTHORIZATION_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization key"
        )

    return authorization_key


async def get_current_user_mobile(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        mobile_number: str = payload.get("sub")

        if not mobile_number:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return mobile_number


async def get_current_user_object(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Decode JWT
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Get mobile number from JWT
        mobile_number = payload.get("sub")

        if not mobile_number:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # --------------------------------
    # Load User using mobile number
    # --------------------------------

    result =  db.execute(
        select(User).where(
            User.mobile_number == mobile_number
        )
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------
    # Load Profile
    # --------------------------------

    if user.role in ["user", "field_engineer"]:

        profile_query = select(UserProfile).where(
            UserProfile.user_id == user.id
        )

    elif user.role == "vendor":

        profile_query = select(VendorProfile).where(
            VendorProfile.user_id == user.id
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid user type"
        )

    profile_result = db.execute(profile_query)

    profile = profile_result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User profile not found"
        )

    return user, profile