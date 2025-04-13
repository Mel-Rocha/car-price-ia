import os
import json


TRANSFORMER_PATH = os.path.join('artifacts', 'onehotencoder.pkl')
NORMALIZER_PATH = os.path.join('artifacts', 'scaler.pkl')
MODEL_PATH = os.path.join('artifacts', 'randfor_model.pkl')
X_TEST_PATH = os.path.join('data', 'X_test.csv')
ORIGINAL_DF_PATH = os.path.join('data', 'clean_original_df.csv')
BRAND_MODELS_BODYWORK_PATH = os.path.join('data', 'brand_model_bodywork.json')


class Config:
    valid_brands = []
    brand_models_bodywork = {}

    @classmethod
    def load_valid_brands(cls, json_path: str):
        """
        Loads the valid brands and models from the JSON file.
        """
        with open(json_path, 'r') as file:
            cls.brand_models_bodywork = json.load(file)
        cls.valid_brands = list(cls.brand_models_bodywork.keys())


config = Config()
