from pydantic import ValidationError as PydanticValidationError

from web.errors.core_errors import CoreErrors
from web.errors.base_error import BaseError
from web.errors.utils import prettify_validation_error


class ValidationError(BaseError):
    def __init__(self, message: str, err: PydanticValidationError):
        super().__init__(message=message, code=CoreErrors.VALIDATION.value, data=prettify_validation_error(err))


class InvalidTokenError(BaseError):
    def __init__(self, code: str):
        super().__init__(message='_error_msg_invalid_auth_token', code=code)
