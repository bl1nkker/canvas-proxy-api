from typing import Optional

from sqlalchemy import JSON, Boolean, Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.errors.attendance_process_error import AttendanceProcessError
from src.models.base import Base


class Attendance(Base, DbModel, HasWebId):
    __tablename__ = "attendances"
    student_id = Column(Integer, ForeignKey("app.students.id"), nullable=False)
    student = relationship("Student")
    assignment_id = Column(Integer, ForeignKey("app.assignments.id"), nullable=False)
    assignment = relationship("Assignment")
    status = Column(Enum(AttendanceStatus), nullable=False)
    value = Column(Enum(AttendanceValue), nullable=False)

    failed = Column(Boolean, nullable=False)
    error_json = Column(JSON(none_as_null=True), nullable=True)

    @property
    def course(self):
        return self.assignment.course

    @property
    def error(self) -> Optional[AttendanceProcessError]:
        if self.error_json:
            return AttendanceProcessError(**self.error_json)

    @error.setter
    def error(self, value: Optional[AttendanceProcessError]):
        if value is not None:
            self.error_json = value.dict()
        else:
            self.error_json = None
