from db.data_repo import DataRepo
from src.models import Student


class StudentRepo(DataRepo[Student]):
    _type = Student
    _order_by_map = None

    def get_by_web_id(self, web_id: str, query=None):
        query = query or self.query()
        return query.filter(Student.web_id == web_id).first()

    def get_by_canvas_user_id(self, canvas_user_id: int, query=None):
        query = query or self.query()
        return query.filter(Student.canvas_user_id == canvas_user_id).first()
