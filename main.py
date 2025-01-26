import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.car import routes as car_router
from apps.docs import routes as docs_router
from apps.auth.middlewares import AuthMiddleware
from apps.docs.custom_openai import custom_openapi
from settings import config, TRAINED_MODEL, CATEGORICAL_TRANSFORMER, NUMERIC_NORMALIZER, X_TEST_PATH, ORIGINAL_DF


class AppState:
    NORMALIZER: any
    TRANSFORMER: any
    MODEL: any
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
    app.state.NORMALIZER = joblib.load(NUMERIC_NORMALIZER)

    # Carregar o transformador categórico
    app.state.TRANSFORMER = joblib.load(CATEGORICAL_TRANSFORMER)

    # Carregar o modelo treinado
    app.state.MODEL = joblib.load(TRAINED_MODEL)

    # Carregar o conjunto de dados X_test
    app.state.X_test = pd.read_csv(X_TEST_PATH)

    # Carregar o DataFrame original usado para calcular médias dinâmicas
    app.state.ORIGINAL_DF = pd.read_csv(ORIGINAL_DF)
    config.load_valid_brands('data/valid_brands.csv')
