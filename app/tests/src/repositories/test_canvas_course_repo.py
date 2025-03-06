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

    def test_get_canvas_course(
        self, sample_canvas_course, create_canvas_user, canvas_course_repo, cleanup_all
    ):
        canvas_user = create_canvas_user()
        with canvas_course_repo.session():
            course = sample_canvas_course(long_name="test", canvas_user=canvas_user)
            created_course = canvas_course_repo.save_or_update(course)
            for i in range(5):
                another_user = create_canvas_user(
                    username=f"test@{i}.com",
                    canvas_id=f"canvas_id{i}",
                )
                course = sample_canvas_course(
                    long_name=f"test{i}",
                    canvas_user=another_user,
                    canvas_course_id=i,
                )
                canvas_course_repo.save_or_update(course)
        with canvas_course_repo.session():
            courses = canvas_course_repo.list_all()
            assert len(courses) == 6
            course = canvas_course_repo.get_by_db_id(db_id=created_course.id)
            assert course.long_name == "test"
            assert course.canvas_user == canvas_user
            assert course.web_id == "web-id-3"

    def test_update_canvas_course(
        self, sample_canvas_course, create_canvas_user, canvas_course_repo, cleanup_all
    ):
        canvas_user = create_canvas_user()
        with canvas_course_repo.session():
            course = sample_canvas_course(long_name="test", canvas_user=canvas_user)
            created_course = canvas_course_repo.save_or_update(course)

        with canvas_course_repo.session():
            course = canvas_course_repo.get_by_db_id(db_id=created_course.id)
            course.long_name = "another name"
            created_course = canvas_course_repo.save_or_update(course)

        with canvas_course_repo.session():
            courses = canvas_course_repo.list_all()
            assert len(courses) == 1
            course = canvas_course_repo.get_by_db_id(db_id=created_course.id)
            assert course.long_name == "another name"
            assert course.canvas_user == canvas_user
            assert course.web_id == "web-id-3"

    def test_delete_canvas_course(
        self, sample_canvas_course, create_canvas_user, canvas_course_repo, cleanup_all
    ):
        canvas_user = create_canvas_user()
        with canvas_course_repo.session():
            course = sample_canvas_course(long_name="test", canvas_user=canvas_user)
            created_course = canvas_course_repo.save_or_update(course)

        with canvas_course_repo.session():
            courses = canvas_course_repo.list_all()
            assert len(courses) == 1
            course = canvas_course_repo.get_by_db_id(db_id=created_course.id)
            canvas_course_repo.delete(course)

        with canvas_course_repo.session():
            courses = canvas_course_repo.list_all()
            assert len(courses) == 0

    def test_filter_by_canvas_user_id(
        self, sample_canvas_course, create_canvas_user, canvas_course_repo, cleanup_all
    ):
        with canvas_course_repo.session():
            canvas_user = create_canvas_user()
            for i in range(2):
                course = sample_canvas_course(
                    long_name=f"test{i}",
                    canvas_user=canvas_user,
                    canvas_course_id=i,
                )
                canvas_course_repo.save_or_update(course)

            another_user = create_canvas_user(
                username="another@.com",
                canvas_id="canvas_id_228",
            )
            for i in range(5):
                course = sample_canvas_course(
                    long_name=f"another_test{i}",
                    canvas_user=another_user,
                    canvas_course_id=i + 5,
                )
                canvas_course_repo.save_or_update(course)
        with canvas_course_repo.session():
            courses = canvas_course_repo.list_all()
            assert len(courses) == 7
            q = canvas_course_repo.filter_by_canvas_user_id(canvas_user.id)
            courses = canvas_course_repo.list_all(query=q)
            assert len(courses) == 2
