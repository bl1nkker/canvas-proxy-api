from fastapi.responses import JSONResponse

from src.errors.core_errors import CoreErrors
from src.errors.base_error import BaseError


class HttpCoreError(JSONResponse):
    SERVER_ERROR_MESSAGE = 'lsse_server_error'

    def __init__(
        self, status: int, err: BaseError | None = None,
        *, message: str | None = None, code: str | None = None
    ) -> None:
        _message = err.message if err is not None else message if message is not None else self.SERVER_ERROR_MESSAGE
        _code = err.code if err is not None else code if code is not None else CoreErrors.UNKNOWN.value
        data = err.data if err is not None and err.data is not None else None
        response_payload: dict[str, str | dict[str, str]] = {'message': _message, 'code': _code}
        if data is not None:
            response_payload['data'] = data
        super().__init__(status_code=status, content=response_payload)
        self._err = err
