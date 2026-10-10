from pathlib import Path

import joblib
import pandas as pd
from xgboost import XGBClassifier


MODEL_DIR = Path(__file__).resolve().parent / "models"


# ============================================================
# LOAD MODELS
# ============================================================

# Hypertension
hypertension_model = joblib.load(
    MODEL_DIR / "hypertension_model.pkl"
)

# Stroke
stroke_model = joblib.load(
    MODEL_DIR / "stroke_risk_model.pkl"
)

# CKD
ckd_model = joblib.load(
    MODEL_DIR / "ckd_risk_model.pkl"
)

# Diabetes preprocessing
diabetes_preprocessor = joblib.load(
    MODEL_DIR / "diabetes_preprocessor.pkl"
)

# Diabetes XGBoost model
diabetes_model = XGBClassifier()

diabetes_model.load_model(
    MODEL_DIR / "diabetes_xgboost.json"
)

# Heart Disease
heart_disease_model = joblib.load(
    MODEL_DIR / "heart_disease_random_forest_model.pkl"
)


# ============================================================
# HYPERTENSION
# ============================================================

def predict_hypertension(data: dict):

    input_data = pd.DataFrame([data])

    prediction = hypertension_model.predict(input_data)[0]

    probability = hypertension_model.predict_proba(
        input_data
    )[0][1]

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


# ============================================================
# STROKE
# ============================================================

def predict_stroke(data: dict):

    input_data = pd.DataFrame([data])

    prediction = stroke_model.predict(input_data)[0]

    probability = stroke_model.predict_proba(
        input_data
    )[0][1]

    if probability < 0.33:
        risk_level = "Low"
    elif probability < 0.66:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return {
        "disease": "Stroke",
        "prediction": int(prediction),
        "risk_probability": round(float(probability), 4),
        "risk_level": risk_level
    }


# ============================================================
# CHRONIC KIDNEY DISEASE
# ============================================================

def predict_ckd(data: dict):

    input_data = pd.DataFrame([data])

    prediction = ckd_model.predict(input_data)[0]

    probability = ckd_model.predict_proba(
        input_data
    )[0][1]

    if probability < 0.33:
        risk_level = "Low"
    elif probability < 0.66:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return {
        "disease": "Chronic Kidney Disease",
        "prediction": int(prediction),
        "risk_probability": round(float(probability), 4),
        "risk_level": risk_level
    }


# ============================================================
# DIABETES
# ============================================================

def predict_diabetes(data: dict):

    input_data = pd.DataFrame([data])

    # Apply the same preprocessing used during training
    transformed_data = diabetes_preprocessor.transform(
        input_data
    )

    # XGBoost prediction
    prediction = diabetes_model.predict(
        transformed_data
    )[0]

    # Probability of diabetic class
    probability = diabetes_model.predict_proba(
        transformed_data
    )[0][1]

    if probability < 0.33:
        risk_level = "Low"
    elif probability < 0.66:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return {
        "disease": "Diabetes",
        "prediction": int(prediction),
        "risk_probability": round(float(probability), 4),
        "risk_level": risk_level
    }

    # ============================================================
# HEART DISEASE
# ============================================================

def predict_heart_disease(data: dict):

    input_data = pd.DataFrame([data])

    prediction = heart_disease_model.predict(
        input_data
    )[0]

    probability = heart_disease_model.predict_proba(
        input_data
    )[0][1]

    if probability < 0.33:
        risk_level = "Low"
    elif probability < 0.66:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return {
        "disease": "Heart Disease",
        "prediction": int(prediction),
        "risk_probability": round(float(probability), 4),
        "risk_level": risk_level
    }