# import os

BUCKET_NAME = 'cc_detector'
BUCKET_TRAIN_DATA_PATH = 'data/ficspcdata.pgn'
MODEL_STORAGE_LOCATION = "models/cc_detect_lstm_model.joblib"
SCALER_STORAGE_LOCATION = "models/minmax_scaler.pkl"
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ccdetectorproject-e3fc70984fb0.json'
#MODEL_NAME = 'LSTM_model'
#MODEL_VERSION = 'v1'
