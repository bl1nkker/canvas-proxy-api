from contextlib import asynccontextmanager

from fastapi import FastAPI

from ml.service import MlService


@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_service = MlService()
    try:
        model = ml_service.init_model()
        yield
    finally:
        del model
