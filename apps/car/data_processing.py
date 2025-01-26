import logging

import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def transform_data(input_data: pd.DataFrame, NORMALIZER: StandardScaler,
                   TRANSFORMER: OneHotEncoder, X_test: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    # Adicionar features calculadas
    current_year = pd.Timestamp.now().year
    input_data['age_years'] = current_year - input_data['year_model']

    # Calcular médias dinâmicas com base nos dados
    input_data['brand_avg_price'] = input_data['brand'].apply(
        lambda x: df[df['brand'] == x]['price'].mean() if x in df['brand'].values else 0
    )
    input_data['state_avg_price'] = input_data['state'].apply(
        lambda x: df[df['state'] == x]['price'].mean() if x in df['state'].values else 0
    )
    input_data['city_avg_price'] = input_data['city'].apply(
        lambda x: df[df['city'] == x]['price'].mean() if x in df['city'].values else 0
    )

    # Calcular desvio de preço
    def calculate_price_deviation(row):
        group = df[(df['model'] == row['model']) & (df['year_model'] == row['year_model'])]
        group_avg_price = group['price'].mean() if not group.empty else 0
        return group_avg_price - row['brand_avg_price']

    input_data['price_deviation'] = input_data.apply(calculate_price_deviation, axis=1)

    # Identificar marcas de luxo
    input_data['is_luxury_brand'] = input_data['brand'].apply(
        lambda x: 1 if x in ['AUDI', 'BMW', 'MERCEDES', 'PORSCHE'] else 0
    )

    # Separar colunas categóricas e numéricas
    categorical_columns = ['brand', 'model', 'gear', 'fuel', 'bodywork', 'city', 'state']
    numerical_columns = ['year_model', 'mileage', 'age_years', 'price_deviation',
                         'brand_avg_price', 'state_avg_price', 'city_avg_price', 'is_luxury_brand']

    # Aplicar OneHotEncoder
    encoded_categorical = TRANSFORMER.transform(input_data[categorical_columns])
    encoded_categorical_df = pd.DataFrame(
        encoded_categorical,
        columns=TRANSFORMER.get_feature_names_out(categorical_columns),
        index=input_data.index
    )

    # Normalizar colunas numéricas
    normalized_numeric = NORMALIZER.transform(input_data[numerical_columns])
    normalized_numeric_df = pd.DataFrame(
        normalized_numeric,
        columns=numerical_columns,
        index=input_data.index
    )

    # Concatenar as colunas normalizadas e codificadas
    final_input_df = pd.concat([normalized_numeric_df, encoded_categorical_df], axis=1)

    # Garantir consistência com o treinamento
    missing_columns = set(X_test.columns) - set(final_input_df.columns)
    for col in missing_columns:
        final_input_df[col] = 0
    final_input_df = final_input_df[X_test.columns]  # Ordenar as colunas

    return final_input_df
