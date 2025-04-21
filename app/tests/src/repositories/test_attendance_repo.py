import threading
import time
from typing import Callable

import pytest
from sqlalchemy.exc import IntegrityError

from db.session import Session
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.models.attendance import Attendance
from src.repositories.attendance_repo import AttendanceRepo
from tests.base_test import BaseTest

is_done = False


class TestAttendanceRepo(BaseTest):
    @staticmethod
    def block_next_attendance(secs=1):
        condition = threading.Condition()

        def _run():
            global is_done
            session = Session()
            repo = AttendanceRepo(session)
            with repo.session():
                with condition:
                    repo.next_attendance_from_queue()
                    condition.notify()
                    is_done = True
                time.sleep(secs)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return thread, condition

    @staticmethod
    def with_condition(condition: threading.Condition, fn=None):
        with condition:
            while not is_done:
                condition.wait()
            if isinstance(fn, Callable):
                return fn()

    def test_create_assignment(
        self,
        create_student,
        attendance_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        with attendance_repo.session():
            attendance = Attendance(
                web_id="web-id-1",
                student=student,
                assignment_id=assignment.id,
                status=AttendanceStatus.INITIATED,
                value=AttendanceValue.COMPLETE,
                failed=False,
            )
            attendance_repo.save_or_update(attendance)
        with attendance_repo.session():
            atts = attendance_repo.list_all()
            assert len(atts) == 1
            assert atts[0].student == student
            assert atts[0].assignment_id == assignment.id
            assert atts[0].status is AttendanceStatus.INITIATED
            assert atts[0].value is AttendanceValue.COMPLETE

    def test_create_duplicate_assignment_should_raise(
        self,
        create_student,
        attendance_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        with pytest.raises(IntegrityError):
            with attendance_repo.session():
                attendance1 = Attendance(
                    web_id="web-id-1",
                    student=student,
                    assignment_id=assignment.id,
                    status=AttendanceStatus.INITIATED,
                    value=AttendanceValue.COMPLETE,
                    failed=False,
                )
                attendance2 = Attendance(
                    web_id="web-id-2",
                    student=student,
                    assignment_id=assignment.id,
                    status=AttendanceStatus.INITIATED,
                    value=AttendanceValue.COMPLETE,
                    failed=False,
                )
                attendance_repo.save_or_update(attendance1)
                attendance_repo.save_or_update(attendance2)
        with attendance_repo.session():
            atts = attendance_repo.list_all()
            assert len(atts) == 0

    def test_get_assignment_by_db_id(
        self,
        create_attendance,
        create_student,
        create_canvas_user,
        create_canvas_course,
        attendance_repo,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        att = create_attendance(student=student, assignment=assignment)
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
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        student = create_student()
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        att = create_attendance(student=student, assignment=assignment)
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
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        student = create_student()
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        att = create_attendance(student=student, assignment=assignment)
        with attendance_repo.session():
            attendance_repo.delete(att)
        with attendance_repo.session():
            assert not attendance_repo.list_all()

    def test_next_attendance_from_queue_should_get_attendance(
        self,
        create_attendance,
        create_student,
        create_canvas_user,
        create_canvas_course,
        attendance_repo,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        student = create_student()
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )

        attendance = create_attendance(
            student=student, assignment=assignment, status=AttendanceStatus.INITIATED
        )
        with attendance_repo.session():
            result = attendance_repo.next_attendance_from_queue()
            assert result == attendance

    def test_next_attendance_from_queue_should_return_none(
        self,
        attendance_repo,
        cleanup_all,
    ):
        with attendance_repo.session():
            result = attendance_repo.next_attendance_from_queue()
            assert result is None

    def test_next_attendance_from_queue_should_get_attendance_with_initiated_state(
        self,
        create_attendance,
        create_student,
        create_canvas_user,
        create_canvas_course,
        attendance_repo,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        student = create_student()
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        attendance = create_attendance(
            student=student, assignment=assignment, status=AttendanceStatus.INITIATED
        )
        for i in range(5):
            assignment = create_assignment(
                assignment_group=assignment_group, name=f"in progress assignment {i}"
            )
            create_attendance(
                student=student,
                assignment=assignment,
                status=AttendanceStatus.IN_PROGRESS,
            )
        for _ in range(5):
            assignment = create_assignment(
                assignment_group=assignment_group,
                name=f"completed sample assignment {i}",
            )
            create_attendance(
                student=student,
                assignment=assignment,
                status=AttendanceStatus.COMPLETED,
            )

        with attendance_repo.session():
            result = attendance_repo.next_attendance_from_queue()
            assert result == attendance

    def test_next_attendance_from_queue_should_get_attendance_returns_non_blocked(
        self,
        create_attendance,
        create_student,
        create_canvas_user,
        create_canvas_course,
        attendance_repo,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        student = create_student()
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment1 = create_assignment(
            assignment_group=assignment_group, name="sample assignment 1"
        )
        assignment2 = create_assignment(
            assignment_group=assignment_group, name="sample assignment 2"
        )
        create_attendance(
            student=student, assignment=assignment1, status=AttendanceStatus.INITIATED
        )
        att2 = create_attendance(
            student=student, assignment=assignment2, status=AttendanceStatus.INITIATED
        )
        thread, condition = self.block_next_attendance()
        with attendance_repo.session():
            result = self.with_condition(
                condition, lambda: attendance_repo.next_attendance_from_queue()
            )
            assert result == att2
        thread.join()

    def test_next_attendance_from_queue_should_get_none_if_everything_is_blocked(
        self,
        create_attendance,
        create_student,
        create_canvas_user,
        create_canvas_course,
        attendance_repo,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        student = create_student()
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment1 = create_assignment(
            assignment_group=assignment_group, name="sample assignment 1"
        )
        assignment2 = create_assignment(
            assignment_group=assignment_group, name="sample assignment 2"
        )
        create_attendance(
            student=student, assignment=assignment1, status=AttendanceStatus.INITIATED
        )
        create_attendance(
            student=student, assignment=assignment2, status=AttendanceStatus.INITIATED
        )
        self.block_next_attendance()
        thread, condition = self.block_next_attendance()
        with attendance_repo.session():
            result = self.with_condition(
                condition, lambda: attendance_repo.next_attendance_from_queue()
            )
            assert result is None
        thread.join()
