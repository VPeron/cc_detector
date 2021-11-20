FROM python:3.8.6-buster


# code that loads model
COPY cc_detector/ cc_detector/
# API code
COPY chessapi.py chessapi.py
# trained model
# COPY model.joblib model.joblib
COPY requirements.txt /requirements.txt

# credentials
# COPY /home/vini/code/VPeron/GCP/<gcp project> ex: wagon-bootcamp-329012-dd7383abde50.json /crentials.json
# see TFM_PredictInProd/Dockerfile <- delete line for ex only

COPY ccdetectorproject-e3fc70984fb0.json /credentials.json

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD uvicorn chessapi:app --host 0.0.0.0
