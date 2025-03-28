from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.models.attendance import Attendance
from tests.base_test import BaseTest


class TestAttendanceRepo(BaseTest):
    def test_create_assignment(
        self,
        create_student,
        attendance_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment = create_assignment(course=course, name="sample assignment")
        with attendance_repo.session():
            attendance = Attendance(
                student=student,
                assignment_id=assignment.id,
                status=AttendanceStatus.INITIATED,
                value=AttendanceValue.COMPLETE,
                course_id=course.id,
            )
            attendance_repo.save_or_update(attendance)
        with attendance_repo.session():
            atts = attendance_repo.list_all()
            assert len(atts) == 1
            assert atts[0].student == student
            assert atts[0].assignment_id == assignment.id
            assert atts[0].status is AttendanceStatus.INITIATED
            assert atts[0].value is AttendanceValue.COMPLETE

    def test_get_assignment_by_db_id(
        self,
        create_attendance,
        create_student,
        create_canvas_user,
        create_canvas_course,
        attendance_repo,
        create_assignment,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment = create_assignment(course=course, name="sample assignment")
        att = create_attendance(student=student, assignment=assignment, course=course)
        for _ in range(5):
            create_attendance(student=student, assignment=assignment, course=course)
        with attendance_repo.session():
            att = attendance_repo.get_by_db_id(db_id=att.id)
            assert att.assignment_id == assignment.id

    def test_update_assignment(
        self,
        create_attendance,
        create_student,
        attendance_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        student = create_student()
        assignment = create_assignment(course=course, name="sample assignment")
        att = create_attendance(student=student, assignment=assignment, course=course)
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
        self,
        create_attendance,
        create_student,
        create_canvas_user,
        create_canvas_course,
        attendance_repo,
        create_assignment,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        student = create_student()
        assignment = create_assignment(course=course, name="sample assignment")
        att = create_attendance(student=student, assignment=assignment, course=course)
        with attendance_repo.session():
            attendance_repo.delete(att)
        with attendance_repo.session():
            assert not attendance_repo.list_all()
