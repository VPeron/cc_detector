
def set_player_dict():
    player_dict = {
        'White': [],
        'White_Elo': [],
        'Black': [],
        'Black_Elo': [],
        'WhiteIsComp': [],
    }
    return player_dict

def player_info_extractor(game, player_dict):
    '''
    Takes a game from chess library (parsed pgn) and a structure
    of an empty dictionary
    '''

    # Player
    player_dict['White_Elo'].append(game.headers['WhiteElo'])
    player_dict['Black_Elo'].append(game.headers['BlackElo'])
    player_dict['White'].append(game.headers['White'])
    player_dict['Black'].append(game.headers['Black'])
    player_dict['WhiteIsComp'].append(game.headers.get('WhiteIsComp', 'No'))

    return player_dict
