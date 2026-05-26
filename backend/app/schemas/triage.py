from pydantic import BaseModel, Field
from typing import List

class SymptomEvaluationRequest(BaseModel):
    symptoms_text: str

class TriageAssessmentResponse(BaseModel):
    is_emergency: bool = Field(
        ..., 
        description="True if symptoms point to life-threatening conditions needing immediate ER attention."
    )
    severity_tier: str = Field(
        ..., 
        description="Categorized classification: 'CRITICAL', 'URGENT', or 'ROUTINE'."
    )
    risk_factors: List[str] = Field(
        ..., 
        description="Extracted list of high-risk clinical symptoms or warning markers identified."
    )
    clinical_educational_guidance: str = Field(
        ..., 
        description="Structured, evidence-based educational insights summarizing the noted health symptoms."
    )
    safety_disclaimer: str = Field(
        ..., 
        description="Mandatory clear clinical disclaimer reinforcing that this evaluation is an automated review, not a definitive diagnosis."
    )