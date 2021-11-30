from numpy.core.numeric import True_
import chessapi


def test_index():
    status = chessapi.index()
    assert status['OK'] == True

# def test_data():
#     dfs = chessapi.data()
#     assert len(dfs['players']) == 5
#     assert len(dfs['games']) == 8
#