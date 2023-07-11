import pickle

import pandas as pd
from sklearn.pipeline import Pipeline
from typing import List
from .data_model import PredictionRow


class PredictionModel:
    def __init__(self, path_to_file: str) -> None:
        with open("model.pkl", "rb") as f:
            self.model: Pipeline = pickle.load(f)

    def predict(self, data_model: List[PredictionRow]) -> List:
        data = []
        for i in data_model:
            data.append(pd.Series(i))
        return self.model.predict(pd.DataFrame(data))