from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean, JSON
from app.models.base import Base
from datetime import datetime

class ConversationModel(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True) # Thread ID (UUID)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), default="New Consultation")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    messages = relationship("ChatMessageModel", back_populates="conversation", cascade="all, delete-orphan")
    documents = relationship("UploadedDocumentModel", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[str] = mapped_column(String(100), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True) # Stores debugging metrics or path logs
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation = relationship("ConversationModel", back_populates="messages")

class UploadedDocumentModel(Base):
    __tablename__ = "uploaded_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[str] = mapped_column(String(100), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100)) # 'prescription' or 'lab_report'
    raw_ocr_text: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation = relationship("ConversationModel", back_populates="documents")

class PatientClinicalEntityModel(Base):
    __tablename__ = "patient_longitudinal_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100)) # 'medication', 'allergy', 'biomarker_metric'
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value_details: Mapped[str] = mapped_column(Text, nullable=True) # "500mg - Twice Daily" or "HIGH - 180 mg/dL"
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
