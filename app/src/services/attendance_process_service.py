import structlog

from src.dto import auth_dto
from src.proxies.canvas_proxy_provider import CanvasProxyProvider
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.repositories.student_repo import StudentRepo
from src.services.auth_service import AuthService


class AttendanceProcessService:
    def __init__(
        self,
        attendance_repo: AttendanceRepo,
        auth_service: AuthService,
        canvas_course_repo: CanvasCourseRepo,
        student_repo: StudentRepo,
        canvas_proxy_provider_cls=CanvasProxyProvider,
    ):
        self._log = structlog.getLogger(__name__)
        self._attendance_repo = attendance_repo
        self._student_repo = student_repo
        self._canvas_course_repo = canvas_course_repo
        self._auth_service = auth_service
        self._canvas_proxy_provider = canvas_proxy_provider_cls()

    async def process_attendances(self):
        self._log.debug('"process_attendances" called')
        while True:
            try:
                run = await self.process_next_attendance()
                if not run:
                    break
            except Exception as ex:
                self._log.exception(repr(ex), exc_info=True)
                break
        self._log.debug('returning from "process_attendances"')

    async def process_next_attendance(self):
        self._log.debug('"process_next_attendance" called')
        with self._attendance_repo.session():
            attendance = self._attendance_repo.next_attendance_from_queue()
            if attendance is None:
                return False

            return await self.process_single_attendance(attendance.id)

    async def process_single_attendance(self, attendance_id: int) -> bool:
        self._log.debug('"process_single_attendance" called')
        with self._attendance_repo.session():
            attendance = self._attendance_repo.get_by_db_id(db_id=attendance_id)
            student = self._student_repo.get_by_db_id(attendance.student_id)
            course = self._canvas_course_repo.get_by_db_id(attendance.course_id)
            # Invoke canvas login for course creator
            dto = auth_dto.LoginRequest(
                username=course.canvas_user.username,
                password=course.canvas_user.password,
            )
            _, auth_data = await self._auth_service.get_canvas_auth_data(dto=dto)
            # Send request to Canvas API to change attendance data
            await self._canvas_proxy_provider.change_attendance_status(
                canvas_course_id=course.canvas_course_id,
                canvas_assignment_id=attendance.canvas_assignment_id,
                canvas_student_id=student.canvas_user_id,
                attendance_value=attendance.value,
                cookies=auth_data,
            )
            # Change attendance status to 'COMPLETED'
            attendance.status = "COMPLETED"
            self._attendance_repo.save_or_update(attendance)
            self._log.debug('returning from "process_single_attendance"')
            return True
