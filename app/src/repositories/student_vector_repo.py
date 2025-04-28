import numpy as np

from db.data_repo import DataRepo
from src.models import StudentVector


class StudentVectorRepo(DataRepo[StudentVector]):
    _type = StudentVector
    _order_by_map = None

    def get_by_student_id(self, student_id: int, query=None):
        query = query or self.query()
        return query.filter(self._type.student_id == student_id).first()

    def search_course_students_by_embedding(
        self,
        embedding: np.ndarray,
        student_ids: list[int],
        threshold: float = 0.3,
        query=None,
    ):
        query = query or self.query()
        return (
            query.filter(self._type.student_id.in_(student_ids))
            .filter(self._type.embedding.cosine_distance(embedding) < threshold)
            .order_by(self._type.embedding.cosine_distance(embedding))
            .first()
        )

    def search_by_embedding(
        self, embedding: np.ndarray, threshold: float = 0.3, query=None
    ):
        query = query or self.query()
        return (
            query.filter(self._type.embedding.cosine_distance(embedding) < threshold)
            .order_by(self._type.embedding.cosine_distance(embedding))
            .first()
        )
