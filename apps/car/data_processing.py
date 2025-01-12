import logging

import joblib
from settings import NUMERIC_NORMALIZER, CATEGORICAL_TRANSFORMER


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


NORMALIZER = joblib.load(NUMERIC_NORMALIZER)
TRANSFORMER = joblib.load(CATEGORICAL_TRANSFORMER)


def transform_data(input_data):
    # Label Encoding for categorical columns
    cat_cols = ['fuel', 'gear', 'brand', 'model']
    for col in cat_cols:
        try:
            input_data[col] = TRANSFORMER[col].transform(input_data[col].astype(str))
        except ValueError:
            input_data[col] = -1
            logger.error(f"Unknown value found in '{col}': {input_data[col][0]}")

    # StandardScaler for numerical columns
    num_cols = ['year_of_reference', 'engine_size', 'year_model', 'age_years', 'month_of_reference']
    for col in num_cols:
        try:
            input_data[col] = NORMALIZER.transform(input_data[[col]])
        except ValueError:
            input_data[col] = -1
            logger.error(f"Unknown value found in '{col}': {input_data[col][0]}")

    return input_data
