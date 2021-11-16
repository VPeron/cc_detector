import pandas as pd
import numpy as np

from cc_detector.data import ChessData
from cc_detector.ids_generator import game_id, player_id, players_id_df, players_id_list, set_players_id_df
from cc_detector.player import set_players_id_df, finding_comp

dummy_players_id_df = pd.DataFrame({'White' : ["12345", 'DummyName', "1234", "forlat", "Geforce"],
"Black" : ['DummyName', "12345", "Dummy", "Geforce", "Bambi"]})

def test_players_id_list():
    '''checks if the length of df equals the number of unique IDs '''
    df_players, df_games, df_moves = ChessData().import_data()
    players_id = set_players_id_df()
    assert df_players.shape[0] == len(df_players["Player_ID"].unique())
    assert players_id.isnull().values.any() == 0