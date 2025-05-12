from src.dto import file_record_dto, recognition_history_dto
from tests.base_test import BaseTest


class TestRecognitionHistoryService(BaseTest):
    def test_create_recognition_history(
        self,
        recognition_history_repo,
        recognition_history_service,
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
        recognition_history = recognition_history_service.create_recognition_history(
            dto=recognition_history_dto.Create(
                student_id=student.id,
                assignment_id=assignment.id,
                image_file=file_record_dto.Metadata(
                    name="test.jpg",
                    size=1024,
                    content_type="image/jpeg",
                    web_id="web-id-1",
                    path="/dev/null",
                ),
                recognition_details=recognition_history_dto.RecognitionDetails(
                    duration=1.00
                ),
            )
        )
        assert recognition_history.student_id == student.id
        assert recognition_history.assignment_id == assignment.id
        assert recognition_history.image_file == file_record_dto.Metadata(
            name="test.jpg",
            size=1024,
            content_type="image/jpeg",
            web_id="web-id-1",
            path="/dev/null",
        )
        assert (
            recognition_history.recognition_details
            == recognition_history_dto.RecognitionDetails(duration=1.00)
        )
        with recognition_history_repo.session():
            histories = recognition_history_repo.list_all()
            assert len(histories) == 1
            assert histories[0].student_id == student.id
            assert histories[0].assignment_id == assignment.id
            assert histories[0].image_file == file_record_dto.Metadata(
                name="test.jpg",
                size=1024,
                content_type="image/jpeg",
                web_id="web-id-1",
                path="/dev/null",
            )
            assert histories[
                0
            ].recognition_details == recognition_history_dto.RecognitionDetails(
                duration=1.00
            )
