from src.dto import auth_dto
from src.proxies.canvas_proxy_provider import CanvasProxyProvider


class AuthService:
    def __init__(self, canvas_proxy_provider_cls=CanvasProxyProvider):
        self._canvas_proxy_provider = canvas_proxy_provider_cls()

    async def login(self, dto: auth_dto.LoginCredentials) -> auth_dto.LoginCookies:
        cookies = await self._canvas_proxy_provider.get_auth_cookies(
            username=dto.username, password=dto.password
        )
        return cookies
