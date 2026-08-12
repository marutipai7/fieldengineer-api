from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str

    notification_type: str

    entity_type: str | None = None
    entity_id: int | None = None

    type: str = "info"

    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: int
    title: str
    message: str

    notification_type: str

    entity_type: str | None = None
    entity_id: int | None = None

    type: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    is_read: bool
    created_at: datetime | None = None