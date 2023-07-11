import pickle

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.constants import MODEL_NAME

COLUMNS = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", "Credit_History", "Property_Area", "Loan_Status"]  # noqa: E501
REAL_COLS = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", "Credit_History"]
CAT_COLS = ["Gender", "Married", "Education", "Self_Employed", "Property_Area", "Dependents"]
TARGET_COL = "Loan_Status"

TEST_SIZE = 0.2
RANDOM_STATE = 42

df = pd.read_csv("data/loan_sanction_train.csv")
df = df.loc[:, COLUMNS]
df.dropna(inplace=True)
X = df.drop(TARGET_COL, axis=1)
y = df[TARGET_COL]

train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)

transforms = ColumnTransformer([
    ("ss", StandardScaler(), REAL_COLS),
    ("ohe", OneHotEncoder(), CAT_COLS),
])

pipeline = Pipeline([
    ("transforms", transforms),
    ("model", LogisticRegression())
])

pipeline.fit(train_X, train_y)
pred = pipeline.predict(test_X)
print(f1_score(test_y, pred, pos_label="Y"))  # noqa: T201

with open(MODEL_NAME, "wb") as f:
    pickle.dump(pipeline, f)
