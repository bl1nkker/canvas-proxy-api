from db.data_repo import DataRepo
from src.models import Attendance


class AttendanceRepo(DataRepo[Attendance]):
    _type = Attendance
    _order_by_map = None

    def filter_by_assignment_id(self, assignment_id: int):
        return self._query().filter(Attendance.canvas_assignment_id == assignment_id)
