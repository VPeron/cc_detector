from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    # if df == 'players':
    #     players = player_df['White'].unique()
    #     return  {'players': list(players)}
    # if df == 'games':
    #     games = game_df['Game_ID']
    #     return  {'games': list(games)}
    # if df == 'moves':
    #     moves = [move for move in move_df['FEN_moves']]
    #     return  {'players': moves}
    # else:
    #     return{'result': 'No results'}
    players = player_df.to_dict()
    games = game_df.to_dict()
    moves = move_df.to_dict()
    return {
        'players':players,
        'games':games,
        'moves':moves
    }
