from typing import Any, Optional

from pydantic import BaseModel, Field

from src.enums.attendance_value import AttendanceValue


class Create(BaseModel):
    name: str
    email: str
    canvas_user_id: int


class CanvasRead(BaseModel):
    name: str
    email: str
    canvas_user_id: int = Field(validation_alias="id")


class CanvasSubmission(BaseModel):
    id: int
    grade: str | None
    assignment_id: int
    excused: bool | None

    @property
    def value(self):
        if self.grade is None:
            if self.excused is True:
                return AttendanceValue.EXCUSE
        if self.grade in AttendanceValue:
            return AttendanceValue(self.grade)
        return AttendanceValue.INCOMPLETE


class CanvasStudentSubmissions(BaseModel):
    id: int = Field(validation_alias="user_id")
    submissions: list[CanvasSubmission]


class Read(BaseModel):
    id: int
    web_id: Optional[str]
    name: str
    email: str

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            id=item.id,
            name=item.name,
            email=item.email,
            web_id=item.web_id,
        )


class StudentFile(BaseModel):
    origin_name: str
    image_id: str
    canvas_name: str
    canvas_login: str
    canvas_id: int
    image_vector: Optional[Any] = None
    image_vector_512: Optional[Any] = None
    image_vector_4096: Optional[Any] = None
