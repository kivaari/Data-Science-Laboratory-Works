from os import environ
import json
import time
import pickle
import uuid
import numpy as np
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from src.model import PredictionModel
from src.data_model import PredictionRow
from src.constants import MODEL_NAME
from dotenv import load_dotenv

load_dotenv()

SERVER = environ.get("SERVER")
OFFSET = environ.get("OFFSET")
GROUPID = environ.get("GROUPID")
CONSUMER_TIMEOUT = 2000

prediction_model = PredictionModel(MODEL_NAME)

producer = KafkaProducer(
    bootstrap_servers=SERVER,
    key_serializer=lambda x: str(x).encode("utf8"),
    value_serializer=lambda x: json.dumps(x).encode("utf8")
)

consumer = KafkaConsumer(
    "mltopic",
    bootstrap_servers=SERVER, 
    group_id=GROUPID,
    auto_offset_reset=OFFSET,
    consumer_timeout_ms=CONSUMER_TIMEOUT,
    value_deserializer=lambda x: PredictionRow.parse_raw(x.decode('utf8'))
)

BATCH_SIZE = 5

while True:
    batch = []

    try:
        for _ in range(BATCH_SIZE):
            message = next(consumer)
            value = message.value
            batch.append(value)
            print(value)
    except StopIteration:
        pass

    if len(batch) > 0:
        data = [i.dict() for i in batch]
        y_pred = prediction_model.predict(data)

        for i, prediction_row in enumerate(batch):
            prediction_raw = {
                "prediction": y_pred[i],
                **prediction_row.dict()
            }
            producer.send('predtopic', key=uuid.uuid4(), value=prediction_raw)

        consumer.commit()