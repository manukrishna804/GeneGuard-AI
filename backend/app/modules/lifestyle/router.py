from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.modules.lifestyle.service import (
    predict_hypertension,
    predict_stroke,
    predict_ckd,
    predict_diabetes,
    predict_heart_disease,
)


router = APIRouter(
    prefix="/lifestyle",
    tags=["lifestyle"]
)


# ============================================================
# HYPERTENSION
# ============================================================

class HypertensionInput(BaseModel):
    Age: float = Field(..., ge=1, le=120)
    Salt_Intake: float = Field(..., ge=0, le=50)
    Stress_Score: float = Field(..., ge=0, le=10)
    Sleep_Duration: float = Field(..., ge=0, le=24)
    BMI: float = Field(..., ge=5, le=80)

    BP_History: str
    Medication: str
    Family_History: str
    Exercise_Level: str
    Smoking_Status: str


@router.post("/hypertension")
def hypertension_prediction(data: HypertensionInput):
    return predict_hypertension(data.model_dump())


# ============================================================
# STROKE
# ============================================================

class StrokeInput(BaseModel):
    gender: str
    age: float = Field(..., ge=1, le=120)
    hypertension: int = Field(..., ge=0, le=1)
    heart_disease: int = Field(..., ge=0, le=1)
    ever_married: str
    work_type: str
    Residence_type: str

    avg_glucose_level: float = Field(..., gt=0, le=1000)
    bmi: float = Field(..., ge=5, le=80)

    smoking_status: str


@router.post("/stroke")
def stroke_prediction(data: StrokeInput):
    return predict_stroke(data.model_dump())


# ============================================================
# CHRONIC KIDNEY DISEASE
# ============================================================

class CKDInput(BaseModel):
    Bp: float = Field(..., gt=0, le=300)
    Sg: float = Field(..., ge=1.0, le=1.1)
    Al: float = Field(..., ge=0, le=5)
    Su: float = Field(..., ge=0, le=5)

    Rbc: str

    Bu: float = Field(..., gt=0, le=500)
    Sc: float = Field(..., gt=0, le=30)
    Sod: float = Field(..., gt=0, le=200)
    Pot: float = Field(..., gt=0, le=20)
    Hemo: float = Field(..., gt=0, le=30)
    Wbcc: float = Field(..., gt=0, le=50000)
    Rbcc: float = Field(..., gt=0, le=15)

    Htn: str


@router.post("/ckd")
def ckd_prediction(data: CKDInput):
    return predict_ckd(data.model_dump())


# ============================================================
# DIABETES
# ============================================================

class DiabetesInput(BaseModel):
    gender: str
    age: float = Field(..., ge=1, le=120)

    hypertension: int = Field(..., ge=0, le=1)
    heart_disease: int = Field(..., ge=0, le=1)

    smoking_history: str

    bmi: float = Field(..., ge=5, le=80)
    HbA1c_level: float = Field(..., gt=0, le=20)
    blood_glucose_level: int = Field(..., gt=0, le=1000)


@router.post("/diabetes")
def diabetes_prediction(data: DiabetesInput):
    return predict_diabetes(data.model_dump())


# ============================================================
# HEART DISEASE
# ============================================================

class HeartDiseaseInput(BaseModel):
    age: float = Field(..., ge=1, le=120)

    sex: str
    cp: str

    trestbps: float = Field(..., gt=0, le=300)
    chol: float = Field(..., gt=0, le=1000)

    fbs: str
    restecg: str

    thalch: float = Field(..., gt=0, le=300)
    exang: str

    oldpeak: float = Field(..., ge=0, le=20)

    slope: str

    ca: float = Field(..., ge=0, le=4)

    thal: str


@router.post("/heart-disease")
def heart_disease_prediction(data: HeartDiseaseInput):
    return predict_heart_disease(data.model_dump())


# ============================================================
# OVERALL RISK SUMMARY
# ============================================================

def calculate_overall_risk(results: dict):
    risk_levels = [
        result["risk_level"]
        for result in results.values()
    ]

    if "High" in risk_levels:
        overall_risk = "High"
    elif "Moderate" in risk_levels:
        overall_risk = "Moderate"
    else:
        overall_risk = "Low"

    return {
        "overall_risk": overall_risk,
        "diseases_assessed": len(risk_levels),
        "high_risk_conditions": risk_levels.count("High"),
        "moderate_risk_conditions": risk_levels.count("Moderate"),
        "low_risk_conditions": risk_levels.count("Low")
    }

# ============================================================
# UNIFIED LIFESTYLE RISK ASSESSMENT
# ============================================================

class LifestyleRiskAssessmentInput(BaseModel):
    hypertension: HypertensionInput
    stroke: StrokeInput
    ckd: CKDInput
    diabetes: DiabetesInput
    heart_disease: HeartDiseaseInput


@router.post("/risk-assessment")
def lifestyle_risk_assessment(
    data: LifestyleRiskAssessmentInput
):
    results = {
        "hypertension": predict_hypertension(
            data.hypertension.model_dump()
        ),
        "stroke": predict_stroke(
            data.stroke.model_dump()
        ),
        "ckd": predict_ckd(
            data.ckd.model_dump()
        ),
        "diabetes": predict_diabetes(
            data.diabetes.model_dump()
        ),
        "heart_disease": predict_heart_disease(
            data.heart_disease.model_dump()
        ),
    }

    overall_summary = calculate_overall_risk(results)

    return {
        "overall_summary": overall_summary,
        "conditions": results
    }