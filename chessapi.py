from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cc_detector.data import ChessData
from cc_detector.predict import rtp_input
# from google.cloud import storage
import chess.pgn

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


# @app.get("/data")
# def data():
#     chessdata = ChessData()
#     player_df, game_df, move_df = chessdata.import_data(source='gcp')
#     players = player_df.to_dict()   
#     games = game_df.to_dict()
#     moves = move_df.to_dict()
#     return {
#         'players':players,
#         'games':games,
#         'moves':moves
#     }

    
@app.get("/predict")
def predict(file_str):
    
    prediction = rtp_input(source="input", white=True, pgn=file_str)
   
    return {'predictions': prediction}
