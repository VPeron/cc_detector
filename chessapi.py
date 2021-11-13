from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# import chess.pgn
from cc_detector.data import ChessData



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


@app.get("/predict")
def test_epoint():
    chessdata = ChessData()
    player_df, game_df, move_df = chessdata.import_data(data_path='raw_data/Fics_data_pc_data.pgn', 
                                                              import_lim=50)
    data = {
        'players': len(player_df),
        'games': len(game_df),
        'moves': len(move_df)
    }
    return {'df_games_len': data}
