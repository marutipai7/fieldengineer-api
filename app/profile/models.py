from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Date,
    Text,
    Integer,
    Numeric,
    Time
)
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

import uuid
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    FIELD_ENGINEER = "field_engineer"
    VENDOR = "vendor"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole),nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    user_profile = relationship("UserProfile",back_populates="user",uselist=False,cascade="all, delete-orphan")
    field_engineer_profile = relationship("FieldEngineerProfile",back_populates="user",uselist=False,cascade="all, delete-orphan")
    vendor_profile = relationship("VendorProfile",back_populates="user",uselist=False,cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.id", ondelete="CASCADE"),unique=True,nullable=False)
    full_name = Column(String(255))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    profile_image = Column(Text)
    referral_code = Column(String(20), unique=True)
    user = relationship("User",back_populates="user_profile")
    addresses = relationship("UserAddress",back_populates="profile",cascade="all, delete-orphan")
    emergency_contacts = relationship("EmergencyContact",back_populates="profile",cascade="all, delete-orphan")

class UserAddress(Base):
    __tablename__ = "user_addresses"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True),ForeignKey("user_profiles.id",ondelete="CASCADE"),nullable=False)
    address_type = Column(String(50))  # home, office, other
    name = Column(String(255))
    flat_no = Column(String(255))
    street = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    latitude = Column(String(50))
    longitude = Column(String(50))
    is_default = Column(Boolean, default=False)

    profile = relationship("UserProfile",back_populates="addresses")

# class EmergencyContact(Base):
#     __tablename__ = "emergency_contacts"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     profile_id = Column(UUID(as_uuid=True),ForeignKey("user_profiles.id",ondelete="CASCADE"),nullable=False)
#     contact_name = Column(String(255))
#     relationship_type = Column(String(100))
#     mobile_number = Column(String(20))

#     profile = relationship("UserProfile",back_populates="emergency_contacts")


# ## FieldEngineer Profile
# class FieldEngineerProfile(Base):
#     __tablename__ = "field_engineer_profiles"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True),ForeignKey("users.id", ondelete="CASCADE"),unique=True,nullable=False)
#     full_name = Column(String(255))
#     profile_image = Column(Text)
#     date_of_birth = Column(Date)
#     gender = Column(String(50))
#     marital_status = Column(String(50))
#     nationality = Column(String(100))
#     bio = Column(Text)
#     years_of_experience = Column(Integer)
#     current_address = Column(Text)
#     permanent_address = Column(Text)
#     profile_completion = Column(Integer,default=0)
#     average_rating = Column(Numeric(3, 2),default=0.0)
#     total_jobs = Column(Integer,default=0)
#     completed_jobs = Column(Integer,default=0)
#     active_hours = Column(Integer,default=0)
#     is_available = Column(Boolean,default=True)

#     user = relationship("User",back_populates="field_engineer_profile")

# class FieldEngineerSkill(Base):
#     __tablename__ = "field_engineer_skills"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     field_engineer_id = Column(UUID(as_uuid=True),ForeignKey("field_engineer_profiles.id",ondelete="CASCADE"))
#     skill_name = Column(String(255),nullable=False)

# class FieldEngineerExperience(Base):
#     __tablename__ = "field_engineer_experiences"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     field_engineer_id = Column(UUID(as_uuid=True),ForeignKey("field_engineer_profiles.id",ondelete="CASCADE"))
#     company_name = Column(String(255))
#     job_title = Column(String(255))
#     employment_type = Column(String(100))
#     location = Column(String(255))
#     start_date = Column(Date)
#     end_date = Column(Date)
#     currently_working = Column(Boolean,default=False)
#     responsibilities = Column(Text)
#     technologies_used = Column(Text)
#     achievements = Column(Text)
#     document_url = Column(Text)

# class FieldEngineerCertification(Base):
#     __tablename__ = "field_engineer_certifications"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     field_engineer_id = Column(UUID(as_uuid=True),ForeignKey("field_engineer_profiles.id",ondelete="CASCADE"))
#     certification_name = Column(String(255))
#     issued_by = Column(String(255))
#     issue_date = Column(Date)
#     expiry_date = Column(Date)
#     document_url = Column(Text)

# class FieldEngineerEducation(Base):
#     __tablename__ = "field_engineer_education"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     field_engineer_id = Column(UUID(as_uuid=True),ForeignKey("field_engineer_profiles.id",ondelete="CASCADE"))
#     degree_name = Column(String(255))
#     institute_name = Column(String(255))
#     specialization = Column(String(255))
#     grade_percentage = Column(String(50))
#     start_date = Column(Date)
#     end_date = Column(Date)
#     document_url = Column(Text)

# class FieldEngineerLicense(Base):
#     __tablename__ = "field_engineer_licenses"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     field_engineer_id = Column(UUID(as_uuid=True),ForeignKey("field_engineer_profiles.id",ondelete="CASCADE"))
#     license_name = Column(String(255))
#     issued_by = Column(String(255))
#     license_number = Column(String(255))
#     status = Column(String(50))
#     issue_date = Column(Date)
#     expiry_date = Column(Date)
#     document_url = Column(Text)

