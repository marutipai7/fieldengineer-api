from datetime import datetime
from typing import List, Optional

<<<<<<< HEAD
from pydantic import BaseModel


# Create Call
class CallCreate(BaseModel):
    call_type: str = "VIDEO"
    appointment_id: Optional[int] = None
    appointment_reference: Optional[str] = None
    notes: Optional[str] = None


# Add Participant
=======
from pydantic import BaseModel, ConfigDict


# Create one-to-one call
class CallCreate(BaseModel):
    receiver_id: int
    call_type: str = "VIDEO"
    notes: Optional[str] = None


# Add participant to an existing call
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
class CallParticipantCreate(BaseModel):
    user_id: int


<<<<<<< HEAD
# Create Group Call
class GroupCallCreate(BaseModel):
    call_type: str = "VIDEO"
    participant_ids: List[int]
    appointment_id: Optional[int] = None
    appointment_reference: Optional[str] = None
    notes: Optional[str] = None


# Update Call Status
=======
# Create group call
class GroupCallCreate(BaseModel):
    call_type: str = "VIDEO"
    participant_ids: List[int]
    notes: Optional[str] = None


# Update call status
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
class CallStatusUpdate(BaseModel):
    status: str


<<<<<<< HEAD
# Call Participant Response
=======
# Call participant response
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
class CallParticipantResponse(BaseModel):
    id: int
    call_id: int
    user_id: int
<<<<<<< HEAD
    peer_name: Optional[str] = None
    peer_avatar: Optional[str] = None
=======

    peer_name: Optional[str] = None
    peer_avatar: Optional[str] = None

>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
    presenter: bool
    audio_enabled: bool
    video_enabled: bool
    screen_enabled: bool
<<<<<<< HEAD
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
=======

    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Call response
class CallResponse(BaseModel):
    id: int
    room_id: str
    join_url: str
    caller_id: int
    receiver_id: Optional[int] = None

    call_type: str
    status: str

    notes: Optional[str] = None

    join_url: Optional[str] = None
    token: Optional[str] = None

    duration: Optional[int] = None

    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    participants: List[CallParticipantResponse] = []

<<<<<<< HEAD
    class Config:
        from_attributes = True
=======
    model_config = ConfigDict(from_attributes=True)
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
