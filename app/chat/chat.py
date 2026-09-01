from fastapi import APIRouter, Depends, HTTPException, UploadFile,File,Form
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
    ChatHistoryResponse,
    ChatSessionHistoryResponse
)
from pathlib import Path
import uuid

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
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user


    # Create chat session
    chat = ChatSession()

    db.add(chat)
    db.commit()
    db.refresh(chat)

    # Add current user as participant
    creator_participant = ChatParticipant(
        chat_session_id=chat.id,
        user_id=user.id
    )

    db.add(creator_participant)

    # Add requested participants
    for user_id in request.participant_ids:

        if user_id == user.id:
            continue

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
async def send_message(
    chat_session_id: int = Form(...),
    message: str | None = Form(None),
    file: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_object),
):
    user, profile = current_user
    # --------------------------------
    # 1. Validate message/file
    # --------------------------------

    if not message and not file:
        raise HTTPException(
            status_code=400,
            detail="Message or file is required"
        )

    # --------------------------------
    # 2. Check chat session
    # --------------------------------

    chat = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == chat_session_id
        )
        .first()
    )

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )

    # --------------------------------
    # 3. Check participant
    # --------------------------------

    participant = (
        db.query(ChatParticipant)
        .filter(
            ChatParticipant.chat_session_id == chat_session_id,
            ChatParticipant.user_id == user.id
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=403,
            detail="You are not a participant of this chat"
        )

    # --------------------------------
    # 4. Default values
    # --------------------------------

    message_type = "text"

    attachment_path = None
    attachment_name = None
    mime_type = None
    attachment_size = None

    saved_file_path = None

    # --------------------------------
    # 5. Handle attachment
    # --------------------------------

    if file:

        mime_type = file.content_type or ""

        # Determine message type
        if mime_type.startswith("image/"):
            message_type = "image"

        elif mime_type.startswith("video/"):
            message_type = "video"

        elif (
            mime_type == "application/pdf"
            or mime_type.startswith("application/")
        ):
            message_type = "document"

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type"
            )

        # --------------------------------
        # Upload directory
        # --------------------------------

        upload_dir = Path(
            f"uploads/chat/{chat_session_id}"
        )

        upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # --------------------------------
        # Generate unique filename
        # --------------------------------

        original_filename = file.filename or "attachment"

        extension = Path(
            original_filename
        ).suffix

        filename = (
            f"{uuid.uuid4().hex}{extension}"
        )

        saved_file_path = (
            upload_dir / filename
        )

        # --------------------------------
        # Save file
        # --------------------------------

        file_content = await file.read()

        with open(saved_file_path, "wb") as buffer:
            buffer.write(file_content)

        # --------------------------------
        # File information
        # --------------------------------

        attachment_path = str(
            saved_file_path
        )

        attachment_name = original_filename

        attachment_size = (
            saved_file_path.stat().st_size
        )

    # --------------------------------
    # 6. Save chat message
    # --------------------------------

    chat_message = ChatHistory(
        chat_session_id=chat_session_id,
        sender_id=user.id,

        message=message,

        message_type=message_type,

        attachment_path=attachment_path,
        attachment_name=attachment_name,
        mime_type=mime_type,
        attachment_size=attachment_size,
    )

    try:

        db.add(chat_message)

        db.commit()

        db.refresh(chat_message)

    except Exception as e:

        db.rollback()

        # Remove uploaded file if DB insert fails
        if saved_file_path and saved_file_path.exists():
            saved_file_path.unlink()

        raise HTTPException(
            status_code=500, detail="Failed to save chat message"
        ) from e

    return chat_message

@router.get(
    "/history",
    response_model=list[ChatSessionHistoryResponse]
)
def get_all_chat_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user

    # Get all chat sessions where current user is a participant
    sessions = (
        db.query(ChatSession)
        .join(
            ChatParticipant,
            ChatParticipant.chat_session_id == ChatSession.id
        )
        .filter(
            ChatParticipant.user_id == user.id
        )
        .order_by(ChatSession.created_at.desc())
        .all()
    )

    result = []

    for session in sessions:

        messages = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.chat_session_id == session.id
            )
            .order_by(ChatHistory.created_at)
            .all()
        )

        result.append(
            ChatSessionHistoryResponse(
                chat_session_id=session.id,
                created_at=session.created_at,
                messages=messages
            )
        )

    return result

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