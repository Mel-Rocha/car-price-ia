from pydantic import BaseModel, validator

from settings import config


class Car(BaseModel):
    year_of_reference: int
    month_of_reference: int
    engine_size: float
    year_model: int
    age_years: int
    fuel: str
    gear: str
    brand: str
    model: str

    @validator('fuel')
    def validate_fuel(cls, value):
        allowed_fuels = ['Alcohol', 'Diesel', 'Gasoline']
        if value not in allowed_fuels:
            raise ValueError(f'Invalid fuel type: {value}. Allowed values are: {allowed_fuels}')
        return value

    @validator('gear')
    def validate_gear(cls, value):
        allowed_gears = ['automatic', 'manual']
        if value not in allowed_gears:
            raise ValueError(f'Invalid gear type: {value}. Allowed values are: {allowed_gears}')
        return value

    @validator('model')
    def validate_model(cls, value):
        if value not in config.valid_models:
            raise ValueError(f'Invalid model: {value}. Enter a model present in the valid_models.csv file')
        return value