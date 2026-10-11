import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_heart_disease_fbs_exang_probabilities():
    """Regression test (a): the same heart-disease row with fbs/exang true vs false gives different probabilities."""
    base_payload = {
        "age": 55.0,
        "sex": "Male",
        "cp": "typical angina",
        "trestbps": 140.0,
        "chol": 240.0,
        "restecg": "normal",
        "thalch": 150.0,
        "oldpeak": 1.5,
        "slope": "flat",
        "ca": 1.0,
        "thal": "normal",
    }
    payload_true = {**base_payload, "fbs": True, "exang": True}
    payload_false = {**base_payload, "fbs": False, "exang": False}

    res_true = client.post("/api/v1/lifestyle/heart-disease", json=payload_true)
    res_false = client.post("/api/v1/lifestyle/heart-disease", json=payload_false)

    assert res_true.status_code == 200
    assert res_false.status_code == 200
    prob_true = res_true.json()["risk_probability"]
    prob_false = res_false.json()["risk_probability"]
    assert prob_true != prob_false


def test_ckd_valid_numeric_input():
    """Regression test (b): /lifestyle/ckd returns 200 on valid numeric input."""
    payload = {
        "Bp": 80.0,
        "Sg": 1.02,
        "Al": 1.0,
        "Su": 0.0,
        "Rbc": 1,
        "Bu": 36.0,
        "Sc": 1.2,
        "Sod": 137.0,
        "Pot": 4.4,
        "Hemo": 15.4,
        "Wbcc": 7800.0,
        "Rbcc": 5.2,
        "Htn": 1,
    }
    res = client.post("/api/v1/lifestyle/ckd", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["disease"] == "Chronic Kidney Disease"
    assert "risk_probability" in data
    assert "risk_level" in data


def test_invalid_category_returns_422():
    """Regression test (c): an invalid category returns 422."""
    bad_heart = {
        "age": 55.0,
        "sex": "InvalidSex",
        "cp": "typical angina",
        "trestbps": 140.0,
        "chol": 240.0,
        "fbs": True,
        "restecg": "normal",
        "thalch": 150.0,
        "exang": True,
        "oldpeak": 1.5,
        "slope": "flat",
        "ca": 1.0,
        "thal": "normal",
    }
    res = client.post("/api/v1/lifestyle/heart-disease", json=bad_heart)
    assert res.status_code == 422

    bad_diabetes = {
        "gender": "Female",
        "age": 45.0,
        "hypertension": 0,
        "heart_disease": 0,
        "smoking_history": "invalid_smoking_status",
        "bmi": 24.5,
        "HbA1c_level": 5.5,
        "blood_glucose_level": 100,
    }
    res_diab = client.post("/api/v1/lifestyle/diabetes", json=bad_diabetes)
    assert res_diab.status_code == 422

    bad_htn = {
        "Age": 50.0,
        "Salt_Intake": 10.0,
        "Stress_Score": 5.0,
        "Sleep_Duration": 7.0,
        "BMI": 25.0,
        "BP_History": "Normal",
        "Medication": "Aspirin",
        "Family_History": "No",
        "Exercise_Level": "Moderate",
        "Smoking_Status": "Non-Smoker",
    }
    res_htn = client.post("/api/v1/lifestyle/hypertension", json=bad_htn)
    assert res_htn.status_code == 422
