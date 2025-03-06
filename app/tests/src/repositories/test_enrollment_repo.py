from src.models.enrollment import Enrollment
from tests.base_test import BaseTest


class TestEnrollmentRepo(BaseTest):

    def test_create_enrollment(
        self,
        create_student,
        create_canvas_course,
        create_canvas_user,
        enrollment_repo,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)
        with enrollment_repo.session():
            enrollment = Enrollment(
                student_id=student.id, course_id=course.id, web_id="web-id-1"
            )
            enrollment_repo.save_or_update(enrollment)

        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 1

    def test_get_enrollment_by_id(
        self,
        create_enrollment,
        create_student,
        create_canvas_course,
        create_canvas_user,
        enrollment_repo,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)
        enrollment = create_enrollment(course=course, student=student)

        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 1
            enrollment = enrollment_repo.get_by_db_id(db_id=enrollment.id)
            assert enrollment.student == student
            assert enrollment.course == course

    def test_update_enrollment(
        self,
        create_enrollment,
        create_student,
        create_canvas_course,
        create_canvas_user,
        enrollment_repo,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)
        enrollment = create_enrollment(course=course, student=student)

        another_student = create_student()
        another_course = create_canvas_course(
            canvas_user=canvas_user, canvas_course_id=5
        )
        with enrollment_repo.session():
            enrollment = enrollment_repo.get_by_db_id(db_id=enrollment.id)
            enrollment.student = another_student
            enrollment.course = another_course
            enrollment = enrollment_repo.save_or_update(enrollment)

        with enrollment_repo.session():
            enrollment = enrollment_repo.get_by_db_id(db_id=enrollment.id)
            assert enrollment.student == another_student
            assert enrollment.student != student
            assert enrollment.course == another_course
            assert enrollment.course != course

    def test_delete_enrollment(
        self,
        create_enrollment,
        create_student,
        create_canvas_course,
        create_canvas_user,
        enrollment_repo,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)
        enrollment = create_enrollment(course=course, student=student)

        with enrollment_repo.session():
            enrollment = enrollment_repo.get_by_db_id(db_id=enrollment.id)
            enrollment_repo.delete(enrollment)

        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 0

    def test_get_by_student_and_course_id(
        self,
        create_enrollment,
        create_student,
        create_canvas_course,
        create_canvas_user,
        enrollment_repo,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)
        enrollment = create_enrollment(course=course, student=student)
        for i in range(5):
            student = create_student()
            canvas_user = create_canvas_user(username=f"{i}-user", canvas_id=f"{i}")
            course = create_canvas_course(
                canvas_user=canvas_user, canvas_course_id=i + 10
            )
            enrollment = create_enrollment(course=course, student=student)

        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 6
            enrollment = enrollment_repo.get_by_student_and_course_id(
                student_id=student.id, course_id=course.id
            )
            assert enrollment.student == student
            assert enrollment.course == course
