from datetime import datetime

from pydantic import BaseModel


# ============================================================
# 1. CREATE / GET CHAT SESSION
# ============================================================

class CreateChatRequest(BaseModel):
    other_user_id: int


class CreateChatResponse(BaseModel):
    chat_session_id: int
    other_user_id: int


# ============================================================
# 2. SEND MESSAGE
# ============================================================

class SendMessageRequest(BaseModel):
    chat_session_id: int
    message: str
    message_type: str


# ============================================================
# 3. GET CHAT HISTORY
# ============================================================

class ChatHistoryResponse(BaseModel):
    id: int
    chat_session_id: int
    sender_id: int
    is_mine: bool
    message: str | None = None

    message_type: str

    attachment_path: str | None = None
    attachment_name: str | None = None
    mime_type: str | None = None
    attachment_size: int | None = None

    created_at: datetime

    class Config:
        from_attributes = True
