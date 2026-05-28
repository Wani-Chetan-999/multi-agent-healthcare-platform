import base64
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq

from app.agents.state import HealthcareAgentState
from app.services.ocr_service import MedicalOCRProcessingService
from app.rag.vector_store import MedicalKnowledgeVectorMesh
from app.database.session import AsyncSessionLocal
from app.models.chat import ChatMessageModel, UploadedDocumentModel, PatientClinicalEntityModel
from app.services.audio_service import ClinicalAudioVoiceService
from app.core.config import settings

class UnifiedCopilotGraphEngine:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
            temperature=0.2
        )

    async def router_node(self, state: HealthcareAgentState) -> Dict[str, Any]:

        payload = state.get("triage_evaluation") or {}

        mime_type = str(
            payload.get("mime_type", "")
        ).lower()

        text_content = ""

        if state.get("messages"):
            text_content = state["messages"][-1].content.lower()

        # AUDIO
        if "audio" in mime_type:
            return {"next_action": "process_voice"}

        # IMAGE / OCR
        if "image" in mime_type or payload.get("b64_data"):
            return {"next_action": "process_ocr"}

        # RAG
        rag_triggers = [
            "report",
            "prescription",
            "last month",
            "glucose",
            "cholesterol",
            "history",
            "lab result"
        ]

        if any(trigger in text_content for trigger in rag_triggers):
            return {"next_action": "execute_rag"}

        # DEFAULT CHAT
        return {"next_action": "standard_chat"}

    async def voice_node(self, state: HealthcareAgentState) -> Dict[str, Any]:
        """Converts incoming voice recordings into text using Groq Whisper."""
        payload = state["triage_evaluation"]
        audio_bytes = base64.b64decode(payload["b64_data"])
        
        audio_service = ClinicalAudioVoiceService()
        transcription = audio_service.transcribe_audio_stream(audio_bytes, file_name=payload["file_name"])
        
        # Replace the placeholder user message with the transcribed text
        return {"messages": [HumanMessage(content=transcription)], "next_action": "standard_chat"}

    async def ocr_node(self, state: HealthcareAgentState) -> Dict[str, Any]:
        """Extracts text from images using OCR and saves structured entities to the database."""
        payload = state["triage_evaluation"]
        file_bytes = base64.b64decode(payload["b64_data"])
        
        ocr_service = MedicalOCRProcessingService()
        raw_text = ocr_service.extract_raw_text_from_bytes(file_bytes)
        
        # Classify the document automatically using a fast keyword check
        doc_type = "lab_report" if any(k in raw_text.lower() for k in ["lab", "test", "blood", "mg/dl", "count"]) else "prescription"
        
        async with AsyncSessionLocal() as db:
            # 1. Log the document upload attachment entry
            doc_record = UploadedDocumentModel(
                conversation_id=state["session_id"],
                file_name=payload["file_name"],
                document_type=doc_type,
                raw_ocr_text=raw_text
            )
            db.add(doc_record)
            
            # 2. Extract structured fields and update our longitudinal record
            summary_text = ""
            if doc_type == "prescription":
                data = await ocr_service.compile_structured_prescription(raw_text)
                summary_text = f"Parsed Prescription for Patient: {data.patient_name or 'N/A'}.\nMedications: "
                for med in data.medications:
                    summary_text += f"\n- {med.name} ({med.dosage or 'N/A'} - {med.frequency or 'N/A'})"
                    db.add(PatientClinicalEntityModel(user_id=state["user_id"], entity_type="medication", name=med.name, value_details=f"{med.dosage} {med.frequency}"))
            else:
                data = await ocr_service.compile_structured_report(raw_text)
                summary_text = f"Analyzed Lab Report: {data.panel_title}.\nMetrics:"
                for bio in data.biomarkers:
                    summary_text += f"\n- {bio.test_name}: {bio.observed_value} (Status: {bio.status})"
                    db.add(PatientClinicalEntityModel(user_id=state["user_id"], entity_type="biomarker_metric", name=bio.test_name, value_details=f"Value: {bio.observed_value} | Range: {bio.reference_range} | {bio.status}"))
            
            await db.commit()
            
            # 3. Store the text chunks in ChromaDB for future RAG queries
            rag_vector_db = MedicalKnowledgeVectorMesh()
            await rag_vector_db.ingest_raw_medical_text(payload["file_name"], raw_text)

        formatted_reply = (
            f"📎 **Uploaded File Ingested Successfully:** "
            f"`{payload['file_name']}`\n\n"
            f"{summary_text}\n\n"
            f"*This data has been successfully saved to your "
            f"long-term medical history and is ready for "
            f"follow-up questions.*"
        )

        return {
            "messages": [
                AIMessage(content=formatted_reply)
            ]
        }

    async def rag_node(self, state: HealthcareAgentState) -> Dict[str, Any]:
        """Searches ChromaDB to retrieve relevant context from previously uploaded files."""
        user_prompt = state["messages"][-1].content
        
        rag_vector_db = MedicalKnowledgeVectorMesh()
        context_chunks = rag_vector_db.perform_semantic_knowledge_retrieval(user_prompt, k=2)
        
        context_str = "\n".join([
            f"[From File: {c['source']}]: {c['content'][:700]}"
            for c in context_chunks
        ])
        
        system_instruction = (
            "You are an expert Clinical Copilot. Use the following context retrieved from the patient's "
            "uploaded files to answer their question. If the context does not contain the answer, "
            "use your general medical knowledge to provide helpful guidance while noting that the specific detail was not found.\n\n"
            f"RETRIEVED MEDICAL HISTORY CONTEXT:\n{context_str}"
        )
        
        recent_messages = state["messages"][-4:]

        response = self.llm.invoke(
            [SystemMessage(content=system_instruction)] + recent_messages
        )
        return {"messages": [AIMessage(content=response.content)]}

    async def chat_node(self, state: HealthcareAgentState) -> Dict[str, Any]:
        """Handles general conversation and applies standard safety parameters."""
        system_boundary = (
            "You are an advanced AI Healthcare Assistant platform framework. Provide structured guidance regarding "
            "operational medical systems. CRITICAL DIRECTIVE: You must NEVER issue direct definitive clinical diagnoses. "
            "Always include transparent markdown safety notifications instructing users to confirm parameters with a professional physician."
        )
        recent_messages = state["messages"][-4:]

        response = self.llm.invoke(
            [SystemMessage(content=system_boundary)] + recent_messages
        )
        return {"messages": [AIMessage(content=response.content)]}
    
def copilot_router_logic(state: HealthcareAgentState) -> str:
    return state["next_action"]

engine = UnifiedCopilotGraphEngine()
workflow = StateGraph(HealthcareAgentState)

workflow.add_node("router", engine.router_node)
workflow.add_node("process_voice", engine.voice_node)
workflow.add_node("process_ocr", engine.ocr_node)
workflow.add_node("execute_rag", engine.rag_node)
workflow.add_node("standard_chat", engine.chat_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    copilot_router_logic,
    {
        "process_voice": "process_voice",
        "process_ocr": "process_ocr",
        "execute_rag": "execute_rag",
        "standard_chat": "standard_chat"
    }
)

# Route auxiliary processing nodes back into standard chat or end points cleanly
workflow.add_edge("process_voice", "router") # Loop back to check transcription text intent
workflow.add_edge("process_ocr", END)
workflow.add_edge("execute_rag", END)
workflow.add_edge("standard_chat", END)

compiled_copilot_graph = workflow.compile()