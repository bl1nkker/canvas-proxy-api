import shortuuid

from src.dto import attendance_dto, auth_dto, canvas_assignment_dto
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.errors.types import NotFoundError
from src.models.assignment import Assignment
from src.proxies.canvas_proxy_provider import CanvasProxyProvider
from src.repositories.assignment_repo import AssignmentRepo
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.services.attendance_service import AttendanceService


class CanvasAssignmentService:
    def __init__(
        self,
        attendance_service: AttendanceService,
        canvas_course_repo: CanvasCourseRepo,
        assignment_repo: AssignmentRepo,
        canvas_proxy_provider_cls=CanvasProxyProvider,
    ):
        self._canvas_proxy_provider = canvas_proxy_provider_cls()
        self._canvas_course_repo = canvas_course_repo
        self._assignment_repo = assignment_repo
        self._attendance_service = attendance_service

    async def get_attendance_assignment_group(
        self, web_id: str, canvas_auth_data: auth_dto.CanvasAuthData
    ) -> canvas_assignment_dto.AssignmentGroup:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=web_id)
            if not course:
                raise NotFoundError(message=f"_err_message_course_not_found:{web_id}")
        group = await self._canvas_proxy_provider.get_attendance_assignment_group(
            cookies=canvas_auth_data, canvas_course_id=course.canvas_course_id
        )
        return group

    async def create_assignment(
        self,
        web_id: str,
        dto: canvas_assignment_dto.Create,
        canvas_auth_data: auth_dto.CanvasAuthData,
    ) -> canvas_assignment_dto.Read:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=web_id)
            if not course:
                raise NotFoundError(message=f"_err_message_course_not_found:{web_id}")
        canvas_assignment = await self._canvas_proxy_provider.create_assignment(
            canvas_course_id=course.canvas_course_id,
            assignment_group_id=dto.assignment_group_id,
            cookies=canvas_auth_data,
        )
        with self._assignment_repo.session():
            assignment = Assignment(
                web_id=shortuuid.uuid(),
                name=canvas_assignment.name,
                course_id=course.id,
                canvas_assignment_id=canvas_assignment.canvas_assignment_id,
            )
            self._assignment_repo.save_or_update(assignment)

            enrollments = course.enrollments
            for enrollment in enrollments:
                dto = attendance_dto.Create(
                    student_id=enrollment.student_id,
                    status=AttendanceStatus.INITIATED,
                    value=AttendanceValue.INCOMPLETE,
                )
                self._attendance_service.create_attendance(
                    web_id=assignment.web_id, dto=dto
                )
            assignment_read = canvas_assignment_dto.Read.from_dbmodel(assignment)
        return assignment_read
