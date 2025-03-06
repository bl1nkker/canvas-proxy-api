from typing import Optional

from fastapi import Cookie

from src.dto import auth_dto


def get_canvas_auth_data(
    _csrf_token: Optional[str] = Cookie(None, alias="_csrf_token"),
    _legacy_normandy_session: Optional[str] = Cookie(
        None, alias="_legacy_normandy_session"
    ),
    _normandy_session: Optional[str] = Cookie(None, alias="_normandy_session"),
    log_session_id: Optional[str] = Cookie(
        None,
    ),
) -> auth_dto.CanvasAuthData:
    return auth_dto.CanvasAuthData(
        _csrf_token=_csrf_token,
        _legacy_normandy_session=_legacy_normandy_session,
        _normandy_session=_normandy_session,
        log_session_id=log_session_id,
    )
