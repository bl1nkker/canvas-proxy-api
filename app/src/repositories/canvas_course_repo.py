from db.data_repo import DataRepo
from src.models import CanvasCourse


class CanvasCourseRepo(DataRepo[CanvasCourse]):
    _type = CanvasCourse
    _order_by_map = None

    def filter_by_canvas_user_id(self, canvas_user_id: int, query=None):
        query = query or self.query()
        return query.filter(self._type.canvas_user_id == canvas_user_id)

    def get_by_canvas_course_id(self, canvas_course_id: int, query=None):
        query = query or self.query()
        return query.filter(self._type.canvas_course_id == canvas_course_id).first()
