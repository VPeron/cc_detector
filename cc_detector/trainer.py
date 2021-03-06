import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt

from cc_detector.data import ChessData

from tensorflow.keras.models import Sequential
from tensorflow.keras import layers, regularizers, optimizers
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import RMSprop, Adam
from tensorflow.keras.losses import BinaryCrossentropy
from sklearn.model_selection import train_test_split

from memoized_property import memoized_property
import mlflow
from mlflow.tracking import MlflowClient
import joblib
from cc_detector.params import BUCKET_TRAIN_DATA_PATH, BUCKET_NAME, \
    MODEL_STORAGE_LOCATION
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
    def get_data(self, source='local', import_lim=1000, **kwargs) -> DataFrame:
        '''
        Takes a path to a pgn file (data_path) and a max. number of games read
        (default: import_lim=1000), returns three dataframes (player_df, game_df, move_df).
        '''
        player_df, game_df, move_df = ChessData().data_df_maker(
            source=source, import_lim=import_lim, **kwargs)

        return player_df, game_df, move_df

    def transform_move_data(self,
                            move_df,
                            max_game_length=100,
                            training=True,
                            source="local",
                            api=False):
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
                training=True,
                source=source,
                api=api
                )
            self.max_game_length = max_game_length

            print("""Data has been transformed into the correct format. ???
                  Training mode was chosen (X and y will be returned).""")

            return X, y

        else:
            X = ChessData().feature_df_maker(move_df=move_df,
                                             max_game_length=max_game_length,
                                             training=False,
                                             source=source,
                                             api=api)
            self.max_game_length = max_game_length

            print("""Data has been transformed into the correct format. ???
            Training mode was disabled (Only X will be returned).""")
            return X


    def train_model(
            self,
            X_train,
            y_train,
            recurrent_dropout=0.25,
            dense_dropout=0.25,
            l1_reg_rate=None,
            l2_reg_rate=None, #0.001,
            lstm_start_units=64,
            dense_start_units=64,
            verbose=0,
            **kwargs):
        """
        Builds an LSTM model, compiles it, and then fits it to the data transformed
        with the transform_data() function. Returns the trained model
        """
        reg_l1 = regularizers.L1(l1_reg_rate)
        reg_l2 = regularizers.L2(l2_reg_rate)

        self.model = Sequential()

        self.model.add(
            layers.Masking(mask_value=-999.,
                           input_shape=(self.max_game_length, X_train.shape[2])))

        self.model.add(
            layers.LSTM(units=lstm_start_units,
                        activation='tanh',
                        return_sequences=True,
                        recurrent_dropout=recurrent_dropout))
        self.model.add(
            layers.LSTM(units=int(lstm_start_units / 2),
                        activation='tanh',
                        return_sequences=False,
                        recurrent_dropout=recurrent_dropout))

        #self.model.add(layers.Dropout(dense_dropout))

        self.model.add(
            layers.Dense(units=dense_start_units,
                         activation='relu',
                         kernel_regularizer=reg_l2))

        self.model.add(layers.Dropout(dense_dropout))

        # self.model.add(
        #     layers.Dense(units=int(dense_start_units / 2),
        #                  activation='relu',
        #                  kernel_regularizer=reg_l2))
        # self.model.add(layers.Dropout(dense_dropout))

        self.model.add(
            layers.Dense(units=1,
                        activation="sigmoid"))

        # The compilation
        # lr_schedule = optimizers.schedules.ExponentialDecay(
        #     initial_learning_rate=0.001,
        #     decay_steps=10,
        #     decay_rate=0.5)

        rmsprop_opt = RMSprop(learning_rate=0.0001)

        self.model.compile(
            loss='binary_crossentropy',
            optimizer=rmsprop_opt,
            metrics=["accuracy"])

        # The fit
        es = EarlyStopping(monitor="val_accuracy", restore_best_weights=True, patience=25)

        history = self.model.fit(X_train, y_train,
                  batch_size=64,
                  epochs=500,
                  callbacks=[es],
                  validation_split=0.3,
                  verbose=verbose)

        #self.model = model
        self.mlflow_log_param("model", "Sequential: LSTM (2 LSTM layers, 2 Dense layers)")
        self.mlflow_log_param("training_epochs", max(history.epoch)+1)
        self.mlflow_log_param("l1_regularizer_rate", l1_reg_rate)
        self.mlflow_log_param("recurrent_dropout", recurrent_dropout)
        self.mlflow_log_param("dense_dropout", dense_dropout)
        self.mlflow_log_param("lstm_start_units", lstm_start_units)
        self.mlflow_log_param("dense_start_units", dense_start_units)
        self.mlflow_log_param("train_data_size", X_train.shape[0])
        self.mlflow_log_param("train_accuracy", history.history["accuracy"][-25])
        self.mlflow_log_param("validation_accuracy",
                              history.history["val_accuracy"][-25])

        print('''Model has been trained and saved ???? Training params have been logged to MLflow:
        https://mlflow.lewagon.co/#/experiments/21242''')

        self.save_model_to_gcp(self.model)

        return history

    def evaluate_model(self, X_test, y_test, source='local'):
        """
        Takes two numpy arrays (X_test, y_test) and evaluates the model performance.
        """
        if source == "local":
            path_to_joblib = "models/cc_detect_lstm_model.joblib"
            model = self.load_model(path_to_joblib)
        if source == "gcp":
            model = self.load_model_from_gcp()

        result = model.evaluate(x=X_test, y=y_test)

        self.mlflow_log_metric("test loss", result[0])
        self.mlflow_log_metric("test accuracy", result[1])

        print(f'''Evaluation has been logged to MLflow:
              https://mlflow.lewagon.co/#/experiments/21242
              +++++++++++++++++++++++++++++++++++++++++++++
              The accuracy of the model is {result[1]}.''')
        return result

