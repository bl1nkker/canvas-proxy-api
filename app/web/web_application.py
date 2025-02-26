from typing import Type
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine.base import Engine

from db.session import Session
from web.middlewares.log_middleware import LogsMiddleware
from src.errors.types import InvalidContentTypeError, NotFoundError, ValidationError, InvalidTokenError
from web.errors.handler import generate_default_error_handler

from ml import lifespan


def create_web_application(
    db_engine: Engine,
    errors_mapping: dict[Type[Exception], int] | None = None,
) -> FastAPI:
    Session.configure(bind=db_engine)
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(LogsMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    em: dict[Type[Exception], int] = {
        ValidationError: status.HTTP_400_BAD_REQUEST,
        InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
        InvalidContentTypeError: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        NotFoundError: status.HTTP_404_NOT_FOUND,
    }
    em.update(errors_mapping or dict())
    app.add_exception_handler(Exception, generate_default_error_handler(em))
    return app
