from unittest.mock import call, patch

import pytest

from src.enums.attendance_status import AttendanceStatus
from src.services.attendance_process_service import AttendanceProcessService
from tests.base_test import BaseTest

is_done = False


class TestAttendanceProcessService(BaseTest):

    @pytest.mark.asyncio
    @patch.object(AttendanceProcessService, "run_process_attendance", return_value=True)
    async def test_process_attendances_should_process_all_attendances(
        self,
        run_process_attendance_mock,
        attendance_process_service,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        create_assignment_group,
        create_attendance,
        create_student,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        for _ in range(5):
            student = create_student()
            create_attendance(
                student=student,
                assignment=assignment,
                status=AttendanceStatus.INITIATED,
            )
        for _ in range(5):
            student = create_student()
            create_attendance(
                student=student,
                assignment=assignment,
                status=AttendanceStatus.IN_PROGRESS,
            )
        for _ in range(5):
            student = create_student()
            create_attendance(
                student=student,
                assignment=assignment,
                status=AttendanceStatus.COMPLETED,
            )
        await attendance_process_service.process_attendances()
        assert run_process_attendance_mock.call_count == 5

    @pytest.mark.asyncio
    @patch.object(AttendanceProcessService, "run_process_attendance", return_value=True)
    async def test_process_attendances_should_not_call_on_empty_attendances(
        self,
        run_process_attendance_mock,
        attendance_process_service,
        cleanup_all,
    ):
        await attendance_process_service.process_attendances()
        assert run_process_attendance_mock.call_count == 0

    @pytest.mark.asyncio
    @patch.object(
        AttendanceProcessService,
        "process_single_attendance",
        return_value=True,
    )
    async def test_process_next_attendance_should_process_non_blocked_attendance(
        self,
        process_single_attendance_mock,
        attendance_process_service,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        create_assignment_group,
        create_attendance,
        create_student,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        student = create_student()
        att1 = create_attendance(
            student=student,
            assignment=assignment,
            status=AttendanceStatus.INITIATED,
        )
        create_attendance(
            student=student,
            assignment=assignment,
            status=AttendanceStatus.INITIATED,
        )
        create_attendance(
            student=student,
            assignment=assignment,
            status=AttendanceStatus.INITIATED,
        )
        calls = [
            call(1),
            call(2),
        ]
        process_single_attendance_mock.assert_has_calls(calls, any_order=False)

    @pytest.mark.asyncio
    @patch.object(
        AttendanceProcessService,
        "process_attendance",
        return_value=True,
    )
    async def test_theory(
        self,
        run_process_attendance_mock,
        attendance_repo,
        attendance_process_service,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        create_assignment_group,
        create_attendance,
        create_student,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="sample assignment"
        )
        for _ in range(5):
            student = create_student()
            create_attendance(
                student=student,
                assignment=assignment,
                status=AttendanceStatus.INITIATED,
            )
        await attendance_process_service.process_attendances()

        with attendance_repo.session():
            atts = attendance_repo.list_all()
            for att in atts:
                assert att.failed is False
                assert att.status == AttendanceStatus.COMPLETED
