from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.profile.models import User
from app.utils.auth_utils import get_current_user_mobile
from app.settings_support.schemas import ContactSupportSchema


router = APIRouter(
    prefix="/settings/Support_setting",
    tags=["Settings & Support"],
)


# ============================================================
# ABOUT US
# ============================================================

@router.get("/about-us")
async def get_about_us():
    return {
        "success": True,
        "message": "About Us fetched successfully",
        "data": {
            "title": "About Us",
            "sections": [
                {
                    "title": "1. Information We Collect",
                    "description": "We collect the following types of information:",
                    "points": [
                        "Personal Information: Name, email address, phone number, payment details, and shipping address.",
                        "Vendor Information: Business name, tax identification, and product details.",
                        "Usage Data: App usage patterns, device information, and IP address.",
                        "Communication Data: Messages or inquiries sent through the app."
                    ]
                },
                {
                    "title": "2. How We Use Your Information",
                    "description": "We use the collected information to:",
                    "points": [
                        "Process orders and facilitate transactions.",
                        "Enable vendor registrations and product listings.",
                        "Improve user experience and app functionality.",
                        "Communicate important updates or promotions.",
                        "Ensure compliance with legal and regulatory requirements."
                    ]
                },
                {
                    "title": "3. How We Share Your Information",
                    "description": "Your information may be shared with:",
                    "points": [
                        "Service Providers: Payment processors, delivery partners, and analytics providers.",
                        "Vendors: To process orders or address customer inquiries.",
                        "Legal Authorities: If required by law or to protect the platform's integrity."
                    ],
                    "footer": "We do not sell or rent your information to third parties."
                },
                {
                    "title": "4. Data Security",
                    "description": (
                        "We implement security measures to protect your information, "
                        "including encryption and secure servers. However, no method "
                        "of data transmission is completely secure, and we cannot "
                        "guarantee absolute security."
                    )
                }
            ]
        }
    }


# ============================================================
# CONTACT SUPPORT
# ============================================================

@router.post("/contact-support")
async def contact_support(
    payload: ContactSupportSchema,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.mobile_number == current_user_mobile)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "success": True,
        "message": "Support request submitted successfully",
        "data": {
            "subject": payload.subject,
            "message": payload.message
        }
    }


# ============================================================
# DELETE ACCOUNT
# ============================================================

@router.delete("/delete-account")
async def delete_account(
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.mobile_number == current_user_mobile)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "success": True,
        "message": "Account deleted successfully"
    }


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
async def logout(
    current_user_mobile: str = Depends(get_current_user_mobile)
):
    return {
        "success": True,
        "message": "Logout successful"
    }


# ============================================================
# TERMS AND CONDITIONS
# ============================================================

@router.get("/terms-and-conditions")
async def get_terms_and_conditions():
    return {
        "success": True,
        "message": "Terms and Conditions fetched successfully",
        "data": {
            "title": "Terms & Conditions",
            "sections": [
                {
                    "title": "1. Information We Collect",
                    "description": "We collect the following types of information:",
                    "points": [
                        "Personal Information: Name, email address, phone number, payment details, and shipping address.",
                        "Vendor Information: Business name, tax identification, and product details.",
                        "Usage Data: App usage patterns, device information, and IP address.",
                        "Communication Data: Messages or inquiries sent through the app."
                    ]
                },
                {
                    "title": "2. How We Use Your Information",
                    "description": "We use the collected information to:",
                    "points": [
                        "Process orders and facilitate transactions.",
                        "Enable vendor registrations and product listings.",
                        "Improve user experience and app functionality.",
                        "Communicate important updates or promotions.",
                        "Ensure compliance with legal and regulatory requirements."
                    ]
                },
                {
                    "title": "3. How We Share Your Information",
                    "description": "Your information may be shared with:",
                    "points": [
                        "Service Providers: Payment processors, delivery partners, and analytics providers.",
                        "Vendors: To process orders or address customer inquiries.",
                        "Legal Authorities: If required by law or to protect the platform's integrity."
                    ],
                    "footer": "We do not sell or rent your information to third parties."
                },
                {
                    "title": "4. Data Security",
                    "description": (
                        "We implement security measures to protect your information, "
                        "including encryption and secure servers. However, no method "
                        "of data transmission is completely secure, and we cannot "
                        "guarantee absolute security."
                    )
                }
            ]
        }
    }