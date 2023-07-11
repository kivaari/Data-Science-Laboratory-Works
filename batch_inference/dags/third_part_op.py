from datetime import timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonVirtualenvOperator
from airflow.utils.dates import days_ago

s3_server = Variable.get("s3_server")
data_bucket = Variable.get("data_bucket")
artifact_bucket = Variable.get("artifact_bucket")
result_bucket = Variable.get("result_bucket")


def data_from_s3(input_dir, s3_server, data_bucket):
    from minio import Minio
    import os
    from pathlib import Path

    file_name = "generated_data.csv"

    client = Minio(
        s3_server, 
        secure=False, 
        access_key="miniouser", 
        secret_key="miniouser"
    )
    content = client.get_object(
        bucket_name=data_bucket, 
        object_name=file_name
    )

    file_path = os.path.join(f"{input_dir}", "generated_data_from_s3.csv")
    with open(file_path, "wb") as gdfs3:
        gdfs3.write(content.data)

def artifact_from_s3(input_dir, s3_server, artifact_bucket):
    from minio import Minio
    import os
    from pathlib import Path

    pickle_name = "model.pkl"

    client = Minio(
        s3_server, 
        secure=False, 
        access_key="miniouser", 
        secret_key="miniouser"
    )
    content = client.get_object(
        bucket_name=artifact_bucket, 
        object_name=pickle_name
    )

    pickle_path = os.path.join(f"{input_dir}", "model_from_s3.pkl")
    with open(pickle_path, "wb") as mfs3:
        mfs3.write(content.data)


def predict_result(input_dir):
    import os
    from pathlib import Path
    import pickle
    import pandas as pd
    from sklearn.pipeline import Pipeline
    from typing import List
    from src.data_model import PredictionRow

    class PredictionModel:
        def __init__(self, path_to_file: str) -> None:
            pickle_path = os.path.join(f"{input_dir}", "model_from_s3.pkl")
            with open(pickle_path, "rb") as f:
                self.model: Pipeline = pickle.load(f)

        def predict(self, data_model: List[PredictionRow]) -> List:
            data = pd.DataFrame(data_model)
            return self.model.predict(data)

    pickle_path = os.path.join(f"{input_dir}", "model_from_s3.pkl")
    file_path = os.path.join(f"{input_dir}", "generated_data_from_s3.csv")

    prediction_model = PredictionModel(pickle_path)
    
    df = pd.read_csv(file_path)
    predictions = prediction_model.predict(df)

    predictions_file_path = os.path.join(f"{input_dir}", "predictions.txt")
    with open(predictions_file_path, "w") as pred:
        pred.write(str(predictions))


def upload_predictions_to_s3(input_dir, s3_server, result_bucket):
    import os
    from minio import Minio
    from pathlib import Path

    predictions_file_path = os.path.join(f"{input_dir}", "predictions.txt")
    predictions_file_size = os.path.getsize(predictions_file_path)

    with open(predictions_file_path, "rb") as prdct:
        client = Minio(
            s3_server,
            secure=False,
            access_key="miniouser",
            secret_key="miniouser",
        )
        content = client.put_object(
            bucket_name=result_bucket,
            object_name="predictions.txt",
            data=prdct,
            length=predictions_file_size,
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
    "download_predict_upload", 
    default_args=default_args, 
    schedule_interval=None, 
    start_date=days_ago(1)
):
    data_from_s3 = PythonVirtualenvOperator(
        task_id="data_from_s3", 
        python_callable=data_from_s3,
        op_args=["{{ds}}", s3_server, data_bucket],
        requirements=["minio"]
    )

    artifact_from_s3 = PythonVirtualenvOperator(
        task_id="artifact_from_s3", 
        python_callable=artifact_from_s3,
        op_args=["{{ds}}", s3_server, artifact_bucket],
        requirements=["minio"]
    )

    predict_data = PythonVirtualenvOperator(
        task_id="predict",
        python_callable=predict_result,
        op_args=["{{ds}}"]
    )

    result_to_s3 = PythonVirtualenvOperator(
        task_id="upload_predictions_to_s3", 
        python_callable=upload_predictions_to_s3,
        op_args=["{{ds}}", s3_server, result_bucket],
        requirements=["minio"]
    )

    data_from_s3 >> artifact_from_s3 >> predict_data >> result_to_s3