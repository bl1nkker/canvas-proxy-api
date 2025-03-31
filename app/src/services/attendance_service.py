import shortuuid

from db.data_repo import Pagination
from src.dto import attendance_dto
from src.enums.attendance_status import AttendanceStatus
from src.errors.types import NotFoundError
from src.models.attendance import Attendance
from src.repositories.assignment_repo import AssignmentRepo
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.repositories.student_repo import StudentRepo


class AttendanceService:
    def __init__(
        self,
        student_repo: StudentRepo,
        attendance_repo: AttendanceRepo,
        assignment_repo: AssignmentRepo,
        canvas_course_repo: CanvasCourseRepo,
    ):
        self._student_repo = student_repo
        self._canvas_course_repo = canvas_course_repo
        self._assignment_repo = assignment_repo
        self._attendance_repo = attendance_repo

    def create_attendance(
        self, web_id: str, dto: attendance_dto.Create
    ) -> attendance_dto.Read:
        with self._assignment_repo.session():
            assignment = self._assignment_repo.get_by_web_id(web_id=web_id)
        if assignment is None:
            raise NotFoundError(f"_error_msg_assignment_not_found:{web_id}")
        with self._student_repo.session():
            student = self._student_repo.get_by_db_id(dto.student_id)
        if student is None:
            raise NotFoundError(f"_error_msg_student_not_found:{dto.student_id}")
        with self._attendance_repo.session():
            attendance = Attendance(
                web_id=shortuuid.uuid(),
                student_id=student.id,
                assignment_id=assignment.id,
                status=dto.status,
                value=dto.value,
            )
            self._attendance_repo.save_or_update(attendance)
        return attendance_dto.Read.from_dbmodel(attendance)

    def list_attendances_by_assignment(
        self, assignment_web_id: str, page=1, page_size=10, order_by="id", asc=True
    ) -> Pagination[attendance_dto.Read]:
        with self._assignment_repo.session():
            assignment = self._assignment_repo.get_by_web_id(web_id=assignment_web_id)
            if not assignment:
                raise NotFoundError(
                    f"_error_msg_assignment_not_found:{assignment_web_id}"
                )
        with self._attendance_repo.session():
            query = self._attendance_repo.order_by(order_by=order_by, asc=asc)
            query = self._attendance_repo.filter_by_assignment_id(
                assignment_id=assignment.id
            )
            attendances = self._attendance_repo.list_paged(
                page=page, page_size=page_size, query=query
            )
        return Pagination(
            page=attendances.page,
            page_size=attendances.page_size,
            total=attendances.total,
            items=[
                attendance_dto.Read.from_dbmodel(attendance)
                for attendance in attendances.items
            ],
        )

    def mark_attendance(
        self, web_id: str, dto: attendance_dto.Mark
    ) -> attendance_dto.Read:
        with self._attendance_repo.session():
            attendance = self._attendance_repo.get_by_web_id(web_id=web_id)
            if attendance is None:
                raise NotFoundError(f"_error_msg_attendance_not_found: {web_id}")
            attendance.status = AttendanceStatus.INITIATED
            attendance.value = dto.value
            self._attendance_repo.save_or_update(attendance)
        return attendance_dto.Read.from_dbmodel(attendance)
