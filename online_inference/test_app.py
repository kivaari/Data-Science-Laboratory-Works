import pytest
from fastapi.testclient import TestClient

from app import app
from src.constants import APPROVED_NAME, NON_APPROVED_NAME
from src.data_model import PredictionRow

test_client = TestClient(app)
TEST_ROW = PredictionRow(
    Gender="Male",
    Married="Yes",
    Dependents="2",
    Education="Graduate",
    Self_Employed="No",
    ApplicantIncome=4123,
    CoapplicantIncome=412,
    LoanAmount=349.0,
    Loan_Amount_Term=360.0,
    Credit_History=1.0,
    Property_Area="Urban"
)


def test_predict():
    result = test_client.post("/predict", json=TEST_ROW.dict())
    result_json = result.json()
    assert "prediction" in result_json
    assert result_json.get("prediction") in [APPROVED_NAME, NON_APPROVED_NAME]


def test_validation_type_error():
    with pytest.raises(ValueError):
        PredictionRow(
            Gender="AttackHelicopter",
            Married="Yes",
            Dependents="2",
            Education="Graduate",
            Self_Employed="No",
            ApplicantIncome=4123,
            CoapplicantIncome=412,
            LoanAmount=349.0,
            Loan_Amount_Term=360.0,
            Credit_History=1.0,
            Property_Area="Urban"
        )
