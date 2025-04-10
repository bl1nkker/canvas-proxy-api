from unittest.mock import patch

import pytest

from src.dto import attendance_dto, auth_dto, student_dto
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.errors.types import NotFoundError
from src.services.student_service import StudentService
from tests.base_test import BaseTest
from tests.fixtures import sample_data


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

    def test_list_attendances_by_assignment_should_return_list_of_attendances(
        self,
        attendance_service,
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
            create_attendance(student=student, assignment=assignment)
        result = attendance_service.list_attendances_by_assignment(
            assignment_id=assignment.id
        )
        assert result.page == 1
        assert result.page_size == 10
        assert result.total == 5
        assert len(result.items) == 5

    def test_list_attendances_by_assignment_should_raise_on_invalid_assignment_id(
        self,
        attendance_service,
        cleanup_all,
    ):
        with pytest.raises(NotFoundError) as exc:
            attendance_service.list_attendances_by_assignment(assignment_id=999)
        assert exc.value.message == "_error_msg_assignment_not_found:999"

    def test_mark_attendance(
        self,
        attendance_service,
        attendance_repo,
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
        attendance = create_attendance(
            student=student,
            assignment=assignment,
            status=AttendanceStatus.COMPLETED,
            value=AttendanceValue.EXCUSE,
        )
        dto = attendance_dto.Mark(value=AttendanceValue.COMPLETE)
        result = attendance_service.mark_attendance(web_id=attendance.web_id, dto=dto)
        assert result.value is AttendanceValue.COMPLETE
        assert result.status is AttendanceStatus.INITIATED
        with attendance_repo.session():
            atts = attendance_repo.list_all()
            assert len(atts) == 1
            assert atts[0].value == AttendanceValue.COMPLETE
            assert atts[0].status == AttendanceStatus.INITIATED

    @patch.object(
        StudentService,
        "search_student_by_image",
        return_value=student_dto.Read(
            id=1, web_id="web-id-6", name="Test Testname", email="test@gmail.com"
        ),
    )
    def test_mark_attendance_by_image(
        self,
        search_student_by_image_mock,
        attendance_service,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        sample_jpg_file,
        create_student,
        create_attendance,
        attendance_repo,
        cleanup_all,
    ):
        # Create student, enrollment and assignment
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(
            course=course,
            name="Сабаққа қатысу/Посещаемость",
            canvas_assignment_group_id=14761,
        )
        assignment = create_assignment(
            assignment_group=assignment_group,
            name="target assignment",
            canvas_assignment_id=67301,
        )
        student = create_student()
        create_attendance(
            student=student,
            assignment=assignment,
            status=AttendanceStatus.IN_PROGRESS,
            value=AttendanceValue.INCOMPLETE,
        )
        dto = attendance_dto.Search(
            course_id=course.id,
            assignment_id=assignment.id,
        )
        # Get student by image
        result = attendance_service.mark_attendance_by_image(
            dto=dto, stream=sample_jpg_file
        )
        assert result is not None
        assert result.status is AttendanceStatus.INITIATED
        assert result.value is AttendanceValue.COMPLETE
        assert result.student.web_id == "web-id-6"
        assert result.student.name == "Test Testname"

        with attendance_repo.session():
            attendances = attendance_repo.list_all()
            assert len(attendances) == 1
            assert attendances[0].status is AttendanceStatus.INITIATED
            assert attendances[0].value is AttendanceValue.COMPLETE
            assert attendances[0].student_id == 1

    @patch.object(
        StudentService,
        "search_student_by_image",
        return_value=student_dto.Read(
            id=1, web_id="web-id-6", name="Test Testname", email="test@gmail.com"
        ),
    )
    def test_mark_attendance_by_image_should_create_attendance_if_not_exists(
        self,
        search_student_by_image_mock,
        attendance_service,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        sample_jpg_file,
        create_student,
        create_attendance,
        attendance_repo,
        cleanup_all,
    ):
        # Create student, enrollment and assignment
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(
            course=course,
            name="Сабаққа қатысу/Посещаемость",
            canvas_assignment_group_id=14761,
        )
        assignment = create_assignment(
            assignment_group=assignment_group,
            name="target assignment",
            canvas_assignment_id=67301,
        )
        create_student()
        dto = attendance_dto.Search(
            course_id=course.id,
            assignment_id=assignment.id,
        )
        # Get student by image
        result = attendance_service.mark_attendance_by_image(
            dto=dto, stream=sample_jpg_file
        )
        assert result is not None
        assert result.status is AttendanceStatus.INITIATED
        assert result.value is AttendanceValue.COMPLETE
        assert result.student.web_id == "web-id-6"
        assert result.student.name == "Test Testname"

        with attendance_repo.session():
            attendances = attendance_repo.list_all()
            assert len(attendances) == 1
            assert attendances[0].status is AttendanceStatus.INITIATED
            assert attendances[0].value is AttendanceValue.COMPLETE
            assert attendances[0].student_id == 1

    @patch.object(
        StudentService,
        "search_student_by_image",
        return_value=student_dto.Read(
            id=1, web_id="web-id-6", name="Test Testname", email="test@gmail.com"
        ),
    )
    def test_mark_attendance_by_image_should_raise_when_course_not_found(
        self,
        search_student_by_image_mock,
        attendance_service,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        sample_jpg_file,
        create_student,
        create_attendance,
        attendance_repo,
        cleanup_all,
    ):
        # Create student, enrollment and assignment
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(
            course=course,
            name="Сабаққа қатысу/Посещаемость",
            canvas_assignment_group_id=14761,
        )
        assignment = create_assignment(
            assignment_group=assignment_group,
            name="target assignment",
            canvas_assignment_id=67301,
        )
        student = create_student()
        create_attendance(
            student=student,
            assignment=assignment,
            status=AttendanceStatus.COMPLETED,
            value=AttendanceValue.EXCUSE,
        )
        dto = attendance_dto.Search(
            course_id=999,
            assignment_id=assignment.id,
        )
        # Get student by image
        with pytest.raises(NotFoundError) as exc:
            attendance_service.mark_attendance_by_image(dto=dto, stream=sample_jpg_file)
        assert exc.value.message == "_error_msg_course_not_found: 999"

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_load_course_attendances_from_canvas_should_create_attendances(
        self,
        mock_get,
        canvas_get_student_attendances_ok_response,
        attendance_service,
        create_student,
        create_enrollment,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        attendance_repo,
        cleanup_all,
    ):
        mock_get.return_value = canvas_get_student_attendances_ok_response
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(
            course=course,
            name="Сабаққа қатысу/Посещаемость",
            canvas_assignment_group_id=14761,
        )
        assignment_ids = [67301, 73376, 68254]
        for ass_id in assignment_ids:
            create_assignment(
                assignment_group=assignment_group,
                name=f"assignment#{ass_id}",
                canvas_assignment_id=ass_id,
            )

        student1 = create_student(canvas_user_id=18728)
        student2 = create_student(canvas_user_id=18729)
        create_enrollment(course=course, student=student1)
        create_enrollment(course=course, student=student2)

        result = await attendance_service.load_course_attendances_from_canvas(
            dto=attendance_dto.Load(course_id=course.id),
            canvas_auth_data=auth_dto.CanvasAuthData(**sample_data.canvas_auth_data),
        )
        assert result is True
        with attendance_repo.session():
            atts = attendance_repo.list_all()
            assert len(atts) == 6
            for att in atts:
                assert att.status == AttendanceStatus.COMPLETED
                assert att.value is not None

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_load_course_attendances_from_canvas_should_skip_attendance_if_not_exists(
        self,
        mock_get,
        canvas_get_student_attendances_ok_response,
        attendance_service,
        create_student,
        create_enrollment,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        attendance_repo,
        cleanup_all,
    ):
        mock_get.return_value = canvas_get_student_attendances_ok_response
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(
            course=course,
            name="Сабаққа қатысу/Посещаемость",
            canvas_assignment_group_id=14761,
        )
        assignment_ids = [67301, 73376]
        for ass_id in assignment_ids:
            create_assignment(
                assignment_group=assignment_group,
                name=f"assignment#{ass_id}",
                canvas_assignment_id=ass_id,
            )

        student1 = create_student(canvas_user_id=18728)
        student2 = create_student(canvas_user_id=18729)
        create_enrollment(course=course, student=student1)
        create_enrollment(course=course, student=student2)

        result = await attendance_service.load_course_attendances_from_canvas(
            dto=attendance_dto.Load(course_id=course.id),
            canvas_auth_data=auth_dto.CanvasAuthData(**sample_data.canvas_auth_data),
        )
        assert result is True
        with attendance_repo.session():
            atts = attendance_repo.list_all()
            assert len(atts) == 4
            for att in atts:
                assert att.status == AttendanceStatus.COMPLETED
                assert att.value is not None
