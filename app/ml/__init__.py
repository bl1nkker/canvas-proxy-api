from contextlib import asynccontextmanager

from fastapi import FastAPI

from ml.service import MlService


@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_service = MlService()
    try:
        ml_service.init_model(model_name="Facenet512")
        ml_service.init_model(model_name="VGG-Face")
        mobile_model = ml_service.init_model(model_name="Mobile")
        yield
    finally:
        mobile_model.clear()
