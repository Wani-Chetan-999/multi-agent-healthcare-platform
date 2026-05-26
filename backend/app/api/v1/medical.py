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

from fastapi import UploadFile, File, HTTPException
from app.services.ocr_service import MedicalOCRProcessingService
from app.schemas.ocr import StructuredPrescriptionResponse, StructuredReportResponse

@router.post("/scan-prescription", response_model=StructuredPrescriptionResponse)
async def upload_and_scan_prescription_document(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Accepts image file uploads, runs OCR text extraction, and processes 
    the text through an LLM to output a clean, structured prescription format.
    """
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a valid PNG or JPEG image.")
        
    ocr_service = MedicalOCRProcessingService()
    file_bytes = await file.read()
    
    raw_text = ocr_service.extract_raw_text_from_bytes(file_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="OCR engine failed to detect any readable text blocks in this image document.")
        
    structured_prescription = await ocr_service.compile_structured_prescription(raw_text)
    return structured_prescription

@router.post("/analyze-report", response_model=StructuredReportResponse)
async def upload_and_analyze_diagnostic_report(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Accepts image file uploads, runs OCR text extraction, and processes 
    the text through an LLM to output a clean, structured medical report format.
    """
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a valid PNG or JPEG image.")
        
    ocr_service = MedicalOCRProcessingService()
    file_bytes = await file.read()
    
    raw_text = ocr_service.extract_raw_text_from_bytes(file_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="OCR engine failed to detect any readable text blocks in this image document.")
        
    structured_report = await ocr_service.compile_structured_report(raw_text)
    return structured_report