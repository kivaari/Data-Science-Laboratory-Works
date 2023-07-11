
from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago

s3_server = Variable.get("s3_server")
data_bucket = Variable.get("data_bucket")

def generate_data(input_dir):
    import random
    import pandas as pd
    from src.data_model import PredictionRow
    from pathlib import Path

    input_dir_path = Path(input_dir)
    input_dir_path.mkdir(parents=True, exist_ok=True)

    possible_gender_values = ["Male", "Female"]
    possible_married_values = ["Yes", "No"]
    possible_dependents_values = ["0", "1", "2", "3+"]
    possible_education_values = ["Graduate", "Not Graduate"]
    possible_self_employed_values = ["Yes", "No"]
    possible_area_values = ["Urban", "Semiurban", "Rural"]

    data = []

    for _ in range(1000):
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
            Gender=choosen_gender,
            Married=choosen_married,
            Dependents=choosen_dependents,
            Education=choosen_education,
            Self_Employed=choosen_self_employed,
            Applicant_Income=choosen_applicant_income,
            Coapplicant_Income=choosen_coapplicant_income,
            Loan_Amount=choosen_loan_amount,
            Term=choosen_term,
            Credit_History=choosen_credit_history,  
            Area=choosen_area
        )
        data.append(pred_row.dict())

    df = pd.DataFrame(data)
    df.to_csv(input_dir_path / "generated_data.csv")

def upload_data(input_dir, s3_server, data_bucket):
    import os
    from minio import Minio
    from pathlib import Path

    file_path = os.path.join(f"{input_dir}", "generated_data.csv")
    file_size = os.path.getsize(file_path)

    with open(file_path, "rb") as file:
        client = Minio(
            s3_server,
            secure=False,
            access_key="miniouser",
            secret_key="miniouser"
        )
        content = client.put_object(
            bucket_name=data_bucket, 
            object_name="generated_data.csv",
            data=file,
            length=file_size,  
            content_type="application/csv",
        )

default_args = {
    "owner": "kivaari",
    "email": ["ebelousove@gmail.com"],
    'email_on_failure': False,
    'email_on_retry': False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    default_args=default_args, 
    schedule_interval=None,  # "@daily"
    dag_id="generation_and_upload", 
    start_date=days_ago(1)
    ):

    make_dir = BashOperator(
        task_id="mkdir",
        bash_command="mkdir -p ../{{ds}}"
    )

    data_generation = PythonVirtualenvOperator(
        python_callable=generate_data,
        op_args=["{{ds}}"],
        task_id="generate_data",
        requirements=["pandas", "pydantic"]
    )

    upload_s3 = PythonVirtualenvOperator(
        task_id="upload_data",
        python_callable=upload_data,
        op_args=["{{ds}}", s3_server, data_bucket],
        requirements=["minio"]
    )

    make_dir >> data_generation >> upload_s3