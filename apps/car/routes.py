import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException

from apps.car.schemas import Car
from settings import TRAINED_MODEL
from apps.car.data_processing import transform_data


MODEL = joblib.load(TRAINED_MODEL)

router = APIRouter()

@router.post("/predict", response_model=float)
async def predict_car_price(car: Car):
    input_data = pd.DataFrame([car.dict()])
    transformed_data = transform_data(input_data.copy())
    predicted_price = MODEL.predict(transformed_data)

    if predicted_price is None:
        raise HTTPException(status_code=400, detail="Prediction failed")

    return predicted_price[0]
