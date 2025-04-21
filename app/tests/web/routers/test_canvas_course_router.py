from tests.base_test import BaseTest
from tests.fixtures import sample_data
from tests.web.web_application_test import WebApplicationTest


class TestCanvasCourseRouter(BaseTest, WebApplicationTest):

    def test_list_courses(
        self,
        client,
        create_canvas_course,
        create_canvas_user,
        cleanup_all,
    ):
        canvas_user = create_canvas_user()
        for i in range(5):
            create_canvas_course(
                long_name=f"test-long_name{i}",
                canvas_course_id=i,
                canvas_user=canvas_user,
            )
        response = client.get("/api/canvas-courses/v1")
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] == 5
        assert len(data["items"]) == 5

    def test_list_courses_filtered_by_user(
        self,
        client,
        create_canvas_course,
        create_canvas_user,
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
        response = client.get(f"/api/canvas-courses/v1?canvas_user_id={canvas_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] == 2
        for course in data["items"]:
            assert course["owner_username"] == canvas_user.username

    def test_get_course_enrollments(
        self,
        client,
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
        response = client.get(
            f"/api/canvas-courses/v1/{course.web_id}/enrollments",
            cookies=sample_data.canvas_auth_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data == [
            {
                "course": {
                    "canvas_course_id": 1,
                    "long_name": "test-long_name",
                    "short_name": "test-short_name",
                    "original_name": "test-original_name",
                    "course_code": "code-123",
                    "id": 1,
                },
                "student": {
                    "web_id": "web-id-4",
                    "name": "Test Testname",
                    "email": "test@gmail.com",
                    "id": 1,
                },
            },
            {
                "course": {
                    "canvas_course_id": 1,
                    "long_name": "test-long_name",
                    "short_name": "test-short_name",
                    "original_name": "test-original_name",
                    "course_code": "code-123",
                    "id": 1,
                },
                "student": {
                    "web_id": "web-id-6",
                    "name": "Test Testname",
                    "email": "test@gmail.com",
                    "id": 2,
                },
            },
            {
                "course": {
                    "canvas_course_id": 1,
                    "long_name": "test-long_name",
                    "short_name": "test-short_name",
                    "original_name": "test-original_name",
                    "course_code": "code-123",
                    "id": 1,
                },
                "student": {
                    "web_id": "web-id-8",
                    "name": "Test Testname",
                    "email": "test@gmail.com",
                    "id": 3,
                },
            },
        ]
