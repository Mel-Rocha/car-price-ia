import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException

from apps.car.schemas import Car
from settings import TRAINED_MODEL
from apps.car.data_processing import transform_data


MODEL = joblib.load(TRAINED_MODEL)

router = APIRouter()


@router.post("/predict", response_model=dict)
async def predict_car_price(car: Car):
    try:
        # Converter o input para DataFrame
        input_data = pd.DataFrame([car.dict()])

        # Transformar os dados
        transformed_data = transform_data(input_data)

        # Fazer a previsão
        predicted_price = MODEL.predict(transformed_data)[0]

        # Formatar o valor em estilo monetário brasileiro
        formatted_prediction = str(int(predicted_price))  # Converte para string e remove decimais

        if len(formatted_prediction) == 7:  # Caso o número tenha 7 dígitos (2 antes do ponto)
            formatted_prediction = formatted_prediction[:2] + "." + formatted_prediction[
                                                                    2:5] + "," + formatted_prediction[5:]
        elif len(formatted_prediction) == 8:  # Caso o número tenha 8 dígitos (3 antes do ponto)
            formatted_prediction = formatted_prediction[:3] + "." + formatted_prediction[
                                                                    3:6] + "," + formatted_prediction[6:]
        else:
            formatted_prediction = formatted_prediction
        return {"predict": formatted_prediction}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer a previsão: {str(e)}")
