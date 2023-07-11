from pydantic import BaseModel, validator


class PredictionRow(BaseModel):
    Gender: object
    Married: object
    Dependents: object
    Education: object
    Self_Employed: object
    Applicant_Income: float
    Coapplicant_Income: float
    Loan_Amount: float
    Term: float
    Credit_History: float
    Area: object

    @validator("Gender")
    def gender_must_be_valid(cls, value: str) -> str:
        valid_genders = ["Male", "Female"]
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

    @validator("Applicant_Income")
    def applicant_income_must_be_positive(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Applicant_Income must be positive")
        return value

    @validator("Coapplicant_Income")
    def coapplicant_income_must_be_positive(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Coapplicant_Income must be positive")
        return value

    @validator("Term")
    def term_must_be_positive(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Term must be positive")
        return value

    @validator("Credit_History")
    def credit_history_must_be_valid(cls, value: float) -> float:
        if value < 0 and value > 1:
            raise ValueError("Credit_History out of range")
        return value

    @validator("Area")
    def area_must_be_valid(cls, value: str) -> str:
        valid_areas = ["Urban", "Semiurban", "Rural"]
        if value not in valid_areas:
            raise ValueError(f"Area must be one of {valid_areas}")
        return value
