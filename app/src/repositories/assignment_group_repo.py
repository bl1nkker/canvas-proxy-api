from db.data_repo import DataRepo
from src.models import AssignmentGroup


class AssignmentGroupRepo(DataRepo[AssignmentGroup]):

    _type = AssignmentGroup
    _order_by_map = None

    def get_by_web_id(self, web_id: str, query=None):
        query = query or self.query()
        return query.filter(self._type.web_id == web_id).first()

    def filter_by_course_id(self, course_id: str, query=None):
        query = query or self.query()
        return query.filter(self._type.course_id == course_id)

    def get_by_canvas_assignment_group_id(
        self, canvas_assignment_group_id: int, query=None
    ):
        query = query or self.query()
        return query.filter(
            self._type.canvas_assignment_group_id == canvas_assignment_group_id
        ).first()
