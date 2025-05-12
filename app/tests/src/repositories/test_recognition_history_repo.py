from src.models import RecognitionHistory
from tests.base_test import BaseTest


class TestRecognitionHistoryRepo(BaseTest):
    def test_create(
        self,
        recognition_history_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        create_student,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="target assignment"
        )
        with recognition_history_repo.session():
            recognition_history = RecognitionHistory(
                web_id="web-id-1",
                student_id=student.id,
                assignment_id=assignment.id,
                image_file_json={
                    "name": "test",
                    "size": 1024,
                    "content_type": "image/jpeg",
                    "path": "dev/null",
                },
                recognition_details_json={"duration": 1.00},
            )
            recognition_history_repo.save_or_update(recognition_history)
        with recognition_history_repo.session():
            hists = recognition_history_repo.list_all()
            assert len(hists) == 1
            assert hists[0].student_id == student.id
            assert hists[0].assignment_id == assignment.id
            assert hists[0].image_file_json == {
                "name": "test",
                "size": 1024,
                "content_type": "image/jpeg",
                "path": "dev/null",
            }
            assert hists[0].recognition_details_json == {"duration": 1.00}

    def test_get_by_db_id(
        self,
        recognition_history_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        create_student,
        create_recognition_history,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="target assignment"
        )
        recognition_history = create_recognition_history(
            student=student, assignment=assignment
        )
        with recognition_history_repo.session():
            history = recognition_history_repo.get_by_db_id(
                db_id=recognition_history.id
            )
            assert history is not None

    def test_update(
        self,
        recognition_history_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        create_student,
        create_recognition_history,
        cleanup_all,
    ):
        student = create_student()

        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="target assignment"
        )
        recognition_history = create_recognition_history(
            student=student, assignment=assignment
        )
        with recognition_history_repo.session():
            another_student = create_student(canvas_user_id=2)
            another_assignment = create_assignment(
                assignment_group=assignment_group, name="target assignment"
            )
            history = recognition_history_repo.get_by_db_id(
                db_id=recognition_history.id
            )
            history.student_id = another_student.id
            history.assignment_id = another_assignment.id
            history.image_file_json = {
                "name": "test",
                "size": 1024,
                "content_type": "image/jpeg",
                "path": "dev/null",
            }
            history.recognition_details_json = {"duration": 9.00}
            recognition_history_repo.save_or_update(history)

        with recognition_history_repo.session():
            hists = recognition_history_repo.list_all()
            assert len(hists) == 1
            assert hists[0].student_id == another_student.id
            assert hists[0].assignment_id == another_assignment.id
            assert hists[0].image_file_json == {
                "name": "test",
                "size": 1024,
                "content_type": "image/jpeg",
                "path": "dev/null",
            }
            assert hists[0].recognition_details_json == {"duration": 9.00}

    def test_delete(
        self,
        recognition_history_repo,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        create_student,
        create_recognition_history,
        cleanup_all,
    ):
        student = create_student()
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        assignment = create_assignment(
            assignment_group=assignment_group, name="target assignment"
        )
        recognition_history = create_recognition_history(
            student=student, assignment=assignment
        )
        with recognition_history_repo.session():
            recognition_history_repo.delete(recognition_history)

        with recognition_history_repo.session():
            assert not recognition_history_repo.list_all()
