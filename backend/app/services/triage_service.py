import json
import logging
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.schemas.triage import TriageAssessmentResponse

logger = logging.getLogger(__name__)


class ClinicalTriageService:
    def __init__(self):

        self.base_llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
            temperature=0.0
        )

    async def analyze_symptoms_risk_profile(
        self,
        user_input_text: str
    ) -> TriageAssessmentResponse:

        triage_prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                You are an expert clinical triage screening assistant.

                Return ONLY raw JSON.
                Do not explain.
                Do not use markdown.

                JSON format:

                {{
                "is_emergency": false,
                "severity_tier": "LOW",
                "risk_factors": ["factor1", "factor2"],
                "clinical_educational_guidance": "guidance text",
                "safety_disclaimer": "disclaimer"
                }}

                Rules:
                - If symptoms are life threatening set is_emergency=true
                - severity_tier must be:
                LOW, MODERATE, HIGH, or CRITICAL
                - Always return valid JSON only
                """
                ),
                        (
                            "human",
                            "Patient Symptom Log: {patient_symptoms}"
                        )
                    ])

        evaluation_chain = triage_prompt_template | self.base_llm

        try:

            response = evaluation_chain.invoke({
                "patient_symptoms": user_input_text
            })

            raw_content = response.content


            json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)

            if not json_match:
                raise ValueError("No valid JSON returned from model.")

            parsed = json.loads(json_match.group())

            return TriageAssessmentResponse(**parsed)

        except Exception as e:

            logger.error(
                f"Critical exception inside Triage Core Execution: {str(e)}"
            )

            return TriageAssessmentResponse(
                is_emergency=True,
                severity_tier="CRITICAL",
                risk_factors=["System evaluation processing error"],
                clinical_educational_guidance=(
                    "An error occurred while processing this assessment. "
                    "If you are feeling severe physical discomfort, "
                    "please contact emergency services immediately."
                ),
                safety_disclaimer=(
                    "System pipeline fallback active. "
                    "Please consult professional healthcare teams directly."
                )
            )