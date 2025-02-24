from typing import Type, Any

from fastapi import FastAPI

# from db.session import Session
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware


def create_web_application(
    app: FastAPI | None = None,
    errors_mapping: dict[Type[Exception], int] | None = None,
    middlewares: tuple[tuple[BaseHTTPMiddleware, dict]] | None = None,
    **kwargs: Any,
) -> FastAPI:
    # Session.configure(bind=db_engine)
    if app is None:
        app = FastAPI(**kwargs)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
