import joblib
from settings import NUMERIC_NORMALIZER, CATEGORICAL_TRANSFORMER


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
            print(f"Unknown value found in '{col}': {input_data[col][0]}")

    # StandardScaler for numerical columns
    # num_cols = ['year_of_reference', 'engine_size', 'year_model', 'age_years', 'month_of_reference']
    # input_data[num_cols] = NORMALIZER.transform(input_data[num_cols])

    return input_data

