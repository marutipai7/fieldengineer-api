from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Create Call
class CallCreate(BaseModel):
    call_type: str = "VIDEO"
    appointment_id: Optional[int] = None
    appointment_reference: Optional[str] = None
    notes: Optional[str] = None


# Add Participant
class CallParticipantCreate(BaseModel):
    user_id: int


# Create Group Call
class GroupCallCreate(BaseModel):
    call_type: str = "VIDEO"
    participant_ids: List[int]
    appointment_id: Optional[int] = None
    appointment_reference: Optional[str] = None
    notes: Optional[str] = None


# Update Call Status
class CallStatusUpdate(BaseModel):
    status: str


# Call Participant Response
class CallParticipantResponse(BaseModel):
    id: int
    call_id: int
    user_id: int
    peer_name: Optional[str] = None
    peer_avatar: Optional[str] = None
    presenter: bool
    audio_enabled: bool
    video_enabled: bool
    screen_enabled: bool
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Call Response
class CallResponse(BaseModel):
    id: int
    room_id: str
    caller_id: int
    call_type: str
    status: str
    appointment_id: Optional[int] = None
    appointment_reference: Optional[str] = None
    notes: Optional[str] = None
    join_url: Optional[str] = None
    token: Optional[str] = None
    duration: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    participants: List[CallParticipantResponse] = []

    class Config:
        from_attributes = True