from src.models.assignment_group import AssignmentGroup
from tests.base_test import BaseTest


class TestAssignmentGroupRepo(BaseTest):
    def test_create_assignment_group(
        self,
        assignment_group_repo,
        create_canvas_user,
        create_canvas_course,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        with assignment_group_repo.session():
            assignment_group = AssignmentGroup(
                web_id="web-id-1",
                name="Test Group",
                group_weight=10,
                course_id=course.id,
                canvas_assignment_group_id=1,
            )
            assignment_group_repo.save_or_update(assignment_group)

        with assignment_group_repo.session():
            assignment_groups = assignment_group_repo.list_all()
            assert len(assignment_groups) == 1
            assert assignment_groups[0].name == "Test Group"
            assert assignment_groups[0].group_weight == 10
            assert assignment_groups[0].course_id == course.id
            assert assignment_groups[0].canvas_assignment_group_id == 1

    def test_get_assignment_group_by_db_id(
        self,
        assignment_group_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        with assignment_group_repo.session():
            retrieved_assignment_group = assignment_group_repo.get_by_db_id(
                assignment_group.id
            )
            assert retrieved_assignment_group.id == assignment_group.id
            assert retrieved_assignment_group.name == assignment_group.name
            assert (
                retrieved_assignment_group.group_weight == assignment_group.group_weight
            )
            assert retrieved_assignment_group.course_id == assignment_group.course_id
            assert (
                retrieved_assignment_group.canvas_assignment_group_id
                == assignment_group.canvas_assignment_group_id
            )

    def test_get_assignment_group_by_web_id(
        self,
        assignment_group_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        with assignment_group_repo.session():
            retrieved_assignment_group = assignment_group_repo.get_by_web_id(
                web_id=assignment_group.web_id
            )
            assert retrieved_assignment_group.id == assignment_group.id
            assert retrieved_assignment_group.name == assignment_group.name
            assert (
                retrieved_assignment_group.group_weight == assignment_group.group_weight
            )
            assert retrieved_assignment_group.course_id == assignment_group.course_id
            assert (
                retrieved_assignment_group.canvas_assignment_group_id
                == assignment_group.canvas_assignment_group_id
            )

    def test_update_assignment_group(
        self,
        assignment_group_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        another_course = create_canvas_course(
            canvas_user=canvas_user, canvas_course_id=2
        )
        with assignment_group_repo.session():
            retrieved_assignment_group = assignment_group_repo.get_by_web_id(
                web_id=assignment_group.web_id
            )
            retrieved_assignment_group.name = "another group"

            retrieved_assignment_group.group_weight = 20
            retrieved_assignment_group.course_id = another_course.id
            assignment_group_repo.save_or_update(retrieved_assignment_group)

        with assignment_group_repo.session():
            assignment_group = assignment_group_repo.get_by_web_id(
                web_id=assignment_group.web_id
            )
            assert assignment_group.name == "another group"
            assert assignment_group.group_weight == 20
            assert assignment_group.course_id == another_course.id

    def test_delete_assignment_group(
        self,
        assignment_group_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        with assignment_group_repo.session():
            retrieved_assignment_group = assignment_group_repo.get_by_web_id(
                web_id=assignment_group.web_id
            )
            assignment_group_repo.delete(retrieved_assignment_group)

        with assignment_group_repo.session():
            assignment_groups = assignment_group_repo.list_all()
            assert len(assignment_groups) == 0
