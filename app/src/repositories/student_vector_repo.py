import numpy as np

from db.data_repo import DataRepo
from src.models import StudentVector


class StudentVectorRepo(DataRepo[StudentVector]):
    _type = StudentVector
    _order_by_map = None

    def get_by_student_id(self, student_id: int, query=None):
        query = query or self.query()
        return query.filter(self._type.student_id == student_id).first()

    def search_by_embedding(
        self, embedding: np.ndarray, student_ids: list[int], query=None
    ):
        query = query or self.query()
        return (
            query.filter(self._type.student_id.in_(student_ids))
            .order_by(self._type.embedding.l2_distance(embedding))
            .limit(1)
            .first()
        )

    def search_by_embedding_192(self, embedding: np.ndarray, query=None):
        query = query or self.query()
        return (
            query.order_by(self._type.embedding.l2_distance(embedding)).limit(1).first()
        )

    def search_by_embedding_512(self, embedding: np.ndarray, query=None):
        query = query or self.query()
        return (
            query.order_by(self._type.embedding_512.l2_distance(embedding))
            .limit(1)
            .first()
        )

    def search_by_embedding_4096(self, embedding: np.ndarray, query=None):
        query = query or self.query()
        return (
            query.order_by(self._type.embedding_4096.l2_distance(embedding))
            .limit(1)
            .first()
        )
