from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.models.attendance import Attendance
from tests.base_test import BaseTest


class TestAttendanceRepo(BaseTest):
    def test_create_assignment(self, create_student, attendance_repo, cleanup_all):
        student = create_student()
        with attendance_repo.session():
            attendance = Attendance(
                student=student,
                canvas_assignment_id=10,
                status=AttendanceStatus.INITIATED,
                value=AttendanceValue.COMPLETE,
            )
            attendance_repo.save_or_update(attendance)
        with attendance_repo.session():
            atts = attendance_repo.list_all()
            assert len(atts) == 1
            assert atts[0].student == student
            assert atts[0].canvas_assignment_id == 10
            assert atts[0].status is AttendanceStatus.INITIATED
            assert atts[0].value is AttendanceValue.COMPLETE

    def test_get_assignment_by_db_id(
        self, create_attendance, create_student, attendance_repo, cleanup_all
    ):
        student = create_student()
        att = create_attendance(student=student, canvas_assignment_id=2)
        for _ in range(5):
            create_attendance(student=student)
        with attendance_repo.session():
            att = attendance_repo.get_by_db_id(db_id=att.id)
            assert att.canvas_assignment_id == 2

    def test_update_assignment(
        self, create_attendance, create_student, attendance_repo, cleanup_all
    ):
        student = create_student()
        att = create_attendance(student=student, canvas_assignment_id=1)
        with attendance_repo.session():
            att = attendance_repo.get_by_db_id(db_id=att.id)
            att.canvas_assignment_id = 2
            att.status = AttendanceStatus.IN_PROGRESS
            att.value = AttendanceValue.INCOMPLETE
            attendance_repo.save_or_update(att)
        with attendance_repo.session():
            att = attendance_repo.get_by_db_id(db_id=att.id)
            assert att.canvas_assignment_id == 2
            assert att.status == AttendanceStatus.IN_PROGRESS
            assert att.value == AttendanceValue.INCOMPLETE

    def test_delete_assignment(
        self, create_attendance, create_student, attendance_repo, cleanup_all
    ):
        student = create_student()
        att = create_attendance(student=student)
        with attendance_repo.session():
            attendance_repo.delete(att)
        with attendance_repo.session():
            assert not attendance_repo.list_all()
