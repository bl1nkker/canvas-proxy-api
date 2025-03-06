from src.dto import auth_dto, canvas_assignment_dto
from src.errors.types import NotFoundError
from src.proxies.canvas_proxy_provider import CanvasProxyProvider
from src.repositories.canvas_course_repo import CanvasCourseRepo


class CanvasAssignmentService:
    def __init__(
        self,
        canvas_course_repo: CanvasCourseRepo,
        canvas_proxy_provider_cls=CanvasProxyProvider,
    ):
        self._canvas_proxy_provider = canvas_proxy_provider_cls()
        self._canvas_course_repo = canvas_course_repo

    async def get_attendance_assignment_group(
        self, web_id: str, canvas_auth_data: auth_dto.CanvasAuthData
    ) -> canvas_assignment_dto.AssignmentGroup:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=web_id)
            if not course:
                raise NotFoundError(message=f"_err_message_course_not_found:{web_id}")
        group = await self._canvas_proxy_provider.get_attendance_assignment_group(
            cookies=canvas_auth_data, course_id=course.canvas_course_id
        )
        return group

    async def create_assignment(
        self,
        web_id: str,
        dto: canvas_assignment_dto.Create,
        canvas_auth_data: auth_dto.CanvasAuthData,
    ) -> canvas_assignment_dto.Assignment:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=web_id)
            if not course:
                raise NotFoundError(message=f"_err_message_course_not_found:{web_id}")
        assignment = await self._canvas_proxy_provider.create_assignment(
            course_id=course.canvas_course_id,
            assignment_group_id=dto.assignment_group_id,
            cookies=canvas_auth_data,
        )
        return assignment
