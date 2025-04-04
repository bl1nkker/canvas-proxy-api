from src.models.assignment import Assignment
from tests.base_test import BaseTest


class TestAssignmentRepo(BaseTest):
    def test_create_assignment(
        self,
        assignment_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        with assignment_repo.session():
            assignment = Assignment(
                web_id="web-id-1",
                name="sample name",
                assignment_group_id=assignment_group.id,
                canvas_assignment_id=1,
            )
            assignment_repo.save_or_update(assignment)

        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 1
            assert assignments[0].web_id == "web-id-1"
            assert assignments[0].assignment_group_id == assignment_group.id
            assert assignments[0].name == "sample name"
            assert assignments[0].canvas_assignment_id == 1

    def test_get_assignment_by_db_id(
        self,
        assignment_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        another_assignment_group = create_assignment_group(
            course=course, name="Test Group 2"
        )
        assignment = create_assignment(
            assignment_group=assignment_group, name="target assignment"
        )
        for _ in range(5):
            create_assignment(
                assignment_group=another_assignment_group, name="target assignment"
            )
        with assignment_repo.session():
            assignment = assignment_repo.get_by_db_id(assignment.id)
            assert assignment.name == "target assignment"
            assert assignment.assignment_group_id == assignment_group.id

    def test_get_assignment_by_web_id(
        self,
        assignment_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        another_assignment_group = create_assignment_group(
            course=course, name="Test Group 2"
        )
        assignment = create_assignment(
            assignment_group=assignment_group, name="target assignment"
        )
        for _ in range(5):
            create_assignment(
                assignment_group=another_assignment_group, name="target assignment"
            )
        with assignment_repo.session():
            assignment = assignment_repo.get_by_web_id(assignment.web_id)
            assert assignment.name == "target assignment"
            assert assignment.assignment_group_id == assignment_group.id

    def test_update_assignment(
        self,
        assignment_repo,
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
            assignment_group=assignment_group,
            name="target assignment",
            canvas_assignment_id=1,
        )
        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 1
            assignment = assignment_repo.get_by_db_id(assignment.id)
            assert assignment.name == "target assignment"
            assert assignment.assignment_group_id == assignment_group.id
            assert assignment.canvas_assignment_id == 1

        another_assignment_group = create_assignment_group(
            course=course, name="Test Group 2"
        )
        with assignment_repo.session():
            assignment = assignment_repo.get_by_db_id(assignment.id)
            assignment.name = "another assignment"
            assignment.assignment_group_id = another_assignment_group.id
            assignment.canvas_assignment_id = 2
            assignment_repo.save_or_update(assignment)

        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 1
            assignment = assignment_repo.get_by_db_id(assignment.id)
            assert assignment.name == "another assignment"
            assert assignment.assignment_group_id == another_assignment_group.id
            assert assignment.canvas_assignment_id == 2

    def test_delete_assignment(
        self,
        assignment_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        another_assignment_group = create_assignment_group(
            course=course, name="Test Group 2"
        )
        assignment = create_assignment(
            assignment_group=assignment_group, name="target assignment"
        )
        for _ in range(5):
            create_assignment(
                assignment_group=another_assignment_group, name="another assignment"
            )
        with assignment_repo.session():
            assignment = assignment_repo.get_by_db_id(assignment.id)
            assignment_repo.delete(assignment)
        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 5
