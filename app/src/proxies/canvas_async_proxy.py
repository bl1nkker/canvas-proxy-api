import aiohttp
import urllib.parse
from src.dto import auth_dto


class CanvasAsyncProxy:
    def __init__(self, canvas_domain: str) -> None:
        self._canvas_domain = canvas_domain

    async def get_auth_cookies(
        self, username: str, password: str
    ) -> auth_dto.LoginCookies:
        """
        Полный процесс аутентификации в Canvas:
        1. Первый GET-запрос для получения базовых cookies.
        2. Второй GET-запрос для обновления cookies.
        3. POST-запрос с данными пользователя.
        """
        async with aiohttp.ClientSession() as session:
            basic_cookies = await self._get_basic_cookies(session)
            # some bs, but this is how Canvas works
            updated_basic_cookies = await self._get_basic_cookies(
                session, basic_cookies
            )
            final_cookies = await self._perform_login(
                session, username, password, updated_basic_cookies
            )
            return auth_dto.LoginCookies.model_validate(final_cookies)

    async def _get_basic_cookies(
        self, session: aiohttp.ClientSession, cookies: dict = None
    ) -> dict:
        url = f"{self._canvas_domain}/login/canvas"
        cookies = cookies or {}
        async with session.get(url, cookies=cookies) as response:
            response.raise_for_status()
            updated_cookies = {k: v.value for k, v in response.cookies.items()}
            cookies.update(updated_cookies)
            return cookies

    async def _perform_login(
        self, session: aiohttp.ClientSession, email: str, password: str, cookies: dict
    ) -> dict:
        url = f"{self._canvas_domain}/login/canvas"
        csrf_token = urllib.parse.unquote(cookies.get("_csrf_token", ""))
        if not csrf_token:
            raise ValueError("CSRF-токен не найден в cookies")

        data = {
            "authenticity_token": csrf_token,
            "pseudonym_session[unique_id]": email,
            "pseudonym_session[password]": password,
        }

        async with session.post(url, data=data, cookies=cookies) as response:
            response.raise_for_status()
            final_cookies = {k: v.value for k, v in response.cookies.items()}
            cookies.update(final_cookies)
            return cookies
