from app_config import get_app_config
from src.dto import (
    attendance_dto,
    auth_dto,
    canvas_assignment_dto,
    canvas_course_dto,
    student_dto,
)
from src.proxies.canvas_async_proxy import CanvasAsyncProxy


class CanvasProxyProvider:
    def __init__(self):
        self._proxy = CanvasAsyncProxy(canvas_domain=get_app_config().canvas_domain)

    async def get_auth_data(
        self, username: str, password: str
    ) -> auth_dto.CanvasAuthData:
        return await self._proxy.get_auth_data(username=username, password=password)

    async def get_courses(
        self, cookies: auth_dto.CanvasAuthData
    ) -> canvas_course_dto.Read:
        return await self._proxy.get_courses(
            cookies=cookies.model_dump(by_alias=True),
        )

    async def get_course_students(
        self, canvas_course_id: int, cookies: auth_dto.CanvasAuthData
    ) -> list[student_dto.CanvasRead]:
        return await self._proxy.get_course_students(
            canvas_course_id=canvas_course_id,
            cookies=cookies.model_dump(by_alias=True),
        )

    async def get_attendance_assignment_group(
        self, canvas_course_id: int, cookies: auth_dto.CanvasAuthData
    ) -> canvas_assignment_dto.AssignmentGroupCanvas:
        return await self._proxy.get_attendance_assignment_group(
            cookies=cookies.model_dump(by_alias=True), canvas_course_id=canvas_course_id
        )

    async def create_assignment(
        self,
        canvas_course_id: int,
        canvas_assignment_group_id: int,
        cookies: auth_dto.CanvasAuthData,
    ):
        return await self._proxy.create_assignment(
            canvas_course_id=canvas_course_id,
            assignment_group_id=canvas_assignment_group_id,
            cookies=cookies.model_dump(by_alias=True),
        )

    async def change_attendance_status(
        self,
        canvas_course_id: int,
        canvas_assignment_id: int,
        canvas_student_id: int,
        cookies: auth_dto.CanvasAuthData,
        attendance_value: str,
    ) -> attendance_dto.CanvasRead:
        return await self._proxy.change_attendance_status(
            canvas_course_id=canvas_course_id,
            canvas_assignment_id=canvas_assignment_id,
            canvas_student_id=canvas_student_id,
            cookies=cookies.model_dump(by_alias=True),
            attendance_value=attendance_value,
        )

    async def get_student_attendances(
        self,
        canvas_course_id: int,
        student_ids: list[int],
        cookies: auth_dto.CanvasAuthData,
    ):
        return await self._proxy.get_student_attendances(
            canvas_course_id=canvas_course_id,
            student_ids=student_ids,
            cookies=cookies.model_dump(by_alias=True),
        )
