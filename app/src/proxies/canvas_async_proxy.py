import json
import re

import aiohttp

from src.dto import auth_dto, canvas_assignment_dto, canvas_course_dto
from utils.generate_canvas_assignment_data import generate_canvas_assignment_data


def decode_token(token):
    import urllib

    csrf_token = token
    return urllib.parse.unquote(csrf_token)


class CanvasAsyncProxy:
    ATTENDANCE_GROUP_NAME = "Сабаққа қатысу/Посещаемость"

    def __init__(self, canvas_domain: str) -> None:
        self._canvas_domain = canvas_domain

    async def get_auth_data(
        self, username: str, password: str
    ) -> auth_dto.CanvasAuthData:
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
            return auth_dto.CanvasAuthData.model_validate(final_cookies)

    async def get_courses(self, cookies: dict) -> canvas_course_dto.Read:
        url = f"{self._canvas_domain}/api/v1/dashboard/dashboard_cards"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, cookies=cookies) as response:
                response.raise_for_status()
                response_body = await response.json()
                return [
                    canvas_course_dto.Read.from_dict(item) for item in response_body
                ]

    async def get_attendance_assignment_group(
        self,
        cookies: dict,
        course_id: int,
    ) -> canvas_assignment_dto.AssignmentGroup:
        url = f"{self._canvas_domain}/api/v1/courses/{course_id}/assignment_groups"
        query_params = (
            ("exclude_response_fields[]", "description"),
            ("include[]", "assignments"),
            ("per_page", "100"),
        )
        url = url + "?" + "&".join([f"{param[0]}={param[1]}" for param in query_params])
        async with aiohttp.ClientSession() as session:
            async with session.get(url, cookies=cookies) as response:
                response.raise_for_status()
                response_body = await response.json()
                return [
                    canvas_assignment_dto.AssignmentGroup.model_validate(item)
                    for item in response_body
                    if item["name"] == self.ATTENDANCE_GROUP_NAME
                ][0]

    async def create_assignment(
        self,
        course_id: int,
        assignment_group_id: int,
        cookies: dict,
    ) -> canvas_assignment_dto.Assignment:
        async with aiohttp.ClientSession() as session:
            secure_params = await self._get_assignment_secure_params(
                session=session,
                course_id=course_id,
                assignment_group_id=assignment_group_id,
                cookies=cookies,
            )
            data = generate_canvas_assignment_data(
                course_id=course_id,
                assignment_group_id=assignment_group_id,
                secure_params=secure_params,
            )
            assignment = await self._create_assignment(
                session=session, course_id=course_id, data=data, cookies=cookies
            )
            return assignment

    async def _get_assignment_secure_params(
        self,
        session: aiohttp.ClientSession,
        course_id: int,
        assignment_group_id: int,
        cookies: dict,
    ) -> str:
        url = f"{self._canvas_domain}/courses/{course_id}/assignments/new?submission_types=none&name=&due_at=null&points_possible=0&assignment_group_id={assignment_group_id}"
        cookies = cookies or {}
        async with session.get(url, cookies=cookies) as response:
            response.raise_for_status()
            # Parse Canvas HTML and find the "secure_params" token
            html = await response.text()
            match = re.search(r'"secure_params"\s*:\s*"([^"]+)"', html)
            return match.group(1)

    async def _create_assignment(
        self,
        session: aiohttp.ClientSession,
        course_id: int,
        data: dict,
        cookies: auth_dto.CanvasAuthData,
    ) -> canvas_assignment_dto.Assignment:
        url = f"{self._canvas_domain}/api/v1/courses/{course_id}/assignments"
        cookies = cookies or {}
        headers = {
            "Content-Type": "application/json",
            "X-CSRF-Token": decode_token(cookies["_csrf_token"]),
        }
        async with session.post(
            url, headers=headers, data=json.dumps(data), cookies=cookies
        ) as response:
            response.raise_for_status()
            response_body = await response.json()
            return canvas_assignment_dto.Assignment.model_validate(response_body)

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
        csrf_token = decode_token(cookies.get("_csrf_token", ""))
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
