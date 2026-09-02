from typing import Optional
from pydantic import BaseModel

class ContactSupportSchema(BaseModel):
    subject: str
    message: str

class PermissionUpdateSchema(BaseModel):
    location: Optional[bool] = None
    camera: Optional[bool] = None
    microphone: Optional[bool] = None
    notifications: Optional[bool] = None

class ContactSupportSchema(BaseModel):
    subject: str
    message: str