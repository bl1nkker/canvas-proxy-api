from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.models.base import Base


class Attendance(Base, DbModel, HasWebId):
    __tablename__ = "attendances"
    student_id = Column(Integer, ForeignKey("app.students.id"), nullable=False)
    student = relationship("Student")
    assignment_id = Column(Integer, ForeignKey("app.assignments.id"), nullable=False)
    assignment = relationship("Assignment")
    status = Column(Enum(AttendanceStatus), nullable=False)
    value = Column(Enum(AttendanceValue), nullable=False)

    @property
    def course(self):
        return self.assignment.course
