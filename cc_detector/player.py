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

<<<<<<< HEAD
#df_players = pd.DataFrame(player_dict)


def players_id_list(input_df):
    #extract black and white columns
    players_id = set_players_id_df()
    black = list(input_df["Black"]) 
    white = list(input_df["White"])
    
    #merge uniqe values from both columns:
    bw_merged = pd.DataFrame(list(set(black + white)), columns=["Players"])
    
    # Player_ID filled with NaNs:
    players_id = players_id.merge(bw_merged, how="outer", left_on=["Players"], right_on=["Players"])
    
    # NaNs replaced with generated IDs
    nans_to_ids = players_id["Player_ID"].fillna(players_id["Player_ID"].apply(id_generator))
    
    #inserting missing IDs to players_id
    players_id["Player_ID"] = nans_to_ids
    
    computer = finding_comp(input_df)
    players_id = players_id.merge(computer, left_on='Players', right_on='Computer', how='outer')
    players_id = players_id.replace(np.nan, 'No')
    players_id.drop(columns='Computer', inplace=True)
    players_id.rename(columns={'Yes' : 'Computer'}, inplace=True)
    
    return players_id
=======

>>>>>>> master
