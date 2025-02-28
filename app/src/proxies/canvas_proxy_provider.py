from app_config import get_app_config

from src.proxies.canvas_async_proxy import CanvasAsyncProxy
from src.dto import auth_dto


class CanvasProxyProvider:
    def __init__(self):
        self._proxy = CanvasAsyncProxy(canvas_domain=get_app_config().canvas_domain)

    async def get_auth_cookies(
        self, username: str, password: str
    ) -> auth_dto.LoginCookies:
        return await self._proxy.get_auth_cookies(username=username, password=password)
