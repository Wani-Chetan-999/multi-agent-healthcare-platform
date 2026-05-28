from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.v1.auth import get_current_user
from app.models.user import UserModel
from app.schemas.chat import ChatPromptRequest
from app.services.chat_service import ChatEngineService

router = APIRouter()

@router.post("/stream", status_code=status.HTTP_200_OK)
async def stream_chat_interactions(
    payload: ChatPromptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Exposes a real-time token stream endpoint protected by JWT authentication.
    """
    service = ChatEngineService(db)
    
    async def token_generator():
        async for token in service.execute_conversational_stream(
            user_id=current_user.id,
            session_id=payload.session_id,
            current_prompt=payload.message
        ):
            yield token

    return StreamingResponse(token_generator(), media_type="text/plain")