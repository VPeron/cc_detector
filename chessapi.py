import chess
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from cc_detector.predict import rtp_input
from cc_detector.data import ChessData
from cc_detector.predict import rtp_input
import pandas as pd
from google.cloud import storage
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
def predict(Bitmap_moves: list = Query([]),
            Game_ID: list = Query([]),
            FEN_moves: list = Query([]),
            WhiteIsComp: list = Query([]),
            turn: list = Query([]),
            Castling_right: list = Query([]),
            EP_option: list = Query([]),
            Pseudo_EP_option: list = Query([]),
            Halfmove_clock: list = Query([])):

    chessdata = ChessData()

    Bitmap_moves_mod = []
    for move in Bitmap_moves:
        move = move[:-1]
        Bitmap_move_temp = move.split("-")
        Bitmap_move_temp = [int(x) for x in Bitmap_move_temp]
        Bitmap_moves_mod.append(Bitmap_move_temp)

    move_dict = {
        'Game_ID': Game_ID,
        "FEN_moves": FEN_moves,
        "Bitmap_moves": Bitmap_moves_mod,
        "WhiteIsComp": WhiteIsComp,
        "turn": turn,
        "Castling_right": Castling_right,
        "EP_option": EP_option,
        "Pseudo_EP_option": Pseudo_EP_option,
        "Halfmove_clock": Halfmove_clock
    }

    move_df = chessdata.data_df_maker(api=True, input_dict=move_dict)

    prediction = rtp_input(move_df, source="gcp", white=True)

    return {'prediction': str(prediction)}

