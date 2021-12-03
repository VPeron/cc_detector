import pandas as pd
import numpy as np

import chess
import chess.pgn
from stockfish import Stockfish

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.impute import SimpleImputer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from cc_detector.player import set_player_dict, player_info_extractor
from cc_detector.ids_generator import players_id_list
from cc_detector.game import set_game_dict, game_info_extractor
from cc_detector.move import set_move_dict, move_info_extractor,\
    bitmap_representer, castling_right, en_passant_opp, halfmove_clock,\
    binary_board_df, get_bitmap_header, pawn_count, knight_count, bishop_count,\
    rook_count, queen_count, opp_pawn_count, opp_knight_count, opp_bishop_count,\
    opp_rook_count, opp_queen_count

import pickle
#import joblib
from google.cloud import storage
from cc_detector.params import BUCKET_TRAIN_DATA_PATH, BUCKET_NAME,\
    SCALER_STORAGE_LOCATION, SCALER_STORAGE_LOCATION_EVAL
import io
import warnings


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

        #Define move limit for data padding
        self.max_game_length = 100

        #Set stockfish engine for move evaluation
        self.stockfish = Stockfish(path="/usr/games/stockfish",
                                   parameters={
                                       "Threads": 2,
                                       'Min Split Depth': 26,
                                       'Ponder': True
                                   })
        self.stockfish.set_elo_rating(2600)
        self.stockfish.set_skill_level(30)

    def read_data(self,
                  source='local',
                  **kwargs):
        if ((source == 'local') & ('data_path' not in kwargs.keys())):
            data_path = 'raw_data/Fics_data_pc_data.pgn'
            pgn = open(data_path, encoding='UTF-8')

        if source == 'gcp':
            data_path = f"{BUCKET_TRAIN_DATA_PATH}"
            client = storage.Client()
            bucket = client.get_bucket(BUCKET_NAME)
            blob = bucket.get_blob(data_path)
            data = blob.download_as_string()
            data = data.decode('utf-8')
            pgn = io.StringIO(data)

        if 'data_path' in kwargs.keys():
            data_path = kwargs['data_path']
            pgn = open(data_path, encoding='UTF-8')

        if source=="input":
            pgn = kwargs['pgn']

        return pgn

    def import_data(
            self,
            source='local',
            import_lim=50,
            **kwargs):
        '''
        Takes the path to a pgn file as an input as well as a number of
        games to be read from the pgn file (Default: import_lim=50).
        Returns three Pandas dataframes (df_players, df_games, df_moves).
        '''

        pgn = self.read_data(source, **kwargs)

        # read file
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
                variations = game.mainline()
                eval_log = {'evals': []}

                if len(moves) > 5:
                    # Player info parsing
                    players = player_info_extractor(game=game,
                                                    player_dict=player_dict)

                    # Game info parsing
                    games = game_info_extractor(game=game,
                                                game_dict=game_dict,
                                                game_counter=game_counter)

                    #cycle through evals
                    for variation in variations:
                        eval = variation.comment
                        if "%eval" in eval:
                            eval = eval.split('[%eval ')[1].split(']')[0]
                            try:
                                eval_log['evals'].append(float(eval))
                            except ValueError:
                                eval_log['evals'].append("NA")
                        else:
                            eval_log['evals'].append("NA")

                    move_dict["Evaluation"].append(eval_log["evals"])


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
                                                        move_dict=move_dict,
                                                        game_counter=game_counter)

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

        if move_dict["Evaluation"] != "NA":
            move_dict["Evaluation"] = self.flatten_list(
                move_dict["Evaluation"]
                )

        print(f'{game_counter} games read.')
        print(
            f'{games_parsed} games with a total number of {move_counter} moves parsed.'
        )
        return players, games, move_dict

    def data_df_maker(self,
                      source="local",
                      import_lim=50,
                      api=False,
                      **kwargs):
        if api==False:
            players, games, move_dict = self.import_data(source=source,
                                                        import_lim=import_lim,
                                                        **kwargs)
            df_players_temp = pd.DataFrame(players)

            df_games = pd.DataFrame(games)
            df_players = players_id_list(df_players_temp)
            df_moves = pd.DataFrame(move_dict)
            return df_players, df_games, df_moves

        if api==True:
            move_dict = kwargs["input_dict"]
            df_moves = pd.DataFrame(move_dict)
            return df_moves


    def feature_df_maker(self,
                         move_df,
                         max_game_length=100,
                         training=True,
                         api=False,
                         source="local"):
        '''
        Takes a dataframe with moves and transforms them into a padded 3D numpy array
        (a list of 2D numpy arrays, i.e. time series of the moves within one player's game).
        Returns up to two arrays: X and, if training=True, y.
        '''

        ## get binary board representation for each move

        # if api==True:
        #     df_wide = pd.DataFrame(
        #         move_df["Bitmap_moves"].tolist(),
        #         columns=get_bitmap_header())
        # if api==False:
        #     df_wide = binary_board_df(move_df)

        ## Evaluate moves with stockfish
        if api==True:
            eval_dict = {"eval":[]}

            for i in move_df["FEN_moves"]:
                self.stockfish.set_fen_position(i)
                try:
                    eval_dict["eval"].append(
                        self.stockfish.get_evaluation()["value"])
                except ValueError:
                    eval_dict["eval"].append(np.nan)

            move_df["Evaluation"] = eval_dict["eval"]

        # Exctract features
        for i in move_df["Game_ID"].unique():
            move_df.loc[move_df["Game_ID"]==i, 'Evaluation_diff'] = \
                move_df.loc[move_df["Game_ID"]==i, 'Evaluation'].diff()

        move_df["Evaluation"] = move_df.apply(
            lambda x: x["Evaluation"] * (-1)
            if (x["turn"] == "black") else x["Evaluation"],
            axis=1)

        move_df["Evaluation_diff"] = move_df.apply(
            lambda x: x["Evaluation_diff"] * (-1)
            if (x["turn"] == "black") else x["Evaluation_diff"],
            axis=1)

        move_df['pawn_count'] = pawn_count(move_df)
        move_df['knight_count'] = knight_count(move_df)
        move_df['bishop_count'] = bishop_count(move_df)
        move_df['rook_count'] = rook_count(move_df)
        move_df['queen_count'] = queen_count(move_df)

        move_df['opp_pawn_count'] = opp_pawn_count(move_df)
        move_df['opp_knight_count'] = opp_knight_count(move_df)
        move_df['opp_bishop_count'] = opp_bishop_count(move_df)
        move_df['opp_rook_count'] = opp_rook_count(move_df)
        move_df['opp_queen_count'] = opp_queen_count(move_df)

        #get numerical features from move_df (those that need to be scaled)
        game_infos_num = move_df[[
            "Castling_right",
            "EP_option",
            "Halfmove_clock",
            "Evaluation",
            "Evaluation_diff",
            "pawn_count",
            "knight_count",
            "bishop_count",
            "rook_count",
            "queen_count",
            "opp_pawn_count",
            "opp_knight_count",
            "opp_bishop_count",
            "opp_rook_count",
            "opp_queen_count"
            ]]


        game_infos_temp = move_df[[
            "Game_ID", "turn", "WhiteIsComp"
            ]]

        ## concatenate board representations with other features
        #df_wide_full = df_wide.join(game_infos_num)
        df_wide_full = game_infos_num

        ## Scale features and rescale outliers

        if "Evaluation" in df_wide_full.columns:
            df_wide_full.loc[:,"Evaluation"] = df_wide_full["Evaluation"].apply(
                lambda x: np.nan if x == "NA" else (
                    3000 if x > 3000 else (
                        -3000 if x <-3000 else x))
                )
            df_wide_full.loc[:,"Evaluation_diff"] = df_wide_full["Evaluation_diff"].apply(
                lambda x: np.nan if x == "NA" else (
                    2000 if x > 2000 else (
                        -2000 if x <-2000 else x))
                )

            if training:
                minmax_hmc = MinMaxScaler()
                minmax_eval = MinMaxScaler()
                minmax_count = MinMaxScaler()
                imputer_eval = SimpleImputer(strategy="mean")

                eval_transformer = Pipeline([("imputer", imputer_eval),
                                             ("minmax_eval", minmax_eval)])

                preproc_basic = ColumnTransformer(
                    transformers=[
                        ("hmc_scaler", minmax_hmc, ["Halfmove_clock"]),
                        ("eval_trans", eval_transformer,
                         ["Evaluation", "Evaluation_diff"]),
                        ('count_scaler', minmax_count, [
                            "pawn_count", "knight_count", "bishop_count",
                            "rook_count", "queen_count", "opp_pawn_count",
                            "opp_knight_count", "opp_bishop_count",
                            "opp_rook_count", "opp_queen_count"]
                         )
                    ], remainder='passthrough')

                preproc_basic.fit(df_wide_full)
                df_wide_full = pd.DataFrame(preproc_basic.transform(df_wide_full))

                if source=="local":
                    with open("models/scaler.pkl", "wb") as file:
                        pickle.dump(preproc_basic, file)
                if ((source=="gcp") or (source=="input")):
                    with open("scaler.pkl", "wb") as file:
                        pickle.dump(preproc_basic, file)
                    client = storage.Client().bucket(BUCKET_NAME)
                    blob = client.blob(SCALER_STORAGE_LOCATION_EVAL)
                    blob.upload_from_filename('scaler.pkl')
            else:
                if source=="local":
                    preproc_basic = pickle.load(open("models/scaler.pkl", "rb"))
                if ((source == "gcp") or (source == "input")):
                    client = storage.Client().bucket(BUCKET_NAME)
                    blob = client.blob(SCALER_STORAGE_LOCATION_EVAL)
                    blob.download_to_filename("scaler.pkl")
                    print("Scaler downloaded from Google Cloud Storage")
                    preproc_basic = pickle.load(open("scaler.pkl", "rb"))
                df_wide_full = pd.DataFrame(preproc_basic.transform(df_wide_full))
        else:
            if training:
                scaler = MinMaxScaler()
                scaler.fit(df_wide_full[["Halfmove_clock"]])
                df_wide_full["Halfmove_clock"] = scaler.transform(
                    df_wide_full[["Halfmove_clock"]])
                if source=="local":
                    with open("models/minmax_scaler.pkl", "wb") as file:
                        pickle.dump(scaler, file)
                if ((source=="gcp") or (source=="input")):
                    with open("minmax_scaler.pkl", "wb") as file:
                        pickle.dump(scaler, file)
                    client = storage.Client().bucket(BUCKET_NAME)
                    blob = client.blob(SCALER_STORAGE_LOCATION)
                    blob.upload_from_filename('minmax_scaler.pkl')
            else:
                if source=="local":
                    scaler = pickle.load(open("models/minmax_scaler.pkl", "rb"))
                if ((source == "gcp") or (source == "input")):
                    client = storage.Client().bucket(BUCKET_NAME)
                    blob = client.blob(SCALER_STORAGE_LOCATION)
                    blob.download_to_filename("minmax_scaler.pkl")
                    print("Scaler downloaded from Google Cloud Storage")
                    scaler = pickle.load(open("minmax_scaler.pkl", "rb"))
                df_wide_full["Halfmove_clock"] = scaler.transform(
                    df_wide_full[["Halfmove_clock"]])

        # Merge dataframes
        df_wide_full = df_wide_full.join(game_infos_temp)

        # Generate binary feature that indicates if player is computer
        if training:
            df_wide_full["Computer"] = df_wide_full.apply(lambda x: 1 if (
                (x["WhiteIsComp"] == "Yes") and (x["turn"] == "white")) or (
                    (x["WhiteIsComp"] == "No") and
                    (x["turn"] == "black")) else 0,
                                                          axis=1)
        else:
            df_wide_full["Computer"] = "NA"

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

        # padding arrays
        X_pad = pad_sequences(
            games_list,
            dtype='float32',
            padding='post',
            value=-999.,
        )

        if X_pad.shape[1] < max_game_length:
            array_list = []
            for game in X_pad:
                game = np.pad(game,
                            ((0, (max_game_length - game.shape[0])), (0, 0)),
                            "constant",
                            constant_values=(-999., ))
                array_list.append(game)
            X_new = np.stack(array_list, axis=0)

        if X_pad.shape[1] > max_game_length:
            array_list = []
            for game in X_pad:
                game = game[0:max_game_length, :]
                array_list.append(game)
            X_new = np.stack(array_list, axis=0)

        self.max_game_length = max_game_length

        if training:
            return X_new, y
        else:
            return X_new

    def flatten_list(self, _2d_list):
        flat_list = []
        # Iterate through the outer list
        for element in _2d_list:
            if type(element) is list:
                # If the element is of type list, iterate through the sublist
                for item in element:
                    flat_list.append(item)
            else:
                flat_list.append(element)
        return flat_list


if __name__ == "__main__":
    #Print heads of imported dfs
    player_df, game_df, move_df = ChessData().data_df_maker()

    print(player_df.head())
    print(game_df.head())
    print(move_df.head())

    #print feature and target arrays
    X_pad, y = ChessData().feature_df_maker(move_df)

    print(X_pad)
    print(y)
