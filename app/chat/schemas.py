from pydantic import BaseModel
from datetime import datetime


class CreateChatRequest(BaseModel):
    participant_ids: list[int]


class CreateChatResponse(BaseModel):
    chat_session_id: int


class SendMessageRequest(BaseModel):
    chat_session_id: int
    message: str
    message_type: str   # text/image/file


class ChatHistoryResponse(BaseModel):
    id: int
    sender_id: int
    message: str
    message_type: str
    created_at: datetime

    class Config:
        from_attributes = True