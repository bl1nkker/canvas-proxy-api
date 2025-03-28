import pytest

from src.dto import attendance_dto
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.errors.types import NotFoundError
from tests.base_test import BaseTest


class TestAttendanceService(BaseTest):
    def test_create_attendance(
        self,
        attendance_service,
        attendance_repo,
        create_student,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        student = create_student()
        dto = attendance_dto.Create(
            student_id=student.id,
            status=AttendanceStatus.INITIATED,
            value=AttendanceValue.COMPLETE,
        )
        attendance = attendance_service.create_attendance(
            web_id=assignment.web_id, dto=dto
        )
        assert attendance.assignment_id == assignment.id
        assert attendance.status is AttendanceStatus.INITIATED
        assert attendance.value is AttendanceValue.COMPLETE
        with attendance_repo.session():
            atts = attendance_repo.list_all()
            assert len(atts) == 1
            assert atts[0].assignment_id == assignment.id
            assert atts[0].status == AttendanceStatus.INITIATED
            assert atts[0].value == AttendanceValue.COMPLETE

    def test_create_attendance_should_raise_on_invalid_assignment(
        self,
        attendance_service,
        create_student,
        cleanup_all,
    ):
        student = create_student()
        dto = attendance_dto.Create(
            student_id=student.id,
            status=AttendanceStatus.INITIATED,
            value=AttendanceValue.COMPLETE,
        )

        with pytest.raises(NotFoundError) as exc:
            attendance_service.create_attendance(web_id="invalid-web-id", dto=dto)
        assert exc.value.message == "_error_msg_assignment_not_found:invalid-web-id"

    def test_create_attendance_should_raise_on_invalid_student(
        self,
        attendance_service,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        dto = attendance_dto.Create(
            student_id=0,
            status=AttendanceStatus.INITIATED,
            value=AttendanceValue.COMPLETE,
        )

        with pytest.raises(NotFoundError) as exc:
            attendance_service.create_attendance(web_id=assignment.web_id, dto=dto)
        assert exc.value.message == "_error_msg_student_not_found:0"
