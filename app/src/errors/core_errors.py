from enum import Enum


class CoreErrors(str, Enum):
    AUTH_EXPIRED_TOKEN = "auth_expired_token"
    AUTH_INVALID_CREDENTIALS = "auth_invalid_credentials"
    AUTH_INVALID_TOKEN = "auth_invalid_token"
    AUTH_LOGIN_TAKEN = "auth_login_taken"
    FORBIDDEN = "forbidden"
    INSUFFICIENT_RIGHTS = "insufficient_rights"
    INVALID_CONTENT_TYPE = "invalid_content_type"
    MISSING_PARAM = ("_error_code_missing_param",)
    STALE_DATA_ERROR = "_error_code_stale_data_error"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    UNKNOWN = "unknown"
    VALIDATION = "validation"
    INVALID_DATA = "invalid_data"
    CANVAS_API_ERROR = "canvas_api_error"
