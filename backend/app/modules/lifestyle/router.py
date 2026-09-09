from pathlib import Path

import joblib
import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/lifestyle", tags=["lifestyle"])


# Load the trained hypertension model
MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "hypertension_model.pkl"
)

hypertension_model = joblib.load(MODEL_PATH)


class HypertensionInput(BaseModel):
    Age: float
    Salt_Intake: float
    Stress_Score: float
    Sleep_Duration: float
    BMI: float

    BP_History: str
    Medication: str
    Family_History: str
    Exercise_Level: str
    Smoking_Status: str


@router.post("/hypertension")
def predict_hypertension(data: HypertensionInput):

    input_data = pd.DataFrame([{
        "Age": data.Age,
        "Salt_Intake": data.Salt_Intake,
        "Stress_Score": data.Stress_Score,
        "Sleep_Duration": data.Sleep_Duration,
        "BMI": data.BMI,
        "BP_History": data.BP_History,
        "Medication": data.Medication,
        "Family_History": data.Family_History,
        "Exercise_Level": data.Exercise_Level,
        "Smoking_Status": data.Smoking_Status,
    }])

    prediction = hypertension_model.predict(input_data)[0]

    probability = hypertension_model.predict_proba(input_data)[0][1]

    if probability < 0.33:
        risk_level = "Low"
    elif probability < 0.66:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return {
        "disease": "Hypertension",
        "prediction": int(prediction),
        "risk_probability": round(float(probability), 4),
        "risk_level": risk_level
    }