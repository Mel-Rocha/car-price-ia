from pydantic import BaseModel


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
