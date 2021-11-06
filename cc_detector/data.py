import pandas as pd
import numpy as np

import chess
import chess.pgn


class ChessData:
    def __init__(self) -> None:
        # Set list of Pieces
        self.PIECES=[
            chess.Piece.from_symbol('P'),
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
            chess.Piece.from_symbol('k')
            ]

    def import_data(
            self,
            data_path="/Users/manuel/code/VPeron/cc_detector/raw_data/Fics_data_pc_data.pgn",
            import_lim=50):
        '''
        Takes the path to a pgn file as an input as well as a number of
        games to be read from the pgn file (Default: import_lim=50).

        Returns three Pandas dataframes (df_players, df_games, df_moves).
        '''
        # read file
        pgn = open(data_path, encoding='UTF-8')

        game_counter = 0

        #preshape dataframes
        players = {
            'White': [],
            'White_Elo': [],
            'Black': [],
            'Black_Elo': [],
            'WhiteIsComp': [],
        }

        games = {
            'Game_ID': [],
            'Date': [],
            'White': [],  # Dummy ID
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

                    for piece in self.PIECES:
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
                if game_counter == import_lim:  # number of games to read
                    break
            except AttributeError:  # no further games to read
                print('No further games to load.')
                break

        print(f'{game_counter} games read.')

        df_players = pd.DataFrame(players)
        df_games = pd.DataFrame(games)
        df_moves = pd.DataFrame(moves_log_dict)

        return df_players, df_games, df_moves


if __name__ == "__main__":
    player_df, game_df, move_df = ChessData().import_data()

    print(player_df.head())
    print(game_df.head())
    print(move_df.head())
