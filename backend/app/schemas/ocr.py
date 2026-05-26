from pydantic import BaseModel, Field
from typing import List, Optional

class MedicationItem(BaseModel):
    name: str = Field(..., description="The identified name of the medication or therapeutic drug.")
    dosage: Optional[str] = Field(None, description="The specific strength or quantity prescribed (e.g., 500mg, 10ml).")
    frequency: Optional[str] = Field(None, description="How often the drug should be taken (e.g., Twice daily, Before meals).")

class StructuredPrescriptionResponse(BaseModel):
    patient_name: Optional[str] = Field(None, description="Extracted name of the patient if present on the document.")
    medications: List[MedicationItem] = Field(default=[], description="List of all unique drugs identified in the prescription text.")
    clinical_warnings: List[str] = Field(default=[], description="System safety flags or standard educational notifications based on the noted drugs.")

class LabBiomarker(BaseModel):
    test_name: str = Field(..., description="The name of the lab test or biomarker analyzed (e.g., Hemoglobin, Serum Creatinine).")
    observed_value: str = Field(..., description="The specific measurement value recorded from the patient's sample.")
    reference_range: Optional[str] = Field(None, description="The standard healthy baseline reference intervals (e.g., 13.5-17.5 g/dL).")
    status: str = Field(..., description="Categorized status flag: 'NORMAL', 'HIGH', or 'LOW'.")

class StructuredReportResponse(BaseModel):
    panel_title: str = Field(..., description="The overarching title of the medical report (e.g., Complete Blood Count, Liver Function Profile).")
    biomarkers: List[LabBiomarker] = Field(default=[], description="Structured collection of all identified lab test measurements.")
    summary_analysis: str = Field(..., description="A professional, high-level educational summary explaining the observed biomarker interactions.")