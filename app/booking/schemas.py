from pydantic import BaseModel
from app.booking.models import ServiceType
from datetime import datetime
from decimal import Decimal
from typing import Optional

# class BookingCreate(BaseModel):
#     service_type: ServiceType
#     description: str | None = None
#     scheduled_date: str
#     scheduled_time: str
#     address: str


class BookingResponse(BaseModel):
    id: int
    # booking_number: str
    service_type: str
    booking_status: str

    class Config:
        from_attributes = True


class AcceptedEngineerSummary(BaseModel):
    id: int
    user_id: int
    full_name: str | None = None
    mobile_number: str | None = None
    profile_image: str | None = None
    work_preference: str | None = None

    class Config:
        from_attributes = True


class OfferDetailsResponse(BaseModel):
    booking_id: int
    booking_number: str | None = None
    service_name: str | None = None
    sub_service_name: str | None = None
    budget_min: float | None = None
    budget_max: float | None = None
    offer_price: float | None = None
    status: str | None = None
    has_offer: bool = False
    accepted_field_engineer: AcceptedEngineerSummary | None = None

    class Config:
        from_attributes = True


class ServiceResponse(BaseModel):
    id: int
    service_name: str

    class Config:
        from_attributes = True


class SubServiceResponse(BaseModel):
    id: int
    service_id: int
    sub_service_name: str

    class Config:
        from_attributes = True


class ServiceDetailResponse(BaseModel):
    id: int
    service_name: str
    image_url: str | None = None
    about_service: str | None = None
    whats_included: list[str] = []
    min_duration_hours: int = 2
    total_engineers_available: int = 0
    budget_min: float | None = None
    budget_max: float | None = None
    sub_services: list[SubServiceResponse] = []

    class Config:
        from_attributes = True


class SiteTypeResponse(BaseModel):
    id: int
    site_type_name: str

    class Config:
        from_attributes = True


class ProjectTypeResponse(BaseModel):
    id: int
    project_type_name: str

    class Config:
        from_attributes = True

class SiteDetailCreate(BaseModel):
    site_name: str
    company_name: str
    site_type_id: int
    project_type_id: int
    floor_number: str | None = None
    building_wing: str | None = None
    landmark: str | None = None

class BookingAddressCreate(BaseModel):
    country: str
    state: str
    pin_code: str
    area_locality: str
    city: str
    address_line_1: str
    address_line_2: str | None = None
    latitude: float | None = None
    longitude: float | None = None

class SiteContactPersonCreate(BaseModel):
    contact_person_name: str
    mobile_number: str
    alternate_number: str | None = None
    email: str
    department: str | None = None

class AccessInformationCreate(BaseModel):
    entry_instructions: str | None = None
    security_gate_details: str | None = None
    parking_availability: str | None = None
    access_timing: str | None = None
    visitor_pass_required: int = 0
    night_shift_access: int = 0
    weekend_access: int = 0
    id_verification_required: int = 0

 
 
class BookingScheduleCreate(BaseModel):
    scheduled_date: str
    scheduled_time: str
    estimated_duration_hours: int | None = None
    notes: str | None = None

class BookingDocumentCreate(BaseModel):
    file_name: str
    file_url: str
    file_size: str

class BookingCreate(BaseModel):
    budget_min: float
    budget_max: float

    service_id: int
    sub_service_id: int

    requirement_description: str | None = None

    site_details: SiteDetailCreate

    address: BookingAddressCreate

    contact_person: SiteContactPersonCreate

    access_information: AccessInformationCreate

    schedule: BookingScheduleCreate

    documents: list[BookingDocumentCreate] = []


class SiteDetailResponse(BaseModel):
    site_name: str | None = None
    company_name: str | None = None
    site_type_id: int | None = None
    project_type_id: int | None = None
    floor_number: str | None = None
    building_wing: str | None = None
    landmark: str | None = None

    class Config:
        from_attributes = True


class BookingAddressResponse(BaseModel):
    country: str | None = None
    state: str | None = None
    pin_code: str | None = None
    area_locality: str | None = None
    city: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    class Config:
        from_attributes = True


class SiteContactPersonResponse(BaseModel):
    contact_person_name: str | None = None
    mobile_number: str | None = None
    alternate_number: str | None = None
    email: str | None = None
    department: str | None = None

    class Config:
        from_attributes = True


class AccessInformationResponse(BaseModel):
    entry_instructions: str | None = None
    security_gate_details: str | None = None
    parking_availability: str | None = None
    access_timing: str | None = None
    visitor_pass_required: int | None = None
    night_shift_access: int | None = None
    weekend_access: int | None = None
    id_verification_required: int | None = None

    class Config:
        from_attributes = True


class BookingScheduleResponse(BaseModel):
    scheduled_date: str | None = None
    scheduled_time: str | None = None
    estimated_duration_hours: int | None = None
    notes: str | None = None

    class Config:
        from_attributes = True


class BookingDocumentResponse(BaseModel):
    file_name: str | None = None
    file_url: str | None = None
    file_size: str | None = None

    class Config:
        from_attributes = True


class LeadResponse(BaseModel):
    id: int
    user_id: int
    booking_number: str | None = None

    service_type: str | None = None
    description: str | None = None

    budget_min: float | None = None
    budget_max: float | None = None

    service_id: int | None = None
    sub_service_id: int | None = None

    requirement_description: str | None = None

    bid_status: str | None = None
    booking_status: str | None = None

    created_at: datetime
    updated_at: datetime
    match_score: int = 0
    can_accept: bool = False

    site_detail: SiteDetailResponse | None = None
    address: BookingAddressResponse | None = None
    contact_person: SiteContactPersonResponse | None = None
    access_information: AccessInformationResponse | None = None
    schedule: BookingScheduleResponse | None = None
    documents: list[BookingDocumentResponse] = []

    class Config:
        from_attributes = True

class FieldEngineerServiceCreate(BaseModel):
    service_id: int
    sub_service_id: int
    price: Decimal

class FieldEngineerServiceResponse(BaseModel):
    id: int
    service_id: int
    service_name: str

    sub_service_id: int
    sub_service_name: str

    price: Decimal

    class Config:
        from_attributes = True

class LeadListResponse(BaseModel):
    booking_number: str | None = None
    status: str | None = None
    can_accept: bool = False

class ServiceDetailCreateSchema(BaseModel):
    service_id: int
    image_url: Optional[str] = None
    engineers_available: int
    price_per_hour: float
    min_duration_hours: int = 2
    service_tags: Optional[str] = None
    about_service: Optional[str] = None
    whats_included: Optional[str] = None