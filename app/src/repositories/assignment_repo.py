from db.data_repo import DataRepo
from src.models import Assignment


class AssignmentRepo(DataRepo[Assignment]):

    _type = Assignment
    _order_by_map = None

    def get_by_web_id(self, web_id: str, query=None):
        query = query or self.query()
        return query.filter(self._type.web_id == web_id).first()

    def get_by_canvas_assignment_id(self, canvas_assignment_id: int, query=None):
        query = query or self.query()
        return query.filter(
            self._type.canvas_assignment_id == canvas_assignment_id
        ).first()
