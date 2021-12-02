#from cc_detector.ids_generator import game_id


def set_game_dict():
    game_dict = {
        'Game_ID': [],
        'Date' : [],
        'White':[],  # Dummy ID
        'White_Elo': [],
        'Black': [],  # Dummy ID
        'Black_Elo': [],
        'ECO': [],
        'Result': []
        }
    return game_dict


def game_info_extractor(game, game_dict, game_counter):
    if 'FICSGamesDBGameNo' in game.headers:
        game_dict['Game_ID'].append(game.headers['FICSGamesDBGameNo'])
    else:
        game_dict['Game_ID'].append(f"game_{game_counter}")
    game_dict['White'].append(game.headers['White'])  # dummy ID
    game_dict['Black'].append(game.headers['Black'])  # dummy ID
    game_dict['White_Elo'].append(game.headers['WhiteElo'])
    game_dict['Black_Elo'].append(game.headers['BlackElo'])
    if 'ECO' in game.headers:
        game_dict['ECO'].append(game.headers['ECO'])
    else:
        game_dict['ECO'].append("NA")
    game_dict['Result'].append(game.headers['Result'])
    game_dict['Date'].append(game.headers['Date'])

    return game_dict
