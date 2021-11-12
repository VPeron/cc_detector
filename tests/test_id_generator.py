import numpy as np
import pandas as pd

from cc_detector.ids_generator import players_id_df

def test_players_id_df():
    df_dummy = pd.DataFrame({'White' : ["12345", 'DummyName', "1234", "forlat", "Geforce"],
    "Black" : ['DummyName', "12345", "Dummy", "Geforce", "Bambi"]})
    players_id = pd.DataFrame({'Players': [], 'Player_ID' : []})
    players_id_df(df_dummy, players_id)
    assert len(players_id.index) == len(np.unique(players_id))