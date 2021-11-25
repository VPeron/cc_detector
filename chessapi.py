import chess
from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from cc_detector.predict import rtp_input
from cc_detector.data import ChessData
import pandas as pd
import joblib
from google.cloud import storage
from typing import List, Optional
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


# def bitmap_dict(Bitmap_moves: list = Query([])):
#     return list(map(json.loads, Bitmap_moves))


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

    print(Bitmap_moves)

    # move_dict = {
    #     'Game_ID': Game_ID,
    #     "FEN_moves": FEN_moves,
    #     "Bitmap_moves": Bitmap_moves,
    #     "WhiteIsComp": WhiteIsComp,
    #     "turn": turn,
    #     "Castling_right": Castling_right,
    #     "EP_option": EP_option,
    #     "Pseudo_EP_option": Pseudo_EP_option,
    #     "Halfmove_clock": Halfmove_clock
    # }

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

    # move_df = chessdata.data_df_maker(api=True, input_dict=move_dict)
    # prediction = rtp_input(move_df, white=True)

    # return {'prediction': prediction}


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
