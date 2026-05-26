from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.models.chat import ChatMessageModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChatEngineService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        # Initialize Groq using Llama-3-8b for optimal speed and reliability
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
            temperature=0.3,
            streaming=True
        )
        
    async def get_session_history(self, user_id: int, session_id: str) -> list:
        """Retrieves and structures the historical conversation timeline from the database."""
        stmt = (
            select(ChatMessageModel)
            .where(ChatMessageModel.user_id == user_id, ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.created_at.asc())
        )
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        
        langchain_history = []
        for msg in messages:
            if msg.role == "user":
                langchain_history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_history.append(AIMessage(content=msg.content))
        return langchain_history

    async def persist_message(self, user_id: int, session_id: str, role: str, content: str):
        """Saves a message entry to the database for historical persistence."""
        db_msg = ChatMessageModel(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content
        )
        self.db.add(db_msg)
        await self.db.commit()

    async def execute_conversational_stream(self, user_id: int, session_id: str, current_prompt: str):
        """
        Loads the conversation history, applies safety system prompts, 
        and streams tokens sequentially from the Groq API.
        """
        # 1. Fetch historical data entries
        history = await self.get_session_history(user_id, session_id)
        
        # 2. Inject foundational healthcare boundaries
        system_boundary = SystemMessage(content=(
            "You are an advanced, clinical-grade AI Healthcare Assistant platform framework. "
            "You provide highly descriptive, analytical, and structured guidance regarding operational medical systems. "
            "CRITICAL DIRECTIVE: You must NEVER issue direct definitive clinical diagnoses or prescribe concrete treatment courses. "
            "Always include transparent, clean markdown safety notifications instructing users to seek professional clinical confirmation."
        ))
        
        # 3. Assemble full evaluation payload
        payload = [system_boundary] + history + [HumanMessage(content=current_prompt)]
        
        # 4. Stream response tokens from the LLM
        complete_response_content = ""
        try:
            # We use a standard async loop to step through the token streams cleanly
            for chunk in self.llm.stream(payload):
                token = chunk.content
                if token:
                    complete_response_content += token
                    yield token
        except Exception as e:
            logger.error(f"Groq Core Stream Interruption: {str(e)}")
            yield f"\n[Core Execution Interruption: {str(e)}]"
            return

        # 5. Persist the complete interaction to history
        await self.persist_message(user_id, session_id, "user", current_prompt)
        await self.persist_message(user_id, session_id, "assistant", complete_response_content)