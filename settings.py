import csv

import joblib


CATEGORICAL_TRANSFORMER = joblib.load('artifacts/label_encoders.pkl')
NUMERIC_NORMALIZER = joblib.load('artifacts/label_encoders.pkl')
TRAINED_MODEL = joblib.load('artifacts/decision_tree_model.pkl')


class Config:
    valid_models = set()
    valid_brands = set()

    @classmethod
    def load_valid_models(cls, file_path: str):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                cls.valid_models.add(row[0])

    @classmethod
    def load_valid_brands(cls, file_path: str):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                cls.valid_brands.add(row[0])

config = Config()