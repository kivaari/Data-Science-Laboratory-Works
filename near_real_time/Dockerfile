FROM python:3.10-slim-buster

WORKDIR /near_real_time

RUN mkdir -p /online_inference/src

RUN pip3 install --upgrade pip setuptools wheel

COPY model.pkl model.pkl
COPY producer.py producer.py
COPY consumer.py consumer.py
COPY requirements.txt requirements.txt
COPY .env .env
COPY src/__init__.py src/__init__.py
COPY src/data_model.py src/data_model.py
COPY src/model.py src/model.py
COPY src/constants.py src/constants.py

RUN pip3 install -r requirements.txt

ADD . /near_real_time