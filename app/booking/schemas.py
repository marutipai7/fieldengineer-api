from pydantic import BaseModel
from app.booking.models import ServiceType


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