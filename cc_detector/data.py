import pandas as pd
import numpy as np

import chess
import chess.pgn

from cc_detector.player import set_player_dict, player_info_extractor
from cc_detector.game import set_game_dict, game_info_extractor
from cc_detector.move import set_move_dict, move_info_extractor,\
    bitmap_representer, castling_right, en_passant_opp, halfmove_clock #, move_dict_maker


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

        self.SQUARES = [i for i in range(64)]

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
        player_dict = set_player_dict()

        game_dict = set_game_dict()

        move_dict = set_move_dict()

        while True:  # keep reading games
            try:
                game = chess.pgn.read_game(pgn)
                board = game.board()
                moves = list(game.mainline_moves())

                # Player
                players = player_info_extractor(game=game,
                                                player_dict=player_dict)

                # Games
                games = game_info_extractor(game=game,
                                            game_dict=game_dict)

                # MOVE CYCLE
                white = True
                for move in moves:
                    board.push(move)

                    # move_dict = move_dict_maker(game=game,
                    #                             board=board,
                    #                             move_dict=move_dict,
                    #                             white=white,
                    #                             pieces=self.PIECES)

                    #extract GAME ID and FEN moves
                    move_dict = move_info_extractor(game=game,
                                                    board=board,
                                                    move_dict=move_dict)

                    #Generate bitmap representation of FENs
                    move_dict = bitmap_representer(board=board,
                                                   pieces=self.PIECES,
                                                   squares=self.SQUARES,
                                                   move_dict=move_dict)

                    #Turn color and castling availablity
                    move_dict, white = castling_right(game=game,
                                               board=board,
                                               move_dict=move_dict,
                                               white=white)

                    #(Pseudo) en passant opportunity
                    move_dict = en_passant_opp(board=board,
                                               move_dict=move_dict)

                    #Halfmove clock
                    move_dict = halfmove_clock(board=board,
                                               move_dict=move_dict)

                game_counter += 1
                if game_counter == import_lim:  # number of games to read
                    break
            except AttributeError:  # no further games to read
                print('No further games to load.')
                break

        print(f'{game_counter} games read.')

        df_players = pd.DataFrame(players)
        df_games = pd.DataFrame(games)
        df_moves = pd.DataFrame(move_dict)

        return df_players, df_games, df_moves


if __name__ == "__main__":
    player_df, game_df, move_df = ChessData().import_data()

    print(player_df.head())
    print(game_df.head())
    print(move_df.head())
