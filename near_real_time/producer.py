from os import environ
import time
import uuid
import random
from kafka import KafkaProducer
from src.data_model import PredictionRow
from dotenv import load_dotenv

load_dotenv()

SERVER = environ.get("SERVER")

possible_gender_values = ["Male", "Female"]
possible_married_values = ["Yes", "No"]
possible_dependents_values = ["0", "1", "2", "3+"]
possible_education_values = ["Graduate", "Not Graduate"]
possible_self_employed_values = ["Yes", "No"]
possible_area_values = ["Urban", "Semiurban", "Rural"]

producer = KafkaProducer(bootstrap_servers=SERVER)

while True:
    choosen_gender = random.choice(possible_gender_values)
    choosen_married = random.choice(possible_married_values)
    choosen_dependents = random.choice(possible_dependents_values)
    choosen_education = random.choice(possible_education_values)
    choosen_self_employed = random.choice(possible_self_employed_values)
    choosen_applicant_income = random.uniform(0, 1_000_000)
    choosen_coapplicant_income = random.uniform(0, 300_000)
    choosen_loan_amount = random.uniform(0, 16_000_000)
    choosen_term = random.uniform(0, 500)
    choosen_credit_history = random.uniform(0, 1)
    choosen_area = random.choice(possible_area_values)
    pred_row = PredictionRow(
        Gender=choosen_gender, Married=choosen_married, Dependents=choosen_dependents, 
        Education=choosen_education, Self_Employed=choosen_self_employed,
        Applicant_Income=choosen_applicant_income, Coapplicant_Income=choosen_coapplicant_income, 
        Loan_Amount=choosen_loan_amount, Term=choosen_term, Credit_History=choosen_credit_history,
         Area=choosen_area
    )
    producer.send("mltopic", key=str(uuid.uuid4()).encode("utf8"), value=pred_row.json().encode("utf8"))
    time.sleep(5)