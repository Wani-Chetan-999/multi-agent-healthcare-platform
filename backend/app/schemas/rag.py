from pydantic import BaseModel

class DocumentIngestPayload(BaseModel):
    document_title: str
    raw_text_content: str