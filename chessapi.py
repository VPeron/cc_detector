import chess
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from cc_detector.predict import rtp_input
from cc_detector.data import ChessData
import pandas as pd
import joblib
from pydantic import BaseModel, Json
from google.cloud import storage
from typing import Dict, List, Optional
import json


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

class Squares(BaseModel):
    s0: int
    s1: int
    s2: int
    s3: int
    s4: int
    s5: int
    s6: int
    s7: int
    s8: int
    s9: int
    s10: int
    s11: int
    s12: int
    s13: int
    s14: int
    s15: int
    s16: int
    s17: int
    s18: int
    s19: int
    s20: int
    s21: int
    s22: int
    s23: int
    s24: int
    s25: int
    s26: int
    s27: int
    s28: int
    s29: int
    s30: int
    s31: int
    s32: int
    s33: int
    s34: int
    s35: int
    s36: int
    s37: int
    s38: int
    s39: int
    s40: int
    s41: int
    s42: int
    s43: int
    s44: int
    s45: int
    s46: int
    s47: int
    s48: int
    s49: int
    s50: int
    s51: int
    s52: int
    s53: int
    s54: int
    s55: int
    s56: int
    s57: int
    s58: int
    s59: int
    s60: int
    s61: int
    s62: int
    s63: int

class Pieces(BaseModel):
    K: Json[Squares]
    Q: Json[Squares]
    R: Json[Squares]
    B: Json[Squares]
    N: Json[Squares]
    P: Json[Squares]
    k: Json[Squares]
    q: Json[Squares]
    r: Json[Squares]
    b: Json[Squares]
    n: Json[Squares]
    p: Json[Squares]


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


    # move_df = pd.DataFrame(
    #     dict(Game_ID=[Game_ID],
    #         FEN_moves=[FEN_moves],
    #         Bitmap_moves=[Bitmap_moves],
    #         WhiteIsComp=[WhiteIsComp],
    #         turn=[turn],
    #         Castling_right=[Castling_right],
    #         EP_option=[EP_option],
    #         Pseudo_EP_option=[Pseudo_EP_option],
    #         Halfmove_clock=[Halfmove_clock]))

    move_df = chessdata.data_df_maker(api=True, input_dict=move_dict)

    prediction = rtp_input(move_df, source="gcp", white=True)

    return {'prediction': str(prediction)}


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
