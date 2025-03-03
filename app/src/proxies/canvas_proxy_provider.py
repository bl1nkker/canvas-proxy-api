from app_config import get_app_config
from src.dto import auth_dto, canvas_dto
from src.proxies.canvas_async_proxy import CanvasAsyncProxy


class CanvasProxyProvider:
    def __init__(self):
        self._proxy = CanvasAsyncProxy(canvas_domain=get_app_config().canvas_domain)

    async def get_auth_data(self, username: str, password: str) -> auth_dto.AuthData:
        return await self._proxy.get_auth_data(username=username, password=password)

    async def get_courses(self, cookies: auth_dto.AuthData) -> canvas_dto.Course:
        return await self._proxy.get_courses(cookies)
