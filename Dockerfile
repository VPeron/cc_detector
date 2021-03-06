FROM python:3.8.6-buster

# trained model
# COPY model.joblib model.joblib

# code that loads model
COPY cc_detector/ cc_detector/

# API code
COPY chessapi.py /chessapi.py

COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt update && apt install -y stockfish && rm -rf /var/lib/apt/lists/*

CMD uvicorn chessapi:app --host 0.0.0.0 --port $PORT
