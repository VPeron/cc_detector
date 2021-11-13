import chess
import pandas as pd

#functions for the data import and parsing
def set_move_dict():
    move_dict = {
        'Game_ID': [],
        'FEN_moves': [],
        'Bitmap_moves': [],
        'WhiteIsComp': [],
        'turn': [],
        'Castling_right': [],
        'EP_option': [],
        'Pseudo_EP_option': [],
        'Halfmove_clock': []
        }
    return move_dict

def move_info_extractor(game, board, move_dict):
    move_dict['Game_ID'].append(game.headers['FICSGamesDBGameNo'])
    move_dict['FEN_moves'].append(board.fen())
    return move_dict

def bitmap_representer(board, pieces, squares, move_dict):
    bitmap_board_dict = {}
    positions = board.piece_map()

    for piece in pieces:
        bitmap_board = {}
        for square in squares:
            if square in positions.keys():
                if positions[square] == piece:
                    bitmap_board[square] = 1
                else:
                    bitmap_board[square] = 0
            else:
                bitmap_board[square] = 0
        bitmap_board_dict[str(piece)] = bitmap_board

    move_dict['Bitmap_moves'].append(bitmap_board_dict)
    return move_dict

def castling_right(game, board, move_dict, white):
    move_dict['WhiteIsComp'].append(game.headers.get('WhiteIsComp', 'No'))
    if white:
        move_dict['turn'].append('white')
        move_dict['Castling_right'].append(
            int(board.has_castling_rights(chess.WHITE)))
        white = False
    else:
        move_dict['turn'].append('black')
        move_dict['Castling_right'].append(
            int(board.has_castling_rights(chess.BLACK)))
        white = True
    return move_dict, white

def en_passant_opp(board, move_dict):
    move_dict['EP_option'].append(int(board.has_legal_en_passant()))
    move_dict['Pseudo_EP_option'].append(
        int(board.has_pseudo_legal_en_passant()))
    return move_dict

def halfmove_clock(board, move_dict):
    """Counts half-moves goneby without a capture or pawn move."""
    move_dict['Halfmove_clock'].append(board.halfmove_clock)
    return move_dict

# def move_dict_maker(game, board, move_dict, white, pieces):
#     move_dict = move_info_extractor(game, board, move_dict)
#     move_dict = bitmap_representer(board, pieces, move_dict)
#     move_dict, white = castling_right(game, board, move_dict, white)
#     move_dict = en_passant_opp(board, move_dict)
#     move_dict = halfmove_clock(board, move_dict)
#     return move_dict, white


#functions that work with the dataframe generated from the data import
def binary_board_df(move_df):
    list_wide = []
    for line in range(len(move_df['Bitmap_moves'])):
        df_board = pd.DataFrame(move_df['Bitmap_moves'][line])

        dict_wide = {}
        for index1, i in enumerate(df_board.columns):
            for index2, j in enumerate(df_board.index):
                dict_wide[str(i) + str(j)] = df_board.iloc[index2, index1]

        list_wide.append(dict_wide)
    df_wide = pd.DataFrame(list_wide)
    return df_wide
