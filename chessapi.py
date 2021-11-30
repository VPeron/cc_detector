import chess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cc_detector.predict import rtp_input
from cc_detector.data import ChessData
from cc_detector.predict import rtp_input
import pandas as pd
from google.cloud import storage
import chess.pgn
from pydantic import BaseModel

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


class Item(BaseModel):
    Bitmap_moves: list
    Game_ID: list
    FEN_moves: list
    WhiteIsComp: list
    turn: list
    Castling_right: list
    EP_option: list
    Pseudo_EP_option: list
    Halfmove_clock: list
    Evaluation: list
    Player_color: str

@app.post("/predict")
def predict(request: Item):
    # Bitmap_moves: list = Query([]),
    # Game_ID: list = Query([]),
    # FEN_moves: list = Query([]),
    # WhiteIsComp: list = Query([]),
    # turn: list = Query([]),
    # Castling_right: list = Query([]),
    # EP_option: list = Query([]),
    # Pseudo_EP_option: list = Query([]),
    # Halfmove_clock: list = Query([])):

    chessdata = ChessData()

    Bitmap_moves_mod = []
    for move in request.Bitmap_moves:
        move = move[:-1]
        Bitmap_move_temp = move.split("-")
        Bitmap_move_temp = [int(x) for x in Bitmap_move_temp]
        Bitmap_moves_mod.append(Bitmap_move_temp)

    move_dict = {
        'Game_ID': request.Game_ID,
        "FEN_moves": request.FEN_moves,
        "Bitmap_moves": Bitmap_moves_mod,
        "WhiteIsComp": request.WhiteIsComp,
        "turn": request.turn,
        "Castling_right": request.Castling_right,
        "EP_option": request.EP_option,
        "Pseudo_EP_option": request.Pseudo_EP_option,
        "Halfmove_clock": request.Halfmove_clock,
        "Evaluation": request.Evaluation
    }

    player_color = request.Player_color
    if player_color=="White":
        white=True
    else:
        white=False

    move_df = chessdata.data_df_maker(api=True, input_dict=move_dict)

    prediction = rtp_input(move_df, source="gcp", white=white)

    return {'prediction': str(prediction)}
