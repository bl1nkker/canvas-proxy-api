import pytest

from src.dto import canvas_course_dto
from tests.base_test import BaseTest


class TestCanvasCourseService(BaseTest):
    def test_list_courses(
        self,
        create_canvas_course,
        create_canvas_user,
        canvas_course_service,
        cleanup_all,
    ):
        canvas_user = create_canvas_user()
        for i in range(5):
            create_canvas_course(
                long_name=f"test-long_name{i}",
                canvas_course_id=i,
                canvas_user=canvas_user,
            )
        courses = canvas_course_service.list_courses()
        assert courses.page == 1
        assert courses.page_size == 10
        assert courses.total == 5
        assert len(courses.items) == 5

    def test_list_courses_filtered_by_user(
        self,
        create_canvas_course,
        create_canvas_user,
        canvas_course_service,
        cleanup_all,
    ):
        canvas_user = create_canvas_user()
        for i in range(2):
            create_canvas_course(
                long_name=f"test{i}",
                canvas_user=canvas_user,
                canvas_course_id=i,
            )

        another_user = create_canvas_user(
            username="another@.com",
            canvas_id="canvas_id_228",
        )
        for i in range(5):
            create_canvas_course(
                long_name=f"another_test{i}",
                canvas_user=another_user,
                canvas_course_id=i + 5,
            )
        filter_params = canvas_course_dto.FilterParams(canvas_user_id=canvas_user.id)
        courses = canvas_course_service.list_courses(filter_params=filter_params)
        assert courses.page == 1
        assert courses.page_size == 10
        assert courses.total == 2
        for course in courses.items:
            assert course.owner_username == canvas_user.username

    @pytest.mark.asyncio
    async def test_get_course_enrollments(
        self,
        canvas_course_service,
        create_student,
        create_canvas_user,
        create_enrollment,
        create_canvas_course,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        for _ in range(3):
            student = create_student()
            create_enrollment(course=course, student=student)
        canvas_user = create_canvas_user(username="another-user", canvas_id=10)
        another_course = create_canvas_course(
            canvas_user=canvas_user, canvas_course_id=10
        )
        for _ in range(5):
            another_student = create_student()
            create_enrollment(course=another_course, student=another_student)

        enrollments = await canvas_course_service.get_course_enrollments(
            web_id=course.web_id
        )
        assert len(enrollments) == 3
