import uuid
import re, jwt
import random, string
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
# from app.core.config import AUTHORIZATION_KEY, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.config import settings
from fastapi import Header, Depends, status, HTTPException
# from app.profile.models import User, UserProfile, VendorProfile, FieldEngineerProfile, TokenBlacklist
from app.profile.models import User, UserProfile

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def generate_referral_code(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

async def generate_unique_referral_code(db):
    import random, string

    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        result = await db.execute(
            select(UserProfile).where(UserProfile.referral_code == code)
        )

        if not result.scalars().first():
            return code

def is_email(contact: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', contact))

def generate_random_string(length_min=8, length_max=10):
    length = random.randint(length_min, length_max)
    raw_password = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return pbkdf2_sha256.hash(raw_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    # expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # to_encode.update({"exp": expire})
    # return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    expire = datetime.now() + (
       expires_delta or timedelta(
          minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
      )
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
def check_authorization_key(authorization_key: str = Header(...)):
    # if authorization_key != AUTHORIZATION_KEY:
    if authorization_key != settings.AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Invalid authorization key")
    return authorization_key

async def get_current_user_email(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload = jwt.decode(
           token,
           settings.SECRET_KEY,
           algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return email

async def get_current_user_object(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
       )
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check blacklist
    blacklisted = await db.execute(
        select(TokenBlacklist).where(TokenBlacklist.token == token)
    )
    if blacklisted.scalars().first():
        raise HTTPException(status_code=401, detail="Token has been logged out")

    # Load user
    user = (await db.execute(select(User).where(User.email == email))).scalars().first()
    if not user:
        raise HTTPException(404, "User not found")

    if user.user_type in ['user']:
        profile_query = select(UserProfile).where(UserProfile.user_id == user.id)
    elif user.user_type == 'field_engineer':
        profile_query = select(FieldEngineerProfile).where(FieldEngineerProfile.user_id == user.id)
    elif user.user_type == 'vendor':
        profile_query = select(VendorProfile).where(VendorProfile.user_id == user.id)
    else:
        raise HTTPException(400, "Invalid user type")

    profile = (await db.execute(profile_query)).scalars().first()
    if not profile:
        raise HTTPException(404, "User profile not found")

    return user, profile