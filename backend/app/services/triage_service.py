from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.schemas.triage import TriageAssessmentResponse
import logging

logger = logging.getLogger(__name__)

class ClinicalTriageService:
    def __init__(self):
        # Initialize Groq Llama-3 model for precise schema analysis
        self.base_llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama3-8b-8192",
            temperature=0.0  # Zero temperature ensures consistent, deterministic risk evaluation
        )
        # Bind our Pydantic response schema to force structured JSON output formatting
        self.structured_analyzer = self.base_llm.with_structured_output(TriageAssessmentResponse)

    async def analyze_symptoms_risk_profile(self, user_input_text: str) -> TriageAssessmentResponse:
        """
        Runs the incoming symptom profile through our prompt engineering matrix 
        to evaluate potential health emergencies.
        """
        triage_prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert clinical triage screening assistant. Your job is to analyze user-reported symptoms "
                "and identify potential life-threatening health emergencies.\n\n"
                "CRITICAL LIFE-THREATENING EMERGENCY MARKERS INCLUDE:\n"
                "- Chest pain, radiating arm/jaw pain, pressure, or tightness (Myocardial Infarction risk)\n"
                "- Severe shortness of breath, acute dyspnea, or anaphylactic airway closure\n"
                "- Sudden numbness, asymmetric facial drooping, slurred speech (Acute Stroke indicators)\n"
                "- Severe, uncontrolled bleeding, poisoning, or sudden loss of responsiveness\n\n"
                "EVALUATION CRITERIA:\n"
                "1. If any critical emergency markers are found, set `is_emergency` to true and `severity_tier` to 'CRITICAL'.\n"
                "2. Provide highly descriptive, professional clinical educational guidance outlining standard care parameters.\n"
                "3. You must include a transparent safety disclaimer stating that this automated triage check does not replace in-person medical validation."
            )),
            ("human", "Patient Symptom Log: {patient_symptoms}")
        ])

        # Construct the execution chain
        evaluation_chain = triage_prompt_template | self.structured_analyzer
        
        try:
            # Execute the structured prediction pipeline asynchronously
            assessment_result: TriageAssessmentResponse = evaluation_chain.invoke({
                "patient_symptoms": user_input_text
            })
            return assessment_result
        except Exception as e:
            logger.error(f"Critical exception inside Triage Core Execution: {str(e)}")
            # Safe system fallback if the prediction pipeline faces an issue
            return TriageAssessmentResponse(
                is_emergency=True,  # Default to high safety flag on processing failure
                severity_tier="CRITICAL",
                risk_factors=["System evaluation processing error"],
                clinical_educational_guidance="An error occurred while processing this assessment. If you are feeling severe physical discomfort, please contact emergency services immediately.",
                safety_disclaimer="System pipeline fallback active. Please consult professional healthcare teams directly."
            )