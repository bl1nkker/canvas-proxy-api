from db.data_repo import DataRepo
from src.models import Enrollment


class EnrollmentRepo(DataRepo[Enrollment]):
    _type = Enrollment
    _order_by_map = None

    def get_by_student_and_course_id(self, student_id: int, course_id: int, query=None):
        query = query or self.query()
        return (
            query.filter(self._type.student_id == student_id)
            .filter(self._type.course_id == course_id)
            .first()
        )

    def filter_by_course_id(self, course_id: int, query=None):
        query = query or self.query()
        return query.filter(self._type.course_id == course_id)
