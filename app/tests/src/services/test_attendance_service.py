from src.dto import attendance_dto
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from tests.base_test import BaseTest


class TestAttendanceService(BaseTest):
    def test_create_attendance(
        self,
        attendance_service,
        attendance_repo,
        create_student,
        create_canvas_user,
        create_canvas_course,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        student = create_student()
        dto = attendance_dto.Create(
            student_id=student.id,
            canvas_assignment_id=1,
            status=AttendanceStatus.INITIATED,
            value=AttendanceValue.COMPLETE,
        )
        attendance = attendance_service.create_attendance(web_id=course.web_id, dto=dto)
        assert attendance.canvas_assignment_id == 1
        assert attendance.status is AttendanceStatus.INITIATED
        assert attendance.value is AttendanceValue.COMPLETE
        with attendance_repo.session():
            atts = attendance_repo.list_all()
            assert len(atts) == 1
            assert atts[0].canvas_assignment_id == 1
            assert atts[0].status == AttendanceStatus.INITIATED
            assert atts[0].value == AttendanceValue.COMPLETE
