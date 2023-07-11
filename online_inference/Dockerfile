FROM python:3.11

WORKDIR /online_inference

RUN mkdir -p /online_inference/data
RUN mkdir -p /online_inference/src

RUN pip3 install --upgrade pip setuptools wheel

COPY model_trining.py model_trining.py 
COPY app.py app.py
COPY requirements-dev.txt requirements-dev.txt
COPY requirements.txt requirements.txt
COPY data_model.py src/data_model.py
COPY constants.py src/constants.py
COPY model.py src/model.py
COPY model.pkl model.pkl
COPY __init__.py src/__init__.py
COPY loan_sanction_train.csv data/loan_sanction_train.csv 
COPY setup.cfg setup.cfg

RUN pip3 install -r requirements-dev.txt

EXPOSE 8090/tcp

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8090"]
