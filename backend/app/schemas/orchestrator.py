from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class CopilotInboundPayload(BaseModel):
    conversation_id: str
    message: Optional[str] = ""
    attached_file_b64: Optional[str] = None
    attached_file_name: Optional[str] = None
    attached_file_mime: Optional[str] = None  # image/png, audio/wav, etc.

class CopilotOutboundResponse(BaseModel):
    conversation_id: str
    response_text: str
    dispatched_path: str
    extracted_entities: Optional[List[Dict[str, Any]]] = None