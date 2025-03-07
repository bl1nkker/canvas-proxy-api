from typing import Optional

from pydantic import BaseModel, Field

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


class Mark(BaseModel):
    value: AttendanceValue
    student_id: int


class CanvasRead(BaseModel):
    canvas_assignment_id: int = Field(validation_alias="assignment_id")
    student_id: int = Field(validation_alias="user_id")
    graded_at: str = Field(validation_alias="graded_at")
    excused: bool = Field(validation_alias="excused")
    grade: Optional[str] = Field(validation_alias="grade")
