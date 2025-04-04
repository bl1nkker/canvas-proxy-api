import sys
import traceback

from pydantic import BaseModel


class AttendanceProcessError(BaseModel):
    error_type: str
    error_repr: str
    error_traceback: list[str]

    def __init__(self, **kwargs):
        if not kwargs:
            error_type, error_value, error_traceback = sys.exc_info()
            if error_type is not None:
                kwargs["error_type"] = error_type.__name__
                kwargs["error_repr"] = repr(error_value)
                kwargs["error_traceback"] = traceback.format_exception(
                    error_type, error_value, error_traceback
                )

        super().__init__(**kwargs)
