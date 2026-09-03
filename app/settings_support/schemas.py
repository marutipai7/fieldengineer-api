from pydantic import BaseModel
from typing import Optional


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