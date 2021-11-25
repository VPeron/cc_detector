from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cc_detector.data import ChessData
import pandas as pd
import joblib
from google.cloud import storage


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# define a root `/` endpoint
@app.get("/")
def index():
    return {"OK": True}


@app.get("/data")
def data():
    chessdata = ChessData()
    player_df, game_df, move_df = chessdata.data_df_maker(source='gcp')
    players = player_df.to_dict()
    games = game_df.to_dict()
    moves = move_df.to_dict()
    return {
        'players':players,
        'games':games,
        'moves':moves
    }

@app.get("/predict")
def predict():
    return {'predictions': 'this will eventually work'}
#     file_df = '?'
#     #TODO front end reads file sends stringIO to API
#     #TODO turns stringIO into pgn object
#     #TODO transforms into move_df
#     X_pred_DataFrame = pd.DataFrame(move_df)

#    rtp_input(source="input", white=True, **kwargs)


#     return {'prediction': prediction[0]}
#TODO return model#s prediction
# collect prediction from GCP model -> needs training process pipelined?
# https://kitt.lewagon.com/camps/673/lectures/content/07-Data-Engineering_02.html
