from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from asgi_correlation_id import correlation_id
from starlette.requests import Request
from fastapi import FastAPI
import structlog


class LogsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger = structlog.getLogger(__name__)
        request_id = correlation_id.get()
        logger.debug('*** begin request ***', url=request.url, http_request_id=request_id)
        response = await call_next(request)
        logger.debug('*** end request ***', http_request_id=request_id)
        return response
