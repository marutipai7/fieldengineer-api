from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from pathlib import Path
import uuid

from app.utils.auth_utils import get_current_user_object
from app.core.database import get_db

from app.chat.models import (
    ChatSession,
    ChatParticipant,
    ChatHistory,
)

from app.chat.schemas import (
    CreateChatRequest,
    CreateChatResponse,
    ChatHistoryResponse,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# ============================================================
# 1. CREATE / GET CHAT SESSION
# ============================================================

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

    current_user_id = user.id
    other_user_id = request.other_user_id
    print("================================")
    print("CURRENT USER ID:", current_user_id)
    print("OTHER USER ID:", other_user_id)
    print("CURRENT USER:", user)
    print("================================")
    # --------------------------------------------------------
    # Cannot chat with yourself
    # --------------------------------------------------------

    if current_user_id == other_user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot create a chat with yourself"
        )

    # --------------------------------------------------------
    # Check whether other user exists
    # --------------------------------------------------------

    from app.profile.models import User

    other_user = (
        db.query(User)
        .filter(User.id == other_user_id)
        .first()
    )

    if not other_user:
        raise HTTPException(
            status_code=404,
            detail="Other user not found"
        )

    # --------------------------------------------------------
    # Find existing session between these TWO users
    # --------------------------------------------------------

    existing_session = (
        db.query(ChatSession)
        .join(
            ChatParticipant,
            ChatParticipant.chat_session_id == ChatSession.id
        )
        .filter(
            ChatParticipant.user_id.in_([
                current_user_id,
                other_user_id
            ])
        )
        .group_by(ChatSession.id)
        .having(
            func.count(
                distinct(ChatParticipant.user_id)
            ) == 2
        )
        .first()
    )

    # --------------------------------------------------------
    # Existing conversation found
    # --------------------------------------------------------

    if existing_session:

        return {
            "chat_session_id": existing_session.id,
            "other_user_id": other_user_id
        }

    # --------------------------------------------------------
    # No existing conversation
    # Create a NEW session
    # --------------------------------------------------------

    chat = ChatSession()

    db.add(chat)
    db.flush()

    # Current user
    creator_participant = ChatParticipant(
        chat_session_id=chat.id,
        user_id=current_user_id
    )

    # Other user
    other_participant = ChatParticipant(
        chat_session_id=chat.id,
        user_id=other_user_id
    )

    db.add(creator_participant)
    db.add(other_participant)

    db.commit()
    db.refresh(chat)

    return {
        "chat_session_id": chat.id,
        "other_user_id": other_user_id
    }


# ============================================================
# 2. SEND MESSAGE
# ============================================================

@router.post(
    "/send",
    response_model=ChatHistoryResponse
)
async def send_message(
    chat_session_id: int = Form(...),
    message: str | None = Form(None),
    file: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_object),
):
    user, profile = current_user

    # --------------------------------------------------------
    # Validate message/file
    # --------------------------------------------------------

    if not message and not file:
        raise HTTPException(
            status_code=400,
            detail="Message or file is required"
        )

    # --------------------------------------------------------
    # Check chat session
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Check whether current user belongs to this session
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Default values
    # --------------------------------------------------------

    message_type = "text"

    attachment_path = None
    attachment_name = None
    mime_type = None
    attachment_size = None

    saved_file_path = None

    # --------------------------------------------------------
    # Handle attachment
    # --------------------------------------------------------

    if file:

        mime_type = file.content_type or ""

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

        # ----------------------------------------------------
        # Upload directory
        # ----------------------------------------------------

        upload_dir = Path(
            f"uploads/chat/{chat_session_id}"
        )

        upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------------------
        # Generate unique filename
        # ----------------------------------------------------

        original_filename = (
            file.filename or "attachment"
        )

        extension = Path(
            original_filename
        ).suffix

        filename = (
            f"{uuid.uuid4().hex}{extension}"
        )

        saved_file_path = (
            upload_dir / filename
        )

        # ----------------------------------------------------
        # Save file
        # ----------------------------------------------------

        file_content = await file.read()

        with open(
            saved_file_path,
            "wb"
        ) as buffer:
            buffer.write(file_content)

        # ----------------------------------------------------
        # File information
        # ----------------------------------------------------

        attachment_path = str(
            saved_file_path
        )

        attachment_name = (
            original_filename
        )

        attachment_size = (
            saved_file_path.stat().st_size
        )

    # --------------------------------------------------------
    # Save message
    # --------------------------------------------------------

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

        # Update session timestamp
        chat.updated_at = datetime.utcnow()

        db.commit()

        db.refresh(chat_message)

    except Exception as e:

        db.rollback()

        if saved_file_path and saved_file_path.exists():
            saved_file_path.unlink()

        print("CHAT MESSAGE SAVE ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
    )from e

    return chat_message


# ============================================================
# 4. GET SINGLE CHAT HISTORY
# ============================================================

@router.get(
    "/history/{user_id}",
    response_model=list[ChatHistoryResponse]
)
def get_chat_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user

    current_user_id = user.id
    other_user_id = user_id

    # Cannot chat with yourself
    if current_user_id == other_user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot get chat history with yourself"
        )

    # --------------------------------------------------------
    # Find the session between current user and other user
    # --------------------------------------------------------

    chat_session = (
        db.query(ChatSession)
        .join(
            ChatParticipant,
            ChatParticipant.chat_session_id == ChatSession.id
        )
        .filter(
            ChatParticipant.user_id.in_([
                current_user_id,
                other_user_id
            ])
        )
        .group_by(ChatSession.id)
        .having(
            func.count(
                distinct(ChatParticipant.user_id)
            ) == 2
        )
        .first()
    )

    # --------------------------------------------------------
    # No existing conversation
    # --------------------------------------------------------

    if not chat_session:
        return []

    # --------------------------------------------------------
    # Get messages
    # --------------------------------------------------------

    return (
    db.query(ChatHistory)
    .filter(
        ChatHistory.chat_session_id == chat_session.id
    )
    .order_by(
        ChatHistory.created_at.asc()
    )
    .all()
)