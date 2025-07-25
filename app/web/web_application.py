from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine.base import Engine

from db.session import Session
from ml import lifespan
from src.errors.types import (
    InvalidContentTypeError,
    InvalidCredentialsError,
    InvalidDataError,
    InvalidTokenError,
    NotFoundError,
    ValidationError,
)
from web.errors.handler import generate_default_error_handler
from web.middlewares.log_middleware import LogsMiddleware
from web.middlewares.profiler_middleware import ProfilerMiddleware


def create_web_application(
    db_engine: Engine,
    errors_mapping: dict[type[Exception], int] | None = None,
) -> FastAPI:
    Session.configure(bind=db_engine)
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(LogsMiddleware)
    app.add_middleware(ProfilerMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    em: dict[type[Exception], int] = {
        ValidationError: status.HTTP_400_BAD_REQUEST,
        InvalidDataError: status.HTTP_400_BAD_REQUEST,
        InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
        InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
        InvalidContentTypeError: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        NotFoundError: status.HTTP_404_NOT_FOUND,
    }
    em.update(errors_mapping or dict())
    app.add_exception_handler(Exception, generate_default_error_handler(em))
    return app
