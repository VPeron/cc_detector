import pandas as pd
import numpy as np

import chess
import chess.pgn
from stockfish import Stockfish
import os

import uuid        # for id generation
import shortuuid

from cc_detector.ids_generator import game_id, player_id, players_id_df

players = {
    'White':[],
    'White_Elo': [],
    'Black': [],
    'Black_Elo': [],
    'WhiteIsComp':[],
}

games = {
    'Game_ID': [],
    'Date' : [],
    'White':[],  # Dummy ID
    'White_Elo': [],
    'Black': [],  # Dummy ID
    'Black_Elo': [],
    'ECO': [],
    'Result': [],
}

moves_log_dict = {
    'Game_ID': [],
    'FEN_moves': [],
    'Bitmap_moves': [],
    #'cpl': [],
    'WhiteIsComp': [],
    'turn': [],
    'Castling_right': [],
    'EP_option': [],
    'Pseudo_EP_option': [],
    'Halfmove_clock': []
    #'Result': [],
}

# Set list of Pieces
PIECES = [chess.Piece.from_symbol('P'),
         chess.Piece.from_symbol('N'),
         chess.Piece.from_symbol('B'),
         chess.Piece.from_symbol('R'),
         chess.Piece.from_symbol('Q'),
         chess.Piece.from_symbol('K'),
         chess.Piece.from_symbol('p'),
         chess.Piece.from_symbol('n'),
         chess.Piece.from_symbol('b'),
         chess.Piece.from_symbol('r'),
         chess.Piece.from_symbol('q'),
         chess.Piece.from_symbol('k')]

# read file
pgn = open("raw_data/Fics_data_pc_data.pgn", encoding='UTF-8')  # always a Comp vs Player
game_counter = 0

while True:  # keep reading games
    try:
        game = chess.pgn.read_game(pgn)
        board = game.board()
        moves = list(game.mainline_moves())
        
        # Player
        players['White_Elo'].append(game.headers['WhiteElo'])
        players['Black_Elo'].append(game.headers['BlackElo'])
        players['White'].append(game.headers['White'])
        players['Black'].append(game.headers['Black'])
        players['WhiteIsComp'].append(game.headers.get('WhiteIsComp', 'No'))
        
        # Games
        games['Game_ID'].append(game.headers['FICSGamesDBGameNo'])
        games['White'].append(game.headers['White'])  # dummy ID
        games['Black'].append(game.headers['Black'])  # dummy ID
        games['White_Elo'].append(game.headers['WhiteElo'])
        games['Black_Elo'].append(game.headers['BlackElo'])
        games['ECO'].append(game.headers['ECO'])
        games['Result'].append(game.headers['Result'])
        games['Date'].append(game.headers['Date'])
        
        # MOVE CYCLE
        white = True
        for move in moves:
            board.push(move)
            #fen_pos.append(board.fen())
            #stockfish.set_fen_position(board.fen())  # load stockfish with current FEN for eval
            #cpl = stockfish.get_evaluation()['value']/100
            
            moves_log_dict['Game_ID'].append(game.headers['FICSGamesDBGameNo'])
            moves_log_dict['FEN_moves'].append(board.fen())
            
            #Generate bitmap representation of FENs
            bitmap_board_dict = {}
            positions = board.piece_map()

            for piece in PIECES:
                bitmap_board = {}
                for position in positions:
                    if positions[position] == piece: 
                        bitmap_board[position] = 1
                    else:
                        bitmap_board[position] = 0
                bitmap_board_dict[str(piece)] = bitmap_board            
            
            moves_log_dict['Bitmap_moves'].append(bitmap_board_dict)
            
            #moves_log_dict['cpl'].append(cpl)
            
            #Turn color and castling availablity
            moves_log_dict['WhiteIsComp'].append(game.headers.get('WhiteIsComp', 'No'))
            if white:
                moves_log_dict['turn'].append('white')
                moves_log_dict['Castling_right'].append(int(board.has_castling_rights(chess.WHITE)))
                white = False
            else:
                moves_log_dict['turn'].append('black')
                moves_log_dict['Castling_right'].append(int(board.has_castling_rights(chess.BLACK)))
                white = True
                
            #(Pseudo) en passant opportunity
            moves_log_dict['EP_option'].append(int(board.has_legal_en_passant()))
            moves_log_dict['Pseudo_EP_option'].append(int(board.has_pseudo_legal_en_passant()))
            
            #Halfmove clock
            moves_log_dict['Halfmove_clock'].append(board.halfmove_clock)
                
        game_counter += 1
        if game_counter == 10:  # number of games to read
            break
    except AttributeError:  # no further games to read
        print('No further games to load.')
        break

print(f'{game_counter} games read.')

df_players = pd.DataFrame(players)
df_games = pd.DataFrame(games)
df_moves = pd.DataFrame(moves_log_dict)
dummy_players_id_df = pd.DataFrame({'White' : ["12345", 'DummyName', "1234", "forlat", "Geforce"],
"Black" : ['DummyName', "12345", "Dummy", "Geforce", "Bambi"]})

def test_players_id_df():
    '''checks if the lenght of '''
    
    players_id = pd.DataFrame({'Players': [], 'Player_ID' : []})
    players_id_df(df_players, players_id)
    assert players_id.shape[0] == len(players_id["Player_ID"].unique())
    assert players_id.isnull().values.any() == 0

def test_player_id():
    new_df = player_id(df_players)
    #new_df_dic = new_df.to_dict()
    assert df_players.isnull().values.any() == 0
    assert df_players != new_df
    #assert 'White_ID' and 'Black_ID' in new_df_dic.keys()

# def test_game_id():
#     '''checks if the shape of new df'''
#     games = game_id(df_games)
#     #games_dict = games.to_dict()
#     assert df_games.shape[1] != games.shape[1]
#     #assert 'Game_ID' and 'old_ID' in games_dict.keys()

# def test_move_id():
#     #Game_ID value is in Move_ID
#     data = [df_games["Game_ID"], df_games["old_ID"]]
#     headers = ["Game_ID", "old_ID"]
#     df = pd.concat(data, axis=1, keys=headers)
