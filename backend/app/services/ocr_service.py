import easyocr
import json
import re
import numpy as np
import cv2
import logging
from langchain_groq import ChatGroq
from app.core.config import settings
from app.schemas.ocr import StructuredPrescriptionResponse, StructuredReportResponse

logger = logging.getLogger(__name__)

class MedicalOCRProcessingService:
    def __init__(self):
        # Initialize EasyOCR reader configured for English text extraction
        # This downloads lightweight language models automatically on the first run
        self.reader = easyocr.Reader(['en'], gpu=False)
        
        # Initialize Groq Llama 3.1 engine for structural language synthesis
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
            temperature=0.0
        )

    def extract_raw_text_from_bytes(self, image_bytes: bytes) -> str:

        try:

            nparr = np.frombuffer(image_bytes, np.uint8)

            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # upscale image
            img = cv2.resize(
                img,
                None,
                fx=2,
                fy=2,
                interpolation=cv2.INTER_CUBIC
            )

            # grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # noise removal
            gray = cv2.GaussianBlur(gray, (3, 3), 0)

            # sharpen
            kernel = np.array([
                [-1,-1,-1],
                [-1, 9,-1],
                [-1,-1,-1]
            ])

            sharpened = cv2.filter2D(gray, -1, kernel)

            # thresholding
            processed = cv2.threshold(
                sharpened,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )[1]

            ocr_results = self.reader.readtext(
                processed,
                detail=0,
                paragraph=True
            )

            combined_text_blob = "\n".join(ocr_results)

            print("OCR TEXT:")
            print(combined_text_blob)

            return combined_text_blob

        except Exception as e:

            logger.error(f"OCR image reading failure: {str(e)}")

            return ""

    async def compile_structured_prescription(
        self,
        raw_ocr_text: str
    ) -> StructuredPrescriptionResponse:

        prompt = f"""
    You are an expert OCR Cleanup Agent.

    Extract prescription data.

    Return ONLY valid JSON.

    Format:

    {{
    "patient_name": "",
    "medications": [
        {{
        "name": "",
        "dosage": "",
        "frequency": ""
        }}
    ],
    "clinical_warnings": []
    }}

    Raw OCR Text:
    {raw_ocr_text}
    """

        try:

            response = await self.llm.ainvoke(prompt)

            raw_content = response.content

            json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)

            if not json_match:
                raise ValueError("No valid JSON detected.")

            parsed = json.loads(json_match.group())

            return StructuredPrescriptionResponse(**parsed)

        except Exception as e:

            logger.error(f"OCR structuring failure: {str(e)}")

            return StructuredPrescriptionResponse(
                patient_name=None,
                medications=[],
                clinical_warnings=[
                    "Unable to fully structure prescription data."
                ]
            )

    async def compile_structured_report(self, raw_ocr_text: str) -> StructuredReportResponse:
        """
        Processes unstructured OCR text through an LLM to generate a clean, structured medical report schema.
        """
        structured_extractor = self.llm.with_structured_output(StructuredReportResponse)
        
        system_prompt = (
            "You are an expert Medical Lab Analyzer Agent. Your job is to parse noisy, unstructured raw text "
            "extracted from a lab report and organize it into a clean, structured clinical summary.\n\n"
            "INSTRUCTIONS:\n"
            "1. Extract test metrics, recorded values, and normal baseline reference intervals.\n"
            "2. Map the status flag to 'NORMAL', 'HIGH', or 'LOW' based on how the observed value compares to the reference intervals.\n"
            "3. Provide an educational summary explaining what these biomarkers measure. Do not issue a definitive diagnostic judgment."
        )
        
        chain = structured_extractor
        response = await chain.ainvoke([
            ("system", system_prompt),
            ("human", f"Raw Unstructured Diagnostic Report Text Input:\n{raw_ocr_text}")
        ])
        return response