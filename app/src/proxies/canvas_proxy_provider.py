from app_config import get_app_config
from src.dto import auth_dto, canvas_assignment_dto, canvas_course_dto
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

    async def get_attendance_assignment_group(
        self, course_id: int, cookies: auth_dto.CanvasAuthData
    ) -> canvas_assignment_dto.AssignmentGroup:
        return await self._proxy.get_attendance_assignment_group(
            cookies=cookies.model_dump(by_alias=True), course_id=course_id
        )

    async def create_assignment(
        self, course_id: int, assignment_group_id: int, cookies: auth_dto.CanvasAuthData
    ):
        return await self._proxy.create_assignment(
            course_id=course_id,
            assignment_group_id=assignment_group_id,
            cookies=cookies.model_dump(by_alias=True),
        )
