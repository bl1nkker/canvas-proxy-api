from pydantic import ValidationError as PydanticValidationError

from src.errors.core_errors import CoreErrors
from src.errors.base_error import BaseError
from src.errors.utils import prettify_validation_error


class ValidationError(BaseError):
    def __init__(self, message: str, err: PydanticValidationError):
        super().__init__(
            message=message,
            code=CoreErrors.VALIDATION.value,
            data=prettify_validation_error(err),
        )


class InvalidTokenError(BaseError):
    def __init__(self, code: str):
        super().__init__(message="_error_msg_invalid_auth_token", code=code)


class NotFoundError(BaseError):
    def __init__(self, message: str, code: str = CoreErrors.NOT_FOUND.value):
        super().__init__(message=message, code=code)


class InvalidContentTypeError(BaseError):
    def __init__(self, message: str):
        super().__init__(message=message, code=CoreErrors.INVALID_CONTENT_TYPE.value)
