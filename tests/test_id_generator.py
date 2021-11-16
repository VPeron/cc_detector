import pandas as pd
import numpy as np

from cc_detector import data
from cc_detector.ids_generator import game_id, player_id, players_id_df

dummy_players_id_df = pd.DataFrame({'White' : ["12345", 'DummyName', "1234", "forlat", "Geforce"],
"Black" : ['DummyName', "12345", "Dummy", "Geforce", "Bambi"]})

def test_players_id_df():
    '''checks if the lenght of '''
    
    players_id = pd.DataFrame({'Players': [], 'Player_ID' : []})
    players_id_df(df_players, players_id)
    assert players_id.shape[0] == len(players_id["Player_ID"].unique())
    assert players_id.isnull().values.any() == 0

def test_player_id():
    new_df = player_id(df_players)
    #new_df_dic = new_df.to_dict()
    assert df_players.isnull().values.any() == 0
    assert df_players != new_df
    #assert 'White_ID' and 'Black_ID' in new_df_dic.keys()

# def test_game_id():
#     '''checks if the shape of new df'''
#     games = game_id(df_games)
#     #games_dict = games.to_dict()
#     assert df_games.shape[1] != games.shape[1]
#     #assert 'Game_ID' and 'old_ID' in games_dict.keys()

# def test_move_id():
#     #Game_ID value is in Move_ID
#     data = [df_games["Game_ID"], df_games["old_ID"]]
#     headers = ["Game_ID", "old_ID"]
#     df = pd.concat(data, axis=1, keys=headers)
