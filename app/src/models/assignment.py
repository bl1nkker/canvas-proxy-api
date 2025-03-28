from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.models.base import Base


class Assignment(Base, DbModel, HasWebId):
    __tablename__ = "assignments"
    name = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("app.canvas_courses.id"))
    course = relationship("CanvasCourse", back_populates="assignments")
    canvas_assignment_id = Column(Integer, nullable=False)
    attendances = relationship(
        "Attendance",
        back_populates="assignment",
        primaryjoin="Assignment.id == Attendance.assignment_id",
        lazy="selectin",
    )
