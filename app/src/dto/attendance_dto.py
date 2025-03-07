from pydantic import BaseModel

from src.dto import student_dto
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue


class Create(BaseModel):
    student_id: int
    canvas_assignment_id: int
    status: AttendanceStatus
    value: AttendanceValue


class Read(BaseModel):
    canvas_assignment_id: int
    status: AttendanceStatus
    value: AttendanceValue
    student: student_dto.Read

    @classmethod
    def from_dbmodel(cls, dbmodel):
        return cls(
            canvas_assignment_id=dbmodel.canvas_assignment_id,
            status=dbmodel.status,
            value=dbmodel.value,
            student=student_dto.Read.from_dbmodel(dbmodel.student),
        )
