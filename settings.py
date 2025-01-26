import os
import csv


CATEGORICAL_TRANSFORMER = os.path.join('artifacts', 'onehotencoder.pkl')
NUMERIC_NORMALIZER = os.path.join('artifacts', 'scaler.pkl')
TRAINED_MODEL = os.path.join('artifacts', 'randfor_model.pkl')


class Config:
    valid_brands = set()

    @classmethod
    def load_valid_brands(cls, file_path: str):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                cls.valid_brands.add(row[0])

config = Config()