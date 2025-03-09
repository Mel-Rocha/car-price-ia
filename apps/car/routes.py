import logging
import traceback
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, HTTPException, Request, Query, Path

from apps.car.utils import format_price
from apps.car.schemas import Car, BrandPredict
from apps.car.data_processing import transform_data
from apps.car.exceptions import InvalidCategoryException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=dict)
async def predict_car_price(request: Request, car: Car):
    """
        Objetivo:
        - prever o preço de um carro.

        Descrição:
        - Este endpoint recebe os dados de um carro, transforma esses dados usando
        normalização e codificação, e então usa um modelo treinado para prever o
        preço do carro. O preço previsto é formatado no estilo monetário brasileiro.

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


@router.post("/brand_predict/{brand}", response_model=dict)
async def brand_predict(request: Request,
                        params: BrandPredict,
                        brand: str = Path(...,
                                          description="Brand")):
    """
    Objetivo:
    - Prever o preço de todos os modelos de uma marca para o próximo ano modelo.

    Parâmetros:
    - brand: marca (obrigatório na URL).
    - params: Parâmetros comuns para todos os modelos da marca (JSON).

    Retorna:
    - JSON com as previsões para todos os modelos da marca.
    """
    try:
        brand = brand.upper()
        df_brands = request.app.state.BRAND_MODELS

        if brand not in df_brands.columns:
            raise HTTPException(status_code=400, detail="Marca inválida")

        # Get the list of models for the brand
        models = df_brands[brand].dropna().tolist()

        # Obter objetos globaison
        MODEL = request.app.state.MODEL
        NORMALIZER = request.app.state.NORMALIZER
        TRANSFORMER = request.app.state.TRANSFORMER
        X_test = request.app.state.X_test
        df = request.app.state.ORIGINAL_DF

        next_year = datetime.now().year + 1
        predictions = []

        for model in models:
            input_data = pd.DataFrame({
                'brand': [brand],
                'model': [model],
                'year_model': [next_year],
                'mileage': [params.mileage],
                'gear': [params.gear],
                'fuel': [params.fuel],
                'bodywork': [params.bodywork],
                'city': [params.city],
                'state': [params.state]
            })

            # Transformação dos dados
            transformed_data = transform_data(
                input_data, NORMALIZER, TRANSFORMER, X_test, df)
            predicted_price = MODEL.predict(transformed_data)[0]
            formatted_price = format_price(
                predicted_price)  # Use the utility function

            predictions.append(
                {"model": model, "predicted_value": formatted_price})

        return {
            "brand": brand,
            "year_model": next_year,
            "predictions": predictions}

    except HTTPException as e:
        raise e
    except Exception as e:
        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao fazer a previsão: {str(e)}\n{''.join(tb_str)}")
