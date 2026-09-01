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
    chat_session_id: int
    sender_id: int

    message: str | None = None

    message_type: str

    attachment_path: str | None = None
    attachment_name: str | None = None
    mime_type: str | None = None
    attachment_size: int | None = None

    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionHistoryResponse(BaseModel):
    chat_session_id: int
    created_at: datetime
    messages: list[ChatHistoryResponse]

    class Config:
        from_attributes = True