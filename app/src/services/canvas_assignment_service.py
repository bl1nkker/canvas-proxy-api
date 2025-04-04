import shortuuid

from src.dto import attendance_dto, auth_dto, canvas_assignment_dto
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.errors.types import CanvasAPIError, NotFoundError
from src.models.assignment import Assignment
from src.models.assignment_group import AssignmentGroup
from src.proxies.canvas_proxy_provider import CanvasProxyProvider
from src.repositories.assignment_group_repo import AssignmentGroupRepo
from src.repositories.assignment_repo import AssignmentRepo
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.services.attendance_service import AttendanceService


class CanvasAssignmentService:
    def __init__(
        self,
        attendance_service: AttendanceService,
        canvas_course_repo: CanvasCourseRepo,
        assignment_repo: AssignmentRepo,
        assignment_group_repo: AssignmentGroupRepo,
        canvas_proxy_provider_cls=CanvasProxyProvider,
    ):
        self._canvas_proxy_provider = canvas_proxy_provider_cls()
        self._canvas_course_repo = canvas_course_repo
        self._assignment_repo = assignment_repo
        self._assignment_group_repo = assignment_group_repo
        self._attendance_service = attendance_service

    async def get_attendance_assignment_group(
        self, web_id: str, canvas_auth_data: auth_dto.CanvasAuthData
    ) -> canvas_assignment_dto.AssignmentGroupRead:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=web_id)
            if not course:
                raise NotFoundError(message=f"_err_message_course_not_found:{web_id}")
        assignment_group = None
        group = await self._canvas_proxy_provider.get_attendance_assignment_group(
            cookies=canvas_auth_data, canvas_course_id=course.canvas_course_id
        )
        if not group:
            # ? Should we syncronize the assignment groups here? If there is no assignment group, we might delete the records from the database
            raise CanvasAPIError(
                message=f"_err_message_no_attendance_assignment_groups_for_this_course:{web_id}"
            )
        with self._assignment_group_repo.session():
            assignment_group = (
                self._assignment_group_repo.get_by_canvas_assignment_group_id(
                    canvas_assignment_group_id=group.assignment_group_id
                )
            )
            if not assignment_group:
                assignment_group = AssignmentGroup(
                    web_id=shortuuid.uuid(),
                    name=group.name,
                    group_weight=group.group_weight,
                    course_id=course.id,
                    canvas_assignment_group_id=group.assignment_group_id,
                )
                self._assignment_group_repo.save_or_update(assignment_group)

            for assignment in group.assignments:
                existing_assignment = self._assignment_repo.get_by_canvas_assignment_id(
                    canvas_assignment_id=assignment.canvas_assignment_id
                )
                if not existing_assignment:
                    assignment = Assignment(
                        web_id=shortuuid.uuid(),
                        name=assignment.name,
                        assignment_group_id=assignment_group.id,
                        canvas_assignment_id=assignment.canvas_assignment_id,
                    )
                    self._assignment_repo.save_or_update(assignment)
        return canvas_assignment_dto.AssignmentGroupRead.from_dbmodel(assignment_group)

    async def create_assignment(
        self,
        web_id: str,
        assignment_group_web_id: str,
        canvas_auth_data: auth_dto.CanvasAuthData,
    ) -> canvas_assignment_dto.Read:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=web_id)
            if not course:
                raise NotFoundError(message=f"_err_message_course_not_found:{web_id}")

        with self._assignment_group_repo.session():
            assignment_group = self._assignment_group_repo.get_by_web_id(
                web_id=assignment_group_web_id
            )
            if not assignment_group:
                raise NotFoundError(
                    message=f"_err_message_assignment_group_not_found:{assignment_group_web_id}"
                )
        canvas_assignment = await self._canvas_proxy_provider.create_assignment(
            canvas_course_id=course.canvas_course_id,
            canvas_assignment_group_id=assignment_group.canvas_assignment_group_id,
            cookies=canvas_auth_data,
        )
        with self._assignment_repo.session():
            assignment = Assignment(
                web_id=shortuuid.uuid(),
                name=canvas_assignment.name,
                assignment_group_id=assignment_group.id,
                canvas_assignment_id=canvas_assignment.canvas_assignment_id,
            )
            self._assignment_repo.save_or_update(assignment)

            enrollments = course.enrollments
            for enrollment in enrollments:
                dto = attendance_dto.Create(
                    student_id=enrollment.student_id,
                    status=AttendanceStatus.COMPLETED,
                    value=AttendanceValue.INCOMPLETE,
                )
                self._attendance_service.create_attendance(
                    web_id=assignment.web_id, dto=dto
                )
            assignment_read = canvas_assignment_dto.Read.from_dbmodel(assignment)
        return assignment_read
