from db.data_repo import DataRepo
from src.models import RecognitionHistory


class RecognitionHistoryRepo(DataRepo[RecognitionHistory]):
    _type = RecognitionHistory
    _order_by_map = None

    def filter_by_assignment_id(self, assignment_id: int, query=None):
        query = query or self.query()
        return query.filter(self._type.assignment_id == assignment_id)

    def filter_by_student_id(self, student_id: int, query=None):
        query = query or self.query()
        return query.filter(self._type.student_id == student_id)
