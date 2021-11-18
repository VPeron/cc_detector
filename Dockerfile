FROM python:3.8.6-buster

# trained model
# COPY model.joblib model.joblib

# code that loads model
# COPY cc_detector/ cc_detector/

# API code
# COPY api/chessapi.py api/chessapi.py

# credentials
# COPY /home/vini/code/VPeron/GCP/<gcp project> ex: wagon-bootcamp-329012-dd7383abde50.json /crentials.json
# see TFM_PredictInProd/Dockerfile <- delete line for ex only

COPY app /app
COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD uvicorn app.chessapi:app --host 0.0.0.0 
