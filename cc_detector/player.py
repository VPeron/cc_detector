import pandas as pd
import numpy as np


from cc_detector.ids_generator import id_generator, finding_comp


def set_player_dict():
    player_dict = {
        'Player_ID' : [],
        'White': [],
        'Black': [],
        'WhiteIsComp': [],
    }

    return player_dict

def set_players_id_df():
    players_id = pd.DataFrame({'Players': [], 'Player_ID' : []})
    return players_id

def player_info_extractor(game, player_dict):
    '''
    Takes a game from chess library (parsed pgn) and a structure
    of an empty dictionary
    '''
    new_player_id = 'ToDo'
    # Player
    player_dict['Player_ID'].append(new_player_id)


    player_dict['White'].append(game.headers['White'])
    player_dict['Black'].append(game.headers['Black'])
    player_dict['WhiteIsComp'].append(game.headers.get('WhiteIsComp', 'No'))

    return player_dict


