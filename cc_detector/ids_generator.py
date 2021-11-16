import pandas as pd
import numpy as np
import uuid
import shortuuid


def id_generator(id):
    '''generates unique IDs, 32 integers'''
    return uuid.uuid4().int

def short_id_gen(id):
    '''generates unique IDs, string with 15 characters'''
    return shortuuid.ShortUUID().random(length=15)


# for df_players - a df consisting unique player names and ID's
players_id = pd.DataFrame({'Players': [], 'Player_ID' : []})

def finding_comp(df_players):
    ''' taking all players from df_players, who are computer'''
    # checking the White column for computers
    comp1 = df_players.loc[df_players['WhiteIsComp'] == "Yes"]
    comp1 = comp1[['White']].copy()
    comp1.drop_duplicates(inplace=True)

    #checking the black column for computers
    comp2 = df_players.loc[df_players['WhiteIsComp'] == "No"]
    comp2 = comp2[['Black']].copy()
    comp2.drop_duplicates(inplace=True)
    
    # merge and get the unique names
    c1 = list(comp1['White'])
    c2 = list(comp2['Black'])
    computer = list(set(c1 + c2))
    
    computer = pd.DataFrame({'Computer' : computer})
    computer['Yes'] = 'Yes'
    
    # returns a df with computer names
    return computer

def players_id_df(input_df, players_id):
    '''generates list with unique player names and IDs to merge with df_players'''
    #extract black and white columns
    black = list(input_df["Black"]) 
    white = list(input_df["White"])
    
    #merge uniqe values from both columns:
    bw_merged = pd.DataFrame(list(set(black + white)), columns=["Players"])
    
    # Player_ID column filled with NaNs:
    players_id = players_id.merge(bw_merged, how="outer", left_on=["Players"], right_on=["Players"])
    
    # NaNs replaced with generated IDs
    nans_to_ids = players_id["Player_ID"].fillna(players_id["Player_ID"].apply(id_generator))
    
    #inserting missing IDs to players_id
    players_id["Player_ID"] = nans_to_ids

    #finding computers in df
    computer = finding_comp()

    #merging df on unique names
    players_id = players_id.merge(computer, left_on='Players', right_on='Computer', how='outer')
    players_id = players_id.replace(np.nan, 'No')
    players_id.drop(columns='Computer', inplace=True)
    players_id.rename(columns={'Yes' : 'Computer'}, inplace=True)

    return players_id


def player_id(df_players): 
    '''returns a df with 2 new columns and assigns IDs to the player'''
    # merging input_df on white column with players_id
    m_white = df_players.merge(players_id, left_on=["White"], right_on=['Players'])   #
    m_white['White_ID'] = m_white['Player_ID']
    m_white.drop(columns=['Players', "Player_ID"], inplace=True)

    # merging input_df on black column with players_id
    m_bw = m_white.merge(players_id, left_on=["Black"], right_on=['Players']).astype(object)
    m_bw['Black_ID'] = m_bw['Player_ID']
    m_bw.drop(columns=['Players', "Player_ID"], inplace=True)
    df_players = m_bw
    return df_players


def game_id(df_games):
    '''generates ids for games'''
    df_games["old_ID"] = df_games["Game_ID"]
    df_games['Game_ID'] = df_games['Game_ID'].apply(short_id_gen)
    
    # adding players ids
    # df_games = df_games.merge(players_id, left_on='White', right_on='Players')
    # df_games = df_games.merge(players_id, left_on='Black', right_on='Players')
    # df_games.drop(columns=['Players_x', 'Players_y'], inplace=True) #optionally drop White, Black columns
    # df_games.rename(columns = {'Game_ID_y' : 'Game_ID', 'Player_ID_x': 'White_ID', 'Player_ID_y': 'Black_ID'}, inplace=True)
    
    return df_games

def move_id(df_moves, df_games):
    '''generates ids for each move'''
    # create reference df for merging on Game_ID
    data = [df_games["Game_ID"], df_games["old_ID"]]
    headers = ["Game_ID", "old_ID"]
    df = pd.concat(data, axis=1, keys=headers)

    # merging df with df_moves to insert new ids
    merging = df_moves.merge(df, how="left", left_on="Game_ID", right_on="old_ID")

    # dropping and renaming columns
    merging.drop(columns=["Game_ID_x", "old_ID"], inplace=True)
    merging.rename(columns = {'Game_ID_y' : 'Game_ID'}, inplace = True)

    # creating new column with move ids and placing it on the beginning of df
    merging.insert(0, "Moves_ID", merging.apply(lambda row: f"{row.Game_ID }-{row.turn}-{row.Halfmove_clock}", axis=1))
    df_moves = merging
    return df_moves


def find_and_replace_duplicates(df, subset):
    while True:
        if df.duplicated(subset=subset, keep=False).any() == True:
            is_dup = df.duplicated(subset=subset, keep="first")
            if subset == 'Game_ID':
                df[subset] = df[subset].where(~is_dup, df[subset].apply(short_id_gen))
            return df
            df[subset] = df[subset].where(~is_dup, df[subset].apply(id_generator))
        else: print(f'\u2713 no duplicates in {subset}s')
        break