from fastapi import APIRouter, Depends, status, HTTPException
from app.api.v1.auth import get_current_user
from app.models.base import UserModel
from app.schemas.triage import SymptomEvaluationRequest, TriageAssessmentResponse
from app.services.triage_service import ClinicalTriageService

router = APIRouter()

@router.post("/triage-check", response_model=TriageAssessmentResponse, status_code=status.HTTP_200_OK)
async def perform_clinical_symptom_triage(
    payload: SymptomEvaluationRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Evaluates patient-reported symptoms, extracts health risk factors, 
    and returns a structured severity tier assessment.
    """
    triage_engine = ClinicalTriageService()
    assessment = await triage_engine.analyze_symptoms_risk_profile(payload.symptoms_text)
    return assessment

from app.schemas.rag import DocumentIngestPayload
from app.rag.vector_store import MedicalKnowledgeVectorMesh

@router.post("/ingest-knowledge", status_code=status.HTTP_201_CREATED)
async def ingest_reference_knowledge_into_vector_mesh(
    payload: DocumentIngestPayload,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Exposes an authenticated endpoint to process, chunk, 
    and store clinical reference manuals inside ChromaDB.
    """
    vector_db = MedicalKnowledgeVectorMesh()
    success = await vector_db.ingest_raw_medical_text(payload.document_title, payload.raw_text_content)
    if not success:
        raise HTTPException(status_code=400, detail="Document ingestion failed. Verify data parameters.")
    return {"status": "success", "message": f"Document '{payload.document_title}' ingested and indexed successfully."}