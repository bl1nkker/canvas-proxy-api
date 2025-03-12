from sqlalchemy import text

from db.data_repo import DataRepo
from src.models import Attendance


class AttendanceRepo(DataRepo[Attendance]):
    _type = Attendance
    _order_by_map = None

    def filter_by_assignment_id(self, assignment_id: int, query=None):
        query = query or self.query()
        return query.filter(Attendance.canvas_assignment_id == assignment_id)

    def get_by_student_id(self, student_id: int, query=None):
        query = query or self.query()
        return query.filter(Attendance.student_id == student_id).first()

    def next_attendance_from_queue(self, query=None):
        return (
            self.query()
            .from_statement(
                text(
                    """SELECT * FROM app.attendances WHERE status = 'INITIATED' or status = 'IN_PROGRESS' FOR UPDATE SKIP LOCKED LIMIT 1"""
                )
            )
            .first()
        )
