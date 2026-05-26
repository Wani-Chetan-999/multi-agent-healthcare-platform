from fastapi import APIRouter, Depends, status
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