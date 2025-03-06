from pydantic import BaseModel

from src.dto import canvas_course_dto, student_dto


class Read(BaseModel):
    course: canvas_course_dto.Read
    student: student_dto.Read

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            student=student_dto.Read.from_dbmodel(item.student),
            course=canvas_course_dto.Read.from_dbmodel(item.course),
        )
