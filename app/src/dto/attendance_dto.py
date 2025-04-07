from typing import Optional

from pydantic import BaseModel, Field

from src.dto import student_dto
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue


class FilterParams(BaseModel):
    assignment_web_id: str


class Create(BaseModel):
    student_id: int
    status: AttendanceStatus
    value: AttendanceValue


class Read(BaseModel):
    web_id: str
    assignment_id: int
    status: AttendanceStatus
    value: AttendanceValue
    student: student_dto.Read

    @classmethod
    def from_dbmodel(cls, dbmodel):
        return cls(
            web_id=dbmodel.web_id,
            assignment_id=dbmodel.assignment_id,
            status=dbmodel.status,
            value=dbmodel.value,
            student=student_dto.Read.from_dbmodel(dbmodel.student),
        )


class Mark(BaseModel):
    value: AttendanceValue


class Search(BaseModel):
    course_id: int
    assignment_id: int


class CanvasRead(BaseModel):
    canvas_assignment_id: int = Field(validation_alias="assignment_id")
    student_id: int = Field(validation_alias="user_id")
    graded_at: str = Field(validation_alias="graded_at")
    excused: bool = Field(validation_alias="excused")
    grade: Optional[str] = Field(validation_alias="grade")
