import pickle

import pandas as pd
from sklearn.pipeline import Pipeline

from .constants import APPROVAL_LABEL, APPROVED_NAME, NON_APPROVED_NAME
from .data_model import PredictionRow


class PredictionModel:

    def __init__(self, path_to_file: str) -> None:
        with open(r"C:/Users/kivaari/Desktop/sss/mlops/online_inference/model.pkl", "rb") as f:
            self.model: Pipeline = pickle.load(f)

    def predict(self, data_model: PredictionRow) -> str:
        prediction_row = data_model.dict()
        series = pd.Series(prediction_row)
        df = pd.DataFrame(data=[series])
        prediction = self.model.predict(df)
        return APPROVED_NAME if prediction[0] == APPROVAL_LABEL else NON_APPROVED_NAME
