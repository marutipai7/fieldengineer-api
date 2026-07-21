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
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    FIELD_ENGINEER = "field_engineer"
    VENDOR = "vendor"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole),nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user_profile = relationship("UserProfile",back_populates="user",uselist=False,cascade="all, delete-orphan")
    # field_engineer_profile = relationship("FieldEngineerProfile",back_populates="user",uselist=False,cascade="all, delete-orphan")
    vendor_profile = relationship("VendorProfile",back_populates="user",uselist=False,cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.id", ondelete="CASCADE"),unique=True,nullable=False)
    full_name = Column(String(255))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    profile_image = Column(Text)
    referral_code = Column(String(20), unique=True)
    is_associated_with_vendor = Column(
       Boolean,
       default=False
    )

    vendor_id = Column(
       Integer,
       ForeignKey("vendors.id"),
       nullable=True
    )

    years_of_experience_id = Column(
       Integer,
       ForeignKey("years_of_experience.id"),
       nullable=True
    )

    primary_specialization_id = Column(
       Integer,
       ForeignKey("primary_specializations.id"),
       nullable=True
    )
    user = relationship("User",back_populates="user_profile")
    addresses = relationship("UserAddress",back_populates="profile",cascade="all, delete-orphan")
    vendor = relationship("Vendor")

    years_of_experience = relationship(
        "YearsOfExperience"
    )

    primary_specialization = relationship(
        "PrimarySpecialization"
    )
    documents = relationship(
       "FieldEngineerDocument",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan"
    )

    availability = relationship(
       "FieldEngineerAvailability",
       back_populates="profile",
       cascade="all, delete-orphan"
    )

    service_areas = relationship(
       "FieldEngineerServiceArea",
        back_populates="profile",
        cascade="all, delete-orphan"
    )



    customer_identity = relationship(
       "CustomerIdentity",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan"
    )

    customer_business = relationship(
       "CustomerBusiness",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan"
    )

    customer_documents = relationship(
       "CustomerDocument",
       back_populates="profile",
       uselist=False,
       cascade="all, delete-orphan"
    )
    # emergency_contacts = relationship("EmergencyContact",back_populates="profile",cascade="all, delete-orphan")

class UserAddress(Base):
    __tablename__ = "user_addresses"

    id = Column(Integer,primary_key=True,autoincrement=True)
    profile_id = Column(Integer,ForeignKey("user_profiles.id", ondelete="CASCADE"),nullable=False)
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


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_name = Column(String(255), nullable=False, unique=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class YearsOfExperience(Base):
    __tablename__ = "years_of_experience"

    id = Column(Integer, primary_key=True, autoincrement=True)
    experience = Column(String(100), nullable=False, unique=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class PrimarySpecialization(Base):
    __tablename__ = "primary_specializations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    specialization = Column(String(255), nullable=False, unique=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )



# class EmergencyContact(Base):
#     __tablename__ = "emergency_contacts"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     profile_id = Column(
#         Integer,
#         ForeignKey("user_profiles.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     contact_name = Column(String(255))
#     relationship_type = Column(String(100))
#     mobile_number = Column(String(20))

#     profile = relationship(
#         "UserProfile",
#         back_populates="emergency_contacts"
#     )


# class FieldEngineerProfile(Base):
#     __tablename__ = "field_engineer_profiles"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     user_id = Column(
#         Integer,
#         ForeignKey("users.id", ondelete="CASCADE"),
#         unique=True,
#         nullable=False
#     )

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

#     profile_completion = Column(Integer, default=0)

#     average_rating = Column(Numeric(3, 2), default=0.0)

#     total_jobs = Column(Integer, default=0)
#     completed_jobs = Column(Integer, default=0)
#     active_hours = Column(Integer, default=0)

#     is_available = Column(Boolean, default=True)

#     user = relationship(
#         "User",
#         back_populates="field_engineer_profile"
#     )

# class FieldEngineerSkill(Base):
#     __tablename__ = "field_engineer_skills"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     field_engineer_id = Column(
#         Integer,
#         ForeignKey("field_engineer_profiles.id", ondelete="CASCADE")
#     )

#     skill_name = Column(String(255), nullable=False)

# class FieldEngineerExperience(Base):
#     __tablename__ = "field_engineer_experiences"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     field_engineer_id = Column(
#         Integer,
#         ForeignKey("field_engineer_profiles.id", ondelete="CASCADE")
#     )

#     company_name = Column(String(255))
#     job_title = Column(String(255))
#     employment_type = Column(String(100))
#     location = Column(String(255))

#     start_date = Column(Date)
#     end_date = Column(Date)

#     currently_working = Column(Boolean, default=False)

#     responsibilities = Column(Text)
#     technologies_used = Column(Text)
#     achievements = Column(Text)

#     document_url = Column(Text)

# class FieldEngineerCertification(Base):
#     __tablename__ = "field_engineer_certifications"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     field_engineer_id = Column(
#         Integer,
#         ForeignKey("field_engineer_profiles.id", ondelete="CASCADE")
#     )

#     certification_name = Column(String(255))
#     issued_by = Column(String(255))

#     issue_date = Column(Date)
#     expiry_date = Column(Date)

#     document_url = Column(Text)

# class FieldEngineerEducation(Base):
#     __tablename__ = "field_engineer_education"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     field_engineer_id = Column(
#         Integer,
#         ForeignKey("field_engineer_profiles.id", ondelete="CASCADE")
#     )

#     degree_name = Column(String(255))
#     institute_name = Column(String(255))
#     specialization = Column(String(255))
#     grade_percentage = Column(String(50))

#     start_date = Column(Date)
#     end_date = Column(Date)

#     document_url = Column(Text)

# class FieldEngineerLicense(Base):
#     __tablename__ = "field_engineer_licenses"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     field_engineer_id = Column(
#         Integer,
#         ForeignKey("field_engineer_profiles.id", ondelete="CASCADE")
#     )

#     license_name = Column(String(255))
#     issued_by = Column(String(255))
#     license_number = Column(String(255))
#     status = Column(String(50))

#     issue_date = Column(Date)
#     expiry_date = Column(Date)

#     document_url = Column(Text)

# class FieldEngineerTool(Base):
#     __tablename__ = "field_engineer_tools"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     field_engineer_id = Column(
#         Integer,
#         ForeignKey("field_engineer_profiles.id", ondelete="CASCADE")
#     )

#     tool_name = Column(String(255))

# class FieldEngineerDocument(Base):
#     __tablename__ = "field_engineer_documents"

#     id = Column(Integer, primary_key=True, autoincrement=True)

    # field_engineer_id = Column(
    #     Integer,
    #     # ForeignKey("field_engineer_profiles.id", ondelete="CASCADE")
    #     ForeignKey("user_profiles.id", ondelete="CASCADE")
    # )

    # document_type = Column(String(100))
    # document_number = Column(String(255))
    # file_url = Column(Text)

    # verified = Column(Boolean, default=False)

class FieldEngineerDocument(Base):
    __tablename__ = "field_engineer_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    identity_proof = Column(Text, nullable=True)

    education_certificate = Column(Text, nullable=True)

    work_company_id = Column(Text, nullable=True)

    certification = Column(Text, nullable=True)

    experience_certificate = Column(Text, nullable=True)

    driving_license = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # profile = relationship("UserProfile")
    profile = relationship(
       "UserProfile",
       back_populates="documents"
    )


# class FieldEngineerBankAccount(Base):
#     __tablename__ = "field_engineer_bank_accounts"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     field_engineer_id = Column(
#         Integer,
#         ForeignKey("field_engineer_profiles.id", ondelete="CASCADE")
#     )

#     bank_name = Column(String(255))
#     account_holder_name = Column(String(255))
#     account_number = Column(String(255))
#     ifsc_code = Column(String(50))
#     account_type = Column(String(50))

#     is_primary = Column(Boolean, default=False)

class FieldEngineerAvailability(Base):
    __tablename__ = "field_engineer_availability"

    id = Column(Integer, primary_key=True, autoincrement=True)

    field_engineer_id = Column(
        Integer,
        # ForeignKey("field_engineer_profiles.id", ondelete="CASCADE")
        ForeignKey("user_profiles.id", ondelete="CASCADE")
    )

    day_of_week = Column(Integer)

    start_time = Column(Time)
    end_time = Column(Time)

    is_available = Column(Boolean, default=True)

    created_at = Column(
       DateTime(timezone=True),
       server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
 
    profile = relationship(
       "UserProfile",
       back_populates="availability"
    )


class FieldEngineerServiceArea(Base):
    __tablename__ = "field_engineer_service_areas"

    id = Column(Integer, primary_key=True, autoincrement=True)

    field_engineer_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    primary_city = Column(String(100), nullable=True)

    service_radius = Column(Integer, nullable=True)

    preferred_work_areas = Column(Text, nullable=True)

    latitude = Column(String(50), nullable=True)

    longitude = Column(String(50), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


    updated_at = Column(
       DateTime(timezone=True),
       server_default=func.now(),
       onupdate=func.now()
    )

    profile = relationship(
       "UserProfile",
        back_populates="service_areas"
    )


# class FieldEngineerAvailabilityException(Base):
#     __tablename__ = "field_engineer_availability_exceptions"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     field_engineer_id = Column(
#         Integer,
#         ForeignKey("field_engineer_profiles.id", ondelete="CASCADE")
#     )

#     date = Column(Date)

#     start_time = Column(Time)
#     end_time = Column(Time)

#     is_available = Column(Boolean, default=False)


# # ## Vendor Profile
class VendorProfile(Base):
    __tablename__ = "vendor_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    company_name = Column(String(255))
    owner_manager_name = Column(String(255))

    vendor_type = Column(String(100))
    legal_business_name = Column(String(255))
    business_type = Column(String(100))
    industry = Column(String(255))

    company_registration_number = Column(String(100))
    gst_number = Column(String(100))
    pan_number = Column(String(100))

    website = Column(Text)

    years_in_business = Column(Integer)

    company_registration_date = Column(Date)

    employee_count = Column(Integer)

    primary_service_category = Column(String(255))

    about_business = Column(Text)

    address = Column(Text)

    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))

    timezone = Column(String(100))
    working_hours = Column(String(100))

    profile_image = Column(Text)

    user = relationship(
        "User",
        back_populates="vendor_profile"
    )


class VendorDocument(Base):
    __tablename__ = "vendor_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)

    vendor_profile_id = Column(
        Integer,
        ForeignKey("vendor_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    gst_certificate = Column(Text, nullable=True)
    pan_card = Column(Text, nullable=True)
    registration_certificate = Column(Text, nullable=True)
    cancelled_cheque = Column(Text, nullable=True)
    other_document = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    vendor_profile = relationship("VendorProfile")



class VendorServiceCoverage(Base):
    __tablename__ = "vendor_service_coverages"

    id = Column(Integer, primary_key=True, autoincrement=True)

    vendor_profile_id = Column(
        Integer,
        ForeignKey("vendor_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    state = Column(String(100))
    city = Column(String(100))
    service_radius = Column(Integer)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    vendor_profile = relationship("VendorProfile")


class VendorWorkforce(Base):
    __tablename__ = "vendor_workforces"

    id = Column(Integer, primary_key=True, autoincrement=True)

    vendor_profile_id = Column(
        Integer,
        ForeignKey("vendor_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    total_engineers = Column(Integer, default=0)
    certified_engineers = Column(Integer, default=0)
    support_staff = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    vendor_profile = relationship("VendorProfile")


class VendorBankDetail(Base):
    __tablename__ = "vendor_bank_details"

    id = Column(Integer, primary_key=True, autoincrement=True)

    vendor_profile_id = Column(
        Integer,
        ForeignKey("vendor_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    account_holder_name = Column(String(255))
    bank_name = Column(String(255))
    account_number = Column(String(100))
    ifsc_code = Column(String(50))
    branch_name = Column(String(255))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    vendor_profile = relationship("VendorProfile")


class VendorNotificationPreference(Base):
    __tablename__ = "vendor_notification_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)

    vendor_profile_id = Column(
        Integer,
        ForeignKey("vendor_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    email_notification = Column(Boolean, default=True)
    sms_notification = Column(Boolean, default=False)
    push_notification = Column(Boolean, default=True)

    vendor_profile = relationship("VendorProfile")


class CustomerIdentity(Base):
    __tablename__ = "customer_identities"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    identity_type = Column(
        String(100),
        nullable=True
    )

    identity_number = Column(
        String(255),
        nullable=True
    )

    front_image = Column(
        Text,
        nullable=True
    )

    back_image = Column(
        Text,
        nullable=True
    )

    verified = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    profile = relationship(
       "UserProfile",
        back_populates="customer_identity"
    )


class CustomerBusiness(Base):
    __tablename__ = "customer_businesses"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    company_name = Column(
        String(255),
        nullable=True
    )

    business_type = Column(
        String(100),
        nullable=True
    )

    industry = Column(
        String(255),
        nullable=True
    )

    website = Column(
        Text,
        nullable=True
    )

    office_address = Column(
        Text,
        nullable=True
    )

    city = Column(
        String(100),
        nullable=True
    )

    state = Column(
        String(100),
        nullable=True
    )

    pincode = Column(
        String(20),
        nullable=True
    )

    latitude = Column(
        String(50),
        nullable=True
    )

    longitude = Column(
        String(50),
        nullable=True
    )

    gst_number = Column(
        String(100),
        nullable=True
    )

    tax_number = Column(
        String(100),
        nullable=True
    )

    authorized_person_name = Column(
        String(255),
        nullable=True
    )

    designation = Column(
        String(100),
        nullable=True
    )

    work_email = Column(
        String(255),
        nullable=True
    )

    work_phone = Column(
        String(20),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    profile = relationship(
       "UserProfile",
        back_populates="customer_business"
    )


class CustomerDocument(Base):
    __tablename__ = "customer_documents"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    gst_certificate = Column(
        Text,
        nullable=True
    )

    tax_identification_card = Column(
        Text,
        nullable=True
    )

    company_registration_certificate = Column(
        Text,
        nullable=True
    )

    moa_aoa = Column(
        Text,
        nullable=True
    )

    bank_account_proof = Column(
        Text,
        nullable=True
    )

    other_document = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    profile = relationship(
       "UserProfile",
        back_populates="customer_documents"
    )







# class VendorContactPerson(Base):
#     __tablename__ = "vendor_contact_persons"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     vendor_id = Column(
#         Integer,
#         ForeignKey("vendor_profiles.id", ondelete="CASCADE")
#     )

#     contact_type = Column(String(50))

#     full_name = Column(String(255))
#     designation = Column(String(255))

#     phone_number = Column(String(20))
#     email = Column(String(255))

# class VendorDocumentType(str, enum.Enum):
#     GST_CERTIFICATE = "gst_certificate"
#     COMPANY_PAN = "company_pan"
#     REGISTRATION_CERTIFICATE = "registration_certificate"
#     OTHER = "other"

# class VendorDocument(Base):
#     __tablename__ = "vendor_documents"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     vendor_id = Column(
#         Integer,
#         ForeignKey("vendor_profiles.id", ondelete="CASCADE")
#     )

#     document_type = Column(Enum(VendorDocumentType))

#     file_url = Column(Text)

#     verified = Column(Boolean, default=False)

# class VendorBankAccount(Base):
#     __tablename__ = "vendor_bank_accounts"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     vendor_id = Column(
#         Integer,
#         ForeignKey("vendor_profiles.id", ondelete="CASCADE")
#     )

#     bank_name = Column(String(255))
#     account_holder_name = Column(String(255))
#     account_number = Column(String(255))
#     ifsc_code = Column(String(50))

#     upi_id = Column(String(255))

#     payout_cycle = Column(String(50))

#     is_primary = Column(Boolean, default=False)

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