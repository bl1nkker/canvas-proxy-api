from tests.base_test import BaseTest
from tests.web.web_application_test import WebApplicationTest


class TestStudentRouter(BaseTest, WebApplicationTest):
    def test_enroll_student(
        self,
        client,
        create_student,
        create_canvas_user,
        create_canvas_course,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)
        response = client.post(
            f"/api/students/v1/{student.web_id}/enroll/{course.web_id}"
        )
        assert response.status_code == 201
        data = response.json()
        assert data == {
            "course": {
                "long_name": "test-long_name",
                "short_name": "test-short_name",
                "original_name": "test-original_name",
                "course_code": "code-123",
                "course_id": 228337,
            },
            "student": {
                "web_id": "web-id-1",
                "name": "Test Testname",
                "email": "test@gmail.com",
                "canvas_user_id": 1,
            },
        }

    def test_enroll_student_should_raise_when_student_not_found(
        self,
        client,
        create_canvas_user,
        create_canvas_course,
        cleanup_all,
    ):
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)
        response = client.post(
            f"/api/students/v1/unknown-web-id/enroll/{course.web_id}"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["message"] == "_error_msg_student_not_found:unknown-web-id"

    def test_enroll_student_should_raise_when_course_not_found(
        self,
        client,
        create_student,
        cleanup_all,
    ):
        student = create_student()
        response = client.post(
            f"/api/students/v1/{student.web_id}/enroll/unknown-web-id"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["message"] == "_error_msg_course_not_found:unknown-web-id"

    def test_enroll_student_should_raise_on_existing_enrollment(
        self,
        client,
        create_student,
        create_canvas_user,
        create_canvas_course,
        create_enrollment,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user()
        course = create_canvas_course(canvas_user=canvas_user)
        create_enrollment(course=course, student=student)
        response = client.post(
            f"/api/students/v1/{student.web_id}/enroll/{course.web_id}"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["message"] == "_error_msg_enrollment_already_exists"
