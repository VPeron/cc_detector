import pandas as pd
import numpy as np
import uuid 

def id_generator(id):
    '''generates unique IDs'''
    return uuid.uuid4().int


# for df_players
players_id = pd.DataFrame({'Players': [], 'Player_ID' : []})


def players_id_list(input_df, players_id):
    '''generates list with player names and IDs'''
    #extract black and white columns
    black = list(input_df["Black"]) 
    white = list(input_df["White"])
    
    #merge uniqe values from both columns:
    bw_merged = pd.DataFrame(list(set(black + white)), columns=["Players"])
    
    # Player_ID columns filled with NaNs:
    players_id = players_id.merge(bw_merged, how="outer", left_on=["Players"], right_on=["Players"])
    
    # NaNs replaced with generated IDs
    nans_to_ids = players_id["Player_ID"].fillna(players_id["Player_ID"].apply(id_generator))
    
    #inserting missing IDs to players_id
    players_id["Player_ID"] = nans_to_ids 
    return players_id


def assign_player_id(input_df): 
    '''returns a df with 2 new columns and assigns IDs to the player'''
    # merging on white column with player_id
    m_white = input_df.merge(players_id, left_on=["White"], right_on=['Players'])   #
    m_white['White_ID'] = m_white['Player_ID']
    m_white.drop(columns=['Players', "Player_ID"], inplace=True)

    # merging on black column with player_id
    m_bw = m_white.merge(players_id, left_on=["Black"], right_on=['Players'])
    m_bw['Black_ID'] = m_bw['Player_ID']
    m_bw.drop(columns=['Players', "Player_ID"], inplace=True)
    df_players = m_bw
    return df_players



def game_id(input_df):
    '''generates IDs for df_games'''
    input_df['Game_ID'] = input_df['Game_ID'].apply(id_generator)
    return input_df

