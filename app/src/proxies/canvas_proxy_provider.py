from app.src.proxies.canvas_async_proxy import CanvasAsyncProxy
from src.dto import canvas_dto
from app_config import get_app_config


class CanvasProxyProvider:
    def __init__(self):
        self._proxy = CanvasAsyncProxy(canvas_domain=get_app_config().canvas_domain)
    
    async def get_auth_cookies(self, email: str, password: str) -> canvas_dto.LoginCookies:
        return await self._proxy.get_auth_cookies(email=email, password=password)