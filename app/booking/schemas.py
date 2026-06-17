from pydantic import BaseModel


class BookingCreate(BaseModel):
    service_type: str
    description: str | None = None
    scheduled_date: str
    scheduled_time: str
    address: str


class BookingResponse(BaseModel):
    id: int
    booking_number: str
    service_type: str
    booking_status: str

    class Config:
        from_attributes = True