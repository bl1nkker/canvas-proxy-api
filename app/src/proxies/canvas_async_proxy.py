import json
import re

import aiohttp
import structlog

from src.dto import (
    attendance_dto,
    auth_dto,
    canvas_assignment_dto,
    canvas_course_dto,
    student_dto,
)
from src.enums.attendance_value import AttendanceValue
from utils.generate_canvas_assignment_data import generate_canvas_assignment_data


def is_student(canvas_course_id: int, user_dict: dict) -> bool:
    course_enrollment = next(
        (
            enrollment
            for enrollment in user_dict.get("enrollments", [])
            if enrollment["course_id"] == canvas_course_id
        ),
        None,
    )
    return (
        course_enrollment["type"] == "StudentEnrollment" if course_enrollment else False
    )


def decode_token(token):
    import urllib

    csrf_token = token
    return urllib.parse.unquote(csrf_token)


def generate_canvas_header(cookies):
    return {
        "Content-Type": "application/json",
        "X-CSRF-Token": decode_token(cookies["_csrf_token"]),
    }


class CanvasAsyncProxy:
    ATTENDANCE_GROUP_NAME = "Сабаққа қатысу/Посещаемость"

    def __init__(self, canvas_domain: str) -> None:
        self._log = structlog.getLogger(__name__)
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
        self._log.info("fetching from Canvas", url=url)
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
        canvas_course_id: int,
    ) -> canvas_assignment_dto.AssignmentGroupCanvas:
        url = (
            f"{self._canvas_domain}/api/v1/courses/{canvas_course_id}/assignment_groups"
        )
        query_params = (
            ("exclude_response_fields[]", "description"),
            ("include[]", "assignments"),
            ("per_page", "100"),
        )
        url = url + "?" + "&".join([f"{param[0]}={param[1]}" for param in query_params])
        self._log.info("fetching from Canvas", url=url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, cookies=cookies) as response:
                response.raise_for_status()
                response_body = await response.json()
                for item in response_body:
                    if item["name"] == self.ATTENDANCE_GROUP_NAME:
                        return (
                            canvas_assignment_dto.AssignmentGroupCanvas.model_validate(
                                item
                            )
                        )
                return None

    async def create_assignment(
        self,
        canvas_course_id: int,
        assignment_group_id: int,
        cookies: dict,
    ) -> canvas_assignment_dto.Read:
        async with aiohttp.ClientSession() as session:
            secure_params = await self._get_assignment_secure_params(
                session=session,
                canvas_course_id=canvas_course_id,
                assignment_group_id=assignment_group_id,
                cookies=cookies,
            )
            data = generate_canvas_assignment_data(
                canvas_course_id=canvas_course_id,
                assignment_group_id=assignment_group_id,
                secure_params=secure_params,
            )
            assignment = await self._create_assignment(
                session=session,
                canvas_course_id=canvas_course_id,
                data=data,
                cookies=cookies,
            )
            return assignment

    async def change_attendance_status(
        self,
        canvas_course_id: int,
        canvas_assignment_id: int,
        canvas_student_id: int,
        cookies: dict,
        attendance_value: str,
    ) -> attendance_dto.CanvasRead:
        url = f"{self._canvas_domain}/api/v1/courses/{canvas_course_id}/assignments/{canvas_assignment_id}/submissions/{canvas_student_id}"
        self._log.info("fetching from Canvas", url=url)
        headers = generate_canvas_header(cookies)
        data = {
            "submission": {
                "assignment_id": canvas_assignment_id,
                "user_id": canvas_student_id,
                "excuse": False,
                "posted_grade": None,
            },
            "include": ["visibility"],
            "prefer_points_over_scheme": False,
            "originator": "gradebook",
        }
        if attendance_value is AttendanceValue.EXCUSE:
            data["submission"]["excuse"] = True
        else:
            data["submission"]["posted_grade"] = attendance_value.value
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url, headers=headers, cookies=cookies, data=json.dumps(data)
            ) as response:
                response.raise_for_status()
                response_body = await response.json()
                return attendance_dto.CanvasRead.model_validate(response_body)

    async def get_course_students(
        self, canvas_course_id: int, cookies: dict
    ) -> list[student_dto.CanvasRead]:
        url = f"{self._canvas_domain}/api/v1/courses/{canvas_course_id}/users?include_inactive=true&include[]=email&include[]=enrollments&per_page=50"
        self._log.info("fetching from Canvas", url=url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, cookies=cookies) as response:
                response.raise_for_status()
                response_body = await response.json()
                students = [
                    student_dto.CanvasRead.model_validate(item)
                    for item in response_body
                    if is_student(canvas_course_id, item)
                ]
                return students

    async def get_student_attendances(
        self, canvas_course_id: int, student_ids: list[int], cookies: dict
    ) -> list[student_dto.CanvasStudentSubmissions]:
        url = f"{self._canvas_domain}/api/v1/courses/{canvas_course_id}/students/submissions?exclude_response_fields[]=preview_url&exclude_response_fields[]=external_tool_url&exclude_response_fields[]=url&grouped=1&response_fields[]=assignment_id&response_fields[]=attachments&response_fields[]=attempt&response_fields[]=cached_due_date&response_fields[]=custom_grade_status_id&response_fields[]=entered_grade&response_fields[]=entered_score&response_fields[]=excused&response_fields[]=grade&response_fields[]=grade_matches_current_submission&response_fields[]=grading_period_id&response_fields[]=id&response_fields[]=late&response_fields[]=late_policy_status&response_fields[]=missing&response_fields[]=points_deducted&response_fields[]=posted_at&response_fields[]=proxy_submitter&response_fields[]=proxy_submitter_id&response_fields[]=redo_request&response_fields[]=score&response_fields[]=seconds_late&response_fields[]=submission_type&response_fields[]=submitted_at&response_fields[]=user_id&response_fields[]=workflow_state&per_page=50"
        for student_id in student_ids:
            url += f"&student_ids[]={student_id}"
        self._log.info("fetching from Canvas", url=url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, cookies=cookies) as response:
                response.raise_for_status()
                response_body = await response.json()
                student_submissions = [
                    student_dto.CanvasStudentSubmissions.model_validate(item)
                    for item in response_body
                ]
                return student_submissions

    async def _get_assignment_secure_params(
        self,
        session: aiohttp.ClientSession,
        canvas_course_id: int,
        assignment_group_id: int,
        cookies: dict,
    ) -> str:
        url = f"{self._canvas_domain}/courses/{canvas_course_id}/assignments/new?submission_types=none&name=&due_at=null&points_possible=0&assignment_group_id={assignment_group_id}"
        self._log.info("fetching from Canvas", url=url)
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
        canvas_course_id: int,
        data: dict,
        cookies: auth_dto.CanvasAuthData,
    ) -> canvas_assignment_dto.CanvasRead:
        url = f"{self._canvas_domain}/api/v1/courses/{canvas_course_id}/assignments"
        self._log.info("fetching from Canvas", url=url)
        cookies = cookies or {}
        headers = generate_canvas_header(cookies)
        async with session.post(
            url, headers=headers, data=json.dumps(data), cookies=cookies
        ) as response:
            response.raise_for_status()
            response_body = await response.json()
            return canvas_assignment_dto.CanvasRead.model_validate(response_body)

    async def _get_basic_cookies(
        self, session: aiohttp.ClientSession, cookies: dict = None
    ) -> dict:
        url = f"{self._canvas_domain}/login/canvas"
        self._log.info("fetching from Canvas", url=url)
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
        self._log.info("fetching from Canvas", url=url)
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
