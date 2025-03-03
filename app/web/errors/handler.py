from typing import TypeVar, Callable

from sqlalchemy.orm.exc import StaleDataError
import structlog

from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from fastapi import Request, status

from web.errors.http_core_error import HttpCoreError
from src.errors.core_errors import CoreErrors
from src.errors.base_error import BaseError
from src.errors.types import ValidationError


BaseErrorType = TypeVar("BaseErrorType", bound=BaseError)


def generate_default_error_handler(errors_map: dict[type[Exception], int]) -> Callable:
    logger = structlog.getLogger(__name__)

    def _default_error_handler(request: Request, exc: Exception) -> JSONResponse:
        if type(exc) in errors_map.keys():
            status_code = errors_map[type(exc)]
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        match exc:
            case BaseError():
                return HttpCoreError(status_code, exc)
            case PydanticValidationError():
                return HttpCoreError(
                    status.HTTP_400_BAD_REQUEST,
                    ValidationError("_error_msg_validation_error", exc),
                )
            case StaleDataError():
                return HttpCoreError(
                    status.HTTP_400_BAD_REQUEST,
                    message="_error_msg_stale_data_error",
                    code=CoreErrors.STALE_DATA_ERROR,
                )
        message = HttpCoreError.SERVER_ERROR_MESSAGE
        if (
            hasattr(exc, "message")
            and exc.message is not None
            and isinstance(exc.message, str)
        ):
            message = exc.message
        else:
            error_args = exc.args
            if (
                isinstance(error_args, tuple)
                and len(error_args) > 0
                and isinstance(error_args[0], str)
            ):
                message = error_args[0]
        logger.exception(repr(exc), exc_info=True)
        return HttpCoreError(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            code=CoreErrors.UNKNOWN.value,
        )

    return _default_error_handler
