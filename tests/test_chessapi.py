from api import chessapi

dfs = chessapi.data()


def test_data():
    assert len(dfs['players']) == 5
    assert len(dfs['games']) == 8