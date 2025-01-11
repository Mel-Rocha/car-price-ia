from fastapi import APIRouter

from apps.car.schemas import Car

router = APIRouter()

@router.get("/car", response_model=Car)
async def get_car():
    return {
        "year_of_reference": 2023,
        "month_of_reference": 10,
        "engine_size": 2.0,
        "year_model": 2023,
        "age_years": 0,
        "fuel": "Gasoline",
        "gear": "Automatic",
        "brand": "Toyota",
        "model": "Corolla"
    }