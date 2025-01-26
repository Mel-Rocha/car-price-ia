import os
import csv


TRANSFORMER_PATH = os.path.join('artifacts', 'onehotencoder.pkl')
NORMALIZER_PATH = os.path.join('artifacts', 'scaler.pkl')
MODEL_PATH = os.path.join('artifacts', 'randfor_model.pkl')
X_TEST_PATH = os.path.join('data', 'X_test.csv')
ORIGINAL_DF_PATH = os.path.join('data', 'clean_original_df.csv')


class Config:
    valid_brands = set()

    @classmethod
    def load_valid_brands(cls, file_path: str):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                cls.valid_brands.add(row[0])

config = Config()
