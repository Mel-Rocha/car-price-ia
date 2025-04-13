import logging
import traceback
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, HTTPException, Request, Query, Path

from apps.car.schemas import Car
from apps.car.utils import format_price
from apps.car.data_processing import transform_data
from apps.car.exceptions import InvalidCategoryException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=dict)
async def predict_car_price(request: Request, car: Car):
    """
    Objetivo:
    - Permitir que o usuário obtenha a previsão de preço de um veículo específico,
      utilizando a combinação de características que desejar.

    Descrição:
    - Essa funcionalidade possibilita previsões para veículos que podem não estar presentes
      em nosso histórico de dados.

    Parâmetros:
    Obrigatórios:
    - request: Objeto de requisição do FastAPI.
    - car: Objeto do tipo Car contendo os dados do carro.

    Retorna:
    - JSON, Um dicionário com a previsão do preço do carro formatado.
    - Em caso de erro, retorna uma mensagem de erro com status code 500.
    """
    try:
        # Converter o input para DataFrame
        input_data = pd.DataFrame([car.dict()])

        MODEL = request.app.state.MODEL
        NORMALIZER = request.app.state.NORMALIZER
        TRANSFORMER = request.app.state.TRANSFORMER
        X_test = request.app.state.X_test
        df = request.app.state.ORIGINAL_DF

        # Transformar os dados
        transformed_data = transform_data(
            input_data, NORMALIZER, TRANSFORMER, X_test, df)

        # Fazer a previsão
        predicted_price = MODEL.predict(transformed_data)[0]

        formatted_prediction = format_price(
            predicted_price)  # Use the utility function
        return {"predict": formatted_prediction}

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Erro ao fazer a previsão: {str(e)}")


@router.get("/list/{category}", response_model=dict)
async def list_category(
    request: Request, category: str, page: int = Query(
        1, ge=1), page_size: int = Query(
            10, ge=1)):
    """
    Objetivo:
    - Listagem páginada de categorias válidas (brand, fuel, gear, bodywork).

    Parâmetros Obrigatórios:
    - category: Categoria a ser listada (brand, fuel, gear, bodywork).

    Parâmetros Opcionais:
    - page: Número da página (default: 1).
    - page_size: Tamanho da página (default: 10).

    Retorna:
    - JSON com a listagem da categoria, número da página, tamanho da página,
      quantidade total de páginas e quantidade total de resultados.
    """
    if category not in InvalidCategoryException.VALID_CATEGORIES:
        raise InvalidCategoryException(category)
    try:
        data_valid = request.app.state.DATA_VALID

        if category not in data_valid.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category: {category}")

        valid_values = data_valid[category].dropna().unique().tolist()

        total_results = len(valid_values)
        total_pages = (total_results + page_size - 1) // page_size

        if page > total_pages:
            page = total_pages

        start = (page - 1) * page_size
        end = start + page_size
        values_list = valid_values[start:end]

        return {
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_results": total_results,
            category: values_list
        }

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error listing {category}: {str(e)}")



@router.get("/list-brands", response_model=dict)
async def list_brands_or_models(
    request: Request,
    brand: str = Query(None, description="Nome da marca (opcional)")
):
    """
    Lista todas as marcas ou os modelos de uma marca específica.

    Parâmetros:
    - brand (str): Nome da marca (opcional).

    Retorna:
    - JSON com a lista de marcas ou modelos.
    """
    try:
        # Carregar o DataFrame de marcas e modelos
        df_brands = request.app.state.BRAND_MODELS

        if brand:
            # Normalizar a entrada da marca
            brand = brand.strip().upper()

            # Verificar se a marca existe no DataFrame
            if brand not in df_brands.columns:
                raise HTTPException(status_code=400, detail="Marca inválida")

            # Listar os modelos da marca
            models = df_brands[brand].dropna().tolist()
            return {"brand": brand, "models": models}

        # Listar todas as marcas
        brands = df_brands.columns.tolist()
        return {"brands": brands}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar: {str(e)}")


@router.post("/brand_predict/{brand}", response_model=dict)
async def brand_predict(request: Request,
                        brand: str = Path(...,
                                          description="Brand")):
    """
    Objetivo:
    - Prever o preço de todos os modelos de uma determinada marca para o próximo ano modelo.

    Descrição:
    - Utilizamos como entrada a **combinação de características mais frequente** para cada modelo,
      garantindo que as previsões sejam baseadas em dados historicamente representativos.

    Parâmetros:
    - brand (str): Nome da marca (obrigatório na URL).

    Retorna:
    - JSON contendo as previsões de preço para todos os modelos da marca,
      considerando os dados de entrada mais comuns no histórico do dataset.
    """
    try:
        brand = brand.upper()
        df_brands = request.app.state.BRAND_MODELS

        if brand not in df_brands.columns:
            raise HTTPException(status_code=400, detail="Marca inválida")

        # Get the list of models for the brand
        models = df_brands[brand].dropna().tolist()

        # Objetos globais do modelo
        MODEL = request.app.state.MODEL
        NORMALIZER = request.app.state.NORMALIZER
        TRANSFORMER = request.app.state.TRANSFORMER
        X_test = request.app.state.X_test
        df = request.app.state.ORIGINAL_DF  # Dados originais do treinamento

        next_year = datetime.now().year + 1
        predictions = []

        for model in models:
            # Filtrar apenas os registros da marca e modelo
            valid_combinations = df[(df["brand"] == brand)
                                    & (df["model"] == model)]

            if valid_combinations.empty:
                continue  # Se não há registros, pula para o próximo modelo

            # Escolher a combinação mais frequente
            most_frequent_combination = valid_combinations.mode().iloc[0]

            input_data = pd.DataFrame({
                'brand': [brand],
                'model': [model],
                'year_model': [next_year],
                'mileage': [most_frequent_combination["mileage"]],
                'gear': [most_frequent_combination["gear"]],
                'fuel': [most_frequent_combination["fuel"]],
                'bodywork': [most_frequent_combination["bodywork"]],
                'city': [most_frequent_combination["city"]],
                'state': [most_frequent_combination["state"]]
            })

            # Transformação dos dados
            transformed_data = transform_data(
                input_data, NORMALIZER, TRANSFORMER, X_test, df)
            predicted_price = MODEL.predict(transformed_data)[0]
            formatted_price = format_price(predicted_price)

            predictions.append({
                "model": model,
                "mileage": most_frequent_combination["mileage"],
                "gear": most_frequent_combination["gear"],
                "fuel": most_frequent_combination["fuel"],
                "bodywork": most_frequent_combination["bodywork"],
                "city": most_frequent_combination["city"],
                "state": most_frequent_combination["state"],
                "predicted_value": formatted_price
            })

        return {
            "brand": brand,
            "year_model": next_year,
            "predictions": predictions
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao fazer a previsão: {str(e)}\n{''.join(tb_str)}")
