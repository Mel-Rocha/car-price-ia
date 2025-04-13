import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from apps.car import routes as car_router
from apps.docs import routes as docs_router
from apps.auth.middlewares import AuthMiddleware
from apps.docs.custom_openai import custom_openapi
from settings import config, MODEL_PATH, NORMALIZER_PATH, TRANSFORMER_PATH, X_TEST_PATH, ORIGINAL_DF_PATH


class AppState:
    NORMALIZER: StandardScaler
    TRANSFORMER: OneHotEncoder
    MODEL: RandomForestRegressor
    X_test: pd.DataFrame
    ORIGINAL_DF: pd.DataFrame


def create_application() -> FastAPI:
    application = FastAPI()

    application.add_middleware(AuthMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=[
            "DELETE",
            "GET",
            "OPTIONS",
            "PATCH",
            "POST",
            "PUT",
        ],
        allow_headers=["*"]
    )

    application.include_router(docs_router.router, tags=['car'])
    application.include_router(car_router.router, prefix="/car",
                               tags=['car'])

    return application


app = create_application()

app.openapi = lambda: custom_openapi(app)


@app.on_event('startup')
async def startup_event():
    app.state = AppState()

    app.state.NORMALIZER = joblib.load(NORMALIZER_PATH)
    app.state.TRANSFORMER = joblib.load(TRANSFORMER_PATH)
    app.state.MODEL = joblib.load(MODEL_PATH)
    app.state.X_test = pd.read_csv(X_TEST_PATH)
    app.state.ORIGINAL_DF = pd.read_csv(ORIGINAL_DF_PATH)
    app.state.DATA_VALID = pd.read_csv('data/data_valid.csv')
    app.state.BRAND_MODELS = pd.read_csv('data/brand_models.csv')
    app.state.STATE_CITIES = pd.read_csv('data/state_cities.csv')

    config.load_valid_brands(app.state.BRAND_MODELS)
