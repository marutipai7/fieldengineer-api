import pyotp
import binascii
import random
from datetime import datetime, timedelta

def generate_otp_secret():
    """Generate a random 6-digit OTP code"""
    return str(random.randint(100000, 999999))

def generate_otp(secret: str) -> str:
    """For email/SMS OTPs, the secret itself IS the OTP code"""
    return secret

def verify_otp(secret: str, otp: str) -> bool:
    """Simple string comparison for email/SMS OTPs"""
    try:
        if not secret or not otp:
            return False
        # Direct comparison for email/SMS OTPs
        return str(secret).strip() == str(otp).strip()
    except Exception as e:
        print(f"Error verifying OTP: {e}")
        return False

# In-memory store — replace with Redis or DB table in production
otp_store = {}

def send_otp_to_user(email_or_phone: str):
    otp = str(random.randint(100000, 999999))
    otp_store[email_or_phone] = {"otp": otp, "expires_at": datetime.utcnow() + timedelta(minutes=5)}
    print(f"[OTP DEBUG] OTP for {email_or_phone} → {otp}")
    # TODO: Integrate with Twilio / Email service

def verify_otp_for_user(email_or_phone: str, otp: str = None):
    data = otp_store.get(email_or_phone)
    if not data:
        return False
    if datetime.utcnow() > data["expires_at"]:
        del otp_store[email_or_phone]
        return False
    if otp is None:
        # OTP pre-verification placeholder
        return True
    if data["otp"] == otp:
        del otp_store[email_or_phone]
        return True
    return False
