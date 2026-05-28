import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

# LangChain / LangGraph Engine Elements
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.workflow_copilot import compiled_copilot_graph

# Database and Session Dependencies
from app.database.session import get_db
from app.api.v1.auth import get_current_user

# Data Models
from app.models.user import UserModel
from app.models.chat import ConversationModel, ChatMessageModel

# Pydantic Schemas
from app.schemas.orchestrator import CopilotInboundPayload, CopilotOutboundResponse
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

# -------------------------------------------------------
# DATA SCHEMAS
# -------------------------------------------------------
class MessageResponse(BaseModel):
    role: str
    content: str

    class Config:
        from_attributes = True


# -------------------------------------------------------
# THREAD OPERATIONS
# -------------------------------------------------------
@router.post("/threads", status_code=status.HTTP_201_CREATED)
async def create_new_conversation_thread(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Initializes a distinct, trackable conversation session thread."""
    new_id = str(uuid.uuid4())
    thread = ConversationModel(
        id=new_id, 
        user_id=current_user.id, 
        title="New Consultation Workspace"
    )
    db.add(thread)
    await db.commit()
    return {"conversation_id": new_id, "title": thread.title}


@router.get("/threads", status_code=status.HTTP_200_OK)
async def list_user_conversation_threads(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Fetches list of all historical communication logs matching an account ID."""
    stmt = (
        select(ConversationModel)
        .where(ConversationModel.user_id == current_user.id)
        .order_by(ConversationModel.created_at.desc())
    )
    res = await db.execute(stmt)
    threads = res.scalars().all()
    return [{"conversation_id": t.id, "title": t.title, "created_at": t.created_at} for t in threads]


@router.get("/threads/{thread_id}/messages", response_model=List[MessageResponse])
async def get_thread_messages(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Production-grade endpoint fetching historic structural conversation arrays 
    ordered chronologically. Validates user ownership boundaries via relationship joins.
    """
    try:
        # Secure boundary verification: Ensure thread belongs to requesting current_user
        auth_stmt = (
            select(ConversationModel)
            .where(ConversationModel.id == thread_id, ConversationModel.user_id == current_user.id)
        )
        auth_res = await db.execute(auth_stmt)
        thread_exists = auth_res.scalar_one_or_none()

        if not thread_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation thread not found or access unauthorized."
            )

        # Query messages chronologically
        stmt = (
            select(ChatMessageModel)
            .where(ChatMessageModel.conversation_id == thread_id)
            .order_by(ChatMessageModel.created_at.asc())
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        return [{"role": msg.role, "content": msg.content} for msg in messages]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring thread context metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore conversational data mapping: {str(e)}"
        )


# -------------------------------------------------------
# AGENTIC LOOP EXECUTION
# -------------------------------------------------------
@router.post("/copilot-execute", response_model=CopilotOutboundResponse)
async def execute_unified_copilot_loop(
    payload: CopilotInboundPayload,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Ingests inbound payload tokens, hydrates current message loops with historical 
    SQL sequences, evaluates state vectors using LangGraph and pushes updates to database.
    """
    # 1. Fetch previous history messages from SQL to maintain conversation memory
    stmt = (
        select(ChatMessageModel)
        .where(ChatMessageModel.conversation_id == payload.conversation_id)
        .order_by(ChatMessageModel.created_at.asc())
    )
    res = await db.execute(stmt)
    history_records = res.scalars().all()
    
    graph_messages = []
    for msg in history_records:
        if msg.role == "user":
            graph_messages.append(HumanMessage(content=msg.content))
        else:
            graph_messages.append(AIMessage(content=msg.content))
            
    # Append current input prompt text context
    if payload.message:
        graph_messages.append(HumanMessage(content=payload.message))
        db.add(ChatMessageModel(conversation_id=payload.conversation_id, role="user", content=payload.message))

    # Assemble initial state variables dictionary
    initial_state = {
        "messages": graph_messages,
        "user_id": current_user.id,
        "session_id": payload.conversation_id,
        "next_action": "",
        "triage_evaluation": {
            "b64_data": payload.attached_file_b64,
            "file_name": payload.attached_file_name,
            "mime_type": payload.attached_file_mime
        }
    }

    # Run our LangGraph state machine asynchronously
    final_state = await compiled_copilot_graph.ainvoke(initial_state)
    
    # Save the final response text back to your database history logs
    final_reply = final_state["messages"][-1].content
    db.add(ChatMessageModel(conversation_id=payload.conversation_id, role="assistant", content=final_reply))
    
    # Dynamically update thread title if it's still the default name
    if len(history_records) < 2 and payload.message:
        thread_stmt = select(ConversationModel).where(ConversationModel.id == payload.conversation_id)
        thread_res = await db.execute(thread_stmt)
        thread_obj = thread_res.scalar_one_or_none()
        if thread_obj:
            # Set summary slice preview
            thread_obj.title = payload.message[:30] + "..."
            
    await db.commit()
    
    async def token_generator():

        chunks = final_reply.splitlines(keepends=True)

        for chunk in chunks:

            yield chunk

            await asyncio.sleep(0.02)

    return StreamingResponse(
        token_generator(),
        media_type="text/plain"
    )