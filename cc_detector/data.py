import pandas as pd
import numpy as np

import chess
import chess.pgn

from sklearn.preprocessing import MinMaxScaler

from cc_detector.player import set_player_dict, player_info_extractor
from cc_detector.ids_generator import players_id_list
from cc_detector.game import set_game_dict, game_info_extractor
from cc_detector.move import set_move_dict, move_info_extractor,\
    bitmap_representer, castling_right, en_passant_opp, halfmove_clock,\
    binary_board_df#, move_dict_maker

import pickle
from google.cloud import storage    
from cc_detector.params import BUCKET_TRAIN_DATA_PATH, BUCKET_NAME, GOOGLE_APPLICATION_CREDENTIALS



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

        #Set list of all squares on the board
        self.SQUARES = [i for i in range(64)]

    def import_data(
            self,
            source='local',
            data_path='raw_data/Fics_data_pc_data.pgn',
            import_lim=50):
        '''
        Takes the path to a pgn file as an input as well as a number of
        games to be read from the pgn file (Default: import_lim=50).
        Returns three Pandas dataframes (df_players, df_games, df_moves).
        '''
        if source == 'local':
            data_path = 'raw_data/Fics_data_pc_data.pgn'
        if source == 'gcp':
            data_path = f"gs://{BUCKET_NAME}/{BUCKET_TRAIN_DATA_PATH}"
        # read file
        # client = storage.Client()
        pgn = open(data_path, encoding='UTF-8')
        game_counter = 0
        games_parsed = 0
        move_counter = 0

        #preshape dataframes
        player_dict = set_player_dict()
        game_dict = set_game_dict()
        move_dict = set_move_dict()

        while True:  # keep reading games
            try:
                game = chess.pgn.read_game(pgn)
                board = game.board()
                moves = list(game.mainline_moves())

                if len(moves) > 5:
                    # Player info parsing
                    players = player_info_extractor(game=game,
                                                    player_dict=player_dict)

                    # Game info parsing
                    games = game_info_extractor(game=game,
                                                game_dict=game_dict)

                    # Moves info parsing
                    white = True
                    for move in moves:
                        board.push(move)

                        # move_dict = move_dict_maker(game=game,
                        #                             board=board,
                        #                             move_dict=move_dict,
                        #                             white=white,
                        #                             pieces=self.PIECES)

                        #Extract GAME ID and FEN moves
                        move_dict = move_info_extractor(game=game,
                                                        board=board,
                                                        move_dict=move_dict)

                        #Generate bitmap representation of FENs
                        move_dict = bitmap_representer(board=board,
                                                    pieces=self.PIECES,
                                                    squares=self.SQUARES,
                                                    move_dict=move_dict)

                        #Extract turn color and castling availablity
                        move_dict, white = castling_right(game=game,
                                                board=board,
                                                move_dict=move_dict,
                                                white=white)

                        #Identify (pseudo) en passant opportunity
                        move_dict = en_passant_opp(board=board,
                                                move_dict=move_dict)

                        #Extract Halfmove clock
                        move_dict = halfmove_clock(board=board,
                                                move_dict=move_dict)
                        move_counter += 1
                    games_parsed += 1

                game_counter += 1
                if game_counter == import_lim:  # number of games to read
                    break
            except AttributeError:  # no further games to read
                print('No further games to load.')
                break

        print(f'{game_counter} games read.')
        print(
            f'{games_parsed} games with a total number of {move_counter} moves parsed.'
        )

        df_players_temp = pd.DataFrame(players)
        df_games = pd.DataFrame(games)
        df_moves = pd.DataFrame(move_dict)

        df_players = players_id_list(df_players_temp)

        return df_players, df_games, df_moves


    def feature_df_maker(self, move_df, training=True):
        '''
        Takes a dataframe with moves and transforms them into a list of
        2D numpy arrays (time series).
        Returns up to two lists/arrays: X (list) and, if training=True, y (array).
        '''

        #get binary board representation for each move
        df_wide = binary_board_df(move_df)

        #get non-board-representation features from move_df
        game_infos = move_df[[
            "Game_ID", "turn", "WhiteIsComp", "Castling_right", "EP_option",
            "Halfmove_clock"
        ]]

        # concatenate board representations with other features
        df_wide_full = df_wide.join(game_infos)

        # Generate binary feature that indicates if player is computer
        if training:
            df_wide_full["Computer"] = df_wide_full.apply(
                lambda x: 1 if (
                (x["WhiteIsComp"] == "Yes") and (x["turn"] == "white")
                ) or (
                    (x["WhiteIsComp"] == "No") and (x["turn"] == "black")
                    ) else 0,
                axis=1)
        else:
            df_wide_full["Computer"] = "NA"


        # Scale features
        if training:
            scaler = MinMaxScaler()
            scaler.fit(df_wide_full[["Halfmove_clock"]])
            df_wide_full["Halfmove_clock"] = scaler.transform(
                df_wide_full[["Halfmove_clock"]])
            with open("models/minmax_scaler.pkl", "wb") as file:
                pickle.dump(scaler, file)
        else:
            scaler = pickle.load(open("models/minmax_scaler.pkl", "rb"))
            df_wide_full["Halfmove_clock"] = scaler.transform(
            df_wide_full[["Halfmove_clock"]])

        #Generate Target vector
        if training:
            y = df_wide_full.groupby(by=["Game_ID", "turn"],
                                    sort=False).agg(min)["Computer"].values

        #Split df into white and black games
        df_white = df_wide_full[df_wide_full["turn"] == "white"]
        df_black = df_wide_full[df_wide_full["turn"] == "black"]

        #generate Game-ID list
        game_list = df_wide_full["Game_ID"].unique()

        # create list of game arrays that conatain the moves of one player
        # respectively plus additional features
        games_list = []
        for game_id in game_list:
            df_w_temp = df_white[df_white["Game_ID"] == game_id].drop(
                columns=["turn", "WhiteIsComp", "Game_ID", "Computer"])
            games_list.append(np.array(df_w_temp))
            df_b_temp = df_black[df_black["Game_ID"] == game_id].drop(
                columns=["turn", "WhiteIsComp", "Game_ID", "Computer"])
            games_list.append(np.array(df_b_temp))

        X = games_list

        if training:
            return X, y
        else:
            return X


if __name__ == "__main__":
    #Print heads of imported dfs
    player_df, game_df, move_df = ChessData().import_data()

    print(player_df.head())
    print(game_df.head())
    print(move_df.head())

    #print feature and target arrays
    X_pad, y = ChessData().feature_df_maker(move_df)

    print(X_pad)
    print(y)
