from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.car import routes as car_router
from apps.docs import routes as docs_router
from apps.auth.middlewares import AuthMiddleware
from apps.docs.custom_openai import custom_openapi
from settings import config


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
    config.load_valid_models('data/valid_models.csv')
