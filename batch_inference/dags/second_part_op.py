from datetime import timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonVirtualenvOperator
from airflow.utils.dates import days_ago

s3_server = Variable.get("s3_server")
train_bucket = Variable.get("train_bucket")
artifact_bucket = Variable.get("artifact_bucket")
metrics_bucket = Variable.get("metrics_bucket")


def upload_data(input_dir, s3_server, train_bucket):
    from minio import Minio
    import os
    from pathlib import Path

    file_name = "loan_train.csv"

    client = Minio(
        s3_server, 
        secure=False, 
        access_key="miniouser", 
        secret_key="miniouser"
    )
    content = client.get_object(
        bucket_name=train_bucket, 
        object_name=file_name
    )

    file_path = os.path.join(f"{input_dir}", "loan_train.csv")
    with open(file_path, "wb") as fio:
        fio.write(content.data)


def load_data_and_train(input_dir):
    import pickle
    import os
    import pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import (LabelEncoder, OneHotEncoder,
                                       StandardScaler)
    from pathlib import Path

    file_path = os.path.join(f"{input_dir}", "loan_train.csv")

    TARGET_COL = "Status"
    COLUMNS = [
        "Gender", 
        "Married", 
        "Dependents", 
        "Education", 
        "Self_Employed", 
        "Applicant_Income", 
        "Coapplicant_Income", 
        "Loan_Amount", "Term", 
        "Credit_History", 
        "Area", 
        "Status"
    ]
    REAL_COLS = [
        "Applicant_Income", 
        "Coapplicant_Income", 
        "Loan_Amount", 
        "Term", 
        "Credit_History"
    ]
    CAT_COLS = [
        "Gender", 
        "Married", 
        "Education", 
        "Self_Employed", 
        "Area", 
        "Dependents"
    ]

    TEST_SIZE = 0.2
    RANDOM_STATE = 42

    df = pd.read_csv(file_path)
    df = df.loc[:, COLUMNS]
    df.dropna(inplace=True)
    X = df.drop(TARGET_COL, axis=1)
    y = df[TARGET_COL]

    train_X, test_X, train_y, test_y = train_test_split(
        X, 
        y, 
        test_size=TEST_SIZE, 
        random_state=RANDOM_STATE
    )

    transforms = ColumnTransformer([
        ("ss", StandardScaler(), REAL_COLS),
        ("ohe", OneHotEncoder(), CAT_COLS)
    ])

    pipeline = Pipeline([
        ("transforms", transforms),
        ("model", LogisticRegression())
    ])

    pipeline.fit(train_X, train_y)
    pred = pipeline.predict(test_X)
    f1_score_value = f1_score(test_y, pred, pos_label="Y")

    # дамп артифакта
    pickle_file_path = os.path.join(f"{input_dir}", "model.pkl")
    with open(pickle_file_path, "wb") as f:
        pickle.dump(pipeline, f)

    # сохранение метрик в f1_score.txt для загрузки
    f1_file_path = os.path.join(f"{input_dir}", "f1_score.txt")
    with open(f1_file_path, "w") as f1:
        f1.write(str(f1_score_value))


def upload_artifact_to_s3(input_dir, s3_server, artifact_bucket):
    import os
    from minio import Minio
    from pathlib import Path

    pickle_file_path = os.path.join(f"{input_dir}", "model.pkl")
    pickle_file_size = os.path.getsize(pickle_file_path)

    with open(pickle_file_path, "rb") as artifact:
        client = Minio(
            s3_server,
            secure=False,
            access_key="miniouser",
            secret_key="miniouser",
        )
        content = client.put_object(
            bucket_name=artifact_bucket,
            object_name="model.pkl",
            data=artifact,
            length=pickle_file_size,
        )


def upload_metrics_to_s3(input_dir, s3_server, metrics_bucket):
    import os
    from minio import Minio
    from pathlib import Path

    metrics_file_path = os.path.join(f"{input_dir}", "f1_score.txt")
    metrics_file_size = os.path.getsize(metrics_file_path)

    with open(metrics_file_path, "rb") as metrics:
        client = Minio(
            s3_server,
            secure=False,
            access_key="miniouser",
            secret_key="miniouser",
        )
        content = client.put_object(
            bucket_name=metrics_bucket,
            object_name="f1_score.txt",
            data=metrics,
            length=metrics_file_size,
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
    "download_train_upload", 
    default_args=default_args, 
    schedule_interval=None, 
    start_date=days_ago(1)
):
    download_from_s3 = PythonVirtualenvOperator(
        task_id="upload_data_from_s3", 
        python_callable=upload_data,
        op_args=["{{ds}}", s3_server, train_bucket],
        requirements=["minio"]
    )

    model_training = PythonVirtualenvOperator(
        task_id="training",
        python_callable=load_data_and_train,
        op_args=["{{ds}}"],
        requirements=["pandas", "scikit-learn"]
    )

    upload_artifact = PythonVirtualenvOperator(
        task_id="upload_artifact", 
        python_callable=upload_artifact_to_s3,
        op_args=["{{ds}}", s3_server, artifact_bucket],
        requirements=["minio"]
    )

    upload_metrics = PythonVirtualenvOperator(
        task_id="upload_metrics", 
        python_callable=upload_metrics_to_s3,
        op_args=["{{ds}}", s3_server, metrics_bucket],
        requirements=["minio"]
    )

    download_from_s3 >> model_training >> upload_artifact >> upload_metrics