# class FieldEngineerTool(Base):
#     __tablename__ = "field_engineer_tools"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     field_engineer_id = Column(UUID(as_uuid=True),ForeignKey("field_engineer_profiles.id",ondelete="CASCADE"))
#     tool_name = Column(String(255))

# class FieldEngineerDocument(Base):
#     __tablename__ = "field_engineer_documents"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     field_engineer_id = Column(UUID(as_uuid=True),ForeignKey("field_engineer_profiles.id",ondelete="CASCADE"))
#     document_type = Column(String(100))
#     document_number = Column(String(255))
#     file_url = Column(Text)
#     verified = Column(Boolean,default=False)

# class FieldEngineerBankAccount(Base):
#     __tablename__ = "field_engineer_bank_accounts"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     field_engineer_id = Column(UUID(as_uuid=True),ForeignKey("field_engineer_profiles.id",ondelete="CASCADE"))
#     bank_name = Column(String(255))
#     account_holder_name = Column(String(255))
#     account_number = Column(String(255))
#     ifsc_code = Column(String(50))
#     account_type = Column(String(50))
#     is_primary = Column(Boolean,default=False)

# class FieldEngineerAvailability(Base):
#     __tablename__ = "field_engineer_availability"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     field_engineer_id = Column(UUID(as_uuid=True),ForeignKey("field_engineer_profiles.id",ondelete="CASCADE"))
#     day_of_week = Column(Integer)  # 0-6
#     start_time = Column(Time)
#     end_time = Column(Time)
#     is_available = Column(Boolean,default=True)

# class FieldEngineerAvailabilityException(Base):
#     __tablename__ = "field_engineer_availability_exceptions"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     field_engineer_id = Column(UUID(as_uuid=True),ForeignKey("field_engineer_profiles.id",ondelete="CASCADE"))
#     date = Column(Date)
#     start_time = Column(Time)
#     end_time = Column(Time)
#     is_available = Column(Boolean,default=False)


# ## Vendor Profile
# class VendorProfile(Base):
#     __tablename__ = "vendor_profiles"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),unique=True,nullable=False)
#     company_name = Column(String(255))
#     legal_business_name = Column(String(255))
#     business_type = Column(String(100))
#     industry = Column(String(255))
#     company_registration_number = Column(String(100))
#     gst_number = Column(String(100))
#     pan_number = Column(String(100))
#     website = Column(Text)
#     years_in_business = Column(Integer)
#     company_registration_date = Column(Date)
#     employee_count = Column(Integer)
#     primary_service_category = Column(String(255))
#     about_business = Column(Text)
#     address = Column(Text)
#     city = Column(String(100))
#     state = Column(String(100))
#     pincode = Column(String(20))
#     timezone = Column(String(100))
#     working_hours = Column(String(100))
#     profile_image = Column(Text)
#     user = relationship(
#         "User",
#         back_populates="vendor_profile"
#     )

# class VendorContactPerson(Base):
#     __tablename__ = "vendor_contact_persons"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     vendor_id = Column(UUID(as_uuid=True),ForeignKey("vendor_profiles.id",ondelete="CASCADE"))
#     contact_type = Column(String(50))  # primary, billing, support
#     full_name = Column(String(255))
#     designation = Column(String(255))
#     phone_number = Column(String(20))
#     email = Column(String(255))

# import enum

# class VendorDocumentType(str, enum.Enum):
#     GST_CERTIFICATE = "gst_certificate"
#     COMPANY_PAN = "company_pan"
#     REGISTRATION_CERTIFICATE = "registration_certificate"
#     OTHER = "other"

# class VendorDocument(Base):
#     __tablename__ = "vendor_documents"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     vendor_id = Column(UUID(as_uuid=True),ForeignKey("vendor_profiles.id",ondelete="CASCADE"))
#     document_type = Column(Enum(VendorDocumentType))
#     file_url = Column(Text)
#     verified = Column(Boolean,default=False)

# class VendorBankAccount(Base):
#     __tablename__ = "vendor_bank_accounts"

#     id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     vendor_id = Column(UUID(as_uuid=True),ForeignKey("vendor_profiles.id",ondelete="CASCADE"))
#     bank_name = Column(String(255))
#     account_holder_name = Column(String(255))
#     account_number = Column(String(255))
#     ifsc_code = Column(String(50))
#     upi_id = Column(String(255))
#     payout_cycle = Column(String(50))  # weekly/monthly
#     is_primary = Column(Boolean,default=False)

# class TokenBlacklist(Base):
#     __tablename__ = "token_blacklist"

#     id = Column(Integer, primary_key=True, index=True)
#     token = Column(String, nullable=False)
#     user_id = Column(Integer, nullable=False)
#     expires_at = Column(DateTime, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

# class OtpSession(Base):
#     __tablename__ = "otp_sessions"

#     id = Column(Integer, primary_key=True, index=True)
#     otp_token = Column(String(128), unique=True, index=True, nullable=False)
#     otp_secret = Column(String(128), nullable=False)
#     contact = Column(String(128), nullable=False)
#     purpose = Column(String(32), nullable=False)  # "register" or "login"
#     referral_code = Column(String(64), nullable=True)
#     is_verified = Column(Boolean, default=False)
#     is_consumed = Column(Boolean, default=False)  # Marks OTP as used/consumed
#     expires_at = Column(DateTime, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)