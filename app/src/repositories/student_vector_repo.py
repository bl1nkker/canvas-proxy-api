import numpy as np

from db.data_repo import DataRepo
from src.models import StudentVector


class StudentVectorRepo(DataRepo[StudentVector]):
    _type = StudentVector
    _order_by_map = None

    def search_by_embedding(self, embedding: np.ndarray, query=None):
        query = query or self.query()
        return (
            query.order_by(self._type.embedding.l2_distance(embedding)).limit(1).first()
        )
