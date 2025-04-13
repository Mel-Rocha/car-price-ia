import os

import pandas as pd


TRANSFORMER_PATH = os.path.join('artifacts', 'onehotencoder.pkl')
NORMALIZER_PATH = os.path.join('artifacts', 'scaler.pkl')
MODEL_PATH = os.path.join('artifacts', 'randfor_model.pkl')
X_TEST_PATH = os.path.join('data', 'X_test.csv')
ORIGINAL_DF_PATH = os.path.join('data', 'clean_original_df.csv')


class Config:
    valid_brands = []

    @classmethod
    def load_valid_brands(cls, data_valid: pd.DataFrame):
        """
        Populates the valid_brands list with the column names of the DataFrame.
        """
        cls.valid_brands = list(data_valid.columns)


config = Config()
