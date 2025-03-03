from src.models import CanvasCourse
from tests.base_test import BaseTest


class TestCanvasCourseRepo(BaseTest):

    def test_create_canvas_course(
        self, create_canvas_user, canvas_course_repo, cleanup_all
    ):
        canvas_user = create_canvas_user()
        with canvas_course_repo.session():
            course = CanvasCourse(
                web_id="web-id-1",
                long_name="test-long_name",
                short_name="test-short_name",
                original_name="test-original_name",
                course_code="code-123",
                canvas_course_id=228,
                canvas_user_id=canvas_user.id,
            )
            canvas_course_repo.save_or_update(course)
        with canvas_course_repo.session():
            courses = canvas_course_repo.list_all()
            assert len(courses) == 1
