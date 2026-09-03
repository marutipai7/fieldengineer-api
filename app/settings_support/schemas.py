from typing import Optional
from pydantic import BaseModel

class ContactSupportSchema(BaseModel):
    subject: str
    message: str

class PermissionUpdateSchema(BaseModel):
    location: Optional[bool] = None
    communication: Optional[bool] = None
    notifications: Optional[bool] = None
    camera: Optional[bool] = None
    media: Optional[bool] = None
    audio: Optional[bool] = None
    payment: Optional[bool] = None
    security: Optional[bool] = None
    network: Optional[bool] = None
    device: Optional[bool] = None

class ContactSupportSchema(BaseModel):
    subject: str
    message: str