from pydantic import BaseModel, validator

from settings import config


class Car(BaseModel):
    brand: str
    model: str
    year_model: int
    mileage: int
    gear: str
    fuel: str
    bodywork: str
    city: str
    state: str


    @validator('brand')
    def validate_brand(cls, value):
        if value not in config.valid_brands:
            raise ValueError(f'Invalid brand: {value}. Enter a brand present in the valid_brands.csv file')
        return value
