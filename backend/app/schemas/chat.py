from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatPromptRequest(BaseModel):
    session_id: str
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True