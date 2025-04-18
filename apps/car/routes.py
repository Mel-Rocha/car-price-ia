import logging
import traceback

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


@router.post("/brand_predict/{brand}", response_model=dict)
async def brand_predict(
    request: Request,
    brand: str = Path(..., description="Brand"),
    page: int = Query(1, ge=1, description="Page number (default: 1)"),
    page_size: int = Query(10, ge=1, description="Number of items per page (default: 10)")
):
    """
    Predicts the price of all models of a specific brand for the next model year.

    Parameters:
    - brand (str): Brand name (required in the URL).
    - page (int): Page number for pagination (default: 1).
    - page_size (int): Number of items per page for pagination (default: 10).

    Returns:
    - JSON containing price predictions for the specified page.
    """
    try:
        brand = brand.upper()
        brand_models_bodywork = request.app.state.BRAND_MODELS_BODYWORK

        if brand not in brand_models_bodywork:
            raise HTTPException(status_code=400, detail="Invalid brand")

        # Get the models and bodywork for the brand
        models = list(brand_models_bodywork[brand].keys())

        # Pagination logic
        total_results = len(models)
        total_pages = (total_results + page_size - 1) // page_size

        if page > total_pages:
            page = total_pages

        start = (page - 1) * page_size
        end = start + page_size
        paginated_models = models[start:end]

        # Global model objects
        MODEL = request.app.state.MODEL
        NORMALIZER = request.app.state.NORMALIZER
        TRANSFORMER = request.app.state.TRANSFORMER
        X_test = request.app.state.X_test
        df = request.app.state.ORIGINAL_DF  # Training dataset

        predictions = []

        for model in paginated_models:
            # Filter records for the brand and model
            valid_combinations = df[(df["brand"] == brand)
                                    & (df["model"] == model)]

            if valid_combinations.empty:
                continue  # Skip if no records exist

            # Choose the most frequent combination
            most_frequent_combination = valid_combinations.mode().iloc[0]

            input_data = pd.DataFrame({
                'brand': [brand],
                'model': [model],
                'year_model': [most_frequent_combination['year_model']],
                'mileage': [most_frequent_combination["mileage"]],
                'gear': [most_frequent_combination["gear"]],
                'fuel': [most_frequent_combination["fuel"]],
                'bodywork': [most_frequent_combination["bodywork"]],
                'city': [most_frequent_combination["city"]],
                'state': [most_frequent_combination["state"]]
            })

            # Transform the data
            transformed_data = transform_data(
                input_data, NORMALIZER, TRANSFORMER, X_test, df)
            predicted_price = MODEL.predict(transformed_data)[0]
            formatted_price = format_price(predicted_price)

            predictions.append({
                "model": model,
                "year_model": int(most_frequent_combination["year_model"]),
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
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_results": total_results,
            "predictions": predictions
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao fazer a previsão: {str(e)}\n{''.join(tb_str)}")


@router.get("/list/{category}", response_model=dict)
async def list_category(
    request: Request, category: str, page: int = Query(
        1, ge=1), page_size: int = Query(
            10, ge=1)):
    """
    Objetivo:
    - Listagem páginada de categorias válidas (fuel, gear).

    Parâmetros Obrigatórios:
    - category: Categoria a ser listada  (fuel, gear).

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
async def list_brands_models_bodyworks(
    request: Request,
    brand: str = Query(None, description="Brand name (optional)"),
    model: str = Query(None, description="Model name (optional)")
):
    """
    Lists all brands, models of a brand, or bodyworks of a model.

    Parameters:
    - brand (str): Brand name (optional).
    - model (str): Model name (optional).

    Returns:
    - JSON with the list of brands, models, or bodyworks.
    """
    try:
        # Access the BRAND_MODELS_BODYWORK data
        brand_models_bodywork = request.app.state.BRAND_MODELS_BODYWORK

        if not brand:
            # List all brands
            return {"brands": list(brand_models_bodywork.keys())}

        brand = brand.strip().upper()
        if brand not in brand_models_bodywork:
            raise HTTPException(status_code=400, detail="Invalid brand")

        if not model:
            # List all models of the brand
            return {
                "brand": brand, "models": list(
                    brand_models_bodywork[brand].keys())}

        model = model.strip().upper()
        if model not in brand_models_bodywork[brand]:
            raise HTTPException(status_code=400,
                                detail="Invalid model for the specified brand")

        # List all bodyworks of the model
        return {
            "brand": brand,
            "model": model,
            "bodyworks": brand_models_bodywork[brand][model]}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing brands, models, or bodyworks: {str(e)}"
        )


@router.get("/list-states", response_model=dict)
async def list_states_or_cities(
    request: Request,
    state: str = Query(None, description="Nome do estado (opcional)")
):
    """
    Lista todos os estados ou as cidades de um estado específico.

    Parâmetros:
    - state (str): Nome do estado (opcional).

    Retorna:
    - JSON com a lista de estados ou cidades.
    """
    try:
        # Carregar o DataFrame de estados e cidades
        df_states = request.app.state.STATE_CITIES

        if state:
            # Normalizar a entrada do estado
            state = state.strip().upper()

            # Verificar se o estado existe no DataFrame
            if state not in df_states.columns:
                raise HTTPException(status_code=400, detail="Estado inválido")

            # Listar as cidades do estado
            cities = df_states[state].dropna().tolist()
            return {"state": state, "cities": cities}

        # Listar todos os estados
        states = df_states.columns.tolist()
        return {"states": states}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar: {str(e)}")
