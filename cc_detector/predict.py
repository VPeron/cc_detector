import pandas as pd
import numpy as np
from cc_detector.trainer import Trainer
from cc_detector.data import ChessData

## functions used for prediction
def predict_comp(X, source='local'):
    '''
    Predicts if the game (X) was played by a computer or a human.
    Returns a prediction in the form of an array.
    '''
    if source == "local":
        path_to_joblib = "models/cc_detect_lstm_model.joblib"
        model = Trainer().load_model(path_to_joblib)
    if ((source == "gcp") or (source == "input")):
        model = Trainer().load_model_from_gcp()
    prediction = model.predict(X)
    return prediction

def rtp_input(move_df, source="local", white=True, api=True, **kwargs):
    '''
    Reads and transforms the content of a pgn file, then returns a
    prediction if the chosen player (default: white=True) is a computer or not.

    Please pass the pgn object as a kwarg (pgn="...").

    '''
    # player_df, game_df, move_df = ChessData().data_df_maker(source=source,
    #                                                         import_lim=1,
    #                                                         **kwargs)
    X_pad = Trainer().transform_move_data(move_df,
                                          training=False,
                                          source="gcp",
                                          api=api)

    if white:
        X_eval = X_pad[0]
    else:
        X_eval = X_pad[1]
    X_eval = X_eval.reshape(1, X_eval.shape[0], X_eval.shape[1])

    prediction = predict_comp(X=X_eval, source=source)
    return prediction[0][0]
