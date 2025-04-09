from unittest.mock import patch

import pytest

from src.dto import auth_dto
from src.errors.types import InvalidDataError, NotFoundError
from tests.base_test import BaseTest
from tests.fixtures import sample_data


class TestStudendService(BaseTest):
    def test_enroll_student(
        self,
        student_service,
        create_student,
        create_canvas_user,
        create_canvas_course,
        enrollment_repo,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)

        student_service.enroll_student(
            web_id=student.web_id, course_web_id=course.web_id
        )

        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 1
            assert enrollments[0].course == course
            assert enrollments[0].student == student

    def test_enroll_student_should_raise_when_student_not_found(
        self,
        student_service,
        create_canvas_user,
        create_canvas_course,
        cleanup_all,
    ):
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)
        with pytest.raises(NotFoundError) as exc:
            student_service.enroll_student(
                web_id="unknown-web-id", course_web_id=course.web_id
            )
        assert exc.value.message == "_error_msg_student_not_found:unknown-web-id"

    def test_enroll_student_should_raise_when_course_not_found(
        self,
        student_service,
        create_student,
        cleanup_all,
    ):
        student = create_student()
        with pytest.raises(NotFoundError) as exc:
            student_service.enroll_student(
                web_id=student.web_id, course_web_id="unknown-web-id"
            )
        assert exc.value.message == "_error_msg_course_not_found:unknown-web-id"

    def test_enroll_student_should_raise_when_enrollment_already_exists(
        self,
        student_service,
        create_student,
        create_canvas_user,
        create_enrollment,
        create_canvas_course,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)
        create_enrollment(course=course, student=student)
        with pytest.raises(InvalidDataError) as exc:
            student_service.enroll_student(
                web_id=student.web_id, course_web_id=course.web_id
            )
        assert exc.value.message == "_error_msg_enrollment_already_exists"

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_load_students_should_save_students(
        self,
        mock_get,
        canvas_get_students_ok_response,
        student_service,
        student_repo,
        create_canvas_user,
        create_canvas_course,
        cleanup_all,
    ):
        mock_get.return_value = canvas_get_students_ok_response
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user, canvas_course_id=2997)
        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        result = await student_service.load_students(
            course_web_id=course.web_id, canvas_auth_data=canvas_auth_data
        )
        mock_get.assert_called_once()
        assert len(result) == 2
        with student_repo.session():
            students = student_repo.list_all()
            assert len(students) == 2

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_load_students_should_create_enrollments_for_each_student(
        self,
        mock_get,
        canvas_get_students_ok_response,
        student_service,
        create_canvas_user,
        create_canvas_course,
        enrollment_repo,
        cleanup_all,
    ):
        mock_get.return_value = canvas_get_students_ok_response
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user, canvas_course_id=2997)
        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        await student_service.load_students(
            course_web_id=course.web_id, canvas_auth_data=canvas_auth_data
        )
        mock_get.assert_called_once()
        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 2
            assert enrollments[0].course_id == course.id

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_load_students_should_create_enrollments_already_existing_students(
        self,
        mock_get,
        canvas_get_students_ok_response,
        student_service,
        create_student,
        create_canvas_user,
        create_canvas_course,
        enrollment_repo,
        student_repo,
        cleanup_all,
    ):
        mock_get.return_value = canvas_get_students_ok_response
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user, canvas_course_id=2997)
        create_student(canvas_user_id=18728)
        create_student(canvas_user_id=18729)

        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        await student_service.load_students(
            course_web_id=course.web_id, canvas_auth_data=canvas_auth_data
        )
        mock_get.assert_called_once()
        with student_repo.session():
            students = student_repo.list_all()
            assert len(students) == 2
        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 2
            assert enrollments[0].course_id == course.id

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_load_students_should_not_create_enrollment_if_already_exists(
        self,
        mock_get,
        canvas_get_students_ok_response,
        student_service,
        create_student,
        create_canvas_user,
        create_canvas_course,
        create_enrollment,
        enrollment_repo,
        student_repo,
        cleanup_all,
    ):
        mock_get.return_value = canvas_get_students_ok_response
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user, canvas_course_id=2997)
        student = create_student(canvas_user_id=18728)
        create_enrollment(course=course, student=student)

        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        await student_service.load_students(
            course_web_id=course.web_id, canvas_auth_data=canvas_auth_data
        )
        mock_get.assert_called_once()
        with student_repo.session():
            students = student_repo.list_all()
            assert len(students) == 2
        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 2
            assert enrollments[0].course_id == course.id

    def test_load_students_from_excel(
        self,
        student_service,
        student_repo,
        student_vector_repo,
        students_file,
        cleanup_all,
    ):
        result = student_service.load_students_from_excel(
            "test.csv", "text/csv", students_file
        )
        assert result is True
        with student_repo.session():
            students = student_repo.list_all()
            assert len(students) == 5
            for student in students:
                assert student.canvas_user_id is not None

        with student_vector_repo.session():
            vectors = student_vector_repo.list_all()
            assert len(vectors) == 5
