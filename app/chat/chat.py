from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.utils.auth_utils import get_current_user_object
from app.core.database import get_db

from app.chat.models import (
    ChatSession,
    ChatParticipant,
    ChatHistory
)

from app.chat.schemas import (
    CreateChatRequest,
    CreateChatResponse,
    SendMessageRequest,
    ChatHistoryResponse
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# Create Chat Session
@router.post(
    "/session",
    response_model=CreateChatResponse
)
def create_chat(
    request: CreateChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_object)
):
    user, profile = current_user

    chat = ChatSession()

    db.add(chat)
    db.commit()
    db.refresh(chat)


    for user_id in request.participant_ids:
        participant = ChatParticipant(
            chat_session_id=chat.id,
            user_id=user_id
        )

        db.add(participant)


    db.commit()


    return {
        "chat_session_id": chat.id
    }



# Send Message
@router.post("/history")
def send_message(
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_object)
):

    user, profile = current_user

    message = ChatHistory(
        chat_session_id=request.chat_session_id,
        sender_id=user.id,
        message=request.message,
        message_type=request.message_type
    )


    db.add(message)
    db.commit()
    db.refresh(message)


    return message



# Get Chat History
@router.get(
    "/history/{chat_session_id}",
    response_model=list[ChatHistoryResponse]
)
def get_chat_history(
    chat_session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_object)
):
    user, profile = current_user

    messages = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.chat_session_id == chat_session_id
        )
        .order_by(ChatHistory.created_at)
        .all()
    )


    return messages