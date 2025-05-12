import shortuuid

from db.data_repo import Pagination
from src.dto import recognition_history_dto
from src.models import RecognitionHistory
from src.repositories.recognition_history_repo import RecognitionHistoryRepo


class RecognitionHistoryService:
    def __init__(self, recognition_history_repo: RecognitionHistoryRepo):
        self._recognition_history_repo = recognition_history_repo

    def _set_filter_params(
        self, query, filter_params=recognition_history_dto.FilterParams
    ):
        if filter_params.assignment_id:
            query = self._recognition_history_repo.filter_by_assignment_id(
                filter_params.assignment_id, query=query
            )
        if filter_params.student_id:
            query = self._recognition_history_repo.filter_by_student_id(
                filter_params.student_id, query=query
            )
        return query

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

    def list_recognition_histories(
        self,
        page=1,
        page_size=10,
        order_by="id",
        asc=True,
        filter_params: recognition_history_dto.FilterParams = None,
    ) -> Pagination[recognition_history_dto.Read]:
        with self._recognition_history_repo.session():
            query = self._recognition_history_repo.order_by(order_by=order_by, asc=asc)
            if filter_params is not None:
                query = self._set_filter_params(query, filter_params)
            assignments = self._recognition_history_repo.list_paged(
                page=page, page_size=page_size, query=query
            )
        return Pagination(
            page=assignments.page,
            page_size=assignments.page_size,
            total=assignments.total,
            items=[
                recognition_history_dto.Read.from_dbmodel(assignments)
                for assignments in assignments.items
            ],
        )
