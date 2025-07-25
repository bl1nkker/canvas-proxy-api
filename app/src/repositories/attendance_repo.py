from sqlalchemy import text

from db.data_repo import DataRepo
from src.models import Attendance


class AttendanceRepo(DataRepo[Attendance]):
    _type = Attendance
    _order_by_map = None

    def filter_by_assignment_id(self, assignment_id: int, query=None):
        query = query or self.query()
        return query.filter(self._type.assignment_id == assignment_id)

    def get_by_student_id(self, student_id: int, query=None):
        query = query or self.query()
        return query.filter(self._type.student_id == student_id).first()

    def get_by_student_and_assignment_id(
        self, student_id: int, assignment_id: int, query=None
    ):
        query = query or self.query()
        return (
            query.filter(self._type.student_id == student_id)
            .filter(self._type.assignment_id == assignment_id)
            .first()
        )

    def get_by_web_id(self, web_id: str, query=None):
        query = query or self.query()
        return query.filter(self._type.web_id == web_id).first()

    def next_attendance_from_queue(self, query=None):
        query = query or self.query()
        return query.from_statement(
            text(
                # TODO: Also filter by date
                """SELECT * FROM app.attendances WHERE status = 'INITIATED' FOR UPDATE SKIP LOCKED LIMIT 1"""
            )
        ).first()
