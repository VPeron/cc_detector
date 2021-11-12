from cc_detector.ids_generator import players_id_df

def test_players_id_df():
    res = players_id_df()
    assert res.shape() == (2,)
    