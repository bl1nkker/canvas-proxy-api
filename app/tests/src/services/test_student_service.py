import pytest

from src.errors.types import InvalidDataError, NotFoundError
from tests.base_test import BaseTest


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
            assert len(students) == 4
            for student in students:
                assert student.canvas_user_id is not None

        with student_vector_repo.session():
            vectors = student_vector_repo.list_all()
            assert len(vectors) == 4

    def test_load_students_from_excel_should_not_create_duplicate_students(
        self,
        student_service,
        student_repo,
        student_vector_repo,
        students_file,
        create_student,
        cleanup_all,
    ):
        canvas_user_ids = [8348, 8349, 8350]
        for cuid in canvas_user_ids:
            student = create_student(canvas_user_id=cuid)
        result = student_service.load_students_from_excel(
            "test.csv", "text/csv", students_file
        )
        assert result is True
        with student_repo.session():
            students = student_repo.list_all()
            assert len(students) == 4
            for student in students:
                assert student.canvas_user_id is not None

        with student_vector_repo.session():
            vectors = student_vector_repo.list_all()
            assert len(vectors) == 4

    def test_load_students_from_excel_should_overwrite_existing_vectors(
        self,
        student_service,
        student_vector_repo,
        students_file,
        create_student,
        create_student_vector,
        cleanup_all,
    ):
        student = create_student(canvas_user_id=8348)
        create_student_vector(student=student)
        with student_vector_repo.session():
            vector = student_vector_repo.get_by_student_id(student_id=student.id)
            before_embedding = vector.embedding[:]
        student_service.load_students_from_excel("test.csv", "text/csv", students_file)

        with student_vector_repo.session():
            vectors = student_vector_repo.list_all()
            assert len(vectors) == 4
            new_vector = student_vector_repo.get_by_student_id(student_id=student.id)
            assert sorted(new_vector.embedding) != sorted(before_embedding)
