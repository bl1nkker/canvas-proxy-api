import structlog
from asgi_correlation_id import correlation_id
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class LogsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            logger = structlog.getLogger(__name__)
            request_id = correlation_id.get()
            logger.debug(
                "*** begin request ***", url=request.url, http_request_id=request_id
            )
            response = await call_next(request)
        except Exception as ex:
            logger.exception(repr(ex), exc_info=True)
            raise
        finally:
            logger.debug("*** end request ***", http_request_id=request_id)
        return response
