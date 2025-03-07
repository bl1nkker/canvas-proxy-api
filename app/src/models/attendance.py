from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from db import DbModel
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.models.base import Base


class Attendance(Base, DbModel):
    __tablename__ = "attendances"
    student_id = Column(Integer, ForeignKey("app.students.id"), nullable=False)
    student = relationship("Student")
    course_id = Column(Integer, ForeignKey("app.canvas_courses.id"), nullable=False)
    course = relationship("CanvasCourse")
    canvas_assignment_id = Column(Integer, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    value = Column(Enum(AttendanceValue), nullable=False)
