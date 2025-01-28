import logging

import pandas as pd
from fastapi import APIRouter, HTTPException, Request, Query

from apps.car.schemas import Car
from apps.car.data_processing import transform_data


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


valid_brands = pd.read_csv('data/valid_brands.csv')


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

        # Formatar o valor em estilo monetário brasileiro
        # Converte para string e remove decimais
        formatted_prediction = str(int(predicted_price))

        if len(
                formatted_prediction) == 7:  # Caso o número tenha 7 dígitos (2 antes do ponto)
            formatted_prediction = formatted_prediction[:2] + "." + \
                formatted_prediction[2:5] + "," + formatted_prediction[5:]
        elif len(formatted_prediction) == 8:  # Caso o número tenha 8 dígitos (3 antes do ponto)
            formatted_prediction = formatted_prediction[:3] + "." + \
                formatted_prediction[3:6] + "," + formatted_prediction[6:]
        else:
            formatted_prediction = formatted_prediction
        return {"predict": formatted_prediction}

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Erro ao fazer a previsão: {str(e)}")


@router.get("/list/brands", response_model=dict)
async def list_brands(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    """
    Listagem páginada de marcas válidas.

    Parâmetros:
    - page: Número da página (default: 1).
    - page_size: Tamanho da página (default: 10).

    Retorna:
    - JSON com a listagem das marcas, número da página, tamanho da página,
      quantidade total de páginas e quantidade total de resultados.
    """
    try:
        if valid_brands is None or valid_brands.empty:
            raise HTTPException(status_code=500, detail="Brands data is not loaded or empty.")

        # Obtendo o nome da primeira coluna
        column_name = valid_brands.columns[0]

        total_results = len(valid_brands)
        total_pages = (total_results + page_size - 1) // page_size

        if page > total_pages:
            page = total_pages

        start = (page - 1) * page_size
        end = start + page_size
        brands_list = valid_brands.iloc[start:end][column_name].tolist()

        return {
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_results": total_results,
            "brands": brands_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing brands: {str(e)}")
