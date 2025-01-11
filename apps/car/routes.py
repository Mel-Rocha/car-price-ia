from fastapi import APIRouter

from apps.car.schemas import Car

router = APIRouter()

@router.post("/predict", response_model=Car)
async def create_car(car: Car):
    return car