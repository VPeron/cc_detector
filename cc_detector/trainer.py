import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt

from cc_detector.data import ChessData

from tensorflow.keras.models import Sequential
from tensorflow.keras import layers, regularizers
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import RMSprop
from sklearn.model_selection import train_test_split

from memoized_property import memoized_property
import mlflow
from mlflow.tracking import MlflowClient
import joblib
from cc_detector.params import BUCKET_TRAIN_DATA_PATH, BUCKET_NAME, \
    STORAGE_LOCATION
from google.cloud import storage


class Trainer():
    MLFLOW_URI = "https://mlflow.lewagon.co/"


    def __init__(self) -> None:
        self.model = None
        self.max_game_length = 100
        self.experiment_name = "DE-BERLIN-673-mclemens-cc_detect"

    ## MLflow functions
    def set_experiment_name(self, experiment_name):
        '''defines the experiment name for MLFlow'''
        self.experiment_name = experiment_name

    @memoized_property
    def mlflow_client(self):
        mlflow.set_tracking_uri(self.MLFLOW_URI)
        return MlflowClient()

    @memoized_property
    def mlflow_experiment_id(self):
        try:
            return self.mlflow_client.create_experiment(self.experiment_name)
        except BaseException:
            return self.mlflow_client.get_experiment_by_name(
                self.experiment_name).experiment_id

    @memoized_property
    def mlflow_run(self):
        return self.mlflow_client.create_run(self.mlflow_experiment_id)

    def mlflow_log_param(self, key, value):
        self.mlflow_client.log_param(self.mlflow_run.info.run_id, key, value)

    def mlflow_log_metric(self, key, value):
        self.mlflow_client.log_metric(self.mlflow_run.info.run_id, key, value)


    ###Data import and processing; Training functions
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
            X, y = ChessData().feature_df_maker(
                move_df=move_df,
                max_game_length=max_game_length,
                training=True
                )
            self.max_game_length = max_game_length

            print("""Data has been transformed into the correct format. ✅
                  Training mode was chosen (X and y will be returned).""")

            return X, y

        else:
            X = ChessData().feature_df_maker(
                move_df=move_df,
                max_game_length=max_game_length,
                training=False
                )
            self.max_game_length = max_game_length

            print("""Data has been transformed into the correct format. ✅
            Training mode was disabled (Only X will be returned).""")
            return X


    def train_model(self, X_train, y_train,
                    recurrent_dropout=0.3,
                    dense_dropout=0.3,
                    l1_reg_rate=0.001,
                    lstm_start_units=128,
                    dense_start_units=64,
                    verbose=0,
                    **kwargs):
        """
        Builds an LSTM model, compiles it, and then fits it to the data transformed
        with the transform_data() function. Returns the trained model
        """
        reg_l1 = regularizers.L1(l1_reg_rate)
        if 'l2_reg_rate' in kwargs.keys():
            reg_l2 = regularizers.L2(kwargs['l2_reg_rate'])

        model = Sequential()

        model.add(
            layers.Masking(mask_value=-999,
                           input_shape=(self.max_game_length, 771)))
        model.add(
            layers.LSTM(units=lstm_start_units,
                        activation='tanh',
                        return_sequences=True,
                        recurrent_dropout=recurrent_dropout))
        model.add(
            layers.LSTM(units=int(lstm_start_units / 2),
                        activation='tanh',
                        return_sequences=False,
                        recurrent_dropout=recurrent_dropout))
        model.add(
            layers.Dense(units=dense_start_units,
                         activation='relu',
                         kernel_regularizer=reg_l1))
        model.add(layers.Dropout(dense_dropout))
        model.add(
            layers.Dense(units=int(dense_start_units / 2),
                         activation='relu',
                         kernel_regularizer=reg_l1))
        model.add(layers.Dropout(dense_dropout))
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
        self.mlflow_log_param("model", "Sequential: LSTM (2 LSTM layers, 2 Dense layers)")
        self.mlflow_log_param("l1 regularizer rate", l1_reg_rate)
        self.mlflow_log_param("recurrent dropout", recurrent_dropout)
        self.mlflow_log_param("dense dropout", dense_dropout)
        self.mlflow_log_param("lstm_start_units", lstm_start_units)
        self.mlflow_log_param("dense_start_units", dense_start_units)
        self.mlflow_log_param("train_data_size", X_train.shape[0])

        print('''Model has been trained and saved 💪 Training params have been logged to MLflow:
        https://mlflow.lewagon.co/#/experiments/21242''')

        self.save_model_to_gcp(model)

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

    def get_path_to_joblib(self,
                           source="local"):
        if source == "local":
            path = "models/cc_detect_lstm_model.joblib"
        if source == "gcp":
            path = ""
        return path

    def evaluate_model(self,
                       X_test,
                       y_test,
                       source='local'):
        """
        Takes two numpy arrays (X_test, y_test) and evaluates the model performance.
        """
        path_to_joblib = self.get_path_to_joblib(source=source)
        model = self.get_model(path_to_joblib)
        result = model.evaluate(x=X_test, y=y_test)

        self.mlflow_log_metric("test loss", result[0])
        self.mlflow_log_metric("test accuracy", result[1])

        print('''Evaluation has been logged to MLflow:
              https://mlflow.lewagon.co/#/experiments/21242''')
        return result

    def save_model_to_gcp(self,
                          model):
        """ method that saves the model into a .joblib file and uploads it
        on Google Storage /models folder """
        joblib.dump(model, 'models/cc_detect_lstm_model.joblib')
        self.gcp_upload()
        print("Uploaded model.joblib to gcp cloud storage")

    def gcp_upload(self):
        client = storage.Client().bucket(BUCKET_NAME)
        storage_location = STORAGE_LOCATION
        blob = client.blob(storage_location)
        blob.upload_from_filename('cc_detect_lstm_model.joblib')

    def get_model(self, path_to_joblib):
        '''
        Loads a joblib model from the given path and returns the model.
        '''
        model = joblib.load(path_to_joblib)
        return model

    def predict(self, X,
                path_to_joblib="models/cc_detect_lstm_model.joblib"):
        '''
        Predicts if the game (X) was played by a computer or a human.
        Returns a prediction in the form of an array.
        '''
        model = self.get_model(path_to_joblib)
        prediction = model.predict(X)
        return prediction

    def rtp_input(self,
                  source="local",
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

        path_to_joblib = self.get_path_to_joblib(source=source)

        prediction = self.predict(X_eval, path_to_joblib)
        return prediction


if __name__ == "__main__":
    #Instanciate Trainer
    trainer = Trainer()

    #Retrieve data from file
    player_df, game_df, move_df = trainer.get_data(
        data_path='raw_data/Fics_data_pc_data.pgn',
        import_lim=100
        )

    #Transform data into correct shape
    X, y = trainer.transform_move_data(move_df=move_df,
                                       max_game_length=100,
                                       training=True)

    #Split Data into train and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        test_size=0.2)

    #Train model
    trainer.train_model(X_train, y_train, verbose=0)

    #Evaluate model
    trainer.evaluate_model(X_test, y_test)
