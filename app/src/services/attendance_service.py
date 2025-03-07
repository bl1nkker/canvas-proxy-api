from src.dto import attendance_dto
from src.enums.attendance_status import AttendanceStatus
from src.errors.types import NotFoundError
from src.models.attendance import Attendance
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.repositories.student_repo import StudentRepo


class AttendanceService:
    def __init__(
        self,
        student_repo: StudentRepo,
        attendance_repo: AttendanceRepo,
        canvas_course_repo: CanvasCourseRepo,
    ):
        self._student_repo = student_repo
        self._canvas_course_repo = canvas_course_repo
        self._attendance_repo = attendance_repo

    def create_attendance(
        self, web_id: str, dto: attendance_dto.Create
    ) -> attendance_dto.Read:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=web_id)
        if course is None:
            raise NotFoundError(f"_error_msg_course_not_found:{web_id}")
        with self._student_repo.session():
            student = self._student_repo.get_by_db_id(dto.student_id)
        if student is None:
            raise NotFoundError(f"_error_msg_student_not_found:{dto.student_id}")
        with self._attendance_repo.session():
            attendance = Attendance(
                student_id=student.id,
                canvas_assignment_id=dto.canvas_assignment_id,
                status=dto.status,
                value=dto.value,
                course_id=course.id,
            )
            self._attendance_repo.save_or_update(attendance)
        return attendance_dto.Read.from_dbmodel(attendance)

    def list_attendance_by_assignment_id(
        self, web_id: str, assignment_id: int
    ) -> list[attendance_dto.Read]:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=web_id)
        if course is None:
            raise NotFoundError(f"_error_msg_course_not_found:{web_id}")
        with self._attendance_repo.session():
            query = self._attendance_repo.filter_by_assignment_id(
                assignment_id=assignment_id
            )
            attendances = self._attendance_repo.list_all(query=query)
        return [
            attendance_dto.Read.from_dbmodel(attendance) for attendance in attendances
        ]

    def mark_attendance(
        self, web_id: str, assignment_id: int, dto: attendance_dto.Mark
    ) -> attendance_dto.Read:
        with self._canvas_course_repo.session():
            course = self._canvas_course_repo.get_by_web_id(web_id=web_id)
        if course is None:
            raise NotFoundError(f"_error_msg_course_not_found:{web_id}")
        with self._attendance_repo.session():
            query = self._attendance_repo.filter_by_assignment_id(
                assignment_id=assignment_id
            )
            attendance = self._attendance_repo.get_by_student_id(
                student_id=dto.student_id, query=query
            )
            if attendance is None:
                raise NotFoundError("_error_msg_attendance_not_found")
            attendance.status = AttendanceStatus.IN_PROGRESS.value
            attendance.value = dto.value
            self._attendance_repo.save_or_update(attendance)
        return attendance_dto.Read.from_dbmodel(attendance)