### plotting training history

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


## Functions that deal with model storing and loading

    def save_model(self, model, path= "models/cc_detect_lstm_model.joblib"):
        '''
        Saves the model locally in the form of a joblib file.
        '''
        joblib.dump(model, path)
        print(f"Model.joblib was saved locally under {path}.")

    def save_model_to_gcp(self,
                          model):
        '''
        Method that saves the model into a .joblib file and uploads it
        on Google Storage /models folder
        '''
        joblib.dump(model, 'cc_detect_lstm_model.joblib')
        client = storage.Client().bucket(BUCKET_NAME)
        storage_location = MODEL_STORAGE_LOCATION
        blob = client.blob(storage_location)
        blob.upload_from_filename('cc_detect_lstm_model.joblib')
        print("Uploaded model.joblib to gcp cloud storage.")

    def load_model(self, path_to_joblib="models/cc_detect_lstm_model.joblib"):
        '''
        Loads a joblib model from the given path and returns the model.
        '''
        model = joblib.load(path_to_joblib)
        return model

    def load_model_from_gcp(self):
        client = storage.Client().bucket(BUCKET_NAME)
        blob = client.blob(MODEL_STORAGE_LOCATION)
        blob.download_to_filename('cc_detect_lstm_model.joblib')
        print("Model downloaded from Google Cloud Storage")
        model = joblib.load('cc_detect_lstm_model.joblib')
        return model



if __name__ == "__main__":
    #Instanciate Trainer
    trainer = Trainer()

    #Retrieve data from file
    player_df, game_df, move_df = trainer.get_data(
        source="gcp",
        import_lim=5000
        )

    #Transform data into correct shape
    X, y = trainer.transform_move_data(move_df=move_df,
                                       max_game_length=100,
                                       training=True,
                                       source='gcp')

    #Split Data into train and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        test_size=0.2)

    #Train model
    trainer.train_model(X_train, y_train, verbose=0)

    ##Evaluate model
    trainer.evaluate_model(X_test, y_test, source='gcp')
