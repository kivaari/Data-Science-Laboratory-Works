from pydantic import BaseModel, validator


class PredictionRow(BaseModel):
    Gender: object
    Married: object
    Dependents: object
    Education: object
    Self_Employed: object
    ApplicantIncome: float
    CoapplicantIncome: float
    LoanAmount: float
    Loan_Amount_Term: float
    Credit_History: float
    Property_Area: object

    @validator("Gender")
    def gender_must_be_valid(cls, value: str) -> str:
        valid_genders = ["Male", "Female", "Other"]
        if value not in valid_genders:
            raise ValueError(f"Gender must be one of {valid_genders}")
        return value

    @validator("Married")
    def married_must_be_valid(cls, value: str) -> str:
        valid_married = ["Yes", "No"]
        if value not in valid_married:
            raise ValueError(f"Married must be one of {valid_married}")
        return value

    @validator("Dependents")
    def dependents_must_be_valid(cls, value: str) -> str:
        valid_dependents = ["0", "1", "2", "3+"]
        if value not in valid_dependents:
            raise ValueError(f"Dependents must be one of {valid_dependents}")
        return value

    @validator("Education")
    def education_must_be_valid(cls, value: str) -> str:
        valid_education = ["Graduate", "Not Graduate"]
        if value not in valid_education:
            raise ValueError(f"Education must be one of {valid_education}")
        return value

    @validator("Self_Employed")
    def self_employed_must_be_valid(cls, value: str) -> str:
        valid_self_employed = ["Yes", "No"]
        if value not in valid_self_employed:
            raise ValueError(f"Self_Employed must be one of {valid_self_employed}")
        return value

    @validator("ApplicantIncome")
    def applicant_income_must_be_positive(cls, value: float) -> float:
        if value < 0:
            raise ValueError("ApplicantIncome must be positive")
        return value

    @validator("CoapplicantIncome")
    def coapplicant_income_must_be_positive(cls, value: float) -> float:
        if value < 0:
            raise ValueError("CoapplicantIncome must be positive")
        return value

    @validator("LoanAmount")
    def loan_amount_must_be_positive(cls, value: float) -> float:
        if value < 0:
            raise ValueError("LoanAmount must be positive")
        return value

    @validator("Loan_Amount_Term")
    def loan_amount_term_must_be_positive(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Loan_Amount_Term must be positive")
        return value

    @validator("Credit_History")
    def credit_history_must_be_valid(cls, value: float) -> float:
        valid_credit_history = [0.0, 1.0]
        if value not in valid_credit_history:
            raise ValueError(f"Credit_History must be one of {valid_credit_history}")
        return value

    @validator("Property_Area")
    def property_area_must_be_valid(cls, value: str) -> str:
        valid_property_areas = ["Urban", "Semiurban", "Rural"]
        if value not in valid_property_areas:
            raise ValueError(f"Property_Area must be one of {valid_property_areas}")
        return value
