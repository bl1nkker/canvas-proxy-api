from src.models.assignment import Assignment
from tests.base_test import BaseTest


class TestAssignmentRepo(BaseTest):
    def test_create_assignment(
        self,
        assignment_repo,
        create_canvas_user,
        create_canvas_course,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        with assignment_repo.session():
            assignment = Assignment(
                web_id="web-id-1",
                name="sample name",
                course_id=course.id,
                canvas_assignment_id=1,
            )
            assignment_repo.save_or_update(assignment)

        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 1
            assert assignments[0].web_id == "web-id-1"
            assert assignments[0].course_id == course.id
            assert assignments[0].name == "sample name"
            assert assignments[0].canvas_assignment_id == 1

    def test_get_assignment_by_db_id(
        self,
        assignment_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        another_course = create_canvas_course(
            canvas_user=canvas_user, canvas_course_id=2
        )
        assignment = create_assignment(course=course, name="target assignment")
        for _ in range(5):
            create_assignment(course=another_course, name="another assignment")
        with assignment_repo.session():
            assignment = assignment_repo.get_by_db_id(assignment.id)
            assert assignment.name == "target assignment"
            assert assignment.course_id == course.id

    def test_get_assignment_by_web_id(
        self,
        assignment_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        another_course = create_canvas_course(
            canvas_user=canvas_user, canvas_course_id=2
        )
        assignment = create_assignment(course=course, name="target assignment")
        for _ in range(5):
            create_assignment(course=another_course, name="another assignment")
        with assignment_repo.session():
            assignment = assignment_repo.get_by_web_id(web_id=assignment.web_id)
            assert assignment.name == "target assignment"
            assert assignment.course_id == course.id

    def test_update_assignment(
        self,
        assignment_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment = create_assignment(
            course=course, name="target assignment", canvas_assignment_id=1
        )
        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 1
            assignment = assignment_repo.get_by_db_id(assignment.id)
            assert assignment.name == "target assignment"
            assert assignment.course_id == course.id
            assert assignment.canvas_assignment_id == 1

        another_course = create_canvas_course(
            canvas_user=canvas_user, canvas_course_id=2
        )
        with assignment_repo.session():
            assignment = assignment_repo.get_by_db_id(assignment.id)
            assignment.name = "another assignment"
            assignment.course_id = another_course.id
            assignment.canvas_assignment_id = 2
            assignment_repo.save_or_update(assignment)

        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 1
            assignment = assignment_repo.get_by_db_id(assignment.id)
            assert assignment.name == "another assignment"
            assert assignment.course_id == another_course.id
            assert assignment.canvas_assignment_id == 2

    def test_delete_assignment(
        self,
        assignment_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        another_course = create_canvas_course(
            canvas_user=canvas_user, canvas_course_id=2
        )
        assignment = create_assignment(course=course, name="target assignment")
        for _ in range(5):
            create_assignment(course=another_course, name="another assignment")
        with assignment_repo.session():
            assignment = assignment_repo.get_by_db_id(assignment.id)
            assignment_repo.delete(assignment)
        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 5
