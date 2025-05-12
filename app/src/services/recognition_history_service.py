import shortuuid

from src.dto import recognition_history_dto
from src.models import RecognitionHistory
from src.repositories.recognition_history_repo import RecognitionHistoryRepo


class RecognitionHistoryService:
    def __init__(self, recognition_history_repo: RecognitionHistoryRepo):
        self._recognition_history_repo = recognition_history_repo

    def create_recognition_history(
        self, dto: recognition_history_dto.Create
    ) -> recognition_history_dto.Read:
        with self._recognition_history_repo.session():
            recognition_history = RecognitionHistory(
                web_id=shortuuid.uuid(),
                student_id=dto.student_id,
                assignment_id=dto.assignment_id,
                image_file_json=dto.image_file.model_dump(),
                recognition_details_json=dto.recognition_details.model_dump(),
            )
            self._recognition_history_repo.save_or_update(recognition_history)
        return recognition_history_dto.Read.from_dbmodel(recognition_history)

    def list_recognition_histories(self):
        pass
