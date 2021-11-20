import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt

from cc_detector.data import ChessData

from tensorflow.keras.models import Sequential
from tensorflow.keras import layers, regularizers
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.sequence import pad_sequences

import joblib

class Trainer():
    def __init__(self) -> None:

        self.model = None
        self.max_game_length = 100

    def get_data(self,
                 data_path="raw_data/Fics_data_pc_data.pgn",
                 import_lim=1000) -> DataFrame:
        '''
        Takes a path to a pgn file (data_path) and a max. number of games read
        (default: import_lim=1000), returns three dataframes (player_df, game_df, move_df).
        '''
        player_df, game_df, move_df = ChessData().import_data(data_path=data_path,
                                                              import_lim=import_lim)

        return player_df, game_df, move_df

    def transform_move_data(self, move_df, max_game_length=100, training=True):
        """
        Takes the move dataframe (move_df) and returns a padded 3D numpy array
        (padding with value -999). The maximum number of moves for the padding
        can be specified with max_game_length (default: 100).
        Also returns y as an numpy array if training=True.
        """
        if training:
            X, y = ChessData().feature_df_maker(move_df=move_df,
                                                training=True)
        else:
            X = ChessData().feature_df_maker(move_df=move_df,
                                             training=False)

        # padding arrays
        X_pad = pad_sequences(
            X,
            dtype='float32',
            padding='post',
            value=-999,
        )

        if X_pad.shape[1] < max_game_length:
            array_list = []
            for game in X_pad:
                game = np.pad(game,
                        ((0,(max_game_length-game.shape[0])),(0,0)),
                        "constant",
                        constant_values=(-999.,))
                array_list.append(game)
            X_new = np.stack(array_list, axis = 0)

        if X_pad.shape[1] > max_game_length:
            array_list = []
            for game in X_pad:
                game = game[0:max_game_length,:]
                array_list.append(game)
            X_new = np.stack(array_list, axis = 0)

        self.max_game_length = max_game_length

        print("Data has been transformed into the correct format ✅")
        if training:
            return X_new, y
        else:
            return X_new

    def train_model(self, X_train, y_train, verbose=0):
        """
        Builds an LSTM model, compiles it, and then fits it to the data transformed
        with the transform_data() function. Returns the trained model
        """
        reg_l1 = regularizers.L1(0.001)
        #reg_l2 = regularizers.L2(0.01)
        #reg_l1_l2 = regularizers.l1_l2(l1=0.005, l2=0.0005)

        model = Sequential()

        model.add(
            layers.Masking(mask_value=-999,
                           input_shape=(self.max_game_length, 771)))
        model.add(
            layers.LSTM(units=128,
                        activation='tanh',
                        return_sequences=True,
                        recurrent_dropout=0.3))
        model.add(
            layers.LSTM(units=64,
                        activation='tanh',
                        return_sequences=False,
                        recurrent_dropout=0.3))
        model.add(
            layers.Dense(units=64,
                         activation='relu',
                         kernel_regularizer=reg_l1))
        model.add(layers.Dropout(0.3))
        model.add(
            layers.Dense(units=32,
                         activation='relu',
                         kernel_regularizer=reg_l1))
        model.add(layers.Dropout(0.3))
        model.add(
            layers.Dense(units=1,
                        activation="sigmoid"))

        # The compilation
        rmsprop_opt = RMSprop(learning_rate=0.001)

        model.compile(loss='binary_crossentropy',
                      optimizer=rmsprop_opt,
                      metrics=["accuracy"])

        # The fit
        es = EarlyStopping(restore_best_weights=True, patience=5)

        history = model.fit(X_train, y_train,
                  batch_size=32,
                  epochs=50,
                  callbacks=[es],
                  validation_split=0.2,
                  verbose=verbose)

        self.model = model
        joblib.dump(model, 'models/cc_detect_lstm_model.joblib')

        print("Model has been trained and saved 💪")

        return history

    def plot_train_history(self, history):
        '''
        Plots the training history (loss and accuracy curve)
        for the latest training iteration.
        '''
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(13,4))
        ax1.plot(history.history['loss'])
        ax1.plot(history.history['val_loss'])
        ax1.set_title('Model loss')
        ax1.set_ylabel('Loss')
        ax1.set_xlabel('Epoch')
        #ax1.set_ylim(ymin=0, ymax=200)
        ax1.legend(['Train', 'Validation'], loc='best')
        ax1.grid(axis="x",linewidth=0.5)
        ax1.grid(axis="y",linewidth=0.5)

        ax2.plot(history.history['accuracy'])
        ax2.plot(history.history['val_accuracy'])
        ax2.set_title('Accuracy')
        ax2.set_ylabel('Accuracy')
        ax2.set_xlabel('Epoch')
        #ax2.set_ylim(ymin=0, ymax=20)
        ax2.legend(['Train', 'Validation'], loc='best')
        ax2.grid(axis="x",linewidth=0.5)
        ax2.grid(axis="y",linewidth=0.5)

    def evaluate_model(self, X_test, y_test):
        """
        Takes two numpy arrays (X_test, y_test) and evaluates the model performance.
        """
        result = self.model.evaluate(x=X_test, y=y_test)

        return result

    def get_model(self, path_to_joblib="models/cc_detect_lstm_model.joblib"):
        '''
        Loads a joblib model from the given path and returns the model.
        '''
        model = joblib.load(path_to_joblib)
        return model

    def predict(self, X, path_to_joblib="models/cc_detect_lstm_model.joblib"):
        '''
        Predicts if the game (X) was played by a computer or a human.
        Returns a prediction in the form of an array.
        '''
        model = self.get_model(path_to_joblib)
        prediction = model.predict(X)
        return prediction

    def rtp_input(self,
                  path_to_joblib="models/cc_detect_lstm_model.joblib",
                  data_file_path="raw_data/Fics_data_pc_data.pgn",
                  white=True):
        '''
        Reads and transforms the content of a pgn file, then returns a
        prediction if the chosen player (default: white=True) is a computer or not.
        '''
        player_df, game_df, move_df = ChessData().import_data(
            data_path=data_file_path, import_lim=1)
        X_pad = self.transform_move_data(move_df, training=False)

        if white:
            X_eval = X_pad[0]
        else:
            X_eval = X_pad[1]
        X_eval = X_eval.reshape(1, X_eval.shape[0], X_eval.shape[1])

        prediction = self.predict(X_eval, path_to_joblib)
        return prediction
