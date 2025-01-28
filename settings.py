import os

import pandas as pd


TRANSFORMER_PATH = os.path.join('artifacts', 'onehotencoder.pkl')
NORMALIZER_PATH = os.path.join('artifacts', 'scaler.pkl')
MODEL_PATH = os.path.join('artifacts', 'randfor_model.pkl')
X_TEST_PATH = os.path.join('data', 'X_test.csv')
ORIGINAL_DF_PATH = os.path.join('data', 'clean_original_df.csv')


class Config:
    valid_brands = set()

    @classmethod
    def load_valid_brands(cls, data_valid: pd.DataFrame):
        """
        Popula o set valid_brands com as marcas únicas do DataFrame carregado.
        """
        cls.valid_brands = set(data_valid['brand'].dropna().unique())

config = Config()
